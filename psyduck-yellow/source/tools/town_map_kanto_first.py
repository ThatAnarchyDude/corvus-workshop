"""Town Map / Fly map: Kanto only until the first arrival in Johto (owner 2026-11-03: "Town Map should show ONLY Kanto until you arrive in Johto for the first time", New Bark Town unlocked as a Fly destination only directly after; owner idea: reuse HeartGold's own initial-map mechanics).
HeartGold's Fly map (overlay 101) has a lock of its own: a 2-bit "map unlock level" in the save (script command 804). Level 0 = only the Johto half exists (the cursor cannot enter tile columns >= 22, only entries on Johto tiles are drawn, the Kanto picture is never loaded); level 2 = the whole map.
Only the Johto half is the unlocked one at level 0, and the Kanto picture is not loaded there, so the vanilla level cannot lock Johto. This build keeps the map at level 2 (both pictures loaded) and applies the same three restrictions, MIRRORED, while Johto is locked.
Johto counts as unlocked once the Fly point of New Bark Town is set (flag 0x9BB = Fly point 11, 0x9B0 + 11): Elm's call on the first Johto arrival sets it (johto_step2), nothing else does. While it is clear:
 - cursor (overlay 101 0x021EA7A8): the level read becomes the helper below and `blo` -> `bhs` at 0x021EA7BE, so the cursor cannot enter columns < 22 (the Johto half) and a locked tile has no destination;
 - icons (0x021EB00A, 0x021EB020): the level read becomes the helper and `cmp r0, #0` -> `cmp r0, #2` (the tile-class function 0x021E5C50 returns 2 for the Johto columns), so Johto entries are not drawn;
 - left limit: both map apps (Fly 0x021ED980, Town Map 0x021E78EC) write the cursor rectangle at app+0x100.. (min column 1, max column from the per-level table, min row 1, max row 17): while locked the min column is 22 instead of 1 (0x021EDA6C / 0x021E7A5C), so the cursor cannot leave Kanto;
 - opening page (0x021ED998, the Fly map's init, before the picture is loaded): `adds r1,r1,#1 ; strb r1,[r4,#0xD]` (page = persisted byte + 1, 1 = Johto, 2 = Kanto) becomes a routine that, while locked, forces the persisted page byte to 1 (Kanto) and the persisted cursor tile ([[args+0x20]+0x22], +0x23) to Pallet Town's, so the map opens on a Kanto town.
Once the flag is set every check passes through unchanged and the map is vanilla (both halves, the page it was last on).
The Town Map app (0x021E78EC) opens on the page of the player's current region (Kanto during the Kanto campaign); its call to the destination builder 0x021ED4E0 (0x021E7900) goes through a wrapper that, while locked, sets the persisted cursor tile to Pallet Town first.
Helpers live in overlay 129's free bytes (0x023DE5CE-0x023DE808 only (570 zero bytes between two code sections, no pointers into them; the whole length of every helper is asserted zero and inside that run)):
 unlocked(r0 = app) -> r0 = 1 when Fly point 11 is set, else 0; touches only r0-r3 (the call sites keep r4-r7);
 page: replaces the two page instructions; r0 (the app pointer for the call that follows) and r2 are live there and are preserved.
Saving overlay 101 must keep it compressed (it is stored compressed in the ROM). No save change; the unlock level stays whatever the scripts set (2 from the Viridian reward on).
Usage (from yellow-heartgold, PYTHONPATH=tools): town_map_kanto_first.py <in.nds> <out.nds>"""
import sys
import ndspy.code
import ndspy.rom
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from prototype import thumb_bl

CURSOR_LEVEL = 0x021EA7A8        # movs r0,#0x4e ; lsls r0,r0,#2 ; ldrb r0,[r6,r0] ; lsls r0,r0,#0x19 ; lsrs r0,r0,#0x1e  (then bne: skip the Kanto-half block)
CURSOR_TEST = 0x021EA7BE         # blo -> bhs (the column test of that block)
CURSOR_SKIP = 0x021EA7C4
ICON_LEVEL = 0x021EB00A          # the same level read through r5, then cmp r0,#2 (then bhs: draw everything)
ICON_TEST = 0x021EB020           # cmp r0,#0 -> cmp r0,#2 (then beq: skip the entry)
PAGE = 0x021ED998                # adds r1,r1,#1 ; strb r1,[r4,#0xd]
FLY_POINT = 0x02066930           # (flags, action 2 = test, index) -> set?
NEW_BARK = 11                    # Fly point index of New Bark Town (flag 0x9BB)
START_X, START_Z = 32, 11        # the persisted cursor tile while locked: Pallet Town's entry (x 32, z 11) in the Fly map's table at 0x021F79B4
LEFT_LIMIT = 22                  # first Kanto column
MIN_COLUMN_FLY = 0x021EDA6C      # movs r1,#1 ; adds r0,r1,#0 ; adds r0,#0xff ; strh r1,[r4,r0]   (writes min column 1 to app+0x100)
MIN_COLUMN_TOWN = 0x021E7A5C     # the same with r5
TOWN_BUILD_CALL = 0x021E7900     # bl 0x021ED4E0 in the Town Map app's init
BUILD = 0x021ED4E0
FREE_RUN = (0x023DE5CE, 0x023DE808)   # the 570 zero bytes between two code sections of overlay 129; unchanged at runtime in the 0157 crash dump
UNLOCKED_AT = 0x023DE5D0
MIN_COLUMN_AT = 0x023DE5F0
TOWN_WRAP_AT = 0x023DE610
PAGE_AT = 0x023DE640
LEVEL_READ = 'movs r0, #0x4e\nlsls r0, r0, #2\nldrb r0, [%s, r0]\nlsls r0, r0, #0x19\nlsrs r0, r0, #0x1e'
FILLER = bytes.fromhex('c046')   # mov r8, r8: the ARMv5 no-op (Thumb-2 `nop`, 0xBF00, is undefined on this CPU)


def asm(source, addr):
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(source, addr=addr)[0])


def patch(rom):
    ovs = rom.loadArm9Overlays()
    o101, o129 = ovs[101], ovs[129]
    o101.data, o129.data = bytearray(o101.data), bytearray(o129.data)

    def put(ov, addr, old, new):
        at = addr - ov.ramAddress
        assert bytes(ov.data[at:at + len(old)]) == old, (hex(addr), bytes(ov.data[at:at + len(old)]).hex(), old.hex())
        assert len(new) == len(old), (hex(addr), len(new), len(old))
        ov.data[at:at + len(new)] = new

    unlocked = asm('''
push {r3, lr}
ldr r0, [r0, #0x10]
ldr r0, [r0, #0x2c]
movs r1, #2
movs r2, #%d
ldr r3, flycheck
blx r3
cmp r0, #0
beq locked
movs r0, #1
locked:
pop {r3, pc}

.align 2
flycheck: .word %d''' % (NEW_BARK, FLY_POINT | 1), UNLOCKED_AT)
    page = asm('''
push {r0, r1, r2, r3, lr}
adds r0, r4, #0
bl #%d
cmp r0, #1
pop {r0, r1, r2, r3}
bhs open
push {r2, r3}
ldr r2, [r4, #0x10]
ldr r2, [r2, #0x20]
movs r1, #1
strb r1, [r2]
adds r2, #0x22
movs r3, #%d
strb r3, [r2]
movs r3, #%d
strb r3, [r2, #1]
pop {r2, r3}
open:
adds r1, r1, #1
strb r1, [r4, #0xd]
pop {pc}''' % (UNLOCKED_AT, START_X, START_Z), PAGE_AT)
    min_column = asm('''
push {r2, r3, lr}
adds r3, r0, #0
bl #%d
movs r1, #1
cmp r0, #1
bhs store
movs r1, #%d
store:
movs r2, #0x80
lsls r2, r2, #1
strh r1, [r3, r2]
movs r1, #1
pop {r2, r3, pc}''' % (UNLOCKED_AT, LEFT_LIMIT), MIN_COLUMN_AT)
    town_wrap = asm('''
push {r4, lr}
adds r4, r0, #0
bl #%d
cmp r0, #1
bhs call
ldr r1, [r4, #0x10]
ldr r1, [r1, #0x20]
movs r0, #1
strb r0, [r1]
adds r1, #0x22
movs r0, #%d
strb r0, [r1]
movs r0, #%d
strb r0, [r1, #1]
call:
adds r0, r4, #0
bl #%d
pop {r4, pc}''' % (UNLOCKED_AT, START_X, START_Z, BUILD), TOWN_WRAP_AT)
    assert MIN_COLUMN_AT + len(min_column) <= TOWN_WRAP_AT and TOWN_WRAP_AT + len(town_wrap) <= 0x023DE800, (len(min_column), len(town_wrap))
    helpers = ((UNLOCKED_AT, unlocked), (MIN_COLUMN_AT, min_column), (TOWN_WRAP_AT, town_wrap), (PAGE_AT, page))
    for at, code in helpers:
        # 0157 bug: only the first 0x20 bytes of each helper were checked and the 42-byte page routine ran 2 bytes into the real function at 0x23DEAD8 (battle crash on the first Quick Attack)
        off = at - o129.ramAddress
        assert FREE_RUN[0] <= at and at + len(code) <= FREE_RUN[1], (hex(at), len(code))
        assert not any(o129.data[off:off + len(code)]), 'the helper space is not free: %x' % at
    assert all(a + len(c) <= b for (a, c), (b, _) in zip(helpers, helpers[1:])), 'helpers overlap'
    for at, code in helpers:
        off = at - o129.ramAddress
        o129.data[off:off + len(code)] = code
    def ask(site, app):
        return asm('adds r0, %s, #0' % app, site) + thumb_bl(site + 2, UNLOCKED_AT)

    put(o101, CURSOR_LEVEL, asm(LEVEL_READ % 'r6', CURSOR_LEVEL), ask(CURSOR_LEVEL, 'r6') + asm('cmp r0, #0', CURSOR_LEVEL + 6) + FILLER)
    put(o101, CURSOR_TEST, asm('blo #%d' % CURSOR_SKIP, CURSOR_TEST), asm('bhs #%d' % CURSOR_SKIP, CURSOR_TEST))
    put(o101, ICON_LEVEL, asm(LEVEL_READ % 'r5' + '\ncmp r0, #2', ICON_LEVEL), ask(ICON_LEVEL, 'r5') + asm('cmp r0, #1', ICON_LEVEL + 6) + FILLER * 2)
    put(o101, ICON_TEST, asm('cmp r0, #0', ICON_TEST), asm('cmp r0, #2', ICON_TEST))
    put(o101, PAGE, asm('adds r1, r1, #1\nstrb r1, [r4, #0xd]', PAGE), thumb_bl(PAGE, PAGE_AT))
    old_min = asm('movs r1, #1\nadds r0, r1, #0\nadds r0, #0xff', 0)
    put(o101, MIN_COLUMN_FLY, old_min + asm('strh r1, [r4, r0]', 0), ask(MIN_COLUMN_FLY, 'r4')[:2] + thumb_bl(MIN_COLUMN_FLY + 2, MIN_COLUMN_AT) + FILLER)
    put(o101, MIN_COLUMN_TOWN, old_min + asm('strh r1, [r5, r0]', 0), asm('adds r0, r5, #0', 0) + thumb_bl(MIN_COLUMN_TOWN + 2, MIN_COLUMN_AT) + FILLER)
    put(o101, TOWN_BUILD_CALL, thumb_bl(TOWN_BUILD_CALL, BUILD), thumb_bl(TOWN_BUILD_CALL, TOWN_WRAP_AT))
    for ov in (o101, o129):
        rom.files[ov.fileID] = ov.save(compress=ov.compressed)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(unlocked=hex(UNLOCKED_AT), unlocked_bytes=len(unlocked), page=hex(PAGE_AT), page_bytes=len(page), min_column=hex(MIN_COLUMN_AT), min_column_bytes=len(min_column), town_wrap=hex(TOWN_WRAP_AT), town_wrap_bytes=len(town_wrap))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
