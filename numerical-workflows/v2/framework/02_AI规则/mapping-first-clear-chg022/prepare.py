"""Read-only extraction for CHG-022. XLSX authoring belongs to update.mjs."""
import hashlib,json
from pathlib import Path
from openpyxl import load_workbook
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
OUT=ROOT/'06_最终配置/映射装备'
FORMAL=Path('D:/Vgame/Config/GameConfig/Datas')
FILES=['Drop_dungeon.xlsx','Items.xlsx','SpecialEquipmentGenerate.xlsx','UIlevel.xlsx','00_配置清单.xlsx']
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p,sheet=None):
 w=load_workbook(p,read_only=True,data_only=False);s=w[sheet] if sheet else w.worksheets[0]
 name=s.title;rows=[list(r) for r in s.values];w.close()
 header=rows[0] if rows[0][0]=='##var' else rows[3]
 index={str(v).split('\n')[-1]:i for i,v in enumerate(header) if v}
 return name,rows,index

patches=[]
for f,key,value,field,new in [
 ('Drop_dungeon.xlsx','DropId',20000012,'DropItem_id',4375),
 ('Items.xlsx','Id',4375,'Description','开启后固定获得1件10级金色映射装备。'),
 ('Items.xlsx','Id',4375,'##','第三层首通专用实际宝箱；蓝色外观，固定开出1件10级金装'),
 ('Items.xlsx','Id',4375,'Status','CHG-022_ACTUAL_FIRST_CLEAR_BOX')]:
 sheet,rs,h=read(OUT/f)
 matches=[i for i,r in enumerate(rs[4:],4) if r[h[key]]==value and (key!='DropId' or r[h['DropItem_id']]==4212)]
 assert len(matches)==1,(f,matches)
 i=matches[0];assert not str(rs[i][h[field]]).startswith('=')
 patches.append(dict(file=f,sheet=sheet,row=i,col=h[field],old=rs[i][h[field]],new=new))
 if key=='DropId':
  c=h['##备注'];patches.append(dict(file=f,sheet=sheet,row=i,col=c,old=rs[i][c],new='首通专用蓝箱（固定10级金装）'))

sheet,gr,gh=read(OUT/'SpecialEquipmentGenerate.xlsx')
assert all(r[gh['Id']]!=4375 for r in gr[4:])
_,fr,fh=read(FORMAL/'SpecialEquipment/SpecialEquipmentGenerate.xlsx')
special=next(r for r in fr[4:] if r[fh['Id']]==4375)
assert special[fh['GradeList']]=='10,1000' and special[fh['QualityList']]=='Orange,1000'
assert special[fh['GenerateMax']]==special[fh['GenerateMin']]==1
newrow=[None]*len(gr[0])
for field,c in gh.items():
 if field!='##var' and field in fh:newrow[c]=special[fh[field]]
newrow[2]='第3层首通专用蓝箱（固定10级金装）'
source=dict(revision='CHG-022',files=FILES,patches=patches,newGenerate=dict(sheet=sheet,row=len(gr),values=newrow),
 candidateHashes={p.name:SHA(p) for p in OUT.glob('*.xlsx') if not p.name.startswith('~$')},
 formalHashes={str(FORMAL/p):SHA(FORMAL/p) for p in ['Drop/Drop_dungeon.xlsx','items/Items.xlsx','SpecialEquipment/SpecialEquipmentGenerate.xlsx','level/UIlevel.xlsx','level/EquipmentLevel.xlsx']},
 mdHash=SHA(ROOT/'03_沉淀MD/经济/05_玩法_映射副本经济沉淀-2026-07-08.md'))
(HERE/'source.json').write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'patches':len(patches),'newGenerateRow':len(gr)+1,'files':len(FILES)}))
