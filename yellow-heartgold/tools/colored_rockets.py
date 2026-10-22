"""Owner-supplied colored Jessie/James class129 battle artwork, with strict bundle checks."""
import hashlib
from pathlib import Path
import ndspy.narc
ARCHIVE='a/0/5/8'
FILES=(
 (645,'645_animation.NCGR','0c84fd6032e3f37a4654cd7092d5dc39b768f030ee0095c070296d669fa7303b','7c683638ae7951b18cbf347a4eb2ecfb8ade33e03e4436471479b8743fe11447'),
 (646,'646_palette.NCLR','3bb0c0d35df2385c4a0a8afd710f6ff3dc1e5e8c8b7e183d1ba473de766604ec','0a6436e7570f36ab1ef99810f1a9b64bdfe630818791d5c6d71da6836d29f59d'),
 (647,'647_cells.NCER','8653d1a231b808ea29e3c614e7dcfc7eb1e8cc2042db51da415dfa58e8dea44c','8653d1a231b808ea29e3c614e7dcfc7eb1e8cc2042db51da415dfa58e8dea44c'),
 (648,'648_animation.NANR','57c4f638dca35c82365e420f8c7d794c33f8f33053ddda43d831536fc24b21f0','57c4f638dca35c82365e420f8c7d794c33f8f33053ddda43d831536fc24b21f0'),
 (649,'649_static.NCGR','c3a9df54a12d5890dffe0e7253aac2591034acd7a5bf48e1a98a1d263dc2309c','28df02101767ccdd6aafb92d55d241ca6ef5500b03cc9ccb0a3eb4851c552964'))

def sha(data):return hashlib.sha256(data).hexdigest()

def patch(rom,assets):
    assets=Path(assets);fid=rom.filenames.idOf(ARCHIVE);arc=ndspy.narc.NARC(rom.files[fid])
    old=tuple(sha(arc.files[mid]) for mid,*_ in FILES)
    assert old in (tuple(row[2] for row in FILES),tuple(row[3] for row in FILES)), 'Unknown or partially changed battle bundle'
    replacements=[]
    for mid,name,original,colored in FILES:
        raw=(assets/name).read_bytes()
        assert sha(raw)==colored and len(raw)==len(arc.files[mid]), ('Supplied asset mismatch',mid)
        replacements.append(raw)
    changed=[]
    for (mid,*_),raw in zip(FILES,replacements):
        if arc.files[mid]!=raw:changed.append(mid)
        arc.files[mid]=raw
    rom.files[fid]=arc.save()
    return dict(archive=ARCHIVE,trainer_class=129,trainer_id=777,changed_members=changed,
        colored_bundle_sha256={str(row[0]):row[3] for row in FILES},native_battle_verification_pending=True)
