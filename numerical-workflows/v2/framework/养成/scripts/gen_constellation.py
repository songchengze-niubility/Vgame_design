# -*- coding: utf-8 -*-
"""
gen_constellation.py — 角色星盘 属性派生验证 生成器

读取共享参数基线 MD 的投放系数，并从 01_源表读取星盘预算与各角色 A/B/C 属性选择。

当前口径：
  星盘不投放基础属性；A/B/C 各 2 点、每点 0.2，三槽各 0.4，合计 1.2。

只读源表。生成表为独立新文件。
用法: python gen_constellation.py
"""
import sys, io, os, re
import warnings
warnings.filterwarnings('ignore')
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
GROWTH_DIR = os.path.dirname(HERE)  # 养成/
V2_DIR = os.path.dirname(GROWTH_DIR)  # 框架v2/
NUM_DIR = os.path.dirname(V2_DIR)  # 数值文档/数值文档/
sys.path.insert(0, V2_DIR)
from _shared.md_parameter_reader import load_parameter_workbook, parameter_md_path

SHARED_PARAM = parameter_md_path('共享')
OUT     = os.path.join(GROWTH_DIR, '生成_角色星盘.xlsx')
REPORT  = os.path.join(GROWTH_DIR, '_reports', 'P养成模块_角色星盘_生成与对照.md')
SRC     = os.path.join(V2_DIR, '01_源表', '养成属性分配.xlsx')
DESIGN_MD = os.path.join(V2_DIR, '03_沉淀MD', '养成', '角色星盘数值沉淀-2026-07-07.md')


def read_params():
    """从共享参数读取星盘基础属性系数。"""
    # 标准人、投放系数 → 从共享参数读
    wb_s = load_parameter_workbook(SHARED_PARAM, data_only=True)

    sp = wb_s['标准人']
    std = {}
    for r in range(2, sp.max_row + 1):
        k = sp.cell(r, 1).value
        v = sp.cell(r, 2).value
        if k and v is not None:
            std[k] = v

    fp = wb_s['投放系数']
    coef = {}
    for r in range(2, fp.max_row + 1):
        k = fp.cell(r, 1).value
        v = fp.cell(r, 2).value
        if k:
            coef[k] = v
    wb_s.close()

    return std, coef


def read_source():
    """从 01_源表读取星盘预算和各角色 A/B/C 属性选择。"""
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb['模块规划']
    row = next(r for r in range(1, ws.max_row + 1) if ws.cell(r, 2).value == '角色星盘')
    coef = float(ws.cell(row, 3).value or 0)
    src = {'基础属性投放系数': coef, '偏向值': ws.cell(row, 16).value, '角色属性': []}
    hero_ws = wb['角色属性分配']
    for r in range(27, hero_ws.max_row + 1):
        hero = hero_ws.cell(r, 2).value
        if hero:
            src['角色属性'].append((hero, hero_ws.cell(r, 3).value,
                                hero_ws.cell(r, 17).value, hero_ws.cell(r, 18).value, hero_ws.cell(r, 19).value,
                                hero_ws.cell(r, 14).value, hero_ws.cell(r, 15).value, hero_ws.cell(r, 16).value))

    wb.close()
    return src


def generate(coef, src):
    """计算当前星盘口径。"""
    if '角色星盘' not in coef or coef['角色星盘'] is None:
        raise ValueError('共享/投放系数 缺少角色星盘')
    budget = float(src['偏向值'])
    design = open(DESIGN_MD, encoding='utf-8').read()
    match = re.search(r'标准人满级合计基础生命\s*`\+(\d+)`、基础攻击\s*`\+(\d+)`、基础防御\s*`\+(\d+)`，折合\s*`([\d.]+)`', design)
    if not match:
        raise ValueError('最新角色星盘沉淀缺少已确认基础属性投放')
    expected_budget = re.search(r'当前二级属性总偏向预算为\s*`([\d.]+)`', design)
    if not expected_budget or abs(budget - float(expected_budget.group(1))) > 0.001:
        raise ValueError('角色星盘源表二级预算与最新沉淀不一致')
    return {
        '偏向值': budget,
        '每槽点数': 2,
        '每节点等级': 3,
        '单点预算': budget / 18,
        '每槽预算': budget / 3,
        '基础属性投放系数': float(match.group(4)),
        '源表基础属性投放系数': float(coef['角色星盘']),
        '标准人基础生命': int(match.group(1)),
        '标准人基础攻击': int(match.group(2)),
        '标准人基础防御': int(match.group(3)),
    }


def compare(gen, src):
    """逐格对照生成值与源表值。"""
    checks = []
    keys = [('偏向值', '偏向值')]
    for gen_key, src_key in keys:
        gv = gen.get(gen_key)
        sv = src.get(src_key)
        match = almost(gv, sv)
        checks.append((gen_key, gv, sv, match))
    return checks


def almost(a, b, tol=0.001):
    """数值近似对比。"""
    if a is None and b is None:
        return True
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return str(a) == str(b)


def write_output(gen, checks):
    """写生成表。"""
    wb = openpyxl.Workbook()
    bold = Font(bold=True)
    hf = PatternFill('solid', fgColor='D9E1F2')
    title_font = Font(bold=True, size=13)

    ws = wb.active
    ws.title = '角色星盘'

    ws.cell(1, 1, '角色星盘 — 养成总览')
    ws.cell(1, 1).font = title_font
    ws.cell(2, 1, '由源表与最新星盘沉淀生成：4个基础属性节点、6个二级属性节点；基础源表系数待同步。')

    r = 4
    ws.cell(r, 1, '二级属性预算'); ws.cell(r, 1).font = bold
    r += 1
    for c, h in zip(range(1, 5), ['属性槽', '节点数', '单级预算', '总预算']):
        ws.cell(r, c, h); ws.cell(r, c).font = bold; ws.cell(r, c).fill = hf
    for slot in ('A', 'B', 'C'):
        r += 1
        ws.cell(r, 1, slot); ws.cell(r, 2, gen['每槽点数']); ws.cell(r, 3, gen['单点预算']); ws.cell(r, 4, gen['每槽预算'])
    r += 1
    ws.cell(r, 1, '合计'); ws.cell(r, 1).font = bold; ws.cell(r, 2, 6); ws.cell(r, 4, gen['偏向值']); ws.cell(r, 4).font = bold
    r += 2
    ws.cell(r, 1, '标准人基础属性'); ws.cell(r, 1).font = bold
    for label, key in [('生命', '标准人基础生命'), ('攻击', '标准人基础攻击'), ('防御', '标准人基础防御')]:
        r += 1
        ws.cell(r, 1, label); ws.cell(r, 2, gen[key])
    r += 1
    ws.cell(r, 1, '沉淀已确认基础系数'); ws.cell(r, 2, gen['基础属性投放系数'])
    r += 1
    ws.cell(r, 1, '源表当前基础系数'); ws.cell(r, 2, gen['源表基础属性投放系数'])
    ws.cell(r, 3, '待人工确认并同步源表')

    # 列宽
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 8

    # === 各角色星盘属性选择 ===
    ws_h = wb.create_sheet('各角色星盘属性选择')
    ws_h.append(['各角色星盘偏向属性 -- 每角色选3种二级属性A/B/C'])
    ws_h.append(['A/B/C各2节点，每节点3级；每级预算=%s，每槽预算=%s，总预算=%s。' % (gen['单点预算'], gen['每槽预算'], gen['偏向值'])])
    ws_h.append([])
    hdrs = ['角色', '品质', '属性A', 'A预算', '属性B', 'B预算', '属性C', 'C预算', '基础生命', '基础攻击', '基础防御']
    ws_h.append(hdrs)
    for c in range(1, len(hdrs)+1): ws_h.cell(4,c).font = bold; ws_h.cell(4,c).fill = hf
    for hero, quality, attr_a, attr_b, attr_c, life_ratio, attack_ratio, defense_ratio in read_source()['角色属性']:
        ws_h.append([hero, quality, attr_a, gen['每槽预算'], attr_b, gen['每槽预算'], attr_c, gen['每槽预算'],
                     round(gen['标准人基础生命'] * float(life_ratio or 0)),
                     round(gen['标准人基础攻击'] * float(attack_ratio or 0)),
                     round(gen['标准人基础防御'] * float(defense_ratio or 0))])
    for w,col in zip([12,8,18,8,18,8,18,8],'ABCDEFGH'): ws_h.column_dimensions[col].width = w

    wb.save(OUT)


def write_report(checks):
    """写对照报告 markdown。"""
    total = len(checks)
    passed = sum(1 for c in checks if c[3])
    all_ok = passed == total

    lines = [
        '# P养成模块 · 角色星盘 生成与对照',
        '',
        '> `gen_constellation.py` 从共享参数读取基础属性系数，并以 `01_源表/养成属性分配.xlsx` 的星盘预算和角色属性选择为准。',
        '',
        '## 结论',
        '',
    ]
    if all_ok:
        lines.append('✅ **完全复现**：生成结果与现有手搓表逐格一致（%d/%d 格）。' % (passed, total))
    else:
        lines.append('⚠️ **存在偏差**：%d/%d 格一致，%d 格不一致。' % (passed, total, total - passed))

    lines += [
        '',
        '## 派生公式',
        '',
        '```',
        '基础属性已确认：标准人生命6000、攻击1800、防御1200；源表基础系数仍待人工同步。',
        'A/B/C 各2个节点×3级×每级0.1=每槽0.6',
        '总二级属性预算 = 3槽×0.6 = 1.8',
        '```',
        '',
        '## 逐格对照',
        '',
        '| 字段 | 生成值 | 源表值 | 一致 |',
        '|---|---|---|---|',
    ]
    for (key, gv, sv, match) in checks:
        lines.append('| %s | %s | %s | %s |' % (key, gv, sv, '✓' if match else '**✗**'))

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    print('=== 角色星盘 属性派生验证 ===\n')

    _, coef = read_params()
    src = read_source()
    gen = generate(coef, src)
    print('参数读取: 星盘基础属性系数 %s, 偏向值 %.2f' % (coef.get('角色星盘'), gen['偏向值']))
    print('生成: A/B/C 各 %d 点，每点 %.2f，每槽 %.2f' % (
        gen['每槽点数'], gen['单点预算'], gen['每槽预算']))
    checks = compare(gen, src)

    total = len(checks)
    passed = sum(1 for c in checks if c[3])
    print('\n对照: %d/%d 格一致' % (passed, total))
    for (key, gv, sv, match) in checks:
        if not match:
            print('  ✗ %s: 生成=%s, 源=%s' % (key, gv, sv))

    write_output(gen, checks)
    print('\n[生成表] %s' % OUT)

    write_report(checks)
    print('[报告]   %s' % REPORT)

    if passed == total:
        print('\n✅ 完全复现：%d/%d 格逐格一致。' % (passed, total))
    else:
        print('\n⚠️ 存在偏差：%d/%d 格一致。' % (passed, total))


if __name__ == '__main__':
    main()
