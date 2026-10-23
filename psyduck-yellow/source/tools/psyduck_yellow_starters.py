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
# Ability effects already defined in vanilla HGSS include/constants/abilities.h.
# Only these verified native effects may be used in the planned Kanto-only gifts.
NATIVE_HG_ABILITIES = {
    6: "Damp", 13: "Cloud Nine", 28: "Synchronize", 32: "Serene Grace",
    33: "Swift Swim", 34: "Chlorophyll", 39: "Inner Focus", 50: "Run Away",
    55: "Hustle", 62: "Guts", 91: "Adaptability", 93: "Hydration",
    95: "Quick Feet", 105: "Super Luck", 107: "Anticipation",
    115: "Ice Body",
}
EXPECTED_STARTER_ABILITIES = {
    54: (6, 13, 33),       # Psyduck
    175: (55, 32, 105),    # Togepi
    133: (50, 91, 107),    # Eevee
}
EXPECTED_EVOLUTION_HIDDEN = {
    55: 33, 176: 105, 468: 105, 134: 93, 135: 95, 136: 62,
    196: None, 197: 39, 470: 34, 471: 115,
}



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
    abilities = data["starter_creation"]["ability_slots"]
    mapping = abilities["mapping"]
    actual = {row["species"]: tuple(slot["id"] for slot in row["slots"])
              for row in mapping}
    if len(mapping) != 3 or actual != EXPECTED_STARTER_ABILITIES:
        raise ValueError("Starter Hidden Ability list has drifted")
    if set(abilities["native_hg_ability_ids_used"]) != set(NATIVE_HG_ABILITIES):
        raise ValueError("Native HG ability list has drifted")
    for row in mapping:
        if [a["slot"] for a in row["slots"]] != [1, 2, 3]:
            raise ValueError("Ability slots must be 1, 2, 3")
        for ability in row["slots"]:
            ability_id = ability["id"]
            if NATIVE_HG_ABILITIES.get(ability_id) != ability["name"]:
                raise ValueError("Attempted an ability not supported by HeartGold")
            if bool(ability.get("hidden", False)) != (ability["slot"] == 3):
                raise ValueError("Only slot 3 may be marked Hidden")
    targets = abilities["evolution_targets"]
    evolved = {row["species"]: row["hidden_ability_id"] for row in targets}
    if len(targets) != len(EXPECTED_EVOLUTION_HIDDEN) or evolved != EXPECTED_EVOLUTION_HIDDEN:
        raise ValueError("Evolution Hidden Ability catalog has drifted")
    for row in targets:
        ability_id = row["hidden_ability_id"]
        if ability_id is None:
            if row["species"] != 196 or row["hidden_ability"] != "Magic Bounce":
                raise ValueError("Unrecognized missing Hidden Ability")
            if (row.get("native_fallback") != "Synchronize"
                or row.get("native_fallback_id") != 28):
                raise ValueError("Espeon must use its native HG ability")
        elif NATIVE_HG_ABILITIES.get(ability_id) != row["hidden_ability"]:
            raise ValueError("Evolution requires an ability not supported by HeartGold")
    rules = {(entry["player_gender"], entry["chosen_starter"]):
             entry["rival_starter"] for entry in data["rival_rules"]}
    if len(rules) != len(data["rival_rules"]):
        raise ValueError("Duplicate rival rule")
    if any(k[0] not in VALID_GENDERS or k[1] not in (54, 133, 175)
           or v not in (54, 133, 175, None) for k, v in rules.items()):
        raise ValueError("Unsupported starter/gender/rival configuration")
    for entry in data['rival_rules']:
        if entry['rival_starter'] is None and (entry['chosen_starter'] != 175 or entry.get('rival_starter_choices') != [54,133]):
            raise ValueError('Unsupported random rival choice')
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


def rival_starter(player_gender: str, player_starter: int, randbelow=None) -> int:
    """Return the approved rival species, requiring an RNG for Togepi."""
    rules = {(entry["player_gender"], entry["chosen_starter"]):
             entry["rival_starter"] for entry in get_config()["rival_rules"]}
    if player_gender not in VALID_GENDERS or player_starter not in (54, 133, 175):
        raise ValueError("Invalid player gender or Kanto starter")
    key = (player_gender, player_starter)
    if key not in rules:
        raise NotImplementedError(f"Rival starter still requires supervisor decision: {key}")
    if rules[key] is None:
        if randbelow is None:raise ValueError('Togepi requires a random rival-choice roll')
        roll=randbelow(2)
        if type(roll) is not int or not 0<=roll<2:raise ValueError('Invalid rival-choice roll')
        return (54,133)[roll]
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


def starter_ability_options(species: int) -> tuple[int, int, int]:
    """Returns vetted vanilla-HeartGold effects for Kanto starter slots 1-3."""
    if species not in EXPECTED_STARTER_ABILITIES:
        raise ValueError("Not a supported Kanto starter")
    get_config()
    return EXPECTED_STARTER_ABILITIES[species]


def choose_starter_ability(species: int, randbelow) -> tuple[int, int, bool]:
    """Select (ability_id, slot_number, hidden) using uniform randbelow(3).

    This is pure planning logic, not an integrated DS ROM implementation.
    """
    abilities = starter_ability_options(species)
    index = randbelow(len(abilities))
    if type(index) is not int or index not in (0, 1, 2):
        raise ValueError("Ability roll must be an integer between 0 and 2")
    return abilities[index], index + 1, index == 2


def evolved_hidden_ability(species: int, previously_hidden: bool) -> tuple[int | None, bool]:
    """Return ability override and third-slot marker for an evolution.

    None means permit vanilla HeartGold to determine the ability, not invent a
    substitute Hidden Ability. On evolving Hidden Ability Eevee to Espeon,
    both result fields are reset because Magic Bounce is not in HeartGold.
    Other evolution branches are planned only; hooks have not been built.
    """
    if type(previously_hidden) is not bool:
        raise ValueError("Hidden Ability marker must be boolean")
    if species not in EXPECTED_EVOLUTION_HIDDEN:
        raise ValueError("Not a supported evolution of our three starters")
    get_config()
    ability = EXPECTED_EVOLUTION_HIDDEN[species]
    if not previously_hidden or ability is None:
        return None, False
    return ability, True
