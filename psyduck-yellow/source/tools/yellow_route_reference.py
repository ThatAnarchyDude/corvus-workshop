"""Read-only Yellow Route9 campaign evidence (teams, moves, dialogue, wilds)."""
import re,hashlib
from pathlib import Path

def reference(source, map_name="Route9", expected_count=9, extra_roles=None, wild=True, first_index=0,header_count=None):
 source=Path(source);hashes={}
 def read(path):
  raw=(source/path).read_bytes();hashes[path]=hashlib.sha256(raw).hexdigest();return raw.decode()
 dex=re.findall(r'^\s*const\s+DEX_(\w+)',read('constants/pokedex_constants.asm'),re.M);assert len(dex)==151
 species={name:i+1 for i,name in enumerate(dex)}
 moves={name:i for i,name in enumerate(re.findall(r'^\s*const\s+(\w+)',read('constants/move_constants.asm'),re.M))}
 parties=read('data/trainers/parties.asm');evos=read('data/pokemon/evos_moves.asm')
 objects=read('data/maps/objects/'+map_name+'.asm');scripts=read('scripts/'+map_name+'.asm');texts=read('text/'+map_name+'.asm')+('\n'+read('text/'+map_name+'_2.asm') if (source/('text/'+map_name+'_2.asm')).exists() else '')
 def party(kind,index):
  block=re.search(r'^'+kind+r'Data:\s*\n(.*?)(?=^\w+Data:|\Z)',parties,re.M|re.S).group(1)
  row=[v.strip() for v in re.findall(r'^\s*db\s+([^;\n]+)',block,re.M)[index-1].split(',')];assert row[-1]=='0';level=int(row[0]);team=[]
  for name in row[1:-1]:
   base=read('data/pokemon/base_stats/'+name.lower().replace('_','')+'.asm');initial=re.search(r'db\s+([^;\n]+); level 1 learnset',base).group(1)
   learned=[m.strip() for m in initial.split(',') if m.strip()!='NO_MOVE']
   label=name.title().replace('_','')+'EvosMoves';learnset=re.search(r'^'+label+r':\s*\n(.*?)(?=^\w+EvosMoves:|\Z)',evos,re.M|re.S).group(1).split('; Learnset')[1]
   for lv,move in re.findall(r'^\s*db\s+(\d+),\s*(\w+)',learnset,re.M):
    if int(lv)<=level and move not in learned:learned=(learned+[move])[-4:]
   team.append(dict(species=species[name],symbol=name,level=level,moves=[moves[m] for m in learned]+[0]*(4-len(learned))))
  return team
 headers=re.findall(r'trainer EVENT_BEAT_\w+_TRAINER_(\d+),\s*(\d+),\s*(\w+)BattleText,\s*(\w+)EndBattleText,\s*(\w+)AfterBattleText',scripts);assert len(headers)==(header_count or expected_count)
 roles={'OPP_JR_TRAINER_F':'JrTrainerF','OPP_JR_TRAINER_M':'JrTrainerM','OPP_YOUNGSTER':'Youngster','OPP_HIKER':'Hiker','OPP_BUG_CATCHER':'BugCatcher','OPP_POKEMANIAC':'Pokemaniac','OPP_CHANNELER':'Channeler'}
 roles.update(extra_roles or {})
 entries=[]
 for row in re.findall(r'^\s*object_event\s+([^\n]+)',objects,re.M):
  f=[s.strip() for s in row.split(',')]
  if len(f)<8 or f[6] not in roles:continue
  i=len(entries);head=headers[i];assert int(head[0])==i+first_index;messages={}
  for suffix,label in zip(('BattleText','EndBattleText','AfterBattleText'),head[2:]):
   found=re.search(r'^_'+label+suffix+r'::\s*\n(.*?)(?=^_\w+::|\Z)',texts,re.M|re.S)
   if not found:   # pokeyellow ships some trainers without text; reuse the previous trainer's line
    messages[suffix]=entries[-1]['messages'][suffix];continue
   block=found.group(1)
   messages[suffix]=' '.join(re.findall(r'(?:text|line|cont|para)\s+"([^"]*)"',block)).replace('#MON','POKEMON').replace('<PLAYER>','{PLAYER}').replace('<RIVAL>','{RIVAL}')
  role=roles[f[6]];entries.append(dict(role=role,yellow_position=[int(f[0]),int(f[1])],facing=f[4],vision=int(head[1]),messages=messages,team=party(role,int(f[7]))))
 assert len(entries)==expected_count
 if not wild:return dict(map=map_name,trainers=entries,grass=[],grass_rate=0,source_sha256=hashes)
 wildtext=read('data/wild/maps/'+map_name+'.asm');grass_block=wildtext.split('end_grass_wildmons')[0];grass=[dict(level=int(lv),species=species[name]) for lv,name in re.findall(r'^\s*db\s+(\d+),\s*(\w+)',grass_block,re.M)];assert len(grass)==10
 rate=int(re.search(r'def_grass_wildmons\s+(\d+)',wildtext).group(1))
 return dict(map=map_name,trainers=entries,grass=grass,grass_rate=rate,source_sha256=hashes)


