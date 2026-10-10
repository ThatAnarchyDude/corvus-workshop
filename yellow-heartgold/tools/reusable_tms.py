"""Preserve all TM items after native successful teaching, including Bide."""
import ndspy.narc
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages,encode_messages,thumb_bl

CONSUME_SITE=0x020825B4
LEARN_MOVE=0x0208254C
TAKE_ITEM=0x02078434

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    at=CONSUME_SITE-0x02000000
    assert bytes(d[at:at+4])==thumb_bl(CONSUME_SITE,TAKE_ITEM)
    # This call belongs exclusively to TM/HM teaching. Keep move assignment,
    # PP reset, compatibility, friendship, mood and HM forgetting rules.
    # Other item consumption, selling, tossing and depositing remain native.
    d[at:at+4]=bytes.fromhex('c046c046')
    file=rom.filenames.idOf('a/0/2/7');texts=ndspy.narc.NARC(rom.files[file])
    key,messages=decode_messages(texts.files[221])
    messages[115]=decode_messages(encode_text(['A reusable TM containing BIDE. The user endures attacks, then returns the damage twofold.'],PH))[1][0]
    texts.files[221]=encode_messages(key,messages)
    rom.files[file]=texts.save();rom.arm9=main.save(compress=True)
    return dict(learning_function=hex(LEARN_MOVE),consumption_site=hex(CONSUME_SITE),
                all_native_tms_reusable=True,custom_bide_reusable=True,hms_unchanged=True)
