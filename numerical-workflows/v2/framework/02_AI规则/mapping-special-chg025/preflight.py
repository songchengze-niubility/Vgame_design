"""CHG-025 Excel read-only baseline; source values are not authoring instructions."""
import hashlib
import json
import os
from pathlib import Path
import openpyxl

HERE=Path(__file__).resolve().parent
FRAMEWORK=HERE.parent.parent
OUT=FRAMEWORK/'06_最终配置/映射装备'
CONFIG=Path(os.environ['VGAME_CONFIG_DATAS'])
RULES=json.loads((HERE.parent/'mapping-named-chg024/rules.json').read_text(encoding='utf-8'))
IDS=set(RULES['skills'].values())
FILES=['SpecialEquipment.xlsx','SpecialEquipmentEffectDrop.xlsx','SpecialEquipmentEffect.xlsx','00_配置清单.xlsx']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def snap(p,width=None,data_only=False):
    w=openpyxl.load_workbook(p,read_only=True,data_only=data_only)
    result={}
    for s in w:
        s.reset_dimensions()
        result[s.title]=[list(r) for r in s.iter_rows(max_col=width,values_only=True)]
    w.close()
    return result

before={f:snap(OUT/f) for f in FILES}
eq=before[FILES[0]]['SpecialEquipment']
ef=before[FILES[2]]['SpecialEquipment']
pool=before[FILES[1]]['SpecialEquipment']
assert len(eq)==484 and len(ef)==943 and len(pool)==263
assert not IDS.intersection(r[1] for r in pool[4:])
formal_pool=snap(CONFIG/'SpecialEquipment/SpecialEquipmentEffectDrop.xlsx',3)['SpecialEquipment']
assert not IDS.intersection(r[1] for r in formal_pool[4:] if r[0]!='##')
source_path=Path('C:/Users/songchengze/Downloads/映射装备.xlsx')
source=snap(source_path,9)[RULES['sourceSheet']]
source_skills={r[3]:r[2] for r in source[98:] if isinstance(r[2],int)}
assert source_skills==RULES['skills']
skills=next(iter(snap(CONFIG/'Skill/Skill.xlsx',14,True).values()))
assert IDS<={r[1] for r in skills[4:] if r[0]!='##' and r[9]=='SkillsSpecialEquipment'}
changes=[];bindings=[]
for n,r in enumerate(eq[4:],5):
    name=RULES['aliases'].get(r[2],r[2])
    named=source_skills.get(name) if r[5]=='Red' else None
    if named:bindings.append({'equipmentId':r[1],'name':r[2],'grade':r[3],'quality':r[5],'skillName':name,'skillId':named})
    expected={9:r[9] if r[5] in ('Orange','Red') else None,10:named,11:None if r[11] in IDS else r[11]}
    for col,new in expected.items():
        assert not (isinstance(r[col],str) and r[col].startswith('='))
        if r[col]!=new:changes.append({'row':n,'col':col,'old':r[col],'new':new})
assert [b['equipmentId'] for b in bindings]==RULES['expectedEquipmentIds']
assert {c:sum(x['col']==c for x in changes) for c in (9,10,11)}=={9:288,10:480,11:22}
tracked=[CONFIG/'SpecialEquipment'/f for f in FILES[:3]]+[CONFIG/'SpecialEquipment/SpecialEquipmentQuality.xlsx',CONFIG/'Skill/Skill.xlsx',source_path]
pre={'files':FILES,'before':before,'changes':changes,'bindings':bindings,'skills':source_skills,
     'candidateHashes':{p.name:sha(p) for p in OUT.glob('*.xlsx')},'formalHashes':{str(p):sha(p) for p in tracked}}
(HERE/'preflight.json').write_text(json.dumps(pre,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'clearRare':288,'replaceSpecial':480,'clearFix':22,'newPools':21,'bindings':22},ensure_ascii=False))
