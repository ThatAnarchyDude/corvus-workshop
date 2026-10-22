#!/usr/bin/env bash
# Direct DS-frame streaming works without system packages or root.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m venv "$project_dir/.venv"
"$project_dir/.venv/bin/python" -m pip install -r "$project_dir/requirements.txt" -r "$project_dir/requirements-live.txt"
if [[ "${1:-}" == '--x11' ]]; then
  packages=(xvfb x11vnc novnc websockify xdotool python3-tk)
  if [[ $EUID == 0 ]]; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"
  elif command -v sudo >/dev/null && sudo -n true 2>/dev/null; then
    sudo apt-get update
    sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"
  else
    echo 'Optional X11 packages need a root-enabled environment; direct streaming is ready.' >&2
    exit 2
  fi
fi
