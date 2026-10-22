"""Private native gym fixture; event grants and teleport are never published."""
import argparse
import json
import shutil
import struct
from pathlib import Path

import ndspy.narc
import ndspy.rom

from build_rom import PROJECT
from opening import Script, script_bank
from parcel_quest import split_bank
from prepare_forest_test import BOOT
from viridian_tutorial import TABLE
from pewter_gym import GYM_MAP, TM_GIVEN


def prepare(label='gym', source=None):
    source = source or PROJECT/'build/pewter-city-development.nds'
    rom = ndspy.rom.NintendoDSRom.fromFile(str(source))
    d = rom.loadArm9().sections[0].data
    sid = struct.unpack_from('<H',d,TABLE+505*24+6)[0]
    fid = rom.filenames.idOf('a/0/1/2')
    arc = ndspy.narc.NARC(rom.files[fid])
    bank = split_bank(arc.files[sid])
    s = Script().emit(96)
    if label=='bide':
        s.emit(125,115,1,0x800C)
    else:
        species,level=(54,1) if label=='gym-loss' else (55,20)
        s.emit(137,species,level,0,0,0,0x800C).emit(364,0).emit(282)
    for trainer in (756,757):
        s.emit(37,trainer)
    s.emit(31,TM_GIVEN)
    if label!='bide':
        s.emit(174,6,6,0,0).emit(175)
        mapid,x,z,facing={'gym':(GYM_MAP,7,5,0),'gym-loss':(GYM_MAP,7,5,0),
                         'junior':(GYM_MAP,7,20,2),'route-guide':(51,1085,104,3),
                         'museum-guide':(51,1041,85,3)}[label]
        s.emit(176,mapid,0,x,z,facing).emit(174,6,6,1,0).emit(175)
    s.emit(254,0x800C).emit(97).emit(2)
    bank[0] = s.finish()
    arc.files[sid] = script_bank(bank)
    rom.files[fid] = arc.save()
    fixture = PROJECT/f'build/015-{label}-fixture.nds'
    rom.saveToFile(str(fixture))
    out = PROJECT/f'build/emulator-015-{label}-prepare'
    out.mkdir(exist_ok=True)
    shutil.copyfile(PROJECT/'build/emulator-010-lab/yellow-heartgold-prototype-010.dsv',
                    out/fixture.with_suffix('.dsv').name)
    actions = BOOT+[{'frames':15,'buttons':[8]},
                    {'frames':2200,'screenshot':'normal-save.png'}]
    (PROJECT/f'build/015-{label}-prepare-actions.json').write_text(json.dumps(actions))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('label',nargs='?',default='gym',choices=['gym','gym-loss','junior','route-guide','museum-guide','bide'])
    parser.add_argument('--source',type=Path)
    args=parser.parse_args()
    prepare(args.label,args.source)
