"""Independent CHG-025 business matrix and full-cell preservation checks; read-only."""
import copy
import hashlib
import json
import sys
from pathlib import Path
import openpyxl

HERE=Path(__file__).resolve().parent;FRAMEWORK=HERE.parent.parent
OUT=FRAMEWORK/'06_最终配置/映射装备'
TARGET=OUT if '--final' in sys.argv else HERE/'staged'
PRE=json.loads((HERE/'preflight.json').read_text(encoding='utf-8'))
ALIASES={'千湖守望之剑':'祝福之剑','神圣禁言吊坠':'神圣祷言','千湖指挥官项链':'千湖指挥官吊坠'}
checks=[]
def check(n,ok,detail=None):checks.append({'name':n,'pass':bool(ok),'detail':detail})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snap(p,data_only=False):
 w=openpyxl.load_workbook(p,read_only=True,data_only=data_only);d={}
 for s in w:
  s.reset_dimensions();d[s.title]=[list(r) for r in s.iter_rows(values_only=True)]
 w.close();return d
def cell(rs,r,c):return rs[r][c] if r<len(rs) and c<len(rs[r]) else None

books={f:snap(TARGET/f) for f in PRE['files']}
eq=books['SpecialEquipment.xlsx']['SpecialEquipment'];old=PRE['before']['SpecialEquipment.xlsx']['SpecialEquipment']
ids=set(PRE['skills'].values());matrix={};binding={}
check('Schema和480条装备',eq[:4]==old[:4] and len(eq)==484)
for n,r in enumerate(eq[4:],4):
 q,g=r[5],r[3];expected=list(old[n]);name=ALIASES.get(r[2],r[2])
 rare=6000+(1 if g<=20 else 2 if g<=40 else 3)+(3 if q=='Red' else 0) if q in ('Orange','Red') else None
 special=PRE['skills'].get(name) if q=='Red' else None
 expected[9]=rare;expected[10]=special;expected[11]=None
 check(f'装备完整行:{r[1]}',r==expected)
 if special is not None:binding[r[1]]=special
 matrix.setdefault(q,[0,0,0,0]);matrix[q][0]+=1
 for c in range(9,12):matrix[q][c-8]+=int(r[c] is not None)
expected_matrix={'Green':[96,0,0,0],'Blue':[96,0,0,0],'Purple':[96,0,0,0],'Orange':[96,96,0,0],'Red':[96,96,22,0]}
for q in expected_matrix:check(f'品质准入矩阵:{q}',matrix[q]==expected_matrix[q],matrix[q])
check('所有480件FixEffect为空',all(r[11] is None for r in eq[4:]))
check('两件手套与三组别名',all(binding.get(i)==s for i,s in {80451:30602,80455:30602,80396:30101,80407:30202,80408:30201}.items()))
check('虚空无特殊效果',80393 not in binding)
check('22件红装覆盖21技能',len(binding)==22 and set(binding.values())==ids)

pools=books['SpecialEquipmentEffectDrop.xlsx']['SpecialEquipment'];oldp=PRE['before']['SpecialEquipmentEffectDrop.xlsx']['SpecialEquipment']
pd={r[1]:r[2] for r in pools[4:]}
effects=books['SpecialEquipmentEffect.xlsx']['SpecialEquipment'];ed={r[1]:r for r in effects[4:]}
check('原259池逐格不变',pools[:len(oldp)]==oldp)
check('280池且Id唯一',len(pools)==284 and len(pd)==280)
check('新增21池Id无多余',set(pd)-{r[1] for r in oldp[4:]}==ids)
check('939条Effect业务与Schema不变',effects==PRE['before']['SpecialEquipmentEffect.xlsx']['SpecialEquipment'])
for i in sorted(ids):
 check(f'单技能池:{i}',pd.get(i)==f'{i},100')
 check(f'Effect到Skill:{i}',i in ed and ed[i][7]==i)
for eid,sid in binding.items():check(f'装备到池到效果到技能:{eid}',pd.get(sid)==f'{sid},100' and ed[sid][7]==sid)
for suffix in range(1,7):check(f'稀有池完整:{suffix}',pd.get(6000+suffix)==';'.join(f'{c*100+suffix},100' for c in range(311,323)))

for f,before in PRE['before'].items():
 for sn,oldrows in before.items():
  if sn=='SpecialEquipment':continue
  current=books[f][sn];allowed=set()
  if sn=='中文说明':allowed={(r,1) for r in (2,3,6,8)}
  elif sn=='配置清单':allowed={(r,c) for r,row in enumerate(oldrows) if len(row)>1 and row[1] in PRE['files'][:3] for c in (3,4,6)}
  elif sn=='CHG024具名技能':allowed={(0,0),(2,5),(26,0),(30,0)}|{(r,6) for r in range(3,25)}
  elif sn=='CHG023稀有词条':allowed={(26,0)}
  diffs=[]
  for r in range(max(len(current),len(oldrows))):
   for c in range(max(len(current[r]) if r<len(current) else 0,len(oldrows[r]) if r<len(oldrows) else 0)):
    if (r,c) not in allowed and cell(current,r,c)!=cell(oldrows,r,c):diffs.append((r,c))
  check(f'未授权说明/历史页单元格不变:{f}/{sn}',not diffs,diffs)
  if sn=='中文说明':check(f'现行说明不再宣称FixEffect绑定:{f}','CHG-025' in current[8][1] and '当前939条；只用于红装FixEffect' not in current[8][1])
 counts={'SpecialEquipment.xlsx':480,'SpecialEquipmentEffectDrop.xlsx':280,'SpecialEquipmentEffect.xlsx':939}
 if f in counts:check(f'说明行数:{f}',books[f]['中文说明'][6][1]==counts[f])
 expected_sheets=set(before)|({'CHG025品质准入'} if f=='00_配置清单.xlsx' else set())
 check(f'页签完整:{f}',set(books[f])==expected_sheets)
 cached=snap(TARGET/f,True)
 errors=[v for rs in cached.values() for r in rs for v in r if isinstance(v,str) and v.startswith(('#REF!','#VALUE!','#DIV/0!','#NAME?','#NUM!','#N/A'))]
 check(f'公式缓存无错:{f}',not errors,errors)
a=books['00_配置清单.xlsx']['CHG025品质准入']
check('清单品质矩阵与真实数据一致',a[3:8]==[[label,*expected_matrix[q]] for label,q in [('绿','Green'),('蓝','Blue'),('紫','Purple'),('金','Orange'),('红','Red')]])
named=books['00_配置清单.xlsx']['CHG024具名技能']
check('具名清单22件SpecialEffect',all(r[6]=='SpecialEffect' and binding.get(r[0])==r[5] for r in named[3:25]))
for f,h in PRE['candidateHashes'].items():
 if f not in PRE['files']:check(f'其他候选未改:{f}',sha(OUT/f)==h)
for p,h in PRE['formalHashes'].items():check(f'正式/附件未改:{p}',sha(Path(p))==h)

sys.path.insert(0,str(HERE.parent))
from mapping_named_rules import add_named_pools,named_effect_id
from mapping_rare_rules import rare_pool_id
test=copy.deepcopy(oldp[4:]);cols={'Id':1,'EffectList':2}
add_named_pools(test,cols);check('纯数据生成池一致',test==pools[4:]);add_named_pools(test,cols);check('池生成幂等',test==pools[4:])
test[-1][2]='wrong'
try:add_named_pools(test,cols);rejected=False
except ValueError:rejected=True
check('池ID冲突拒绝',rejected)
for r in eq[4:]:check(f'生成函数品质映射:{r[1]}',rare_pool_id(r[5],r[3])==r[9] and named_effect_id(r[5],r[2])==r[10])
failed=[c for c in checks if not c['pass']]
result={'status':'FAIL' if failed else 'PASS','target':str(TARGET),'checks':len(checks),'pass':len(checks)-len(failed),'fail':len(failed),'matrix':matrix,'hashes':{f:sha(TARGET/f) for f in PRE['files']},'details':checks}
report=FRAMEWORK/'05_验算核算'/('mapping-special-CHG025-validation.json' if '--final' in sys.argv else 'mapping-special-CHG025-staged-validation.json')
report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('details','hashes')},ensure_ascii=False))
if failed:print(json.dumps(failed,ensure_ascii=False));raise SystemExit(1)
