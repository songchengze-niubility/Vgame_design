# -*- coding: utf-8 -*-
"""CHG-013 修订一（评审反馈）：
A) 第1~7天竞技场分数线(5105~5705)改为累计挑战次数线；5108/5210 与新线重复，替换为BOSS类任务。
B) 第8~14天由10条/天改为6条/天（42条），删除旧70条按新数据重写，TaskId/DropId 重新连续编号。
只改 06_最终配置；SVN 未动。
"""
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

import chg012_data as D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "05_验算核算" / "十四日活动CHG012_20260831"
CFG = ROOT / "06_最终配置" / "任务"

# A) 第1~7天改写映射：task_id -> (新描述, 新类型, 新参数, 玩法奖励或None不变)
D17_EDITS = {
    5105: ("累计挑战竞技场3次", "Target_TTT_Arena_Challenge_Times", "0,3", None),
    5205: ("累计挑战竞技场6次", "Target_TTT_Arena_Challenge_Times", "0,6", None),
    5305: ("累计挑战竞技场10次", "Target_TTT_Arena_Challenge_Times", "0,10", None),
    5405: ("累计挑战竞技场14次", "Target_TTT_Arena_Challenge_Times", "0,14", None),
    5505: ("累计挑战竞技场18次", "Target_TTT_Arena_Challenge_Times", "0,18", None),
    5605: ("累计挑战竞技场22次", "Target_TTT_Arena_Challenge_Times", "0,22", None),
    5705: ("累计挑战竞技场26次", "Target_TTT_Arena_Challenge_Times", "0,26", None),
    5108: ("累计通关BOSS挑战1次", "Target_TTT_Type_LevelClearNum", "23,1", (106, 1, "旅券")),
    5210: ("累计击败BOSS敌人6个", "Target_TTT_BossMonster_Kill_Times", "0,6", (102, 5, "高阶记录盘")),
}


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def col_index(header, name):
    for i, h in enumerate(header):
        if h == name:
            return i
    raise SystemExit(f"表头缺少列 {name}")


NEW_IDS = set()
for _lo in (5801, 5901, 6101, 6201, 6301, 6401, 6501):
    NEW_IDS.update(range(_lo, _lo + 10))


def main():
    rev_dir = RUN / "rev1-CHG013"
    (rev_dir / "backup").mkdir(parents=True, exist_ok=True)
    plan = {"batch": "ARENA-COUNT-CHG013", "created": datetime.now().isoformat(), "files": []}

    def backup(rel):
        src = CFG / rel
        dst = rev_dir / "backup" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return src, dst

    # ---------- A1: Task 9 行 + TaskTarget 9 行 ----------
    for rel, sheet in [("Task.xlsx", "Task"), ("TaskTarget.xlsx", "TaskTarget")]:
        src, bak = backup(rel)
        wb = load_workbook(src)
        ws = wb[sheet]
        head = [c.value for c in next(ws.iter_rows(max_row=1))]
        iId = col_index(head, "Id")
        iDesc = col_index(head, "TaskDesc" if sheet == "Task" else "TargetDesc")
        iName = col_index(head, "TaskName") if sheet == "Task" else None
        iType = col_index(head, "TaskType") if sheet == "Task" else col_index(head, "TargetType")
        iParam = col_index(head, "ParamList") if sheet == "TaskTarget" else None
        n = 0
        for row in range(5, ws.max_row + 1):
            tid = ws.cell(row=row, column=iId + 1).value
            if tid in D17_EDITS:
                desc, ttype, param, _ = D17_EDITS[tid]
                ws.cell(row=row, column=iDesc + 1).value = desc
                if iName:
                    ws.cell(row=row, column=iName + 1).value = desc
                ws.cell(row=row, column=iType + 1).value = ttype
                if iParam:
                    ws.cell(row=row, column=iParam + 1).value = param
                n += 1
        wb.save(src)
        plan["files"].append({"file": rel, "cells_changed": n,
                              "sha256_before": sha256(bak), "sha256_after": sha256(src)})
        print(f"{rel}: 改写 {n} 行")

    # ---------- A2: Drop 91000008 / 91000020 玩法奖励替换 ----------
    rel = "Drop_TimeLimitedActivity.xlsx"
    src, bak = backup(rel)
    wb = load_workbook(src)
    ws = wb["Drop"]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    iDrop = col_index(head, "DropId")
    iItem = col_index(head, "DropItem_id")
    iMin = col_index(head, "DropItemNumMin")
    iMax = col_index(head, "DropItemNumMax")
    iNameC = col_index(head, "DropName")
    changes = {91000008: (106, 1, "旅券"), 91000020: (102, 5, "高阶记录盘")}
    n = 0
    for row in range(5, ws.max_row + 1):
        did = ws.cell(row=row, column=iDrop + 1).value
        if did in changes and ws.cell(row=row, column=iItem + 1).value != 32:
            item, num, name = changes[did]
            ws.cell(row=row, column=iItem + 1).value = item
            ws.cell(row=row, column=iMin + 1).value = num
            ws.cell(row=row, column=iMax + 1).value = num
            old = ws.cell(row=row, column=iNameC + 1).value or ""
            ws.cell(row=row, column=iNameC + 1).value = old.replace("奖励-19", f"奖励-{item}")
            n += 1
    wb.save(src)
    plan["files"].append({"file": rel, "cells_changed": n,
                          "sha256_before": sha256(bak), "sha256_after": sha256(src)})
    print(f"Drop 玩法奖励替换: {n} 行")

    # ---------- B: 第8~14天删除旧70条、重写42条 ----------
    # B1: Task 删除旧行
    rel = "Task.xlsx"
    src = CFG / rel
    wb = load_workbook(src)
    ws = wb["Task"]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    iId, iName, iDesc, iType, iTarget, iUnlock, iDropId, iAccept = (
        col_index(head, "Id"), col_index(head, "TaskName"), col_index(head, "TaskDesc"),
        col_index(head, "TaskType"), col_index(head, "TaskTarget"),
        col_index(head, "UnlockId"), col_index(head, "DropId"), col_index(head, "AcceptType"))
    old_ids = {t for t, _, _, _, _ in [(a, b, c, dd, e) for a, (b, c, dd, e) in []]}  # noqa
    to_delete = []
    for row in range(5, ws.max_row + 1):
        tid = ws.cell(row=row, column=iId + 1).value
        if isinstance(tid, int) and (5801 <= tid <= 5810 or 5901 <= tid <= 5910
                or 6101 <= tid <= 6110 or 6201 <= tid <= 6210 or 6301 <= tid <= 6310
                or 6401 <= tid <= 6410 or 6501 <= tid <= 6510):
            to_delete.append(row)
    for row in reversed(to_delete):
        ws.delete_rows(row)
    print(f"Task: 删除第8~14天旧行 {len(to_delete)}")
    # 收割 unlock 映射（同 apply）
    wb_tt = load_workbook(CFG / "TaskTarget.xlsx", read_only=True)
    tt_rows = list(wb_tt["TaskTarget"].iter_rows(values_only=True))
    wb_tt.close()
    tt_head = tt_rows[0]
    iG_id, iG_type = col_index(tt_head, "Id"), col_index(tt_head, "TargetType")
    type_unlock = {}
    for r in tt_rows[4:]:
        if r and isinstance(r[iG_id], int) and 5101 <= r[iG_id] <= 5710:
            type_unlock[r[iG_type]] = None
    wb_tk_ro = load_workbook(CFG / "Task.xlsx", read_only=True)
    tk_rows = list(wb_tk_ro["Task"].iter_rows(values_only=True))
    wb_tk_ro.close()
    tk_head = tk_rows[0]
    for r in tk_rows[4:]:
        if r and isinstance(r[col_index(tk_head, "Id")], int) and 5101 <= r[col_index(tk_head, "Id")] <= 5710:
            t_type = None
            tt_id = r[col_index(tk_head, "TaskTarget")]
            for rr in tt_rows[4:]:
                if rr and rr[iG_id] == tt_id:
                    t_type = rr[iG_type]
                    break
            if t_type and t_type not in type_unlock or type_unlock.get(t_type) is None:
                type_unlock[t_type] = r[col_index(tk_head, "UnlockId")]
    fallback = {"Target_TTT_Roguelike_ChallengeTimes": 4103, "Target_TTT_Roguelike_MaxPassLevel": 4103}
    # 追加新 42 行
    appended = 0
    for day, _, drop_id, tid, target, reward in D.iter_tasks():
        desc = target[0]
        row = [None] * ws.max_column
        row[iId] = tid
        row[iName] = desc
        row[iDesc] = desc
        row[iType] = "Task_TTT_FourteenActive"
        row[iTarget] = tid
        row[iUnlock] = type_unlock.get(target[1]) or fallback.get(target[1])
        row[iDropId] = drop_id
        row[iAccept] = "Task_TAT_Active"
        ws.append(row)
        appended += 1
    wb.save(src)
    print(f"Task: 追加新行 {appended}")

    # B2: TaskTarget 删除+追加
    rel = "TaskTarget.xlsx"
    src = CFG / rel
    wb = load_workbook(src)
    ws = wb["TaskTarget"]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    iGId = col_index(head, "Id")
    iGDesc = col_index(head, "TargetDesc")
    iGType = col_index(head, "TargetType")
    iGParam = col_index(head, "ParamList")
    iGHidden = col_index(head, "IsHidden")
    iGAccess = col_index(head, "TaskAccessList")
    iGHint = col_index(head, "Hint")
    to_delete = [row for row in range(5, ws.max_row + 1)
                 if isinstance(ws.cell(row=row, column=iGId + 1).value, int)
                 and ws.cell(row=row, column=iGId + 1).value in NEW_IDS]
    for row in reversed(to_delete):
        ws.delete_rows(row)
    print(f"TaskTarget: 删除旧行 {len(to_delete)}")
    # access 映射
    type_access = Counter()
    for r in tt_rows[4:]:
        if r and isinstance(r[iG_id], int) and 5101 <= r[iG_id] <= 5710 and r[iG_type]:
            type_access[(r[iG_type], r[col_index(tt_head, "TaskAccessList")])] += 1
    for day, _, drop_id, tid, target, reward in D.iter_tasks():
        desc, ttype, param = target[0], target[1], target[2]
        hint = target[3] if len(target) > 3 else None
        best = [(n_, a_) for (t_, a_), n_ in type_access.items() if t_ == ttype and a_ is not None]
        row = [None] * ws.max_column
        row[iGId] = tid
        row[iGDesc] = desc
        row[iGType] = ttype
        row[iGParam] = param
        row[iGHidden] = 0
        row[iGAccess] = max(best)[1] if best else None
        if hint and iGHint is not None:
            row[iGHint] = hint
        ws.append(row)
    wb.save(src)
    print("TaskTarget: 追加新行 42")

    # B3: FourteenDayActivity TaskList 重写（days 8~14 各6条）
    rel = "FourteenDayActivity.xlsx"
    src = CFG / rel
    wb = load_workbook(src)
    ws = wb.worksheets[0]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    iDay, iList = col_index(head, "OpenDay"), col_index(head, "TaskList")
    n = 0
    for row in range(5, ws.max_row + 1):
        day = ws.cell(row=row, column=iDay + 1).value
        if day in D.DAYS:
            spec = D.DAYS[day]
            ws.cell(row=row, column=iList + 1).value = ";".join(
                str(spec["tasks"] + i) for i in range(len(spec["rows"])))
            n += 1
    wb.save(src)
    print(f"FourteenDayActivity: 重写 {n} 天 TaskList")

    # B4: Drop 删除 400369~400522，追加新 84 行
    rel = "Drop_TimeLimitedActivity.xlsx"
    src = CFG / rel
    wb = load_workbook(src)
    ws = wb["Drop"]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    iID = col_index(head, "ID")
    iDDrop = col_index(head, "DropId")
    iDItem = col_index(head, "DropItem_id")
    iDMin = col_index(head, "DropItemNumMin")
    iDMax = col_index(head, "DropItemNumMax")
    iDName = col_index(head, "DropName")
    iDId2 = col_index(head, "DropId2")
    iDType = col_index(head, "DropType")
    iDMinN = col_index(head, "DropMinNum")
    iDMaxN = col_index(head, "DropMaxNum")
    iDWeight = col_index(head, "DropWeight")
    label_col = None
    template = None
    for row in range(5, ws.max_row + 1):
        rid = ws.cell(row=row, column=iID + 1).value
        if rid == 400369:
            template = [ws.cell(row=row, column=c + 1).value for c in range(ws.max_column)]
            for j, v in enumerate(template):
                if isinstance(v, str) and v.endswith("-32"):
                    label_col = j
            break
    to_delete = [row for row in range(5, ws.max_row + 1)
                 if isinstance(ws.cell(row=row, column=iID + 1).value, int)
                 and 400369 <= ws.cell(row=row, column=iID + 1).value <= 400522]
    for row in reversed(to_delete):
        ws.delete_rows(row)
    print(f"Drop: 删除旧行 {len(to_delete)}")

    def drop_row(next_id, drop_id, name, item, num):
        row = [None] * ws.max_column
        row[iID] = next_id
        row[iDDrop] = drop_id
        if label_col is not None:
            row[label_col] = f"{name}-{item}"
        row[iDName] = name
        row[iDId2] = 0
        row[iDType] = "fixed_"
        row[iDMinN] = 1
        row[iDMaxN] = 1
        row[iDItem] = item
        row[iDMin] = num
        row[iDMax] = num
        row[iDWeight] = 10000
        return row

    next_id = 400369
    for day in sorted(D.DAYS):
        spec = D.DAYS[day]
        for i, (tid, target, reward) in enumerate(spec["rows"]):
            name = f"开服挑战第{day}天任务{i + 1:02d}"
            drop_id = spec["drop"] + i
            ws.append(drop_row(next_id, drop_id, name, D.SCORE_ITEM, D.SCORE_NUM))
            next_id += 1
            ws.append(drop_row(next_id, drop_id, name, reward[0], reward[1]))
            next_id += 1
    wb.save(src)
    print(f"Drop: 追加新行 {next_id - 400369}")

    (rev_dir / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print("rev1 done")


if __name__ == "__main__":
    main()
