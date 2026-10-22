"""Replace only the captain entry with Yellow's recovery fanfare sequence."""
import struct
import ndspy.narc
from viridian_tutorial import TABLE
from ss_anne_captain import captain

def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);at=TABLE+255*24
 fid=rom.filenames.idOf('a/0/1/2');arc=ndspy.narc.NARC(rom.files[fid]);sid=struct.unpack_from('<H',d,at+6)[0]
 native=arc.files[sid];assert struct.unpack_from('<H',native,12)[0]==0xFD13
 bank=bytearray(native);bank.extend(bytes(-len(bank)%4));struct.pack_into('<I',bank,0,len(bank)-4);bank.extend(captain())
 ns=len(arc.files);arc.files.append(bank);struct.pack_into('<H',d,at+6,ns)
 rom.files[fid]=arc.save();rom.arm9=main.save(compress=True)
 return {'map':255,'old_script':sid,'script':ns,'recovery_fanfare':1183,'waits_for_fanfare':True,'faces_player_after_recovery':True,'native_test_pending':True}
