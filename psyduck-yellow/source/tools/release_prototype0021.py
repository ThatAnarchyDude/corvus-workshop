"""Prepare a cumulative modification patch locally; never publishes a ROM."""
import json
import subprocess
from build_rom import PROJECT,BASE,EXPECTED,sha
from build_prototype0021 import build
from package_playtest import build as package


def prepare():
    target=PROJECT/'build/yellow-heartgold-prototype-0021.nds'
    patch=target.with_suffix('.xdelta')
    destination=PROJECT/'build/prototype-0021-web'
    if target.exists() or patch.exists() or destination.exists():
        raise FileExistsError('A prepared 0021 artifact exists; preserve it rather than overwrite it.')
    assert sha(BASE.read_bytes())==EXPECTED
    target,report=build('build/yellow-heartgold-prototype-0021.nds')
    decoded=PROJECT/'build/0021-release-roundtrip.nds'
    subprocess.run([str(PROJECT/'.tools/xdelta3'),'-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True)
    subprocess.run([str(PROJECT/'.tools/xdelta3'),'-d','-s',str(BASE),str(patch),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==report['output_sha256']
    package(destination,'0021')
    report.update(patch_sha256=sha(patch.read_bytes()),roundtrip_verified=True,
                  publication='Prepared locally only; requires final release validation')
    (PROJECT/'build/prototype-0021-release-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return target,destination,report


if __name__=='__main__':prepare()
