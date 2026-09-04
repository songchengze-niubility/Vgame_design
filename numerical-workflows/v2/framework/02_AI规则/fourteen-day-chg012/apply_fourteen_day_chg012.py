# -*- coding: utf-8 -*-
"""CHG-012：七日活动扩为14日，生成第 8~14 天 70 条任务并写入 06_最终配置 五张表。

批次协议：备份 → 追加行 → plan.json → 逐格校验（既有单元格零改动）→ 业务校验。
"""
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

import chg012_data as D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "05_验算核算" / "十四日活动CHG012_20260831"
CFG = ROOT / "06_最终配置" / "任务"

FILES = [
    "FourteenDayActivity.xlsx",
    "Task.xlsx",
    "TaskTarget.xlsx",
    "ActiveReward.xlsx",
    "Drop_TimeLimitedActivity.xlsx",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def col_index(header, name):
    for i, h in enumerate(header):
        if h == name:
            return i
    raise SystemExit(f"表头缺少列 {name}")


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "backup" / "任务").mkdir(parents=True, exist_ok=True)
    plan = {
        "batch": "FOURTEEN-DAY-CHG012",
        "created": datetime.now().isoformat(),
        "root": str(ROOT),
        "run": str(RUN),
        "files": [],
    }

    # --- 收割既有映射：TargetType -> TaskAccessList / UnlockId ---
    wb_tt_old = load_workbook(CFG / "TaskTarget.xlsx", read_only=True)
    tt_rows_old = list(wb_tt_old["TaskTarget"].iter_rows(values_only=True))
    tt_head = tt_rows_old[0]
    i_desc, i_type, i_param, i_hidden, i_access = (
        col_index(tt_head, "TargetDesc"), col_index(tt_head, "TargetType"),
        col_index(tt_head, "ParamList"), col_index(tt_head, "IsHidden"),
        col_index(tt_head, "TaskAccessList"),
    )
    type_access = Counter()
    old_targets = {}
    for r in tt_rows_old[4:]:
        if r and isinstance(r[1], int) and 5101 <= r[1] <= 5710:
            old_targets[r[1]] = r
            if r[i_type]:
                type_access[(r[i_type], r[i_access])] += 1
    wb_task_old = load_workbook(CFG / "Task.xlsx", read_only=True)
    task_rows_old = list(wb_task_old["Task"].iter_rows(values_only=True))
    tk_head = task_rows_old[0]
    i_tid, i_tname, i_tdesc, i_ttype, i_ttarget, i_unlock, i_drop, i_accept = (
        col_index(tk_head, "Id"), col_index(tk_head, "TaskName"), col_index(tk_head, "TaskDesc"),
        col_index(tk_head, "TaskType"), col_index(tk_head, "TaskTarget"),
        col_index(tk_head, "UnlockId"), col_index(tk_head, "DropId"), col_index(tk_head, "AcceptType"),
    )
    type_unlock = {}
    for r in task_rows_old[4:]:
        if r and isinstance(r[i_tid], int) and 5101 <= r[i_tid] <= 5710:
            t = old_targets.get(r[i_ttarget])
            if t is not None and t[i_type] not in type_unlock:
                type_unlock[t[i_type]] = r[i_unlock]
    # 新引入类型的回落值（肉鸽→4103 既有肉鸽解锁；邮票获得→沿用邮票副本解锁）
    fallback_unlock = {
        "Target_TTT_Roguelike_ChallengeTimes": 4103,
        "Target_TTT_Roguelike_MaxPassLevel": 4103,
        "Target_TTT_StrategyCard_Acquire": type_unlock.get("Target_TTT_StrategyCardLevel_PassMax"),
    }

    def access_of(ttype):
        best = [(n, a) for (t, a), n in type_access.items() if t == ttype and a is not None]
        return max(best)[1] if best else None

    def unlock_of(ttype):
        return type_unlock.get(ttype) or fallback_unlock.get(ttype)

    # --- 枚举校验准备 ---
    wb_enum = load_workbook(ROOT / "06_最终配置" / "任务" / "__enums__.xlsx", read_only=True)
    enum_types = set()
    for r in wb_enum.worksheets[0].iter_rows(values_only=True):
        if r and isinstance(r[0], str) and r[0].startswith("Target_TTT_"):
            enum_types.add(r[0])
    wb_enum.close()

    backups = {}
    counts = {}

    # --- FourteenDayActivity：追加 Id 8~14 ---
    rel = "FourteenDayActivity.xlsx"
    src = CFG / rel
    backups[rel] = RUN / "backup" / "任务" / rel
    shutil.copy2(src, backups[rel])
    wb = load_workbook(src)
    ws = wb.worksheets[0]
    head = [c.value for c in ws[1]]
    iId, iAct, iDay, iList = (col_index(head, "Id"), col_index(head, "ActivityId"),
                              col_index(head, "OpenDay"), col_index(head, "TaskList"))
    width = ws.max_column
    edits = []
    for day in sorted(D.DAYS):
        row = [None] * width
        row[iId] = day
        row[iAct] = 1
        row[iDay] = day
        row[iList] = ";".join(str(D.DAYS[day]["tasks"] + i) for i in range(10))
        ws.append(row)
        edits.append({"row": ws.max_row, "id": day})
    wb.save(src)
    counts[rel] = 7

    # --- Task + TaskTarget：各追加 70 行 ---
    rel = "TaskTarget.xlsx"
    src = CFG / rel
    backups[rel] = RUN / "backup" / "任务" / rel
    shutil.copy2(src, backups[rel])
    wb_tt = load_workbook(src)
    ws_tt = wb_tt["TaskTarget"]
    width_tt = ws_tt.max_column
    tt_append = []
    for _, task_id, _, _, target, _ in D.iter_tasks():
        desc, ttype, param = target[0], target[1], target[2]
        hint = target[3] if len(target) > 3 else None
        row = [None] * width_tt
        row[col_index(tt_head, "Id")] = task_id
        row[i_desc] = desc
        row[i_type] = ttype
        row[i_param] = param
        row[i_hidden] = 0
        row[i_access] = access_of(ttype)
        if col_index(tt_head, "Hint") is not None and hint:
            row[col_index(tt_head, "Hint")] = hint
        tt_append.append(row)
    for row in tt_append:
        ws_tt.append(row)
        edits.append({"row": ws_tt.max_row, "id": row[1]})
    wb_tt.save(src)
    counts[rel] = 70

    rel = "Task.xlsx"
    src = CFG / rel
    backups[rel] = RUN / "backup" / "任务" / rel
    shutil.copy2(src, backups[rel])
    wb_tk = load_workbook(src)
    ws_tk = wb_tk["Task"]
    width_tk = ws_tk.max_column
    tk_append = []
    for day, _, drop_id, tid, target, reward in D.iter_tasks():
        desc = target[0]
        row = [None] * width_tk
        row[i_tid] = tid
        row[i_tname] = desc
        row[i_tdesc] = desc
        row[i_ttype] = "Task_TTT_FourteenActive"
        row[i_ttarget] = tid
        row[i_unlock] = unlock_of(target[1])
        row[i_drop] = drop_id
        row[i_accept] = "Task_TAT_Active"
        tk_append.append(row)
    for row in tk_append:
        ws_tk.append(row)
        edits.append({"row": ws_tk.max_row, "id": row[i_tid]})
    wb_tk.save(src)
    counts[rel] = 70

    plan["files"].append({
        "file": "任务/FourteenDayActivity.xlsx", "edits_count": 7,
        "sha256_before": sha256(backups["FourteenDayActivity.xlsx"]),
        "sha256_after": sha256(CFG / "FourteenDayActivity.xlsx"),
    })
    plan["files"].append({
        "file": "任务/TaskTarget.xlsx", "edits_count": 70,
        "sha256_before": sha256(backups["TaskTarget.xlsx"]),
        "sha256_after": sha256(CFG / "TaskTarget.xlsx"),
    })
    plan["files"].append({
        "file": "任务/Task.xlsx", "edits_count": 70,
        "sha256_before": sha256(backups["Task.xlsx"]),
        "sha256_after": sha256(CFG / "Task.xlsx"),
    })

    # --- ActiveReward：追加 Id 8~14 ---
    rel = "ActiveReward.xlsx"
    src = CFG / rel
    backups[rel] = RUN / "backup" / "任务" / rel
    shutil.copy2(src, backups[rel])
    wb_ar = load_workbook(src)
    ws_ar = wb_ar.worksheets[0]
    head_ar = [c.value for c in next(ws_ar.iter_rows(max_row=1))]
    id_key = "ID" if "ID" in head_ar else "Id"
    iaId, iaAct, iaPoint, iReward = (col_index(head_ar, id_key), col_index(head_ar, "ActivityId"),
                                     col_index(head_ar, "ActivePoint"), col_index(head_ar, "RewardId"))
    width_ar = ws_ar.max_column
    for new_id, (point, reward_id, _) in zip(range(8, 15), D.MILESTONES):
        row = [None] * width_ar
        row[iaId] = new_id
        row[iaAct] = 1
        row[iaPoint] = point
        row[iReward] = reward_id
        ws_ar.append(row)
        edits.append({"row": ws_ar.max_row, "id": new_id})
    wb_ar.save(src)
    counts[rel] = 7
    plan["files"].append({
        "file": "任务/ActiveReward.xlsx", "edits_count": 7,
        "sha256_before": sha256(backups[rel]),
        "sha256_after": sha256(src),
    })

    # --- Drop_TimeLimitedActivity：任务 70×2 行 + 里程碑 7×2 行 ---
    rel = "Drop_TimeLimitedActivity.xlsx"
    src = CFG / rel
    backups[rel] = RUN / "backup" / "任务" / rel
    shutil.copy2(src, backups[rel])
    wb_dr = load_workbook(src)
    ws_dr = wb_dr["Drop"]
    head_dr = [c.value for c in ws_dr[1]]
    ci = {name: col_index(head_dr, name) for name in
          ("ID", "DropId", "DropName", "DropId2", "DropType", "DropMinNum", "DropMaxNum",
           "DropItem_id", "DropItemNumMin", "DropItemNumMax", "DropWeight", "ShowItemID")}
    # 模板行定位备注列（None 表头、形如 '-2' 的后缀）
    label_col = None
    for r in ws_dr.iter_rows(min_row=5, values_only=True):
        if r and r[ci["ID"]] == 400367:
            for j, v in enumerate(r):
                if isinstance(v, str) and v.endswith("-2"):
                    label_col = j
            template = list(r)
            break
    width_dr = ws_dr.max_column

    def drop_row(next_id, drop_id, name, item, num):
        row = [None] * width_dr
        row[ci["ID"]] = next_id
        row[ci["DropId"]] = drop_id
        if label_col is not None:
            row[label_col] = f"{name}-{item}"
        row[ci["DropName"]] = name
        row[ci["DropId2"]] = 0
        row[ci["DropType"]] = "fixed_"
        row[ci["DropMinNum"]] = 1
        row[ci["DropMaxNum"]] = 1
        row[ci["DropItem_id"]] = item
        row[ci["DropItemNumMin"]] = num
        row[ci["DropItemNumMax"]] = num
        row[ci["DropWeight"]] = 10000
        return row

    next_id = D.DROP_ROW_ID_START
    name_by_task = {}
    for day_key, spec in D.DAYS.items():
        for i, (t, _, _) in enumerate(spec["rows"]):
            name_by_task[t] = f"开服挑战第{day_key}天任务{i + 1:02d}"
    for _, drop_id, _, tid, _, reward in D.iter_tasks():
        name = name_by_task[tid]
        ws_dr.append(drop_row(next_id, drop_id, name, D.SCORE_ITEM, D.SCORE_NUM))
        next_id += 1
        ws_dr.append(drop_row(next_id, drop_id, name, reward[0], reward[1]))
        next_id += 1
    for point, reward_id, (item, num, iname) in D.MILESTONES:
        name = f"开服挑战{point}积分奖励"
        ws_dr.append(drop_row(next_id, reward_id, name, 2, 500))
        next_id += 1
        ws_dr.append(drop_row(next_id, reward_id, name, item, num))
        next_id += 1
    wb_dr.save(src)
    counts[rel] = 154
    plan["files"].append({
        "file": "任务/Drop_TimeLimitedActivity.xlsx", "edits_count": 154,
        "sha256_before": sha256(backups[rel]),
        "sha256_after": sha256(src),
    })

    (RUN / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print("appended:", counts, "| drop rows:", next_id - D.DROP_ROW_ID_START)
    print("unlock mapping:", {k: v for k, v in sorted(type_unlock.items())})
    print("fallbacks:", fallback_unlock)
    print("access mapping sample:", dict(sorted(set(type_access.elements()))))


if __name__ == "__main__":
    main()
