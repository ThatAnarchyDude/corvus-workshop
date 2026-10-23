#!/bin/bash
# Delete old build/ folders. Keeps 0037-0041 builds, owner-save-*, live-view-window-*.
# Usage: clean_old_builds.sh          (dry run: lists what would be deleted)
#        clean_old_builds.sh --delete (actually deletes)
cd "$(dirname "$0")/../build" || exit 1
KEEP='^(0037|0038|0039|0040|0041)-|^owner-save|^live-view-window'
LIST=$(ls -d */ | tr -d / | grep -v -E "$KEEP")
echo "$LIST" | wc -l | xargs echo "folders to delete:"
echo "$LIST" | xargs du -shc | tail -1
if [ "$1" = "--delete" ]; then
  echo "$LIST" | xargs rm -rf
  echo "done"; du -sh .
else
  echo "(dry run; re-run with --delete to remove)"
fi
