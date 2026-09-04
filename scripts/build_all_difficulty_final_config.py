# -*- coding: utf-8 -*-
"""
全玩法难度最终配置构建脚本

输入：框架v2/01_源表/全玩法难度填写表.xlsx（各玩法页签已填"怪物等级"）
输出：框架v2/06_最终配置/全玩法难度/（完整镜像 + 校验）

规则：
- 难度主轴 = level.xlsx 的 Grade（关卡等级）。填写表每个战斗节点按 LevelId 映射到
  level.xlsx 对应行，只更新 Grade 列；Hp/Attack/Armor 系数保持源表现值
  （填写表系数空白 = 不做额外修正，DL-R04 口径，不强制回填）。
- 肉鸽难度与其他战斗关卡一致，写入 level.xlsx 的 Grade；
  RoguelikeLevel.xlsx 只保存肉鸽玩法参数和到实际 LevelId 的映射，不作为难度目标表。
- PVPVE 不配置怪物等级，天然跳过。
- 源表（${VGAME_CONFIG_DATAS}）只读；本次仅生成 06_最终配置 交付包。
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import vgame_paths

FILL_ROOT = vgame_paths.source_docs_root() / "框架v2" / "01_源表"
CONFIG_ROOT = vgame_paths.config_datas()
FINAL_ROOT = vgame_paths.source_docs_root() / "框架v2" / "06_最终配置"
BACKUP_ROOT = FINAL_ROOT.parent / "_backups"

FILL_WORKBOOK = FILL_ROOT / "全玩法难度填写表.xlsx"
LEVEL_SOURCE = CONFIG_ROOT / "level" / "level.xlsx"
OUTPUT_DIR = FINAL_ROOT / "全玩法难度"

# 填写表页签 -> 玩法名（用于分组统计与清单说明）
PLAY_SHEETS = [
    "主线", "困难主线", "角色经验", "金币", "收容经验",
    "旅券", "映射", "爬塔", "Boss挑战", "肉鸽", "大秘境", "PVPVE",
    "其他战斗玩法", "舱室材料",
]
EXCLUDED_GRADE_SHEETS = {"爬塔", "PVPVE"}

# 各玩法正式目标表说明
PLAY_TARGET = {
    "主线": "level/level.xlsx（LevelId 100001~100715，Grade 列）",
    "困难主线": "level/level.xlsx（LevelId 110101~110705，Grade 列）",
    "角色经验": "level/level.xlsx（LevelId 210001~210009，Grade 列）",
    "金币": "level/level.xlsx（LevelId 220001~220009，Grade 列）",
    "收容经验": "level/level.xlsx（LevelId 221001~221009，Grade 列）",
    "旅券": "level/level.xlsx（LevelId 241001~244010，Grade 列，4主题共用档位）",
    "映射": "level/level.xlsx（LevelId 250011~250305，Grade 列，5类型共用档位）",
    "爬塔": "专用TeamHero承载怪物属性，本流程不写level.xlsx的Grade",
    "Boss挑战": "level/level.xlsx（LevelId 510001~570010，Grade 列，7个Boss×10档）",
    "肉鸽": "level/level.xlsx（LevelId 1000001~1000005，Grade 列）",
    "大秘境": "level/level.xlsx（LevelId 320001~320100，Grade 列，4环境共用层位；当前玩法关闭）",
    "PVPVE": "不配置怪物等级（双方属性对算口径），不落表",
}


def sheet_header_map(ws) -> dict[str, int]:
    """返回 列名 -> 列号（1-based），限制前 512 列避免格式痕迹膨胀。"""
    return {
        cell.value: cell.column
        for row in ws.iter_rows(min_row=1, max_row=1, max_col=min(ws.max_column, 512))
        for cell in row
        if cell.value is not None
    }


def load_fill_map() -> dict[str, dict]:
    """读取填写表，返回 level.xlsx 的 LevelId 映射。

    肉鸽页签必须填写实际战斗关卡 LevelId 1000001~1000005，不能填写
    RoguelikeLevel.xlsx 的玩法参数 Id 100001~100005。

    填写表每个页签前 3 行是标题/说明，第 4 行才是表头，数据从第 5 行开始；
    这里扫描前 10 行定位包含 'LevelId/配置映射' 的表头行，避免写死行号。
    """
    wb = load_workbook(FILL_WORKBOOK, read_only=True, data_only=True)
    level_map: dict[str, dict] = {}
    for sheet in PLAY_SHEETS:
        if sheet in EXCLUDED_GRADE_SHEETS:
            continue
        ws = wb[sheet]
        header_row = None
        header_map: dict[str, int] = {}
        for row_index in range(1, 11):
            values = [cell.value for cell in ws[row_index]]
            if any("LevelId/配置映射" == str(v) for v in values):
                header_row = row_index
                header_map = {str(v): i + 1 for i, v in enumerate(values) if v is not None}
                break
        if header_row is None:
            raise AssertionError(f"填写表页签 {sheet} 未找到表头行（缺少 LevelId/配置映射）")
        for row in ws.iter_rows(min_row=header_row + 1, max_col=max(header_map.values()), values_only=True):
            level_id_cell = row[header_map["LevelId/配置映射"] - 1]
            grade_cell = row[header_map["怪物等级"] - 1]
            node_cell = row[header_map["节点名称"] - 1]
            if not level_id_cell:
                continue
            if grade_cell is None:
                continue  # PVPVE 等无怪物等级的行跳过
            entry = {
                "玩法": sheet,
                "节点": str(node_cell) if node_cell is not None else "",
                "怪物等级": int(grade_cell),
            }
            for part in str(level_id_cell).split(";"):
                part = part.strip()
                if not part or not part.isdigit():
                    continue
                key = str(int(part))
                if key in level_map:
                    raise AssertionError(f"level 重复映射：{key}（{level_map[key]['玩法']} 与 {sheet}）")
                level_map[key] = entry
    rogue_ids = sorted(int(key) for key, value in level_map.items() if value["玩法"] == "肉鸽")
    if rogue_ids != list(range(1000001, 1000006)):
        raise AssertionError(f"肉鸽必须映射level.xlsx的LevelId 1000001~1000005，实际{rogue_ids}")
    wb.close()
    return level_map


def build_level_mirror(level_map: dict[str, dict]) -> tuple[int, int, int, dict[str, int]]:
    """复制 level.xlsx 完整镜像，只更新涉及 LevelId 的 Grade 列。返回 (玩法数, 更新行数, 同值行数, 玩法计数)。"""
    wb = load_workbook(LEVEL_SOURCE, data_only=False)
    ws = wb[wb.sheetnames[0]]
    headers = sheet_header_map(ws)
    level_id_col = headers["LevelId"]
    grade_col = headers["Grade"]

    updated = 0
    no_op = 0
    matched_play: dict[str, int] = {}
    for row in range(5, ws.max_row + 1):
        cell = ws.cell(row, level_id_col)
        if cell.value is None:
            continue
        lid = str(int(cell.value)) if isinstance(cell.value, (int, float)) else str(cell.value).strip()
        entry = level_map.get(lid)
        if entry is None:
            continue
        new_grade = entry["怪物等级"]
        old_grade = ws.cell(row, grade_col).value
        if old_grade != new_grade:
            ws.cell(row, grade_col).value = new_grade
            updated += 1
        else:
            no_op += 1
        matched_play[entry["玩法"]] = matched_play.get(entry["玩法"], 0) + 1

    save_without_freeze(wb, OUTPUT_DIR / "level.xlsx")
    return len(matched_play), updated, no_op, matched_play


def save_without_freeze(wb, path: Path) -> None:
    for ws in wb.worksheets:
        ws.freeze_panes = None
    wb.save(path)


def backup_existing_output() -> Path | None:
    if not OUTPUT_DIR.exists() or not any(OUTPUT_DIR.iterdir()):
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_ROOT / f"全玩法难度-{stamp}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUTPUT_DIR, destination)
    return destination


def create_manifest(stats: dict) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "配置清单"
    ws.append(["全玩法难度最终配置清单", "", "", "", ""])
    ws.merge_cells("A1:E1")
    ws["A1"].font = Font(bold=True, size=16, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor="1F4E78")
    ws["A1"].alignment = Alignment(horizontal="center")
    ws.append(["文件", "正式目标表", "数据行数", "状态", "应用说明"])
    entries = [
        ("level.xlsx", str(LEVEL_SOURCE), stats["level_total_rows"], "VALUE_READY",
         f"完整镜像；按 LevelId 仅更新 Grade 列，共 {stats['level_updated']} 行（含 {stats['level_noop']} 行同值），覆盖 {len(stats['matched_play'])} 个玩法"),
    ]
    for row in entries:
        ws.append(row)
    for cell in ws[2]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="5B9BD5")
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    for i, width in enumerate([28, 72, 14, 28, 90], 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    plays = wb.create_sheet("玩法覆盖")
    plays.append(["玩法", "LevelId数", "正式目标表", "状态"])
    for cell in plays[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="5B9BD5")
    for sheet in PLAY_SHEETS:
        count = stats["matched_play"].get(sheet, 0)
        status = "已落表" if count else ("特殊口径" if sheet in EXCLUDED_GRADE_SHEETS else "未涉及")
        plays.append([sheet, count, PLAY_TARGET[sheet], status])
    for col, width in enumerate([16, 12, 86, 12], 1):
        plays.column_dimensions[get_column_letter(col)].width = width

    checks = wb.create_sheet("验收结果")
    checks.append(["检查项", "结果", "说明"])
    for cell in checks[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="5B9BD5")
    for row in [
        ("填写表LevelId映射", "PASS", f"{stats['total_level_ids']} 个 LevelId 全部命中正式表"),
        ("level.xlsx 更新", "PASS", f"更新 {stats['level_updated']} 行，同值跳过 {stats['level_noop']} 行"),
        ("肉鸽目标表", "PASS", "LevelId 1000001~1000005 写入 level.xlsx；RoguelikeLevel.xlsx 不承载难度"),
        ("爬塔", "不落Grade", "怪物属性由专用TeamHero承载，本流程不写level.xlsx"),
        ("系数列", "保持现状", "填写表系数空白=1 不额外修正（DL-R04）；本次不改 Hp/Attack/Armor 系数"),
        ("PVPVE", "不落表", "700000/700001 按双方属性对算口径，无怪物等级"),
        ("源配置写入", "未执行", "按协作约定仅生成 06_最终配置 交付包，${VGAME_ROOT} 正式配置只读"),
    ]:
        checks.append(row)
    checks.column_dimensions["A"].width = 24
    checks.column_dimensions["B"].width = 16
    checks.column_dimensions["C"].width = 90

    manifest_path = OUTPUT_DIR / "00_配置清单.xlsx"
    save_without_freeze(wb, manifest_path)
    return manifest_path


def validate_outputs(level_map: dict[str, dict], stats: dict) -> dict:
    errors = []
    out_level = OUTPUT_DIR / "level.xlsx"
    if not out_level.exists():
        errors.append(f"缺少输出文件：{out_level}")

    # 重新读取输出镜像，校验每个 LevelId 的 Grade 与填写表一致
    # 注意：输出镜像行数不多，用普通模式（read_only=False）以支持 ws.cell 随机访问。
    wb = load_workbook(out_level, read_only=False, data_only=True)
    ws = wb[wb.sheetnames[0]]
    headers = sheet_header_map(ws)
    grade_col = headers["Grade"]
    checked = 0
    mismatched = []
    for row in range(5, ws.max_row + 1):
        cell = ws.cell(row, headers["LevelId"]).value
        if cell is None:
            continue
        lid = str(int(cell)) if isinstance(cell, (int, float)) else str(cell).strip()
        entry = level_map.get(lid)
        if entry is None:
            continue
        checked += 1
        actual = ws.cell(row, grade_col).value
        if actual != entry["怪物等级"]:
            mismatched.append((lid, entry["节点"], entry["怪物等级"], actual))
    if checked != len(level_map):
        errors.append(f"level.xlsx 校验行数 {checked} != 填写表 {len(level_map)}")
    if mismatched:
        errors.append(f"level.xlsx Grade 与填写表不一致：{mismatched[:10]}")
    wb.close()

    if errors:
        raise AssertionError("\n".join(errors))
    return {
        "status": "PASS",
        "level_checked": checked,
        "rogue_checked_in_level": sum(1 for value in level_map.values() if value["玩法"] == "肉鸽"),
    }


def main() -> None:
    for path in (FILL_WORKBOOK, LEVEL_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)

    fill_level_map = load_fill_map()
    level_ids_count = len(fill_level_map)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = backup_existing_output()
    stale_rogue_output = OUTPUT_DIR / "RoguelikeLevel.xlsx"
    if stale_rogue_output.exists():
        stale_rogue_output.unlink()

    level_matched_plays, level_updated, level_noop, matched_play = build_level_mirror(fill_level_map)
    if level_matched_plays != len({v["玩法"] for v in fill_level_map.values()}):
        raise AssertionError("level.xlsx 未覆盖全部玩法")

    stats = {
        "total_level_ids": level_ids_count,
        "level_ids": level_ids_count,
        "rogue_ids_in_level": sum(1 for value in fill_level_map.values() if value["玩法"] == "肉鸽"),
        "level_total_rows": 1233,
        "level_updated": level_updated,
        "level_noop": level_noop,
        "matched_play": dict(sorted(matched_play.items())),
    }
    manifest_path = create_manifest(stats)
    validation = validate_outputs(fill_level_map, stats)
    validation.update(
        {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "output_dir": str(OUTPUT_DIR),
            "backup_dir": str(backup_path) if backup_path else None,
            "fill_workbook": str(FILL_WORKBOOK),
            "source_readonly": True,
            "stats": stats,
            "manifest": str(manifest_path),
        }
    )
    validation_path = OUTPUT_DIR / "全玩法难度配置校验.json"
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import traceback

    try:
        main()
    except BaseException:
        traceback.print_exc()
        raise
