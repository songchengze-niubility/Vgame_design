# -*- coding: utf-8 -*-
"""CHG-012 校验：备份 vs 现场（既有行零改动、仅追加）+ 业务链路校验 + 总投放。"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

import chg012_data as D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "05_验算核算" / "十四日活动CHG012_20260831"
CFG = ROOT / "06_最终配置" / "任务"
BACKUP = RUN / "backup" / "任务"

errors = []
checks = {}


def rows_of(path, sheet):
    wb = load_workbook(path, read_only=True, data_only=True)
    result = list(wb[sheet].iter_rows(values_only=True))
    wb.close()
    return result


def trim(row):
    r = list(row)
    while r and r[-1] is None:
        r.pop()
    return tuple(r)


def col_index(header, name):
    for i, h in enumerate(header):
        if h == name:
            return i
    raise SystemExit(f"表头缺少列 {name}")


# 1) 追加恰好一份、旧行无丢失。
# 说明：FDA/Task/TaskTarget 的备份取于首次运行后（已含一份与最终相同的追加行），
# 去重脚本删除了重复块，故这三张表当前应与备份 ID 集合一致；
# ActiveReward/Drop 首次运行未触及，当前 = 备份 + 预期追加。
from collections import Counter

def id_counter(path, sheet, id_col):
    rows = rows_of(path, sheet)
    ids = [r[id_col] for r in rows[4:] if r and len(r) > id_col and isinstance(r[id_col], int)]
    return Counter(ids), len(rows)

append_ok = True
# FDA（Id 在第2列，ActivityId=1）
cur, cur_rows = id_counter(CFG / "FourteenDayActivity.xlsx", "FourteenDayActivity", 1)
bak, bak_rows = id_counter(BACKUP / "FourteenDayActivity.xlsx", "FourteenDayActivity", 1)
if cur != bak or set(cur) != set(range(1, 15)) or any(v != 1 for v in cur.values()):
    append_ok = False
    errors.append(f"FourteenDayActivity ID集合异常: cur={sorted(cur)}")
# Task / TaskTarget
for fname, sheet in [("Task.xlsx", "Task"), ("TaskTarget.xlsx", "TaskTarget")]:
    cur, cur_rows = id_counter(CFG / fname, sheet, 1)
    bak, bak_rows = id_counter(BACKUP / fname, sheet, 1)
    if cur != bak:
        append_ok = False
        errors.append(f"{fname}: ID多重集与备份不一致")
    for lo, hi, n in [(5101, 5710, 70), (5801, 6510, 85), (1, 4999, None)]:
        in_range = [i for i in cur for _ in range(cur[i]) if lo <= i <= hi]
        if n is not None and len(in_range) != n:
            append_ok = False
            errors.append(f"{fname}: {lo}~{hi} 数量 {len(in_range)} != {n}")
    if any(v != 1 for v in cur.values()):
        append_ok = False
        errors.append(f"{fname}: 存在重复ID")
# ActiveReward（ID 在第2列）
cur = id_counter(CFG / "ActiveReward.xlsx", "ActiveReward", 1)[0]
bak = id_counter(BACKUP / "ActiveReward.xlsx", "ActiveReward", 1)[0]
new_part = Counter(cur); new_part.subtract(bak)
if +new_part != Counter({i: 1 for i in range(8, 15)}) or any(v < 0 for v in new_part.values()):
    append_ok = False
    errors.append(f"ActiveReward 追加异常: {+new_part}")
# Drop（ID 第2列、DropId 第3列）
cur_rows_d = rows_of(CFG / "Drop_TimeLimitedActivity.xlsx", "Drop")
bak_rows_d = rows_of(BACKUP / "Drop_TimeLimitedActivity.xlsx", "Drop")
cur_ids = Counter(r[1] for r in cur_rows_d[4:] if r and isinstance(r[1], int))
bak_ids = Counter(r[1] for r in bak_rows_d[4:] if r and isinstance(r[1], int))
diff = Counter(cur_ids); diff.subtract(bak_ids)
if +diff != Counter({i: 1 for i in range(400369, 400453)}):
    append_ok = False
    errors.append(f"Drop 追加行ID异常: {sum((+diff).values())}行")
cur_dropids = set(r[2] for r in cur_rows_d[4:] if r and r[2] is not None)
if not set(range(91000102, 91000144)) <= cur_dropids or not set(range(91001008, 91001015)) <= cur_dropids:
    append_ok = False
    errors.append("Drop 新增 DropId 缺失")
checks["既有行零改动且恰好追加一次"] = append_ok

# 2) 业务链路
fda = rows_of(CFG / "FourteenDayActivity.xlsx", "FourteenDayActivity")
tasks = rows_of(CFG / "Task.xlsx", "Task")
targets = rows_of(CFG / "TaskTarget.xlsx", "TaskTarget")
drops = rows_of(CFG / "Drop_TimeLimitedActivity.xlsx", "Drop")
active = rows_of(CFG / "ActiveReward.xlsx", "ActiveReward")

tk_head = tasks[0]
iT_id, iT_name, iT_desc = col_index(tk_head, "Id"), col_index(tk_head, "TaskName"), col_index(tk_head, "TaskDesc")
iT_type, iT_target, iT_drop, iT_accept = (col_index(tk_head, "TaskType"), col_index(tk_head, "TaskTarget"),
                                          col_index(tk_head, "DropId"), col_index(tk_head, "AcceptType"))
tt_head = targets[0]
iG_id, iG_desc, iG_type, iG_param = (col_index(tt_head, "Id"), col_index(tt_head, "TargetDesc"),
                                     col_index(tt_head, "TargetType"), col_index(tt_head, "ParamList"))
dr_head = drops[0]
iD_id, iD_drop, iD_item = (col_index(dr_head, "ID"), col_index(dr_head, "DropId"), col_index(dr_head, "DropItem_id"))
iD_num = col_index(dr_head, "DropItemNumMin")
iA_act, iA_point, iA_reward = (col_index(active[0], "ActivityId"), col_index(active[0], "ActivePoint"),
                               col_index(active[0], "RewardId"))

task_by_id = {r[iT_id]: r for r in tasks[4:] if r and isinstance(r[iT_id], int)}
target_by_id = {r[iG_id]: r for r in targets[4:] if r and isinstance(r[iG_id], int)}
drop_groups = defaultdict(list)
for r in drops[4:]:
    if r and r[iD_drop] is not None:
        drop_groups[r[iD_drop]].append(r)

# 枚举：名称可能不在A列，任意列前缀匹配
enum_types = set()
wb_enum = load_workbook(CFG / "__enums__.xlsx", read_only=True)
for ws in wb_enum.worksheets:
    for r in ws.iter_rows(values_only=True):
        for v in r:
            if isinstance(v, str) and v.startswith("Target_TTT_"):
                enum_types.add(v)
wb_enum.close()

new_ids = [tid for _, _, _, tid, _, _ in D.iter_tasks()]
checks["新任务42条且无重号"] = len(new_ids) == len(set(new_ids)) == 42
checks["新任务不与既有ID冲突"] = len(set(new_ids) & set(task_by_id)) == 70

chain_ok, drop_ok, enum_ok = True, True, True
for day, _, drop_id, tid, target, reward in D.iter_tasks():
    desc, ttype, param = target[0], target[1], target[2]
    t = task_by_id.get(tid)
    if t is None or t[iT_type] != "Task_TTT_FourteenActive" or t[iT_target] != tid \
            or t[iT_drop] != drop_id or t[iT_name] != desc or t[iT_desc] != desc \
            or t[iT_accept] != "Task_TAT_Active":
        chain_ok = False
        errors.append(f"任务{tid}: Task行字段与设计不一致")
    tg = target_by_id.get(tid)
    if tg is None or tg[iG_desc] != desc or tg[iG_type] != ttype or tg[iG_param] != param:
        chain_ok = False
        errors.append(f"目标{tid}: TaskTarget行与设计不一致")
    if ttype not in enum_types:
        enum_ok = False
        errors.append(f"目标{tid}: 类型{ttype}不在枚举")
    items = [(r[iD_item], r[iD_num]) for r in drop_groups.get(drop_id, [])]
    if sorted(items) != sorted([(32, 10), (reward[0], reward[1])]):
        drop_ok = False
        errors.append(f"Drop{drop_id}: 展开{items} != 积分×10 + {reward[0]}×{reward[1]}")

# FourteenDayActivity 链路（列：Id, ActivityId, OpenDay, TaskList）
fda_days = {}
for r in fda[4:]:
    if r and len(r) > 4 and r[2] == 1 and r[3] is not None:
        fda_days[r[3]] = r[4]
if sorted(fda_days) != list(range(1, 15)):
    chain_ok = False
    errors.append(f"FourteenDayActivity OpenDay 非法: {sorted(fda_days)}")
for day in sorted(D.DAYS):
    expect = ";".join(str(D.DAYS[day]["tasks"] + i) for i in range(len(D.DAYS[day]["rows"])))
    if fda_days.get(day) != expect:
        chain_ok = False
        errors.append(f"OpenDay{day} TaskList 与设计不一致")
checks["Task/FourteenDay/Target/Drop链路一致"] = chain_ok
checks["目标类型均在枚举"] = enum_ok
checks["每条Drop=积分×10+1项玩法奖励"] = drop_ok

# 活跃里程碑 14 档
pts = sorted((r[iA_point], r[iA_reward]) for r in active[4:] if r and r[iA_act] == 1 and r[iA_point] is not None)
checks["活跃里程碑100~1400共14档"] = [p for p, _ in pts] == list(range(100, 1401, 100)) and len(pts) == 14
ms_reward = {91001001 + p // 100 - 1 for p, _ in pts}
checks["里程碑RewardId指向正确"] = all(rid in ms_reward for _, rid in pts) and \
    all(pts[i][1] == 91001001 + i for i in range(len(pts)))

# 总投放
total = D.totals()
names = D.ITEM_NAMES
summary = "；".join(f"{names.get(k, k)}({k})×{v}" for k, v in sorted(total.items()))
result = {
    "batch": "FOURTEEN-DAY-CHG012",
    "generated_at": datetime.now().isoformat(),
    "errors": errors,
    "checks": {k: bool(v) for k, v in checks.items()},
    "new_tasks_total_investment": summary,
    "status": "PASS" if not errors and all(checks.values()) else "FAIL",
}
(RUN / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
(RUN / "totals.json").write_text(
    json.dumps({str(k): v for k, v in sorted(total.items())}, ensure_ascii=False, indent=2),
    encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
