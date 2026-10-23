import unittest
from test_pc_storage_layout import legacy
from pc_storage_layout import *

class RecoveryTests(unittest.TestCase):
 def test_native_counter_wrap_and_equal_copy_preference(self):
  self.assertEqual(rank_copies([0,0xFFFFFFFF]),(2,(0,1)))
  self.assertEqual(rank_copies([0xFFFFFFFF,0]),(2,(1,0)))
  self.assertEqual(rank_copies([7,7]),(2,(0,1)))
  self.assertEqual(counter_compare(1,0xFFFFFFFE),-1)
 def test_legacy_expanded_mix_preserves_selection_and_counters(self):
  for expanded_mask in range(4):
   counts=[]
   for i,count in enumerate((42,41)):
    data=legacy(count)
    if expanded_mask&(1<<i):data=normalize_general(data)[0]
    _,check=normalize_general(data);counts.append(check['count'])
   self.assertEqual(select_native_pair(counts,[42,41]),(1,0))
 def test_interrupted_write_falls_back_only_to_matching_pair(self):
  self.assertEqual(select_native_pair([42,41],[41,41]),(2,1))
  self.assertEqual(select_native_pair([42,41],[40,40]),(3,None))
  self.assertEqual(select_native_pair([None,41],[42,41]),(2,1))
  self.assertEqual(select_native_pair([42,41],[None,41]),(2,1))
 def test_missing_and_split_valid_copies_do_not_get_combined(self):
  self.assertEqual(select_native_pair([None,None],[None,None]),(0,None))
  self.assertEqual(select_native_pair([None,None],[1,1]),(3,None))
  self.assertEqual(select_native_pair([2,None],[None,2]),(3,None))
  self.assertEqual(select_native_pair([None,2],[None,2]),(1,1))
  with self.assertRaises(ValueError):select_native_pair([None,2],[None,3])
 def test_all_validity_masks_return_only_usable_coherent_pairs(self):
  for mask in range(16):
   g=[42 if mask&1 else None,41 if mask&2 else None]
   s=[42 if mask&4 else None,41 if mask&8 else None]
   status,index=select_native_pair(g,s)
   if index is not None:
    self.assertIn(status,(1,2));self.assertIsNotNone(g[index]);self.assertEqual(g[index],s[index])
   else:self.assertIn(status,(0,3))
if __name__=='__main__':unittest.main()
