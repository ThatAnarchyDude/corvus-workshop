"""Offline proposed PC extension contract. NOT an installed game/save hook.

Functions copy byte buffers only; they never read or write owner save files.
Legacy ten stacks stay in saved vars; this tail adds fifty physical stacks.
Native dual-copy selection and atomic saving remain native-engine work.
"""
import binascii,struct
LEGACY_SIZE=0xF628
EXPANDED_SIZE=0xF700
FOOTER_SIZE=16
TAIL=LEGACY_SIZE-FOOTER_SIZE
NEW_FOOTER=EXPANDED_SIZE-FOOTER_SIZE
NATIVE_MAGIC=0x20060623
HEADER=struct.Struct('<4sHHII')
EXTENSION_MAGIC=b'PYPC'
EXTENSION_VERSION=1
EXTRA_STACKS=50

def capacity(kanto_badges):
 if not isinstance(kanto_badges,int) or not 0<=kanto_badges<=255:raise ValueError('Expected eight-bit Kanto badge mask')
 return 20+5*kanto_badges.bit_count()

def native_valid(data,size,expected_slot=0):
 if len(data)<size:return False
 count,stored_size,magic,slot,crc=struct.unpack_from('<IIIHH',data,size-16)
 return stored_size==size and magic==NATIVE_MAGIC and slot==expected_slot and binascii.crc_hqx(data[:size-16],65535)==crc

def extension_valid(data):
 if len(data)<EXPANDED_SIZE:return False
 if HEADER.unpack_from(data,TAIL)!=(EXTENSION_MAGIC,EXTENSION_VERSION,EXTRA_STACKS,0,0):return False
 for n in range(EXTRA_STACKS):
  item,qty=struct.unpack_from('<HH',data,TAIL+HEADER.size+4*n)
  if (item==0)!=(qty==0) or qty>999:return False
 return True

def normalize_general(data):
 """Return a normalized COPY and provenance; preserve storage/tail after F700.

Reject invalid checksums. Do not select between save copies here: native
selection also coordinates the general and Pokemon-storage block counters.
 """
 if len(data)<EXPANDED_SIZE:raise ValueError('Need complete general window through F700')
 if native_valid(data,EXPANDED_SIZE):
  if not extension_valid(data):raise ValueError('Unsupported or corrupt PC extension')
  return bytes(data),{'layout':'expanded','migrated':False,'count':struct.unpack_from('<I',data,NEW_FOOTER)[0]}
 if not native_valid(data,LEGACY_SIZE):raise ValueError('No valid supported general footer')
 count=struct.unpack_from('<I',data,TAIL)[0];out=bytearray(data)
 out[TAIL:NEW_FOOTER]=HEADER.pack(EXTENSION_MAGIC,EXTENSION_VERSION,EXTRA_STACKS,0,0)+bytes(EXTRA_STACKS*4)
 assert len(out)==len(data)
 struct.pack_into('<IIIHH',out,NEW_FOOTER,count,EXPANDED_SIZE,NATIVE_MAGIC,0,binascii.crc_hqx(out[:NEW_FOOTER],65535))
 assert native_valid(out,EXPANDED_SIZE) and extension_valid(out)
 return bytes(out),{'layout':'expanded','migrated':True,'count':count}

# Source-faithful reference for save.c selection. NO engine replacement.
# Invalid checks use None; valid checks carry their native u32 counter.
def counter_compare(first,second):
 if first==0xFFFFFFFF and second==0:return -1
 if first==0 and second==0xFFFFFFFF:return 1
 return (first>second)-(first<second)

def rank_copies(checks):
 if len(checks)!=2:raise ValueError('Exactly two native copies required')
 good=[i for i,v in enumerate(checks) if v is not None]
 if len(good)==2:return 2,(0,1) if counter_compare(*checks)>=0 else (1,0)
 if good:return 1,(good[0],2)
 return 0,(2,2)

def select_native_pair(general,storage):
 """Port of Save_GetSaveFilesStatus selection only; statuses match save.h.

Migration must preserve these counter decisions. This reference does not
perform flash I/O, emulate a native hook, or make invalid copies valid.
 """
 ng,(new,old)=rank_copies(general);ns,(snew,sold)=rank_copies(storage)
 if ng==0 and ns==0:return 0,None
 if ng==0 or ns==0:return 3,None
 if ng==2 and ns==2:
  if general[new]==storage[new]:return 1,new
  if general[old]!=storage[old]:return 3,None
  return 2,old
 if ng==1 and ns==2:
  return (2,new) if general[new]==storage[new] else (3,None)
 if ng==2 and ns==1:
  if general[new]==storage[new]:return 1,new
  if general[old]==storage[old]:return 2,old
  return 3,None
 if new==snew:
  if general[new]!=storage[snew]:raise ValueError('Native assertion: mismatched sole valid block counters')
  return 1,new
 return 3,None
