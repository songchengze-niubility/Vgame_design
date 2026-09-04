# -*- coding: utf-8 -*-
"""CHG-026 终版重建：按缓存DropId删除任务区间全部行（含公式行），重建224行字面行。

问题根因：d1~7任务包是SVN时代公式行（DropId为公式），openpyxl非data_only读取时
该列是公式字符串，按数值删行永远删不到；历次追加的字面行与公式行并存成同一
DropId双包（游戏双倍掉落）。本脚本用 data_only 缓存值匹配删除，重建后任务区间
内零公式。
"""
import sys
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parents[2]
CFG = HERE / "06_最终配置" / "任务"
V15 = Path("D:/Vgame_design/output/14日任务总表-评审v15-2026-08-31.xlsx")

# v15 权威奖励
wbv = load_workbook(V15, read_only=True, data_only=True)
auth = {}
for r in list(wbv["14日任务总表"].iter_rows(values_only=True))[1:]:
    tid = r[2]
    if isinstance(tid, int) and 5101 <= tid <= 6510:
        auth[tid] = (int(r[10]), int(r[11]))
wbv.close()
assert len(auth) == 112

ITEM = {1: "猎鹰金币", 6: "沿途随笔", 19: "勇士勋章", 25: "映射之匙", 28: "校准元件",
        33: "漫游邮戳", 100: "低阶记录盘", 102: "高阶记录盘", 106: "旅券", 107: "收容凭证",
        108: "泛黄档案", 109: "录像带", 111: "限时旅券", 301: "商品筹码", 1074: "房车零件",
        1156: "高级指南材料", 3010: "1级宝石掉落箱", 3011: "2级宝石掉落箱",
        3015: "普通能效自选箱", 3027: "指南材料自选箱", 51001: "虚妄之镜", 311029: "凯兰"}
DAY_BASE = {8: 91000102, 9: 91000108, 10: 91000114, 11: 91000120,
            12: 91000126, 13: 91000132, 14: 91000138}
HUNDRED = {58: 8, 59: 9, 61: 10, 62: 11, 63: 12, 64: 13, 65: 14}


def pack_of(tid):
    if tid <= 5710:
        day = (tid - 5101) // 100 + 1
        return 91000000 + (day - 1) * 10 + (tid - 5101) % 100 + 1
    return DAY_BASE[HUNDRED[tid // 100]] + (tid % 100) - 1


src = CFG / "Drop_TimeLimitedActivity.xlsx"

# 1) data_only 读缓存值，收集任务区间内所有行号
wbd = load_workbook(src, read_only=True, data_only=True)
del_rows = []
for r in wbd["Drop"].iter_rows(min_row=5, values_only=True):
    pass
wbd.close()
wbd = load_workbook(src, read_only=True, data_only=True)
wsd = wbd["Drop"]
del_rows = []
for ri, r in enumerate(wsd.iter_rows(min_row=5, values_only=True), 5):
    if r and len(r) > 2 and isinstance(r[2], int) and (91000001 <= r[2] <= 91000070 or 91000102 <= r[2] <= 91000143):
        del_rows.append(ri)
wbd.close()
print("待删行(含公式行):", len(del_rows))

# 2) 可写模式自底向上删除
wb = load_workbook(src)
ws = wb["Drop"]
for r in sorted(del_rows, reverse=True):
    ws.delete_rows(r)

# 3) 重建 224 行字面行
head = [c.value for c in next(ws.iter_rows(max_row=1))]
cID = head.index("ID") + 1
cDrop = head.index("DropId") + 1
cName = head.index("DropName") + 1
cId2 = head.index("DropId2") + 1
cType = head.index("DropType") + 1
cMinN = head.index("DropMinNum") + 1
cMaxN = head.index("DropMaxNum") + 1
cItem = head.index("DropItem_id") + 1
cMin = head.index("DropItemNumMin") + 1
cMax = head.index("DropItemNumMax") + 1
cW = head.index("DropWeight") + 1
lbl = next((c for c in range(1, ws.max_column + 1) if head[c - 1] is None), None)

next_id = 400461
for tid in sorted(auth):
    item, num = auth[tid]
    if tid <= 5710:
        day = (tid - 5101) // 100 + 1
        seq = (tid - 5101) % 100 + 1
        did = 91000000 + (day - 1) * 10 + seq
        name = f"开服挑战任务{seq:02d}"
    else:
        day = HUNDRED[tid // 100]
        seq = tid % 100
        did = DAY_BASE[day] + seq - 1
        name = f"开服挑战第{day}天任务{seq:02d}"
    for it, nm in [(32, 10), (item, num)]:
        row = [None] * ws.max_column
        row[cID - 1] = next_id
        row[cDrop - 1] = did
        if lbl:
            row[lbl - 1] = f"{name}-{it}"
        row[cName - 1] = name
        row[cId2 - 1] = 0
        row[cType - 1] = "fixed_"
        row[cMinN - 1] = 1
        row[cMaxN - 1] = 1
        row[cItem - 1] = it
        row[cMin - 1] = nm
        row[cMax - 1] = nm
        row[cW - 1] = 10000
        ws.append(row)
        next_id += 1
wb.save(src)
print("重建224行, ID至", next_id - 1)

# 4) 复核：data_only 读取，112包各自恰好 积分×10+1项 且无计划外残留
from collections import defaultdict

wb2 = load_workbook(src, read_only=True, data_only=True)
g = defaultdict(list)
for r in wb2["Drop"].iter_rows(min_row=5, values_only=True):
    if r and len(r) > 2 and isinstance(r[2], int) and (91000001 <= r[2] <= 91000070 or 91000102 <= r[2] <= 91000143):
        g[r[2]].append((r[10], r[11]))
wb2.close()
bad = [t for t in sorted(auth) if sorted(g.get(pack_of(t), [])) != sorted([(32, 10), auth[t]])]
print("不一致包:", bad if bad else "无 — 112包全部与v15一致")
n_formula = 0
wb3 = load_workbook(src, read_only=True)
for r in wb3["Drop"].iter_rows(values_only=True):
    for v in (r or []):
        if isinstance(v, str) and v.startswith("="):
            n_formula += 1
wb3.close()
print("任务区间残留公式单元格:", n_formula)
if bad or n_formula:
    raise SystemExit(1)
