# -*- coding: utf-8 -*-
"""
gen_mapping_equip.py — 映射装备 主属性曲线 生成器 (养成系数10, 最大模块)

读取养成参数基线 MD「映射装备参数」→ 生成 各部位×各稀有度 的主属性曲线，
与现有 养成数值「映射装备数值」(主属性部分 行10-56) 逐格对照。

主属性曲线 (可生成):
  对每个部位的红装基准(0级值 base_red / 每级成长 grow_red, 设计录入)，
  各稀有度 r (品质系数 coef, 等级上限 cap):
    基础 = coef × base_red
    成长 = coef × grow_red
    1级  = coef × (base_red + grow_red)
    满级 = 基础 + cap × 成长
  主属性1 / 主属性2 各一套 (E/F/G/H 与 J/K/L/M)。

附: 单件最终输出 (普通映射装备数值 O:T) 逐格对照 ——
  单件按 部位+稀有度 取主属性曲线的「1级数值/成长」，再乘单件偏向系数(M/N, 设计录入)
  并按面板取整。偏向系数 + 物品花名册为「输入型」，此处直接读源作输入，验证变换公式。

只读源表。生成表为独立新文件。
用法: python gen_mapping_equip.py [--check]
"""
import sys, io, os, argparse
from decimal import Decimal, ROUND_HALF_UP
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

GROWTH_PARAM = parameter_md_path('养成')
OUT     = os.path.join(GROWTH_DIR, '生成_映射装备.xlsx')
REPORT  = os.path.join(GROWTH_DIR, '_reports', 'P养成模块_映射装备主属性_生成与对照.md')
SRC     = os.path.join(NUM_DIR, 'Vgame养成数值.xlsx')

RARITY_ORDER = ['蓝', '紫', '金', '红']
# Blue/Purple/Orange/Red -> 中文
RAR_EN = {'Blue': '蓝', 'Purple': '紫', 'Orange': '金', 'Red': '红'}


def normalize_attack_name(v):
    if not isinstance(v, str):
        return v
    return (v.replace('物理攻击百分比', '攻击百分比')
             .replace('魔法攻击百分比', '攻击百分比')
             .replace('物理攻击加成', '攻击加成')
             .replace('魔法攻击加成', '攻击加成')
             .replace('物理攻击力', '攻击力')
             .replace('魔法攻击力', '攻击力')
             .replace('物理攻击%', '攻击%')
             .replace('魔法攻击%', '攻击%')
             .replace('物理攻击', '攻击')
             .replace('魔法攻击', '攻击')
             .replace('物攻', '攻击')
             .replace('魔攻', '攻击'))


def almost(a, b, tol=0.001):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return a == b


def read_params():
    # 映射装备参数 → 从养成参数 MD 读
    wb_g = load_parameter_workbook(GROWTH_PARAM, data_only=True)
    ws = wb_g['映射装备参数']
    quality = {}   # 稀有度 -> (品质系数, 等级上限)
    parts = []     # (部位, 再分类, 主1名, base1, grow1, 主2名, base2, grow2)
    mode = None
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if a == '稀有度':
            mode = 'q'; continue
        if a == '部位':
            mode = 'p'; continue
        if mode == 'q' and a in RARITY_ORDER:
            quality[a] = (float(ws.cell(r, 2).value), int(ws.cell(r, 3).value))
        elif mode == 'p' and a:
            parts.append((
                a, ws.cell(r, 2).value,
                normalize_attack_name(ws.cell(r, 3).value), ws.cell(r, 4).value, ws.cell(r, 5).value,
                normalize_attack_name(ws.cell(r, 6).value), ws.cell(r, 7).value, ws.cell(r, 8).value,
            ))
    wb_g.close()
    return quality, parts


def D(x):
    return Decimal(repr(x))


def gen_curve(quality, parts):
    """返回 {(部位, 再分类, 稀有度): {'主1':(名,基础,成长,1级,满级), '主2':(...)}}
    用 Decimal 计算, 避免二进制浮点漂移导致 0.0345 之类边界值在面板取整时翻错。"""
    out = {}
    for (bw, sub, n1, b1, g1, n2, b2, g2) in parts:
        for rar in RARITY_ORDER:
            coef_f, cap = quality[rar]
            coef = D(coef_f); capD = Decimal(cap)
            def slot(name, base_red, grow_red):
                br, gr = D(base_red), D(grow_red)
                base = coef * br
                grow = coef * gr
                lv1 = coef * (br + gr)
                full = base + capD * grow
                return (name, base, grow, lv1, full)
            out[(bw, sub, rar)] = {'主1': slot(n1, b1, g1), '主2': slot(n2, b2, g2)}
    return out


def part_key_of(part, subclass):
    """主表里武器按再分类(仪器/枪炮/权杖)区分, 其余按部位; 副表花名册部位列直接是再分类或部位。"""
    return subclass if subclass and subclass != '无' else part


def parity_master(curve):
    """对照 映射装备数值 行10-56: A部位 B再分类 C稀有 D主1名 E基础 F成长 G1级 H满级 I主2名 J K L M。"""
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb['映射装备数值']
    fails = []; checks = 0
    for r in range(10, 57):
        a = ws.cell(r, 1).value
        if a is None:
            continue
        sub = ws.cell(r, 2).value
        rar = ws.cell(r, 3).value
        key = (a, sub, rar)
        if key not in curve:
            fails.append(('主表 缺键 %s (R%d)' % (str(key), r), '-', '-'))
            continue
        cur = curve[key]
        # 主1: D名 E基础 F成长 G1级 H满级
        for slot, cols, namecol in [('主1', (5, 6, 7, 8), 4), ('主2', (10, 11, 12, 13), 9)]:
            name, base, grow, lv1, full = cur[slot]
            act_name = normalize_attack_name(ws.cell(r, namecol).value)
            checks += 1
            if act_name != name:
                fails.append(('主表 R%d %s 名(%s!=%s)' % (r, slot, name, act_name), name, act_name))
            for val, col, lbl in [(base, cols[0], '基础'), (grow, cols[1], '成长'),
                                  (lv1, cols[2], '1级'), (full, cols[3], '满级')]:
                act = ws.cell(r, col).value
                checks += 1
                if not almost(val, act):
                    fails.append(('主表 R%dC%d %s %s' % (r, col, slot, lbl), round(val, 4), act))
    wb.close()
    return checks, fails


def parity_items(curve):
    """对照 普通映射装备数值 O:T 单件最终输出。
    单件: 部位(E) 稀有度(F, 英文) 偏向系数 主1=M(col13) 主2=N(col14)。
    取曲线[部位,稀有度] 的 1级/成长, ×偏向, 面板取整:
       1级数值 = ROUND(curve_1级 × coef, 0 if >=1 else 3)
       成长    = ROUND(curve_成长 × coef, 0 if >=1 else 3)  (主2成长<1 时小数位4)
    对照源 O(主1名) P(1级) Q(成长) R(主2名) S(1级) T(成长)。"""
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb['普通映射装备数值']
    fails = []; checks = 0; nitems = 0

    def rnd(v, base_for_prec, growth=False):
        # Excel ROUND: 四舍五入(远离0), 区别于 Python 银行家舍入; v 为 Decimal
        prec = 0 if abs(base_for_prec) >= 1 else (4 if growth else 3)
        q = Decimal(1).scaleb(-prec)
        return float(v.quantize(q, rounding=ROUND_HALF_UP))

    for r in range(3, ws.max_row + 1):
        cid = ws.cell(r, 3).value
        if cid is None:
            continue
        part = ws.cell(r, 5).value
        rar_en = ws.cell(r, 6).value
        rar = RAR_EN.get(rar_en, rar_en)
        m = ws.cell(r, 13).value  # 主属性1系数
        n = ws.cell(r, 14).value  # 主属性2系数
        if m is None or n is None:
            continue
        # find curve key: part may be 仪器/枪炮/权杖 (再分类) or 头盔.. (部位)
        key = None
        for (bw, sub, rr) in curve:
            if rr == rar and part_key_of(bw, sub) == part:
                key = (bw, sub, rr); break
        if key is None:
            fails.append(('单件 R%d 缺键 part=%s rar=%s' % (r, part, rar), '-', '-')); continue
        nitems += 1
        cur = curve[key]
        for slot, coef, cols in [('主1', D(m), (15, 16, 17)), ('主2', D(n), (18, 19, 20))]:
            name, base, grow, lv1, full = cur[slot]
            exp_name = name
            exp_lv1 = rnd(lv1 * coef, lv1)
            exp_grow = rnd(grow * coef, lv1, growth=True)
            act_name = normalize_attack_name(ws.cell(r, cols[0]).value)
            act_lv1 = ws.cell(r, cols[1]).value
            act_grow = ws.cell(r, cols[2]).value
            for val, act, lbl in [(exp_name, act_name, '名'), (exp_lv1, act_lv1, '1级'), (exp_grow, act_grow, '成长')]:
                checks += 1
                ok = (val == act) if lbl == '名' else almost(val, act)
                if not ok:
                    fails.append(('单件 ID%s R%d %s %s' % (cid, r, slot, lbl), val, act))
    wb.close()
    return checks, fails, nitems


def write_out(curve, parts):
    wb = openpyxl.Workbook()
    bold = Font(bold=True); hf = PatternFill('solid', fgColor='D9E1F2')

    # Sheet 1: 主属性曲线
    ws = wb.active; ws.title = '主属性曲线'
    ws.append(['【自动生成·勿手改】各档基础/成长=品质系数×红装基准; 满级=基础+等级上限×成长'])
    ws.append([])
    ws.append(['部位', '再分类', '稀有度', '主属性1', '基础1', '成长1', '1级1', '满级1',
               '主属性2', '基础2', '成长2', '1级2', '满级2'])
    for c in range(1, 14):
        ws.cell(3, c).font = bold; ws.cell(3, c).fill = hf
    for (bw, sub, n1, b1, g1, n2, b2, g2) in parts:
        for rar in RARITY_ORDER:
            cur = curve[(bw, sub, rar)]
            s1 = cur['主1']; s2 = cur['主2']
            ws.append([bw, sub, rar,
                       s1[0], float(round(s1[1], 4)), float(round(s1[2], 4)), float(round(s1[3], 4)), float(round(s1[4], 4)),
                       s2[0], float(round(s2[1], 4)), float(round(s2[2], 4)), float(round(s2[3], 4)), float(round(s2[4], 4))])
    for w, col in zip([8, 8, 8, 14, 10, 10, 10, 11, 16, 10, 10, 10, 11], 'ABCDEFGHIJKLM'):
        ws.column_dimensions[col].width = w

    # Sheet 2: 稀有度参数
    ws2 = wb.create_sheet('稀有度')
    ws2.append(['品质', '等级上限', '主属性品质系数', '副属性品质系数',
                '默认孔位', '可打孔数', '最大孔位', '副词条上限', '副词条下限',
                '打孔道具', '打孔金币'])
    for c in range(1, 12):
        ws2.cell(1, c).font = bold; ws2.cell(1, c).fill = hf
    # 从参数基线 MD 读稀有度完整信息
    try:
        wb_p = load_parameter_workbook(GROWTH_PARAM, data_only=True)
        ws_r = wb_p['映射装备_稀有度']
        for r in range(4, ws_r.max_row + 1):
            row = [ws_r.cell(r, c).value for c in range(1, 12)]
            if row[0]:
                ws2.append(row)
        wb_p.close()
    except Exception:
        pass
    for w, col in zip([8, 10, 16, 16, 10, 10, 10, 12, 12, 14, 12], 'ABCDEFGHIJK'):
        ws2.column_dimensions[col].width = w

    # Sheet 3: 红装数据
    ws3 = wb.create_sheet('红装')
    ws3.append(['序号', '技能ID', '名称', '部位', '额外词条效果', '主属性1', '主属性2',
                '副属性1', '副属性2', '副属性3', '副属性4'])
    for c in range(1, 12):
        ws3.cell(1, c).font = bold; ws3.cell(1, c).fill = hf
    try:
        wb_p = load_parameter_workbook(GROWTH_PARAM, data_only=True)
        ws_rd = wb_p['映射装备_红装']
        for r in range(5, ws_rd.max_row + 1):
            row = [normalize_attack_name(ws_rd.cell(r, c).value) for c in range(1, 12)]
            if row[0]:
                ws3.append(row)
        wb_p.close()
    except Exception:
        pass
    for w, col in zip([6, 10, 18, 16, 40, 14, 14, 16, 16, 16, 16], 'ABCDEFGHIJK'):
        ws3.column_dimensions[col].width = w

    # Sheet 4: 宝石
    ws4 = wb.create_sheet('宝石')
    ws4.append(['宝石等级', '红(攻击)', '蓝(攻击)', '黄(防御)', '绿(生命)',
                '紫(技能冷却)', '橙(能量回复)', '青(暴击)', '白(暴伤)'])
    for c in range(1, 10):
        ws4.cell(1, c).font = bold; ws4.cell(1, c).fill = hf
    try:
        wb_p = load_parameter_workbook(GROWTH_PARAM, data_only=True)
        ws_gem = wb_p['映射装备_宝石']
        for r in range(5, ws_gem.max_row + 1):
            row = [ws_gem.cell(r, c).value for c in range(1, 10)]
            if row[0] is not None:
                ws4.append(row)
            else:
                break
        wb_p.close()
    except Exception:
        pass
    for w, col in zip([10, 12, 12, 12, 12, 14, 14, 12, 12], 'ABCDEFGHI'):
        ws4.column_dimensions[col].width = w

    # Sheet 5: 副属性
    ws5 = wb.create_sheet('副属性')
    ws5.append(['序号', '属性名', '属性下限', '属性上限', '最小随机单位', '权重', '词条基础评分'])
    for c in range(1, 8):
        ws5.cell(1, c).font = bold; ws5.cell(1, c).fill = hf
    try:
        wb_p = load_parameter_workbook(GROWTH_PARAM, data_only=True)
        ws_sub = wb_p['映射装备_副属性']
        for r in range(5, ws_sub.max_row + 1):
            row = [normalize_attack_name(ws_sub.cell(r, c).value) for c in range(1, 8)]
            if row[0] is not None and isinstance(row[0], (int, float)):
                ws5.append(row)
            else:
                break
        wb_p.close()
    except Exception:
        pass
    for w, col in zip([6, 20, 12, 12, 14, 8, 14], 'ABCDEFG'):
        ws5.column_dimensions[col].width = w

    wb.save(OUT)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); args = ap.parse_args()
    quality, parts = read_params()
    curve = gen_curve(quality, parts)
    mc, mf = parity_master(curve)
    ic, iff, nitems = parity_items(curve)
    if not args.check:
        write_out(curve, parts)

    md = []
    def o(s=''):
        print(s); md.append(s)
    o('# 养成模块 · 映射装备 主属性 生成与对照'); o()
    o('> 系数10最大养成模块。主属性曲线由参数派生; 与现有 养成数值 逐格对照。源表只读。'); o()
    o('## 主属性曲线 (映射装备数值 行10-56)')
    o('- 对照 %d 格，不一致 %d' % (mc, len(mf)))
    if mf:
        o('| 位置 | 生成 | 源 |'); o('|---|--:|--:|')
        for (loc, v, a) in mf[:20]:
            o('| %s | %s | %s |' % (loc, v, a))
    else:
        o('- ✅ **主属性曲线逐格复现** (10部位 × 4稀有度 × 主1/主2 × 基础/成长/1级/满级+名)')
    o()
    o('## 单件最终输出 (普通映射装备数值 O:T, %d件)' % nitems)
    o('- 偏向系数(M/N)+物品花名册为输入型, 读源作输入, 验证「曲线×偏向→面板取整」变换。')
    o('- 对照 %d 格，不一致 %d' % (ic, len(iff)))
    if iff:
        o('| 位置 | 生成 | 源 |'); o('|---|--:|--:|')
        for (loc, v, a) in iff[:20]:
            o('| %s | %s | %s |' % (loc, v, a))
    else:
        o('- ✅ **单件最终主属性逐格复现** (1级数值/成长, 主1/主2)')
    o()
    o('**合计对照 %d 格，不一致 %d**' % (mc + ic, len(mf) + len(iff)))
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    print('\n[报告] %s' % REPORT)
    if not args.check:
        print('[生成表] %s' % OUT)


if __name__ == '__main__':
    main()
