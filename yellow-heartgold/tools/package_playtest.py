"""Create an offline-capable downloader containing a patch, never a ROM."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
VENDOR = PROJECT/'tools/vendor/rom-patcher'


def build(destination, version='004'):
    if version not in ('004', '005', '006', '007', '008', '009', '010', '011'):
        raise ValueError('Unsupported prototype version')
    destination.mkdir(parents=True, exist_ok=True)
    patch = PROJECT/f'build/yellow-heartgold-prototype-{version}.xdelta'
    rom = PROJECT/f'build/yellow-heartgold-prototype-{version}.nds'
    manifest = dict(version=version, source_sha256=
        '65f02a56842b75aa92d775d56d657a56fe3fa993550b04dc20704ab82d760105',
        output_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
        source_bytes=134217728, output_bytes=rom.stat().st_size,
        patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest())
    vendors = '\n'.join((VENDOR/name).read_text() for name in
        ['HashCalculator.js','BinFile.js','RomPatcher.format.vcdiff.js'])
    worker = vendors + '''
function adler32(file, offset, length) {
  return HashCalculator.adler32(file._u8array.buffer, offset, length);
}
async function sha256(buffer) {
  const hash = await crypto.subtle.digest('SHA-256', buffer);
  return Array.from(new Uint8Array(hash), b=>b.toString(16).padStart(2,'0')).join('');
}
self.onmessage = async ({data}) => {
  try {
    if (data.rom.byteLength !== data.manifest.source_bytes)
      throw new Error('Select the original, unmodified USA HeartGold .nds file.');
    self.postMessage({status:'Checking your original file…'});
    if (await sha256(data.rom) !== data.manifest.source_sha256)
      throw new Error('This is not the supported unmodified USA HeartGold ROM. Please select your original file, rather than an earlier prototype.');
    self.postMessage({status:'Building your playable NDS locally…'});
    const result = VCDIFF.fromFile(new BinFile(data.patch)).apply(new BinFile(data.rom), true);
    if (await sha256(result._u8array.buffer) !== data.manifest.output_sha256)
      throw new Error('The finished file did not pass verification. No download was created.');
    self.postMessage({rom:result._u8array.buffer},[result._u8array.buffer]);
  } catch (error) {self.postMessage({error:error.message});}
};
'''
    data = dict(manifest=manifest, patch=base64.b64encode(patch.read_bytes()).decode(), worker=worker)
    # JSON resides in a non-executable script; escape closing-tag characters.
    encoded = json.dumps(data, ensure_ascii=True).replace('<','\\u003c')
    html = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; worker-src blob:; connect-src 'none'; img-src data:">
<title>Pokémon Psyduck Yellow — Playtest download</title>
<style>body{font:18px/1.55 system-ui;max-width:650px;margin:40px auto;padding:0 24px;color:#222;background:#fff9e7}h1{font-size:30px}button,a.download{font:inherit;background:#294f35;color:white;padding:14px 22px;border:0;border-radius:8px;display:inline-block;margin:16px 0}button:disabled{opacity:.6}input{display:block;width:100%;margin:18px 0}small{font-size:14px}#status{min-height:56px}footer{margin-top:50px;font-size:14px}</style>
<h1>Pokémon Psyduck Yellow</h1><p>Opening playtest · Prototype 004</p>
<p>Select your original USA HeartGold <strong>.nds</strong> file, then press the button to create your playable prototype.</p>
<p>Your original file stays on your device. It is never uploaded or changed.</p>
<label for="rom">Original HeartGold file</label><input id="rom" type="file" accept=".nds">
<button id="build" disabled>Create my playable NDS</button>
<p id="status" role="status" aria-live="polite">Select your original file to begin.</p>
<a id="download" class="download" hidden>Download prototype 004.nds</a>
<p>Open the downloaded NDS in your Android DS emulator. Start a <strong>new game</strong> to test the revised opening. Keep earlier saves backed up.</p>
<small>This is an opening prototype, not a complete Yellow remake. The route remains blocked beyond the first testing area. Oak’s Psyduck capture currently uses field animation.</small>
<footer>Unofficial fan prototype. Pokémon belongs to its respective owners. This page distributes a modification patch, not the original game.<br>Local patch decoder: RomPatcher.js by Marc Robledo, MIT license. <a href="LICENSE.txt">License</a></footer>
<script id="package" type="application/json">PACKAGE</script>
<script>
const config=JSON.parse(document.getElementById('package').textContent);
const input=document.getElementById('rom'), button=document.getElementById('build');
const status=document.getElementById('status'), download=document.getElementById('download');
let outputUrl=null;
input.addEventListener('change',()=>{button.disabled=!input.files.length;download.hidden=true;status.textContent='Ready to create your prototype.';});
button.addEventListener('click',async()=>{
  button.disabled=true;input.disabled=true;download.hidden=true;
  let worker=null, workerUrl=null;
  function finish(){worker?.terminate();if(workerUrl)URL.revokeObjectURL(workerUrl);button.disabled=false;input.disabled=false;}
  try {
    if(!globalThis.crypto?.subtle || !globalThis.Worker)throw new Error('Open this page in a current Chrome or Firefox browser using HTTPS.');
    status.textContent='Reading your original file…';
    const rom=await input.files[0].arrayBuffer();
    const patch=Uint8Array.from(atob(config.patch),c=>c.charCodeAt(0)).buffer;
    workerUrl=URL.createObjectURL(new Blob([config.worker],{type:'text/javascript'}));
    worker=new Worker(workerUrl);
    worker.onerror=()=>{status.textContent='The browser could not complete the build. Close other tabs and try again.';finish();};
    worker.onmessage=({data})=>{
      if(data.status)status.textContent=data.status;
      else if(data.error){status.textContent=data.error;finish();}
      else if(data.rom){
        if(outputUrl)URL.revokeObjectURL(outputUrl);
        outputUrl=URL.createObjectURL(new Blob([data.rom],{type:'application/octet-stream'}));
        download.href=outputUrl;download.download='Pokemon-Psyduck-Yellow-prototype-004.nds';download.hidden=false;
        status.textContent='Your prototype passed verification. Tap Download below.';finish();
      }
    };
    worker.postMessage({rom,patch,manifest:config.manifest},[rom,patch]);
  } catch(error){status.textContent=error.message;finish();}
});
</script></html>'''.replace('004', version).replace('PACKAGE', encoded)
    if version in ('005', '006', '007', '008', '009', '010', '011'):
        html=html.replace('Start a <strong>new game</strong> to test the revised opening. Keep earlier saves backed up.',
            'Start a <strong>new game</strong> to test the opening, or import a backed-up prototype 004 normal save through your emulator. Emulator save states should not be transferred between builds.')
    if version == '006':
        html=html.replace('Opening playtest · Prototype 006','Evolution playtest · Prototype 006')
        html=html.replace('a backed-up prototype 004 normal save','a backed-up prototype 004 or 005 normal save')
        html=html.replace('Oak’s Psyduck capture currently uses field animation.',
            'Reopen the bedroom PC to receive 95 of each evolution item. Make space in storage if prompted, then reopen it to collect the remainder.')
    if version in ('007', '008', '009', '010', '011'):
        html=html.replace(f'Opening playtest · Prototype {version}',f'Oak’s Parcel playtest · Prototype {version}')
        html=html.replace('a backed-up prototype 004 normal save','a backed-up prototype 004, 005, 006 or 007 normal save')
        html=html.replace('The route remains blocked beyond the first testing area. Oak’s Psyduck capture currently uses field animation.',
            'Route 1 now opens after Mom gives you Running Shoes. The cashier greets you outside Viridian and escorts you into the Mart. Deliver Oak’s Parcel to receive the National Pokédex. Areas beyond Viridian remain blocked. Imported saves keep their caught records, but Pokédex access waits for parcel delivery. Evolution supplies remain available in the player’s PC.')
    if version == '009':
        html=html.replace('Oak’s Parcel playtest · Prototype 009','Intro playtest · Prototype 009')
        html=html.replace('a backed-up prototype 004, 005, 006 or 007 normal save','a backed-up prototype 004–008 normal save')
        html=html.replace('Start a <strong>new game</strong> to test the opening','Start a <strong>new game</strong> to see FireRed Blue’s full portrait and Oak’s shiny Eevee release with sparkles and sound')
    if version in ('010','011'):
        html=html.replace(f'Oak’s Parcel playtest · Prototype {version}',f'Viridian tutorial playtest · Prototype {version}')
        html=html.replace('a backed-up prototype 004, 005, 006 or 007 normal save','a backed-up prototype 004–009 normal save')
        html=html.replace('Evolution supplies remain available in the player’s PC.', 'Oak walks to collect the two visible Pokédexes before giving them out. The last starter ball has its own message. Viridian’s old man blocks the northern path before the Pokédex, then shows a catching demonstration and steps aside. Route 2 and Viridian Forest remain closed for the next prototype. Evolution supplies remain in the player’s PC. Use a new game or a save made before parcel delivery to see the revised Oak scene.')
    if version == '011':
        html=html.replace('Viridian tutorial playtest · Prototype 011','Opening corrections playtest · Prototype 011')
        html=html.replace('prototype 004–009 normal save','prototype 004–010 normal save')
        html=html.replace('Viridian’s old man blocks the northern path before the Pokédex, then shows a catching demonstration and steps aside.', 'Viridian’s old man lies in the center lane; invisible barriers close both side lanes and prevent walking around him. After the Pokédex, he stands, demonstrates catching, and walks aside. Blue’s full portrait appears in the touch-screen panel during his introduction and name confirmation. Eevee and its sparkles share Marill’s original resting position. Start a new game to check the intro.')
    # hidden must override display on the downloadable link.
    html=html.replace('footer{margin-top', '[hidden]{display:none!important}footer{margin-top')
    (destination/'index.html').write_text(html)
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (destination/'LICENSE.txt').write_text((VENDOR/'LICENSE').read_text())
    print(json.dumps(manifest,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('destination',type=Path)
    parser.add_argument('--version',choices=['004','005','006','007','008','009','010','011'],default='004')
    args=parser.parse_args()
    build(args.destination,args.version)
