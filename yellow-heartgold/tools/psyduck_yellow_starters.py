"""Psyduck Yellow's validated starter decisions. ROM patching is separate.

This module deliberately rejects currently unspecified rival combinations
instead of quietly inventing story behavior. Johto selection must use a
separate unmodified HeartGold flow.

HGSS species IDs: Psyduck=54, Eevee=133, Togepi=175.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import json


PROJECT = Path(__file__).resolve().parents[1]
CONFIG = PROJECT / "data" / "psyduck-yellow-starters.json"
VALID_GENDERS = ("male", "female")
EXPECTED_TABLE = (("left", 54, "male"), ("center", 175, "natural"),
                  ("right", 133, "female"))
JOHTO_STARTERS = (152, 155, 158)


@lru_cache(maxsize=1)
def get_config() -> dict:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert data["project_name"] == "Pokémon Psyduck Yellow"
    options = tuple((row["position"], row["species"], row["starter_gender"])
                    for row in data["lab_table"]["options"])
    if options != EXPECTED_TABLE:
        raise ValueError("Starter table layout or gender rules changed unexpectedly")
    if tuple(data["johto_preservation"]["original_starters"]) != JOHTO_STARTERS:
        raise ValueError("Johto's original starters must remain untouched")
    rules = {(entry["player_gender"], entry["chosen_starter"]):
             entry["rival_starter"] for entry in data["rival_rules"]}
    if len(rules) != len(data["rival_rules"]):
        raise ValueError("Duplicate rival rule")
    if any(k[0] not in VALID_GENDERS or k[1] not in (54, 133, 175)
           or v not in (54, 133, 175) for k, v in rules.items()):
        raise ValueError("Unsupported starter/gender/rival configuration")
    undecided = {(entry["player_gender"], entry["chosen_starter"])
                 for entry in data["unresolved_rival_cases"]}
    if set(rules) & undecided:
        raise ValueError("An explicit rule overlaps an unresolved one")
    if len(undecided) != len(data["unresolved_rival_cases"]):
        raise ValueError("Duplicate undecided case")
    if set(rules) | undecided != {(g, s) for g in VALID_GENDERS
                                  for s in (54, 133, 175)}:
        raise ValueError("Some starter branches are neither confirmed nor marked undecided")
    return data


def player_starter_at(position: str) -> int:
    """Species assigned to a physical ball on Oak's right-side table."""
    for row in get_config()["lab_table"]["options"]:
        if row["position"] == position:
            return row["species"]
    raise ValueError(f"No starter at position: {position!r}")


def required_starter_gender(species: int) -> str:
    """Return 'male', 'female', or 'natural' (normal species ratio)."""
    for row in get_config()["lab_table"]["options"]:
        if row["species"] == species:
            return row["starter_gender"]
    raise ValueError(f"Not a Kanto starter: {species}")


def rival_starter(player_gender: str, player_starter: int) -> int:
    """Return explicitly approved rival species; fail on undecided branches."""
    rules = {(entry["player_gender"], entry["chosen_starter"]):
             entry["rival_starter"] for entry in get_config()["rival_rules"]}
    if player_gender not in VALID_GENDERS or player_starter not in (54, 133, 175):
        raise ValueError("Invalid player gender or Kanto starter")
    key = (player_gender, player_starter)
    if key not in rules:
        raise NotImplementedError(f"Rival starter still requires supervisor decision: {key}")
    return rules[key]


def pokemon_gender_for_pid(species: int, personality: int, ratio: int) -> str:
    """HG Gen-IV gender test for a non-fixed-gender species.

    In HG, female iff the species gender threshold > (PID & 0xff).
    Threshold must be read from the ROM's personal data, never guessed.
    0xFF is genderless, 0xFE female-only, and 0 male-only.
    """
    if not 0 <= personality <= 0xFFFFFFFF or not 0 <= ratio <= 255:
        raise ValueError("Invalid PID/gender ratio")
    if ratio == 255:
        return "genderless"
    if ratio == 254:
        return "female"
    if ratio == 0:
        return "male"
    return "female" if ratio > (personality & 255) else "male"


def matches_required_gender(species: int, personality: int, ratio: int) -> bool:
    required = required_starter_gender(species)
    return required == "natural" or pokemon_gender_for_pid(species, personality, ratio) == required
