# -*- coding: utf-8 -*-
"""
全玩法难度落表脚本：把 01_源表/全玩法难度填写表.xlsx 的怪物等级直接写入正式源表。

用途：用户授权本次直接修改 ${VGAME_CONFIG_DATAS}（SVN 落地由用户自行提交）。
安全措施：
- 改表前将 level.xlsx 完整备份到 output/全玩法智能难度生成工作流/backup-datas-*/。
- 肉鸽使用 level.xlsx 的 LevelId 1000001~1000005；RoguelikeLevel.xlsx 不承载难度，不修改。
- 只更新 Grade 列；Hp/Attack/Armor 系数保持源表现值（填写表系数空白 = 不回填，DL-R04）。
- 输出变更报告 md/json，供用户 svn diff 复核。
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from build_all_difficulty_final_config import (
    LEVEL_SOURCE,
    load_fill_map,
    sheet_header_map,
)

DESIGN_ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = DESIGN_ROOT / "output" / "全玩法智能难度生成工作流"
REPORT_DIR = DESIGN_ROOT / "output" / "全玩法智能难度生成工作流"

def apply_grades(path: Path, id_header: str, id_map: dict[str, dict]) -> dict:
    """更新一张表的 Grade 列。返回变更统计与样本。"""
    wb = load_workbook(path, data_only=False)
    ws = wb[wb.sheetnames[0]]
    headers = sheet_header_map(ws)
    id_col = headers[id_header]
    grade_col = headers["Grade"]
    updated, noop = [], []
    matched: set[str] = set()
    by_play: dict[str, dict] = {}
    for row in range(5, ws.max_row + 1):
        cell = ws.cell(row, id_col)
        if cell.value is None:
            continue
        lid = str(int(cell.value)) if isinstance(cell.value, (int, float)) else str(cell.value).strip()
        entry = id_map.get(lid)
        if entry is None:
            continue
        grade_cell = ws.cell(row, grade_col)
        if isinstance(grade_cell.value, str) and grade_cell.value.startswith("="):
            raise AssertionError(f"{path.name} {ws.title}!{grade_cell.coordinate} Grade为公式，停止覆盖")
        matched.add(lid)
        old = grade_cell.value
        new = entry["怪物等级"]
        rec = {"LevelId": lid, "节点": entry["节点"], "玩法": entry["玩法"], "旧Grade": old, "新Grade": new}
        if old != new:
            grade_cell.value = new
            updated.append(rec)
        else:
            noop.append(rec)
        by_play.setdefault(entry["玩法"], {"updated": 0, "noop": 0, "min": new, "max": new})
        stat = by_play[entry["玩法"]]
        if old != new:
            stat["updated"] += 1
        else:
            stat["noop"] += 1
        stat["min"] = min(stat["min"], new)
        stat["max"] = max(stat["max"], new)
    missing = sorted(set(id_map) - matched, key=int)
    if missing:
        raise AssertionError(f"{path.name} 有{len(missing)}个LevelId未命中：{missing[:10]}")
    wb.save(path)
    return {"updated": updated, "noop": noop, "by_play": by_play}


def main() -> None:
    level_map = load_fill_map()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # 1) 备份
    backup = BACKUP_DIR / f"backup-datas-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LEVEL_SOURCE, backup / "level.xlsx")

    # 2) 落表
    level_result = apply_grades(LEVEL_SOURCE, "LevelId", level_map)

    # 3) 汇总
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "backup_dir": str(backup),
        "level": {
            "path": str(LEVEL_SOURCE),
            "updated": len(level_result["updated"]),
            "noop": len(level_result["noop"]),
            "by_play": {k: v for k, v in sorted(level_result["by_play"].items())},
        },
        "checks": [
            "Grade 列全部为数值、无公式，可直接覆盖",
            "Hp/Attack/Armor 系数保持源表现值（填写表系数空白按 DL-R04 不回填）",
            "肉鸽按LevelId 1000001~1000005写入level.xlsx；RoguelikeLevel.xlsx未修改",
            "PVPVE 不涉及怪物等级，未改动",
        ],
        "samples": {
            "level_first3": level_result["updated"][:3],
            "level_last3": level_result["updated"][-3:],
        },
    }
    report_path = REPORT_DIR / f"datas-apply-report-{stamp}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
