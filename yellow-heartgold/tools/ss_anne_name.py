"""Give the isolated Kanto ship copies their own appended location name."""
import struct
import ndspy.narc
from prototype import decode_messages,encode_messages
from opening import encode_text
from parcel_quest import PH
from viridian_tutorial import TABLE
SECTION=235
NAME_BANK=279
CLONES=(254,255)
def patch(rom):
 fid=rom.filenames.idOf('a/0/2/7');texts=ndspy.narc.NARC(rom.files[fid]);key,words=decode_messages(texts.files[NAME_BANK]);assert len(words)==SECTION
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 assert all(d[TABLE+mid*24+18]!=SECTION for mid in range(540))
 _,added=decode_messages(encode_text(['S.S. Anne'],PH));assert len(added)==1
 texts.files[NAME_BANK]=encode_messages(key,words+added)
 for mid in CLONES:
  assert d[TABLE+mid*24+18]==226
  d[TABLE+mid*24+18]=SECTION
 rom.files[fid]=texts.save();rom.arm9=main.save(compress=True)
 return {'section':SECTION,'name':'S.S. Anne','existing_aqua_name_preserved':True,'original_name_entries_preserved':SECTION,'clones':CLONES,'no_native_ship_preview_art_exists':True,'world_map_position_audit_pending':True,'native_name_test_pending':True}