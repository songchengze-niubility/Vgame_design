"""Sync only the chapter Markdown body from user-confirmed 06 workbooks.

All Excel files are read-only.  Historical text is archived outside the active
deposit directory; rendered Markdown tables are independently re-read below.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[2]
FINAL=ROOT/'06_最终配置'
MD=ROOT/'03_沉淀MD/经济/11_外循环_任务_04_章节任务经济沉淀-2026-07-09.md'
RUN=ROOT/'05_验算核算/章节任务MD同步_20260827'
ARCHIVE=RUN/'章节任务经济沉淀_旧正文_2026-08-27.md'
NAMES={1:'金币',2:'元晶',25:'映射之匙',34:'指南笔记I',35:'指南笔记II',101:'中阶记录盘',102:'高阶记录盘',103:'熔晶',106:'旅券',107:'收容凭证',110:'未知笔记',111:'限时旅券',1074:'房车零件',2505:'5级蓝色映射装备箱',2506:'10级蓝色映射装备箱',2507:'15级紫色映射装备箱',2508:'20级紫色映射装备箱',2509:'25级金色映射装备箱',2510:'30级金色映射装备箱',3011:'2级随机宝石箱',3012:'3级随机宝石箱',3013:'4级随机宝石箱',3015:'普通能效材料自选箱',3016:'稀有能效材料自选箱',3017:'史诗能效材料自选箱',3018:'传说能效材料自选箱',3027:'房车天赋树材料自选箱',3028:'低级房车建材',3029:'中级房车建材'}
CATEGORY={'Target_TTT_RoleLevel':'玩家等级','Target_TTT_HeroLevel':'角色等级','Target_TTT_UseEnegyPoint_SomeRole':'能效点','Target_TTT_Rv_Level':'房车等级','Target_TTT_RvCabin_LevelUp_Num':'舱室','Target_TTT_SpecialEquipmentLevelUp_Num':'映射装备','Target_TTT_RvGuide_ProfessionNodeActivateNum':'职业指南','Target_TTT_EquipmentLevelUp_Num':'收容物','Target_TTT_SpecialEquipmentGem_EquipNum':'宝石','Target_TTT_SpecialEquipmentGem_NumAtLevel':'宝石','Target_TTT_StrategyCard_CraftTimes':'邮票合成'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    w=load_workbook(p,read_only=True,data_only=True)
    out=list(w.worksheets[0].values);w.close();return out
def records(p):return {r[1]:r for r in rows(p)[4:] if len(r)>1 and isinstance(r[1],int) and r[0]!='##'}
def rewards_text(items):return '；'.join(f'{NAMES[k]}({k})×{v}' for k,v in items)
def table(headers,items):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']+['| '+' | '.join(str(x) for x in r)+' |' for r in items])

def source():
    p=FINAL/'任务'
    tasks=records(p/'Task.xlsx');targets=records(p/'TaskTarget.xlsx');groups=records(p/'JottingsTask.xlsx');chapters=records(p/'Jottings.xlsx')
    drops={}
    for r in rows(p/'Drop_other.xlsx')[4:]:
        if len(r)>12 and isinstance(r[2],int) and r[0]!='##':drops.setdefault(r[2],[]).append(r)
    def reward(did):
        result=[]
        for r in drops[did]:
            assert r[5]==0 and r[6]=='fixed_' and r[7:9]==(1,1) and r[11]==r[12]
            assert r[10] in NAMES
            result.append((r[10],r[11]))
        return result
    all_tasks=[];all_chapters=[]
    for cid,c in chapters.items():
        gs=list(map(int,str(c[3]).split(';')));cts=[]
        for gid in gs:
            for tid in map(int,str(groups[gid][2]).split(';')):
                t=tasks[tid];target=targets[t[7]]
                assert t[2]==t[3]==target[2]
                item={'chapter':cid,'group':gid,'task':tid,'target':t[7],'type':target[3],'param':target[4],'desc':t[2],'drop':t[14],'rewards':reward(t[14])}
                cts.append(item);all_tasks.append(item)
        all_chapters.append({'id':cid,'groups':gs,'tasks':cts,'drop':c[4],'rewards':reward(c[4])})
    assert [len(c['groups']) for c in all_chapters]==[5,6,7,8,10,10,10]
    assert len(all_tasks)==len({t['task'] for t in all_tasks})==69
    single=Counter();complete=Counter()
    for t in all_tasks:
        for k,n in t['rewards']:single[k]+=n
    for c in all_chapters:
        for k,n in c['rewards']:complete[k]+=n
    assert single[25]==18 and single[2]==600 and complete[106]==21 and complete[111]==21 and complete[2]==0
    return all_chapters,all_tasks,single,complete

def make_md(chapters,tasks,single,complete,history):
    sections=['# 11-4_外循环_章节任务经济沉淀',
      '初始生成：2026-07-09。正文更新：2026-08-27。当前版本：`CHG-007`。',
      '> 用户已明确确认“06当前配置是对的”。本篇以 `06_最终配置/任务` 当前挂载配置为数值依据，直接同步任务目标、奖励、明细和统计；不再用旧正文覆盖06。本次只更新文档，不改06、SVN或生成配置，不代表运行版本已经发布。',
      '## 结论摘要',
      '1. 第一至第七章共7个阶段，各章5/6/7/8/10/10/10组目标，合计56组；主线分步展开后69条任务，均从Jottings实际挂载链统计。\n2. 主线进度共20个分步，每步元晶(2)×30，合计600；其余单项奖励按下表配置，并非全部发元晶。\n3. 第二至第七章各1条映射装备任务，每条映射之匙(25)×3，无副材、无子掉落，合计18把一次性奖励。\n4. 第一至五章舱室任务依次为1个Lv2、2个Lv2、1个Lv3、2个Lv3、1个Lv4；前两章分别奖励低级房车建材(3028)×2、×3。\n5. 七章完成奖各有旅券(106)×3、限时旅券(111)×3，两种券各合计21；章节完成奖不发元晶，每章不超过6种奖励。\n6. 未挂载旧任务和旧ChapterTasks链不计入上述数量及产出；所有奖励均为一次性，不并入日周常驻产出。',
      '## 当前设计规则',
      '- 序章不设置当前章节任务；每章同一养成类型只保留一个目标，按任务组计最多10组。主线组内的分步分别计入Task条数。\n- 主线目标按JottingsTask.TaskID列表顺序承接；第一章为1-4/1-8，第二章为2-4/2-8/2-12，第三至七章为各章5/10/15节点。\n- 玩家等级目标依次10/20/25/30/33/36/38；角色等级、能效点、房车、收容物、职业指南、宝石和邮票目标见七章任务总表。\n- 舱室从第一章开始承接；房车等级任务从第三章开始。舱室参数为“等级,数量”，目标类型为Target_TTT_RvCabin_LevelUp_Num。\n- 映射装备使用“收集X件Y级的映射装备”，从第二章开始，参数为“等级,数量”；暂复用Target_TTT_SpecialEquipmentLevelUp_Num，持有量统计仍需运行验证。\n- 本次不调整日周任务的UnlockId、玩法入口、装备箱显示名或开箱规则；不得以文档同步为由顺带改配置。',
      '## 七章任务总表']
    overview=[]
    for c in chapters:
        groups=[]
        for gid in c['groups']:
            gt=[t for t in c['tasks'] if t['group']==gid]
            groups.append(' → '.join(t['desc'] for t in gt))
        overview.append([f"第{c['id']}章",len(c['groups']),len(c['tasks']),'；'.join(groups)])
    sections.append(table(['章节','任务组数','Task条数','任务目标（主线组内按顺序）'],overview))
    sections.append('## 单项任务奖励')
    cats=['玩家等级','角色等级','能效点','房车等级','舱室','映射装备','职业指南','收容物','宝石','邮票合成']
    matrix=[]
    for c in chapters:
        cells={}
        for t in c['tasks']:
            if t['type']=='Target_TTT_pass_Level':continue
            cat=CATEGORY[t['type']];assert cat not in cells
            cells[cat]=rewards_text(t['rewards'])
        matrix.append([f"第{c['id']}章"]+[cells.get(cat,'—') for cat in cats])
    sections.append(table(['章节']+cats,matrix))
    sections.append('主线进度分步均为元晶(2)×30，未在上表重复列出。映射任务只发25×3；所有当前任务奖励均无子掉落。')
    sections.append('## 章节完成奖励')
    sections.append('所有章节固定投放旅券(106)×3、限时旅券(111)×3；下表仅列额外奖励。装备箱按开箱产物等级/品质描述，ItemId用于关联配置。')
    sections.append(table(['章节','Jottings.DropID','额外奖励'],[[f"第{c['id']}章",c['drop'],rewards_text([(k,n) for k,n in c['rewards'] if k not in {106,111}])] for c in chapters]))
    sections.append('## 挂载与目标明细')
    sections.append('来源链：`Jottings.JottingsTasks → JottingsTask.TaskID → Task.TaskTarget / DropId → TaskTarget / Drop_other`。这里列出全部69条已挂载任务；TargetType/ParamList保持原配置值，未推测或改写计数语义。')
    sections.append(table(['章节','组ID','TaskId','TargetId','任务目标','TargetType','ParamList','DropId','奖励'],[[t['chapter'],t['group'],t['task'],t['target'],t['desc'],t['type'],t['param'],t['drop'],rewards_text(t['rewards'])] for t in tasks]))
    sections.append('## 一次性产出汇总')
    sections.append('只统计当前挂载任务直接发放的物品，不把装备箱或材料自选箱的内容重复展开计入。单项列按Task逐条求和；章节列按Jottings每章完成奖各计一次。')
    sections.append(table(['ItemId','资源','单项任务','章节完成','合计'],[[k,NAMES[k],single[k],complete[k],single[k]+complete[k]] for k in sorted(single.keys()|complete.keys())]))
    sections.append('## 来源、范围与验收')
    sections.append(table(['来源','用途'],[
      ['用户2026-08-27确认','06当前配置正确；本次仅更新沉淀MD正文'],
      ['06_最终配置/任务/Jottings.xlsx','7章挂载与章节完成DropID'],
      ['06_最终配置/任务/JottingsTask.xlsx','56个任务组及顺序任务列表'],
      ['06_最终配置/任务/Task.xlsx','69条已挂载任务名称、TargetId与奖励DropId'],
      ['06_最终配置/任务/TaskTarget.xlsx','目标类型、参数与任务描述'],
      ['06_最终配置/任务/Drop_other.xlsx','单项及章节完成奖励的实际物品与数量'],
      ['05_验算核算/章节任务MD同步_20260827/validation.json','MD表格逐项复读、产出汇总及配置哈希保护']]))
    sections.append('- 这里只对06候选的任务数值与MD做一致性验收；不把候选镜像、配置存在或过去的Luban记录当作当前运行生效证明。\n- 装备箱2505～2510的开箱依赖为4621～4626；正式源表中已有对应固定等级/品质规则。06按分模块候选交付，合表时沿用正式依赖；本次不改箱子或补建配置。\n- 映射装备目标按当前持有量统计、旧存量初始化、奖励领取与章节推进属于运行验收事项；本次文档更新不宣称这些行为已经联调通过。\n- 旧ChapterTasks及未挂载序章不属于本篇当前产出。其旧缺源记录仅作历史追溯，不在正文重复陈列为当前结论。')
    sections.append('## 历史归档与变更记录')
    sections.append('旧正文及旧配置明细已移出当前正文，保存于[正文更新前归档](../../05_验算核算/章节任务MD同步_20260827/章节任务经济沉淀_旧正文_2026-08-27.md)。归档中的旧阶段数、旧任务目标和旧奖励不再用于当前配表。')
    sections.append('- 2026-08-27 `[CHG-007]`：用户明确确认06当前配置正确。将确认口径同步到本篇全部正文：总表、单项奖励、章节完成奖、69条目标明细、一次性统计与来源边界；只改文档，06和SVN保持不变。此前只补顶部说明的做法作废。\n- 2026-08-27 `[CHG-006]`：汇总8月26日的前两章舱室、玩家等级、第二章映射任务与每条3把钥匙口径，纠正清单为56组/69条；本次将这些内容并入正式正文。\n- CHG-001～CHG-005及更早旧链路记录保存在上述归档，不作为当前数值规则。')
    return '\n\n'.join(sections)+'\n'

def sync():
    assert not (RUN/'baseline.json').exists(), 'Refuse to overwrite audit baseline'
    RUN.mkdir(parents=True,exist_ok=True)
    old=MD.read_text(encoding='utf-8')
    formal=Path('D:/Vgame/Config/GameConfig/Datas')
    protected={str(p):sha(p) for p in FINAL.rglob('*.xlsx')}
    for rel in ['task/Task.xlsx','task/TaskTarget.xlsx','task/Jottings.xlsx','task/JottingsTask.xlsx','Drop/Drop_other.xlsx','items/Items.xlsx','SpecialEquipment/SpecialEquipmentGenerate.xlsx']:
        p=formal/rel;protected[str(p)]=sha(p)
    baseline={'md_before_sha256':sha(MD),'protected_config_hashes':protected,'archive':str(ARCHIVE),'authority':'用户确认06当前配置正确；只更新文档正文','batch':'CHAPTER-MD-CHG007-20260827'}
    (RUN/'baseline.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf-8')
    ARCHIVE.write_text('# 历史归档：章节任务正文更新前\n\n> 本文件仅用于追溯，不代表当前数值；当前正文以用户确认的06配置为准。以下保留更新前全文。\n\n'+old,encoding='utf-8')
    chapters,tasks,single,complete=source()
    MD.write_text(make_md(chapters,tasks,single,complete,old),encoding='utf-8')
    validate()

def parse_table(text,section):
    body=text.split('## '+section+'\n',1)[1].split('\n## ',1)[0]
    lines=[l for l in body.splitlines() if l.startswith('|')]
    return [[x.strip() for x in line.strip('|').split('|')] for line in lines[2:]]

def validate():
    baseline=json.loads((RUN/'baseline.json').read_text(encoding='utf-8'))
    text=MD.read_text(encoding='utf-8')
    chapters,tasks,single,complete=source()
    detail=parse_table(text,'挂载与目标明细');assert len(detail)==69
    for actual,t in zip(detail,tasks):
        expected=list(map(str,[t['chapter'],t['group'],t['task'],t['target'],t['desc'],t['type'],t['param'],t['drop'],rewards_text(t['rewards'])]))
        assert actual==expected,(actual,expected)
    overview=parse_table(text,'七章任务总表');assert len(overview)==7
    for r,c in zip(overview,chapters):
        assert int(r[1])==len(c['groups']) and int(r[2])==len(c['tasks'])
        for t in c['tasks']:assert t['desc'] in r[3]
    reward_matrix=parse_table(text,'单项任务奖励')
    cats=['玩家等级','角色等级','能效点','房车等级','舱室','映射装备','职业指南','收容物','宝石','邮票合成']
    for r,c in zip(reward_matrix,chapters):
        bycat={CATEGORY[t['type']]:rewards_text(t['rewards']) for t in c['tasks'] if t['type']!='Target_TTT_pass_Level'}
        assert r==[f"第{c['id']}章"]+[bycat.get(cat,'—') for cat in cats]
    for r,c in zip(parse_table(text,'章节完成奖励'),chapters):
        assert r==[f"第{c['id']}章",str(c['drop']),rewards_text([(k,n) for k,n in c['rewards'] if k not in {106,111}])]
        assert dict(c['rewards'])[106]==dict(c['rewards'])[111]==3
    totals=parse_table(text,'一次性产出汇总')
    assert len(totals)==len(single.keys()|complete.keys())
    for r in totals:
        item=int(r[0]);assert list(map(int,r[2:]))==[single[item],complete[item],single[item]+complete[item]]
    for bad in ['共 4 个阶段','关联 30 个 Task','副材(1152~1155)','1个舱室2级','玩家35级','玩家40级','当前正式章节任务明细']:
        assert bad not in text,bad
    for p,h in baseline['protected_config_hashes'].items():assert sha(Path(p))==h,p
    output={'batch':baseline['batch'],'status':'PASS_MD_MATCHES_CONFIRMED_06','task_count':69,'group_count':56,'chapter_count':7,'mainline_steps':20,'single_task_yuanjing':single[2],'single_task_keys':single[25],'completion_coupons':{106:complete[106],111:complete[111]},'md_sha256':sha(MD),'protected_configs_unchanged':len(baseline['protected_config_hashes']),'single_rewards':dict(single),'completion_rewards':dict(complete),'tables_verified':['七章任务总表','单项任务奖励','章节完成奖励','挂载与目标明细','一次性产出汇总'],'runtime_verified':False}
    (RUN/'validation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(output,ensure_ascii=False))

if __name__=='__main__':
    if sys.argv[1]=='sync':sync()
    elif sys.argv[1]=='validate':validate()
    else:raise ValueError(sys.argv[1])
