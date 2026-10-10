"""Route 3 balance, native trainer dispatch and cumulative preservation."""
import struct,sys,unittest
from pathlib import Path
from collections import Counter
import ndspy.rom,ndspy.narc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from route3 import patch, DATA
from viridian_tutorial import TABLE
from opening import events_decode
from parcel_quest import split_bank, BOUNDARY
from forest_progression import HG_WEIGHTS
from prototype import decode_messages
from pewter_museum import TICKET

class Route3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=str(PROJECT/'build/yellow-heartgold-prototype-0016.nds')
        cls.old=ndspy.rom.NintendoDSRom.fromFile(path);cls.new=ndspy.rom.NintendoDSRom.fromFile(path)
        cls.report=patch(cls.new);cls.d=cls.new.loadArm9().sections[0].data
    def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
    def test_eight_trainers_have_exact_yellow_species_levels_and_explicit_moves(self):
        expected=[[(10,10),(13,10),(10,10)],[(19,11),(23,11)],[(16,9),(16,9)],[(13,9),(14,9),(10,9),(11,9)],[(19,10),(32,10)],[(21,14)],[(10,11),(11,11)],[(39,14)]]
        self.assertEqual(len(self.report['trainers']),8)
        trainers=self.arc(self.new,'a/0/5/5');parties=self.arc(self.new,'a/0/5/6')
        for row,team in zip(self.report['trainers'],expected):
            header=trainers[row['id']];self.assertEqual((header[0],header[1],header[3]),(1,row['trainer_class'],len(team)))
            records=list(struct.iter_unpack('<BB3H4H',parties[row['id']]))
            self.assertEqual([(r[3],r[2]) for r in records],team)
            self.assertEqual([r[5:] for r in records],[tuple(p['moves']) for p in row['team']])
            self.assertTrue(all(r[4]==0 for r in records))
    def test_wild_species_levels_probabilities_match_yellow_in_all_time_periods(self):
        raw=self.arc(self.new,'a/0/3/7')[self.report['wild']]
        self.assertEqual(raw[:6],bytes([20,0,0,0,0,0]))
        expected=Counter()
        for p,w in zip(DATA['wild_slots'],(20,20,15,10,10,10,5,5,4,1)):expected[(p['level'],p['species'])]+=w
        for period in range(3):
            species=struct.unpack_from('<12H',raw,20+24*period);actual=Counter()
            for level,s,w in zip(raw[8:20],species,HG_WEIGHTS):actual[(level,s)]+=w
            self.assertEqual(actual,expected)
        self.assertEqual({p['species'] for p in DATA['wild_slots']},{19,21,27,56})
    def test_actor_positions_and_warps_preserved_without_inherited_items_or_extra_trainers(self):
        arc=self.arc(self.new,'a/0/3/2');g=events_decode(arc[self.report['event']]);old=events_decode(arc[self.report['originals']['event']])
        oldrows={struct.unpack_from('<H',r)[0]:r for r in old[1]}
        self.assertEqual(g[2],old[2]);self.assertEqual(g[3],[]);self.assertEqual(len(g[1]),9)
        for row in g[1]:self.assertEqual(row[24:],oldrows[struct.unpack_from('<H',row)[0]][24:])
        for trainer in self.report['trainers']:
            row=next(r for r in g[1] if struct.unpack_from('<H',r)[0]==trainer['actor'])
            self.assertEqual(struct.unpack_from('<H',row,10)[0],3000+trainer['id']-1)
            self.assertEqual(struct.unpack_from('<H',row,6)[0],1)
        self.assertFalse(any(struct.unpack_from('<H',r,2)[0] in (84,85,86,87) for r in g[1]))
        self.assertEqual(len(g[0]),1)
    def test_new_trainer_names_and_dialogue_indexes_keep_previous_entries(self):
        texts=self.arc(self.new,'a/0/2/7');oldtexts=self.arc(self.old,'a/0/2/7')
        for member in (728,729):
            a,b=decode_messages(oldtexts[member])[1],decode_messages(texts[member])[1];self.assertEqual(a,b[:len(a)])
        names=decode_messages(texts[729])[1]
        for row in self.report['trainers']:self.assertEqual(names[row['id']],[0xFFFF])
        table=self.arc(self.new,'a/0/5/7')[0];ofs=self.arc(self.new,'a/1/3/1')[0]
        for row in self.report['trainers']:
            at=struct.unpack_from('<H',ofs,2*row['id'])[0]
            self.assertEqual(list(struct.iter_unpack('<2H',table[at:at+12])),[(row['id'],i) for i in range(3)])
        self.assertIn('30 POKEMON',DATA['messages']['Route3Youngster2AfterBattleText'])
    def test_brock_gate_uses_badge_and_retains_museum_reset_and_city_events(self):
        scripts=self.arc(self.new,'a/0/1/2');bank=split_bank(scripts[self.report['city_script']])
        self.assertEqual(bank[-1][:4],struct.pack('<2H',31,TICKET))
        self.assertIn(struct.pack('<3H',294,8,0x800C),bank[-1]);self.assertIn(struct.pack('<3H',41,BOUNDARY,1),bank[-1])
        oldd=self.old.loadArm9().sections[0].data
        self.assertEqual(oldd[TABLE+51*24+16:TABLE+51*24+18],self.d[TABLE+51*24+16:TABLE+51*24+18])
        self.assertEqual(self.report['city_init'],struct.unpack_from('<H',self.d,TABLE+51*24+8)[0])
    def test_every_other_map_and_previous_event_party_wild_geometry_are_preserved(self):
        oldd=self.old.loadArm9().sections[0].data
        for m in range(540):
            if m not in (11,51):self.assertEqual(oldd[TABLE+m*24:TABLE+(m+1)*24],self.d[TABLE+m*24:TABLE+(m+1)*24])
        for p in ('a/0/1/2','a/0/3/2','a/0/5/5','a/0/5/6','a/0/3/7'):
            a,b=self.arc(self.old,p),self.arc(self.new,p);self.assertEqual(a,b[:len(a)])
        for p in ('a/0/4/1','a/0/6/5','a/1/4/8','a/0/4/2','a/0/4/3','a/1/0/8','a/0/8/1'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(p)],self.new.files[self.new.filenames.idOf(p)])
        self.assertEqual(self.old.arm7,self.new.arm7)
        self.assertEqual(bytes(self.old.loadArm9().sections[1].data),bytes(self.new.loadArm9().sections[1].data))

if __name__=='__main__':unittest.main()
