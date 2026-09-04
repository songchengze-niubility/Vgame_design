# -*- coding: utf-8 -*-
"""CHG-014 修订六：第8~14天改为 固定4条（储能/映射/爬塔/高难）+ 轮换2条（邮票/BOSS难度/行商/肉鸽）。

TaskId/DropId 沿用各天01~06与91000102~91000143，FourteenDayActivity TaskList 不变。
只改 06_最终配置；SVN 未动。
"""
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

NEW_IDS = set()
for _lo in (5801, 5901, 6101, 6201, 6301, 6401, 6501):
    NEW_IDS.update(range(_lo, _lo + 10))

FALLBACK_UNLOCK = {
    "Target_TTT_BossChallenge_AnyBossDifficulty": 4105,
    "Target_TTT_Roguelike_ChallengeTimes": 4103,
    "Target_TTT_Roguelike_MaxPassLevel": 4103,
}


def col_index(header, name):
    for i, h in enumerate(header):
        if h == name:
            return i
    raise SystemExit(f"表头缺少列 {name}")


def main():
    rev_dir = RUN / "rev6-CHG018"
    (rev_dir / "backup").mkdir(parents=True, exist_ok=True)

    # 收割既有映射（前7天）
    wb_tt = load_workbook(CFG / "TaskTarget.xlsx", read_only=True)
    tt_rows = list(wb_tt["TaskTarget"].iter_rows(values_only=True))
    wb_tt.close()
    tt_head = tt_rows[0]
    iG_id, iG_type = col_index(tt_head, "Id"), col_index(tt_head, "TargetType")
    iG_desc = col_index(tt_head, "TargetDesc")
    iG_param = col_index(tt_head, "ParamList")
    iG_hidden = col_index(tt_head, "IsHidden")
    iG_access = col_index(tt_head, "TaskAccessList")
    iG_hint = col_index(tt_head, "Hint")
    type_access = Counter()
    for r in tt_rows[4:]:
        if r and isinstance(r[iG_id], int) and 5101 <= r[iG_id] <= 5710 and r[iG_type]:
            type_access[(r[iG_type], r[iG_access])] += 1
    wb_tk = load_workbook(CFG / "Task.xlsx", read_only=True)
    tk_rows = list(wb_tk["Task"].iter_rows(values_only=True))
    wb_tk.close()
    tk_head = tk_rows[0]
    iT_id = col_index(tk_head, "Id")
    type_unlock = {}
    for r in tk_rows[4:]:
        if r and isinstance(r[iT_id], int) and 5101 <= r[iT_id] <= 5710:
            ttid = r[col_index(tk_head, "TaskTarget")]
            ttype = next((rr[iG_type] for rr in tt_rows[4:] if rr and rr[iG_id] == ttid), None)
            if ttype and type_unlock.get(ttype) is None:
                type_unlock[ttype] = r[col_index(tk_head, "UnlockId")]

    def access_of(ttype):
        best = [(n_, a_) for (t_, a_), n_ in type_access.items() if t_ == ttype and a_ is not None]
        return max(best)[1] if best else None

    # Task：删旧42、追新42
    src = CFG / "Task.xlsx"
    shutil.copy2(src, rev_dir / "backup" / "Task.xlsx")
    wb = load_workbook(src)
    ws = wb["Task"]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    iId = col_index(head, "Id")
    iName = col_index(head, "TaskName")
    iDesc = col_index(head, "TaskDesc")
    iType = col_index(head, "TaskType")
    iTarget = col_index(head, "TaskTarget")
    iUnlock = col_index(head, "UnlockId")
    iDropId = col_index(head, "DropId")
    iAccept = col_index(head, "AcceptType")
    to_delete = [row for row in range(5, ws.max_row + 1)
                 if ws.cell(row=row, column=iId + 1).value in NEW_IDS]
    for row in reversed(to_delete):
        ws.delete_rows(row)
    for day, _, drop_id, tid, target, reward in D.iter_tasks():
        desc = target[0]
        row = [None] * ws.max_column
        row[iId] = tid
        row[iName] = desc
        row[iDesc] = desc
        row[iType] = "Task_TTT_FourteenActive"
        row[iTarget] = tid
        row[iUnlock] = type_unlock.get(target[1]) or FALLBACK_UNLOCK.get(target[1])
        row[iDropId] = drop_id
        row[iAccept] = "Task_TAT_Active"
        ws.append(row)
    wb.save(src)
    print(f"Task: 删{len(to_delete)} 追42")

    # TaskTarget：删旧42、追新42
    src = CFG / "TaskTarget.xlsx"
    shutil.copy2(src, rev_dir / "backup" / "TaskTarget.xlsx")
    wb = load_workbook(src)
    ws = wb["TaskTarget"]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    iGId = col_index(head, "Id")
    to_delete = [row for row in range(5, ws.max_row + 1)
                 if ws.cell(row=row, column=iGId + 1).value in NEW_IDS]
    for row in reversed(to_delete):
        ws.delete_rows(row)
    for day, _, drop_id, tid, target, reward in D.iter_tasks():
        desc, ttype, param = target[0], target[1], target[2]
        hint = target[3] if len(target) > 3 else None
        row = [None] * ws.max_column
        row[iGId] = tid
        row[iG_desc] = desc
        row[iG_type] = ttype
        row[iG_param] = param
        row[iG_hidden] = 0
        row[iG_access] = access_of(ttype)
        if hint and iG_hint is not None:
            row[iG_hint] = hint
        ws.append(row)
    wb.save(src)
    print(f"TaskTarget: 删{len(to_delete)} 追42")

    # Drop：删 400369~400452，追新84
    src = CFG / "Drop_TimeLimitedActivity.xlsx"
    shutil.copy2(src, rev_dir / "backup" / "Drop_TimeLimitedActivity.xlsx")
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
                 and 400369 <= ws.cell(row=row, column=iID + 1).value <= 400452]
    for row in reversed(to_delete):
        ws.delete_rows(row)

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
    print(f"Drop: 删{len(to_delete)} 追{next_id - 400369}")

    (rev_dir / "plan.json").write_text(
        json.dumps({"batch": "REALTYPE-CHG018", "created": datetime.now().isoformat()},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    


if __name__ == "__main__":
    main()

    # CHG-018：5209/5210/5310 换真实类型
    d18 = {
        5209: ("8件装备达到15级", "Target_TTT_SpecialEquipmentLevelUp_Num", "15,8"),
        5210: ("领取1次爬塔挂机奖励", "Target_TTT_RvDevice_IdleCollect_Times", "0,1"),
        5310: ("4件装备达到20级", "Target_TTT_SpecialEquipmentLevelUp_Num", "20,4"),
    }
    for rel, sheet in [("Task.xlsx", "Task"), ("TaskTarget.xlsx", "TaskTarget")]:
        src = CFG / rel
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
            if tid in d18:
                desc, ttype, param = d18[tid]
                ws.cell(row=row, column=iDesc + 1).value = desc
                if iName:
                    ws.cell(row=row, column=iName + 1).value = desc
                ws.cell(row=row, column=iType + 1).value = ttype
                if iParam:
                    ws.cell(row=row, column=iParam + 1).value = param
                n += 1
        wb.save(src)
        print(f"CHG018 {rel}: 改写 {n} 行")

    print("rev2 done")
