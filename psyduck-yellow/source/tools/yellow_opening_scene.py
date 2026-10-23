"""Verified HGSS scene constants and conservative movement planning.

Research reference:
- pret/pokeheartgold include/constants/movements.h, sndseq.h,
  src/data/fieldmap/script_cmd_table.h at revision
  9d8b7591f09b65804da2fb2dfd56f320633e0d36.

This does not modify ROMs or replace the existing event. In particular, a
movement path is not a claim that collision and map transitions have passed
emulator tests.
"""
from dataclasses import dataclass

# Script command opcodes as indexed in HGSS's script command dispatch table.
CMD_PLAY_SE = 73
CMD_PLAY_CRY = 76
CMD_WAIT_CRY = 77
CMD_PLAY_FANFARE = 78
CMD_WAIT_FANFARE = 79
CMD_PLAY_BGM = 80
CMD_RESET_BGM = 82
CMD_APPLY_MOVEMENT = 94
CMD_WAIT_MOVEMENT = 95

# Existing HeartGold soundtrack IDs. Exact Yellow melody replacement would
# require editing audio assets and separate auditory validation.
BGM_OAK_MEETING = 1067          # SEQ_GS_OHKIDO
BGM_OAK_ESCORT = 1086           # SEQ_GS_E_TSURETEKE1
BGM_RIVAL_CHALLENGE = 1088      # SEQ_GS_E_RIVAL1 (placeholder timbre)
BGM_OAK_LAB = 1103              # SEQ_GS_OHKIDO_RABO

SFX_SELECTION = 1394            # SEQ_SE_PL_BUTTON
SFX_ALERT = 1389                # SEQ_SE_PL_ALERT
FANFARE_POKEMON_RECEIVED = 1187 # SEQ_ME_POKEGET

# Field movement opcodes from include/constants/movements.h.
MOVE_FACE_UP = 0
MOVE_FACE_DOWN = 1
MOVE_FACE_LEFT = 2
MOVE_FACE_RIGHT = 3
MOVE_UP = 12
MOVE_DOWN = 13
MOVE_LEFT = 14
MOVE_RIGHT = 15
MOVE_EXCLAMATION = 75
MOVE_END = 254

# Proposed visible Oak staging point, not a native NPC position.
# Native HG Pallet actor 0 (sprite 325) at (1040,367) is a woman.
# Prototype 003 adds separate Oak actor 3 (sprite 366) at (1038,354).
# The proposed south start must pass field collision testing before use.
ORIGINAL_OAK_START = (1038, 367)
NORTH_EXIT_COLUMNS = (1030, 1031, 1032, 1033)
OAK_INTERCEPT_Z = 353
# Native HeartGold Pallet Town map 49's warp to Oak's Lab is at
# world coordinate (1045,373); immediately west is the approach tile.
OAK_LAB_DOOR = (1045, 373)
OAK_LAB_APPROACH = (1044, 373)


@dataclass(frozen=True)
class Segment:
    movement: int
    steps: int


def oak_approach(player_x: int):
    """Plan movement from a proposed visible Oak position to Route 1's edge.

    Candidate collision route along the town's open central corridor;
    requires an emulator walkthrough before it is wired into the live event.
    """
    if player_x not in NORTH_EXIT_COLUMNS:
        raise ValueError("Unexpected exit column: inspect the route collision first")
    x, z = ORIGINAL_OAK_START
    path = (Segment(MOVE_LEFT, x - player_x),
            Segment(MOVE_UP, z - OAK_INTERCEPT_Z))
    assert all(step.steps > 0 for step in path)
    return path


def follow_path(path):
    """Reverse a cardinal movement path, for the escorted return journey."""
    opposites = {MOVE_UP: MOVE_DOWN, MOVE_DOWN: MOVE_UP,
                 MOVE_LEFT: MOVE_RIGHT, MOVE_RIGHT: MOVE_LEFT}
    return tuple(Segment(opposites[step.movement], step.steps)
                 for step in reversed(path))


def destination(start, path):
    x, z = start
    for segment in path:
        if segment.movement == MOVE_LEFT:
            x -= segment.steps
        elif segment.movement == MOVE_RIGHT:
            x += segment.steps
        elif segment.movement == MOVE_UP:
            z -= segment.steps
        elif segment.movement == MOVE_DOWN:
            z += segment.steps
        else:
            raise ValueError("Not a cardinal movement")
    return x, z

def oak_to_lab(player_x: int):
    """Candidate uninterrupted world-space walk from north edge to lab door.

    Path reverses the visible approach, then follows Pallet's open courtyard.
    Must be collision-tested in melonDS; DO NOT run as a live cutscene yet.
    """
    approach = oak_approach(player_x)
    return (follow_path(approach)
            + (Segment(MOVE_RIGHT, 6), Segment(MOVE_DOWN, 6),
               Segment(MOVE_RIGHT, 1)))
