# -*- coding: utf-8 -*-
"""CHG-012 SVN 落表：把 06 已验证的第 8~14 天 70 条任务同步到 SVN 工作副本。

涉及：
- task/Task.xlsx、task/TaskTarget.xlsx（追加 70 行，列按表头名定位，SVN Task 比 06 多 Target 列）
- Activity/FourteenDayActivity.xlsx（追加 OpenDay 8~14）
- Activity/ActiveReward.xlsx（追加 Id 8~14）
- Drop/Drop_TimeLimitedActivity.xlsx（追加 154 行）

执行前请确认用户已授权；只改工作副本，不执行 svn commit。
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

import chg012_data as D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "05_验算核算" / "十四日活动CHG012_20260831"
import os
DATAS = Path(os.environ.get("VGAME_CONFIG_DATAS") or str(
        Path(__file__).resolve().parents[5].parent / "Vgame" / "Config" / "GameConfig" / "Datas"
    ))

SVN_FILES = [
    (DATAS / "task" / "Task.xlsx", "Task", RUN / "06_最终配置" / "任务" / "Task.xlsx"),
    (DATAS / "task" / "TaskTarget.xlsx", "TaskTarget", ROOT / "06_最终配置" / "任务" / "TaskTarget.xlsx"),
    (DATAS / "Activity" / "FourteenDayActivity.xlsx", "FourteenDayActivity", ROOT / "06_最终配置" / "任务" / "FourteenDayActivity.xlsx"),
    (DATAS / "Activity" / "ActiveReward.xlsx", "ActiveReward", ROOT / "06_最终配置" / "任务" / "ActiveReward.xlsx"),
    (DATAS / "Drop" / "Drop_TimeLimitedActivity.xlsx", "Drop", ROOT / "06_最终配置" / "任务" / "Drop_TimeLimitedActivity.xlsx"),
]


def col_index(header, name):
    for i, h in enumerate(header):
        if h == name:
            return i
    raise SystemExit(f"表头缺少列 {name}")


def append_rows_from_06():
    """以 06 表中 CHG-012 的追加行（与 SVN 同名列对齐）为源，写入 SVN 表。"""
    import shutil, hashlib
    backup_dir = RUN / "backup-svn"
    backup_dir.mkdir(parents=True, exist_ok=True)
    plan = {
        "batch": "FOURTEEN-DAY-CHG012-SVN",
        "created": datetime.now().isoformat(),
        "files": [],
    }
    for svn_path, sheet, src06 in SVN_FILES:
        backup = backup_dir / svn_path.name
        shutil.copy2(svn_path, backup)
        wb_src = load_workbook(src06, read_only=True)
        src_rows = list(wb_src[sheet].iter_rows(values_only=True))
        wb_src.close()
        src_head = src_rows[0]
        # 06 追加行范围
        if sheet == "Task":
            sel = lambda r: isinstance(r[1], int) and tuple(r[1] // 100 for r in [r]) and (
                r[1] // 100 in (58, 59, 61, 62, 63, 64, 65) and 1 <= r[1] % 100 <= 6)
        elif sheet == "TaskTarget":
            sel = lambda r: isinstance(r[1], int) and (
                r[1] // 100 in (58, 59, 61, 62, 63, 64, 65) and 1 <= r[1] % 100 <= 6)
        elif sheet == "FourteenDayActivity":
            sel = lambda r: isinstance(r[1], int) and 8 <= r[1] <= 14
        elif sheet == "ActiveReward":
            sel = lambda r: isinstance(r[1], int) and 8 <= r[1] <= 14
        else:  # Drop
            sel = lambda r: isinstance(r[1], int) and 400369 <= r[1] <= 400452
        picked = [r for r in src_rows[4:] if sel(r)]

        wb = load_workbook(svn_path)
        ws = wb[sheet]
        head = [c.value for c in next(ws.iter_rows(max_row=1))]
        width = ws.max_column
        # 表头名映射（06 列名 -> 行内容）
        for r in picked:
            row = [None] * width
            for j, h in enumerate(src_head):
                if h is None or h.startswith("#"):
                    continue
                if h not in head:
                    # SVN 独有列（如 Task.Target）留空
                    continue
                row[head.index(h)] = r[j]
            ws.append(row)
        wb.save(svn_path)
        plan["files"].append({
            "file": str(svn_path), "sheet": sheet, "backup": str(backup),
            "appended": len(picked),
        })
        print(f"{svn_path.name}: 追加 {len(picked)} 行")
    (RUN / "plan-svn.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


def validate():
    result = {"batch": "FOURTEEN-DAY-CHG012-SVN", "generated_at": datetime.now().isoformat(), "errors": []}
    errs = result["errors"]
    # 链路抽查：每条新任务在 SVN 的 Task/Target/Drop 三链一致
    t = list(load_workbook(DATAS / "task" / "Task.xlsx", read_only=True, data_only=True)["Task"].iter_rows(values_only=True))
    g = list(load_workbook(DATAS / "task" / "TaskTarget.xlsx", read_only=True, data_only=True)["TaskTarget"].iter_rows(values_only=True))
    d = list(load_workbook(DATAS / "Drop" / "Drop_TimeLimitedActivity.xlsx", read_only=True, data_only=True)["Drop"].iter_rows(values_only=True))
    f = list(load_workbook(DATAS / "Activity" / "FourteenDayActivity.xlsx", read_only=True, data_only=True)["FourteenDayActivity"].iter_rows(values_only=True))
    a = list(load_workbook(DATAS / "Activity" / "ActiveReward.xlsx", read_only=True, data_only=True)["ActiveReward"].iter_rows(values_only=True))
    t_head, g_head, d_head = t[0], g[0], d[0]
    i_drop, i_tt, i_type = col_index(t_head, "DropId"), col_index(t_head, "TaskTarget"), col_index(t_head, "TaskType")
    i_gtype, i_gparam = col_index(g_head, "TargetType"), col_index(g_head, "ParamList")
    i_ddrop, i_item, i_num = col_index(d_head, "DropId"), col_index(d_head, "DropItem_id"), col_index(d_head, "DropItemNumMin")
    task_by = {r[1]: r for r in t[4:] if r and len(r) > 2 and isinstance(r[1], int)}
    targ_by = {r[1]: r for r in g[4:] if r and len(r) > 2 and isinstance(r[1], int)}
    groups = {}
    for r in d[4:]:
        if r and len(r) > max(i_ddrop, i_item, i_num) and r[i_ddrop] is not None:
            groups.setdefault(r[i_ddrop], []).append((r[i_item], r[i_num]))
    for day, _, drop_id, tid, target, reward in D.iter_tasks():
        desc = target[0]
        r = task_by.get(tid)
        if r is None or r[i_type] != "Task_TTT_FourteenActive" or r[i_tt] != tid or r[i_drop] != drop_id or r[2] != desc:
            errs.append(f"Task{tid} 与 SVN 设计不一致")
        tg = targ_by.get(tid)
        if tg is None or tg[i_gtype] != target[1] or tg[i_gparam] != target[2]:
            errs.append(f"Target{tid} 与 SVN 设计不一致")
        items = sorted(groups.get(drop_id, []))
        if items != sorted([(32, 10), (reward[0], reward[1])]):
            errs.append(f"SVN Drop{drop_id} 展开 {items} 错误")
    fda = {r[3]: r[4] for r in f[4:] if len(r) > 4 and r[2] == 1 and r[3] is not None}
    if sorted(fda) != list(range(1, 15)):  # OpenDay 1~14
        errs.append(f"SVN FourteenDayActivity OpenDay 异常: {sorted(fda)}")
    pts = sorted(r[3] for r in a[4:] if len(r) > 3 and len(r) > 2 and r[2] == 1 and len(r) > 3 and r[3] is not None)
    if pts != list(range(100, 1401, 100)):
        errs.append(f"SVN ActiveReward 档位异常: {pts}")
    result["status"] = "PASS" if not errs else "FAIL"
    (RUN / "validation-svn.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    append_rows_from_06()
    validate()
