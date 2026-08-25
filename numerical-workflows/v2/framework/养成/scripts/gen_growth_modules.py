# -*- coding: utf-8 -*-
"""
gen_growth_modules.py — 养成模块曲线 生成器 (专武 / 炮台)

读取共享参数基线 MD + 养成参数基线 MD → 生成 专武 与 炮台 的等级属性曲线，与现有表逐格对照。

专武:
  总投放 = 标准人 × 专武投放系数(投放系数页)
  基础(SSR) = 总投放 × 基础属性占比
  每级成长(SSR) = 总投放 × (1 - 基础属性占比) / 上限等级
  SR/R = SSR × 品质系数(升级曲线参数 R/SR/SSR)
炮台:
  每级值 = (单炮台属性 / 基准上限) × 档位品阶系数
  value(N) = 每级值 × N    (生命四舍五入, 攻击向下取整) ; N 跑到该档自身上限

只读源表。生成表为独立新文件。
用法: python gen_growth_modules.py [--check]
"""
import sys, io, os, argparse, math
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
OUT_WEAPON = os.path.join(GROWTH_DIR, '生成_专武.xlsx')
OUT_TURRET = os.path.join(GROWTH_DIR, '生成_炮台.xlsx')
REPORT  = os.path.join(GROWTH_DIR, '_reports', 'P养成模块_专武炮台_生成与对照.md')
SRC     = os.path.join(NUM_DIR, 'Vgame养成数值.xlsx')

def almost(a, b, tol=0.01):
    try: return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError): return a == b

def read_params():
    # 标准人、投放系数 → 从共享参数 MD 读
    wb_s = load_parameter_workbook(SHARED_PARAM, data_only=True)
    sp = wb_s['标准人']; std = {sp.cell(r,1).value: sp.cell(r,2).value for r in range(2,5)}
    fp = wb_s['投放系数']; coef = {}
    for r in range(2, fp.max_row+1):
        if fp.cell(r,1).value: coef[fp.cell(r,1).value] = fp.cell(r,2).value
    wb_s.close()

    # 升级曲线参数、养成模块参数 → 从养成参数 MD 读
    wb_g = load_parameter_workbook(GROWTH_PARAM, data_only=True)
    cp = wb_g['升级曲线参数']; qual = {}
    for r in range(2, cp.max_row+1):
        k = cp.cell(r,1).value
        if k and str(k).startswith('品阶系数_'): qual[str(k).split('_')[1]] = cp.cell(r,2).value
    gp = wb_g['养成模块参数']
    gm = {}; turret_grades = []
    for r in range(1, gp.max_row+1):
        k = gp.cell(r,1).value; v = gp.cell(r,2).value; v3 = gp.cell(r,3).value
        if k in ('专武基础属性占比','专武上限等级','单炮台生命','单炮台攻击','炮台基准上限'):
            gm[k] = v
        if k in ('B','A','S'):
            turret_grades.append((k, int(v), v3))
    wb_g.close()
    return std, coef, qual, gm, turret_grades

# ---------- 专武 ----------
def gen_weapon(std, coef, qual, gm):
    total = {a: std[a] * float(coef['专武']) for a in ('生命','攻击','防御')}  # 20000/6000/4000
    ratio = float(gm['专武基础属性占比']); cap = int(gm['专武上限等级'])
    rows = {}  # 品质 -> dict(基础=(h,a,d), 成长=(h,a,d))
    for q in ('SSR','SR','R'):
        qf = float(qual[q])
        base = {a: total[a]*ratio*qf for a in ('生命','攻击','防御')}
        grow = {a: total[a]*(1-ratio)/cap*qf for a in ('生命','攻击','防御')}
        rows[q] = (base, grow)
    return total, rows

def parity_weapon(rows):
    """对照 养成数值/专武: SSR 基础 row27 D/E/F, 成长 row28; SR row33/34; R row39/40。列 B/C/D=生命/攻击/防御(从col2)."""
    wb = openpyxl.load_workbook(SRC, data_only=True); ws = wb['专武']
    # 专武页: 基础行/成长行 的 生命/攻击/防御 在 col2/3/4
    locs = {'SSR':(27,28),'SR':(33,34),'R':(39,40)}
    fails=[]; checks=0
    for q,(rb,rg) in locs.items():
        base, grow = rows[q]
        for col,a in [(2,'生命'),(3,'攻击'),(4,'防御')]:
            for srow, kind, val in [(rb,'基础',base[a]),(rg,'成长',grow[a])]:
                act = ws.cell(srow, col).value
                checks+=1
                if not almost(val, act):
                    fails.append(('专武 %s %s %s(R%dC%d)'%(q,kind,a,srow,col), round(val,2), act))
    wb.close()
    return checks, fails

# ---------- 炮台 ----------
def gen_turret(gm, grades):
    base_cap = int(gm['炮台基准上限'])
    per = {}  # grade -> (hp_per, atk_per, cap)
    series = {}
    for (g, cap, q) in grades:
        hp_per = gm['单炮台生命']/base_cap * q
        atk_per = gm['单炮台攻击']/base_cap * q
        per[g] = (hp_per, atk_per, cap)
        series[g] = [(N, round(hp_per*N), int(atk_per*N)) for N in range(1, cap+1)]
    return per, series

def parity_turret(series):
    """对照 养成数值/炮台养成数值: S块 col2/3/4(等级/生命/攻击) 从row28; A块 col6/7/8; B块 col10/11/12."""
    wb = openpyxl.load_workbook(SRC, data_only=True); ws = wb['炮台养成数值']
    blocks = {'S':(2,3,4), 'A':(6,7,8), 'B':(10,11,12)}
    fails=[]; checks=0
    for g,(cL,cH,cA) in blocks.items():
        for i,(N,hp,atk) in enumerate(series[g]):
            r = 28 + i
            aL, aH, aA = ws.cell(r,cL).value, ws.cell(r,cH).value, ws.cell(r,cA).value
            if aL is None: continue
            for label, val, act in [('等级',N,aL),('生命',hp,aH),('攻击',atk,aA)]:
                checks+=1
                if not almost(val, act):
                    fails.append(('炮台%s L%d %s(R%d)'%(g,N,label,r), val, act))
    wb.close()
    return checks, fails

def write_out(total, wrows, tper, tseries):
    bold=Font(bold=True); hf=PatternFill('solid',fgColor='D9E1F2')

    # === 专武 ===
    wb1 = openpyxl.Workbook()
    ws=wb1.active; ws.title='专武'
    ws.append(['【自动生成·勿手改】总投放=标准人×专武系数=生命%g/攻击%g/防御%g'%(total['生命'],total['攻击'],total['防御'])])
    ws.append([]); ws.append(['品质','项','生命','攻击','防御'])
    for c in range(1,6): ws.cell(3,c).font=bold; ws.cell(3,c).fill=hf
    for q in ('SSR','SR','R'):
        base, grow = wrows[q]
        ws.append([q,'基础',round(base['生命'],2),round(base['攻击'],2),round(base['防御'],2)])
        ws.append([q,'成长',round(grow['生命'],2),round(grow['攻击'],2),round(grow['防御'],2)])
    for w,col in zip([8,8,12,12,12],'ABCDE'): ws.column_dimensions[col].width=w

    # === 各专武属性（以专武自身系数计算） ===
    ws_wp = wb1.create_sheet('各专武属性')
    ws_wp.append(['各专武属性（以专武自身的职业/伤害类型/微调系数计算）'])
    ws_wp.append(['公式: 标准专武基础/成长 × 职业比 × 统一攻击比 × 微调比 × 品质比'])
    ws_wp.append([])
    wp_headers = ['专武名称','品质','职业','伤害类型','基础生命','成长生命','基础攻击','成长攻击','基础防御','成长防御']
    ws_wp.append(wp_headers)
    for c in range(1, len(wp_headers)+1): ws_wp.cell(4,c).font=bold; ws_wp.cell(4,c).fill=hf

    # 读武将系数参数里的专武列表
    wb_p = load_parameter_workbook(GROWTH_PARAM, data_only=True)
    ws_wj = wb_p['武将系数']
    dmg_types = {}; weapons = []
    sec = None
    for r in range(1, ws_wj.max_row+1):
        v = ws_wj.cell(r,1).value
        if v == '伤害类型攻击分配': sec = 'dmg'; continue
        if v == '专武系数列表': sec = 'weap'; continue
        if sec == 'dmg' and v in ('物理','魔法','混合'):
            dmg_types[v] = (float(ws_wj.cell(r,2).value), float(ws_wj.cell(r,3).value))
        if sec == 'weap' and v and v != '专武名称':
            weapons.append([ws_wj.cell(r,c).value for c in range(1,14)])

    # 读标准人
    wb_s = load_parameter_workbook(SHARED_PARAM, data_only=True)
    std_hp = wb_s['标准人'].cell(2,2).value
    std_atk = wb_s['标准人'].cell(3,2).value
    std_def = wb_s['标准人'].cell(4,2).value
    wb_s.close()

    # 读专武参数
    ws_gm = wb_p['养成模块参数']
    w_base_ratio = w_cap = None; coef_w = 4
    for r in range(1, ws_gm.max_row+1):
        k = ws_gm.cell(r,1).value
        if k == '专武基础属性占比': w_base_ratio = float(ws_gm.cell(r,2).value)
        if k == '专武上限等级': w_cap = int(ws_gm.cell(r,2).value)
    wb_p.close()

    w_total = {'生命': std_hp*coef_w, '攻击': std_atk*coef_w, '防御': std_def*coef_w}

    for wp in weapons:
        name,rarity,job,dmg = wp[0],wp[1],wp[2],wp[3]
        job_hp,job_atk,job_def = float(wp[4]),float(wp[5]),float(wp[6])
        adj_hp,adj_pa,adj_ma,adj_df = float(wp[7]),float(wp[8]),float(wp[9]),float(wp[10])
        quality = float(wp[12])
        b_hp = w_total['生命'] * w_base_ratio * job_hp * adj_hp * quality
        g_hp = w_total['生命'] * (1-w_base_ratio) / w_cap * job_hp * adj_hp * quality
        # 01_源表已统一为单一攻击；伤害类型只保留表现语义，不再二次缩放攻击。
        b_atk = w_total['攻击'] * w_base_ratio * job_atk * adj_pa * quality
        g_atk = w_total['攻击'] * (1-w_base_ratio) / w_cap * job_atk * adj_pa * quality
        b_df = w_total['防御'] * w_base_ratio * job_def * adj_df * quality
        g_df = w_total['防御'] * (1-w_base_ratio) / w_cap * job_def * adj_df * quality
        ws_wp.append([name, rarity, job, dmg,
                      round(b_hp,2), round(g_hp,2), round(b_atk,2), round(g_atk,2),
                      round(b_df,2), round(g_df,2)])
    for w,col in zip([16,6,16,10,10,10,10,10,10,10],'ABCDEFGHIJ'): ws_wp.column_dimensions[col].width=w

    # === 突破属性页 ===
    ws_br = wb1.create_sheet('突破属性')
    ws_br.append(['专武突破 — 每次突破投放偏向基础属性%+二级属性'])
    ws_br.append(['总偏向值=0.6; 每把专武选择一种二级属性，5次突破逐级投放'])
    ws_br.append([])
    # 从参数基线 MD 读完整突破数据
    try:
        wb_br = load_parameter_workbook(GROWTH_PARAM, data_only=True)
        ws_brs = wb_br['专武突破']

        # 投放档位表
        br_headers = ['玩家等级', '突破等级', 'SSR投放', 'SR投放', 'R投放']
        ws_br.append(br_headers)
        for c in range(1, len(br_headers)+1): ws_br.cell(ws_br.max_row,c).font=bold; ws_br.cell(ws_br.max_row,c).fill=hf
        for r in range(6, ws_brs.max_row+1):
            lv = ws_brs.cell(r, 1).value
            if lv is None or not isinstance(lv, (int, float)): break
            ws_br.append([ws_brs.cell(r,c).value for c in range(1, 6)])

        # 各专武突破属性明细
        ws_br.append([])
        ws_br.append(['各专武突破属性明细'])
        ws_br.cell(ws_br.max_row, 1).font = bold
        ws_br.append([])
        detail_headers = ['专武名称', '所属角色', '品质', '突破属性', '突破1', '突破2', '突破3', '突破4', '突破5']
        ws_br.append(detail_headers)
        for c in range(1, len(detail_headers)+1): ws_br.cell(ws_br.max_row,c).font=bold; ws_br.cell(ws_br.max_row,c).fill=hf

        # 找到明细区域
        found_detail = False
        for r in range(1, ws_brs.max_row+1):
            if ws_brs.cell(r, 1).value == '各专武突破属性明细':
                found_detail = True; continue
            if found_detail and ws_brs.cell(r, 1).value == '专武名称': continue
            if found_detail and ws_brs.cell(r, 2).value in (None, '所属角色'):
                continue  # 跳过说明行和表头
            if found_detail and ws_brs.cell(r, 1).value and ws_brs.cell(r, 2).value:
                ws_br.append([ws_brs.cell(r,c).value for c in range(1, 10)])

        wb_br.close()
    except Exception as e:
        ws_br.append(['读取失败: %s' % str(e)])
    for w,col in zip([16, 12, 6, 18, 10, 10, 10, 10, 10], 'ABCDEFGHI'): ws_br.column_dimensions[col].width=w

    wb1.save(OUT_WEAPON)

    # === 炮台 ===
    wb2 = openpyxl.Workbook()
    ws2=wb2.active; ws2.title='炮台(竞技场)'
    ws2.append(['【自动生成·勿手改】炮台为竞技场专属养成，与外部战斗不互通'])
    ws2.append(['每级=(单炮台属性/基准上限)×品阶; value=每级×等级(攻击向下取整)'])
    ws2.append([]); ws2.append(['档位','等级','生命','攻击'])
    for c in range(1,5): ws2.cell(4,c).font=bold; ws2.cell(4,c).fill=hf
    for g in ('S','A','B'):
        for (N,hp,atk) in tseries[g]:
            ws2.append([g,N,hp,atk])
    for w,col in zip([8,8,10,10],'ABCD'): ws2.column_dimensions[col].width=w
    wb2.save(OUT_TURRET)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    std, coef, qual, gm, grades = read_params()
    total, wrows = gen_weapon(std, coef, qual, gm)
    tper, tseries = gen_turret(gm, grades)
    wc, wf = parity_weapon(wrows)
    tc, tf = parity_turret(tseries)
    if not args.check:
        write_out(total, wrows, tper, tseries)

    md=[]
    def o(s=''):
        print(s); md.append(s)
    o('# 养成模块 · 专武 / 炮台 生成与对照'); o()
    o('> 参数→曲线，与现有 养成数值 逐格对照。源表只读。'); o()
    o('## 专武'); o('- 总投放(标准人×专武系数) 生命%g/攻击%g/防御%g'%(total['生命'],total['攻击'],total['防御']))
    o('- 对照 %d 格，不一致 %d'%(wc,len(wf)))
    if wf:
        o('| 位置 | 生成 | 源 |'); o('|---|--:|--:|')
        for (loc,v,a) in wf[:15]: o('| %s | %s | %s |'%(loc,v,a))
    else: o('- ✅ 专武曲线逐格复现')
    o()
    o('## 炮台'); o('- 对照 %d 格，不一致 %d'%(tc,len(tf)))
    if tf:
        o('| 位置 | 生成 | 源 |'); o('|---|--:|--:|')
        for (loc,v,a) in tf[:15]: o('| %s | %s | %s |'%(loc,v,a))
    else: o('- ✅ 炮台曲线逐格复现 (S/A/B 三档)')
    o()
    o('**合计对照 %d 格，不一致 %d**'%(wc+tc, len(wf)+len(tf)))
    os.makedirs(os.path.dirname(REPORT),exist_ok=True)
    with open(REPORT,'w',encoding='utf-8') as f: f.write('\n'.join(md))
    print('\n[报告] %s'%REPORT)
    if not args.check: print('[生成表] %s' % OUT_WEAPON); print('[生成表] %s' % OUT_TURRET)

if __name__=='__main__':
    main()
