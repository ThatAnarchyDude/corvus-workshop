"""Use HG's visible home computer at Bill's existing PC interaction tile."""
import struct
import ndspy.narc
from cerulean_robbery import land_start
from viridian_tutorial import TABLE

def patch(rom):
    main = rom.loadArm9();d = main.sections[0].data = bytearray(main.sections[0].data)
    mp, lp = 'a/0/4/1', 'a/0/6/5'
    matrices = ndspy.narc.NARC(rom.files[rom.filenames.idOf(mp)])
    lands = ndspy.narc.NARC(rom.files[rom.filenames.idOf(lp)])
    rec = TABLE + 440 * 24;area = d[rec+1]
    areas = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/2')])
    lists = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/3')])
    prop_list = struct.unpack_from('<H', areas.files[area])[0]
    models = struct.unpack('<' + str(len(lists.files[prop_list])//2) + 'H', lists.files[prop_list])
    assert 138 in models[1:], 'Native computer must already be loaded for Bill’s area'
    template = lands.files[225];base = land_start(template);ps, bs = struct.unpack_from('<2I', template)
    pcs = [template[a:a+48] for a in range(base+ps, base+ps+bs, 48)
           if struct.unpack_from('<I', template, a)[0] == 138]
    assert len(pcs) == 1
    pc = bytearray(pcs[0])
    struct.pack_into('<3i', pc, 4, int((2-15.5)*65536), 0, int((7-15.5)*65536))
    old_mid = struct.unpack_from('<H', d, rec+4)[0];mat = bytearray(matrices.files[old_mid])
    at = 5 + mat[4];old_lid = struct.unpack_from('<H', mat, at)[0];land = bytearray(lands.files[old_lid])
    base = land_start(land);ps, bs = struct.unpack_from('<2I', land)
    land[base+ps+bs:base+ps+bs] = pc;struct.pack_into('<I', land, 4, bs+48)
    # The computer is an actual solid prop, with its existing A-button script.
    permission = base + 2*(7*32+2);original = struct.unpack_from('<H', land, permission)[0]
    struct.pack_into('<H', land, permission, original | 0x8000)
    lid = len(lands.files);lands.files.append(land);struct.pack_into('<H', mat, at, lid)
    mid = len(matrices.files);matrices.files.append(mat);struct.pack_into('<H', d, rec+4, mid)
    rom.files[rom.filenames.idOf(mp)] = matrices.save();rom.files[rom.filenames.idOf(lp)] = lands.save()
    rom.arm9 = main.save(compress=True)
    return dict(map=440, model=138, interaction=[2,7], matrix=mid, land=lid,
                old_matrix=old_mid, old_land=old_lid, previous_permission=original,
                native_scripts_unchanged=True, native_area_list_unchanged=True)
