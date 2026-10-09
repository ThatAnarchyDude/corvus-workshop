"""Offline checks for the Git tracking safety gate. No proprietary ROMs required."""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from check_repo_safety import scan

class RepoSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def tracked(self, name: str, data: bytes):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        subprocess.run(["git", "-C", str(self.root), "add", "--", name], check=True)

    def zip(self, name: str, member: str):
        path = self.root / name
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr(member, b"dummy data; not an actual ROM")
        subprocess.run(["git", "-C", str(self.root), "add", "--", name], check=True)

    def test_clean_patch_archive_is_permitted(self):
        self.zip("safe-patch.zip", "prototype-003.xdelta")
        self.assertEqual(scan(self.root), [])

    def test_unpacked_nds_is_rejected(self):
        self.tracked("build/output.nds", b"dummy data")
        self.assertEqual(len(scan(self.root)), 1)

    def test_rom_hidden_in_zip_is_rejected(self):
        self.zip("some-release.zip", "readme/changed-game.nds")
        self.assertEqual(len(scan(self.root)), 1)

    def test_save_file_is_rejected(self):
        self.tracked("saves/test.dsv", b"dummy data")
        self.assertEqual(len(scan(self.root)), 1)

    def test_untracked_rom_not_flagged(self):
        (self.root / "source.gbc").write_bytes(b"dummy data")
        self.assertEqual(scan(self.root), [])

if __name__ == "__main__":
    unittest.main()
