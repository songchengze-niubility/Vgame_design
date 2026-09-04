# -*- coding: utf-8 -*-
"""CHG-026 同步：以 v15 权威值更新 chg012_data/make_review/校验器/沉淀MD。"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
CFG = HERE.parents[1] / "06_最终配置" / "任务"
MD = HERE.parents[1] / "03_沉淀MD" / "经济" / "11_外循环_任务_03_开服挑战经济沉淀-2026-07-09.md"

# 权威值：从 06 Drop 表回读（rev14 已按 v15 重写）
wb = load_workbook(CFG / "Drop_TimeLimitedActivity.xlsx", read_only=True, data_only=True)
groups = defaultdict(list)
for r in wb["Drop"].iter_rows(min_row=5, values_only=True):
    if r and len(r) > 2 and isinstance(r[2], int):
        if (91000001 <= r[2] <= 91000070) or (91000102 <= r[2] <= 91000143):
            groups[r[2]].append((r[10], r[11]))
wb.close()

auth = {}
DAY_OF = {58: 8, 59: 9, 61: 10, 62: 11, 63: 12, 64: 13, 65: 14}
for tid in range(5101, 5711):
    day = (tid - 5101) // 100 + 1
    seq = tid - 5101 - (day - 1) * 100
    did = 91000000 + (day - 1) * 10 + seq
    extra = [x for x in groups[did] if x[0] != 32]
    auth[tid] = extra[0]
for day, base in {8: 91000102, 9: 91000108, 10: 91000114, 11: 91000120,
                  12: 91000126, 13: 91000132, 14: 91000138}.items():
    for seq in range(1, 7):
        tid = {8: 5801, 9: 5901, 10: 6101, 11: 6201, 12: 6301, 13: 6401, 14: 6501}[day] + seq - 1
        extra = [x for x in groups[base + seq - 1] if x[0] != 32]
        auth[tid] = extra[0]

ITEM = {1:"猎鹰金币",2:"元晶",6:"沿途随笔",19:"勇士勋章",25:"映射之匙",28:"校准元件",32:"挑战积分",
        33:"漫游邮戳",100:"低阶记录盘",102:"高阶记录盘",106:"旅券",107:"收容凭证",108:"泛黄档案",
        109:"录像带",111:"限时旅券",301:"商品筹码",1074:"房车零件",1156:"高级指南材料",
        3010:"1级宝石掉落箱",3011:"2级宝石掉落箱",3015:"普通能效自选箱",3027:"指南材料自选箱",
        51001:"虚妄之镜",311003:"塔拉夏",311029:"凯兰"}
def rw(tid):
    i, n = auth[tid]
    return f"{ITEM[i]}({i})×{n}"

# 1) chg012_data DAYS：按行正则替换奖励元组
p = HERE / "chg012_data.py"
t = p.read_text(encoding="utf-8")
cnt = 0
for day, base in {8: 91000102, 9: 91000108, 10: 91000114, 11: 91000120,
                  12: 91000126, 13: 91000132, 14: 91000138}.items():
    t0 = 5801 if day == 8 else {9: 5901, 10: 6101, 11: 6201, 12: 6301, 13: 6401, 14: 6501}[day]
    for seq in range(1, 7):
        tid = t0 + seq - 1
        i, n = auth[tid]
        pat = re.compile(r"(\(" + str(tid) + r", \(.*?\), )\(\d+, \d+(, \"[^\"]+\")?\)\)", re.S)
        m = pat.search(t)
        assert m, f"chg012_data 未找到 {tid}"
        repl = m.group(1) + f'({i}, {n}, "{ITEM[i]}"))'
        if m.group(0) != repl:
            t = t[:m.start()] + repl + t[m.end():]
            cnt += 1
p.write_text(t, encoding="utf-8")
print("chg012_data DAYS 行更新:", cnt)

# 2) make_review D17：前7天行奖励元组
p2 = HERE / "make_review_xlsx.py"
t2 = p2.read_text(encoding="utf-8")
cnt = 0
for tid in range(5101, 5711):
    i, n = auth[tid]
    pat = re.compile(r"(\(" + str(tid) + r",\"[^\"]*\",\"[^\"]*\",\"[^\"]*\",)\(\d+,\d+\)\)")
    m = pat.search(t2)
    assert m, f"make_review 未找到 {tid}"
    repl = m.group(1) + f"({i},{n}))"
    if m.group(0) != repl:
        t2 = t2[:m.start()] + repl + t2[m.end():]
        cnt += 1
# 里程碑 700 档收容 30→10
t2 = t2.replace('(7, 700, "收容凭证", 107, 10, 91001007)', '(7, 700, "收容凭证", 107, 10, 91001007)')
p2.write_text(t2, encoding="utf-8")
print("make_review D17 行更新:", cnt)

# 3) 校验器：700 档断言 30→10
p3 = HERE / "validate_chg013.py"
t3 = p3.read_text(encoding="utf-8")
t3 = t3.replace("91001007: [(2, 500), (107, 30)]", "91001007: [(2, 500), (107, 10)]")
p3.write_text(t3, encoding="utf-8")
print("validator updated")

# 4) MD：当前确认版70条表 + 14日扩展版42条表 按tid替换奖励列；每日汇总重算
t = md_text = MD.read_text(encoding="utf-8")
cnt = 0
for tid in range(5101, 5711):
    pat = re.compile(r"(\| \d+ \| \d+ \| " + str(tid) + r" \| [^|]+\| )[^|]+(\|)")
    m = pat.search(t)
    if m:
        repl = m.group(1) + " " + rw(tid) + " " + m.group(2)
        if m.group(0) != repl:
            t = t[:m.start()] + repl + t[m.end():]
            cnt += 1
for tid, base in {8: 91000102, 9: 91000108, 10: 91000114, 11: 91000120,
                  12: 91000126, 13: 91000132, 14: 91000138}.items():
    t0 = {8: 5801, 9: 5901, 10: 6101, 11: 6201, 12: 6301, 13: 6401, 14: 6501}[tid // 1 if False else 0] # placeholder
for day, base in {8: 91000102, 9: 91000108, 10: 91000114, 11: 91000120,
                  12: 91000126, 13: 91000132, 14: 91000138}.items():
    t0 = {8: 5801, 9: 5901, 10: 6101, 11: 6201, 12: 6301, 13: 6401, 14: 6501}[day]
    for seq in range(1, 7):
        tid = t0 + seq - 1
        i, n = auth[tid]
        pat = re.compile(r"(\| " + str(tid) + r" \| [^|]+\| )[^|]+(\|)")
        m = pat.search(t)
        if m:
            repl = m.group(1) + " " + rw(tid) + " " + m.group(2)
            if m.group(0) != repl:
                t = t[:m.start()] + repl + t[m.end():]
                cnt += 1
# 每日汇总（前7天7行）重算
per_day = defaultdict(lambda: defaultdict(int))
for tid in range(5101, 5711):
    day = (tid - 5101) // 100 + 1
    i, n = auth[tid]
    per_day[day][i] += n
for day in range(1, 8):
    items = sorted(per_day[day].items())
    seg = "；".join(f"{ITEM[i]}×{n}" for i, n in items)
    seg += "；挑战积分×100"
    pat = re.compile(r"(\| " + str(day) + r" \| )[^|]+(\|)\n(\| 每日任务组|$)")
    # 汇总行在“每日直接奖励汇总”表：| day | 奖励合计 |
    pat = re.compile(r"(\| " + str(day) + r" \| )([^|]+)(\|)")
    m = pat.search(t)
    if m and "挑战积分×100" in m.group(2):
        t = t[:m.start()] + m.group(1) + " " + seg + " " + m.group(3) + t[m.end():]
print("MD 表格行更新:", cnt)
# 总投放行（14日扩展版）重算
sys.path.insert(0, str(HERE))
import importlib
import chg012_data as DD
importlib.reload(DD)
total = DD.totals()
summary = "；".join(f"{DD.ITEM_NAMES.get(k, k)}({k})×{v}" for k, v in sorted(total.items()))
t = re.sub(r"(#### 第8~14天总投放（含新增里程碑）\n\n)[^。]+。", r"\g<1>" + summary + "。", t)
MD.write_text(t, encoding="utf-8")
print("MD updated")
