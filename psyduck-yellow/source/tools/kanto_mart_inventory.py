"""One cumulative Kanto inventory definition shared by participating Marts."""
import struct
from opening import Script
BALLS=frozenset(('POKE_BALL','GREAT_BALL','ULTRA_BALL'))
FORBIDDEN=frozenset(('MASTER_BALL','CHERISH_BALL'))
ORDER=('Pewter','Cerulean','Vermilion','Lavender','Fuchsia','Saffron','Cinnabar','Viridian')

def kanto_badge_count(profile_badges):
 if not 0<=profile_badges<=0xFFFF:raise ValueError('Expected native 16-bit badge flags')
 return (profile_badges>>8).bit_count()

def badge_count_script():
 # Native CheckBadge uses profile bits8..15. Local special variables are temporary.
 s=Script().emit(41,0x8004,0)
 for badge in range(8,16):s.emit(294,badge,0x800C).emit(39,0x8004,0x800C)
 return s.finish()

def build_stages(source):
 stock=[];result=[]
 def add(names):
  if FORBIDDEN.intersection(names):raise ValueError('Forbidden shop ball')
  for name in names:
   if name not in stock:stock.append(name)
 def snapshot(count,city):
  result.append({'badges':count,'added_from':city,'balls':[n for n in stock if n in BALLS],'supplies':[n for n in stock if n not in BALLS]})
 add(source['Viridian']);snapshot(0,'Viridian')
 for count,city in enumerate(ORDER,1):
  add(source[city])
  snapshot(count,city)
 return result

def stage_for_mask(stages,profile_badges):
 count=kanto_badge_count(profile_badges)
 if count>=len(stages):raise ValueError('Inventory stage awaits owner clarification')
 return stages[count]