"""Compact shop adapter for inline, generated Kanto catalogs.

Installed only in the private shared-Mart candidate; no released ROM uses it. The caller supplies the
native context in r4 and resolved catalog ID in r0 at 02048176. Catalog 30 is
reserved for authored scripts: a u16 byte length followed by terminated items.
The adapter advances the script pointer over that data before native Mart_Init.
"""
import struct
from keystone import Ks,KS_ARCH_ARM,KS_MODE_THUMB
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
SITE=0x02048176
RESUME=0x02048184
NATIVE_TABLE=0x0210FA3C
CUSTOM=30

def inline_catalog(items):
 items=tuple(items)
 if not items or len(items)>=255 or any(not 0<x<0xFFFF for x in items):
  raise ValueError('Invalid terminated native shop catalog')
 if len(set(items))!=len(items) or set(items).intersection((1,16)):
  raise ValueError('Duplicate, Master Ball or Cherish Ball in catalog')
 raw=struct.pack('<'+'H'*(len(items)+1),*items,0xFFFF)
 return struct.pack('<H',len(raw))+raw

def assemble(address):
 source='''
mov r2,r0
ldr r0,[r4,#0x74]
mov r1,r4
adds r1,#0x80
ldr r1,[r1]
cmp r2,#30
bne native
ldr r2,[r4,#8]
ldrh r3,[r2]
adds r2,#2
adds r3,r2,r3
str r3,[r4,#8]
movs r3,#0
b done
native:
lsls r4,r2,#2
ldr r2,native_table
ldr r2,[r2,r4]
done:
bx lr
.balign 4
native_table: .word 0x0210FA3C
'''
 raw=bytes(Ks(KS_ARCH_ARM,KS_MODE_THUMB).asm(source,addr=address)[0])
 if len(raw)>44:raise ValueError('Adapter exceeds existing hook footprint')
 for i in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(raw[:-4],address):
  if i.size!=2:raise ValueError('Adapter requires unsupported widened instruction')
 return raw