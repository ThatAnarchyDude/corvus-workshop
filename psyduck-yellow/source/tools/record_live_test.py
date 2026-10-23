#!/usr/bin/env python3
"""Record the native DS feed and RAM HUD into a silent, shareable H.264 MP4."""
import argparse,io,json,os,subprocess,time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=20)
    p.add_argument('--url',default='http://127.0.0.1:8080')
    p.add_argument('--actions',type=Path)
    p.add_argument('--label',default='Pokémon Psyduck Yellow — native test')
    args=p.parse_args()
    if not 1<=args.seconds<=600:p.error('seconds must be 1–600')
    if args.output.exists():p.error('Output exists; recordings are never overwritten')
    actions=json.loads(args.actions.read_text()) if args.actions else []
    for a in actions:
        if not 0<=a['at']<args.seconds:p.error('Action timestamp outside recording')
    actions=sorted(actions,key=lambda a:a['at'])
    headers={'X-Live-Token':os.environ.get('LIVE_TEST_TOKEN','')}
    def request(path,body=None):
        r=Request(args.url+path,headers={**headers,'Content-Type':'application/json'},
                  data=json.dumps(body).encode() if body is not None else None)
        return urlopen(r,timeout=10)
    with request('/control',{'video':True}):pass
    args.output.parent.mkdir(parents=True,exist_ok=True)
    # Never pass credentials, remote URLs or ROMs to the encoder.
    ffmpeg=subprocess.Popen(['ffmpeg','-v','error','-f','rawvideo','-pixel_format','rgb24',
        '-video_size','1024x768','-framerate','12','-i','pipe:0','-an','-c:v','libx264',
        '-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',
        '-n',str(args.output)],stdin=subprocess.PIPE)
    try:font=ImageFont.truetype('DejaVuSansMono.ttf',17)
    except OSError:font=ImageFont.load_default(size=17)
    history=[];status={};frames=0;next_status=0;started=time.monotonic()
    try:
        url=args.url+'/stream.mjpg?token='+quote(headers['X-Live-Token'])
        with urlopen(url,timeout=10) as feed:
            for _ in range(args.seconds*12):
                now=time.monotonic()-started
                while actions and now>=actions[0]['at']:
                    action=actions.pop(0)
                    with request('/control',{'button':action['button'],'frames':action.get('frames',8)}):pass
                    history.append({'elapsed_seconds':round(now,3),'button':action['button']})
                line=feed.readline()
                if line!=b'--frame\r\n':raise RuntimeError('Invalid MJPEG boundary')
                feed.readline();length=int(feed.readline().split(b':',1)[1]);feed.readline()
                if not 1<=length<=2_000_000:raise RuntimeError('Invalid JPEG length')
                raw=feed.read(length);feed.read(2)
                native=Image.open(io.BytesIO(raw)).convert('RGB')
                if now>=next_status:
                    with request('/status') as response:status=json.load(response)
                    next_status=now+1
                    history.append({'elapsed_seconds':round(now,3),'status':status})
                canvas=Image.new('RGB',(1024,768),'#131824')
                canvas.paste(native.resize((512,768),Image.Resampling.NEAREST),(0,0))
                draw=ImageDraw.Draw(canvas)
                draw.text((532,24),args.label,fill='white',font=font)
                lines=['RECORDED PLAYTEST — SILENT',f'Elapsed: {now:.1f} seconds','Native DS frames + read-only RAM','',
                       'Only queued controller inputs;','no RAM writes by this recorder.','',
                       *json.dumps(status,indent=2).splitlines(),'','Input log:']
                lines += [f"{a['elapsed_seconds']:5.1f}s  {a['button']}" for a in history if 'button' in a][-6:]
                for i,line in enumerate(lines[:31]):draw.text((532,70+i*21),line,fill='#cde',font=font)
                ffmpeg.stdin.write(canvas.tobytes());frames+=1
    finally:
        ffmpeg.stdin.close();exit_code=ffmpeg.wait(timeout=20)
    if exit_code:raise RuntimeError(f'Encoder exited {exit_code}')
    report={'label':args.label,'video_frames':frames,'encoded_fps':12,'silent':True,
            'elapsed_wall_seconds':round(time.monotonic()-started,3),'events':history}
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'frames':frames,'output':str(args.output),'silent':True}))

if __name__=='__main__':main()
