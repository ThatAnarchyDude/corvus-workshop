"""Reproduce the PRIVATE 0027 terrain/scenery/guard probe; not a release builder."""
import argparse,json
from pathlib import Path
import ndspy.rom
from build_rom import PROJECT,sha
from route5_terrain import patch_probe
from route5_doors import patch_probe_doors
from route5_materials import patch_probe_materials
from route5_props import patch_probe_props
from route5_mirror_materials import patch_probe_mirror_materials
from saffron_gates import patch as patch_gates
from route5_connections import patch_probe_connections
BASE_SHA='a848bd038f2aea75ea10bae692d24679da42f5f4cd1c54ef1ed442e340b6abe5'
def build(output,*,diagnostic=False,city_links=False):
 if not diagnostic:raise ValueError('Unfinished private layout requires diagnostic=True')
 target=(PROJECT/output).resolve();report_path=target.with_suffix('.json')
 if not target.is_relative_to((PROJECT/'build').resolve()):raise ValueError('Private ROMs must remain under ignored build/')
 if target.exists() or report_path.exists():raise FileExistsError('Use new output paths')
 source=PROJECT/'build/0027-gates-development-v1.nds';assert sha(source.read_bytes())==BASE_SHA
 layout_path=PROJECT/'build/0027-route5-walking-reference-v1/topology.json';layout=json.loads(layout_path.read_text());rom=ndspy.rom.NintendoDSRom.fromFile(str(source))
 report=dict(private=True,released=False,baseline_sha256=BASE_SHA,baseline_already_has_guards=True,layout_sha256=sha(layout_path.read_bytes()))
 report['terrain']=patch_probe(rom,layout,diagnostic=True);report['doors']=patch_probe_doors(rom,diagnostic=True);report['materials']=patch_probe_materials(rom,diagnostic=True);report['props']=patch_probe_props(rom,diagnostic=True,scenery=True);report['mirror_resources']=patch_probe_mirror_materials(rom,diagnostic=True)
 # Reapply after door edits, retaining both new Route 5 return anchors.
 report['guards']=patch_gates(rom)
 if city_links:report['city_links']=patch_probe_connections(rom,diagnostic=True)
 report['pending']=['city connections and matrix integration','legacy saved-coordinate migration','trees and ledge geometry','Yellow gate interior','cloned door animation verification','Fly/follower/camera tests','release recording and pristine-base patch']
 target.parent.mkdir(parents=True,exist_ok=True);rom.saveToFile(str(target));report['output_sha256']=sha(target.read_bytes());report_path.write_text(json.dumps(report,indent=2)+'\n');assert sha(source.read_bytes())==BASE_SHA
 return target,report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--diagnostic',action='store_true');p.add_argument('--city-links',action='store_true');a=p.parse_args();target,report=build(a.output,diagnostic=a.diagnostic,city_links=a.city_links);print(target);print(report['output_sha256'])
