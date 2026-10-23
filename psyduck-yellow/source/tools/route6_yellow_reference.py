"""Extract Route 6 trainer evidence from a read-only local Yellow source tree."""
import hashlib,re
from pathlib import Path

SPECIES={'WEEPINBELL':70,'CUBONE':104,'WEEDLE':13,'CATERPIE':10,'BUTTERFREE':12,'SPEAROW':21,'RATICATE':20,'PIDGEY':16}

def trainer_reference(source):
    source=Path(source);inputs={}
    def read(path):
        data=(source/path).read_bytes();inputs[path]=hashlib.sha256(data).hexdigest();return data.decode()
    constants=read('constants/move_constants.asm')
    moves={name:i for i,name in enumerate(re.findall(r'^\s*const\s+(\w+)',constants,re.M))}
    parties=read('data/trainers/parties.asm');evos=read('data/pokemon/evos_moves.asm')
    objects=read('data/maps/objects/Route6.asm');text=read('text/Route6.asm');script=read('scripts/Route6.asm')
    def party(kind,index):
        block=re.search(r'^'+kind+r'Data:\s*\n(.*?)(?=^\w+Data:|\Z)',parties,re.M|re.S).group(1)
        rows=re.findall(r'^\s*db\s+([^;\n]+)',block,re.M);row=[v.strip() for v in rows[index-1].split(',')]
        assert row[-1]=='0' and row[0].isdigit()
        level=int(row[0]);team=[]
        for mon in row[1:-1]:
            base=read('data/pokemon/base_stats/'+mon.lower()+'.asm')
            initial=re.search(r'db\s+([^;\n]+); level 1 learnset',base).group(1)
            learned=[m.strip() for m in initial.split(',') if m.strip()!='NO_MOVE']
            label=mon.title().replace('_','')+'EvosMoves'
            block=re.search(r'^'+label+r':\s*\n(.*?)(?=^\w+EvosMoves:|\Z)',evos,re.M|re.S).group(1).split('; Learnset')[1]
            for lv,move in re.findall(r'^\s*db\s+(\d+),\s*(\w+)',block,re.M):
                if int(lv)<=level and move not in learned:learned=(learned+[move])[-4:]
            team.append(dict(species=SPECIES[mon],symbol=mon,level=level,moves=[moves[m] for m in learned]+[0]*(4-len(learned)),move_names=learned))
        return team
    entries=[]
    for row in re.findall(r'^\s*object_event\s+([^\n]+)',objects,re.M):
        fields=[x.strip() for x in row.split(',')];x,y=int(fields[0]),int(fields[1]);kind={'OPP_JR_TRAINER_M':'JrTrainerM','OPP_JR_TRAINER_F':'JrTrainerF','OPP_BUG_CATCHER':'BugCatcher'}[fields[6]]
        token=fields[5].removeprefix('TEXT_ROUTE6_');dialogue='Route6'+{'COOLTRAINER_M1':'CooltrainerM1','COOLTRAINER_F1':'CooltrainerF1','YOUNGSTER1':'Youngster1','COOLTRAINER_M2':'CooltrainerM2','COOLTRAINER_F2':'CooltrainerF2','YOUNGSTER2':'Youngster2'}[token]
        lines={}
        for suffix in ('BattleText','EndBattleText','AfterBattleText'):
            block=re.search(r'^_'+dialogue+suffix+r'::\s*\n(.*?)(?=^_\w+::|\Z)',text,re.M|re.S).group(1)
            lines[suffix]=' '.join(re.findall(r'(?:text|line|cont|para)\s+"([^"]*)"',block)).replace('#MON','POKEMON')
        vision=int(re.search(r'trainer EVENT_BEAT_ROUTE_6_TRAINER_'+str(len(entries))+r',\s*(\d+)',script).group(1))
        entries.append(dict(role=kind,yellow_party_index=int(fields[7]),yellow_position=[x,y],facing=fields[4],vision=vision,dialogue=dialogue,messages=lines,team=party(kind,int(fields[7]))))
    assert len(entries)==6
    return dict(map='Route6',trainers=entries,source_sha256=inputs,scope='Source evidence only; trainer installation and final exterior positions remain pending')
