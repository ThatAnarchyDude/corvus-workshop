"""Static Pokedex audit: python dex_audit.py <rom> [out.json]. Per dex number 1..1026 checks list->species, text rows, per-species tables."""
import json, struct, sys
from collections import Counter
import ndspy.rom, ndspy.narc
from prototype import decode_messages

rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
lists = ndspy.narc.NARC(rom.getFileByName('a/2/1/4'))
raw = bytes(lists.files[11])
order = struct.unpack('<%dH' % (len(raw) // 2), raw)
BANKS = dict(entry=803, w1=812, w2=813, h1=814, h2=815, category=816, name=817, cat2=823)
bank = {k: decode_messages(texts.files[v])[1] for k, v in BANKS.items()}
pad = {k: bank[k][494] for k in bank}
narcs = {p: ndspy.narc.NARC(rom.getFileByName(p)) for p in ('a/2/5/6', 'a/2/4/8', 'a/2/2/1', 'a/0/6/9')}
size_arr = [bytes(lists.files[i]) for i in (0, 1, 2)]
def gen(n):
    for i, hi in enumerate((151, 251, 386, 493, 649, 721, 809, 905, 1025), 1):
        if n <= hi: return i
    return 10
print('list entries', len(order), 'unique', len(set(order)), 'max', max(order), 'min', min(order))
dups = [s for s, c in Counter(order).items() if c > 1]
print('duplicate species in list:', dups[:20])
res = {}
for n, sp in enumerate(order, 1):
    p = []
    for k in bank:
        if sp >= len(bank[k]): p.append(k + ':missing')
        elif bank[k][sp] == pad[k] and sp != 494: p.append(k + ':padrow')
        elif not bank[k][sp]: p.append(k + ':empty')
    for path, nr in narcs.items():
        if sp >= len(nr.files): p.append(path + ':missing')
        elif len(nr.files[sp]) == 0: p.append(path + ':empty')
        elif sp != 494 and bytes(nr.files[sp]) == bytes(nr.files[494]): p.append(path + ':==pad')
    res[n] = dict(species=sp, gen=gen(n), problems=p)
gens = {}
for n, r in res.items():
    g = gens.setdefault(r['gen'], dict(total=0, bad=0, kinds=Counter()))
    g['total'] += 1
    if r['problems']:
        g['bad'] += 1
        for q in r['problems']: g['kinds'][q] += 1
for g, v in sorted(gens.items()): print('gen', g, v['total'], 'bad', v['bad'], dict(v['kinds']))
json.dump(res, open(sys.argv[2] if len(sys.argv) > 2 else '/dev/null', 'w'))
