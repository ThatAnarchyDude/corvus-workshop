#!/usr/bin/env python3
"""Record native DS gameplay and actual emulator audio from a private battery save."""
import argparse, json, subprocess, tempfile, wave
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from live_core import Emulator, BUTTONS, field_metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--core', type=Path, required=True)
    parser.add_argument('--save-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=30)
    parser.add_argument('--actions', type=Path, help='JSON list of frame/buttons actions, including boot navigation')
    parser.add_argument('--skip-frames', type=int, default=0)
    parser.add_argument('--label', default='Prototype 0022 — prepared test save')
    args = parser.parse_args()
    if not 1 <= args.seconds <= 600 or args.skip_frames < 0: parser.error('Invalid recording duration')
    if args.output.exists() or args.output.with_suffix('.json').exists(): parser.error('Recordings are never overwritten')
    actions = json.loads(args.actions.read_text()) if args.actions else []
    for action in actions:
        if action['frame'] < 0 or action.get('frames', 8) < 1 or any(b not in BUTTONS for b in action['buttons']):
            parser.error('Invalid controller action')
    actions.sort(key=lambda a: a['frame'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    emulator = Emulator(args.core.resolve(), args.rom.resolve(), args.save_dir.resolve(), capture_audio=True)
    fps, rate = emulator.fps, round(emulator.sample_rate)
    if not 1 < fps < 240 or not 8000 <= rate <= 192000: raise RuntimeError('Invalid native AV timing')
    try: font = ImageFont.truetype('DejaVuSansMono.ttf', 17)
    except OSError: font = ImageFont.load_default(size=17)
    history = []; metrics = None; hint = None; samples = 0; video_frames = 0; nonzero = False
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(dir=args.output.parent) as temp:
        temp = Path(temp)
        encoder = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24',
            '-video_size', '1024x768', '-framerate', str(fps/5), '-i', 'pipe:0', '-an',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '25', '-pix_fmt', 'yuv420p', str(temp/'video.mp4')], stdin=subprocess.PIPE)
        try:
            with wave.open(str(temp/'audio.wav'), 'wb') as audio:
                audio.setnchannels(2); audio.setsampwidth(2); audio.setframerate(rate)
                end = args.skip_frames + round(args.seconds * fps / 5) * 5
                remaining = 0
                for frame in range(end):
                    while actions and frame >= actions[0]['frame']:
                        action = actions.pop(0)
                        emulator.buttons = {BUTTONS[b] for b in action['buttons']}
                        remaining = action.get('frames', 8)
                        history.append({'native_frame': frame, 'buttons': action['buttons']})
                    emulator.run()
                    if remaining:
                        remaining -= 1
                        if not remaining: emulator.buttons.clear()
                    pcm = emulator.drain_audio()
                    if frame < args.skip_frames: continue
                    audio.writeframesraw(pcm); samples += len(pcm)//4
                    nonzero = nonzero or any(pcm)
                    relative = frame - args.skip_frames
                    if relative % 60 == 0:
                        metrics = field_metrics(emulator.ram(), hint)
                        hint = int(metrics['field_system'],16)-0x02000000 if metrics else None
                        history.append({'elapsed_seconds': round(relative/fps,3), 'ram': metrics})
                    if relative % 5: continue
                    image = emulator.image()
                    if image is None: raise RuntimeError('Missing emulator video frame')
                    canvas = Image.new('RGB', (1024,768), '#131824')
                    canvas.paste(image.resize((512,768), Image.Resampling.NEAREST), (0,0))
                    draw = ImageDraw.Draw(canvas)
                    lines = [args.label, 'REAL GAME AUDIO + NATIVE VIDEO', f'Elapsed: {relative/fps:.1f}s',
                        'Prepared save; not normal progression.', 'Controller inputs; no RAM writes.', '',
                        *json.dumps(metrics,indent=2).splitlines(), '', 'Recent controller inputs:']
                    lines += [f"frame {e['native_frame']}: {','.join(e['buttons'])}" for e in history if 'buttons' in e][-5:]
                    for i,line in enumerate(lines[:33]): draw.text((530,24+i*22),line,fill='#dce8ff',font=font)
                    encoder.stdin.write(canvas.tobytes()); video_frames += 1
                    if video_frames == 1: canvas.save(args.output.with_suffix('.jpg'), quality=90)
        finally:
            emulator.close(); encoder.stdin.close(); result = encoder.wait(timeout=30)
        if result: raise RuntimeError('Video encoding failed')
        if not samples or not nonzero: raise RuntimeError('Emulator did not produce audible PCM')
        video_duration = video_frames/(fps/5)
        audio_duration = samples / rate
        drift = audio_duration - video_duration
        tempo = audio_duration / video_duration
        # DeSmuME's SPU callback clock can drift slightly from its reported DS
        # video clock, especially across field loads. Use the complete native
        # PCM track, preserving pitch and aligning it to the frame timeline.
        # Large discrepancies still fail rather than masking dropped capture.
        if abs(tempo - 1) > 0.01:
            raise RuntimeError(f'Audio/video clock discrepancy exceeds 1%: '
                               f'audio={audio_duration:.6f}s video={video_duration:.6f}s')
        subprocess.run(['ffmpeg','-v','error','-i',str(temp/'video.mp4'),'-i',str(temp/'audio.wav'),
            '-c:v','copy','-af',f'atempo={tempo:.12f}',
            '-c:a','aac','-b:a','128k','-movflags','+faststart','-n',str(args.output)],check=True)
        probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams',
                                                    '-of','json',str(args.output)]))
        durations = {s['codec_type']:float(s['duration']) for s in probe['streams']}
        if abs(durations['audio']-durations['video']) > 0.2:
            raise RuntimeError(f'Encoded audio/video duration mismatch: {durations}')
    report = {'label':args.label,'recorded_at_utc':started,'silent':False,'audio_source':'native libretro PCM callbacks',
        'sample_rate':rate,'audio_samples':samples,'audio_nonzero':nonzero,'native_fps':fps,
        'video_frames':video_frames,'duration_seconds':video_duration,
        'source_audio_duration_seconds':audio_duration,'source_clock_drift_seconds':drift,
        'audio_tempo_correction':tempo,'audio_pitch_preserved':True,
        'encoded_stream_durations':durations,'ram_writes':False,'events':history}
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='events'}))

if __name__ == '__main__': main()
