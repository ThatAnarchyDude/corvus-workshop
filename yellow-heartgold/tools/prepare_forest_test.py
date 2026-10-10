"""Create ignored native test fixtures; these event grants are never released."""
import argparse,json,struct,shutil
from pathlib import Path
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from opening import Script,script_bank
from parcel_quest import split_bank,PARCEL_STATE,BOUNDARY
from forest_progression import TABLE
POSITIONS={'battle':(147,44,73,3),'battle-win':(147,44,73,3),
           'south':(147,32,76,0),'north':(147,12,17,0)}
BOOT=[{'frames':1200},{'frames':15,'buttons':[8]},{'frames':400},{'frames':15,'buttons':[8]},{'frames':600},{'frames':15,'buttons':[8]},{'frames':600}]

def prepare(label,save):
    r=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-014.nds'));d=r.loadArm9().sections[0].data;sid=struct.unpack_from('<H',d,TABLE+505*24+6)[0];fid=r.filenames.idOf('a/0/1/2');a=ndspy.narc.NARC(r.files[fid]);bank=split_bank(a.files[sid]);s=Script().emit(96)
    for trainer in range(751,756):s.emit(37,trainer)
    if label=='battle-win':
        # Native GiveMon/ReturnLoanMon replace the single fixture party member.
        # A level-15 Eevee isolates battle completion from opening balance.
        s.emit(137,133,15,0,0,0,0x800C).emit(364,0).emit(282)
    s.emit(31,800+85).emit(31,800+87).emit(41,PARCEL_STATE,2).emit(41,BOUNDARY,0).emit(174,6,6,0,0).emit(175)
    mapid,x,z,facing=POSITIONS[label];s.emit(176,mapid,0,x,z,facing).emit(174,6,6,1,0).emit(175).emit(254,0x800C).emit(97).emit(2);bank[0]=s.finish();a.files[sid]=script_bank(bank);r.files[fid]=a.save()
    fixture=PROJECT/f'build/014-{label}-fixture.nds';r.saveToFile(str(fixture));out=PROJECT/f'build/emulator-014-{label}-prepare';out.mkdir(exist_ok=True);shutil.copyfile(save,out/fixture.with_suffix('.dsv').name)
    acts=BOOT+[{'frames':15,'buttons':[8]},{'frames':2500,'screenshot':'normal-saved.png'}];(PROJECT/f'build/014-{label}-prepare-actions.json').write_text(json.dumps(acts));print(fixture)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label',choices=POSITIONS);p.add_argument('save',type=Path);args=p.parse_args();prepare(args.label,args.save)
