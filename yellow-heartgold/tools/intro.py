"""Restore rival naming inside Oak's pre-game introduction, before Pallet."""
import struct

import ndspy.code
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB

from build_rom import PROJECT, sha
from prototype import decode_messages, encode_messages, thumb_bl

EXPECTED_OVERLAY = '19a3c683b5e82e37d71bb3cab902b106c14694676550482c15fcdf6c4a850ac0'


def patch_intro(rom, texts, encode_text, placeholder):
    overlays = rom.loadArm9Overlays()
    overlay = overlays[53]
    if sha(overlay.data) != EXPECTED_OVERLAY or overlay.ramAddress != 0x021E5900 or overlay.bssSize:
        raise ValueError('Unexpected Oak intro overlay')
    old = bytes(overlay.data)
    hook, original_task = 0x021E5A5C, 0x021E6F9C
    at = hook - overlay.ramAddress
    assert old[at:at + 4] == thumb_bl(hook, original_task)
    assert struct.unpack_from('<I', old, 0x2384)[0] == 0x02102610
    source = (PROJECT / 'asm/oak-rival-name.s').read_text()
    assembly = '\n'.join(line.split('@')[0] for line in source.splitlines())
    address = overlay.ramAddress + len(old)
    assert address == 0x021E88A0
    raw, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(assembly, addr=address)
    code = bytes(raw)
    # ARM946E-S requires Thumb-1: accept 32-bit BL only, no Thumb-2 opcodes.
    disassembly = list(Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(code[:-4], address))
    assert sum(i.size for i in disassembly) == len(code) - 4
    assert all(i.size == 2 or i.mnemonic == 'bl' for i in disassembly)
    assert code[-4:] == struct.pack('<I', 0x02102610)
    overlay.data.extend(code)
    overlay.data[at:at + 4] = thumb_bl(hook, address)
    assert len(overlay.data) < 0x4000
    rom.files[overlay.fileID] = overlay.save(compress=True)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
    key, messages = decode_messages(texts.files[219])
    assert len(messages) == 63
    original_messages = list(messages)
    additions = decode_messages(encode_text([
        "This is my grandson. He's been your rival since you were a baby.\r...Erm, what is his name again?",
        "Right! So his name is {RIVAL}!"
    ], placeholder))[1]
    messages.extend(additions)
    texts.files[219] = encode_messages(key, messages)
    assert decode_messages(texts.files[219])[1][:63] == original_messages
    return dict(overlay=53, hook=hex(hook), helper=hex(address), helper_bytes=len(code),
                original_overlay_sha256=EXPECTED_OVERLAY, output_overlay_sha256=sha(overlay.data),
                new_message_ids=[63, 64],
                phase_field='OakSpeechData.unk_010', placement='Oak intro, after player naming, before bedroom')
