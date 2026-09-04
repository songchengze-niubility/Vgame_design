# -*- coding: utf-8 -*-
"""CHG-010 SVN 落表：把与 06 相同的 16 格竞技场分数改动同步到 ${VGAME_CONFIG_DATAS}/task。

列位置按表头名定位（SVN Task.xlsx 比 06 多 Target 列，坐标不通用）。
备份与校验落在 05_验算核算/七日竞技场分数CHG010_20260831/ 的 *-svn 产物。
只改工作副本，不执行 svn commit。
"""
import hashlib
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "05_验算核算" / "七日竞技场分数CHG010_20260831"
SVN_TASK_DIR = Path(os.environ.get("VGAME_CONFIG_DATAS") or str(
        Path(__file__).resolve().parents[5].parent / "Vgame" / "Config" / "GameConfig" / "Datas"
    )) / "task"

CHANGES = {
    5105: ("竞技场历史最高达到1100分", 1100),
    5205: ("竞技场历史最高达到1200分", 1200),
    5605: ("竞技场历史最高达到1600分", 1600),
    5705: ("竞技场历史最高达到1700分", 1700),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def col_of(header, name):
    for idx, h in enumerate(header, 1):
        if h == name:
            return idx
    raise SystemExit(f"表头缺少列 {name}")


def main():
    (RUN / "backup-svn" / "task").mkdir(parents=True, exist_ok=True)

    specs = [
        ("Task.xlsx", "Task", {"TaskName": None, "TaskDesc": None}),
        ("TaskTarget.xlsx", "TaskTarget", {"TargetDesc": None, "ParamList": None}),
    ]

    plan = {
        "batch": "ARENA-SCORE-CHG010-SVN",
        "created": datetime.now().isoformat(),
        "svn_dir": str(SVN_TASK_DIR),
        "files": [],
    }

    for filename, sheet, fields in specs:
        src = SVN_TASK_DIR / filename
        backup = RUN / "backup-svn" / "task" / filename
        shutil.copy2(src, backup)

        wb = load_workbook(src)
        ws = wb[sheet]
        rows = list(ws.iter_rows(values_only=True))
        header = rows[0]
        id_col = col_of(header, "Id")
        row_by_id = {}
        for ri, r in enumerate(rows[4:], 5):
            if r and r[id_col - 1] in CHANGES:
                row_by_id[r[id_col - 1]] = ri
        missing = sorted(set(CHANGES) - set(row_by_id))
        if missing:
            raise SystemExit(f"{filename}: 未找到目标行 {missing}")

        file_plan = {
            "file": f"task/{filename}",
            "source": str(src),
            "backup": str(backup),
            "sha256_before": sha256(src),
            "edits": [],
        }
        for tid in sorted(CHANGES):
            name, score = CHANGES[tid]
            values = {}
            if "TaskName" in fields:
                values["TaskName"] = name
            if "TaskDesc" in fields:
                values["TaskDesc"] = name
            if "TargetDesc" in fields:
                values["TargetDesc"] = name
            if "ParamList" in fields:
                values["ParamList"] = f"0,{score}"
            for field, new in values.items():
                ci = col_of(header, field)
                cell = ws.cell(row=row_by_id[tid], column=ci)
                old = cell.value
                if old == new:
                    continue
                file_plan["edits"].append(
                    {
                        "sheet": sheet,
                        "row": row_by_id[tid],
                        "col": ci,
                        "field": field,
                        "task_id": tid,
                        "old": old,
                        "new": new,
                    }
                )
                cell.value = new

        plan["files"].append(file_plan)
        wb.save(src)
        file_plan["sha256_after"] = sha256(src)

    (RUN / "plan-svn.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 逐格校验：备份 vs 现场，仅允许 plan 内单元格变化。
    expected = defaultdict(dict)
    for f in plan["files"]:
        for e in f["edits"]:
            expected[(f["file"], e["sheet"])][(e["row"], e["col"])] = e["new"]

    errors = []
    for filename, sheet, _ in specs:
        rel = f"task/{filename}"
        old_wb = load_workbook(RUN / "backup-svn" / "task" / filename, read_only=True)
        new_wb = load_workbook(SVN_TASK_DIR / filename, read_only=True)
        old_rows = list(old_wb[sheet].iter_rows(values_only=True))
        new_rows = list(new_wb[sheet].iter_rows(values_only=True))
        if len(old_rows) != len(new_rows):
            errors.append(f"{rel}: 行数变化 {len(old_rows)}->{len(new_rows)}")
            continue
        allow = expected.get((rel, sheet), {})
        for ri, (old_r, new_r) in enumerate(zip(old_rows, new_rows), 1):
            for ci, (old_v, new_v) in enumerate(zip(old_r, new_r), 1):
                if old_v != new_v and allow.get((ri, ci)) != new_v:
                    errors.append(
                        f"{rel}!{sheet}!{get_column_letter(ci)}{ri}: "
                        f"{old_v!r}->{new_v!r} 不在计划内"
                    )
        old_wb.close()
        new_wb.close()

    # 业务校验：9 天竞技场分数线、类型、解锁与奖励。
    wb_task = load_workbook(SVN_TASK_DIR / "Task.xlsx", read_only=True, data_only=True)
    wb_tt = load_workbook(SVN_TASK_DIR / "TaskTarget.xlsx", read_only=True, data_only=True)
    t_rows = list(wb_task["Task"].iter_rows(values_only=True))
    tt_rows = list(wb_tt["TaskTarget"].iter_rows(values_only=True))
    th, tth = t_rows[0], tt_rows[0]
    unlock_c, drop_c, target_c = col_of(th, "UnlockId"), col_of(th, "DropId"), col_of(th, "TaskTarget")
    param_c = col_of(tth, "ParamList")
    param = {r[1]: r[param_c - 1] for r in tt_rows[4:] if r and r[1] is not None}
    days, expected_drop = {}, {1: "91000005", 2: "91000015", 3: "91000025",
                               4: "91000035", 5: "91000045", 6: "91000055", 7: "91000065"}
    for r in t_rows[4:]:
        tid = r[1]
        if isinstance(tid, int) and 5105 <= tid <= 5705 and tid % 100 == 5:
            days[tid // 100 - 50] = {
                "param": param.get(tid),
                "unlock": r[unlock_c - 1],
                "drop": str(r[drop_c - 1]),
            }
    score_ok = all(
        days[d]["param"] == f"0,{1100 + (d - 1) * 100}" for d in days
    )
    meta_ok = all(
        days[d]["unlock"] == 4112 and days[d]["drop"] == expected_drop[d] for d in days
    )
    wb_task.close()
    wb_tt.close()

    result = {
        "batch": "ARENA-SCORE-CHG010-SVN",
        "generated_at": datetime.now().isoformat(),
        "cell_diff_outside_plan": errors,
        "business_checks": {
            "七日竞技场分数线": {f"第{d}天": days[d]["param"] for d in sorted(days)},
            "分数线符合1100~1700": score_ok,
            "解锁与奖励不变": meta_ok,
        },
        "status": "PASS" if not errors and score_ok and meta_ok else "FAIL",
    }
    (RUN / "validation-svn.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
