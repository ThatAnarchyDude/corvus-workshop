#!/usr/bin/env bash
# Optional desktop stream for an installed GUI emulator; bind locally only.
# Usage: bash tools/start_x11_stream.sh desmume /private/prototype.nds
set -euo pipefail
if [[ $# == 0 ]]; then echo 'Supply a GUI emulator command and ROM path' >&2; exit 2; fi
for tool in Xvfb x11vnc websockify; do command -v "$tool" >/dev/null || { echo "Missing $tool: run install_live_testing.sh --x11 as root" >&2; exit 2; }; done
xvfb_pid=''; vnc_pid=''; web_pid=''; game_pid=''
cleanup() { for pid in "$game_pid" "$web_pid" "$vnc_pid" "$xvfb_pid"; do if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; fi; done; }
trap cleanup EXIT INT TERM
if [[ -e /tmp/.X99-lock ]]; then echo 'Display :99 already in use; refusing to attach to an unrelated desktop' >&2; exit 2; fi
Xvfb :99 -screen 0 1024x768x24 -nolisten tcp & xvfb_pid=$!
export DISPLAY=:99
for attempt in {1..50}; do [[ -S /tmp/.X11-unix/X99 ]] && break; sleep 0.1; done
[[ -S /tmp/.X11-unix/X99 ]] || { echo 'Xvfb failed to start' >&2; exit 1; }
x11vnc -display :99 -localhost -rfbport 5900 -nopw -forever -shared & vnc_pid=$!
websockify --web=/usr/share/novnc 127.0.0.1:6080 127.0.0.1:5900 & web_pid=$!
"$@" & game_pid=$!
echo 'Optional noVNC desktop listens on local port 6080. Use an authenticated workspace port-forward.'
wait "$game_pid"
