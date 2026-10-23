"""Yellow's robbed house, rear passage and stolen Dig TM after helping Bill."""
import struct
import ndspy.narc
from opening import Script, actor, events_decode, events_encode, script_bank, encode_text, end, trigger, talk
from parcel_quest import split_bank, PH
from prototype import decode_messages, encode_messages
from cerulean import BILL_STATE, THIEF_BEAT, THIEF_HIDE, M
from route24 import refresh_hook
from save_compatibility import assert_persistent
from viridian_tutorial import TABLE
from title_models import mesh

THIEF, TRAINER, DIG = 31, 786, 355
SPAWN_HIDE, SCENE = 0xA9C, 0x414D
MARKER = 0x4D502531
EXIT_X, EXIT_Z = 1305, 112


def land_start(raw):
    # HG outdoor files can prepend an extra layout block to permissions.
    magic = struct.unpack_from('<I', raw, 16)[0]
    assert magic & 0xFFFF == 0x1234
    return 20 + (magic >> 16)


def append_mesh(raw, commands):
    """Add a small untextured mesh to the last drawn native land shape.

    Leave all original dictionaries, textures and display lists in place.
    Redirect one shape to a copy of its original list plus our new commands.
    The native model's position scale and bounds remain unchanged.
    """
    g = bytearray(raw)
    assert g[:4] == b'BMD0' and struct.unpack_from('<H', g, 14)[0] == 1
    block = struct.unpack_from('<I', g, 16)[0]
    assert g[block:block + 4] == b'MDL0'
    count = g[block + 9]
    assert count == 1
    mo = block + struct.unpack_from('<I', g, block + 12 + 8 + 4 * count + 4)[0]
    size, sbc, mats, shapes, shape_end = struct.unpack_from('<5I', g, mo)
    assert mo + size == len(g) and shape_end == size
    sb = bytes(g[mo + sbc:mo + mats])
    # Last native SHP command occurs before POS_SCALE(0x2B), RET(0x01).
    assert sb[-8:].find(bytes([0x2B, 1])) != -1
    last = sb.rfind(bytes([5]))
    shape = sb[last + 1]
    sc = g[mo + shapes + 1]
    assert shape < sc
    info = mo + shapes + 4 + 8 + 4 * sc
    so = mo + shapes + struct.unpack_from('<I', g, info + 4 + 4 * shape)[0]
    dl, length = struct.unpack_from('<2I', g, so + 8)
    old = bytes(g[so + dl:so + dl + length])
    new = old + commands
    struct.pack_into('<2I', g, so + 8, len(g) - so, len(new))
    g.extend(new)
    struct.pack_into('<I', g, mo, size + len(new))
    struct.pack_into('<I', g, mo + 16, size + len(new))
    struct.pack_into('<I', g, block + 4, len(g) - block)
    struct.pack_into('<I', g, 8, len(g))
    return bytes(g)


def hole_mesh():
    # A jagged dark passage and broken plaster below the back-wall window.
    center = (-152, 13, -204)
    points = [(-166, 0, -204), (-167, 12, -204), (-163, 25, -204),
              (-156, 29, -204), (-148, 27, -204), (-139, 23, -204),
              (-138, 11, -204), (-140, 0, -204)]
    tris = []
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        tris.append((center, a, b, (17, 16, 20)))
        aa = (center[0] + (a[0] - center[0]) * 1.17,
              max(0, center[1] + (a[1] - center[1]) * 1.14), -204)
        bb = (center[0] + (b[0] - center[0]) * 1.17,
              max(0, center[1] + (b[1] - center[1]) * 1.14), -204)
        tris.extend([(a, aa, bb, (136, 112, 76)), (a, bb, b, (171, 148, 100))])
    return mesh([(tuple(v / 64 for v in a), tuple(v / 64 for v in b),
                  tuple(v / 64 for v in c), col) for a, b, c, col in tris])


def robber(first):
    s = Script().emit(73, 1500).emit(96).emit(104).emit(32, THIEF_HIDE).jump('done', 1)
    s.emit(32, THIEF_BEAT).jump('reward', 1).msg(first).emit(213, TRAINER, 0)
    s.data.extend(bytes(2))
    s.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.emit(36, TRAINER).emit(30, THIEF_BEAT).emit(41, SCENE, 1).msg(first + 1)
    s.label('reward').msg(first + 2).emit(125, DIG, 1, 0x800C)
    s.compare(0x800C, 0).jump('full', 1)
    s.emit(30, THIEF_HIDE).emit(30, SPAWN_HIDE).emit(41, SCENE, 1)
    s.emit(78, 1185).msg(first + 3).emit(79).msg(first + 4)
    # Walk around the north side of the buildings, never through their walls.
    s.movement(THIEF, 'leave').emit(95).emit(101, THIEF)
    s.label('done');end(s)
    s.label('full').msg(first + 5);end(s)
    s.label('lost').emit(219);end(s)
    return s.moves('leave', [(15, 12)]).finish()


def city_init_prefix():
    s = Script().emit(30, SPAWN_HIDE).emit(41, SCENE, 1)
    s.compare(BILL_STATE, 1).jump('done', 5).emit(32, THIEF_HIDE).jump('done', 1)
    s.emit(31, SPAWN_HIDE).emit(32, THIEF_BEAT).jump('done', 1).emit(41, SCENE, 0)
    return s.label('done').finish()


def patch(rom):
    for flag in (SPAWN_HIDE, THIEF_BEAT, THIEF_HIDE):
        assert_persistent(flag);assert flag < 0xAA0
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    paths = ('a/0/1/2', 'a/0/2/7', 'a/0/3/2', 'a/0/4/1', 'a/0/6/5')
    scripts, texts, events, matrices, lands = arcs = [ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    city, house = TABLE + 52 * 24, TABLE + 429 * 24
    csid, ciid, ctid = struct.unpack_from('<3H', d, city + 6)
    ceid = struct.unpack_from('<H', d, city + 16)[0]
    cg = events_decode(events.files[ceid]);bank = split_bank(scripts.files[csid])
    key, lines = decode_messages(texts.files[ctid]);first = len(lines)
    messages = [M[k] for k in ('CeruleanCityRocketText', 'CeruleanCityRocketIGiveUpText',
                              'CeruleanCityRocketIllReturnTheTMText', 'CeruleanCityRocketReceivedTM28Text',
                              'CeruleanCityRocketIBetterGetMovingText', 'CeruleanCityRocketTM28NoRoomText')]
    lines.extend(decode_messages(encode_text(messages, PH))[1])
    entry = len(bank) + 1;bank.append(robber(first))
    # The roof projects over the two nearest backyard rows. Stand in the
    # northern lane so the full Rocket sprite is visible before his battle.
    cg[1].append(actor(THIEF, 222, entry, 1307, 109, SPAWN_HIDE, 2))
    for x, z in ((1306, 109), (1307, 108), (1307, 110)):
        cg[3].append(trigger(entry, x, z, 1, SCENE, 0))
    back_entry = len(bank) + 1
    s = Script().emit(96).emit(174, 6, 6, 0, 0).emit(175)
    s.emit(176, 429, 0, 6, 4, 1).emit(174, 6, 6, 1, 0).emit(175)
    bank.append(end(s).finish())
    cg[3].append(trigger(back_entry, EXIT_X, EXIT_Z, 1, BILL_STATE, 1))
    warp = len(cg[2]);assert warp == 8
    # Target for the house's native exit. Its outdoor grass stays normal;
    # the coordinate entry is gated by Bill, preventing an early back-door bypass.
    cg[2].append(struct.pack('<4Hi', EXIT_X, EXIT_Z, 429, 1, 0))
    bank[12] = city_init_prefix() + bank[12]
    refresh = refresh_hook(main, [THIEF], MARKER)
    s = Script().emit(1);s.data.extend(struct.pack('<I', MARKER))
    s.emit(32, SPAWN_HIDE).jump('done', 1).emit(100, THIEF).label('done')
    bank[15] = s.finish() + bank[15]
    ns, nt, ne = len(scripts.files), len(texts.files), len(events.files)
    scripts.files.append(script_bank(bank));texts.files.append(encode_messages(key, lines));events.files.append(events_encode(cg))
    struct.pack_into('<H', d, city + 6, ns);struct.pack_into('<H', d, city + 10, nt);struct.pack_into('<H', d, city + 16, ne)

    heid = struct.unpack_from('<H', d, house + 16)[0]
    hg = events_decode(events.files[heid]);hg[2].append(struct.pack('<4Hi', 6, 3, 52, warp, 0))
    hsid = struct.unpack_from('<H', d, house + 6)[0];hb = split_bank(scripts.files[hsid])
    hb.append(talk(3));hg[0].append(struct.pack('<HHiiiH2x', 3, 0, 6, 3, 0, 4))
    old_mid = struct.unpack_from('<H', d, house + 4)[0];mat = bytearray(matrices.files[old_mid])
    at = 5 + mat[4];old_lid = struct.unpack_from('<H', mat, at)[0];land = bytearray(lands.files[old_lid])
    base = land_start(land);ps, bs, ms = struct.unpack_from('<3I', land)
    props = [bytes(land[base + ps + i:base + ps + i + 48]) for i in range(0, bs, 48)]
    model_start = base + ps + bs
    model = append_mesh(bytes(land[model_start:model_start + ms]), hole_mesh())
    tail = bytes(land[model_start + ms:])
    land = bytearray(land[:base + ps]) + b''.join(props) + model + tail
    struct.pack_into('<2I', land, 4, len(props) * 48, len(model))
    permission = base + 2 * (3 * 32 + 6)
    assert struct.unpack_from('<H', land, permission)[0] == 0x0600
    struct.pack_into('<H', land, permission, 0x0064)  # Native north-facing exit.
    lid = len(lands.files);lands.files.append(land);struct.pack_into('<H', mat, at, lid)
    mid = len(matrices.files);matrices.files.append(mat)
    hs, ht, he = len(scripts.files), len(texts.files), len(events.files)
    scripts.files.append(script_bank(hb))
    old_ht = struct.unpack_from('<H', d, house + 10)[0];hk, hl = decode_messages(texts.files[old_ht])
    hl.extend(decode_messages(encode_text([M['CeruleanTrashedHouseWallHoleText']], PH))[1]);texts.files.append(encode_messages(hk, hl));events.files.append(events_encode(hg))
    struct.pack_into('<H', d, house + 4, mid);struct.pack_into('<H', d, house + 6, hs);struct.pack_into('<H', d, house + 10, ht);struct.pack_into('<H', d, house + 16, he)
    for p, arc in zip(paths, arcs):rom.files[rom.filenames.idOf(p)] = arc.save()
    main.sections[1].data.extend(bytes(-len(main.sections[1].data) % 4))
    struct.pack_into('<I', d, 0xD2C68, main.sections[1].ramAddress + len(main.sections[1].data))
    assert len(main.sections[1].data) <= 0x8000
    rom.arm9 = main.save(compress=True)
    return dict(city=dict(script=ns, init=ciid, text=nt, event=ne, thief_entry=entry, back_entry=back_entry,
                          first_message=first, refresh=refresh, exit=[EXIT_X, EXIT_Z], warp=warp),
                house=dict(script=hs, text=ht, event=he, matrix=mid, land=lid, old_matrix=old_mid,
                           old_land=old_lid, rear_exit=[6, 3], original_event=heid),
                trainer=TRAINER, team=[dict(species=66, level=17), dict(species=96, level=17)],
                dig_item=DIG, flags=[THIEF_BEAT, THIEF_HIDE, SPAWN_HIDE], scene_var=SCENE,
                johto_unchanged=True, no_new_HM_barriers=True)
