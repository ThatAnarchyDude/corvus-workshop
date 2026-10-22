"""Either the Soul Badge or Fog Badge unlocks Surf in both regions."""
import struct
import ndspy.code
from prototype import thumb_bl
from starter_properties import append_code

SURF_BADGE_SITE = 0x020680FA
SHORE_BADGE_SITE = 0x021E7534
PROFILE_TEST_BADGE = 0x02028F98

def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    at = SURF_BADGE_SITE - 0x02000000
    assert d[at-2:at] == bytes((3, 0x21))
    assert d[at:at+4] == thumb_bl(SURF_BADGE_SITE, PROFILE_TEST_BADGE)
    # User-approved exception: earning Soul in Kanto unlocks Surf everywhere.
    # Retain Fog as an alternative; all other native Surf checks remain.
    source = f"""
push {{r4,lr}}
movs r4,r0
movs r1,#12
ldr r3,profile_test
blx r3
cmp r0,#0
bne done
movs r0,r4
movs r1,#3
ldr r3,profile_test
blx r3
done:
pop {{r4,pc}}
nop
.balign 4
profile_test: .word {PROFILE_TEST_BADGE|1}
"""
    hook, code = append_code(main, source)
    d[at:at+4] = thumb_bl(SURF_BADGE_SITE, hook)
    overlays = rom.loadArm9Overlays()
    shore = overlays[1]
    shore_at = SHORE_BADGE_SITE - shore.ramAddress
    assert shore.data[shore_at-2:shore_at] == bytes((3, 0x21))
    assert shore.data[shore_at:shore_at+4] == thumb_bl(SHORE_BADGE_SITE, PROFILE_TEST_BADGE)
    shore.data[shore_at:shore_at+4] = thumb_bl(SHORE_BADGE_SITE, hook)
    rom.files[shore.fileID] = shore.save(compress=shore.compressed)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
    struct.pack_into('<I', d, 0xD2C68, main.sections[1].ramAddress + len(main.sections[1].data))
    rom.arm9 = main.save(compress=True)
    return {'site':hex(SURF_BADGE_SITE), 'hook':hex(hook), 'code_bytes':len(code),
            'shore_hook':hex(hook), 'shore_site':hex(SHORE_BADGE_SITE),
            'shore_overlay_file':shore.fileID, 'accepted_badges':[12,3],
            'both_regions':True, 'other_native_checks_preserved':True}