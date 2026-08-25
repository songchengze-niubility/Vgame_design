# -*- coding: utf-8 -*-
"""
gen_combat_late.py — 标准战斗模型 后期层 生成器 (框架重搭 P2b)

读取共享参数基线 MD（标准人）+ 战斗参数基线 MD（战斗后期参数 / 英雄职业系数 / 战斗模型参数K）→
复现 标准模型 后期全链:
  有百分比标准人属性 → 减伤/eHP/ttk
  BOSS战斗系数(普攻/必杀/技能量级) → 伤害量级总和
  各属性边际收益(普攻速度/必杀回复/冷却缩减提升比例)
  六大乘区 → MAX单体每秒伤害 / 5人每秒伤害
  后期/中期标准boss属性(生命放大→eHP/ttk)
  英雄职业系数(echo)

与现有 战斗框架/标准模型 逐格对照 (源表只读)。
注: 后期链建在「标准模型自带(stale)投放 7.9/20」上以逐格复现源; ruling②(8.1) 分歧见报告。

默认只写校验报告；如需临时导出 xlsx，可加 --export-xlsx。

用法:
    python gen_combat_late.py
    python gen_combat_late.py --export-xlsx
"""
import sys, io, os, argparse
import warnings
warnings.filterwarnings('ignore')
import openpyxl
from openpyxl.styles import Font, PatternFill

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(COMBAT_DIR)
NUM_DIR = os.path.dirname(V2_DIR)
sys.path.insert(0, V2_DIR)
from _shared.md_parameter_reader import load_parameter_workbook, parameter_md_path

SHARED_PARAM = parameter_md_path('共享')
COMBAT_PARAM = parameter_md_path('战斗')
OUT = os.path.join(COMBAT_DIR, '生成_战斗模型后期.xlsx')
REPORT = os.path.join(COMBAT_DIR, '_reports', 'P2b_战斗模型后期_生成与对照.md')
SRC = os.path.join(NUM_DIR, 'Vgame基本战斗框架.xlsx')


def almost(a, b):
    if a is None or b is None:
        return a == b
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return a == b
    tol = max(0.01, abs(b) * 1e-6)   # 大数用相对容差
    return abs(a - b) <= tol


def read_params():
    wb = load_parameter_workbook(SHARED_PARAM, data_only=True)
    sp = wb['标准人']
    std = {sp.cell(r, 1).value: sp.cell(r, 2).value for r in range(2, sp.max_row + 1) if sp.cell(r, 1).value}
    wb.close()
    wb = load_parameter_workbook(COMBAT_PARAM, data_only=True)
    mp = wb['战斗模型参数']
    model = {mp.cell(r, 1).value: mp.cell(r, 2).value for r in range(2, mp.max_row + 1) if mp.cell(r, 1).value}
    lp = wb['战斗后期参数']
    p = {lp.cell(r, 1).value: lp.cell(r, 2).value for r in range(2, lp.max_row + 1) if lp.cell(r, 1).value}
    jp = wb['英雄职业系数']
    jobs = []
    for r in range(2, jp.max_row + 1):
        if jp.cell(r, 1).value and jp.cell(r, 1).value != '职业':
            jobs.append((jp.cell(r, 1).value, jp.cell(r, 2).value, jp.cell(r, 3).value, jp.cell(r, 4).value))
    wb.close()
    return std, model, p, jobs


def compute(std, model, p):
    K = float(model['防御常数K'])
    dps_coef = float(model['怪物DPS系数'])
    g = {}

    # 中期 base (stale 7.9 / 20)
    nb = float(p['裸体总和系数']); ext = float(p['额外总和系数'])
    bh, ba, bd = std['生命'] * nb, std['攻击'] * nb, std['防御'] * nb      # 39500/11850/7900
    eh, ea, ed = std['生命'] * ext, std['攻击'] * ext, std['防御'] * ext   # 100000/30000/20000
    th, ta, td = bh + eh, ba + ea, bd + ed                               # 总 139500/41850/27900

    # 后期 有百分比属性
    ap = float(p['攻击力百分比投放']); dp = ap * float(p['防御百分比系数'])
    C65 = th
    D65 = ba * (1 + ap) + ea
    E65 = bd * (1 + dp) + ed
    Q65 = round(E65 / (E65 + K), 2)
    S65 = round(C65 / (1 - Q65))
    S66 = S65 / (D65 * dps_coef)
    D67 = D65 / ta - 1
    g.update(C65=C65, D65=D65, E65=E65, Q65=Q65, S65=S65, S66=S66, D67=D67, I65=ap, J65=dp)

    # 量级
    H76 = float(p['boss对战能量上限']); H77 = float(p['必杀能量上限']); J77 = float(p['必杀回复速度'])
    H78 = float(p['技能释放间隔']); H80 = float(p['技能数量'])
    C76 = float(p['普攻频率']); C77 = float(p['必杀频率']); C78 = float(p['技能频率'])
    L75 = H77 / J77
    M76 = H77 / J77 * C76
    H82 = H76 / J77 * C77
    M77 = L75 * J77 / H76 * H82
    H79 = H78 * C78
    H81 = H79 / H80
    M78 = L75 / H78 * H79
    M79 = M76 + M77 + M78
    C79 = C76 + C77 + C78
    D82 = 1 + float(p['天赋提升']); D83 = 1 + float(p['专武提升']); D84 = 1 + float(p['旅券提升'])
    D85 = 1 + float(p['主角装备提升']); D86 = 1 + float(p['星盘天赋提升'])
    C89 = D82 * D83 * D84 * D85 * D86
    C90 = D83 * D84 * D85 * D86
    C92 = C89 * C76; C93 = C77 * C89; C94 = C78 * C89
    C95 = C79 * D82 * D83 * D84 * D86 * D85
    g.update(L75=L75, M76=M76, H82=H82, M77=M77, H79=H79, H81=H81, M78=M78, M79=M79,
             C79=C79, D82=D82, D83=D83, D84=D84, D85=D85, D86=D86, C89=C89, C90=C90,
             C92=C92, C93=C93, C94=C94, C95=C95,
             N76=M76 / M79, N77=M77 / M79, N78=M78 / M79)

    # 回血 sub-block
    J72 = float(p['玩家吃到伤害比例'])
    J70 = H76 / J77; J71 = J70 * 100; J73 = J71 * J72

    # 边际收益
    C99 = float(p['普攻速度提升']); C101 = float(p['必杀回复速度提升']); C103 = float(p['冷却缩减'])
    F99 = (1 + C99) * M76 + M77 + M78; H99 = F99 / M79 - 1
    A101 = (1 + C101) * J77
    F101 = L75 / (H76 / J77 / (1 + C101)) * M77 + M76 + M78; H101 = F101 / M79 - 1
    F103 = M76 + M77 + M78 * 1 / (1 - C103); H103 = F103 / M79 - 1
    g.update(F99=F99, H99=H99, A101=A101, F101=F101, H101=H101, F103=F103, H103=H103)

    # 乘区 → MAX DPS
    G65 = float(p['暴击率']); H65 = float(p['暴击伤害']); F12 = float(p['暴击伤害基础'])
    C105 = float(p['增伤乘区预计投放']); J108 = float(p['五人系数'])
    B110 = 1 + G65 * (H65 + F12 - 1)
    C110 = 1.0
    D110 = H99 + 1
    E110 = H101 + 1
    F110 = C105 + 1
    G110 = 1 + H103
    H110 = B110 * C110 * D110 * E110 * F110 * G110
    I110 = C95 * H110 * D65
    J110 = I110 * J108
    g.update(B110=B110, C110=C110, D110=D110, E110=E110, F110=F110, G110=G110,
             H110=H110, I110=I110, J110=J110)

    # boss 后期
    A116 = float(p['boss生命放大_后期'])
    B116 = A116 * C65; C116 = D65; D116 = E65
    G116 = round(D116 / (D116 + K), 2)
    I116 = round(B116 / (1 - G116))
    I117 = I116 / (C116 * C95 * H110)
    g.update(B116=B116, C116=C116, D116=D116, G116=G116, I116=I116, I117=I117)
    # 标准必杀回血系数 J74 = J73×G116 (依赖boss减伤)
    J74 = J73 * G116
    g.update(J70=J70, J71=J71, J73=J73, J74=J74)

    # boss 中期
    A122 = float(p['boss生命放大_中期'])
    B122 = bh * A122; C122 = ba; D122 = bd
    G122 = round(D122 / (D122 + K), 2)
    I122 = round(B122 / (1 - G122))
    I123 = I122 / (C122 * dps_coef)
    g.update(B122=B122, C122=C122, D122=D122, G122=G122, I122=I122, I123=I123)

    return g


# 生成键 -> 源表 标准模型 单元格
CELL_MAP = [
    # 后期 有百分比属性
    ('C65', 'C65', '后期总生命'), ('D65', 'D65', '后期攻击'), ('E65', 'E65', '后期防御'),
    ('Q65', 'Q65', '后期减伤率'), ('S65', 'S65', '后期eHP'), ('S66', 'S66', '后期ttk'),
    ('D67', 'D67', '攻击提升'),
    # 量级
    ('L75', 'L75', '秒伤害系数'), ('M76', 'M76', '普攻伤害'), ('H82', 'H82', '必杀系数'),
    ('M77', 'M77', '必杀伤害'), ('H79', 'H79', '技能系数'), ('H81', 'H81', '单技能系数'),
    ('M78', 'M78', '技能伤害'), ('M79', 'M79', '量级合'), ('C79', 'C79', '频率总和'),
    ('C89', 'C89', '总提升比例'), ('C90', 'C90', '无天赋提升'),
    ('C92', 'C92', '普攻量级'), ('C93', 'C93', '必杀量级'), ('C94', 'C94', '技能量级'),
    ('C95', 'C95', '伤害量级总和'),
    ('N76', 'N76', '普攻占比'), ('N77', 'N77', '必杀占比'), ('N78', 'N78', '技能占比'),
    ('J70', 'J70', '必杀释放速度'), ('J71', 'J71', '怪物伤害'), ('J73', 'J73', '单必杀吃伤'),
    ('J74', 'J74', '标准必杀回血系数'),
    # 边际
    ('F99', 'F99', '普攻速度40s伤害'), ('H99', 'H99', '普攻速度提升比例'),
    ('A101', 'A101', '必杀回复秒数'), ('F101', 'F101', '必杀回复40s伤害'), ('H101', 'H101', '必杀回复提升比例'),
    ('F103', 'F103', '冷却40s伤害'), ('H103', 'H103', '冷却提升比例'),
    # 乘区
    ('B110', 'B110', '暴击乘区'), ('C110', 'C110', '攻击力乘区'), ('D110', 'D110', '普攻乘区'),
    ('E110', 'E110', '必杀乘区'), ('F110', 'F110', '增伤乘区'), ('G110', 'G110', '技能乘区'),
    ('H110', 'H110', 'MAX单体每秒伤害'), ('I110', 'I110', 'MAX单体DPS值'), ('J110', 'J110', '5人每秒伤害'),
    # boss 后期
    ('B116', 'B116', 'boss后期生命'), ('C116', 'C116', 'boss后期攻击'), ('D116', 'D116', 'boss后期防御'),
    ('G116', 'G116', 'boss后期减伤'), ('I116', 'I116', 'boss后期eHP'), ('I117', 'I117', 'boss后期ttk'),
    # boss 中期
    ('B122', 'B122', 'boss中期生命'), ('C122', 'C122', 'boss中期攻击'), ('D122', 'D122', 'boss中期防御'),
    ('G122', 'G122', 'boss中期减伤'), ('I122', 'I122', 'boss中期eHP'), ('I123', 'I123', 'boss中期ttk'),
]


def parity(g):
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb['标准模型']
    fails = []; checks = 0
    for (key, cell, label) in CELL_MAP:
        exp = g[key]; act = ws[cell].value
        checks += 1
        if not almost(exp, act):
            fails.append((label + '(' + cell + ')', exp, act))
    wb.close()
    return checks, fails


def write_out(g, jobs):
    wb = openpyxl.Workbook(); bold = Font(bold=True); hf = PatternFill('solid', fgColor='D9E1F2')
    ws = wb.active; ws.title = '标准模型-后期层'
    ws.append(['【自动生成·勿手改】源:03_沉淀MD/参数基线（共享+战斗）. 复现标准模型后期全链'])
    ws.append([])
    sections = [
        ('后期 有百分比标准人属性', [('总生命', 'C65'), ('攻击', 'D65'), ('防御', 'E65'),
                            ('减伤率', 'Q65'), ('eHP', 'S65'), ('ttk', 'S66'), ('攻击提升', 'D67')]),
        ('BOSS战斗系数 / 伤害量级', [('普攻伤害', 'M76'), ('必杀伤害', 'M77'), ('技能伤害', 'M78'),
                            ('量级合', 'M79'), ('必杀系数', 'H82'), ('技能系数', 'H79'),
                            ('总提升比例', 'C89'), ('伤害量级总和', 'C95')]),
        ('各属性边际收益', [('普攻速度提升', 'H99'), ('必杀回复提升', 'H101'), ('冷却提升', 'H103')]),
        ('六大乘区 → MAX DPS', [('暴击乘区', 'B110'), ('必杀乘区', 'E110'), ('增伤乘区', 'F110'),
                          ('技能乘区', 'G110'), ('MAX单体每秒伤害', 'H110'),
                          ('MAX单体DPS', 'I110'), ('5人每秒伤害', 'J110')]),
        ('后期标准boss', [('生命', 'B116'), ('eHP', 'I116'), ('ttk', 'I117')]),
        ('中期标准boss', [('生命', 'B122'), ('eHP', 'I122'), ('ttk', 'I123')]),
    ]
    for title, items in sections:
        ws.append([title]); ws.cell(ws.max_row, 1).font = bold; ws.cell(ws.max_row, 1).fill = hf
        for (lbl, key) in items:
            v = g[key]
            ws.append([lbl, round(v, 4) if isinstance(v, float) else v])
        ws.append([])
    ws.append(['英雄职业系数']); ws.cell(ws.max_row, 1).font = bold; ws.cell(ws.max_row, 1).fill = hf
    ws.append(['职业', '生命', '攻击', '防御'])
    for (job, h, a, d) in jobs:
        ws.append([job, h, a, d])
    for w, col in zip([20, 16, 10, 10], 'ABCD'):
        ws.column_dimensions[col].width = w
    wb.save(OUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='兼容旧参数；默认即只验证/写报告')
    ap.add_argument('--export-xlsx', action='store_true', help='临时导出调试用 xlsx')
    args = ap.parse_args()
    std, model, p, jobs = read_params()
    g = compute(std, model, p)
    checks, fails = parity(g)
    if args.export_xlsx:
        write_out(g, jobs)

    md = []
    def o(s=''):
        print(s); md.append(s)
    o('# P2b · 标准战斗模型 后期层 生成与对照'); o()
    o('> 有百分比属性→量级→边际→乘区→MAX DPS / boss打桩ttk + 职业系数。源表只读。'); o()
    o('- 后期链建在标准模型自带(stale)投放 7.9/20 上以复现源(=0) (ruling② 为 8.1, 见下).'); o()
    o('## 逐格对照 (标准模型 后期段, %d 格)' % checks)
    o('- 不一致 %d' % len(fails))
    if fails:
        o('| 项 | 生成 | 源 |'); o('|---|--:|--:|')
        for (loc, v, a) in fails[:30]:
            o('| %s | %s | %s |' % (loc, v, a))
    else:
        o('- ✅ **后期层逐格复现** (有百分比属性 / 伤害量级 / 边际收益 / 六乘区 / MAX DPS / boss打桩)')
    o()
    o('## 关键产出')
    o('- 后期标准人 生命%g/攻击%g/防御%g, 减伤%.2f, eHP%g, ttk%.3fs' % (g['C65'], g['D65'], g['E65'], g['Q65'], g['S65'], g['S66']))
    o('- 伤害量级总和 %.2f/s; MAX单体每秒伤害倍率 %.3f → MAX单体DPS %g, 5人 %g' % (g['C95'], g['H110'], g['I110'], g['J110']))
    o('- 后期boss eHP %g, ttk %.2fs; 中期boss eHP %g, ttk %.2fs' % (g['I116'], g['I117'], g['I122'], g['I123']))
    o()
    o('## 待确认 (投放口径)')
    o('- 后期链沿用标准模型自带投放(裸体7.9/额外20); ruling② 权威投放为 8.1(升级4.8/升阶0/星盘2.3)。')
    o('  若后期也切 ruling②, 攻击/防御/eHP/ttk/DPS 全链会变。本表先逐格复现源(=0), 切换与否待裁决。')
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    print('\n[报告] %s' % REPORT)
    if args.export_xlsx:
        print('[生成表] %s' % OUT)


if __name__ == '__main__':
    main()
