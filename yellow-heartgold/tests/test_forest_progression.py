"""Yellow encounter probabilities, native trainers and preserved HG assets."""
import json,struct,sys,unittest
from collections import Counter
from pathlib import Path
import ndspy.rom,ndspy.narc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from forest_progression import *
from test_parcel_quest import QuestRun

class ForestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-013.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-014.nds'));cls.report=json.loads((PROJECT/'build/forest-progression-report.json').read_text());cls.main=cls.new.loadArm9().sections[0].data
    def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
    def events(self,m):return events_decode(self.arc(self.new,'a/0/3/2')[struct.unpack_from('<H',self.main,TABLE+24*m+16)[0]])
    def test_grass_tables_preserve_exact_yellow_species_level_probabilities_all_day(self):
        expected={10:{(19,3):20,(16,3):20,(19,4):15,(32,4):10,(29,4):10,(16,5):10,(32,6):5,(29,6):5,(16,7):5},147:{(10,3):20,(11,4):20,(10,4):15,(10,5):10,(16,4):10,(16,6):10,(10,6):5,(11,6):5,(16,8):4,(17,9):1}}
        for m in [10,414,147]:
            row=self.arc(self.new,'a/0/3/7')[self.main[TABLE+24*m]];self.assertEqual(list(row[:6]),[25,0,0,0,0,0])
            for period in range(3):
                got=Counter()
                for species,level,weight in zip(struct.unpack_from('<12H',row,20+24*period),row[8:20],HG_WEIGHTS):got[species,level]+=weight
                self.assertEqual(dict(got),expected[10 if m==414 else m])
    def test_five_trainers_have_yellow_teams_and_no_postgame_items(self):
        teams=[[(10,7),(10,7)],[(11,6),(10,6),(11,6)],[(29,6),(32,6)],[(10,8),(11,8)],[(10,10)]]
        for entry,wanted in zip(self.report['trainers'],teams):
            i=entry['id'];row=self.arc(self.new,'a/0/5/5')[i];party=self.arc(self.new,'a/0/5/6')[i]
            self.assertEqual((row[0],row[1],row[3]),(0,3 if i==753 else 6,len(wanted)));self.assertEqual(row[4:12],bytes(8));self.assertEqual(row[16],0)
            got=[(species,level) for difficulty,gender,level,species,capsule in struct.iter_unpack('<BB3H',party)];self.assertEqual(got,wanted)
    def test_native_trainer_vision_and_interaction_dispatch_to_correct_records(self):
        actors={struct.unpack_from('<H',a)[0]:struct.unpack('<6Hh5h2Hi',a) for a in self.events(147)[1]}
        for entry in self.report['trainers']:
            a=actors[entry['actor']];self.assertEqual(a[3],1);self.assertEqual(a[5]+1-3000,entry['id']);self.assertEqual(a[1],320 if entry['class']==3 else 318)
    def test_new_trainer_text_lookup_preserves_old_table_and_maps_intro_loss_after(self):
        oldtable=self.arc(self.old,'a/0/5/7')[0];newtable=self.arc(self.new,'a/0/5/7')[0];ofs=self.arc(self.new,'a/1/3/1')[0];self.assertEqual(newtable[:len(oldtable)],oldtable)
        oldmsgs=decode_messages(self.arc(self.old,'a/0/2/7')[728])[1];newmsgs=decode_messages(self.arc(self.new,'a/0/2/7')[728])[1];self.assertEqual(newmsgs[:len(oldmsgs)],oldmsgs)
        for entry in self.report['trainers']:
            start=struct.unpack_from('<H',ofs,entry['id']*2)[0]
            for k,suffix in enumerate(['BattleText','EndBattleText','AfterBattleText']):
                at=start+4*k;self.assertEqual(struct.unpack_from('<2H',newtable,at),(entry['id'],k));self.assertEqual(newmsgs[at//4],decode_messages(encode_text([DATA['messages'][entry['dialogue']+suffix]],PH))[1][0])
    def test_common_trainer_extension_preserves_existing_shared_bytecode(self):
        old=self.arc(self.old,'a/0/1/2')[953];new=self.arc(self.new,'a/0/1/2')[self.report['trainer_common_bank']];self.assertEqual(new[755*4:],old[740*4:])
        def target(b,i):return i*4+4+struct.unpack_from('<I',b,i*4)[0]
        for i in range(740):self.assertEqual(target(new,i)-target(old,i),60)
        for i in range(740,755):self.assertEqual(target(new,i),target(new,0))
    def test_route2_has_no_trainers_and_viridian_north_boundary_removed(self):
        for m in [10,414]:self.assertFalse(any(struct.unpack_from('<H',a,6)[0]==1 for a in self.events(m)[1]))
        self.assertFalse(any(struct.unpack_from('<Hhh',t)==(10,992,230) for t in self.events(50)[3]));self.assertTrue(any(struct.unpack_from('<Hhh',t)==(11,1001,224) for t in self.events(50)[3]))
    def test_native_hidden_item_table_works_for_potion_antidote_and_preserves_other_entries(self):
        old=self.old.loadArm9().sections[0].data;at=int(self.report['hidden_items']['original_table'],16)-0x2000000;raw=old[at:at+231*8];self.assertEqual(self.main[at:at+231*8],raw)
        sec=self.new.loadArm9().sections[1];pos=int(self.report['hidden_items']['active_table'],16)-sec.ramAddress;active=sec.data[pos:pos+231*8]
        for o,n in zip(struct.iter_unpack('<HBBHH',raw),struct.iter_unpack('<HBBHH',active)):
            self.assertEqual(n,((17 if o[-1]==85 else 18),*o[1:]) if o[-1] in [85,87] else o)
        bgs=[struct.unpack('<HHiiiH2x',b) for b in self.events(147)[0] if struct.unpack_from('<H',b,2)[0]==2];self.assertEqual([b[0] for b in bgs],[8085,8087])
    def test_pickups_are_once_only_and_retry_after_bag_full(self):
        code=pickup(17,ITEM_FLAGS[0],2,1);r=QuestRun(code).run();self.assertEqual(r.bag,{17:1});self.assertIn(ITEM_FLAGS[0],r.flags);self.assertEqual(r.messages,[2])
        again=QuestRun(code,flags=r.flags,bag=r.bag).run();self.assertEqual(again.bag,{17:1});self.assertEqual(again.messages,[])
        full=QuestRun(code,full=True).run();self.assertEqual(full.bag,{});self.assertNotIn(ITEM_FLAGS[0],full.flags);self.assertEqual(full.messages,[3])
    def test_original_events_scripts_parties_wild_tables_and_graphics_stay_archived(self):
        for p in ['a/0/1/2','a/0/3/2','a/0/5/5','a/0/5/6','a/0/3/7']:
            a,b=self.arc(self.old,p),self.arc(self.new,p);self.assertEqual(a,b[:len(a)])
        for p in ['a/1/2/0','a/0/3/1','a/0/6/5','a/0/8/1']:self.assertEqual(self.arc(self.old,p),self.arc(self.new,p))
        self.assertEqual(self.old.arm7,self.new.arm7);self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)
        a,b=self.old.loadArm9().sections[0].data,self.main
        for m in range(540):
            if m not in [10,50,147,414,419,420]+[r['map'] for r in self.report['removed_terrain_gates']]:self.assertEqual(a[TABLE+24*m:TABLE+24*(m+1)],b[TABLE+24*m:TABLE+24*(m+1)])
    def test_inherited_kanto_hm_objects_removed_but_johto_and_requested_trees_preserved(self):
        oldmain=self.old.loadArm9().sections[0].data
        for m in range(540):
            if not oldmain[TABLE+24*m+20]&1:
                self.assertEqual(oldmain[TABLE+24*m+16:TABLE+24*m+18],self.main[TABLE+24*m+16:TABLE+24*m+18])
                continue
            gates=[struct.unpack_from('<2H',a) for a in self.events(m)[1]
                   if struct.unpack_from('<H',a,2)[0] in (84,85,86)
                   and struct.unpack_from('<H',a,10)[0] in (10000,10001,10002)]
            self.assertEqual(gates,[(19,86),(20,86)] if m==50 else [])
    def test_gate_warps_are_unchanged_and_both_yellow_npcs_are_available(self):
        oldmain=self.old.loadArm9().sections[0].data
        for m in [147,419,420]:
            old=events_decode(self.arc(self.old,'a/0/3/2')[struct.unpack_from('<H',oldmain,TABLE+24*m+16)[0]]);new=self.events(m);self.assertEqual(new[2],old[2])
            if m!=147:self.assertEqual(len(new[1]),2)

if __name__=='__main__':unittest.main()
