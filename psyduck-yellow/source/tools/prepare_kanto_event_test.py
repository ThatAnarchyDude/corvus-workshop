"""Generate isolated, ignored Kanto event fixtures from an owner save copy.

Never alters the input ROM/save. Test transport and optional drink grants are
excluded from development/release ROMs and must be labeled in recordings.
"""
import argparse,json,struct,shutil
from pathlib import Path
import ndspy.rom,ndspy.narc
from build_rom import PROJECT,sha
from opening import Script,script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE
from saffron_gates import DRINKS,DRINK_GIVEN
POSITIONS={'gate-empty':(391,5,6,1),'gate-water':(391,5,6,1),'gate-soda':(391,5,6,1),'gate-lemon':(391,5,6,1),'gate-empty6':(389,5,8,0),'gate-empty7':(493,5,7,2),'gate-empty8':(390,6,7,3),'route5-sign':(13,1308,187,0),'gate-open6':(389,5,8,0),'gate-open7':(493,5,7,2),'gate-open8':(390,6,7,3)}

def prepare(source,save,output,mode,clear_drinks=0,source_map=29):
    if not 0 <= clear_drinks <= 999:raise ValueError('Invalid private drink preparation quantity')
    output=output.resolve()
    if not output.is_relative_to((PROJECT/'build').resolve()):raise ValueError('Private output must stay under ignored build/')
    if output.exists():raise FileExistsError('Use a new fixture directory')
    source_hash=sha(source.read_bytes());save_hash=sha(save.read_bytes())
    output.mkdir(parents=True)
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    # Input owner save is on Route 25 (map 29); a one-shot transition scene
    # transports it without rewriting any save bytes or using cross-ROM states.
    if not 0 <= source_map < 540 or not d[TABLE+source_map*24+20]&1:raise ValueError('Private transport must be on a Kanto map')
    rec=TABLE+source_map*24;sid=struct.unpack_from('<H',d,rec+6)[0]
    fid=rom.filenames.idOf('a/0/1/2');arc=ndspy.narc.NARC(rom.files[fid]);bank=split_bank(arc.files[sid])
    s=Script().emit(96).emit(41,0x4000,1)
    if mode.startswith('gate-empty') or mode in ('gate-water','gate-soda','gate-lemon'):
        s.emit(31,DRINK_GIVEN)
        # Quantity is explicit, fixture-only and must be checked in native RAM.
        if clear_drinks:
            for item in DRINKS:s.emit(126,item,clear_drinks,0x800C)
        if mode in ('gate-water','gate-soda','gate-lemon'):s.emit(125,{'gate-water':30,'gate-soda':31,'gate-lemon':32}[mode],2,0x800C)
    m,x,z,facing=POSITIONS[mode]
    s.emit(174,6,6,0,0).emit(175).emit(176,m,0,x,z,facing).emit(174,6,6,1,0).emit(175).emit(97).emit(2)
    entry=len(bank)+1;bank.append(s.finish());reset=len(bank)+1;bank.append(Script().emit(41,0x4000,0).emit(2).finish())
    ns=len(arc.files);arc.files.append(script_bank(bank));ni=len(arc.files)
    arc.files.append(struct.pack('<BHHBI',2,reset,0,1,1)+bytes(1)+struct.pack('<3H',0x4000,0,entry)+bytes(2))
    struct.pack_into('<2H',d,rec+6,ns,ni);rom.files[fid]=arc.save();rom.arm9=main.save(compress=True)
    target=output/f'{mode}-private-fixture.nds';rom.saveToFile(str(target));shutil.copy2(save,output/(target.stem+'.dsv'))
    report=dict(mode=mode,source_sha256=source_hash,save_sha256=save_hash,private_transport=True,clear_drink_quantity=clear_drinks,drink_grant=2 if mode in ('gate-water','gate-soda','gate-lemon') else 0,no_pokemon_grants=True,target_map=m)
    (output/'fixture.json').write_text(json.dumps(report,indent=2)+'\n')
    assert sha(source.read_bytes())==source_hash and sha(save.read_bytes())==save_hash
    print(target)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--save',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',choices=POSITIONS,required=True);p.add_argument('--clear-drinks',type=int,default=0);p.add_argument('--source-map',type=int,default=29);a=p.parse_args()
    prepare(a.rom,a.save,a.output,a.mode,a.clear_drinks,a.source_map)
