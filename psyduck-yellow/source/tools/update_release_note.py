"""Adds (or refreshes) the real-hardware note on the prototype-0110-beta GitHub release page. Needs the owner's temporary token in env GH_TOKEN; the token is never written to disk.
Usage: GH_TOKEN=... update_release_note.py [--dry-run]"""
import json
import os
import sys
import urllib.request

API = 'https://api.github.com/repos/ThatAnarchyDude/Psyduck-Yellow-Releases/releases/tags/prototype-0110-beta'
MARK = '<!-- real-hardware-note -->'
NOTE = MARK + '''
## Real DS / 3DS: not working yet
This beta has only been played in PC emulators (DeSmuME and RetroArch's DeSmuME core). **Play it in an emulator.**
On a hacked **3DS** running it through nds-bootstrap (v2.17.0) the game crashes with a red *"Data Abort"* screen on **Route 2 north**, at the point between the Diglett's Cave entrance and Pewter City (walking up the fenced path, or into the tall grass beside it). Changing nds-bootstrap's settings and re-ordering the files inside the ROM did not help. The cause is not known yet. A real DS with a flashcart has not been tested. Treat real hardware as **untested**.
'''


def call(token, method, data=None):
    req = urllib.request.Request(API if data is None else data['url'], method=method, headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json'}, data=data and json.dumps(data['body']).encode())
    return json.load(urllib.request.urlopen(req))


def main():
    token = os.environ['GH_TOKEN']
    rel = call(token, 'GET')
    body = rel['body']
    if MARK in body:
        body = body[:body.index(MARK)].rstrip() + '\n\n'
    marker = '\nFiles below:'
    at = body.index(marker) if marker in body else len(body)
    new = body[:at].rstrip() + '\n\n' + NOTE + body[at:]
    if '--dry-run' in sys.argv:
        print(new)
        return
    out = call(token, 'PATCH', {'url': rel['url'], 'body': {'body': new}})
    print('updated', out['html_url'])


if __name__ == '__main__':
    main()
