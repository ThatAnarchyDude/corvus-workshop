"""Open the native Kanto badge page first without renumbering saved badges."""
import struct
import ndspy.code,ndspy.narc

def patch(rom):
    overlays=rom.loadArm9Overlays(); o=overlays[51]; o.data=bytearray(o.data)
    edits=((0x021E5BA4,'06d0','c046'), (0x021E5BD6,'0121','0021'))
    for address,before,after in edits:
        off=address-o.ramAddress
        assert o.data[off:off+2]==bytes.fromhex(before),hex(address)
        o.data[off:off+2]=bytes.fromhex(after)
    # Native badge IDs and animation sequences stay fixed. Move their display
    # positions together with the matching leaders/background, not their flags.
    at=0x021E801C-o.ramAddress
    coords=bytes(o.data[at:at+128]);assert len(coords)==128
    o.data[at:at+128]=coords[64:]+coords[:64]
    path='a/0/4/9';fid=rom.filenames.idOf(path);art=ndspy.narc.NARC(rom.files[fid])
    full=bytearray(art.files[52]);assert struct.unpack_from('<2H',full,24)==(256,192)
    start=36;row=64;first=start+2*row;second=start+13*row;size=11*row
    upper=bytes(full[first:first+size]);lower=bytes(full[second:second+size])
    full[first:first+size]=lower;full[second:second+size]=upper;art.files[52]=bytes(full)
    single=bytearray(art.files[51]);single[first:first+size]=lower;art.files[51]=bytes(single)
    rom.files[fid]=art.save()
    rom.files[o.fileID]=o.save(compress=True)
    rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    return dict(overlay=51,initial_page='Kanto',saved_badge_numbers_unchanged=True,
                portrait_regions_swapped=True,native_portraits_and_polishing_preserved=True)
