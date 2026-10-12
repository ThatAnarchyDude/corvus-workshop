"""Cross-map trainer ownership, old-save refresh and robbed-house retry paths."""
import json, os, struct, sys, unittest
from pathlib import Path
import ndspy.rom, ndspy.narc
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_rom import PROJECT
from trainer_visibility import MARKER as VIS_MARKER
from cerulean_robbery import robber, city_init_prefix, SPAWN_HIDE, SCENE, DIG, TRAINER, land_start
from cerulean import THIEF_BEAT, THIEF_HIDE, BILL_STATE
from opening import Script, events_decode
from parcel_quest import split_bank
from viridian_tutorial import TABLE
from test_prototype0021 import run
from test_prototype0024 import run as init_run


class Story(unittest.TestCase):
    def test_defeat_does_not_award_TM_or_mark_quest_complete(self):
        r = run(robber(24), win=False)
        self.assertTrue(r['whiteout']);self.assertEqual(r['bag'], {})
        self.assertFalse({THIEF_BEAT, THIEF_HIDE} & r['flags'])

    def test_success_rewards_once_and_walks_away(self):
        r = run(robber(24))
        self.assertEqual(r['battles'], [TRAINER]);self.assertEqual(r['bag'], {DIG: 1})
        self.assertTrue({THIEF_BEAT, THIEF_HIDE, SPAWN_HIDE} <= r['flags'])
        self.assertEqual(r['messages'], list(range(24, 29)))
        self.assertEqual(r['walks'], [(31, [(15, 12)])])
        repeat = run(robber(24), flags=r['flags'], bag=r['bag'])
        self.assertEqual(repeat['bag'], {DIG: 1});self.assertEqual(repeat['battles'], [])

    def test_full_pocket_keeps_robber_and_retry_does_not_repeat_battle(self):
        r = run(robber(24), room=False)
        self.assertIn(THIEF_BEAT, r['flags']);self.assertNotIn(THIEF_HIDE, r['flags'])
        self.assertEqual(r['bag'], {});self.assertEqual(r['walks'], [])
        retry = run(robber(24), flags=r['flags'])
        self.assertEqual(retry['battles'], []);self.assertEqual(retry['bag'], {DIG: 1})

    def test_bill_and_reward_control_spawn_and_automatic_trigger(self):
        code = city_init_prefix() + Script().emit(2).finish()
        for bill, flags in ((0, ()), (1, ()), (1, (THIEF_BEAT,)), (1, (THIEF_HIDE,))):
            r = init_run(code, variables={BILL_STATE: bill}, flags=flags)
            self.assertEqual(SPAWN_HIDE in r['flags'], bill != 1 or THIEF_HIDE in flags)
            self.assertEqual(r['vars'][SCENE], int(bill != 1 or THIEF_BEAT in flags or THIEF_HIDE in flags))


class Assets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0024.nds'))
        cls.new = ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/os.environ.get('PROTOTYPE0025_ROM', 'build/yellow-heartgold-prototype-0025.nds')))
        cls.report = json.loads((PROJECT/'build/0025-development-report.json').read_text())
    def arc(self, rom, p):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]).files
    def cpu(self):
        c = Uc(UC_ARCH_ARM, UC_MODE_THUMB);c.mem_map(0x01FF8000, 0x8000);c.mem_map(0x02000000, 0x400000)
        for sec in self.new.loadArm9().sections[:2]:c.mem_write(sec.ramAddress, bytes(sec.data))
        c.reg_write(UC_ARM_REG_SP, 0x023F0000);c.reg_write(UC_ARM_REG_LR, 0x023FF001)
        return c
    def test_archives_and_all_other_maps_preserved(self):
        for p in ('a/0/1/2', 'a/0/2/7', 'a/0/3/2', 'a/0/4/1', 'a/0/6/5'):
            old = self.arc(self.old, p);self.assertEqual(self.arc(self.new, p)[:len(old)], old, p)
        for p in ('a/0/5/5', 'a/0/5/6', 'a/0/3/7', 'a/0/0/2', 'a/0/4/0'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(p)], self.new.files[self.new.filenames.idOf(p)], p)
        a, b = [r.loadArm9().sections[0].data for r in (self.old, self.new)]
        for m in range(540):
            if m not in (52, 429, 440):self.assertEqual(a[TABLE+m*24:TABLE+(m+1)*24], b[TABLE+m*24:TABLE+(m+1)*24], m)
        self.assertEqual(self.old.arm7, self.new.arm7)
    def test_aliases_match_real_trainers_and_local_script_lookup_stays_unambiguous(self):
        ev = self.arc(self.new, 'a/0/3/2');d = self.new.loadArm9().sections[0].data
        city = events_decode(ev[struct.unpack_from('<H', d, TABLE+52*24+16)[0]])[1]
        route = events_decode(ev[struct.unpack_from('<H', d, TABLE+28*24+16)[0]])[1]
        aliases = [a for a in city if struct.unpack_from('<H', a, 10)[0] == 0xFFFF]
        self.assertEqual(len(aliases), 3)
        for alias in aliases:
            obj = struct.unpack_from('<H', alias)[0]
            real = next(a for a in route if struct.unpack_from('<H', a)[0] == obj)
            self.assertEqual(alias[:8], real[:8]);self.assertEqual(alias[12:], real[12:])
            self.assertEqual(struct.unpack_from('<2H', alias, 8), (28, 0xFFFF))
        local = [struct.unpack_from('<H', a)[0] for a in city if struct.unpack_from('<H', a, 10)[0] != 0xFFFF]
        self.assertEqual(len(local), len(set(local)))
    def test_native_sight_classification_skips_aliases_and_preserves_all_real_types(self):
        for alias in (False, True):
            for typ in range(9):
                c = self.cpu();obj = 0x02300000
                c.mem_write(obj, struct.pack('<I', 1 | ((1<<25) if alias else 0)))
                c.mem_write(obj+24, struct.pack('<I', typ));c.reg_write(UC_ARM_REG_R0, obj)
                c.emu_start(0x02064299, 0x023FF000, count=1000)
                self.assertEqual(c.reg_read(UC_ARM_REG_R0), 0 if alias else typ if typ < 4 else 1)
    def test_missing_saved_aliases_added_without_duplicates_or_local_id_conflicts(self):
        for present in (0, 1, 3):
            c = self.cpu();ctx, fs, mgr, objs, script = [0x02300000 + n*0x10000 for n in range(5)]
            c.mem_write(ctx+8, struct.pack('<I', script));c.mem_write(ctx+128, struct.pack('<I', fs))
            c.mem_write(fs+60, struct.pack('<I', mgr));c.mem_write(mgr+4, struct.pack('<I', 20))
            c.mem_write(mgr+0x124, struct.pack('<I', objs));c.mem_write(script, struct.pack('<I', VIS_MARKER))
            # Local city actors have matching IDs, but must not mask missing aliases.
            for i in range(3):
                off = objs+i*300;c.mem_write(off, struct.pack('<I', 1));c.mem_write(off+8, struct.pack('<I', i))
            for i in range(present):
                off = objs+(i+3)*300;c.mem_write(off, struct.pack('<I', 1|(1<<25)))
                c.mem_write(off+8, struct.pack('<I', i));c.mem_write(off+28, struct.pack('<I', 28))
            made = []
            def hook(c, addr, size, _):
                if addr == 0x0205E1D0:
                    self.assertEqual(c.reg_read(UC_ARM_REG_R0), mgr);self.assertEqual(c.reg_read(UC_ARM_REG_R2), 52)
                    row = bytes(c.mem_read(c.reg_read(UC_ARM_REG_R1), 32));made.append(struct.unpack_from('<H', row)[0])
                    self.assertEqual(struct.unpack_from('<2H', row, 8), (28, 0xFFFF))
                    c.reg_write(UC_ARM_REG_R0, objs+3000);c.reg_write(UC_ARM_REG_PC, c.reg_read(UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook);c.reg_write(UC_ARM_REG_R0, ctx)
            c.emu_start(int(self.report['visibility']['saved_actor_refresh']['hook'], 16)|1, 0x023FF000, count=10000)
            self.assertEqual(made, list(range(present, 3)))
            self.assertEqual(struct.unpack('<I', c.mem_read(ctx+8, 4))[0], script+4)
    def test_original_rocket_team_and_new_dialogue_links(self):
        tr = self.arc(self.new, 'a/0/5/5')[TRAINER];party = self.arc(self.new, 'a/0/5/6')[TRAINER]
        self.assertEqual(tr[1], 55);self.assertEqual(tr[3], 2)
        self.assertEqual([(struct.unpack_from('<H', party, 16*i+4)[0], struct.unpack_from('<H', party, 16*i+2)[0]) for i in range(2)], [(66,17), (96,17)])
        r = self.report['robbery'];bank = split_bank(self.arc(self.new, 'a/0/1/2')[r['city']['script']])
        self.assertEqual(bank[r['city']['thief_entry']-1], robber(r['city']['first_message']))
        self.assertLess(SPAWN_HIDE, 0xAA0);self.assertNotIn(SCENE, range(0x4152, 0x4166))
    def test_rear_exit_and_native_permissions_preserve_room_furniture_and_front_door(self):
        h = self.report['robbery']['house'];lands = self.arc(self.new, 'a/0/6/5')
        old, new = lands[h['old_land']], lands[h['land']]
        p, b = struct.unpack_from('<2I', old);base = land_start(old)
        self.assertEqual(old[base+p:base+p+b], new[base+p:base+p+b])
        perms = bytearray(old[base:base+p]);struct.pack_into('<H', perms, 2*(3*32+6), 0x64)
        self.assertEqual(bytes(perms), new[base:base+p])
        ev = self.arc(self.new, 'a/0/3/2');hg = events_decode(ev[h['event']]);original = events_decode(ev[h['original_event']])
        self.assertEqual(hg[2][0], original[2][0]);self.assertEqual(struct.unpack('<4Hi', hg[2][1]), (6,3,52,8,0))
        cg = events_decode(ev[self.report['robbery']['city']['event']])
        self.assertEqual(struct.unpack('<4Hi', cg[2][-1]), (1305,112,429,1,0))
    def test_startup_extension_stays_aligned_within_ITCM(self):
        m = self.new.loadArm9();self.assertEqual(len(m.sections[1].data)%4, 0)
        self.assertLess(len(m.sections[1].data), 0x8000)
        self.assertEqual(struct.unpack_from('<I', m.sections[0].data, 0xD2C68)[0], m.sections[1].ramAddress+len(m.sections[1].data))
    def test_daily_rollover_preserves_robbery_flags(self):
        c = self.cpu();flags = 0x02300000
        c.mem_write(flags, bytes([255])*1100+b'CHECKSUM')
        def hook(c, address, size, _):
            if address == 0x020503D0:
                c.reg_write(UC_ARM_REG_R0, flags);c.reg_write(UC_ARM_REG_PC, c.reg_read(UC_ARM_REG_LR))
        c.hook_add(UC_HOOK_CODE, hook);c.reg_write(UC_ARM_REG_R0, 0x02310000)
        c.emu_start(0x02040471, 0x023FF000, count=1000)
        for f in (THIEF_BEAT, THIEF_HIDE, SPAWN_HIDE, 0x550+TRAINER):
            self.assertTrue(c.mem_read(flags+0x2E0+f//8, 1)[0] & (1<<(f%8)))
    def test_bill_computer_is_a_native_solid_prop_without_changing_machine_script(self):
        p = self.report['bill_pc'];lands = self.arc(self.new, 'a/0/6/5');raw = lands[p['land']]
        base = land_start(raw);ps, bs = struct.unpack_from('<2I', raw)
        row = raw[base+ps+bs-48:base+ps+bs]
        self.assertEqual(struct.unpack_from('<I', row)[0], 138)
        self.assertEqual(struct.unpack_from('<3i', row, 4), (-884736, 0, -557056))
        self.assertTrue(struct.unpack_from('<H', raw, base+2*(7*32+2))[0]&0x8000)
        for off in (6,8,10,16):
            old = self.old.loadArm9().sections[0].data;new = self.new.loadArm9().sections[0].data
            self.assertEqual(old[TABLE+440*24+off:TABLE+440*24+off+2], new[TABLE+440*24+off:TABLE+440*24+off+2])
    def test_bridge_board_has_manual_text_at_its_actual_prop_position(self):
        p = self.report['bridge_sign'];g = events_decode(self.arc(self.new, 'a/0/3/2')[p['event']])
        rows = [r for r in g[0] if struct.unpack_from('<2i', r, 4) == (1324,106)]
        self.assertEqual(len(rows), 1);self.assertEqual(struct.unpack_from('<2H', rows[0]), (p['entry'],0))
        self.assertIn('NUGGET BRIDGE', p['text'])

if __name__ == '__main__':unittest.main()
