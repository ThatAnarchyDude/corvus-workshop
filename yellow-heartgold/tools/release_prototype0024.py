"""Prepare 0024's cumulative patch and verify a pristine-base round trip."""
import json,subprocess
from build_rom import PROJECT,BASE,EXPECTED,sha
from build_prototype0024 import build
from package_playtest import build as package
def prepare():
    target=PROJECT/'build/yellow-heartgold-prototype-0024.nds';patch=target.with_suffix('.xdelta');destination=PROJECT/'build/prototype-0024-web'
    if any(p.exists() for p in (target,patch,destination)):raise FileExistsError('Existing checkpoints are never overwritten.')
    assert sha(BASE.read_bytes())==EXPECTED
    target,report=build('build/yellow-heartgold-prototype-0024.nds')
    decoded=PROJECT/'build/0024-release-roundtrip.nds'
    subprocess.run([str(PROJECT/'.tools/xdelta3'),'-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True)
    subprocess.run([str(PROJECT/'.tools/xdelta3'),'-d','-s',str(BASE),str(patch),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==report['output_sha256'];package(destination,'0024')
    report.update(patch_sha256=sha(patch.read_bytes()),roundtrip_verified=True,publication='Prepared locally; validation required before publication')
    (PROJECT/'build/prototype-0024-release-report.json').write_text(json.dumps(report,indent=2)+'\n');return target,destination,report
if __name__=='__main__':prepare()
