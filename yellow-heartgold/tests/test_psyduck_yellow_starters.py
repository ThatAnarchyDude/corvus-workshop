"""Psyduck Yellow: explicit Kanto starter rules and Gen-IV gender logic."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from psyduck_yellow_starters import (
    get_config, player_starter_at, required_starter_gender, rival_starter,
    pokemon_gender_for_pid, matches_required_gender,
)

class PsyduckYellowStarterTests(unittest.TestCase):
    def test_game_name_and_table_order(self):
        self.assertEqual(get_config()["project_name"], "Pokémon Psyduck Yellow")
        self.assertEqual([player_starter_at(x) for x in ("left","center","right")],
                         [54,175,133])

    def test_gender_independent_of_player_gender(self):
        self.assertEqual(required_starter_gender(54),"male")
        self.assertEqual(required_starter_gender(133),"female")
        self.assertEqual(required_starter_gender(175),"natural")

    def test_explicit_blue_rival_choices(self):
        self.assertEqual(rival_starter("male",133),54)
        self.assertEqual(rival_starter("female",54),133)
        self.assertEqual(rival_starter("male",175),133)
        self.assertEqual(rival_starter("female",175),133)

    def test_unspecified_choices_fail_closed(self):
        with self.assertRaises(NotImplementedError):
            rival_starter("male",54)
        with self.assertRaises(NotImplementedError):
            rival_starter("female",133)

    def test_invalid_entries_fail_closed(self):
        for gender,species in (("other",54),("male",25),("female",155)):
            with self.assertRaises(ValueError):
                rival_starter(gender,species)

    def test_gen_iv_pid_gender_selection(self):
        # Hypothetical thresholds: actual species ratio must be loaded from ROM.
        self.assertEqual(pokemon_gender_for_pid(54, 0xFFFFFFFF, 127),"male")
        self.assertEqual(pokemon_gender_for_pid(54, 0x12340000, 127),"female")
        self.assertEqual(pokemon_gender_for_pid(133,0,31),"female")
        self.assertEqual(pokemon_gender_for_pid(133,0xFF,31),"male")
        self.assertEqual(pokemon_gender_for_pid(175,5,255),"genderless")
        self.assertEqual(pokemon_gender_for_pid(54,5,254),"female")
        self.assertEqual(pokemon_gender_for_pid(54,5,0),"male")

    def test_gender_constraints_respect_pokemon_not_player(self):
        self.assertTrue(matches_required_gender(54,0x7F,127))
        self.assertFalse(matches_required_gender(54,0x7E,127))
        self.assertTrue(matches_required_gender(133,0x1E,31))
        self.assertFalse(matches_required_gender(133,0x1F,31))
        self.assertTrue(matches_required_gender(175,0x1F,31))
        self.assertTrue(matches_required_gender(175,0x01,31))

    def test_johto_baseline_is_not_changed(self):
        self.assertEqual(get_config()["johto_preservation"]["original_starters"],[152,155,158])

if __name__ == "__main__":
    unittest.main()
