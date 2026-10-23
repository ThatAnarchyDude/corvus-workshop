import sys,struct,json,unittest
from pathlib import Path
sys.path.insert(0,'yellow-heartgold/tools')
from kanto_mart_shared import vendor_script,IDS
class SharedMartScript(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stages=json.loads(Path('yellow-heartgold/data/kanto-mart-inventory.json').read_text())['verified_stages']
  cls.scripts={v:vendor_script(cls.stages,v) for v in ('balls','supplies')}
 def run_script(self,code,mask,choice):
  at=0;values={};comparison=None
  def words(n):
   nonlocal at
   result=struct.unpack_from('<'+'H'*n,code,at);at+=n*2;return result
  for _ in range(200):
   op=words(1)[0]
   if op in (96,97,104,54,746,747,50,53):pass
   elif op==73:words(1)
   elif op==20:self.assertEqual(words(1)[0],2011)
   elif op==749:at+=6
   elif op==751:words(3)
   elif op==752:values[0x800C]=choice
   elif op==17:
    var,value=words(2);comparison=values.get(var,0)==value
   elif op in (22,28):
    take=True
    if op==28:
     condition=code[at];at+=1;self.assertEqual(condition,1);take=comparison
    delta=struct.unpack_from('<i',code,at)[0];at+=4
    if take:at+=delta
   elif op==41:
    var,value=words(2);values[var]=value
   elif op==42:
    dst,src=words(2);values[dst]=values[src]
   elif op==294:
    badge,out=words(2);self.assertIn(badge,range(8,16));values[out]=(mask>>badge)&1
   elif op==39:
    dst,src=words(2);values[dst]+=values[src]
   elif op==276:
    var=words(1)[0];self.assertEqual(values[var],30);length=words(1)[0]
    items=words(length//2);self.assertEqual(items[-1],0xFFFF);return ('buy',items[:-1])
   elif op==782:return ('sell',())
   elif op in (438,440):words(2)
   elif op==2:return ('exit',())
   else:self.fail('Unexpected compiled command '+str(op))
  self.fail('Unbounded compiled script flow')
 def test_all_badge_masks_both_vendors_select_exact_cumulative_catalog(self):
  for mask in range(65536):
   stage=self.stages[(mask>>8).bit_count()]
   for vendor,code in self.scripts.items():
    expected=tuple(IDS[n] for n in stage[vendor])
    self.assertEqual(self.run_script(code,mask,0),('buy',expected))
 def test_sell_and_cancel_do_not_depend_on_badges_or_read_inline_stock(self):
  for code in self.scripts.values():
   for mask in (0,0xFF,0x100,0xFFFF):
    self.assertEqual(self.run_script(code,mask,1),('sell',()))
    for choice in (2,0xFF,0xFFFE):self.assertEqual(self.run_script(code,mask,choice),('exit',()))
if __name__=='__main__':unittest.main()