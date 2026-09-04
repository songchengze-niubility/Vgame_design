# -*- coding: utf-8 -*-
"""CHG-026：以用户 v15 评审表为权威源，重写 112 个任务奖励包并同步设计数据。

同时修复 Drop 表历史零值/缺行（CHG-008 时代串包残留）。
"""
import json
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

CFG = Path(__file__).resolve().parents[2] / "06_最终配置" / "任务"
RUN = CFG.parents[1] / "05_验算核算" / "十四日活动CHG012_20260831"
REV = RUN / "rev14-CHG026"
V15 = Path("D:/Vgame_design/output/14日任务总表-评审v15-2026-08-31.xlsx")
SCORE_ID, SCORE_NUM = 32, 10

# 1) 从 v15 读权威奖励
wb = load_workbook(V15, read_only=True, data_only=True)
rows = list(wb["14日任务总表"].iter_rows(values_only=True))[1:]
auth = {}
for r in rows:
    tid = r[2]
    if isinstance(tid, int) and 5101 <= tid <= 6510:
        assert r[7] == 32 and r[8] == 10, f"{tid} 积分列异常: {r[7]},{r[8]}"
        assert r[10] is not None and r[11] is not None, f"{tid} 玩法奖励缺失"
        auth[tid] = (int(r[10]), int(r[11]))
ms_v15 = {}
for r in list(wb["活跃里程碑"].iter_rows(values_only=True))[1:]:
    ms_v15[r[1]] = (r[2], r[4], r[5])  # 元晶, 额外ID, 额外数量
wb.close()

# 2) 重写 06 Drop：112 个任务包 → 恰好 (32,10)+(extra) 两行
REV.mkdir(parents=True, exist_ok=True)
src = CFG / "Drop_TimeLimitedActivity.xlsx"
shutil.copy2(src, REV / "Drop_TimeLimitedActivity.xlsx")
wb = load_workbook(src)
ws = wb["Drop"]
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
lbl = next((c for c in range(1, ws.max_column + 1) if head[c-1] is None), None)

packs = defaultdict(list)
del_rows = []
for r in range(5, ws.max_row + 1):
    did = ws.cell(row=r, column=cDrop).value
    if isinstance(did, int) and 91000001 <= did <= 91000070 or (isinstance(did, int) and 91000102 <= did <= 91000143):
        packs[did].append(r)
changed = added = removed = 0
for tid, (item, num) in sorted(auth.items()):
    day = (tid - 5101) // 100 + 1 if tid <= 5710 else {58: 8, 59: 9, 61: 10, 62: 11, 63: 12, 64: 13, 65: 14}[tid // 100]
    seq = (tid - 1) % 100 + 1 if tid <= 5710 else tid % 100
    if tid <= 5710:
        did = 91000000 + (tid - 5100) if False else 91000000 + (day - 1) * 10 + seq
    else:
        base = {8: 91000102, 9: 91000108, 10: 91000114, 11: 91000120,
                12: 91000126, 13: 91000132, 14: 91000138}[day]
        did = base + seq - 1
    name = f"开服挑战第{day}天任务{seq:02d}" if tid > 5710 else None
    rs = packs.get(did, [])
    target = [(SCORE_ID, SCORE_NUM), (item, num)]
    # 删除不在目标内的行；更新匹配行
    seen = set()
    for r in rs:
        it = ws.cell(row=r, column=cItem).value
        nm = (ws.cell(row=r, column=cMin).value, ws.cell(row=r, column=cMax).value)
        match = next((t for t in target if t[0] == it), None)
        if match and nm != (match[1], match[1]):
            ws.cell(row=r, column=cMin).value = match[1]
            ws.cell(row=r, column=cMax).value = match[1]
            changed += 1
        if match:
            seen.add(it)
            if name and tid > 5710:
                ws.cell(row=r, column=cName).value = name
        else:
            del_rows.append(r)
    for it, num2 in target:
        if it in seen:
            continue
        row = [None] * ws.max_column
        row[cID - 1] = "NEW"
        row[cDrop - 1] = did
        if lbl:
            row[lbl - 1] = f"{name or '开服挑战任务'}-{it}"
        row[cName - 1] = name or f"开服挑战任务{seq:02d}"
        row[cId2 - 1] = 0
        row[cType - 1] = "fixed_"
        row[cMinN - 1] = 1
        row[cMaxN - 1] = 1
        row[cItem - 1] = it
        row[cMin - 1] = num2
        row[cMax - 1] = num2
        row[cW - 1] = 10000
        ws.append(row)
        added += 1
for r in sorted(del_rows, reverse=True):
    ws.delete_rows(r)
    removed += 1
# 统一给新增行分配顺序ID
next_id = 400461
for r in range(5, ws.max_row + 1):
    if ws.cell(row=r, column=cID).value == "NEW":
        ws.cell(row=r, column=cID).value = next_id
        next_id += 1
print("新增行ID至", next_id - 1)
print(f"Drop: 改{changed} 增{added} 删{removed}")
wb.save(src)
shutil.copy2(src, REV / "Drop_after.json")
(REV / "plan.json").write_text(json.dumps(
    {"batch": "USERV15-CHG026", "created": datetime.now().isoformat(),
     "task_packs": len(auth), "drop_changed": changed, "drop_added": added,
     "drop_removed": removed}, ensure_ascii=False, indent=2), encoding="utf-8")
print("Drop 重写完成")
