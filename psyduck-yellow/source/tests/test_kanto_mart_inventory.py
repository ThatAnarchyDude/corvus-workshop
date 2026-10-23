import sys,struct,json,unittest,copy
from pathlib import Path
sys.path.insert(0,'yellow-heartgold/tools')
from kanto_mart_inventory import *
class KantoMartInventory(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=json.loads(Path('yellow-heartgold/data/kanto-mart-inventory.json').read_text());cls.source=cls.data['catalogs'];cls.stages=build_stages(cls.source)
 def test_exact_initial_unlocks_and_lavender_fourth_stage(self):
  expected=[{'ESCAPE_ROPE','AWAKENING'},{'REPEL'},{'SUPER_POTION','ICE_HEAL'},{'GREAT_BALL','REVIVE','SUPER_REPEL'},{'ULTRA_BALL','HYPER_POTION','FULL_HEAL'},{'MAX_REPEL'},set(),set()]
  for index,items in enumerate(expected,1):self.assertEqual(set(self.stages[index]['balls']+self.stages[index]['supplies'])-set(self.stages[index-1]['balls']+self.stages[index-1]['supplies']),items)
  self.assertEqual(self.stages[4]['added_from'],'Lavender')
 def test_every_native_badge_mask_ignores_johto_and_order(self):
  for mask in range(65536):
   count=(mask>>8).bit_count();self.assertEqual(kanto_badge_count(mask),count);self.assertEqual(stage_for_mask(self.stages,mask),self.stages[count])
 def test_compiled_badge_counter_all_65536_masks(self):
  code=badge_count_script();self.assertEqual(struct.unpack_from('<3H',code),(41,0x8004,0))
  for mask in range(65536):
   values={};at=0
   while at<len(code):
    op,a,b=struct.unpack_from('<3H',code,at);at+=6
    if op==41:values[a]=b
    elif op==294:self.assertIn(a,range(8,16));values[b]=(mask>>a)&1
    elif op==39:values[a]+=values[b]
    else:self.fail('Unexpected command')
   self.assertEqual(values[0x8004],(mask>>8).bit_count())
 def test_vendor_partition_cumulative_stock_and_exclusions(self):
  self.assertEqual(len(self.stages),9)
  for old,new in zip(self.stages,self.stages[1:]):self.assertLessEqual(set(old['balls']+old['supplies']),set(new['balls']+new['supplies']))
  for stage in self.stages:
   self.assertFalse(set(stage['balls'])&set(stage['supplies']));self.assertEqual(len(stage['balls']+stage['supplies']),len(set(stage['balls']+stage['supplies'])));self.assertFalse(FORBIDDEN.intersection(stage['balls']+stage['supplies']))
   self.assertFalse({'FULL_RESTORE','MAX_POTION'}.intersection(stage['supplies']))
  self.assertEqual(self.stages[3]['balls'],['POKE_BALL']);self.assertEqual(self.stages[4]['balls'],['POKE_BALL','GREAT_BALL']);self.assertEqual(self.stages[5]['balls'],['POKE_BALL','GREAT_BALL','ULTRA_BALL'])
 def test_invalid_mask_and_forbidden_stock_rejected(self):
  for value in (-1,65536):
   with self.assertRaises(ValueError):kanto_badge_count(value)
  for name in FORBIDDEN:
   source=copy.deepcopy(self.source);source['Lavender'].append(name)
   with self.assertRaises(ValueError):build_stages(source)
if __name__=='__main__':unittest.main()