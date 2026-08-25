# -*- coding: utf-8 -*-
"""
gen_growth_budget.py — 养成战力预算链 生成器 (框架重搭 P1)

读取 `03_沉淀MD/参数基线` →
  1) 生成「模块属性分配表」(投放 = 标准人 × 投放系数)
  2) 生成「角色升级曲线」(单级属性系数 = 1 + 等级×单级成长)
  3) 写出生成表 (养成/生成_养成战力预算.xlsx)
  4) 与现有 Vgame养成数值.xlsx 逐格对照，输出复现一致性报告 (parity)

只读现有源表，绝不修改它们。生成表是独立新文件。

用法:
    python gen_growth_budget.py            # 生成 + 对照
    python gen_growth_budget.py --check    # 只对照，不写生成表
"""
import sys, io, os, argparse
import warnings
warnings.filterwarnings('ignore')
import openpyxl
from openpyxl.styles import Font, PatternFill

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
GROWTH_DIR = os.path.dirname(HERE)  # 养成/
V2_DIR = os.path.dirname(GROWTH_DIR)  # 框架v2/
NUM_DIR = os.path.dirname(V2_DIR)  # 数值文档/数值文档/
sys.path.insert(0, V2_DIR)
from _shared.md_parameter_reader import load_parameter_workbook, parameter_md_path

SHARED_PARAM = parameter_md_path('共享')
GROWTH_PARAM = parameter_md_path('养成')
OUT_OVERVIEW = os.path.join(GROWTH_DIR, '生成_养成总览.xlsx')
OUT_LEVELUP  = os.path.join(GROWTH_DIR, '生成_角色升级.xlsx')
REPORT  = os.path.join(GROWTH_DIR, '_reports', 'P1_养成战力预算_复现对照.md')
SRC     = os.path.join(NUM_DIR, 'Vgame养成数值.xlsx')

def almost(a, b, tol=1e-6):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return a == b

# ---------- 读参数 ----------
def read_params():
    # 标准人、投放系数 → 从共享参数 MD 读
    wb_s = load_parameter_workbook(SHARED_PARAM, data_only=True)
    sp = wb_s['标准人']
    std = {sp.cell(r,1).value: sp.cell(r,2).value for r in range(2,5)}  # 生命/攻击/防御
    fp = wb_s['投放系数']
    coefs = []  # (模块, 系数 or None, 类型)
    for r in range(2, fp.max_row+1):
        name = fp.cell(r,1).value
        if not name: continue
        coefs.append((name, fp.cell(r,2).value, fp.cell(r,3).value, fp.cell(r,5).value))
    wb_s.close()

    # 升级曲线参数 → 从养成参数 MD 读
    wb_g = load_parameter_workbook(GROWTH_PARAM, data_only=True)
    cp = wb_g['升级曲线参数']
    curve = {cp.cell(r,1).value: cp.cell(r,2).value for r in range(2, cp.max_row+1) if cp.cell(r,1).value}
    wb_g.close()
    return std, curve, coefs

# ---------- 计算 ----------
def compute(std, curve, coefs):
    hp, atk, dfs = std['生命'], std['攻击'], std['防御']
    lvcap = int(curve['等级上限']); grow = float(curve['单级成长'])
    lvl_coef = lvcap * grow  # 升级派生系数

    # 模块分配
    alloc = []  # (模块, 系数, 生命, 攻击, 防御, 类型)
    for (name, coef, typ, classify) in coefs:
        kind = classify or '基础'
        if typ == '派生' and '升级' in name:
            c = lvl_coef
            alloc.append((name, c, round(hp*c), round(atk*c), round(dfs*c), kind))
        elif typ == '锚':
            c = float(coef)
            alloc.append((name, c, round(hp*c), round(atk*c), round(dfs*c), kind))
        elif typ and typ.startswith('旋钮(%)'):
            alloc.append((name, coef, None, None, None, classify or '百分比'))
        elif typ == '旋钮':
            c = float(coef)
            alloc.append((name, c, round(hp*c), round(atk*c), round(dfs*c), kind))
    # 升级曲线 (SSR=品阶系数1.0 基准)。攻击已统一，不再拆物理/魔法两列。
    rows = []
    for L in range(1, lvcap+1):
        sc = 1 + L*grow
        rows.append((L, round(grow,4), round(sc,4), round(hp*sc), round(atk*sc), round(dfs*sc)))
    return lvl_coef, alloc, rows

# ---------- 写生成表 ----------
def write_out(std, lvl_coef, alloc, rows):
    bold=Font(bold=True); hf=PatternFill('solid',fgColor='D9E1F2')

    # === 生成_养成总览.xlsx ===
    wb1 = openpyxl.Workbook()
    ws=wb1.active; ws.title='投放预算分配'
    ws.append(['【自动生成 · 勿手改】源: 03_沉淀MD/参数基线/共享参数基线.md + 养成参数基线.md'])
    ws.append([f'标准人 生命{std["生命"]}/攻击{std["攻击"]}/防御{std["防御"]}  升级派生系数={lvl_coef}'])
    ws.append([])
    ws.append(['养成模块','投放系数','生命','攻击','防御','类型'])
    for c in range(1,7): ws.cell(4,c).font=bold; ws.cell(4,c).fill=hf
    for (name,coef,h,a,d,typ) in alloc:
        ws.append([name, coef, h, a, d, typ])
    for w,col in zip([12,12,12,12,12,10],'ABCDEF'): ws.column_dimensions[col].width=w

    # === 养成汇总: 标准人各模块属性总计 ===
    ws_sum = wb1.create_sheet('养成属性汇总')
    ws_sum.append(['养成属性汇总 -- 标准人(SSR基准)各模块满级属性'])
    ws_sum.append(['最终属性 = 裸体 × (1 + 升星%) × (1 + 二级%) + 额外'])
    ws_sum.append([])

    # 从共享参数读属性分类
    wb_shared = load_parameter_workbook(SHARED_PARAM, data_only=True)
    ws_coef = wb_shared['投放系数']
    mod_classify = {}  # 模块名 -> (系数, 类型, 属性分类)
    for r in range(2, ws_coef.max_row+1):
        name = ws_coef.cell(r, 1).value
        coef_val = ws_coef.cell(r, 2).value
        typ = ws_coef.cell(r, 3).value
        classify = ws_coef.cell(r, 5).value
        if name:
            mod_classify[name] = (coef_val, typ, classify)
    wb_shared.close()

    # 构造各模块数据
    all_modules = []
    for name, (coef_val, typ, classify) in mod_classify.items():
        if typ == '派生':
            coef_num = lvl_coef
        elif coef_val and isinstance(coef_val, (int, float)):
            coef_num = float(coef_val)
        else:
            coef_num = 0
        hp = coef_num * std['生命']
        atk = coef_num * std['攻击']
        df = coef_num * std['防御']
        all_modules.append((name, coef_num, hp, atk, df, classify or ''))

    # 裸体属性区
    ws_sum.append(['裸体属性（被百分比加成）'])
    ws_sum.cell(ws_sum.max_row, 1).font = bold
    ws_sum.append(['模块', '投放系数', '生命', '攻击', '防御'])
    for c in range(1,6): ws_sum.cell(ws_sum.max_row, c).font = bold; ws_sum.cell(ws_sum.max_row, c).fill = hf
    naked_hp = naked_atk = naked_def = 0
    for (name, coef, hp, atk, df, cls) in all_modules:
        if cls == '裸体':
            ws_sum.append([name, coef, round(hp,0), round(atk,0), round(df,0)])
            naked_hp += hp; naked_atk += atk; naked_def += df
    ws_sum.append(['裸体合计', '', round(naked_hp,0), round(naked_atk,0), round(naked_def,0)])
    ws_sum.cell(ws_sum.max_row, 1).font = bold

    # 额外属性区
    ws_sum.append([])
    ws_sum.append(['额外属性（不被百分比加成）'])
    ws_sum.cell(ws_sum.max_row, 1).font = bold
    ws_sum.append(['模块', '投放系数', '生命', '攻击', '防御'])
    for c in range(1,6): ws_sum.cell(ws_sum.max_row, c).font = bold; ws_sum.cell(ws_sum.max_row, c).fill = hf
    extra_hp = extra_atk = extra_def = 0
    for (name, coef, hp, atk, df, cls) in all_modules:
        if cls == '额外':
            ws_sum.append([name, coef, round(hp,0), round(atk,0), round(df,0)])
            extra_hp += hp; extra_atk += atk; extra_def += df
    ws_sum.append(['额外合计', '', round(extra_hp,0), round(extra_atk,0), round(extra_def,0)])
    ws_sum.cell(ws_sum.max_row, 1).font = bold

    # 百分比属性区
    ws_sum.append([])
    ws_sum.append(['百分比属性（各为独立乘区，乘裸体属性）'])
    ws_sum.cell(ws_sum.max_row, 1).font = bold
    hdr_row3 = ws_sum.max_row + 1
    ws_sum.append(['乘区', '生命%', '攻击%', '防御%', '说明', ''])
    for c in range(1,6): ws_sum.cell(hdr_row3, c).font = bold; ws_sum.cell(hdr_row3, c).fill = hf

    ws_sum.append(['升星乘区', 0.3, 0.3, 0.3, '星3(0.15)+星5(0.15), 独立乘区'])
    ws_sum.append(['二级属性%乘区', '—', '—', '—', '来自各模块二级中的基础属性%, 独立乘区'])
    ws_sum.append([])
    ws_sum.append(['注: 0.9是投放系数页的预算值(含天赋战力折算), 不是直接属性%'])
    ws_sum.append(['    升星显式给的属性% = 0.15×2 = 0.30'])

    # 二级属性预算区
    ws_sum.append([])
    ws_sum.append(['二级属性预算(攻击%等价, 不分裸体/额外)'])
    ws_sum.cell(ws_sum.max_row, 1).font = bold
    hdr_row4 = ws_sum.max_row + 1
    ws_sum.append(['模块', '普通二级', '稀有二级', '基础属性%', '说明'])
    for c in range(1,6): ws_sum.cell(hdr_row4, c).font = bold; ws_sum.cell(hdr_row4, c).fill = hf
    sec_data = [
        ('星盘', 1.2, 0, 0, '偏向=中外圈8属性点×0.15; 每角色选3种'),
        ('升星', 0.6, 0, 0.9, '偏向普通二级0.6; 基础属性%=0.9(含天赋折算)'),
        ('专武', 0.6, 0, 0, '突破5次投放; 总偏向0.6'),
        ('旅券', 4.2, 0, 0, '主32%+副68%分配; 主17种/副10种属性'),
        ('映射装备', 8.2, 3.2, 0, '终局最大二级投放'),
    ]
    for d in sec_data: ws_sum.append(list(d))
    ws_sum.append(['合计', sum(d[1] for d in sec_data), 3.2, 0.9, ''])
    ws_sum.cell(ws_sum.max_row, 1).font = bold

    # 最终属性预估
    ws_sum.append([])
    ws_sum.append(['最终基础属性预估(标准人满养成)'])
    ws_sum.cell(ws_sum.max_row, 1).font = bold
    hdr_row5 = ws_sum.max_row + 1
    ws_sum.append(['', '生命', '攻击', '防御', '公式'])
    for c in range(1,6): ws_sum.cell(hdr_row5, c).font = bold; ws_sum.cell(hdr_row5, c).fill = hf
    # 最终 = 裸体 × (1+升星%) × (1+二级基础属性%) + 额外
    # 二级基础属性%暂未汇总具体值，先只算升星乘区
    final_hp = naked_hp * (1 + 0.3) + extra_hp
    final_atk = naked_atk * (1 + 0.3) + extra_atk
    final_def = naked_def * (1 + 0.3) + extra_def
    ws_sum.append(['仅含升星乘区', round(final_hp,0), round(final_atk,0), round(final_def,0), '裸体×(1+0.3)+额外, 未含二级%乘区'])
    ws_sum.append(['说明', '', '', '', '二级属性%乘区(各模块给的攻击%/生命%等)需按角色具体选择计算'])

    for w,col in zip([14,12,12,12,12,34],'ABCDEF'): ws_sum.column_dimensions[col].width = w

    wb1.save(OUT_OVERVIEW)

    # === 生成_角色升级.xlsx ===
    wb2 = openpyxl.Workbook()
    ws2=wb2.active; ws2.title='升级曲线'
    ws2.append(['【自动生成 · 勿手改】单级属性系数=1+等级×单级成长 ; 属性=标准人×系数 (SSR基准)'])
    ws2.append([])
    ws2.append(['等级','单级成长','单级属性系数','生命','攻击','防御'])
    for c in range(1,7): ws2.cell(3,c).font=bold; ws2.cell(3,c).fill=hf
    for row in rows: ws2.append(list(row))
    for w,col in zip([8,10,14,10,10,10],'ABCDEF'): ws2.column_dimensions[col].width=w

    # 各角色升级属性页
    ws_h = wb2.create_sheet('各角色升级属性')
    ws_h.append(['各角色升级属性（基础+成长×等级上限）'])
    ws_h.append(['公式: 基础=标准人×职业比×统一攻击比×微调比×品质比; 成长=基础×单级成长'])
    ws_h.append([])
    h_headers = ['角色','品质','职业','伤害类型','基础生命','成长生命','基础攻击','成长攻击','基础防御','成长防御']
    ws_h.append(h_headers)
    for c in range(1, len(h_headers)+1): ws_h.cell(4,c).font=bold; ws_h.cell(4,c).fill=hf
    # 读武将系数
    wb_p2 = load_parameter_workbook(GROWTH_PARAM, data_only=True)
    ws_wj = wb_p2['武将系数']
    dmg_types = {}; heroes = []
    sec = None
    for r in range(1, ws_wj.max_row+1):
        v = ws_wj.cell(r,1).value
        if v == '伤害类型攻击分配': sec = 'dmg'; continue
        if v == '角色系数列表': sec = 'hero'; continue
        if v == '专武系数列表': break
        if sec == 'dmg' and v in ('物理','魔法','混合'):
            dmg_types[v] = (float(ws_wj.cell(r,2).value), float(ws_wj.cell(r,3).value))
        if sec == 'hero' and v and v != '武将名称':
            heroes.append([ws_wj.cell(r,c).value for c in range(1,14)])
    wb_p2.close()
    growth = lvl_coef / 60
    wb_p3 = load_parameter_workbook(GROWTH_PARAM, data_only=True)
    ws_lp = wb_p3['升级曲线参数']
    for r in range(2, ws_lp.max_row+1):
        if ws_lp.cell(r,1).value == '单级成长': growth = float(ws_lp.cell(r,2).value)
    wb_p3.close()
    for h in heroes:
        name,rarity,job,dmg = h[0],h[1],h[2],h[3]
        job_hp,job_atk,job_def = float(h[4]),float(h[5]),float(h[6])
        adj_hp,adj_pa,adj_ma,adj_df = float(h[7]),float(h[8]),float(h[9]),float(h[10])
        quality = float(h[12])
        b_hp = std['生命']*job_hp*adj_hp*quality
        # 01_源表已统一为单一攻击；伤害类型只保留表现语义，不再二次缩放攻击。
        b_atk = std['攻击']*job_atk*adj_pa*quality
        b_df = std['防御']*job_def*adj_df*quality
        ws_h.append([name,rarity,job,dmg, round(b_hp,2),round(b_hp*growth,2),
                     round(b_atk,2),round(b_atk*growth,2),
                     round(b_df,2),round(b_df*growth,2)])
    for w,col in zip([12,6,16,10,10,10,10,10,10,10],'ABCDEFGHIJ'): ws_h.column_dimensions[col].width=w

    wb2.save(OUT_LEVELUP)

# ---------- 对照现有源表 ----------
def parity(std, lvl_coef, alloc, rows):
    wb = openpyxl.load_workbook(SRC, data_only=True)
    fails=[]; checks=0

    # 1) 养成属性规划 预算块 rows 36-43, D/E/F = 生命/攻击/防御
    plan = wb['养成属性规划']
    row_map = {  # 源行 -> 生成模块名
        36:'角色初始',37:'角色升级',38:'角色升阶',39:'角色星盘',
        41:'专武',42:'旅券',43:'映射装备'}
    alloc_by_name = {a[0]:a for a in alloc}
    for srow, mod in row_map.items():
        a = alloc_by_name.get(mod)
        if not a or a[2] is None: continue
        _,_,h,at,d,_ = a
        for col, exp, label in [(4,h,'生命'),(5,at,'攻击'),(6,d,'防御')]:
            act = plan.cell(srow, col).value
            checks+=1
            if not almost(exp, act):
                fails.append(('养成属性规划 R%dC%d %s/%s'%(srow,col,mod,label), exp, act))

    # 2) 角色升级升阶 升级曲线: 数据从 row15, B=等级, E/F/H=生命/攻击(旧物攻侧)/防御
    cur = wb['角色升级升阶']
    exp_by_lvl = {r[0]: r for r in rows}
    r = 15
    matched_lvls = 0
    while r <= cur.max_row:
        lv = cur.cell(r,2).value
        if isinstance(lv,(int,float)) and int(lv)>=1 and int(lv) in exp_by_lvl:
            L=int(lv); e=exp_by_lvl[L]
            for col, exp, label in [(5,e[3],'生命'),(6,e[4],'攻击'),(8,e[5],'防御')]:
                act = cur.cell(r,col).value
                checks+=1
                if not almost(exp, act):
                    fails.append(('升级升阶 L%d R%dC%d %s'%(L,r,col,label), exp, act))
            matched_lvls+=1
        r+=1
    wb.close()
    return checks, matched_lvls, fails

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    std,curve,coefs = read_params()
    lvl_coef, alloc, rows = compute(std,curve,coefs)
    if not args.check:
        write_out(std, lvl_coef, alloc, rows)

    checks, matched_lvls, fails = parity(std, lvl_coef, alloc, rows)

    md=[]
    def o(s=''):
        print(s); md.append(s)
    o('# P1 · 养成战力预算链 复现对照报告'); o()
    o('> 生成器结果 vs 现有 Vgame养成数值.xlsx 逐格对照。源表只读未改。'); o()
    o('- 升级派生系数 = 等级上限 × 单级成长 = %s' % lvl_coef); o()
    o('## 模块分配（生成值）'); o()
    o('| 模块 | 系数 | 生命 | 攻击 | 防御 |'); o('|---|---:|---:|---:|---:|')
    for (n,c,h,a,d,t) in alloc:
        if h is None: o('| %s | %s(%%) | — | — | — |'%(n,c))
        else: o('| %s | %s | %d | %d | %d |'%(n,c,h,a,d))
    o()
    o('## 对照结果'); o()
    o('- 对照单元格数: %d' % checks)
    o('- 升级曲线对照等级数: %d' % matched_lvls)
    o('- 不一致: %d' % len(fails)); o()
    if not fails:
        o('✅ **完全复现**：生成结果与现有手搓表逐格一致。')
    else:
        o('🔴 以下不一致（前 30）：'); o()
        o('| 位置 | 生成值 | 源表值 |'); o('|---|---:|---:|')
        for (loc,exp,act) in fails[:30]:
            o('| %s | %s | %s |'%(loc,exp,act))
        if len(fails)>30: o('| … | 还有 %d 处 | |'%(len(fails)-30))
    o()
    os.makedirs(os.path.dirname(REPORT),exist_ok=True)
    with open(REPORT,'w',encoding='utf-8') as f: f.write('\n'.join(md))
    print('\n[报告] %s'%REPORT)
    if not args.check: print('[生成表] %s'%OUT_OVERVIEW); print('[生成表] %s'%OUT_LEVELUP)

if __name__=='__main__':
    main()
