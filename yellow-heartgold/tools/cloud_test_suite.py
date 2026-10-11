#!/usr/bin/env python3
"""Live DS video + read-only RAM HUD. All emulator access stays on one worker.
Chat commands are handled by the agent through /control, not a fictional chat API.
"""
import argparse
import fcntl
import io
import json
import os
import queue
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from live_core import Emulator, BUTTONS, field_metrics

PROJECT=Path(__file__).resolve().parents[1]
PAGE='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Psyduck Yellow live testing</title>
<style>body{background:#131824;color:#eef;font:16px monospace;margin:20px}main{display:flex;gap:24px;flex-wrap:wrap}img{width:512px;max-width:90vw;image-rendering:pixelated}pre{white-space:pre-wrap;width:420px}button{padding:12px;margin:4px}small{display:block}</style>
<h1>Pokémon Psyduck Yellow — live testing</h1><p id="state">Video starts OFF. Emulator and RAM monitoring continue.</p>
<button onclick="command({video:true})">Video ON</button><button onclick="command({video:false})">Video OFF</button>
<main><div><img id="video" alt="Video paused"><div id="buttons"></div></div><pre id="hud">Connecting…</pre></main>
<small>Native DS frames · silent stream · no ROM download · ordinary saves are private. Input commands are queued on the emulator thread.</small>
<script>
const token=new URLSearchParams(location.hash.slice(1)).get('token')||'';
const headers={'Content-Type':'application/json','X-Live-Token':token};
async function command(body){const r=await fetch('control',{method:'POST',headers,body:JSON.stringify(body)});if(!r.ok)alert(await r.text())}
for(const b of ['up','down','left','right','a','b','x','y','start','select','l','r']){let el=document.createElement('button');el.textContent=b;el.onclick=()=>command({button:b,frames:8});document.querySelector('#buttons').append(el)}
let on=false;
async function refresh(){try{let r=await fetch('status',{headers});if(!r.ok)throw Error('Access denied');let s=await r.json();document.querySelector('#hud').textContent=JSON.stringify(s,null,2);document.querySelector('#state').textContent=s.video?'Video ON':'Video OFF — emulation and RAM monitoring continue';if(s.video!==on){on=s.video;const img=document.querySelector('#video');if(on)img.src='stream.mjpg?token='+encodeURIComponent(token)+'&t='+Date.now();else img.removeAttribute('src')}}catch(e){document.querySelector('#hud').textContent=String(e)}setTimeout(refresh,500)}refresh();
</script>'''

class Session:
    def __init__(self,args):
        self.args=args; self.stop=threading.Event(); self.lock=threading.Condition()
        self.commands=queue.Queue(maxsize=100); self.video=False; self.jpeg=None; self.sequence=0
        self.status={'video':False,'frames':0,'phase':'starting','ram':None,'error':None}
    def control(self,body):
        if not isinstance(body,dict): raise ValueError('Expected JSON object')
        if set(body)-{'video','button','frames','stop'}: raise ValueError('Unknown command')
        if 'video' in body and type(body['video']) is not bool:
            raise ValueError('video must be boolean')
        if 'button' in body:
            frames=body.get('frames',8)
            if body['button'] not in BUTTONS or type(frames) is not int or not 1<=frames<=600:
                raise ValueError('Invalid button or duration (1–600 frames)')
            self.commands.put_nowait((body['button'],frames))
        if 'video' in body:
            with self.lock:
                self.video=body['video']; self.status['video']=self.video
                if not self.video: self.jpeg=None
                self.lock.notify_all()
        if body.get('stop') is True: self.stop.set()
    def run(self):
        emulator=None
        try:
            emulator=Emulator(self.args.core,self.args.rom,self.args.save_dir)
            actions=json.loads(self.args.actions.read_text()) if self.args.actions else []
            # Deterministic libretro controller events, with explicit release between actions.
            for action in actions:
                if action.get('button') not in BUTTONS or not 1<=action.get('frames',8)<=600:
                    raise ValueError('Invalid scripted action')
                self.commands.put_nowait((action['button'],action.get('frames',8)))
            frames=0; remaining=0; release=0; hint=None; next_metrics=0; next_capture=0; next_scan=0
            log=self.args.save_dir/'live-metrics.jsonl'
            with log.open('a',buffering=1) as output:
                while not self.stop.is_set():
                    start=time.monotonic()
                    if not remaining:
                        emulator.buttons=set()
                        if release: release-=1
                        else:
                            try:
                                button,remaining=self.commands.get_nowait()
                                emulator.buttons={BUTTONS[button]}
                            except queue.Empty: pass
                    emulator.run(); frames+=1
                    if remaining:
                        remaining-=1
                        if remaining==0: release=4
                    if start>=next_metrics:
                        ram=emulator.ram()
                        metrics=field_metrics(ram,hint) if hint is not None or start>=next_scan else None
                        if metrics is None and hint is None: next_scan=start+5
                        if metrics: hint=int(metrics['field_system'],16)-0x02000000
                        else: hint=None
                        with self.lock:
                            self.status.update(frames=frames,phase='running',ram=metrics,
                                               observed_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
                            status=dict(self.status)
                        # Rotate a bounded live log (never dump raw RAM or ROM bytes).
                        if output.tell()>5_000_000: output.seek(0); output.truncate()
                        output.write(json.dumps(status)+'\n')
                        print('[Automation HUD] '+json.dumps(status),flush=True)
                        next_metrics=start+1
                    with self.lock: enabled=self.video
                    if enabled and start>=next_capture:
                        image=emulator.image()
                        if image:
                            buf=io.BytesIO(); image.save(buf,format='JPEG',quality=85)
                            with self.lock:
                                if self.video:
                                    self.jpeg=buf.getvalue(); self.sequence+=1; self.lock.notify_all()
                        next_capture=start+1/self.args.fps
                    time.sleep(max(0,1/60-(time.monotonic()-start)))
        except Exception as exc:
            with self.lock: self.status['error']=str(exc); self.status['phase']='failed'
            print('[Automation ERROR] '+str(exc),flush=True); self.stop.set()
        finally:
            if emulator: emulator.close() # Native battery-save flush; no cross-ROM save states.
            with self.lock: self.lock.notify_all()


def handler_for(session,token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass # Do not log access tokens in MJPEG query strings.
        def authorized(self):
            import hmac
            from urllib.parse import urlsplit,parse_qs
            supplied=self.headers.get('X-Live-Token','')
            if self.path.startswith('/stream.mjpg'):
                supplied=parse_qs(urlsplit(self.path).query).get('token',[''])[0]
            return not token or hmac.compare_digest(supplied,token)
        def reply(self,code,data,kind='application/json'):
            self.send_response(code); self.send_header('Content-Type',kind)
            self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(data)))
            self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            path=self.path.split('?',1)[0]
            if path=='/': return self.reply(200,PAGE.encode(),'text/html; charset=utf-8')
            if not self.authorized(): return self.reply(403,b'{"error":"Access denied"}')
            if path=='/status':
                with session.lock: data=json.dumps(session.status).encode()
                return self.reply(200,data)
            if path!='/stream.mjpg': return self.reply(404,b'{}')
            self.send_response(200); self.send_header('Content-Type','multipart/x-mixed-replace; boundary=frame')
            self.send_header('Cache-Control','no-store'); self.end_headers()
            sequence=-1
            try:
                while not session.stop.is_set():
                    with session.lock:
                        session.lock.wait_for(lambda:session.stop.is_set() or not session.video or session.sequence!=sequence,timeout=5)
                        if not session.video or session.stop.is_set(): break
                        data=session.jpeg; sequence=session.sequence
                    if data:
                        self.wfile.write(b'--frame\r\nContent-Type: image/jpeg\r\nContent-Length: '+str(len(data)).encode()+b'\r\n\r\n'+data+b'\r\n'); self.wfile.flush()
            except (BrokenPipeError,ConnectionResetError): pass
        def do_POST(self):
            if self.path!='/control': return self.reply(404,b'{}')
            if not self.authorized(): return self.reply(403,b'{}')
            # Reject cross-origin control requests; no CORS permissions.
            origin=self.headers.get('Origin')
            if origin and origin.split('://',1)[-1]!=self.headers.get('Host'):
                return self.reply(403,b'{"error":"Origin denied"}')
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4096: raise ValueError('Invalid request size')
                session.control(json.loads(self.rfile.read(size)))
                self.reply(200,b'{"ok":true}')
            except (ValueError,TypeError,KeyError,queue.Full) as exc:
                self.reply(400,json.dumps({'error':str(exc)}).encode())
    return Handler


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--core',type=Path,default=PROJECT/'.tools/emulator/desmume_libretro.so')
    p.add_argument('--save-dir',type=Path,default=PROJECT/'build/live-testing')
    p.add_argument('--actions',type=Path,help='JSON list of {button, frames}; no endless navigation loop')
    p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8080)
    p.add_argument('--fps',type=int,default=12); args=p.parse_args()
    token=os.environ.get('LIVE_TEST_TOKEN','')
    if args.host not in ('127.0.0.1','localhost','::1') and not token:
        p.error('Non-loopback binding requires LIVE_TEST_TOKEN; use an authenticated port proxy')
    if not 1<=args.fps<=30: p.error('fps must be 1–30')
    if not args.rom.is_file() or not args.core.is_file(): p.error('Private ROM/core missing')
    args.rom=args.rom.resolve(); args.core=args.core.resolve(); args.save_dir.mkdir(parents=True,exist_ok=True)
    args.save_dir=args.save_dir.resolve()
    save_lock=(args.save_dir/'.live-owner.lock').open('w')
    try: fcntl.flock(save_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: p.error('Another live runner owns this save directory')
    session=Session(args); server=ThreadingHTTPServer((args.host,args.port),handler_for(session,token))
    server.daemon_threads=True
    worker=threading.Thread(target=session.run,name='emulator'); worker.start()
    signal.signal(signal.SIGTERM,lambda *_:session.stop.set())
    signal.signal(signal.SIGINT,lambda *_:session.stop.set())
    server.timeout=.5
    print(f'Live-testing server listening on port {args.port}; video OFF. Use /control or agent chat instructions.',flush=True)
    try:
        while not session.stop.is_set(): server.handle_request()
    finally:
        session.stop.set(); worker.join(timeout=15); server.server_close(); save_lock.close()
    if session.status['error']: raise SystemExit(1)

if __name__=='__main__': main()
