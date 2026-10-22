"""Reproduce the PRIVATE compact connected Route5 probe; not a release builder."""
import argparse,json
from pathlib import Path
import ndspy.rom
from build_rom import PROJECT,sha
from route5_connected import patch_connected_probe
BASE_SHA='a848bd038f2aea75ea10bae692d24679da42f5f4cd1c54ef1ed442e340b6abe5'
def build(output,*,diagnostic=False,native_trees=False,visible_ledges=False,north_access=False,native_fences=False,north_wall=False):
 if not diagnostic:raise ValueError('Unfinished connected scenery requires diagnostic=True')
 target=(PROJECT/output).resolve();report_path=target.with_suffix('.json')
 if not target.is_relative_to((PROJECT/'build').resolve()):raise ValueError('Keep private ROMs under ignored build/')
 if target.exists() or report_path.exists():raise FileExistsError('Use a new output path')
 source=PROJECT/'build/0027-gates-development-v1.nds';assert sha(source.read_bytes())==BASE_SHA
 layoutpath=PROJECT/'build/0027-route5-walking-reference-v1/topology.json';layout=json.loads(layoutpath.read_text());rom=ndspy.rom.NintendoDSRom.fromFile(str(source));report=patch_connected_probe(rom,layout,diagnostic=True,native_trees=native_trees,visible_ledges=visible_ledges,north_access=north_access,native_fences=native_fences,north_wall=north_wall);report['source_sha256']=BASE_SHA;report['layout_sha256']=sha(layoutpath.read_bytes())
 report['pending']=([label for enabled,label in ((native_trees,'enable native trees'),(visible_ledges,'enable visible ledges'),(north_access,'enable verified northern access'),(native_fences,'enable native fence scenery')) if not enabled]+([] if north_wall else ['northern visual seam'])+['Yellow gate interior','additional legacy save positions','broader wild encounter and Fly/follower/camera checks','release recording and pristine-base patch verification'])
 target.parent.mkdir(parents=True,exist_ok=True);rom.saveToFile(str(target));report['output_sha256']=sha(target.read_bytes());report_path.write_text(json.dumps(report,indent=2)+'\n');assert sha(source.read_bytes())==BASE_SHA;return target,report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--diagnostic',action='store_true');p.add_argument('--native-trees',action='store_true',help='Include the private native-textured tree probe');p.add_argument('--visible-ledges',action='store_true',help='Include private low cliff geometry');p.add_argument('--north-access',action='store_true',help='Connect native side stairs to Yellow central approach');p.add_argument('--native-fences',action='store_true',help='Include native fence graphics at source boundary cells');p.add_argument('--north-wall',action='store_true',help='Probe visual cliff beneath the native city edge');a=p.parse_args();target,report=build(a.output,diagnostic=a.diagnostic,native_trees=a.native_trees,visible_ledges=a.visible_ledges,north_access=a.north_access,native_fences=a.native_fences,north_wall=a.north_wall);print(target);print(report['output_sha256'])
