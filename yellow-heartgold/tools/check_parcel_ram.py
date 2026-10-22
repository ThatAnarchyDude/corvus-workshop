"""Inspect live quest variables, key items, shoes and retained Dex records."""
import json
import struct
import sys
from pathlib import Path
from check_opening_ram import check
from parcel_quest import PARCEL_STATE, SHOES_STATE, CLERK_STATE, BALLS_GIVEN, QUEST_INIT


def inspect(path, species=133, *, dex_enabled=False, owned=None):
    report=check(path,species,dex_enabled=dex_enabled,owned=owned)
    ram=Path(path).read_bytes();fs=int(report['field']['address'],16)-0x02000000
    save=struct.unpack_from('<I',ram,fs+12)[0]-0x02000000
    def block(index):
        ident,_,offset=struct.unpack_from('<3I',ram,save+0x23014+index*16)
        assert ident==index
        return save+16+offset
    state=block(4)
    report['quest']={name:struct.unpack_from('<H',ram,state+2*(var-0x4000))[0]
                     for name,var in [('parcel',PARCEL_STATE),('shoes',SHOES_STATE),('cashier',CLERK_STATE)]}
    report['quest']['initialized']=bool(ram[state+0x2E0+QUEST_INIT//8]&(1<<(QUEST_INIT%8)))
    report['quest']['balls_given']=bool(ram[state+0x2E0+BALLS_GIVEN//8]&(1<<(BALLS_GIVEN%8)))
    report['pc_storage']=[dict(item=struct.unpack_from('<H',ram,state+2*(0x152+2*i))[0],
                               quantity=struct.unpack_from('<H',ram,state+2*(0x153+2*i))[0])
                           for i in range(10)]
    bag=block(3)
    report['bag_items']={item:count for item,count in
                         (struct.unpack_from('<2H',ram,bag+i*4) for i in range(486)) if item}
    dex=int(report['dex']['address'],16)-0x02000000
    report['dex']['seen']=[s for s in range(1,494)
                           if ram[dex+0x44+(s-1)//8]&(1<<((s-1)%8))]
    report['key_items']={item:count for item,count in
                         (struct.unpack_from('<2H',ram,bag+165*4+i*4) for i in range(50)) if item}
    avatar=struct.unpack_from('<I',ram,fs+0x40)[0]-0x02000000
    player_save=struct.unpack_from('<I',ram,avatar+0x38)[0]-0x02000000
    report['running_unlocked']=struct.unpack_from('<H',ram,player_save)[0]==1
    return report


if __name__=='__main__':
    print(json.dumps(inspect(sys.argv[1],dex_enabled='--delivered' in sys.argv),indent=2))
