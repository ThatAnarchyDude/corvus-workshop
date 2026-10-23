"""Private fresh-game fixture that creates a normal save using native commands.

Used when a new cloud session has no retained emulator save. Never published.
The player still goes through the native new-game introduction and naming UI.
"""
import argparse
import struct
from pathlib import Path

import ndspy.narc
import ndspy.rom

from build_rom import PROJECT
from opening import Script, script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE


def prepare(source, target, mapid=475, x=8, z=12, facing=0):
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source))
    main=rom.loadArm9()
    d=main.sections[0].data=bytearray(main.sections[0].data)
    rec=TABLE+503*24
    sid=struct.unpack_from('<H',d,rec+6)[0]
    fid=rom.filenames.idOf('a/0/1/2')
    arc=ndspy.narc.NARC(rom.files[fid])
    bank=split_bank(arc.files[sid])
    s=Script().emit(96).emit(41,0x4000,1).emit(32,0xB21).jump('done',1)
    s.emit(137,133,5,0,0,0,0x800C).emit(282).emit(30,0x6A)
    for flag in range(0x11B,0x11F):s.emit(30,flag)
    s.emit(30,0xB21).emit(174,6,6,0,0).emit(175)
    s.emit(176,mapid,0,x,z,facing).emit(174,6,6,1,0).emit(175)
    s.emit(254,0x800C).label('done').emit(97).emit(2)
    entry=len(bank)+1
    bank.append(s.finish())
    reset=len(bank)+1
    bank.append(Script().emit(41,0x4000,0).emit(2).finish())
    new_sid=len(arc.files);arc.files.append(script_bank(bank))
    # Transition hooks are synchronous and cannot run dialog/warp/save tasks.
    # Start the interactive fixture through the native on-frame scene table.
    iid=len(arc.files)
    arc.files.append(struct.pack('<BHHBI',2,reset,0,1,1)+bytes(1)
                     +struct.pack('<3H',0x4000,0,entry)+bytes(2))
    struct.pack_into('<2H',d,rec+6,new_sid,iid)
    rom.files[fid]=arc.save();rom.arm9=main.save(compress=True)
    rom.saveToFile(str(target))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    parser.add_argument('target',type=Path)
    parser.add_argument('--map',type=int,default=475)
    parser.add_argument('--x',type=int,default=8)
    parser.add_argument('--z',type=int,default=12)
    args=parser.parse_args()
    prepare(args.source,args.target,args.map,args.x,args.z)
