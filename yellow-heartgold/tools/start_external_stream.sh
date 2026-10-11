#!/usr/bin/env bash
# Publish only the already-running, token-protected dashboard through a temporary tunnel.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
[[ -n ${LIVE_TEST_TOKEN:-} ]] || { echo 'Start the live runner with LIVE_TEST_TOKEN before exposing it externally.' >&2; exit 2; }
[[ -x "$project_dir/.tools/cloudflared" ]] || { echo 'Run tools/install_cloudflared.sh first.' >&2; exit 2; }
"$project_dir/.venv/bin/python" - <<'PY'
import os
from urllib.request import Request,urlopen
from urllib.error import HTTPError
url='http://127.0.0.1:8080/status'
try:
    with urlopen(url,timeout=5): pass
except HTTPError as exc:
    if exc.code!=403: raise
else:
    raise SystemExit('Refusing to expose a server without access-token protection.')
with urlopen(Request(url,headers={'X-Live-Token':os.environ['LIVE_TEST_TOKEN']}),timeout=5) as response:
    assert response.status==200
print('Protected dashboard verified; requesting temporary viewing URL.')
PY
exec "$project_dir/.tools/cloudflared" tunnel --url http://127.0.0.1:8080 --protocol http2 --no-autoupdate
