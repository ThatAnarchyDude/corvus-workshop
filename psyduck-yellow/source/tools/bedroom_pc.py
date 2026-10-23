"""Build a local Prototype-003 derivative with Yellow-style bedroom PC items.

Expected input is the *known-good* Prototype 003 .nds in ignored build/.
This is a focused test feature, NOT the completed authentic-opening prototype.
Only append script/text NARC members and repoint map 506's script/text IDs.
Never upload an output ROM to GitHub.
"""
from __future__ import annotations
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from bedroom_pc_script import (
    TEXT, POTION_WITHDRAWN_FLAG, CANDIES_WITHDRAWN_FLAG, pc_bank,
)

PROJECT = Path(__file__).resolve().parents[1]
BUILD = PROJECT / "build"
PROTO_003 = BUILD / "yellow-heartgold-prototype-003.nds"
PROTO_003_SHA = "1cd5dd980e9c9a542783fe261e5b4b9c59df7b1061e1be2d97f6fa2dd9e635db"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patch(rom, pristine):
    """Patch independently copied map 506 scripts, retaining originals."""
    import ndspy.narc
    from opening import encode_text
    from prototype import decode_messages

    script_path = "a/0/1/2"
    text_path = "a/0/2/7"
    script_file = rom.filenames.idOf(script_path)
    text_file = rom.filenames.idOf(text_path)
    script_arc = ndspy.narc.NARC(rom.files[script_file])
    text_arc = ndspy.narc.NARC(rom.files[text_file])
    originals = (list(script_arc.files), list(text_arc.files))

    pristine_main = bytes(pristine.loadArm9().sections[0].data)
    signature = struct.pack("<3H", 740, 513, 451)
    if pristine_main.count(signature) != 1:
        raise ValueError("Unable to locate one verified US HG map table")
    table = pristine_main.index(signature) - 6 - 505 * 24
    map_record = table + 506 * 24
    pristine_header = struct.unpack_from("<3H", pristine_main, map_record + 6)
    vanilla_event = struct.unpack_from("<H", pristine_main, map_record + 16)[0]
    if pristine_header != (737, 510, 448) or vanilla_event != 458:
        raise ValueError(
            f"Unexpected Red bedroom map script/text/PC layout: "
            f"{pristine_header}, event {vanilla_event}"
        )
    main = rom.loadArm9()
    blob = bytearray(main.sections[0].data)
    current_script, current_init, current_text = struct.unpack_from(
        "<3H", blob, map_record + 6
    )
    current_event = struct.unpack_from("<H", blob, map_record + 16)[0]
    if (current_script, current_init, current_text, current_event) != (
        969, 970, 831, 493
    ):
        raise ValueError("Unexpected Prototype 003 active bedroom map; expected relocated script/text/event copies")

    _, original_messages = decode_messages(text_arc.files[448])
    if len(original_messages) < 2:
        raise ValueError("Expected a two-message vanilla Red bedroom bank")
    # No dynamic player/rival text placeholders in these new messages.
    # The original Wii and PC texts remain in the preserved source archive.
    messages = encode_text(TEXT, [])
    script_id = len(script_arc.files)
    text_id = len(text_arc.files)
    script_arc.files.append(pc_bank())
    text_arc.files.append(messages)
    struct.pack_into("<3H", blob, map_record + 6, script_id, current_init, text_id)
    main.sections[0].data = blob
    rom.arm9 = main.save(compress=True)

    if script_arc.files[:-1] != originals[0] or text_arc.files[:-1] != originals[1]:
        raise ValueError("Original script/text files were modified")
    rom.files[script_file] = script_arc.save()
    rom.files[text_file] = text_arc.save()
    return {
        "map_id": 506,
        "old_script_id": current_script,
        "new_script_id": script_id,
        "old_text_id": current_text,
        "new_text_id": text_id,
        "event_bank_preserved": current_event,
        "wii_script_preserved_semantically": True,
        "pc_event_index": 1,
        "potion_quantity": 1,
        "rare_candy_quantity": 95,
        "potion_flag": POTION_WITHDRAWN_FLAG,
        "rare_candy_flag": CANDIES_WITHDRAWN_FLAG,
    }


def build():
    import ndspy.rom
    from build_rom import BASE, EXPECTED

    original = BASE.read_bytes()
    prior = PROTO_003.read_bytes()
    if sha(original) != EXPECTED:
        raise ValueError("Wrong US HeartGold base ROM")
    if sha(prior) != PROTO_003_SHA:
        raise ValueError("Wrong Prototype 003 reference build")

    rom = ndspy.rom.NintendoDSRom(prior)
    original_rom = ndspy.rom.NintendoDSRom(original)
    details = patch(rom, original_rom)
    output = rom.save()
    check = ndspy.rom.NintendoDSRom(output)
    if check.files != rom.files or check.arm9 != rom.arm9:
        raise ValueError("ROM round-trip failed")

    base = ndspy.rom.NintendoDSRom(prior)
    expected_changed = sorted(rom.filenames.idOf(p) for p in ("a/0/1/2", "a/0/2/7"))
    changed = sorted(i for i, (a, b) in enumerate(zip(base.files, check.files)) if a != b)
    if changed != expected_changed:
        raise ValueError(f"Unexpected modified files: {changed} vs {expected_changed}")
    if check.arm9OverlayTable != base.arm9OverlayTable:
        raise ValueError("Unexpected overlay-table changes")

    BUILD.mkdir(parents=True, exist_ok=True)
    target = BUILD / "psyduck-yellow-bedroom-pc-dev.nds"
    target.write_bytes(output)
    patcher = PROJECT / ".tools" / "xdelta3"
    if patcher.exists():
        patch_path = target.with_suffix(".xdelta")
        subprocess.run([str(patcher), "-f", "-e", "-S", "none",
                        "-s", str(BASE), str(target), str(patch_path)], check=True)
        roundtrip = target.with_suffix(".roundtrip.nds")
        subprocess.run([str(patcher), "-f", "-d", "-s", str(BASE),
                        str(patch_path), str(roundtrip)], check=True)
        if sha(roundtrip.read_bytes()) != sha(output):
            raise ValueError("Patch file does not reconstruct the modified ROM")
        roundtrip.unlink()
    details.update(
        name="Pokémon Psyduck Yellow bedroom-PC development integration",
        source_prototype_sha256=PROTO_003_SHA,
        output_sha256=sha(output),
        changed_file_ids=changed,
        playable_opening_upgrade=False,
        pc_bag_behavior="One Potion and one 95-count Rare Candy stack; independent one-time withdrawals",
        testing_status="binary validation only; gameplay on melonDS still required",
        warning="The existing Prototype 003 starter scene remains unchanged in this focused PC test."
    )
    (BUILD / "bedroom-pc-report.json").write_text(json.dumps(details, indent=2) + "\n")
    print(json.dumps(details, indent=2))
    return target


if __name__ == "__main__":
    build()
