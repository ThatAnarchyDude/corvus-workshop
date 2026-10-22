#!/usr/bin/env python3
"""Live DS video + read-only RAM HUD. All emulator access stays on one worker.
Chat commands are handled by the agent through /control, not a fictional chat API.
"""
import argparse
import base64
from collections import deque
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
<style>body{background:#131824;color:#eef;font:16px monospace;margin:20px}main{display:flex;gap:24px;flex-wrap:wrap}img{width:512px;max-width:90vw;image-rendering:pixelated}pre{white-space:pre-wrap;width:360px}.screens{display:flex;gap:16px;flex-wrap:wrap}.screens figure{margin:0}.screens canvas{width:384px;max-width:90vw;image-rendering:pixelated;aspect-ratio:4/3}.screens figcaption{margin-bottom:8px}#video{position:absolute;left:-10000px;width:256px;height:384px}#touchscreen{cursor:pointer}[hidden]{display:none!important}button{padding:12px;margin:4px}small{display:block}</style>
<h1>Pokémon Psyduck Yellow — live testing</h1><p id="label"></p><p id="activity">Preparing next live playtest.</p><p id="state">Video starts OFF. Emulator and RAM monitoring continue.</p>
<span id="video-controls" hidden><button onclick="command({video:true})">Video ON</button><button onclick="command({video:false})">Video OFF</button></span>
<button id="sound" onclick="toggleSound()">Enable sound</button><main><div><img id="video" alt="Native DS video source"><div class="screens"><figure><figcaption>Top screen</figcaption><canvas id="topscreen" width="256" height="192"></canvas></figure><figure><figcaption>Touch screen</figcaption><canvas id="touchscreen" width="256" height="192"></canvas></figure></div><div id="buttons"></div></div><pre id="hud">Connecting…</pre></main>
<small>Native DS frames · live stereo game audio · no ROM download · ordinary saves are private. Input commands are queued on the emulator thread.</small>
<script>
const token=new URLSearchParams(location.hash.slice(1)).get('token')||'';
let canControl=false;
let on=false;
const headers={'Content-Type':'application/json','X-Live-Token':token};
async function command(body){if(!canControl)return;const r=await fetch('control',{method:'POST',headers,body:JSON.stringify(body)});if(!r.ok)alert(await r.text())}
for(const b of ['up','down','left','right','a','b','x','y','start','select','l','r']){let el=document.createElement('button');el.textContent=b;el.onclick=()=>command({button:b,frames:8});document.querySelector('#buttons').append(el)}
let audioContext=null, sound=false, audioSequence=0, playAt=0;const audioSources=new Set();
async function toggleSound(){
 if(sound){sound=false; await audioContext.suspend(); document.querySelector('#sound').textContent='Enable sound';return}
 audioContext=audioContext||new AudioContext();await audioContext.resume();sound=true;audioSequence=0;playAt=0;
 document.querySelector('#sound').textContent='Mute sound';pollAudio();
}
async function pollAudio(){
 if(!sound)return;
 if(!on){setTimeout(pollAudio,200);return}
 try{
 const r=await fetch('audio.pcm?after='+audioSequence,{headers,cache:'no-store'});if(!r.ok)throw Error('Audio access denied');
 audioSequence=Number(r.headers.get('X-Audio-Sequence'));const rate=Number(r.headers.get('X-Audio-Rate'));
 const raw=new Uint8Array(await r.arrayBuffer());
 if(raw.length){
 const view=new DataView(raw.buffer);
 const n=raw.length/4;const b=audioContext.createBuffer(2,n,rate);
 for(let c=0;c<2;c++){const out=b.getChannelData(c);for(let i=0;i<n;i++)out[i]=view.getInt16(i*4+c*2,true)/32768}
 const now=audioContext.currentTime;
 if(playAt<now||playAt>now+0.75)playAt=now+0.25;
 const source=audioContext.createBufferSource();source.buffer=b;source.connect(audioContext.destination);audioSources.add(source);source.onended=()=>audioSources.delete(source);source.start(playAt);playAt+=b.duration;
 }
 }catch(e){document.querySelector('#sound').textContent='Sound error — tap to retry';sound=false;return}
 if(sound)setTimeout(pollAudio,100);
}
const nativeVideo=document.querySelector('#video');
const topCanvas=document.querySelector('#topscreen'), touchCanvas=document.querySelector('#touchscreen');
const topContext=topCanvas.getContext('2d'), touchContext=touchCanvas.getContext('2d');
function drawScreens(){
 if(on && nativeVideo.naturalWidth){topContext.drawImage(nativeVideo,0,0,256,192,0,0,256,192);touchContext.drawImage(nativeVideo,0,192,256,192,0,0,256,192)}
 requestAnimationFrame(drawScreens);
}
drawScreens();
touchCanvas.onclick=e=>{const r=touchCanvas.getBoundingClientRect();command({touch:[Math.min(255,Math.max(0,Math.round((e.clientX-r.left)/r.width*255))),192+Math.min(191,Math.max(0,Math.round((e.clientY-r.top)/r.height*191)))],frames:8})};
async function refresh(){try{let r=await fetch('status',{headers});if(!r.ok)throw Error('Access denied');let s=await r.json();canControl=!!s.can_control;document.querySelector('#video-controls').hidden=!canControl;document.querySelector('#buttons').hidden=!canControl;touchCanvas.style.cursor=canControl?'pointer':'default';document.querySelector('#hud').textContent=JSON.stringify(s,null,2);document.querySelector('#label').textContent=s.label||'';document.querySelector('#activity').textContent=s.activity||'';document.querySelector('#state').textContent=s.video?'Video ON':'Video OFF — emulation and RAM monitoring continue';if(s.video!==on){on=s.video;const img=document.querySelector('#video');if(on){img.src='stream.mjpg?token='+encodeURIComponent(token)+'&t='+Date.now();if(sound&&audioContext)audioContext.resume().catch(()=>{})}else{img.removeAttribute('src');for(const source of audioSources){try{source.stop()}catch(e){}}audioSources.clear();playAt=0;if(audioContext)audioContext.suspend();for(const context of [topContext,touchContext]){context.fillStyle='#131824';context.fillRect(0,0,256,192);context.fillStyle='#eef';context.font='15px monospace';context.fillText('Feed paused',64,96)}}}}catch(e){document.querySelector('#hud').textContent=String(e)}setTimeout(refresh,500)}refresh();
</script>'''

class RAMProbe:
    def __init__(self):
        self.hint=None; self.next_scan=0
    def read(self,ram,now):
        if self.hint is None and now<self.next_scan: return None
        result=field_metrics(ram,self.hint)
        if result: self.hint=int(result['field_system'],16)-0x02000000
        else: self.hint=None; self.next_scan=now+5
        return result


class Session:
    def __init__(self,args):
        self.args=args; self.stop=threading.Event(); self.lock=threading.Condition()
        self.commands=queue.Queue(maxsize=100); self.video=False; self.jpeg=None; self.sequence=0
        self.audio=deque(maxlen=120); self.audio_sequence=0; self.audio_rate=44100
        self.status={'activity':'Preparing next live playtest','label':getattr(args,'label','Live development testing'),'video':False,'frames':0,'phase':'starting','ram':None,'error':None}
    def control(self,body):
        if not isinstance(body,dict): raise ValueError('Expected JSON object')
        if set(body)-{'video','button','frames','stop','touch','activity'}: raise ValueError('Unknown command')
        if 'video' in body and type(body['video']) is not bool:
            raise ValueError('video must be boolean')
        if 'button' in body:
            frames=body.get('frames',8)
            if body['button'] not in BUTTONS or type(frames) is not int or not 1<=frames<=600:
                raise ValueError('Invalid button or duration (1–600 frames)')
            self.commands.put_nowait((body['button'],frames))
        if 'activity' in body:
            if not isinstance(body['activity'],str) or len(body['activity'])>160:raise ValueError('Invalid activity label')
            with self.lock:self.status['activity']=body['activity']
        if 'touch' in body:
            point=body['touch'];frames=body.get('frames',8)
            if (not isinstance(point,list) or len(point)!=2 or any(type(v) is not int for v in point)
                or not 0<=point[0]<=255 or not 0<=point[1]<=383 or type(frames) is not int or not 1<=frames<=600):
                raise ValueError('Invalid touch point or duration')
            self.commands.put_nowait((point,frames))
        if 'video' in body:
            with self.lock:
                self.video=body['video']; self.status['video']=self.video
                if not self.video: self.jpeg=None
                self.lock.notify_all()
        if body.get('stop') is True: self.stop.set()
    def run(self):
        emulator=None
        try:
            emulator=Emulator(self.args.core,self.args.rom,self.args.save_dir,capture_audio=True)
            self.audio_rate=round(emulator.sample_rate)
            actions=json.loads(self.args.actions.read_text()) if self.args.actions else []
            # Deterministic libretro controller events, with explicit release between actions.
            for action in actions:
                if action.get('button') not in BUTTONS or not 1<=action.get('frames',8)<=600:
                    raise ValueError('Invalid scripted action')
                self.commands.put_nowait((action['button'],action.get('frames',8)))
            frames=0; remaining=0; release=0; probe=RAMProbe(); next_metrics=0; next_capture=0
            log=self.args.save_dir/'live-metrics.jsonl'
            with log.open('a',buffering=1) as output:
                while not self.stop.is_set():
                    start=time.monotonic()
                    if not remaining:
                        emulator.buttons=set();emulator.touch=None
                        if release: release-=1
                        else:
                            try:
                                button,remaining=self.commands.get_nowait()
                                if isinstance(button,list):emulator.touch=button
                                else:emulator.buttons={BUTTONS[button]}
                            except queue.Empty: pass
                    emulator.run(); frames+=1
                    pcm=emulator.drain_audio()
                    if pcm:
                        with self.lock:
                            self.audio_sequence+=1
                            self.audio.append((self.audio_sequence,pcm))
                    if remaining:
                        remaining-=1
                        if remaining==0: release=4
                    if start>=next_metrics:
                        metrics=probe.read(emulator.ram(),start)
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
                            buf=io.BytesIO(); image.save(buf,format='JPEG',quality=65)
                            with self.lock:
                                if self.video:
                                    self.jpeg=buf.getvalue(); self.sequence+=1; self.lock.notify_all()
                        next_capture=start+1/self.args.fps
                    time.sleep(max(0,1/emulator.fps-(time.monotonic()-start)))
        except Exception as exc:
            with self.lock: self.status['error']=str(exc); self.status['phase']='failed'
            print('[Automation ERROR] '+str(exc),flush=True); self.stop.set()
        finally:
            if emulator: emulator.close() # Native battery-save flush; no cross-ROM save states.
            with self.lock: self.lock.notify_all()


def handler_for(session,token,view_token=''):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass # Do not log access tokens in MJPEG query strings.
        def authorized(self,control=False):
            import hmac
            from urllib.parse import urlsplit,parse_qs
            supplied=self.headers.get('X-Live-Token','')
            if self.path.startswith('/stream.mjpg'):
                supplied=parse_qs(urlsplit(self.path).query).get('token',[''])[0]
            if not token:return True
            if hmac.compare_digest(supplied,token):return True
            return not control and bool(view_token) and hmac.compare_digest(supplied,view_token)
        def reply(self,code,data,kind='application/json'):
            self.send_response(code); self.send_header('Content-Type',kind)
            self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(data)))
            self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            path=self.path.split('?',1)[0]
            if path=='/': return self.reply(200,PAGE.encode(),'text/html; charset=utf-8')
            if not self.authorized(): return self.reply(403,b'{"error":"Access denied"}')
            if path in ('/audio','/audio.pcm'):
                from urllib.parse import urlsplit,parse_qs
                try: after=int(parse_qs(urlsplit(self.path).query).get('after',['0'])[0])
                except ValueError: return self.reply(400,b'{}')
                with session.lock:
                    # On first connection send only recent audio, never a stale backlog.
                    chunks=[pcm for seq,pcm in session.audio if seq>after][-30 if after==0 else -60:]
                    data=json.dumps(dict(sequence=session.audio_sequence,rate=session.audio_rate,
                        pcm=base64.b64encode(b''.join(chunks)).decode())).encode()
                if path=='/audio.pcm':
                    self.send_response(200); self.send_header('Content-Type','application/octet-stream')
                    self.send_header('Cache-Control','no-store'); self.send_header('X-Audio-Sequence',str(session.audio_sequence))
                    self.send_header('X-Audio-Rate',str(session.audio_rate)); self.send_header('Content-Length',str(sum(map(len,chunks))))
                    self.end_headers(); self.wfile.write(b''.join(chunks)); return
                return self.reply(200,data)
            if path=='/frame.jpg':
                with session.lock: data=session.jpeg if session.video else None
                return self.reply(200 if data else 204,data or b'','image/jpeg')
            if path=='/status':
                with session.lock: data=json.dumps(dict(session.status,can_control=self.authorized(control=True))).encode()
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
            if not self.authorized(control=True): return self.reply(403,b'{}')
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
    p.add_argument('--label',default='Live development testing')
    p.add_argument('--fps',type=int,default=12); args=p.parse_args()
    token=os.environ.get('LIVE_TEST_TOKEN','')
    view_token=os.environ.get('LIVE_TEST_VIEW_TOKEN','')
    if view_token and (not token or view_token==token):p.error('Viewing and control credentials must be distinct')
    if args.host not in ('127.0.0.1','localhost','::1') and not token:
        p.error('Non-loopback binding requires LIVE_TEST_TOKEN; use an authenticated port proxy')
    if not 1<=args.fps<=30: p.error('fps must be 1–30')
    if not args.rom.is_file() or not args.core.is_file(): p.error('Private ROM/core missing')
    args.rom=args.rom.resolve(); args.core=args.core.resolve(); args.save_dir.mkdir(parents=True,exist_ok=True)
    args.save_dir=args.save_dir.resolve()
    save_lock=(args.save_dir/'.live-owner.lock').open('w')
    try: fcntl.flock(save_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: p.error('Another live runner owns this save directory')
    session=Session(args); server=ThreadingHTTPServer((args.host,args.port),handler_for(session,token,view_token))
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
