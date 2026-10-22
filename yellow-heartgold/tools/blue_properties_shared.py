"""Share Blue's saved-starter wrapper without growing the DS ITCM allocation."""
import struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from keystone import Ks,KS_ARCH_ARM,KS_MODE_THUMB
from prototype import thumb_bl
OLD=0x01FFCCF8
LATEST=0x01FFF29C
CALL=0x01FFF2A4
GUARD=0x01FFF2B2
ELIGIBLE=0x01FFF2C2
FINISHED=0x01FFF3F8

def assemble(source,address):
 source='\n'.join(line.split('@')[0] for line in source.splitlines())
 data,_=Ks(KS_ARCH_ARM,KS_MODE_THUMB).asm(source,addr=address)
 raw=bytes(data)
 for i in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(raw,address):
  assert not (i.mnemonic.startswith('b') and i.mnemonic.endswith('.w')),'Thumb2 forbidden'
 return raw

def helper(first):
 return assemble(f'''movs r0,r3
ldr r1,old_first
subs r0,r0,r1
cmp r0,#9
bls yes
movs r0,r3
ldr r1,cerulean_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,r3
ldr r1,ship_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,#0
bx lr
yes:
movs r0,#1
bx lr
.align 2
old_first: .word 741
cerulean_first: .word 782
ship_first: .word {first}
''',OLD)

def patch(rom,first=809):
 main=rom.loadArm9();itcm=main.sections[1];assert itcm.ramAddress==0x01FF8000 and len(itcm.data)==32756
 source=Path('yellow-heartgold/asm/blue-starter-properties.s').read_text().replace('bl 0x0201FD44\nlsls r0, r0, #20','bl 0x01FFCA64\nlsls r0, r0, #20').replace('cmp r0, #8','cmp r0, #16')
 old=assemble(source,OLD);latest=assemble(source.replace('bl 0x02073604',f'bl {OLD}').replace('adds r1, #9','adds r1, #3').replace('first_trainer: .word 741','first_trainer: .word 782'),LATEST)
 assert bytes(itcm.data[OLD-itcm.ramAddress:OLD-itcm.ramAddress+len(old)])==old
 assert bytes(itcm.data[LATEST-itcm.ramAddress:LATEST-itcm.ramAddress+len(latest)])==latest
 assert bytes(main.sections[0].data[0x73440:0x73444])==thumb_bl(0x02073440,LATEST)
 references=[];pointer_references=[];blocks=[('arm9-'+str(i),s.ramAddress,bytes(s.data)) for i,s in enumerate(main.sections)]
 blocks += [('overlay-'+str(i),o.ramAddress,bytes(o.data)) for i,o in rom.loadArm9Overlays().items()]
 for name,address,raw in blocks:
  decoder=Cs(CS_ARCH_ARM,CS_MODE_THUMB);decoder.skipdata=True
  for insn in decoder.disasm(raw,address):
   if OLD<=insn.address<OLD+len(old):continue
   if insn.mnemonic in ('bl','blx','b') and insn.op_str.startswith('#'):
    target=int(insn.op_str[1:],0)
    if OLD<=target<OLD+len(old):references.append([name,insn.address,target])
  for offset in (0,2):
   data=raw[offset:len(raw)-((len(raw)-offset)%4)]
   for n,(value,) in enumerate(struct.iter_unpack('<I',data)):
    here=address+offset+n*4
    if OLD<=here<OLD+len(old):continue
    if OLD<=value&~1<OLD+len(old):pointer_references.append([name,here,value])
 assert references==[['arm9-1',CALL,OLD]],references
 assert not pointer_references,pointer_references
 code=helper(first);assert len(code)<=len(old)
 itcm.data=bytearray(itcm.data);itcm.data[OLD-itcm.ramAddress:OLD-itcm.ramAddress+len(code)]=code
 itcm.data[CALL-itcm.ramAddress:CALL-itcm.ramAddress+4]=thumb_bl(CALL,0x02073604)
 guard=assemble(f'bl {OLD}\ncmp r0,#0\nbne {ELIGIBLE}\nb {FINISHED}',GUARD);assert len(guard)<=16
 itcm.data[GUARD-itcm.ramAddress:GUARD-itcm.ramAddress+16]=guard+bytes.fromhex('c046')*((16-len(guard))//2)
 rom.arm9=main.save(compress=True)
 return dict(old_hook=OLD,latest_hook=LATEST,helper_bytes=len(code),reclaimable_old_bytes=len(old)-len(code),itcm_length=len(itcm.data),extra_itcm_bytes=0,eligible_ranges=[[741,750],[782,785],[first,first+3]],audited_external_calls=references,audited_pointer_references=pointer_references)
