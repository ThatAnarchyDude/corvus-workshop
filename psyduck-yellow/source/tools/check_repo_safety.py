#!/usr/bin/env python3
"""Reject original or rebuilt ROM images accidentally tracked in this repository.

This checks the current *tracked tree*, not previous Git history. It is not a
copyright audit of code, dialogue, images, or of the contents of patch files.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
import zipfile

ROM_FILE = re.compile(r"\.(?:nds|gbc|gb|gba|3ds|cia|sav|dsv|srm)$", re.I)
ARCHIVE = re.compile(r"\.(?:zip)$", re.I)

def tracked_files(root: pathlib.Path) -> list[pathlib.Path]:
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    return [root / name.decode("utf-8", "surrogateescape")
            for name in completed.stdout.split(b"\0") if name]

def scan(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for path in tracked_files(root):
        if not path.is_file():
            continue
        label = path.relative_to(root).as_posix()
        if ROM_FILE.search(path.name):
            errors.append(f"{label}: ROM or emulator-save file must stay local")
        elif ARCHIVE.search(path.name):
            try:
                with zipfile.ZipFile(path) as zf:
                    for entry in zf.infolist():
                        if not entry.is_dir() and ROM_FILE.search(entry.filename):
                            errors.append(
                                f"{label}: contains {entry.filename!r}; "
                                "ROM or emulator-save file must stay local"
                            )
            except zipfile.BadZipFile:
                errors.append(f"{label}: invalid ZIP archive; cannot verify")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors = scan(root)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ROM safety check could not complete: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("STOP: remove these files from the Git index before committing:")
        for error in errors:
            print("  -", error)
        print("Warning: deleting them in a later commit will NOT erase old history.")
        return 1
    print("PASS: no known ROM or save extensions in tracked files or ZIP members.")
    print("Note: current tree only; history and license review are separate.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
