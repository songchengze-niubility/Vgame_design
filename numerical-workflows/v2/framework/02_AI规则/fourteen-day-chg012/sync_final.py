# -*- coding: utf-8 -*-
"""单进程：稳定复核 + 设计数据/MD/校验器同步到 v15 权威值。"""
import re
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(".").resolve().parents[1]          # framework/
CFG = HERE / "06_最终配置" / "任务"
MD = HERE / "03_沉淀MD" / "经济" / "11_外循环_任务_03_开服挑战经济沉淀-2026-07-09.md"
DATA = HERE / "02_AI规则" / "fourteen-day-chg012" / "chg012_data.py"
REVIEW = HERE / "02_AI规则" / "fourteen-day-chg012" / "make_review_xlsx.py"
VALID = HERE / "02_AI规则" / "fourteen-day-chg012" / "validate_chg013.py"
ITEM = {1: "猎鹰金币", 6: "沿途随笔", 19: "勇士勋章", 25: "映射之匙", 28: "校准元件",
        33: "漫游邮戳", 100: "低阶记录盘", 102: "高阶记录盘", 106: "旅券", 107: "收容凭证",
        108: "泛黄档案", 109: "录像带", 111: "限时旅券", 301: "商品筹码", 1074: "房车零件",
        1156: "高级指南材料", 3010: "1级宝石掉落箱", 3011: "2级宝石掉落箱",
        3015: "普通能效自选箱", 3027: "指南材料自选箱", 51001: "虚妄之镜", 311029: "凯兰"}
DAY_BASE = {8: 91000102, 9: 91000108, 10: 91000114, 11: 91000120,
            12: 91000126, 13: 91000132, 14: 91000138}
HUNDRED = {58: 8, 59: 9, 61: 10, 62: 11, 63: 12, 64: 13, 65: 14}
T0 = {8: 5801, 9: 5901, 10: 6101, 11: 6201, 12: 6301, 13: 6401, 14: 6501}

wb = load_workbook(CFG / "Drop_TimeLimitedActivity.xlsx", read_only=True, data_only=True)
groups = defaultdict(list)
for r in wb["Drop"].iter_rows(min_row=5, values_only=True):
    if r and len(r) > 2 and isinstance(r[2], int) and (91000001 <= r[2] <= 91000070 or 91000102 <= r[2] <= 91000143):
        groups[r[2]].append((r[10], r[11]))
wb.close()


def pack_of(tid):
    if tid <= 5710:
        day = (tid - 5101) // 100 + 1
        return 91000000 + (day - 1) * 10 + (tid - 5101) % 100 + 1
    return DAY_BASE[HUNDRED[tid // 100]] + (tid % 100) - 1


auth, bad, bad_samples = {}, 0, []
for day in range(1, 8):
    for seq in range(1, 11):
        tid = 5101 + (day - 1) * 100 + seq - 1
        did = 91000000 + (day - 1) * 10 + seq
        extra = [x for x in groups[did] if x[0] != 32]
        if (32, 10) not in groups[did] or len(extra) != 1:
            bad += 1
            bad_samples.append((tid, did, groups[did]))
            continue
        auth[tid] = extra[0]
for h, day in HUNDRED.items():
    base = DAY_BASE[day]
    for seq in range(1, 7):
        tid = T0[day] + seq - 1
        extra = [x for x in groups[base + seq - 1] if x[0] != 32]
        if (32, 10) not in groups[base + seq - 1] or len(extra) != 1:
            bad += 1
            bad_samples.append((tid, base + seq - 1, groups[base + seq - 1]))
            continue
        auth[tid] = extra[0]
print("DEBUG CFG =", CFG)
print("DEBUG groups包数 =", len(groups), "| 总行 =", sum(len(v) for v in groups.values()))
print("DEBUG bad =", bad, "| 样本:", bad_samples[:4])
assert bad == 0, f"包结构异常 {bad}"
print("稳定复核: 112包全部为 积分×10 + 1项玩法奖励")
print("DEBUG CFG =", CFG)
print("DEBUG groups包数 =", len(groups), "| 总行 =", sum(len(v) for v in groups.values()))


def rw(tid):
    i, n = auth[tid]
    return f"{ITEM[i]}({i})×{n}"


# chg012_data DAYS 奖励元组（逐行处理）
p = DATA
lines = p.read_text(encoding="utf-8").split("\n")
cnt = 0
for li, line in enumerate(lines):
    s = line.strip()
    m = re.match(r"\((\d+), \(.*\), \(\d+, \d+(?:, \"[^\"]+\")?\)\),?$", s)
    if not m:
        continue
    tid = int(m.group(1))
    if tid not in auth:
        continue
    i, n = auth[tid]
    new_line = re.sub(r"\(\d+, \d+(?:, \"[^\"]+\")?\)\),?$", f'({i}, {n}, "{ITEM[i]}"))', s)
    if new_line != s:
        lines[li] = new_line
        cnt += 1
p.write_text("\n".join(lines), encoding="utf-8")
print("chg012_data:", cnt)

# make_review D17（逐行处理）
p = REVIEW
lines = p.read_text(encoding="utf-8").split("\n")
cnt = 0
for li, line in enumerate(lines):
    s = line.strip()
    m = re.match(r"(\(\d+,\".*\",\))\(\d+,\d+\)\),?$", s)
    if not m:
        continue
    tid = int(m.group(1))
    if tid not in auth:
        continue
    i, n = auth[tid]
    new_line = re.sub(r"\(\d+,\d+\)\),?$", f"({i},{n})),", s)
    if new_line != s:
        lines[li] = new_line
        cnt += 1
p.write_text("\n".join(lines), encoding="utf-8")
print("make_review:", cnt)

# 校验器 700 档
p = VALID
t = p.read_text(encoding="utf-8")
t = t.replace("91001007: [(2, 500), (107, 30)]", "91001007: [(2, 500), (107, 10)]")
p.write_text(t, encoding="utf-8")
print("validator: 700档收容30→10")

# MD
t = MD.read_text(encoding="utf-8")
cnt = 0
for tid, ex in auth.items():
    pat = re.compile(r"(\| \d+ \| \d+ \| " + str(tid) + r" \| [^|]+\| )[^|]+(\|)")
    m = pat.search(t)
    if m:
        i, n = ex
        repl = m.group(1) + " " + f"{ITEM[i]}({i})×{n}" + " " + m.group(2)
        if m.group(0) != repl:
            t = t[:m.start()] + repl + t[m.end():]
            cnt += 1
per_day = defaultdict(lambda: defaultdict(int))
for tid, (i, n) in auth.items():
    if tid <= 5710:
        per_day[(tid - 5101) // 100 + 1][i] += n
for day in range(1, 8):
    seg = "；".join(f"{ITEM[i]}×{n}" for i, n in sorted(per_day[day].items())) + "；挑战积分×100"
    m = re.search(r"(\| " + str(day) + r" \| )([^|]+)(\|)", t)
    if m and "挑战积分×100" in m.group(2):
        t = t[:m.start()] + m.group(1) + " " + seg + " " + m.group(3) + t[m.end():]
cnt_items = defaultdict(int)
for tid, (i, n) in auth.items():
    cnt_items[i] += n
    cnt_items[32] += 10
for yj, item, n in [(500, 106, 5), (500, 106, 5), (500, 111, 5), (1000, 51001, 1), (500, 111, 5),
                    (0, 311029, 1), (500, 107, 30), (500, 106, 5), (500, 111, 5), (500, 107, 20),
                    (500, 51001, 1)]:
    if yj:
        cnt_items[2] += yj
    cnt_items[item] += n
summary = "；".join(f"{ITEM.get(i, i)}({i})×{n}" for i, n in sorted(cnt_items.items()) if n and i != 32)
pat_total = re.compile(r"#### 第8~14天总投放（含新增里程碑）\n\n[^。]+。")
t = pat_total.sub("#### 第8~14天总投放（含新增里程碑）\n\n" + summary + "。", t)
MD.write_text(t, encoding="utf-8")
print("MD:", cnt, "行奖励列更新")
