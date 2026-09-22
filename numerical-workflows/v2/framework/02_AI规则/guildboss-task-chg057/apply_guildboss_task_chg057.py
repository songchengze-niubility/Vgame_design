# -*- coding: utf-8 -*-
"""CHG-057：公会BOSS个人累计挑战任务 QA 速查与源表对齐（2026-09-07 回源修正）。

SVN 正式配置 task/Task.xlsx 与 task/TaskTarget.xlsx 于 2026-09-07 更新：
Task 6001~6007 的 DropId 由 91000070 改回专属奖励包 70001001~70001007，
TaskTarget 门槛由 1/5/10/20/40/60/80 改回 1~7（任务名同步）。本脚本只改
04_数值文档/系统/11_外循环_任务.xlsx 中 TaskId 6001~6015 的 15 行：
- 6001~6007：D 列任务名对齐新口径，G 列 DropId 改为 x7000100N，J 列补启用备注；
- 6008~6015：G 列保持 x91000070 不变，J 列补 `##` 停用备注。

备份、plan.json、逐格校验与业务校验落在 05_验算核算/公会BOSS个人任务CHG057_20260907/。
不修改 04_数值文档/generation-manifest.json（全量重跑时自动刷新，与 CHG-011 口径一致）。
"""
import hashlib
import json
import shutil
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "05_验算核算" / "公会BOSS个人任务CHG057_20260907"

QA_FILE = ROOT / "04_数值文档" / "系统" / "11_外循环_任务.xlsx"
SHEET = "奖励与消耗"
SVN_TASK = Path(os.environ.get("VGAME_CONFIG_DATAS", "D:/Vgame/Config/GameConfig/Datas")) / "task" / "Task.xlsx"

# TaskId -> (任务名中的挑战次数, 期望DropId, 是否GuildBossTask启用档)
EXPECTED = {
    6001: (1, 70001001, True),
    6002: (2, 70001002, True),
    6003: (3, 70001003, True),
    6004: (4, 70001004, True),
    6005: (5, 70001005, True),
    6006: (6, 70001006, True),
    6007: (7, 70001007, True),
    6008: (100, 91000070, False),
    6009: (125, 91000070, False),
    6010: (150, 91000070, False),
    6011: (175, 91000070, False),
    6012: (200, 91000070, False),
    6013: (230, 91000070, False),
    6014: (260, 91000070, False),
    6015: (300, 91000070, False),
}
COL_D, COL_G, COL_J = 4, 7, 10
NOTE_ON = "公会BOSS个人任务启用档（GuildBossTask 6001~6007）；奖励包=元晶(2)+公会个人代币(15)固定值"
NOTE_OFF = "未启用档：GuildBossTask.xlsx 以 ## 停用；DropId 91000070 与开服挑战任务共用"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_svn_source():
    """校验 SVN 正式 Task.xlsx 当前值与 EXPECTED 一致，防止改错方向。"""
    wb = load_workbook(SVN_TASK, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    found = {}
    for row in ws.iter_rows(values_only=True):
        if row and row[1] is not None and str(row[1]).strip() in {str(k) for k in EXPECTED}:
            tid = int(str(row[1]).strip())
            found[tid] = (str(row[2]), int(str(row[15]).strip()))
    wb.close()
    errors = []
    for tid, (times, drop, _enabled) in EXPECTED.items():
        name, drop_id = found.get(tid, (None, None))
        if name is None:
            errors.append(f"SVN Task.xlsx 缺少 TaskId {tid}")
        elif not name.endswith(f"累计挑战{times}次"):
            errors.append(f"SVN TaskId {tid} 任务名 `{name}` 与期望次数 {times} 不符")
        elif drop_id != drop:
            errors.append(f"SVN TaskId {tid} DropId {drop_id} 与期望 {drop} 不符")
    return errors


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    backup_dir = RUN / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    svn_errors = verify_svn_source()
    if svn_errors:
        for e in svn_errors:
            print("SVN源校验失败:", e)
        raise SystemExit("SVN 正式源与 EXPECTED 不一致，拒绝修改 QA 文档")

    backup = backup_dir / QA_FILE.name
    shutil.copy2(QA_FILE, backup)

    wb = load_workbook(QA_FILE)
    ws = wb[SHEET]
    row_by_id = {}
    for r in range(5, ws.max_row + 1):
        v = ws.cell(row=r, column=COL_D).value
        if isinstance(v, str) and v.startswith("TaskId "):
            try:
                tid = int(v.split("｜")[0].split()[1])
            except (IndexError, ValueError):
                continue
            if tid in EXPECTED:
                row_by_id[tid] = r
    missing = sorted(set(EXPECTED) - set(row_by_id))
    if missing:
        raise SystemExit(f"QA 表未找到任务行 {missing}")
    overlap = sorted(set(row_by_id) - set(EXPECTED))
    if overlap:
        raise SystemExit(f"QA 表出现重复任务行 {overlap}")

    plan = {
        "batch": "GUILDBOSS-TASK-CHG057",
        "created": datetime.now().isoformat(),
        "file": str(QA_FILE),
        "backup": str(backup),
        "sha256_before": sha256(QA_FILE),
        "svn_source": str(SVN_TASK),
        "edits": [],
    }
    for tid in sorted(EXPECTED):
        times, drop, enabled = EXPECTED[tid]
        r = row_by_id[tid]
        new_name = f"TaskId {tid}｜Task_TTT_GuildBossTask｜聚集地首领累计挑战{times}次"
        new_drop = f"正式Task奖励：Task.DropId奖励包 x{drop}"
        note = NOTE_ON if enabled else NOTE_OFF
        for col, new in ((COL_D, new_name), (COL_G, new_drop), (COL_J, note)):
            cell = ws.cell(row=r, column=col)
            old = cell.value
            if old == new:
                continue
            plan["edits"].append({"row": r, "col": col, "task_id": tid, "old": old, "new": new})
            cell.value = new

    wb.save(QA_FILE)
    plan["sha256_after"] = sha256(QA_FILE)
    (RUN / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    # 逐格校验：备份 vs 现场，仅允许 plan 内单元格变化。
    expected = {(e["row"], e["col"]): e["new"] for e in plan["edits"]}
    old_wb = load_workbook(backup, read_only=True)
    new_wb = load_workbook(QA_FILE, read_only=True)
    old_rows = list(old_wb[SHEET].iter_rows(values_only=True))
    new_rows = list(new_wb[SHEET].iter_rows(values_only=True))
    old_wb.close()
    new_wb.close()
    errors = []
    if len(old_rows) != len(new_rows):
        errors.append(f"行数变化 {len(old_rows)}->{len(new_rows)}")
    else:
        for ri, (o, n) in enumerate(zip(old_rows, new_rows), 1):
            for ci, (ov, nv) in enumerate(zip(o, n), 1):
                if ov != nv and expected.get((ri, ci)) != nv:
                    errors.append(f"计划外变化 r{ri}c{ci}: {ov!r} -> {nv!r}")

    # 业务校验：15 行终值与 EXPECTED 全一致；启用/停用备注正确。
    wb2 = load_workbook(QA_FILE, read_only=True, data_only=True)
    ws2 = wb2[SHEET]
    rows2 = list(ws2.iter_rows(values_only=True))
    wb2.close()
    for tid, (times, drop, enabled) in EXPECTED.items():
        r = row_by_id[tid]
        d, g, j = rows2[r - 1][COL_D - 1], rows2[r - 1][COL_G - 1], rows2[r - 1][COL_J - 1]
        if d != f"TaskId {tid}｜Task_TTT_GuildBossTask｜聚集地首领累计挑战{times}次":
            errors.append(f"TaskId {tid} D列终值异常: {d!r}")
        if g != f"正式Task奖励：Task.DropId奖励包 x{drop}":
            errors.append(f"TaskId {tid} G列终值异常: {g!r}")
        want_note = NOTE_ON if enabled else NOTE_OFF
        if j != want_note:
            errors.append(f"TaskId {tid} J列备注异常: {j!r}")

    validation = {
        "batch": "GUILDBOSS-TASK-CHG057",
        "validated": datetime.now().isoformat(),
        "edits_applied": len(plan["edits"]),
        "unplanned_diffs": errors,
        "svn_source_check": "PASS（Task 6001~6007 DropId=70001001~70001007、任务名1~7次；6008~6015 DropId=91000070）",
        "status": "PASS" if not errors else "FAIL",
    }
    (RUN / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
