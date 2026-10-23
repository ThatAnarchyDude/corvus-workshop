"""Minimal Yellow Vermilion Gym conversion; retain native puzzle/reward flow."""
import struct
import ndspy.narc
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

GYM_MAP = 365
# Yellow parties.asm: Sailor8, Gentleman3, Rocker1, LtSurge1.
TEAMS = {232: [(81,24)], 337: [(100,22),(81,22)],
         396: [(100,20),(100,20),(100,20)], 255: [(26,28)]}
SURGE_MOVES = (85,5,25,45)  # Thunderbolt, Mega Punch, Mega Kick, Growl.

def patch(rom, original):
    main=rom.loadArm9(); data=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/5/5','a/0/5/6')
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    base={p:ndspy.narc.NARC(original.files[original.filenames.idOf(p)]) for p in paths}
    scripts,texts,trainers,parties=(arcs[p] for p in paths)
    rec=TABLE+GYM_MAP*24
    assert struct.unpack_from('<H',data,rec+6)[0]==778
    assert struct.unpack_from('<H',data,rec+10)[0]==485
    assert scripts.files[778]==base[paths[0]].files[778]
    # Only reward operand changes; all native branch targets/puzzle/flags remain.
    script=bytearray(scripts.files[778]); assert script[909:911]==struct.pack('<H',361)
    struct.pack_into('<H',script,909,351)  # HG TM24 is Thunderbolt, as in Yellow.
    sid=len(scripts.files);scripts.files.append(script)
    struct.pack_into('<H',data,rec+6,sid)
    key,messages=decode_messages(texts.files[485])
    messages[4]=decode_messages(encode_text(["LT. SURGE: That TM contains THUNDERBOLT!\rTeach it to a compatible POKEMON."],PH))[1][0]
    tid=len(texts.files);texts.files.append(encode_messages(key,messages))
    struct.pack_into('<H',data,rec+10,tid)
    for trainer,team in TEAMS.items():
        assert trainers.files[trainer]==base[paths[2]].files[trainer]
        assert parties.files[trainer]==base[paths[3]].files[trainer]
        row=bytearray(trainers.files[trainer]);row[0]=1 if trainer==255 else 0
        row[3]=len(team);row[4:12]=bytes(8);row[16]=0
        trainers.files[trainer]=row
        packed=[]
        for species,level in team:
            part=struct.pack('<BB3H',128,0,level,species,0)
            if trainer==255:part+=struct.pack('<4H',*SURGE_MOVES)
            packed.append(part)
        parties.files[trainer]=b''.join(packed)
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return {'map':GYM_MAP,'script':sid,'text':tid,'teams':TEAMS,'reward_item':351,
            'native_puzzle_and_badge_flow':'preserved','native_playtest':'pending',
            'deferred':'Junior names/class artwork and broader dialogue polish'}
