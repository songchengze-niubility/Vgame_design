"""Independent read-only XLSX checks. No workbook authoring."""
import copy
import hashlib
import json
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
FRAMEWORK = HERE.parent.parent
OUT = FRAMEWORK / "06_最终配置/映射装备"
TARGET = OUT if "--final" in sys.argv else HERE / "staged"
PRE = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))
RULES = json.loads((HERE / "rules.json").read_text(encoding="utf-8"))
checks = []


def check(name, ok, detail=None):
    checks.append({"name":name,"pass":bool(ok),"detail":detail})


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snap(p, data_only=False):
    w = openpyxl.load_workbook(p,read_only=True,data_only=data_only)
    result = {}
    for s in w:
        s.reset_dimensions()
        result[s.title] = [list(r) for r in s.iter_rows(values_only=True)]
    w.close()
    return result


def cell(rs,r,c):
    return rs[r][c] if r<len(rs) and c<len(rs[r]) else None


def same(a,b):
    return all(cell(a,r,c)==cell(b,r,c) for r in range(max(len(a),len(b))) for c in range(max(len(a[r]) if r<len(a) else 0,len(b[r]) if r<len(b) else 0)))


books = {f:snap(TARGET/f) for f in PRE["files"]}
eq = books["SpecialEquipment.xlsx"]["SpecialEquipment"]
old_eq = PRE["before"]["SpecialEquipment.xlsx"]["SpecialEquipment"]
expected = copy.deepcopy(old_eq)
source_skills = PRE["sourceSkills"]
ids = {v["id"] for v in source_skills.values()}
bound = []
for n,r in enumerate(expected[4:],4):
    if r[5] == "Red":
        r[2] = PRE["formalNames"][str(r[1])]
        name = RULES["aliases"].get(r[2],r[2])
        r[11] = source_skills.get(name,{}).get("id")
        if r[11] is not None:
            bound.append(r)
    check(f"Equipment:{r[1]}完整行",eq[n]==r)
check("装备480条且Schema保留",len(eq)==484 and eq[:4]==old_eq[:4])
check("22件红装21种技能",len(bound)==22 and {r[11] for r in bound}==ids)
check("22件装备Id集合",sorted(r[1] for r in bound)==RULES["expectedEquipmentIds"])
check("384件非红装逐格不变",all(eq[n]==r for n,r in enumerate(old_eq) if n>=4 and r[5]!='Red'))
check("所有具名技能仅红装固定绑定",all(r[5]=='Red' for r in eq[4:] if r[11] in ids))
check("10个名称更新",sum(a[2]!=b[2] for a,b in zip(eq[4:],old_eq[4:]))==10)
check("虚空突袭之刃不绑定",any(r[1]==80393 and r[2]=='虚空突袭之刃' and r[11] is None for r in eq[4:]))
check("35/55同名手套均30602",{r[1]:r[11] for r in eq[4:] if r[2]=='白色针织劳保手套' and r[5]=='Red'}=={80451:30602,80455:30602})
for r in eq[4:]:
    if r[5] in ('Orange','Red'):
        suffix=(1 if r[3]<=20 else 2 if r[3]<=40 else 3)+(3 if r[5]=='Red' else 0)
        check(f"六档RareEffect保留:{r[1]}",r[9]==6000+suffix)
check("全部SpecialEffect原值保留",all(a[10]==b[10] for a,b in zip(eq,old_eq)))

effects=books['SpecialEquipmentEffect.xlsx']['SpecialEquipment']
old_effects=PRE['before']['SpecialEquipmentEffect.xlsx']['SpecialEquipment']
by_id={r[1]:r for r in effects[4:]}
check("原918条Effect及Schema不变",effects[:len(old_effects)]==old_effects)
check("新增21条且全部Id唯一",len(effects)==943 and len(by_id)==939 and set(by_id)-{r[1] for r in old_effects[4:]}==ids)
template=next(r for r in old_effects if r[1]==3101)
for i in sorted(ids):
    e=list(template);e[1]=e[7]=i
    check(f"纯技能Effect:{i}",by_id.get(i)==e)
    check(f"Skill存在与资源路径:{i}",PRE['skillRows'][str(i)][9]=='SkillsSpecialEquipment' and PRE['skillRows'][str(i)][11]==f'MappingEquip/ME_skill_{i}')
check("22条FixEffect引用闭环",all(r[11] in by_id and by_id[r[11]][7]==r[11] for r in bound))

for f,before in PRE['before'].items():
    for sn,old in before.items():
        if sn=='SpecialEquipment':
            continue
        current=books[f][sn]
        allowed={(r,1) for r in (2,3,6,8)} if sn=='中文说明' else set()
        if sn=='配置清单':
            allowed={(r,c) for r,row in enumerate(old) if len(row)>1 and row[1] in PRE['files'][:2] for c in (3,4,6)}
        ok=True
        for r in range(max(len(old),len(current))):
            for c in range(max(len(old[r]) if r<len(old) else 0,len(current[r]) if r<len(current) else 0)):
                if (r,c) not in allowed and cell(old,r,c)!=cell(current,r,c):ok=False
        check(f'原说明/清单/历史页保留:{f}/{sn}',ok)
        if sn=='中文说明':
            check(f'说明数据行数:{f}',current[6][1]==(480 if f=='SpecialEquipment.xlsx' else 939))
audit=books['00_配置清单.xlsx']['CHG024具名技能']
check('清单22条绑定逐条一致',audit[3:25]==[[r['equipmentId'],r['name'],r['grade'],r['part'].replace('SEPart_',''),r['skillName'],r['skillId'],'FixEffect',r['sourceRow']] for r in PRE['bindings']])
for f in PRE['files']:
    check(f'工作表集合:{f}',set(books[f])==set(PRE['before'][f])|({'CHG024具名技能'} if f=='00_配置清单.xlsx' else set()))
    values=snap(TARGET/f,True)
    errors=[v for rs in values.values() for r in rs for v in r if isinstance(v,str) and v.startswith(('#REF!','#DIV/0!','#VALUE!','#NAME?','#N/A','#NUM!'))]
    check(f'公式缓存无错误:{f}',not errors,errors)
for p,h in PRE['formalHashes'].items():check(f'正式/附件不变:{p}',sha(Path(p))==h)
for f,h in PRE['candidateHashes'].items():
    if f not in PRE['files']:check(f'未涉及06不变:{f}',sha(OUT/f)==h)

sys.path.insert(0,str(HERE.parent))
from mapping_named_rules import add_named_effects, named_effect_id
cols={v:i for i,v in enumerate(effects[0]) if v}
generated=copy.deepcopy(old_effects[4:])
add_named_effects(generated,cols)
check('纯数据生成器21条结果一致',generated==effects[4:])
add_named_effects(generated,cols)
check('具名Effect重放幂等',generated==effects[4:])
for r in eq[4:]:check(f'生成规则名称绑定:{r[1]}',named_effect_id(r[5],r[2])==r[11])
bad=copy.deepcopy(generated);bad[-1][7]=0
try:
    add_named_effects(bad,cols)
    collision=False
except ValueError:
    collision=True
check('已有Id冲突拒绝',collision)

failed=[c for c in checks if not c['pass']]
result={'status':'FAIL' if failed else 'PASS','target':str(TARGET),'checks':len(checks),'pass':len(checks)-len(failed),'fail':len(failed),
        'equipmentBindings':22,'uniqueSkills':21,'nameUpdates':10,'hashes':{f:sha(TARGET/f) for f in PRE['files']},'details':checks}
report=FRAMEWORK/'05_验算核算'/('mapping-named-CHG024-validation.json' if '--final' in sys.argv else 'mapping-named-CHG024-staged-validation.json')
report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='details'},ensure_ascii=False))
if failed:
    print(json.dumps(failed,ensure_ascii=False))
    raise SystemExit(1)
