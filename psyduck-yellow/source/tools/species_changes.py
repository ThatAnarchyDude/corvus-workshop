"""Owner-approved species changes applied by subsequent cumulative builders."""
import ndspy.narc

PERSONAL_ARCHIVE = 'a/0/0/2'
GOLDUCK = 55
WATER = 11
PSYCHIC = 14


def patch(rom):
    archive_id = rom.filenames.idOf(PERSONAL_ARCHIVE)
    personal = ndspy.narc.NARC(rom.files[archive_id])
    golduck = bytearray(personal.files[GOLDUCK])
    original_types = tuple(golduck[6:8])
    if original_types not in ((WATER, WATER), (WATER, PSYCHIC)):
        raise ValueError(f'Unexpected Golduck types: {original_types}')
    golduck[6:8] = bytes((WATER, PSYCHIC))
    personal.files[GOLDUCK] = bytes(golduck)
    rom.files[archive_id] = personal.save()
    return dict(species=GOLDUCK, original_types=list(original_types),
                types=[WATER, PSYCHIC], move_changes_deferred_until_after_kanto=True)
