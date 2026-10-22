"""Read-only Yellow dialogue (pret/pokeyellow text/*.asm) flattened to project message strings."""
import re
from pathlib import Path


def flatten(block):
    out = []
    for kind, body in re.findall(r'^\s*(text|line|cont|para|page|done|prompt|text_ram)\s*(?:"([^"]*)")?', block, re.M):
        if kind in ('para', 'page'):
            out.append('\r')
        if body:
            out.append(('' if not out or out[-1] == '\r' else ' ') + body)
    s = ''.join(out)
    s = s.replace('<PLAYER>', '{PLAYER}').replace('<RIVAL>', '{RIVAL}').replace('#MON', 'POKEMON').replace('<PKMN>', 'POKEMON')
    s = s.replace('é', 'e').replace('<……>', '...').replace('…', '...')
    return re.sub(r' +', ' ', s).strip()


def message(source, file, label):
    raw = (Path(source) / 'text' / (file + '.asm')).read_text()
    m = re.search(r'^' + re.escape(label) + r'::\s*\n(.*?)(?=^_?\w+::|\Z)', raw, re.M | re.S)
    if not m:
        raise KeyError(label)
    return flatten(m.group(1))
