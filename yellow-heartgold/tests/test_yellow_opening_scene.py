"""Standalone scene-geometry and sound-constant regression checks."""
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from yellow_opening_scene import (
    NORTH_EXIT_COLUMNS, ORIGINAL_OAK_START, OAK_INTERCEPT_Z,
    BGM_OAK_MEETING, BGM_OAK_ESCORT, BGM_RIVAL_CHALLENGE,
    CMD_PLAY_BGM, CMD_APPLY_MOVEMENT, CMD_PLAY_SE, MOVE_LEFT, MOVE_UP,
    destination, follow_path, oak_approach
)

class AuthenticOpeningStageTests(unittest.TestCase):
    def test_all_route_exit_columns_have_a_walk_in(self):
        for x in NORTH_EXIT_COLUMNS:
            with self.subTest(exit_x=x):
                path=oak_approach(x)
                self.assertEqual(path[0].movement, MOVE_LEFT)
                self.assertEqual(path[1].movement, MOVE_UP)
                self.assertEqual(destination(ORIGINAL_OAK_START, path), (x,OAK_INTERCEPT_Z))

    def test_reverse_path_returns_oak_to_his_original_position(self):
        for x in NORTH_EXIT_COLUMNS:
            path=oak_approach(x)
            back=follow_path(path)
            self.assertEqual(destination((x,OAK_INTERCEPT_Z), back), ORIGINAL_OAK_START)

    def test_unexpected_columns_fail_closed(self):
        for x in (0,1029,1034,1040):
            with self.assertRaises(ValueError):
                oak_approach(x)

    def test_references_use_verified_script_and_sound_ids(self):
        self.assertEqual(CMD_APPLY_MOVEMENT, 94)
        self.assertEqual(CMD_PLAY_BGM, 80)
        self.assertEqual(CMD_PLAY_SE, 73)
        self.assertEqual((BGM_OAK_MEETING,BGM_OAK_ESCORT,BGM_RIVAL_CHALLENGE),(1067,1086,1088))

if __name__ == "__main__":
    unittest.main()
