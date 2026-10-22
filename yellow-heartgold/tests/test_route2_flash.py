import sys,struct,json,unittest
from pathlib import Path
sys.path.insert(0,'yellow-heartgold/tools')
from route2_flash import aide,GIVEN,FLASH
from viridian_tutorial import TABLE
import ndspy.rom,ndspy.narc
class FlashRewardTests(unittest.TestCase):
 def execute(self,owned,capacity,flags):
  code=aide();pc=0;compare=0;values={};gifts=[];messages=[]
  def words(n):
   nonlocal pc
   v=struct.unpack_from('<'+'H'*n,code,pc);pc+=n*2;return v
  for _ in range(150):
   op=words(1)[0]
   if op in (96,97,104,50,53,79):pass
   elif op in (190,191):pc+=1
   elif op==78:words(1)
   elif op==45:messages.append(code[pc]);pc+=1
   elif op==32:compare=int(words(1)[0] in flags)
   elif op==246:values[words(1)[0]]=owned
   elif op==17:
    var,n=words(2);compare=values.get(var,0)-n
   elif op in (22,28):
    take=True
    if op==28:
     cond=code[pc];pc+=1;take={0:compare<0,1:compare==0,2:compare>0,3:compare<=0,4:compare>=0,5:compare!=0}[cond]
     # CheckFlag stores boolean directly; native condition1 means TRUE there.
     if prev_op==32:take=bool(compare) if cond==1 else not bool(compare)
    delta=struct.unpack_from('<i',code,pc)[0];pc+=4
    if take:pc+=delta
   elif op==125:
    item,n,out=words(3);self.assertEqual((item,n),(FLASH,1));values[out]=int(capacity)
    if capacity:gifts.append(item)
   elif op==30:flags.add(words(1)[0])
   elif op==2:return gifts,messages
   else:self.fail('Unexpected opcode '+str(op))
   prev_op=op
  self.fail('No end')
 def test_caught_opcode_matches_full_native_table(self):
  import re
  source=Path('private/hg-map-reference/src/data/fieldmap/script_cmd_table.h').read_text().split('gScriptCmdTable[] = {')[1].split('};')[0]
  commands=re.findall(r'^\s*(\w+),',source,re.M)
  self.assertEqual(commands.index('ScrCmd_CountNationalDexOwned'),246)
  self.assertEqual(commands[245],'ScrCmd_CountNationalDexSeen')
  self.assertIn(struct.pack('<2H',246,0x800C),aide())
 def test_caught_threshold_not_seen_or_badges(self):
  for owned in range(494):
   flags={0xA9F};gifts,msg=self.execute(owned,True,flags)
   self.assertEqual(gifts,[FLASH] if owned>=10 else []);self.assertEqual(GIVEN in flags,owned>=10);self.assertIn(0xA9F,flags)
 def test_full_bag_retry_and_one_time_reward(self):
  flags={0xA9E};self.assertEqual(self.execute(10,False,flags),([],[0,3]));self.assertEqual(flags,{0xA9E})
  self.assertEqual(self.execute(10,True,flags),([FLASH],[0,1,4]));self.assertEqual(self.execute(10,True,flags),([],[4]))
 def test_existing_script_bodies_and_other_entry_preserved(self):
  root=Path('yellow-heartgold/build');old=ndspy.rom.NintendoDSRom.fromFile(str(root/'0035-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0035.nds'));new=ndspy.rom.NintendoDSRom.fromFile(str(root/'0036-flash-v2/private-flash.nds'));report=json.loads((root/'0036-flash-v2/report.json').read_text())
  def arc(r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
  a=arc(old,'a/0/1/2')[report['original_script']];b=arc(new,'a/0/1/2')[report['script']];n=report['original_entries'];old_body=min(i*4+4+struct.unpack_from('<I',a,i*4)[0] for i in range(n));self.assertEqual(a[old_body:],b[old_body+4:old_body+4+len(a)-old_body])
  for i in range(1,n):self.assertEqual(struct.unpack_from('<I',b,i*4)[0],struct.unpack_from('<I',a,i*4)[0]+4)
  allowed={old.filenames.idOf(p) for p in ('a/0/1/2','a/0/2/7')}
  for i,(x,y) in enumerate(zip(old.files,new.files)):
   if i not in allowed:self.assertEqual(x,y,f'file{i}')
  x=old.loadArm9();y=new.loadArm9();expected=bytearray(x.sections[0].data)
  for at,size in ((x.codeSettingsOffs+20,4),(TABLE+418*24+6,2),(TABLE+418*24+10,2)):expected[at:at+size]=y.sections[0].data[at:at+size]
  self.assertEqual(expected,y.sections[0].data)
if __name__=='__main__':unittest.main()

