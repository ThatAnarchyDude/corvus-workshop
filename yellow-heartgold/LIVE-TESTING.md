# Watching cloud playtests

The Python live runner serves both Nintendo DS screens alongside a RAM HUD.
It uses the same DeSmuME libretro core as our existing automated tests. Frames
come directly from the emulator callback, and controller presses use its native
input callback. Xvfb, screen clicks, OpenCV, WebRTC and a desktop are unnecessary
for this mode. The MJPEG feed is silent; music testing still needs another method.

Video starts **off**. Turning it off stops JPEG encoding and transmission;
emulation and RAM monitoring continue. The dashboard has video switches and
controller buttons. The HUD also prints to the agent terminal once per second
and writes a bounded `live-metrics.jsonl` log in the private save directory.

## Install and launch

From `yellow-heartgold`:

```bash
bash tools/install_live_testing.sh
.venv/bin/python tools/cloud_test_suite.py \
  --rom build/yellow-heartgold-prototype-0022.nds \
  --save-dir build/live-testing
```

Supply an existing, private ROM and the existing verified core at
`.tools/emulator/desmume_libretro.so`, or specify `--core`. The installer does
not download ROMs or emulator binaries. It installs the project dependencies
plus the optional PyVirtualDisplay and Xlib wrappers.

The dashboard listens at `http://127.0.0.1:8080/` **inside the machine running
it**. This is not a public download or remotely accessible chat link. To watch
from another computer, use the workspace's authenticated port-forward/preview
feature if available, or a tunnel to a machine you control. Only once a port
preview is actually provided should the agent say “Open the live web preview on
port 8080.” A script cannot create a ChatGPT side panel, choose its layout, or
close it. This task's cloud onboarding interface supplies no port-preview tool;
the local service can be verified, but a user-visible preview is not established.

Non-loopback `--host` bindings require `LIVE_TEST_TOKEN` in the process
environment. Use a private, authenticated forwarding service. Provide the same
token in the browser URL fragment `#token=...`; it is not a GitHub secret or
committed setting. No ROM, arbitrary filesystem, raw RAM, or save-file download
endpoints are exposed. The stream is temporary, not a recording archive.

## Chat commands and automated input

There is no Python API for listening to this ChatGPT conversation. During an
active session, the agent handles `/video on` and `/video off` by running:

```bash
.venv/bin/python tools/live_control.py on
.venv/bin/python tools/live_control.py off
.venv/bin/python tools/live_control.py status
.venv/bin/python tools/live_control.py press a --frames 8
.venv/bin/python tools/live_control.py stop
```

The loop accepts explicit presses only. Tests can use `--actions` with
a JSON file, for example `["invalid"]` is rejected, while
`[{"button":"a","frames":8},{"button":"down","frames":8}]` queues two
presses with release frames between them. Run planned navigation through this
bridge when watching tests, rather than a second emulator process. All RAM,
controller and core operations run on one thread; HTTP clients see copied data.

`/video off` pauses the feed, without shutting down the emulator. `stop` requests
a clean shutdown and native battery-save flush. Use the game's Save menu often;
shutdown is not a substitute for saving progress. Copy a normal `.dsv` into the
private save directory under the exact ROM basename before launching to reuse
progress. Never overwrite your sole save. This runner does not load cross-ROM
emulator save states. Core save directories must have a single active owner.

## RAM HUD

Read-only monitoring validates native HeartGold FieldSystem pointers and live
save-block headers, then shows map ID, player X/Y tile coordinates, height,
party size, parcel state and National Pokédex status. Pointer discovery is
cached only while validation succeeds. During an intro, battle or map transition,
`ram: null` means no validated field data was found. Field data may remain present
in a battle and does not prove battle activity. Battle and text-box status are
explicitly unavailable until separately validated hooks are added. Monitoring
does not inject memory or grant items.

## Optional X11/noVNC desktop

On a root-enabled Debian/Ubuntu runner:

```bash
bash tools/install_live_testing.sh --x11
bash tools/start_x11_stream.sh desmume /private/prototype.nds
```

This helper starts `Xvfb :99 -screen 0 1024x768x24`, sets `DISPLAY=:99`,
then starts local x11vnc and noVNC/websockify. It cleans up only its own processes
and refuses to attach to a pre-existing display. Install a GUI emulator separately
and supply its actual CLI syntax; the libretro core is not a `desmume` executable.
noVNC listens locally on port **6080**, separate from the RAM dashboard on 8080.
Use an authenticated tunnel to `vnc.html`; do not expose the passwordless local
VNC endpoint publicly. This optional desktop route is not installed/tested in the
current non-root container. Direct native controller input is the tested route,
not X11 keyboard injection. A GUI-emulator desktop does not automatically share
RAM telemetry with the separate libretro process.

## Validation

```bash
.venv/bin/python -m unittest discover -s tools -p 'test_live_testing.py'
```

The tests cover default-off state, token/origin checks, input validation, pause
behavior, MJPEG decoding and unknown RAM. A native emulator smoke test must also
verify boot, Continue, live frames and meaningful RAM fields before claiming a
playtest stream works. Local verification does not establish remote preview
access or Android compatibility.

## External viewing URL

Optional Cloudflare Quick Tunnel setup, without a paid account:

```bash
bash tools/install_cloudflared.sh
# Generate a private access token in your shell; do not commit it.
export LIVE_TEST_TOKEN="$(.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))')"
# Start the runner with this environment variable, then in a second shell
# with the same LIVE_TEST_TOKEN:
bash tools/start_external_stream.sh
```

The helper verifies token protection before opening a tunnel. Cloudflare prints
an actual `https://...trycloudflare.com` URL only after successful provisioning.
Append `/#token=YOUR_TOKEN` to access the HUD and feed. Keep the full access link
private; it expires when the tunnel stops. This has no uptime guarantee, may be
buffered by intermediate proxies, and is not a permanent development log URL.
Do not publish the token or full access link in the repository. Stop the tunnel
when the session ends; future sessions will need a new tunnel URL.

**Current external-access blocker (October 11, 2026):** the verified Cloudflare
client cannot resolve `api.trycloudflare.com` in this container. An independent
HTTPS request through the environment proxy also returns CONNECT 403. No
external URL was issued. The environment owner must enable a supported inbound
port preview/forwarder, or permit the tunnel service and its edge connectivity
before remote viewing works. Cloudflare Tunnel requires access to its API and
edge domains with outbound port 7844; enabling ordinary HTTPS alone may not
suffice. The scripts do not bypass the environment network policy. The client
installer and native local stream work; the external tunnel remains unverified.

The tunnel was retried after a turn-scoped network permission grant and outside
the command sandbox. The same DNS failure remained, so the restriction requires
a hosting/network configuration change, not another script or dependency.
