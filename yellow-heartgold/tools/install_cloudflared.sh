#!/usr/bin/env bash
# Verified optional tunnel client. No tunnel is opened during installation.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || { echo 'This pinned download supports Linux x86_64 only.' >&2; exit 2; }
mkdir -p "$project_dir/.tools"
download_path=$(mktemp "$project_dir/.tools/cloudflared.XXXXXX")
trap 'rm -f "$download_path"' EXIT
curl -fsSL --max-time 60 'https://github.com/cloudflare/cloudflared/releases/download/2026.10.0/cloudflared-linux-amd64' -o "$download_path"
# Official release page / GitHub asset digest, 2026.10.0.
printf '%s  %s\n' 'd33ff2d14475178d2012c2c56beba87389ac5ded27649519f198a7d3134a99db' "$download_path" | sha256sum -c -
chmod 755 "$download_path"
mv "$download_path" "$project_dir/.tools/cloudflared"
"$project_dir/.tools/cloudflared" --version
