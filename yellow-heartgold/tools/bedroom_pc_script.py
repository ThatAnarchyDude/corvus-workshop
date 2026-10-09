"""Psyduck Yellow: bedroom-PC starter item withdrawals (prototype staging).

Recreates a bounded item-withdrawal interaction on Red's bedroom PC only.
Stock HeartGold has no PC item-storage system. This is a two-item custom
event with persistent flags, *not* a global overhaul of PC inventories.

Map 506: MAP_PALLET_TOWN_REDS_HOUSE_2F
Event bank: 458_T01R0102; PC BG event at (6,3), event script index 1.
Wii at (5,3), event script index 0 is preserved.

The binary patch integration is in bedroom_pc.py. This file has no ndspy
requirement and can run offline bytecode acceptance tests in CI.
"""
from __future__ import annotations
import struct

POTION = 17                       # ITEM_POTION
RARE_CANDY = 50                   # ITEM_RARE_CANDY
POTION_QUANTITY = 1
CANDY_QUANTITY = 95
POTION_WITHDRAWN_FLAG = 0xB56    # reserved only for new bedroom PC
CANDIES_WITHDRAWN_FLAG = 0xB57   # reserved only for new bedroom PC
CHOICE_VAR = 0x800C
ITEM_RESULT_VAR = 0x800D
SOUND_SELECT = 1500              # SEQ_SE_DP_SELECT
FANFARE_ITEM = 1185              # SEQ_ME_ITEM

# HG event script opcode indexes (pret/pokeheartgold).
OP_END = 2
OP_GOTO = 22
OP_GOTO_IF = 28
OP_SETFLAG = 30
OP_CHECKFLAG = 32
OP_COMPARE_VAR_VALUE = 17
OP_NPC_MSG = 45                  # u8 index; unlike most commands
OP_WAIT_BUTTON = 50
OP_CLOSE_MSG = 53
OP_YES_NO = 63
OP_PLAY_SE = 73
OP_PLAY_FANFARE = 78
OP_WAIT_FANFARE = 79
OP_LOCK_ALL = 96
OP_RELEASE_ALL = 97
OP_GIVE_ITEM = 125

TEXT = (
    "It's a Wii! Wii is huge in Kanto, too!",
    "The PC holds one POTION. Withdraw it?",
    "You withdrew one POTION!",
    "The PC holds 95 RARE CANDY. Withdraw all of them?",
    "You withdrew 95 RARE CANDY!",
    "You can't carry that many right now.",
    "There's nothing left in the PC."
)


class Script:
    def __init__(self):
        self.data = bytearray()
        self.labels = {}
        self.fixups = []

    def emit(self, opcode, *args):
        for n in (opcode,) + args:
            if not 0 <= n <= 65535:
                raise ValueError(f"Not a 16-bit script value: {n}")
            self.data.extend(struct.pack("<H", n))
        return self

    def label(self, name):
        if name in self.labels:
            raise ValueError(f"Duplicate label {name}")
        self.labels[name] = len(self.data)
        return self

    def _target(self, name):
        self.fixups.append((len(self.data), name))
        self.data.extend(bytes(4))
        return self

    def jump(self, name, condition=None):
        self.emit(OP_GOTO if condition is None else OP_GOTO_IF)
        if condition is not None:
            self.data.append(condition)  # condition 1 is equal, as in opening.py
        return self._target(name)

    def compare(self, variable, value):
        return self.emit(OP_COMPARE_VAR_VALUE, variable, value)

    def msg(self, index, *, wait=True):
        if not 0 <= index < len(TEXT):
            raise ValueError("Missing message index")
        self.emit(OP_NPC_MSG)
        self.data.append(index)  # NPCMsg accepts 1 byte, unlike other ops
        if wait:
            self.emit(OP_WAIT_BUTTON)
        return self.emit(OP_CLOSE_MSG)

    def yes_no(self, index):
        if not 0 <= index < len(TEXT):
            raise ValueError("Missing message index")
        self.emit(OP_NPC_MSG)
        self.data.append(index)
        self.emit(OP_YES_NO, CHOICE_VAR)
        return self.emit(OP_CLOSE_MSG)

    def finish(self):
        for at, name in self.fixups:
            if name not in self.labels:
                raise ValueError(f"Unresolved script label {name}")
            struct.pack_into("<i", self.data, at, self.labels[name] - at - 4)
        return bytes(self.data)


def wii_script():
    s = Script().emit(OP_PLAY_SE, SOUND_SELECT).emit(OP_LOCK_ALL)
    s.msg(0)
    return s.emit(OP_RELEASE_ALL).emit(OP_END).finish()


def item_pc_script():
    """Present individually withdrawable, non-renewable items.

    Declining either prompt does not consume that item; a bag-full failure
    does not set its flag. Once withdrawn, the gift never duplicates,
    including on save/reload because event flags belong to the save data.
    """
    s = Script().emit(OP_PLAY_SE, SOUND_SELECT).emit(OP_LOCK_ALL)
    s.emit(OP_CHECKFLAG, POTION_WITHDRAWN_FLAG).jump("candy", 1)
    s.yes_no(1).compare(CHOICE_VAR, 0).jump("take_potion", 1)
    s.jump("candy")
    s.label("take_potion").emit(OP_GIVE_ITEM, POTION, POTION_QUANTITY, ITEM_RESULT_VAR)
    s.compare(ITEM_RESULT_VAR, 0).jump("potion_full", 1)
    s.emit(OP_SETFLAG, POTION_WITHDRAWN_FLAG)
    s.emit(OP_PLAY_FANFARE, FANFARE_ITEM).emit(OP_WAIT_FANFARE).msg(2)
    s.jump("candy")
    s.label("potion_full").msg(5)

    s.label("candy").emit(OP_CHECKFLAG, CANDIES_WITHDRAWN_FLAG).jump("empty_check", 1)
    s.yes_no(3).compare(CHOICE_VAR, 0).jump("take_candy", 1)
    s.jump("finish")
    s.label("take_candy").emit(OP_GIVE_ITEM, RARE_CANDY, CANDY_QUANTITY, ITEM_RESULT_VAR)
    s.compare(ITEM_RESULT_VAR, 0).jump("candy_full", 1)
    s.emit(OP_SETFLAG, CANDIES_WITHDRAWN_FLAG)
    s.emit(OP_PLAY_FANFARE, FANFARE_ITEM).emit(OP_WAIT_FANFARE).msg(4)
    s.jump("finish")
    s.label("candy_full").msg(5)
    s.jump("finish")
    s.label("empty_check").emit(OP_CHECKFLAG, POTION_WITHDRAWN_FLAG).jump("both_empty", 1)
    s.jump("finish")
    s.label("both_empty").msg(6)
    s.label("finish").emit(OP_RELEASE_ALL).emit(OP_END)
    return s.finish()


def script_bank(scripts):
    """HG NARC script-bank pointer array followed by 0xFD13 terminator."""
    header = bytearray(4 * len(scripts) + 4)
    struct.pack_into("<H", header, 4 * len(scripts), 0xFD13)
    body = bytearray()
    for i, script in enumerate(scripts):
        struct.pack_into("<I", header, i * 4, len(header) + len(body) - (i * 4) - 4)
        body.extend(script)
        body.extend(bytes(-len(body) % 4))
    return bytes(header + body)


def pc_bank():
    return script_bank([wii_script(), item_pc_script()])
