"""Bill's failure/retry/save states, retained assets and Yellow trainer data."""
import json,os,struct,sys,unittest
from pathlib import Path
import ndspy.rom,ndspy.narc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from route25 import *
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP
from starter_properties import CMD_TABLE
from yellow_tms import MOVE_ENTRY,INDEX_ENTRY

def run(code,*,flags=(),variables=None,room=True,yes=True,x=3,z=6,choices=()):
    flags=set(flags);v=dict(variables or {});bag={};walks=[];shown=[];removed=[];messages=[];pics=[];sounds=[];pc=0;cmp=0;choices=iter(choices)
    def half():
        nonlocal pc
        n=struct.unpack_from('<H',code,pc)[0];pc+=2;return n
    for _ in range(3000):
        op=half()
        if op==2:return dict(flags=flags,vars=v,bag=bag,walks=walks,shown=shown,removed=removed,messages=messages,pictures=pics,sounds=sounds)
        if op in (96,97,104,50,53,79,95,82,175,77,453):pass
        elif op==174:half();half();half();half()
        elif op in (73,75,78,80,81):sounds.append((op,half()))
        elif op==3:half();half()
        elif op in (190,191,45):
            n=code[pc];pc+=1
            if op==45:messages.append(n)
        elif op==17:
            a,b=half(),half();cmp=(v.get(a,0)>b)-(v.get(a,0)<b)
        elif op==28:
            cond=code[pc];pc+=1;off=struct.unpack_from('<i',code,pc)[0];pc+=4
            if {0:cmp<0,1:cmp==0,5:cmp!=0}.get(cond,False):pc+=off
        elif op==22:off=struct.unpack_from('<i',code,pc)[0];pc+=4;pc+=off
        elif op==32:cmp=0 if half() in flags else 1
        elif op in (30,31):
            f=half()
            if op==30:flags.add(f)
            else:flags.discard(f)
        elif op==41:a,b=half(),half();v[a]=b
        elif op==63:v[half()]=0 if yes else 1
        elif op==125:
            a,b,out=half(),half(),half();v[out]=int(room)
            if room:bag[a]=bag.get(a,0)+b
        elif op==105:v[half()]=x;v[half()]=z
        elif op==100:shown.append(half())
        elif op==101:removed.append(half())
        elif op==94:
            obj=half();off=struct.unpack_from('<i',code,pc)[0];pc+=4;at=pc+off;arr=[]
            while True:
                mv,num=struct.unpack_from('<2H',code,at);at+=4
                if mv==254:break
                arr.append((mv,num))
            walks.append((obj,arr))
        elif op==69:pc+=4;out=half();v[out]=next(choices,4)
        elif op==70:half();half();half()
        elif op==71:pass
        elif op==452:pics.append(half());half()
        elif op==76:half();half()
        else:raise AssertionError((op,pc))
    raise AssertionError('Script failed to finish')

class Story(unittest.TestCase):
    def test_help_walks_into_chamber_and_waits_for_PC_including_decline(self):
        for yes in (True,False):
            for x,z in ((3,6),(4,5),(4,7),(5,6)):
                r=run(ask_bill(),yes=yes,x=x,z=z)
                self.assertEqual(r['vars'][PHASE],1);self.assertIn(HIDE_MON,r['flags']);self.assertEqual(r['removed'],[MON]);self.assertEqual(r['bag'],{})
                self.assertEqual(r['walks'][0][1],[(15,1),(12,2),(14,1),(12,1)] if (x,z)==(4,5) else [(12,3)])
    def test_PC_cannot_grant_ticket_before_Bill_enters(self):
        r=run(computer());self.assertEqual(r['messages'],[9]);self.assertEqual(r['bag'],{});self.assertNotIn(SEPARATED,r['flags'])
    def test_separation_visibly_walks_out_and_automatically_rewards(self):
        r=run(computer(),variables={PHASE:1})
        self.assertEqual(r['bag'],{TICKET:1});self.assertTrue({SEPARATED,TICKET_GIVEN,HIDE_MON} - {HIDE_MON} <= r['flags'])
        self.assertEqual(r['vars'][BILL_STATE],1);self.assertEqual(r['vars'][PHASE],2)
        self.assertEqual(r['shown'],[EMERGING,BILL]);self.assertEqual(r['walks'],[(EMERGING,[(13,2),(14,6),(13,2),(2,1)])])
        self.assertTrue({(73,1548),(73,1613),(73,1614),(78,1186)}<=set(r['sounds']))
    def test_full_bag_preserves_separation_and_allows_ticket_retry_once(self):
        r=run(computer(),variables={PHASE:1},room=False)
        self.assertIn(SEPARATED,r['flags']);self.assertNotIn(TICKET_GIVEN,r['flags']);self.assertEqual(r['bag'],{});self.assertEqual(r['vars'][BILL_STATE],1)
        retry=run(bill_talk(),flags=r['flags']);self.assertEqual(retry['bag'],{TICKET:1})
        repeat=run(bill_talk(),flags=retry['flags']);self.assertEqual(repeat['bag'],{});self.assertEqual(repeat['messages'],[7])
    def test_save_reload_restores_monster_inside_or_human_without_repeating(self):
        for variables,flags in (({},set()),({PHASE:1},{HIDE_MON}),({PHASE:2},{SEPARATED,TICKET_GIVEN})):
            r=run(house_init(),variables=variables,flags=flags)
            self.assertIn(HIDE_EMERGING,r['flags'])
            if SEPARATED in flags:self.assertNotIn(HIDE_BILL,r['flags']);self.assertIn(HIDE_MON,r['flags']);self.assertEqual(r['vars'][BILL_STATE],1)
            else:self.assertIn(HIDE_BILL,r['flags']);self.assertEqual(HIDE_MON in r['flags'],variables.get(PHASE)==1)
    def test_post_help_PC_browses_original_four_species_without_party_grants(self):
        r=run(computer(),flags={SEPARATED,TICKET_GIVEN},choices=(0,1,2,3,4))
        self.assertEqual(r['pictures'],[133,136,135,134]);self.assertEqual(r['bag'],{});self.assertNotIn(EMERGING,r['shown'])
        cancel=run(computer(),flags={SEPARATED,TICKET_GIVEN},choices=(0xFFFE,));self.assertEqual(cancel['pictures'],[]);self.assertEqual(cancel['bag'],{})

class Assets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0023.nds'))
        cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/os.environ.get('PROTOTYPE0024_ROM','build/0024-development-2.nds')))
        cls.report=json.loads((PROJECT/'build/0024-development-report.json').read_text())['route25']
    def archive(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
    def test_archive_prefixes_and_every_other_header_preserved(self):
        for p in ('a/0/1/2','a/0/3/2','a/0/5/5','a/0/5/6','a/0/4/1','a/0/6/5'):
            old=self.archive(self.old,p);self.assertEqual(old,self.archive(self.new,p)[:len(old)],p)
        a=self.old.loadArm9().sections[0].data;b=self.new.loadArm9().sections[0].data
        for m in range(540):
            if m not in (29,440):self.assertEqual(a[TABLE+24*m:TABLE+24*(m+1)],b[TABLE+24*m:TABLE+24*(m+1)],m)
        for p in ('a/0/4/0',):self.assertEqual(self.old.files[self.old.filenames.idOf(p)],self.new.files[self.new.filenames.idOf(p)])
    def test_exact_yellow_teams_and_daily_safe_flags(self):
        teams=[[p['species'] for p in t['team']] for t in self.report['trainers']]
        self.assertEqual(teams,[[66,74],[19,21],[95],[79],[32,29],[19,23],[74,74,66,74],[23,27],[43,16,43]])
        self.assertEqual([[p['level'] for p in t['team']] for t in self.report['trainers']],[[15,15],[15,15],[17],[17],[15,15],[14,14],[13]*4,[14,14],[13]*3])
        tr=self.archive(self.new,'a/0/5/5');pa=self.archive(self.new,'a/0/5/6')
        for t in self.report['trainers']:
            self.assertEqual(tr[t['id']][1],t['trainer_class']);self.assertLess(t['defeat_flag'],0xAA0)
            for i,p in enumerate(t['team']):
                row=struct.unpack_from('<BB3H4H',pa[t['id']],16*i);self.assertEqual((row[2],row[3],list(row[5:])),(p['level'],p['species'],p['moves']))
        self.assertTrue(all(f<0xAA0 for f in self.report['flags']));self.assertTrue({ROUTE_FRAME,HOUSE_FRAME,PHASE}.isdisjoint(range(0x4152,0x4166)))
    def test_route_terrain_warps_manual_sign_solid_ball_and_wild(self):
        h=self.report['route'];g=events_decode(self.archive(self.new,'a/0/3/2')[h['event']]);old=events_decode(self.archive(self.old,'a/0/3/2')[h['original']['event']])
        self.assertEqual(g[2],old[2]);self.assertEqual(g[3],[]);self.assertEqual(struct.unpack_from('<2H',g[0][0]),(2,0))
        item=g[1][-1];self.assertEqual(struct.unpack_from('<H',item,2)[0],87);self.assertEqual(struct.unpack_from('<H',item,8)[0],TM_TAKEN)
        wild=self.archive(self.new,'a/0/3/7')[self.report['wild']];self.assertEqual(wild[0],15);self.assertEqual(wild[1:6],bytes(5));self.assertEqual(wild[8:20],bytes([12,12,13,14,14,15,13,13,16,17,16,17]))
    def test_only_four_chamber_permissions_change_and_all_Bill_paths_walkable(self):
        h=self.report['house'];old=bytearray(self.archive(self.old,'a/0/6/5')[h['original_land']]);new=self.archive(self.new,'a/0/6/5')[h['land']]
        for x,z in ((4,3),(4,4),(10,3),(10,4)):struct.pack_into('<H',old,20+2*(z*32+x),0x0600)
        self.assertEqual(bytes(old),new)
        def walk(pos,moves,blocked=()):
            for op,n in moves:
                dx,dz={12:(0,-1),13:(0,1),14:(-1,0),15:(1,0)}[op]
                for _ in range(n):
                    pos=(pos[0]+dx,pos[1]+dz);self.assertNotIn(pos,blocked);self.assertFalse(struct.unpack_from('<H',new,20+2*(pos[1]*32+pos[0]))[0]&0x8000,pos)
            return pos
        self.assertEqual(walk((4,6),[(12,3)]),(4,3));self.assertEqual(walk((4,6),[(15,1),(12,2),(14,1),(12,1)],[(4,5)]),(4,3));self.assertEqual(walk((10,3),[(13,2),(14,6),(13,2)]),(4,7))
    def test_route_trainers_and_TM_approach_are_on_walkable_tiles(self):
        matrix=self.archive(self.new,'a/0/4/1')[0];lands=self.archive(self.new,'a/0/6/5');w,h,headers,heights,n=matrix[:5];at=5+n+w*h*(2*headers+heights)
        def permission(x,z):
            lid=struct.unpack_from('<H',matrix,at+2*(z//32*w+x//32))[0]
            return struct.unpack_from('<H',lands[lid],20+2*((z%32)*32+x%32))[0]
        for t in self.report['trainers']:self.assertFalse(permission(t['x'],t['z'])&0x8000)
        g=events_decode(self.archive(self.new,'a/0/3/2')[self.report['route']['event']]);x,z=struct.unpack_from('<2H',g[1][-1],24)
        self.assertEqual((x,z),(1368,36));self.assertFalse(permission(x,z)&0x8000);self.assertFalse(permission(x,z+1)&0x8000)
        for item in HIDDEN:self.assertFalse(permission(item['x'],item['z'])&0x8000)
    def test_Yellow_hidden_rewards_use_unique_native_ids_and_dowsing(self):
        g=events_decode(self.archive(self.new,'a/0/3/2')[self.report['route']['event']]);hidden=[r for r in g[0] if struct.unpack_from('<H',r,2)[0]==2]
        self.assertEqual([struct.unpack_from('<H',r)[0] for r in hidden],[8107,8199])
        main=self.new.loadArm9();base=int(self.report['hidden_table'],16)-main.sections[1].ramAddress
        for item in HIDDEN:
            rows=[struct.unpack_from('<HBBHH',main.sections[1].data,at) for at in range(base,base+231*8,8) if struct.unpack_from('<H',main.sections[1].data,at+6)[0]==item['script']-8000]
            self.assertEqual(len(rows),1);self.assertEqual(rows[0][:2],(item['item'],1))
    def native_lookup(self,rom,site,item):
        if not hasattr(self,'lookup_cores'):self.lookup_cores={}
        if id(rom) not in self.lookup_cores:
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
            for sec in rom.loadArm9().sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
            self.lookup_cores[id(rom)]=c
        c=self.lookup_cores[id(rom)]
        c.reg_write(UC_ARM_REG_R0,item);c.reg_write(UC_ARM_REG_SP,0x023F0000);c.reg_write(UC_ARM_REG_LR,0x023FF001);c.emu_start(site|1,0x023FF000,count=2000);return c.reg_read(UC_ARM_REG_R0)
    def test_new_TM_and_all_earlier_native_and_custom_lookups_preserved(self):
        for site,expected in ((MOVE_ENTRY,69),(INDEX_ENTRY,106)):
            self.assertEqual(self.native_lookup(self.new,site,TM_ITEM),expected)
            for item in range(537):
                if item!=TM_ITEM:self.assertEqual(self.native_lookup(self.old,site,item),self.native_lookup(self.new,site,item),(site,item))
        main=self.new.loadArm9();self.assertEqual(len(main.sections[1].data)%4,0);self.assertLess(len(main.sections[1].data),0x8000);self.assertEqual(struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0],main.sections[1].ramAddress+len(main.sections[1].data))
    def cpu(self):
        c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
        for sec in self.new.loadArm9().sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
        c.reg_write(UC_ARM_REG_SP,0x023F0000);c.reg_write(UC_ARM_REG_LR,0x023FF001);return c
    def test_native_daily_rollover_preserves_every_new_quest_and_reward_flag(self):
        c=self.cpu();flags=0x02300000;c.mem_write(flags,bytes([255])*1100+b'CHECKSUM')
        def hook(c,address,size,_):
            if address==0x020503D0:c.reg_write(UC_ARM_REG_R0,flags);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        c.hook_add(UC_HOOK_CODE,hook);c.reg_write(UC_ARM_REG_R0,0x02310000);c.emu_start(0x02040471,0x023FF000,count=1000)
        for f in self.report['flags']+[t['defeat_flag'] for t in self.report['trainers']]:self.assertTrue(c.mem_read(flags+0x2E0+f//8,1)[0]&(1<<(f%8)))
        self.assertEqual(bytes(c.mem_read(flags+0x2E0+0xAA0//8,12)),bytes(12));self.assertEqual(bytes(c.mem_read(flags+1100,8)),b'CHECKSUM')
    def test_new_refresh_markers_remove_only_their_local_actor_ids(self):
        for marker in (0x4D502429,0x4D5024BC):
            c=self.cpu();ctx,script,field,manager=0x02300000,0x02301000,0x02302000,0x02303000
            c.mem_write(ctx+8,struct.pack('<I',script));c.mem_write(ctx+128,struct.pack('<I',field));c.mem_write(field+60,struct.pack('<I',manager));c.mem_write(script,struct.pack('<I',marker));asked=[];removed=[]
            def hook(c,address,size,_):
                if address==0x0205EE60:
                    self.assertEqual(c.reg_read(UC_ARM_REG_R0),manager);ident=c.reg_read(UC_ARM_REG_R1);asked.append(ident);c.reg_write(UC_ARM_REG_R0,0x02304000+ident*256)
                elif address==0x0205E3CC:removed.append(c.reg_read(UC_ARM_REG_R0))
                else:return
                c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook);c.reg_write(UC_ARM_REG_R0,ctx);entry=struct.unpack_from('<I',self.new.loadArm9().sections[0].data,CMD_TABLE+4)[0];c.emu_start(entry,0x023FF000,count=3000)
            self.assertEqual(asked,list(range(32)));self.assertEqual(removed,[0x02304000+i*256 for i in range(32)]);self.assertEqual(struct.unpack('<I',c.mem_read(ctx+8,4))[0],script+4)

if __name__=='__main__':unittest.main()
