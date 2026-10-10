"""Psyduck Yellow: explicit Kanto starter rules and Gen-IV gender logic."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from psyduck_yellow_starters import (
    get_config, player_starter_at, required_starter_gender, rival_starter,
    pokemon_gender_for_pid, matches_required_gender,
    starter_ability_options, choose_starter_ability, evolved_hidden_ability,
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
        self.assertEqual(rival_starter("male",175,lambda n:1),133)
        self.assertEqual(rival_starter("female",175,lambda n:0),54)

    def test_remaining_choices_use_paired_favourites(self):
        self.assertEqual(rival_starter("male",54),133)
        self.assertEqual(rival_starter("female",133),54)

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

    def test_three_vetted_starter_abilities_each(self):
        self.assertEqual(starter_ability_options(54), (6,13,33))
        self.assertEqual(starter_ability_options(175), (55,32,105))
        self.assertEqual(starter_ability_options(133), (50,91,107))
        with self.assertRaises(ValueError):
            starter_ability_options(152)

    def test_uniform_slot_selection_boundaries(self):
        for species in (54, 175, 133):
            expected=starter_ability_options(species)
            for i, ability in enumerate(expected):
                self.assertEqual(choose_starter_ability(species, lambda n, i=i: i),
                                 (ability, i+1, i==2))
        for bad in (-1,3,False,1.0):
            with self.assertRaises(ValueError):
                choose_starter_ability(54, lambda n,bad=bad: bad)

    def test_native_evolution_ability_for_hidden_starters(self):
        expected={55:33,176:105,468:105,134:93,135:95,136:62,
                  197:39,470:34,471:115}
        for species, ability in expected.items():
            with self.subTest(species=species):
                self.assertEqual(evolved_hidden_ability(species,True),(ability,True))
                self.assertEqual(evolved_hidden_ability(species,False),(None,False))

    def test_espeon_magic_bounce_is_unavailable_and_falls_back(self):
        self.assertEqual(evolved_hidden_ability(196,True),(None,False))
        self.assertEqual(evolved_hidden_ability(196,False),(None,False))

    def test_never_override_johto_or_other_species(self):
        for species in (25,152,155,158,700):
            with self.assertRaises(ValueError):
                evolved_hidden_ability(species,True)

    def test_johto_baseline_is_not_changed(self):
        self.assertEqual(get_config()["johto_preservation"]["original_starters"],[152,155,158])

if __name__ == "__main__":
    unittest.main()
