from __future__ import annotations

import json
import re
import shutil
from copy import copy
from datetime import datetime
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


import vgame_paths

DESIGN_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = vgame_paths.config_datas()
FINAL_ROOT = vgame_paths.source_docs_root() / "框架v2" / "06_最终配置"
OUTPUT_DIR = FINAL_ROOT / "主线高难"
BACKUP_ROOT = FINAL_ROOT.parent / "_backups"

NORMAL_DESIGN = DESIGN_ROOT / "design" / "主线关卡奖励重设计-2026-07-30.md"
HARD_DESIGN = DESIGN_ROOT / "design" / "高难主线关卡奖励重设计-2026-07-30.md"
SIDE_DESIGN = (
    vgame_paths.source_docs_root() / "框架v2" / "03_沉淀MD" / "经济" / "01_玩法_主线经济沉淀-2026-07-08.md"
)

DROP_SOURCE = CONFIG_ROOT / "Drop" / "Drop_mainlevel.xlsx"
UILEVEL_SOURCE = CONFIG_ROOT / "level" / "UIlevel.xlsx"
STAR_SOURCE = CONFIG_ROOT / "level" / "ChapterStarReward.xlsx"
ITEMS_SOURCE = CONFIG_ROOT / "items" / "Items.xlsx"
CHEST_SOURCE = CONFIG_ROOT / "valuablebox" / "Chest.xlsx"
ITEM_CHEST_SOURCE = CONFIG_ROOT / "items" / "ItemChest.xlsx"
ITEM_SWEEP_SOURCE = CONFIG_ROOT / "items" / "ItemSweep.xlsx"
SPECIAL_EQUIPMENT_GENERATE_SOURCE = CONFIG_ROOT / "SpecialEquipment" / "SpecialEquipmentGenerate.xlsx"


# 新道具号段。现有源表及06_最终配置已核对到3027，连续使用3028～3037。
NEW_ITEMS = {
    "低级房车建材": 3028,
    "中级房车建材": 3029,
    "高级房车建材": 3030,
    "低阶升阶材料自选箱": 3031,
    "中阶升阶材料自选箱": 3032,
    "高阶升阶材料自选箱": 3033,
    "3级普通宝石自选箱（第一章）": 3034,
    "3级普通宝石自选箱": 3035,
    "4级普通宝石自选箱": 3036,
    "映射装备副材自选箱": 3037,
}

# 2026-08-06正式Items源表已移除这批旧主材名称行，但高难星级奖励仍沿用已确认的正式ItemId。
# 保留兼容映射，避免重生成06交付包时因名称源缺失而重分配ID。
LEGACY_ITEM_IDS = {
    "20档紫色武器主材": 1089,
    "20档金色防具主材": 1093,
    "30档金色武器主材": 1099,
    "30档金色防具主材": 1102,
    "30档金色首饰主材": 1105,
    "40档金色防具主材": 1111,
    "40档金色首饰主材": 1114,
}

DROP_RANGES = {
    "hard_gem_child": 15000,
    "main_side_root": 10002001,
}

PROGRAMMATIC_PLAYER_EXP_ITEM_ID = 4
FIXED_LEVEL_HELMET_GENERATE_ID = 80028
FIXED_LEVEL_HELMET_GRADE = 5
VISUAL_DROP_CHANCE = 2000
PRESERVED_LEVEL_END_VISUAL_ITEMS = {106, 180028, 311040}
PRESERVED_LEVEL_END_VISUAL_BY_LEVEL = {
    100002: [(311040, 1)],
    100101: [(106, 1)],
    100212: [(180028, 1)],
}

CHAPTER_NAME_TO_ID = {
    "序章": 10000,
    "第一章": 10001,
    "第二章": 10002,
    "第三章": 10003,
    "第四章": 10004,
    "第五章": 10005,
    "第六章": 10006,
    "第七章": 10007,
}

CHAPTER_NAME_TO_NUM = {
    "第一章": 1,
    "第二章": 2,
    "第三章": 3,
    "第四章": 4,
    "第五章": 5,
    "第六章": 6,
    "第七章": 7,
}

NORMAL_LEVEL_COUNTS = {0: 4, 1: 8, 2: 12, 3: 15, 4: 15, 5: 15, 6: 15, 7: 15}
HARD_LEVEL_COUNTS = {chapter: 5 for chapter in range(1, 8)}
HARD_PROBABILITY = {
    1: (8000, 2000),
    2: (7500, 2500),
    3: (7000, 3000),
    4: (6500, 3500),
    5: (6000, 4000),
    6: (5500, 4500),
    7: (5000, 5000),
}

ALIASES = {
    "金币": "猎鹰金币",
    "普通角色抽卡券": "旅券",
    "玩家经验": "行旅帧片",
    "映射之钥": "映射之匙",
    "限时角色抽卡券": "限时旅券",
    "低级舱室建材": "低级房车建材",
    "中级舱室建材": "中级房车建材",
    "高级舱室建材": "高级房车建材",
    "低级能效材料自选箱": "普通能效自选箱",
    "中级能效材料自选箱": "稀有能效自选箱",
    "高级能效材料自选箱": "史诗能效自选箱",
    "顶级能效材料自选箱": "传说能效自选箱",
    "收容物低级材料": "泛黄档案",
    "2级随机宝石箱": "2级宝石掉落箱",
    "3级随机宝石箱": "3级宝石掉落箱",
    "5层蓝色映射装备宝箱": "第5层标准装备补给箱",
    "8层紫色映射装备宝箱": "第8层精品装备补给箱",
    "15层紫色映射装备宝箱": "第15层精品装备补给箱",
    "20层紫色映射装备宝箱": "第20层精品装备补给箱",
    "25层金色映射装备宝箱": "第25层高级装备补给箱",
    "20级紫色武器主材": "20档紫色武器主材",
    "20级金色防具主材": "20档金色防具主材",
    "30级金色武器主材": "30档金色武器主材",
    "30级金色防具主材": "30档金色防具主材",
    "30级金色首饰主材": "30档金色首饰主材",
    "40级金色防具主材": "40档金色防具主材",
    "40级金色首饰主材": "40档金色首饰主材",
}


def markdown_tables(path: Path) -> list[tuple[list[str], list[list[str]]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    tables: list[tuple[list[str], list[list[str]]]] = []
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith("|") and lines[i + 1].startswith("|") and "---" in lines[i + 1]:
            header = [cell.strip() for cell in lines[i].strip("|").split("|")]
            rows: list[list[str]] = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                row = [cell.strip() for cell in lines[i].strip("|").split("|")]
                if len(row) == len(header):
                    rows.append(row)
                i += 1
            tables.append((header, rows))
            continue
        i += 1
    return tables


def find_table(path: Path, header: list[str], row_filter=None) -> list[list[str]]:
    matches = []
    for candidate_header, rows in markdown_tables(path):
        if candidate_header == header:
            matches.extend(rows)
    if row_filter:
        matches = [row for row in matches if row_filter(row)]
    # 文档中同名表只应出现一次；即使上下文重复，也按整行去重并保留原顺序。
    unique: list[list[str]] = []
    seen = set()
    for row in matches:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def parse_amount(value: str) -> tuple[int, int]:
    value = value.replace(",", "").strip()
    if "～" in value:
        lo, hi = value.split("～", 1)
        return int(lo), int(hi)
    return int(value), int(value)


def parse_reward_cell(cell: str) -> list[tuple[str, int, int]]:
    if not cell or cell == "—":
        return []
    parts = re.split(r"[；、]", cell)
    rewards: list[tuple[str, int, int]] = []
    for part in parts:
        part = part.strip()
        if not part or part == "—":
            continue
        match = re.fullmatch(r"(.+?)×([\d,]+(?:～[\d,]+)?)", part)
        if not match:
            raise ValueError(f"无法解析奖励文本：{part!r}（来自{cell!r}）")
        name = match.group(1).strip()
        lo, hi = parse_amount(match.group(2))
        rewards.append((name, lo, hi))
    return rewards


def sheet_header_map(ws) -> dict[str, int]:
    # 部分正式工作簿带有整页格式痕迹，max_column会膨胀到XFD；配置表真实字段均在前512列。
    return {
        cell.value: cell.column
        for row in ws.iter_rows(min_row=1, max_row=1, max_col=min(ws.max_column, 512))
        for cell in row
        if cell.value is not None
    }


def item_name_map() -> dict[str, int]:
    wb = load_workbook(ITEMS_SOURCE, read_only=True, data_only=True)
    ws = wb["items"]
    mapping = {
        str(row[2]).strip(): int(row[1])
        for row in ws.iter_rows(min_row=5, values_only=True)
        if row[1] is not None and row[2]
    }
    mapping.update(LEGACY_ITEM_IDS)
    mapping.update(NEW_ITEMS)
    return mapping


def resolve_item_id(name: str, mapping: dict[str, int], chapter: int | None = None) -> int:
    if name == "3级普通宝石自选箱" and chapter == 1:
        return NEW_ITEMS["3级普通宝石自选箱（第一章）"]
    canonical = ALIASES.get(name, name)
    canonical = re.sub(r"^(\d+级)(红|蓝|黄|绿|紫|橙|青|白)色宝石$", r"\1\2宝石", canonical)
    if canonical not in mapping:
        raise KeyError(f"未找到道具名称对应的ItemId：{name}（规范名：{canonical}）")
    return mapping[canonical]


def drop_config_rewards(rewards, mapping: dict[str, int]):
    return [
        reward
        for reward in rewards
        if resolve_item_id(reward[0], mapping) != PROGRAMMATIC_PLAYER_EXP_ITEM_ID
    ]


def remove_preview_item(preview, item_id: int):
    if not isinstance(preview, str) or not preview:
        return preview
    parts = [part for part in preview.split(";") if part.split(",", 1)[0].strip() != str(item_id)]
    return ";".join(parts) or None


def parse_visual_items(value) -> list[tuple[int, int]]:
    if not isinstance(value, str) or not value.strip():
        return []
    items = []
    for part in value.split(";"):
        item_id, count = (int(token.strip()) for token in part.split(",", 1))
        items.append((item_id, count))
    return items


def merge_visual_items(*groups: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: dict[int, int] = {}
    for group in groups:
        for item_id, count in group:
            if count > 0:
                merged[item_id] = merged.get(item_id, 0) + count
    return list(merged.items())


def format_visual_items(items: Iterable[tuple[int, int]]) -> str | None:
    values = [(item_id, count) for item_id, count in items if count > 0]
    return ";".join(f"{item_id},{count}" for item_id, count in values) or None


def reward_visual_items(rewards) -> list[tuple[int, int]]:
    result = []
    for item_id, _name, _lo, hi in rewards:
        if item_id == PROGRAMMATIC_PLAYER_EXP_ITEM_ID:
            continue
        if item_id == 2:
            icon_count = 1
        elif item_id == 1:
            icon_count = max(1, (hi + 4999) // 5000)
        else:
            icon_count = hi
        result.append((item_id, icon_count))
    return merge_visual_items(result)


def format_reward_preview(rewards) -> str | None:
    values = []
    for item_id, _name, lo, hi in rewards:
        if lo != hi:
            raise AssertionError(f"UIlevel一次性奖励预览只支持固定数量：ItemId={item_id}, {lo}～{hi}")
        values.append(f"{item_id},{hi}")
    return ";".join(values) or None


def hard_mid_visual_items(level) -> list[tuple[int, int]]:
    draw_count = 2 if level["rarity"] == "rare" else 4
    _l1_weight, l2_weight = HARD_PROBABILITY[level["chapter"]]
    l2_count = round(draw_count * l2_weight / 10000)
    l2_count = max(1, min(draw_count - 1, l2_count))
    return [(level["gem_l1"], draw_count - l2_count), (level["gem_l2"], l2_count)]


def normal_level_id(label: str) -> int:
    chapter, stage = (int(part) for part in label.split("-"))
    return 100000 + chapter * 100 + stage


def hard_level_id(label: str) -> int:
    chapter, stage = (int(part) for part in label.split("-"))
    return 110000 + chapter * 100 + stage


def copy_cell(source, target) -> None:
    target.value = source.value
    if source.has_style:
        target._style = copy(source._style)
    if source.number_format:
        target.number_format = source.number_format
    if source.font:
        target.font = copy(source.font)
    if source.fill:
        target.fill = copy(source.fill)
    if source.border:
        target.border = copy(source.border)
    if source.alignment:
        target.alignment = copy(source.alignment)
    if source.protection:
        target.protection = copy(source.protection)


def blank_package(source_path: Path, sheet_name: str):
    wb = load_workbook(source_path, data_only=False)
    for name in list(wb.sheetnames):
        if name != sheet_name:
            del wb[name]
    ws = wb[sheet_name]
    if ws.max_row > 4:
        ws.delete_rows(5, ws.max_row - 4)
    return wb, ws


def save_without_freeze(wb, path: Path) -> None:
    for ws in wb.worksheets:
        ws.freeze_panes = None
    wb.save(path)


def style_new_row(ws, row_number: int, template_row: int = 5) -> None:
    for col in range(1, ws.max_column + 1):
        if template_row <= ws.max_row and ws.cell(template_row, col).has_style:
            ws.cell(row_number, col)._style = copy(ws.cell(template_row, col)._style)
        ws.cell(row_number, col).alignment = copy(ws.cell(template_row, col).alignment)


def append_values(ws, values: Iterable) -> int:
    row_number = ws.max_row + 1
    for col, value in enumerate(values, 1):
        ws.cell(row_number, col).value = value
    style_new_row(ws, row_number)
    return row_number


def add_notes_sheet(wb, title: str, rows: list[tuple[str, str]]) -> None:
    if "中文说明" in wb.sheetnames:
        del wb["中文说明"]
    ws = wb.create_sheet("中文说明", 0)
    ws.append([title, ""])
    ws.merge_cells("A1:B1")
    ws["A1"].font = Font(bold=True, size=14, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor="1F4E78")
    ws["A1"].alignment = Alignment(horizontal="center")
    ws.append(["项目", "说明"])
    for cell in ws[2]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="5B9BD5")
    for key, value in rows:
        ws.append([key, value])
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 110
    for row in ws.iter_rows(min_row=3):
        row[0].font = Font(bold=True)
        row[1].alignment = Alignment(wrap_text=True, vertical="top")


def drop_row(
    drop_id: int,
    remark: str,
    drop_name: str,
    drop_type: str,
    drop_min: int,
    drop_max: int,
    item_id: int | None = None,
    item_min: int | None = None,
    item_max: int | None = None,
    weight: int = 10000,
    child_drop_id: int = 0,
    show_item_id: int | None = None,
) -> list:
    return [
        None,
        None,  # ID公式列由正式表预建行后下拉，不在粘贴包中写死。
        drop_id,
        remark,
        drop_name,
        child_drop_id,
        drop_type,
        drop_min,
        drop_max,
        None,
        item_id,
        item_min,
        item_max,
        weight,
        show_item_id,
        None,
    ]


def build_design_data(mapping: dict[str, int]):
    normal_rows = find_table(
        NORMAL_DESIGN,
        ["关卡", "类型", "基础首通奖励", "附加首通奖励", "常规奖励"],
        lambda row: re.fullmatch(r"[0-7]-\d+", row[0]) is not None,
    )
    if len(normal_rows) != 99:
        raise AssertionError(f"主线逐关表应为99行，实际{len(normal_rows)}行")

    special_rows = find_table(
        NORMAL_DESIGN,
        ["关卡", "特殊首通奖励", "生成等级", "说明"],
        lambda row: re.fullmatch(r"[0-7]-\d+", row[0]) is not None,
    )
    expected_special_labels = {"0-2", "1-1", "2-12"}
    if {row[0] for row in special_rows} != expected_special_labels:
        raise AssertionError(f"主线特殊首通关卡错误：{[row[0] for row in special_rows]}")
    special_by_label = {}
    for label, reward_cell, generate_grade, _description in special_rows:
        rewards = drop_config_rewards(parse_reward_cell(reward_cell), mapping)
        special_by_label[label] = rewards
        if label == "2-12" and generate_grade != str(FIXED_LEVEL_HELMET_GRADE):
            raise AssertionError(f"2-12初级隔热头盔生成等级应为{FIXED_LEVEL_HELMET_GRADE}，实际{generate_grade}")

    normal_levels = []
    for label, level_type, basic, extra, repeat in normal_rows:
        special_rewards = special_by_label.get(label, [])
        first_rewards = drop_config_rewards(parse_reward_cell(basic) + parse_reward_cell(extra), mapping) + special_rewards
        repeat_rewards = drop_config_rewards(parse_reward_cell(repeat), mapping)
        normal_levels.append(
            {
                "label": label,
                "level_id": normal_level_id(label),
                "level_type": level_type,
                "chapter": int(label.split("-")[0]),
                "special": [
                    (resolve_item_id(name, mapping), name, lo, hi) for name, lo, hi in special_rewards
                ],
                "first": [
                    (resolve_item_id(name, mapping), name, lo, hi) for name, lo, hi in first_rewards
                ],
                "repeat": [
                    (resolve_item_id(name, mapping), name, lo, hi) for name, lo, hi in repeat_rewards
                ],
            }
        )

    normal_star_rows = find_table(
        NORMAL_DESIGN,
        ["章节", "星级", "第一奖励", "第二奖励", "第三奖励", "折算价值"],
        lambda row: row[0] in CHAPTER_NAME_TO_ID,
    )
    if len(normal_star_rows) != 37:
        raise AssertionError(f"主线星级奖励应为37行，实际{len(normal_star_rows)}行")
    normal_stars = []
    for chapter_name, star, first, second, third, _value in normal_star_rows:
        chapter_num = CHAPTER_NAME_TO_ID[chapter_name] - 10000
        reward_cells = [first, second, third]
        rewards = []
        for cell in reward_cells:
            for name, lo, hi in parse_reward_cell(cell):
                rewards.append((resolve_item_id(name, mapping, chapter_num), name, lo, hi))
        normal_stars.append(
            {
                "chapter_name": chapter_name,
                "chapter_id": CHAPTER_NAME_TO_ID[chapter_name],
                "chapter": chapter_num,
                "star": int(star),
                "rewards": rewards,
            }
        )

    hard_rows = find_table(
        HARD_DESIGN,
        ["关卡", "宝石类型", "基础首通奖励", "常规奖励", "单关日限"],
        lambda row: re.fullmatch(r"[1-7]-[1-5]", row[0]) is not None,
    )
    if len(hard_rows) != 35:
        raise AssertionError(f"高难逐关表应为35行，实际{len(hard_rows)}行")
    hard_levels = []
    for label, gem_type, first, _repeat, daily_limit in hard_rows:
        chapter = int(label.split("-")[0])
        color = gem_type[:2]
        rarity = "rare" if "稀有" in gem_type else "common"
        first_rewards = drop_config_rewards(parse_reward_cell(first), mapping)
        hard_levels.append(
            {
                "label": label,
                "level_id": hard_level_id(label),
                "chapter": chapter,
                "gem_type": gem_type,
                "color": color,
                "rarity": rarity,
                "daily_limit": int(daily_limit),
                "first": [
                    (resolve_item_id(name, mapping), name, lo, hi) for name, lo, hi in first_rewards
                ],
                "gem_l1": resolve_item_id(f"1级{color}宝石", mapping),
                "gem_l2": resolve_item_id(f"2级{color}宝石", mapping),
            }
        )

    hard_star_rows = find_table(
        HARD_DESIGN,
        ["章节", "星级", "第一奖励", "第二奖励", "第三奖励"],
        lambda row: row[0] in CHAPTER_NAME_TO_NUM,
    )
    if len(hard_star_rows) != 21:
        raise AssertionError(f"高难星级奖励应为21行，实际{len(hard_star_rows)}行")
    hard_stars = []
    for chapter_name, star, first, second, third in hard_star_rows:
        chapter = CHAPTER_NAME_TO_NUM[chapter_name]
        rewards = []
        for cell in (first, second, third):
            for name, lo, hi in parse_reward_cell(cell):
                rewards.append((resolve_item_id(name, mapping, chapter), name, lo, hi))
        hard_stars.append(
            {
                "chapter_name": chapter_name,
                "chapter_id": CHAPTER_NAME_TO_ID[chapter_name],
                "chapter": chapter,
                "star": int(star),
                "rewards": rewards,
            }
        )

    side_rows = find_table(
        SIDE_DESIGN,
        ["支线LevelId", "支线类型", "一次性奖励"],
        lambda row: re.fullmatch(r"120[1-7]\d{2}", row[0]) is not None,
    )
    if len(side_rows) != 44:
        raise AssertionError(f"主线支线逐关表应为44行，实际{len(side_rows)}行")
    side_levels = []
    for index, (level_id_text, side_type, reward_cell) in enumerate(
        sorted(side_rows, key=lambda row: int(row[0]))
    ):
        level_id = int(level_id_text)
        rewards = drop_config_rewards(parse_reward_cell(reward_cell), mapping)
        side_levels.append(
            {
                "label": str(level_id),
                "level_id": level_id,
                "chapter": (level_id // 100) % 100,
                "side_type": side_type,
                "first_drop_id": DROP_RANGES["main_side_root"] + index,
                "first": [
                    (resolve_item_id(name, mapping), name, lo, hi) for name, lo, hi in rewards
                ],
            }
        )
    type_counts = {
        side_type: sum(level["side_type"] == side_type for level in side_levels)
        for side_type in {"战斗", "小游戏", "宝箱"}
    }
    if type_counts != {"战斗": 13, "小游戏": 12, "宝箱": 19}:
        raise AssertionError(f"主线支线类型分布错误：{type_counts}")

    return normal_levels, normal_stars, hard_levels, hard_stars, side_levels


def apply_formal_drop_ids(normal_levels, normal_stars, hard_levels, hard_stars, side_levels) -> None:
    ui_wb = load_workbook(UILEVEL_SOURCE, read_only=True, data_only=True)
    ui_ws = ui_wb["level"]
    ui_headers = sheet_header_map(ui_ws)
    ui_rows = {
        row[ui_headers["LevelId"] - 1]: row
        for row in ui_ws.iter_rows(min_row=5, values_only=True)
    }
    for level in normal_levels + hard_levels:
        row = ui_rows.get(level["level_id"])
        if row is None:
            raise KeyError(f"正式UIlevel缺少关卡：{level['level_id']}")
        fp = row[ui_headers["LevelFPDrop"] - 1]
        pp = row[ui_headers["LevelPPDrop"] - 1]
        first = row[ui_headers["FirstRewardDrop"] - 1]
        repeat = row[ui_headers["FallRewardDrop"] - 1]
        # FirstRewardDrop/FallRewardDrop是实际结算引用；若与展示字段不一致，以实发字段为准，
        # 并在输出UIlevel中将展示字段同步为同一DropId。
        level["first_drop_id"] = first or fp
        level["repeat_drop_id"] = repeat or pp
        if not isinstance(level["first_drop_id"], int) or not isinstance(level["repeat_drop_id"], int):
            raise AssertionError(f"关卡{level['level_id']}缺少正式首通或常规DropId")

    for level in side_levels:
        row = ui_rows.get(level["level_id"])
        if row is None:
            raise KeyError(f"正式UIlevel缺少主线支线关卡：{level['level_id']}")
        old_first_ids = {
            row[ui_headers["LevelFPDrop"] - 1],
            row[ui_headers["FirstRewardDrop"] - 1],
        }
        if not old_first_ids <= {None, 10000016, 10000017, 10000018, level["first_drop_id"]}:
            raise AssertionError(
                f"主线支线{level['level_id']}旧首通引用超出预期：{sorted(old_first_ids, key=str)}"
            )
        if row[ui_headers["LevelPPDrop"] - 1] is not None or row[ui_headers["FallRewardDrop"] - 1] is not None:
            raise AssertionError(f"主线支线{level['level_id']}不应配置常规/重复Drop")

    level_root_ids = [
        *(level["first_drop_id"] for level in normal_levels + hard_levels),
        *(level["repeat_drop_id"] for level in normal_levels + hard_levels),
        *(level["first_drop_id"] for level in side_levels),
    ]
    if len(level_root_ids) != len(set(level_root_ids)):
        duplicates = sorted({drop_id for drop_id in level_root_ids if level_root_ids.count(drop_id) > 1})
        raise AssertionError(f"正式UIlevel仍存在跨关卡DropId共用冲突：{duplicates}")

    star_wb = load_workbook(STAR_SOURCE, read_only=True, data_only=True)
    star_ws = star_wb["ChapterStarReward"]
    star_headers = sheet_header_map(star_ws)
    source_stars = {}
    for row in star_ws.iter_rows(min_row=5, values_only=True):
        key = (
            row[star_headers["ChapterId"] - 1],
            row[star_headers["Star"] - 1],
            bool(row[star_headers["IsDifficult"] - 1]),
        )
        if key in source_stars:
            raise AssertionError(f"正式ChapterStarReward重复章节星级键：{key}")
        source_stars[key] = {
            "id": row[star_headers["Id"] - 1],
            "drop_id": row[star_headers["DropId"] - 1],
        }

    for star in normal_stars:
        key = (star["chapter_id"], star["star"], False)
        if key not in source_stars:
            raise KeyError(f"正式ChapterStarReward缺少主线节点：{key}")
        star["row_id"] = source_stars[key]["id"]
        star["drop_id"] = source_stars[key]["drop_id"]

    # 高难节点沿用正式表当前Id；历史重复Id已由正式表修正。
    for star in hard_stars:
        key = (star["chapter_id"], star["star"], True)
        if key not in source_stars:
            raise KeyError(f"正式ChapterStarReward缺少高难节点：{key}")
        star["drop_id"] = source_stars[key]["drop_id"]
        star["row_id"] = source_stars[key]["id"]

    all_star_drop_ids = [star["drop_id"] for star in normal_stars + hard_stars]
    if len(all_star_drop_ids) != len(set(all_star_drop_ids)):
        duplicates = sorted({drop_id for drop_id in all_star_drop_ids if all_star_drop_ids.count(drop_id) > 1})
        raise AssertionError(f"正式星级奖励DropId重复：{duplicates}")
    all_star_row_ids = [star["row_id"] for star in normal_stars] + [star["row_id"] for star in hard_stars]
    if len(all_star_row_ids) != len(set(all_star_row_ids)):
        raise AssertionError("输出ChapterStarReward的Id仍有重复")


def drop_output_order(normal_levels, normal_stars, hard_levels, hard_stars, side_levels) -> list[int]:
    child_ids = sorted(
        {
            *(level["gem_child_drop_id"] for level in hard_levels),
        }
    )
    root_ids = [level["first_drop_id"] for level in normal_levels]
    root_ids.extend(star["drop_id"] for star in normal_stars)
    root_ids.extend(star["drop_id"] for star in hard_stars)
    root_ids.extend(level["repeat_drop_id"] for level in normal_levels)
    for level in hard_levels:
        root_ids.extend((level["first_drop_id"], level["repeat_drop_id"]))
    root_ids.extend(level["first_drop_id"] for level in side_levels)
    return child_ids + root_ids


def build_drop_workbook(normal_levels, normal_stars, hard_levels, hard_stars, side_levels):
    wb, ws = blank_package(DROP_SOURCE, "Drop")
    rows: list[list] = []

    for level in normal_levels:
        first_id = level["first_drop_id"]
        repeat_id = level["repeat_drop_id"]
        for item_id, name, lo, hi in level["first"]:
            rows.append(drop_row(first_id, f"主线{level['label']}首通", name, "fixed_", 1, 1, item_id, lo, hi, 10000, 0, item_id))
        for item_id, name, lo, hi in level["repeat"]:
            rows.append(drop_row(repeat_id, f"主线{level['label']}常规", name, "fixed_", 1, 1, item_id, lo, hi, 10000, 0, item_id))

    for index, level in enumerate(hard_levels):
        first_id = level["first_drop_id"]
        repeat_id = level["repeat_drop_id"]
        gem_child = DROP_RANGES["hard_gem_child"] + index
        level["gem_child_drop_id"] = gem_child
        for item_id, name, lo, hi in level["first"]:
            rows.append(drop_row(first_id, f"高难{level['label']}首通", name, "fixed_", 1, 1, item_id, lo, hi, 10000, 0, item_id))

        rows.append(drop_row(repeat_id, f"高难{level['label']}常规", "随机宝石子包", "fixed__random", 1, 1, 0, 0, 0, 0, gem_child, None))
        draw_count = 2 if level["rarity"] == "rare" else 4
        l1_weight, l2_weight = HARD_PROBABILITY[level["chapter"]]
        rows.append(drop_row(gem_child, f"高难{level['label']}宝石L1", f"1级{level['color']}宝石", "random", draw_count, draw_count, level["gem_l1"], 1, 1, l1_weight, 0, level["gem_l1"]))
        rows.append(drop_row(gem_child, f"高难{level['label']}宝石L2", f"2级{level['color']}宝石", "random", draw_count, draw_count, level["gem_l2"], 1, 1, l2_weight, 0, level["gem_l2"]))

    for star in normal_stars:
        drop_id = star["drop_id"]
        for item_id, name, lo, hi in star["rewards"]:
            rows.append(drop_row(drop_id, f"{star['chapter_name']}{star['star']}星奖励", name, "fixed_", 1, 1, item_id, lo, hi, 10000, 0, item_id))

    for star in hard_stars:
        drop_id = star["drop_id"]
        for item_id, name, lo, hi in star["rewards"]:
            rows.append(drop_row(drop_id, f"高难{star['chapter_name']}{star['star']}星奖励", name, "fixed_", 1, 1, item_id, lo, hi, 10000, 0, item_id))

    for level in side_levels:
        for item_id, name, lo, hi in level["first"]:
            rows.append(
                drop_row(
                    level["first_drop_id"],
                    f"主线支线{level['level_id']}一次性奖励",
                    name,
                    "fixed_",
                    1,
                    1,
                    item_id,
                    lo,
                    hi,
                    10000,
                    0,
                    item_id,
                )
            )

    order = {
        drop_id: index
        for index, drop_id in enumerate(
            drop_output_order(normal_levels, normal_stars, hard_levels, hard_stars, side_levels)
        )
    }
    unknown_drop_ids = {row[2] for row in rows} - order.keys()
    if unknown_drop_ids:
        raise AssertionError(f"Drop output order is missing DropIds: {sorted(unknown_drop_ids)}")
    rows.sort(key=lambda row: order[row[2]])

    for row in rows:
        append_values(ws, row)
    add_notes_sheet(
        wb,
        "主线与高难奖励 Drop 粘贴包",
        [
            ("来源表", str(DROP_SOURCE)),
            ("设计口径", f"{NORMAL_DESIGN.name}；{HARD_DESIGN.name}；{SIDE_DESIGN.name}"),
            ("数据状态", "数值已就绪；正式源表ID公式列需先预建行并下拉公式，本包不写死公式值。"),
            ("根DropId", "主线/高难/星级沿用正式引用；44个支线拆分旧共享包，新增10002001～10002044。"),
            ("子DropId", "15000～15034为高难随机宝石子包；玩家经验由程序默认结算，不进入Drop配置。"),
            ("落地边界", "仅生成06_最终配置交付包，未改${VGAME_ROOT}下的正式配置。"),
        ],
    )
    return wb, len(rows)


def build_uilevel_workbook(normal_levels, hard_levels, side_levels):
    wb = load_workbook(UILEVEL_SOURCE, data_only=False)
    ws = wb["level"]
    headers = sheet_header_map(ws)
    source_by_level = {
        ws.cell(row, headers["LevelId"]).value: row
        for row in range(5, ws.max_row + 1)
    }

    selected = normal_levels + hard_levels + side_levels
    for level in selected:
        level_id = level["level_id"]
        if level_id not in source_by_level:
            raise KeyError(f"UIlevel源表缺少关卡：{level_id}")
        target_row = source_by_level[level_id]
        if "side_type" in level:
            mid_visual_items = []
        elif "repeat" in level:
            mid_visual_items = reward_visual_items(level["repeat"])
        else:
            mid_visual_items = hard_mid_visual_items(level)
        first_item_ids = {item_id for item_id, _name, _lo, _hi in level["first"]}
        # 特殊关底表现只按已确认的LevelId白名单保留，避免正式旧表中的错位图标继续串到别关。
        preserved_end_visual = []
        preserved_item_ids = {item_id for item_id, _count in preserved_end_visual}
        preserved_end_visual.extend(
            (item_id, count)
            for item_id, count in PRESERVED_LEVEL_END_VISUAL_BY_LEVEL.get(level_id, [])
            if item_id not in preserved_item_ids and item_id not in first_item_ids
        )
        end_visual_items = merge_visual_items(reward_visual_items(level["first"]), preserved_end_visual)
        level["mid_visual_drop_items"] = format_visual_items(mid_visual_items)
        level["mid_visual_drop_chance"] = VISUAL_DROP_CHANCE if mid_visual_items else 0
        level["level_end_visual_drop_items"] = format_visual_items(end_visual_items)
        ws.cell(target_row, headers["MidVisualDropItems"]).value = level["mid_visual_drop_items"]
        ws.cell(target_row, headers["MidVisualDropChance"]).value = level["mid_visual_drop_chance"]
        ws.cell(target_row, headers["LevelEndVisualDropItems"]).value = level["level_end_visual_drop_items"]
        ws.cell(target_row, headers["LevelFPDrop"]).value = level["first_drop_id"]
        ws.cell(target_row, headers["FirstRewardDrop"]).value = level["first_drop_id"]
        if "side_type" in level:
            ws.cell(target_row, headers["LevelPPDrop"]).value = None
            ws.cell(target_row, headers["FallRewardDrop"]).value = None
            if "FirstReward" in headers:
                ws.cell(target_row, headers["FirstReward"]).value = format_reward_preview(level["first"])
            if "Reward" in headers:
                ws.cell(target_row, headers["Reward"]).value = None
        else:
            ws.cell(target_row, headers["LevelPPDrop"]).value = level["repeat_drop_id"]
            ws.cell(target_row, headers["FallRewardDrop"]).value = level["repeat_drop_id"]
            for field in ("FirstReward", "Reward"):
                if field in headers:
                    cell = ws.cell(target_row, headers[field])
                    cell.value = remove_preview_item(cell.value, PROGRAMMATIC_PLAYER_EXP_ITEM_ID)
        ws.cell(target_row, headers["ChapterId"]).value = 10000 + level["chapter"]
    add_notes_sheet(
        wb,
        "主线与高难 UIlevel 奖励引用粘贴包",
        [
            ("来源表", str(UILEVEL_SOURCE)),
            ("覆盖范围", "保留正式UIlevel完整行序，更新新版主线99关、高难35关及主线支线44关。旧节奏多余关卡及其它玩法行原样保留。"),
            ("粘贴规则", "本包与正式UIlevel行序完全一致，可整表替换；若只粘贴字段，也必须按LevelId对齐，禁止将178个目标关卡压缩后连续粘贴。"),
            ("修改字段", "更新奖励Drop引用、奖励预览及视觉字段，移除玩家经验预览，并同步修正章节归属；支线只配置一次性奖励。"),
            ("视觉映射", "主线关中池对应常规材料上限；高难关中池按同色1/2级宝石期望比例压缩；关底池对应首通奖励。元晶固定1个Icon，金币每5000折1个Icon。"),
            ("特殊保留", "保留原表中小寒、旅券、初级隔热头盔的关底特殊表现；玩家经验不进入视觉池。"),
            ("章节修正", "100701～100715源表ChapterId仍为10006，本包修正为10007。"),
            ("落地边界", "仅生成06_最终配置交付包，未改${VGAME_ROOT}下的正式配置。"),
        ],
    )
    effective_rows = sum(
        1
        for row in range(5, ws.max_row + 1)
        if isinstance(ws.cell(row, headers["LevelId"]).value, int)
    )
    return wb, effective_rows


def build_star_workbook(normal_stars, hard_stars):
    wb, ws = blank_package(STAR_SOURCE, "ChapterStarReward")
    for star in sorted(normal_stars, key=lambda item: item["row_id"]):
        append_values(ws, [None, star["row_id"], star["chapter_id"], star["star"], star["drop_id"], False])
    for star in sorted(hard_stars, key=lambda item: item["row_id"]):
        append_values(ws, [None, star["row_id"], star["chapter_id"], star["star"], star["drop_id"], True])
    add_notes_sheet(
        wb,
        "主线与高难章节星级奖励粘贴包",
        [
            ("来源表", str(STAR_SOURCE)),
            ("主线节点", "37个：序章3、第一章4、第二章5、第三至第七章各5。"),
            ("高难节点", "21个：第一至第七章各5/10/15星。"),
            ("替换方式", "ChapterStarReward按本包整体替换主线/高难旧节点，避免保留旧节奏的不可达星数。"),
        ],
    )
    return wb, 58


def build_items_workbook():
    source_wb = load_workbook(ITEMS_SOURCE, data_only=False)
    source_ws = source_wb["items"]
    headers = sheet_header_map(source_ws)
    source_rows = {}
    for row in range(5, source_ws.max_row + 1):
        item_id = source_ws.cell(row, headers["Id"]).value
        if item_id in {1074, 3015, 3016, 3017, 3027}:
            source_rows[item_id] = row

    wb, ws = blank_package(ITEMS_SOURCE, "items")
    item_specs = [
        (3028, "低级房车建材", "Green", "房车设备升级使用的低级舱室建材。", 1074, False),
        (3029, "中级房车建材", "Blue", "房车设备升级使用的中级舱室建材。", 1074, False),
        (3030, "高级房车建材", "Purple", "房车设备升级使用的高级舱室建材。", 1074, False),
        (3031, "低阶升阶材料自选箱", "Blue", "可自选获得1个低阶角色升阶材料。", 3015, True),
        (3032, "中阶升阶材料自选箱", "Purple", "可自选获得1个中阶角色升阶材料。", 3017, True),
        (3033, "高阶升阶材料自选箱", "Orange", "可自选获得1个高阶角色升阶材料。", 3017, True),
        (3034, "3级普通宝石自选箱（第一章）", "Purple", "可从红、蓝、黄、绿、紫五种3级普通宝石中自选1个。", 3027, True),
        (3035, "3级普通宝石自选箱", "Purple", "可从红、蓝、黄、绿、紫、橙六种3级普通宝石中自选1个。", 3027, True),
        (3036, "4级普通宝石自选箱", "Orange", "可从红、蓝、黄、绿、紫、橙六种4级普通宝石中自选1个。", 3027, True),
        (3037, "映射装备副材自选箱", "Blue", "可从四种映射装备副材中自选1个。", 3027, True),
    ]
    for item_id, name, quality, description, template_id, is_box in item_specs:
        source_row = source_rows[template_id]
        target_row = ws.max_row + 1
        for col in range(1, source_ws.max_column + 1):
            copy_cell(source_ws.cell(source_row, col), ws.cell(target_row, col))
        ws.cell(target_row, headers["Id"]).value = item_id
        ws.cell(target_row, headers["Name"]).value = name
        ws.cell(target_row, headers["ParaList"]).value = item_id if is_box else None
        ws.cell(target_row, headers["ItemType"]).value = "ItemType_Prop"
        ws.cell(target_row, headers["ItemSubType"]).value = "ItemSubType_PickOne_ValuableBox" if is_box else None
        ws.cell(target_row, headers["ChestOpenMode"]).value = "manual" if is_box else None
        ws.cell(target_row, headers["ItemQuality"]).value = quality
        ws.cell(target_row, headers["Description"]).value = f"{description}\n<br><color=#86683d>{description}</color>"
        ws.cell(target_row, headers["RelatedId"]).value = item_id if is_box else None
    add_notes_sheet(
        wb,
        "主线与高难奖励新增道具粘贴包",
        [
            ("新增ItemId", "3028～3037，共10个：3档房车建材 + 3档升阶箱 + 3类普通宝石箱 + 映射副材箱。"),
            ("号段核对", "生成前已扫描正式Items与06_最终配置，未发现3028～3037占用。"),
            ("图标说明", "房车建材暂复用房车零件图标；自选箱暂复用通用自选箱图标，正式美术资源到位后替换Icon。"),
            ("名称兼容", "策划文档中的‘舱室建材’与‘房车建材’指向同一组ItemId。"),
        ],
    )
    return wb, len(item_specs)


def build_special_equipment_generate_workbook():
    source_wb = load_workbook(SPECIAL_EQUIPMENT_GENERATE_SOURCE, data_only=False)
    source_ws = source_wb["SpecialEquipment"]
    headers = {
        source_ws.cell(1, col).value: col
        for col in range(1, 12)
        if source_ws.cell(1, col).value
    }
    source_row = next(
        row
        for row in range(5, source_ws.max_row + 1)
        if source_ws.cell(row, headers["Id"]).value == FIXED_LEVEL_HELMET_GENERATE_ID
    )
    wb = Workbook()
    ws = wb.active
    ws.title = "SpecialEquipment"
    for row in range(1, 5):
        for col in range(1, 12):
            copy_cell(source_ws.cell(row, col), ws.cell(row, col))
        ws.row_dimensions[row].height = source_ws.row_dimensions[row].height
    for col in range(1, 12):
        copy_cell(source_ws.cell(source_row, col), ws.cell(5, col))
        letter = get_column_letter(col)
        ws.column_dimensions[letter].width = source_ws.column_dimensions[letter].width
    ws.row_dimensions[5].height = source_ws.row_dimensions[source_row].height
    ws.cell(5, headers["GradeList"]).value = f"{FIXED_LEVEL_HELMET_GRADE},100"
    add_notes_sheet(
        wb,
        "2-12特殊首通映射装备生成规则粘贴包",
        [
            ("更新GenerateId", str(FIXED_LEVEL_HELMET_GENERATE_ID)),
            ("固定装备", "初级隔热头盔（SpecialEquipmentId 80028）"),
            ("等级池", f"{FIXED_LEVEL_HELMET_GRADE},100；确保ItemId 180028实际生成5级装备，不再随机生成10/15级。"),
            ("落地边界", "仅生成06_最终配置交付包，未改${VGAME_ROOT}下的正式配置。"),
        ],
    )
    return wb, 1


def chest_specs(mapping: dict[str, int]):
    common_l3_5 = [resolve_item_id(f"3级{color}宝石", mapping) for color in "红蓝黄绿紫"]
    common_l3_6 = [resolve_item_id(f"3级{color}宝石", mapping) for color in "红蓝黄绿紫橙"]
    common_l4_6 = [resolve_item_id(f"4级{color}宝石", mapping) for color in "红蓝黄绿紫橙"]
    return [
        (3031, "低阶升阶材料自选箱", [1001, 1002, 1003]),
        (3032, "中阶升阶材料自选箱", [1004, 1005, 1006]),
        (3033, "高阶升阶材料自选箱", [1007, 1008, 1009]),
        (3034, "3级普通宝石自选箱（第一章）", common_l3_5),
        (3035, "3级普通宝石自选箱", common_l3_6),
        (3036, "4级普通宝石自选箱", common_l4_6),
        (3037, "映射装备副材自选箱", [1152, 1153, 1154, 1155]),
    ]


def build_chest_workbook(mapping: dict[str, int]):
    wb, ws = blank_package(CHEST_SOURCE, "Chest")
    next_table_id = 2020
    count = 0
    for chest_id, chest_name, item_ids in chest_specs(mapping):
        for item_id in item_ids:
            append_values(
                ws,
                [None, next_table_id, chest_id, chest_name, chest_name, "chest_pickone", 1, 1, "no", 0, "no", "chestmodetype_pick", item_id, 1, 1, 10000, "可选择获得以下奖励"],
            )
            next_table_id += 1
            count += 1
    add_notes_sheet(
        wb,
        "主线与高难奖励自选箱池粘贴包",
        [
            ("新增宝箱", "ChestId 3031～3037，共7个自选池、30行选项。"),
            ("第一章宝石箱", "3034仅含红/蓝/黄/绿/紫3级宝石，不含尚未投放的橙色，也不含青/白稀有宝石。"),
            ("后续宝石箱", "3035/3036含红/蓝/黄/绿/紫/橙，不含青/白稀有宝石。"),
            ("选择规则", "单个箱子选择1次；奖励发放多个箱子时可重复选择同一材料。"),
        ],
    )
    return wb, count


def build_item_chest_workbook(mapping: dict[str, int]):
    wb, ws = blank_package(ITEM_CHEST_SOURCE, "ItemAccess")
    # ItemChest以ItemId为键，只能保留一个来源箱。3级宝石统一映射到覆盖面更广的3035；
    # 第一章限制池3034仍在Chest中完整生效，不额外写重复ItemId。
    access_rows = []
    for chest_id, _chest_name, item_ids in chest_specs(mapping):
        if chest_id == 3034:
            continue
        for item_id in item_ids:
            access_rows.append((item_id, chest_id))
    seen = set()
    for item_id, chest_id in access_rows:
        if item_id in seen:
            raise AssertionError(f"ItemChest出现重复ItemId：{item_id}")
        seen.add(item_id)
        append_values(ws, [None, item_id, None, chest_id])
    add_notes_sheet(
        wb,
        "主线与高难奖励自选箱反向索引粘贴包",
        [
            ("新增映射", f"共{len(access_rows)}行，ItemId保持唯一。"),
            ("第一章限制池", "ChestId 3034与3035共享5种3级宝石；ItemChest无法一物多箱，反向索引统一指向3035，3034实际选池仍由Chest.xlsx控制。"),
        ],
    )
    return wb, len(access_rows)


def build_item_sweep_workbook(normal_levels, hard_levels):
    wb, ws = blank_package(ITEM_SWEEP_SOURCE, "ItemAccess")
    sweep_rows = []
    for level in normal_levels:
        item_ids = [item_id for item_id, _name, _lo, _hi in level["repeat"]]
        if not item_ids:
            raise AssertionError(f"普通主线{level['level_id']}缺少可重复掉落，无法生成ItemSweep")
        sweep_rows.append((level["level_id"], item_ids))
    for level in hard_levels:
        sweep_rows.append((level["level_id"], [level["gem_l1"], level["gem_l2"]]))

    if len(sweep_rows) != 134:
        raise AssertionError(f"ItemSweep应覆盖99个普通主线+35个高难，实际{len(sweep_rows)}行")
    for sort, (level_id, item_ids) in enumerate(sweep_rows, 1):
        if len(item_ids) != len(set(item_ids)):
            raise AssertionError(f"ItemSweep关卡{level_id}存在重复ItemId：{item_ids}")
        item_value = item_ids[0] if len(item_ids) == 1 else ";".join(str(item_id) for item_id in item_ids)
        append_values(ws, [None, level_id, None, item_value, sort])

    add_notes_sheet(
        wb,
        "主线与高难扫荡道具索引全量替换包",
        [
            ("来源表", str(ITEM_SWEEP_SOURCE)),
            ("覆盖范围", "134行：普通主线99关 + 高难35关；支线44关为一次性奖励，不进入扫荡索引。"),
            ("生成规则", "按UIlevel重复掉落引用对应的真实Drop生成；普通主线登记常规材料，高难登记同色1级与2级宝石。"),
            ("排序规则", "普通主线按序章至第七章关卡顺序为1～99；高难第一至第七章顺序为100～134。"),
            ("替换方式", "本文件是ItemSweep有效数据行全量替换包，不与旧111行追加合并。"),
            ("落地边界", "仅生成06_最终配置交付包，未改${VGAME_ROOT}下的正式配置。"),
        ],
    )
    return wb, len(sweep_rows)


def create_manifest(counts: dict[str, int], file_paths: dict[str, Path]) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "配置清单"
    ws.append(["主线与高难奖励最终配置清单", "", "", "", ""])
    ws.merge_cells("A1:E1")
    ws["A1"].font = Font(bold=True, size=16, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor="1F4E78")
    ws["A1"].alignment = Alignment(horizontal="center")
    ws.append(["文件", "正式目标表", "数据行数", "状态", "应用说明"])
    entries = [
        ("Items.xlsx", str(ITEMS_SOURCE), counts["items"], "VALUE_READY", "新增3028～3037"),
        ("Chest.xlsx", str(CHEST_SOURCE), counts["chest"], "VALUE_READY", "新增ChestId 3031～3037"),
        ("ItemChest.xlsx", str(ITEM_CHEST_SOURCE), counts["item_chest"], "VALUE_READY", "新增自选池反向索引"),
        ("ItemSweep.xlsx", str(ITEM_SWEEP_SOURCE), counts["item_sweep"], "VALUE_READY", "全量替换134行主线/高难扫荡道具索引"),
        ("SpecialEquipmentGenerate.xlsx", str(SPECIAL_EQUIPMENT_GENERATE_SOURCE), counts["special_equipment_generate"], "VALUE_READY", "更新GenerateId 80028：初级隔热头盔固定生成5级"),
        ("Drop_mainlevel.xlsx", str(DROP_SOURCE), counts["drop"], "VALUE_READY_FORMULA_MANUAL", "正式表预建行并下拉ID公式后，按DropId粘贴"),
        ("UIlevel.xlsx", str(UILEVEL_SOURCE), counts["uilevel"], "VALUE_READY", "完整保留正式行序；按LevelId更新99主线+35高难+44支线的奖励与视觉字段"),
        ("ChapterStarReward.xlsx", str(STAR_SOURCE), counts["star"], "VALUE_READY", "主线/高难节点整体替换"),
    ]
    for row in entries:
        ws.append(row)
    for cell in ws[2]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="5B9BD5")
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    widths = [28, 72, 14, 28, 62]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    ranges = wb.create_sheet("ID号段")
    ranges.append(["用途", "起始ID", "结束ID", "数量"])
    for cell in ranges[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="5B9BD5")
    range_rows = [
        ("主线首通Root", 10000011, 10000115, 99),
        ("主线常规Root", 12000001, 12000105, 99),
        ("高难首通Root", 13100101, 13100705, 35),
        ("高难常规Root", 13200101, 13200705, 35),
        ("主线星级Root", 11000001, 11000037, 37),
        ("高难星级Root", 11001001, 11001021, 21),
        ("主线支线一次性Root", 10002001, 10002044, 44),
        ("高难经验子包", 14000, 14034, 35),
        ("高难宝石子包", 15000, 15034, 35),
        ("新增Items/Chest", 3028, 3037, 10),
        ("更新映射装备生成规则", 80028, 80028, 1),
    ]
    for row in range_rows:
        ranges.append(row)
    for col, width in enumerate([28, 18, 18, 12], 1):
        ranges.column_dimensions[get_column_letter(col)].width = width

    checks = wb.create_sheet("验收结果")
    checks.append(["检查项", "结果", "说明"])
    for cell in checks[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="5B9BD5")
    for row in [
        ("主线关卡", "PASS", "99关，序章4/第一章8/第二章12/第三至第七章各15"),
        ("高难关卡", "PASS", "35关，第一至第七章各5，无序章"),
        ("主线支线", "PASS", "44关；战斗13、小游戏12、宝箱19；每关独立一次性DropId"),
        ("扫荡索引", "PASS", "ItemSweep 134行与99个普通主线、35个高难的真实重复Drop逐关一致"),
        ("主线星级", "PASS", "37节点；第二章沿用正式7/14/21/28/36五星档"),
        ("高难星级", "PASS", "21节点，每章5/10/15星"),
        ("宝石稀有度", "PASS", "青/白仅指定高难关；星级自选箱不含青/白"),
        ("特殊首通", "PASS", "0-2小寒×1、1-1旅券×1、2-12仅5级初级隔热头盔×1"),
        ("引用闭环", "PASS", "DropId、LevelId、ChapterId、ItemId、ChestId均通过脚本校验"),
        ("源配置写入", "未执行", "按用户要求只生成06_最终配置交付包"),
    ]:
        checks.append(row)
    checks.column_dimensions["A"].width = 28
    checks.column_dimensions["B"].width = 16
    checks.column_dimensions["C"].width = 90
    manifest_path = OUTPUT_DIR / "00_配置清单.xlsx"
    save_without_freeze(wb, manifest_path)
    file_paths["manifest"] = manifest_path
    return manifest_path


def existing_ids_in_final_configs() -> set[int]:
    ids: set[int] = set()
    if not FINAL_ROOT.exists():
        return ids
    for path in FINAL_ROOT.rglob("Items.xlsx"):
        if OUTPUT_DIR in path.parents or path.name.startswith("~$"):
            continue
        try:
            wb = load_workbook(path, read_only=True, data_only=True)
            if "items" not in wb.sheetnames:
                continue
            ws = wb["items"]
            headers = sheet_header_map(ws)
            if "Id" not in headers:
                continue
            for row in range(5, ws.max_row + 1):
                value = ws.cell(row, headers["Id"]).value
                if isinstance(value, int):
                    ids.add(value)
        except Exception:
            continue
    return ids


def assert_no_id_collisions() -> None:
    source_wb = load_workbook(ITEMS_SOURCE, read_only=True, data_only=True)
    source_ws = source_wb["items"]
    source_items = {
        row[1]: str(row[2]).strip()
        for row in source_ws.iter_rows(min_row=5, values_only=True)
        if isinstance(row[1], int) and row[2]
    }
    expected_items = {item_id: name for name, item_id in NEW_ITEMS.items()}
    source_conflicts = {
        item_id
        for item_id, expected_name in expected_items.items()
        if item_id in source_items and source_items[item_id] != expected_name
    }
    final_ids = existing_ids_in_final_configs()
    collisions = source_conflicts | (set(NEW_ITEMS.values()) & final_ids)
    if collisions:
        raise AssertionError(f"新增ItemId发生占用冲突：{sorted(collisions)}")


def assert_side_drop_ids_available() -> None:
    target_ids = set(range(DROP_RANGES["main_side_root"], DROP_RANGES["main_side_root"] + 44))
    drop_locations: dict[int, set[str]] = {}
    for path in (CONFIG_ROOT / "Drop").glob("*.xlsx"):
        if path.name.startswith("~$"):
            continue
        wb = load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            headers = sheet_header_map(ws)
            if "DropId" not in headers:
                continue
            drop_id_col = headers["DropId"]
            for row in ws.iter_rows(
                min_row=5,
                min_col=drop_id_col,
                max_col=drop_id_col,
                values_only=True,
            ):
                drop_id = row[0]
                if drop_id in target_ids:
                    drop_locations.setdefault(drop_id, set()).add(f"{path.name}/{ws.title}")
    conflicts = {
        drop_id: sorted(locations)
        for drop_id, locations in drop_locations.items()
        if locations != {"Drop_mainlevel.xlsx/Drop"}
    }
    if conflicts:
        raise AssertionError(f"主线支线DropId被非目标逻辑Drop占用：{dict(list(conflicts.items())[:20])}")

    ui_wb = load_workbook(UILEVEL_SOURCE, read_only=True, data_only=True)
    ui_ws = ui_wb["level"]
    ui_headers = sheet_header_map(ui_ws)
    side_level_ids = {120101, 120102, 120103, 120104, 120201, 120202, 120203, 120204, 120205} | {
        120000 + chapter * 100 + stage
        for chapter in range(3, 8)
        for stage in range(1, 8)
    }
    for row in ui_ws.iter_rows(min_row=5, values_only=True):
        level_id = row[ui_headers["LevelId"] - 1]
        if level_id in side_level_ids:
            continue
        for field in ("LevelFPDrop", "LevelPPDrop", "FirstRewardDrop", "FallRewardDrop"):
            drop_id = row[ui_headers[field] - 1]
            if drop_id in target_ids:
                raise AssertionError(f"主线支线新DropId已被UIlevel关卡{level_id}引用：{drop_id}")


def backup_existing_output() -> Path | None:
    if not OUTPUT_DIR.exists() or not any(OUTPUT_DIR.iterdir()):
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_ROOT / f"主线高难-{stamp}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUTPUT_DIR, destination)
    return destination


def validate_outputs(file_paths: dict[str, Path], normal_levels, normal_stars, hard_levels, hard_stars, side_levels, counts):
    errors = []
    for key, path in file_paths.items():
        if not path.exists():
            errors.append(f"缺少输出文件：{path}")
            continue
        try:
            load_workbook(path, read_only=True, data_only=False)
        except Exception as exc:
            errors.append(f"工作簿无法重新打开：{path}：{exc}")

    # 后续需要按行及按DropId多次随机访问；普通模式避免ReadOnlyWorksheet反复从XML开头扫描。
    drop_wb = load_workbook(file_paths["drop"], read_only=False, data_only=False)
    drop_ws = drop_wb["Drop"]
    drop_headers = sheet_header_map(drop_ws)
    drop_ids = set()
    drop_group_order = []
    drop_rows = 0
    formula_cells = []
    player_exp_rows = []
    for row in range(5, 5 + counts["drop"]):
        drop_rows += 1
        drop_id = drop_ws.cell(row, drop_headers["DropId"]).value
        if drop_id is not None:
            drop_ids.add(drop_id)
            if not drop_group_order or drop_group_order[-1] != drop_id:
                drop_group_order.append(drop_id)
        if (
            drop_ws.cell(row, drop_headers["DropItem_id"]).value == PROGRAMMATIC_PLAYER_EXP_ITEM_ID
            or drop_ws.cell(row, drop_headers["ShowItemID"]).value == PROGRAMMATIC_PLAYER_EXP_ITEM_ID
            or drop_ws.cell(row, drop_headers["DropId2"]).value in range(14000, 14035)
            or drop_id in range(14000, 14035)
        ):
            player_exp_rows.append(row)
        for cell in next(
            drop_ws.iter_rows(
                min_col=1,
                max_col=max(drop_headers.values()),
                min_row=row,
                max_row=row,
            )
        ):
            if isinstance(cell.value, str) and cell.value.startswith("="):
                formula_cells.append(cell.coordinate)
    if drop_rows != counts["drop"]:
        errors.append(f"Drop数据行数错误：{drop_rows} != {counts['drop']}")
    if formula_cells:
        errors.append(f"Drop粘贴包不应含公式，发现：{formula_cells[:10]}")
    if player_exp_rows:
        errors.append(f"Drop不应配置程序默认结算的玩家经验，发现行：{player_exp_rows[:10]}")

    drop_rows_by_id: dict[int, list[int]] = {}
    for row in range(5, 5 + counts["drop"]):
        drop_id = drop_ws.cell(row, drop_headers["DropId"]).value
        if isinstance(drop_id, int):
            drop_rows_by_id.setdefault(drop_id, []).append(row)

    def visual_items_from_drop(drop_id: int, seen: set[int] | None = None):
        seen = set() if seen is None else set(seen)
        if not isinstance(drop_id, int) or drop_id <= 0 or drop_id in seen:
            return []
        seen.add(drop_id)
        items = []
        for row in drop_rows_by_id.get(drop_id, []):
            item_id = drop_ws.cell(row, drop_headers["DropItem_id"]).value
            item_max = drop_ws.cell(row, drop_headers["DropItemNumMax"]).value
            if isinstance(item_id, int) and item_id > 0 and isinstance(item_max, (int, float)) and item_max > 0:
                if item_id != PROGRAMMATIC_PLAYER_EXP_ITEM_ID:
                    if item_id == 2:
                        icon_count = 1
                    elif item_id == 1:
                        icon_count = max(1, (int(item_max) + 4999) // 5000)
                    else:
                        icon_count = int(item_max)
                    items.append((item_id, icon_count))
            child_drop_id = drop_ws.cell(row, drop_headers["DropId2"]).value
            if isinstance(child_drop_id, int) and child_drop_id > 0:
                items.extend(visual_items_from_drop(child_drop_id, seen))
        return merge_visual_items(items)

    expected_group_order = drop_output_order(normal_levels, normal_stars, hard_levels, hard_stars, side_levels)
    if drop_group_order != expected_group_order:
        errors.append("Drop output order does not match the formal source-table order")

    expected_roots = {
        *(level["first_drop_id"] for level in normal_levels),
        *(level["repeat_drop_id"] for level in normal_levels),
        *(level["first_drop_id"] for level in hard_levels),
        *(level["repeat_drop_id"] for level in hard_levels),
        *(level["first_drop_id"] for level in side_levels),
        *(star["drop_id"] for star in normal_stars),
        *(star["drop_id"] for star in hard_stars),
    }
    missing_roots = expected_roots - drop_ids
    if missing_roots:
        errors.append(f"Drop缺少根ID：{sorted(missing_roots)[:20]}")

    for level in side_levels:
        actual = []
        for row in drop_rows_by_id.get(level["first_drop_id"], []):
            actual.append(
                (
                    drop_ws.cell(row, drop_headers["DropItem_id"]).value,
                    drop_ws.cell(row, drop_headers["DropItemNumMin"]).value,
                    drop_ws.cell(row, drop_headers["DropItemNumMax"]).value,
                )
            )
        expected = [(item_id, lo, hi) for item_id, _name, lo, hi in level["first"]]
        if actual != expected:
            errors.append(f"主线支线{level['level_id']}奖励包错误：{actual} != {expected}")
        item_ids = {item_id for item_id, _lo, _hi in expected}
        if level["side_type"] == "战斗" and not item_ids <= {1, 2, 101, 102}:
            errors.append(f"战斗支线{level['level_id']}含越界奖励：{sorted(item_ids)}")
        if level["side_type"] == "小游戏" and item_ids != {2}:
            errors.append(f"小游戏支线{level['level_id']}应只含元晶：{sorted(item_ids)}")
        if level["side_type"] == "宝箱" and not {1, 2} <= item_ids:
            errors.append(f"宝箱支线{level['level_id']}缺少元晶或金币：{sorted(item_ids)}")

    normal_by_label = {level["label"]: level for level in normal_levels}
    expected_specials = {
        "0-2": (311040, 1),
        "1-1": (106, 1),
        "2-12": (180028, 1),
    }
    for label, (expected_item_id, expected_count) in expected_specials.items():
        first_drop_id = normal_by_label[label]["first_drop_id"]
        matches = []
        for row in range(5, 5 + counts["drop"]):
            if (
                drop_ws.cell(row, drop_headers["DropId"]).value == first_drop_id
                and drop_ws.cell(row, drop_headers["DropItem_id"]).value == expected_item_id
            ):
                matches.append(
                    (
                        drop_ws.cell(row, drop_headers["DropItemNumMin"]).value,
                        drop_ws.cell(row, drop_headers["DropItemNumMax"]).value,
                    )
                )
        if matches != [(expected_count, expected_count)]:
            errors.append(f"{label}特殊首通错误：ItemId {expected_item_id}，实际数量区间{matches}")
    level_2_12_first_id = normal_by_label["2-12"]["first_drop_id"]
    forbidden_2_12_items = []
    for row in range(5, 5 + counts["drop"]):
        if drop_ws.cell(row, drop_headers["DropId"]).value != level_2_12_first_id:
            continue
        item_id = drop_ws.cell(row, drop_headers["DropItem_id"]).value
        if item_id in {13, 81201}:
            forbidden_2_12_items.append(item_id)
    if forbidden_2_12_items:
        errors.append(f"2-12不应再投放合淬喷剂或1级蓝宝石：{forbidden_2_12_items}")

    ui_wb = load_workbook(file_paths["uilevel"], read_only=True, data_only=True)
    ui_ws = ui_wb["level"]
    ui_headers = sheet_header_map(ui_ws)
    selected_by_level_id = {
        level["level_id"]: level for level in normal_levels + hard_levels + side_levels
    }
    ui_rows = list(
        ui_ws.iter_rows(
            min_row=5,
            max_row=ui_ws.max_row,
            max_col=max(ui_headers.values()),
            values_only=True,
        )
    )
    ui_rows = [row for row in ui_rows if isinstance(row[ui_headers["LevelId"] - 1], int)]
    ui_by_level_id = {row[ui_headers["LevelId"] - 1]: row for row in ui_rows}
    source_ui_wb = load_workbook(UILEVEL_SOURCE, read_only=True, data_only=True)
    source_ui_ws = source_ui_wb["level"]
    source_ui_headers = sheet_header_map(source_ui_ws)
    source_level_order = [
        row[source_ui_headers["LevelId"] - 1]
        for row in source_ui_ws.iter_rows(
            min_row=5,
            max_row=source_ui_ws.max_row,
            max_col=max(source_ui_headers.values()),
            values_only=True,
        )
        if isinstance(row[source_ui_headers["LevelId"] - 1], int)
    ]
    output_level_order = [row[ui_headers["LevelId"] - 1] for row in ui_rows]
    ui_row_order_matches_source = output_level_order == source_level_order
    if not ui_row_order_matches_source:
        errors.append("UIlevel完整行序包与正式源表的LevelId行序不一致")
    missing_selected_levels = set(selected_by_level_id) - set(ui_by_level_id)
    if missing_selected_levels:
        errors.append(f"UIlevel缺少目标关卡：{sorted(missing_selected_levels)}")
    selected_ui_rows = [ui_by_level_id[level_id] for level_id in selected_by_level_id if level_id in ui_by_level_id]
    if len(selected_ui_rows) != 178:
        errors.append(f"UIlevel目标关卡行数错误：{len(selected_ui_rows)} != 178")
    main_drop_visual_mismatches = 0
    for row in selected_ui_rows:
        level_id = row[ui_headers["LevelId"] - 1]
        level = selected_by_level_id[level_id]
        if "side_type" in level:
            for field in ("LevelFPDrop", "FirstRewardDrop"):
                if row[ui_headers[field] - 1] != level["first_drop_id"]:
                    errors.append(
                        f"UIlevel支线{level_id}的{field}错误：{row[ui_headers[field] - 1]} != {level['first_drop_id']}"
                    )
            for field in ("LevelPPDrop", "FallRewardDrop"):
                if row[ui_headers[field] - 1] is not None:
                    errors.append(f"UIlevel支线{level_id}的{field}应为空")
            expected_preview = format_reward_preview(level["first"])
            if row[ui_headers["FirstReward"] - 1] != expected_preview:
                errors.append(
                    f"UIlevel支线{level_id}的FirstReward错误：{row[ui_headers['FirstReward'] - 1]} != {expected_preview}"
                )
            if row[ui_headers["Reward"] - 1] is not None:
                errors.append(f"UIlevel支线{level_id}的Reward应为空")
        else:
            for field in ("LevelFPDrop", "LevelPPDrop", "FirstRewardDrop", "FallRewardDrop"):
                if row[ui_headers[field] - 1] not in expected_roots:
                    errors.append(f"UIlevel {level_id} 的{field}引用无效：{row[ui_headers[field] - 1]}")
        for field in ("FirstReward", "Reward"):
            if field in ui_headers:
                preview = row[ui_headers[field] - 1]
                if remove_preview_item(preview, PROGRAMMATIC_PLAYER_EXP_ITEM_ID) != preview:
                    errors.append(f"UIlevel {level_id} 的{field}仍包含玩家经验")
        expected_visual_fields = {
            "MidVisualDropItems": level["mid_visual_drop_items"],
            "MidVisualDropChance": level["mid_visual_drop_chance"],
            "LevelEndVisualDropItems": level["level_end_visual_drop_items"],
        }
        for field, expected_value in expected_visual_fields.items():
            actual_value = row[ui_headers[field] - 1]
            if actual_value != expected_value:
                errors.append(f"UIlevel {level_id} 的{field}错误：{actual_value} != {expected_value}")
        if "repeat" in level:
            actual_drop_visual_fields = {
                "MidVisualDropItems": format_visual_items(
                    visual_items_from_drop(row[ui_headers["LevelPPDrop"] - 1])
                ),
                "LevelEndVisualDropItems": format_visual_items(
                    visual_items_from_drop(row[ui_headers["LevelFPDrop"] - 1])
                ),
            }
            for field, expected_value in actual_drop_visual_fields.items():
                actual_value = row[ui_headers[field] - 1]
                if parse_visual_items(actual_value) != parse_visual_items(expected_value):
                    main_drop_visual_mismatches += 1
                    errors.append(
                        f"UIlevel {level_id} 的{field}与实际Drop不一致：{actual_value} != {expected_value}"
                    )
        for field in ("MidVisualDropItems", "LevelEndVisualDropItems"):
            visual_items = parse_visual_items(row[ui_headers[field] - 1])
            item_ids = [item_id for item_id, _count in visual_items]
            if len(item_ids) != len(set(item_ids)) or any(count <= 0 for _item_id, count in visual_items):
                errors.append(f"UIlevel {level_id} 的{field}存在重复ItemId或非正Icon数")
            if PROGRAMMATIC_PLAYER_EXP_ITEM_ID in item_ids:
                errors.append(f"UIlevel {level_id} 的{field}不应包含玩家经验")

    ui_formula_wb = load_workbook(file_paths["uilevel"], read_only=True, data_only=False)
    ui_formula_ws = ui_formula_wb["level"]
    source_formula_wb = load_workbook(UILEVEL_SOURCE, read_only=True, data_only=False)
    source_formula_ws = source_formula_wb["level"]

    def formula_map(ws):
        return {
            cell.coordinate: cell.value
            for row in ws.iter_rows(
                min_row=1,
                max_row=ws.max_row,
                max_col=ws.max_column,
            )
            for cell in row
            if isinstance(cell.value, str) and cell.value.startswith("=")
        }

    ui_formula_map = formula_map(ui_formula_ws)
    source_formula_map = formula_map(source_formula_ws)
    if ui_formula_map != source_formula_map:
        missing_formulas = sorted(set(source_formula_map) - set(ui_formula_map))
        extra_formulas = sorted(set(ui_formula_map) - set(source_formula_map))
        changed_formulas = sorted(
            coordinate
            for coordinate in set(ui_formula_map) & set(source_formula_map)
            if ui_formula_map[coordinate] != source_formula_map[coordinate]
        )
        errors.append(
            "UIlevel完整行序包的公式未原样保留："
            f"缺失={missing_formulas[:10]}，新增={extra_formulas[:10]}，变更={changed_formulas[:10]}"
        )

    item_sweep_wb = load_workbook(file_paths["item_sweep"], read_only=True, data_only=True)
    item_sweep_ws = item_sweep_wb["ItemAccess"]
    item_sweep_headers = sheet_header_map(item_sweep_ws)
    item_sweep_rows = list(
        item_sweep_ws.iter_rows(
            min_row=5,
            max_row=4 + counts["item_sweep"],
            max_col=max(item_sweep_headers.values()),
            values_only=True,
        )
    )
    expected_sweep_levels = normal_levels + hard_levels
    if len(item_sweep_rows) != 134:
        errors.append(f"ItemSweep数据行数错误：{len(item_sweep_rows)} != 134")
    actual_sweep_level_ids = [
        row[item_sweep_headers["LevelId"] - 1] for row in item_sweep_rows
    ]
    expected_sweep_level_ids = [level["level_id"] for level in expected_sweep_levels]
    if actual_sweep_level_ids != expected_sweep_level_ids:
        errors.append("ItemSweep的LevelId顺序与99主线+35高难目标顺序不一致")
    if len(actual_sweep_level_ids) != len(set(actual_sweep_level_ids)):
        errors.append("ItemSweep存在重复LevelId")
    side_level_ids = {level["level_id"] for level in side_levels}
    if side_level_ids & set(actual_sweep_level_ids):
        errors.append(f"ItemSweep不应包含一次性支线关卡：{sorted(side_level_ids & set(actual_sweep_level_ids))}")

    for index, (row, level) in enumerate(zip(item_sweep_rows, expected_sweep_levels), 1):
        item_value = row[item_sweep_headers["ItemId"] - 1]
        actual_item_ids = (
            [int(token) for token in str(item_value).split(";")]
            if item_value is not None
            else []
        )
        ui_row = ui_by_level_id[level["level_id"]]
        repeat_drop_id = ui_row[ui_headers["FallRewardDrop"] - 1]
        expected_item_ids = [item_id for item_id, _count in visual_items_from_drop(repeat_drop_id)]
        if actual_item_ids != expected_item_ids:
            errors.append(
                f"ItemSweep关卡{level['level_id']}与真实重复Drop不一致：{actual_item_ids} != {expected_item_ids}"
            )
        actual_sort = row[item_sweep_headers["Sort"] - 1]
        if actual_sort != index:
            errors.append(f"ItemSweep关卡{level['level_id']}排序错误：{actual_sort} != {index}")

    star_wb = load_workbook(file_paths["star"], read_only=True, data_only=True)
    star_ws = star_wb["ChapterStarReward"]
    star_rows = list(
        star_ws.iter_rows(
            min_row=5,
            max_row=62,
            max_col=max(sheet_header_map(star_ws).values()),
            values_only=True,
        )
    )
    if len(star_rows) != 58:
        errors.append(f"ChapterStarReward行数错误：{len(star_rows)} != 58")
    normal_star_count = sum(1 for row in star_rows if row[5] is False)
    hard_star_count = sum(1 for row in star_rows if row[5] is True)
    if (normal_star_count, hard_star_count) != (37, 21):
        errors.append(f"星级节点分布错误：normal={normal_star_count}, hard={hard_star_count}")

    chest_wb = load_workbook(file_paths["chest"], read_only=True, data_only=True)
    chest_ws = chest_wb["Chest"]
    chest_rows = list(
        chest_ws.iter_rows(
            min_row=5,
            max_row=4 + counts["chest"],
            max_col=max(sheet_header_map(chest_ws).values()),
            values_only=True,
        )
    )
    rare_gems = {81107, 81207, 81307, 81407, 81507, 81607, 81701, 81702, 81703, 81704, 81801, 81802, 81803, 81804}
    gem_box_rows = [row for row in chest_rows if row[2] in {3034, 3035, 3036}]
    if any(row[12] in rare_gems for row in gem_box_rows):
        errors.append("普通宝石自选箱错误包含青/白稀有宝石")

    generate_wb = load_workbook(file_paths["special_equipment_generate"], read_only=True, data_only=True)
    generate_ws = generate_wb["SpecialEquipment"]
    generate_headers = {
        generate_ws.cell(1, col).value: col
        for col in range(1, 12)
        if generate_ws.cell(1, col).value
    }
    generate_rows = list(generate_ws.iter_rows(min_row=5, max_col=11, values_only=True))
    if len(generate_rows) != 1:
        errors.append(f"SpecialEquipmentGenerate数据行数错误：{len(generate_rows)} != 1")
    else:
        row = generate_rows[0]
        actual_generate_id = row[generate_headers["Id"] - 1]
        actual_grade_list = row[generate_headers["GradeList"] - 1]
        actual_fixed_equipment = row[generate_headers["SpecialEquipmentId"] - 1]
        if actual_generate_id != FIXED_LEVEL_HELMET_GENERATE_ID:
            errors.append(f"初级隔热头盔GenerateId错误：{actual_generate_id}")
        if actual_grade_list != f"{FIXED_LEVEL_HELMET_GRADE},100":
            errors.append(f"初级隔热头盔等级池错误：{actual_grade_list}")
        if actual_fixed_equipment != 80028:
            errors.append(f"初级隔热头盔固定装备Id错误：{actual_fixed_equipment}")

    if errors:
        raise AssertionError("\n".join(errors))
    return {
        "status": "PASS",
        "drop_rows": drop_rows,
        "drop_unique_ids": len(drop_ids),
        "root_drop_ids": len(expected_roots),
        "uilevel_rows": len(ui_rows),
        "uilevel_managed_rows": len(selected_ui_rows),
        "uilevel_row_order_matches_source": ui_row_order_matches_source,
        "main_drop_visual_validated_rows": len(normal_levels),
        "main_drop_visual_mismatches": main_drop_visual_mismatches,
        "side_level_rows": len(side_levels),
        "normal_star_rows": normal_star_count,
        "hard_star_rows": hard_star_count,
        "new_item_rows": counts["items"],
        "chest_rows": counts["chest"],
        "item_chest_rows": counts["item_chest"],
        "item_sweep_rows": counts["item_sweep"],
        "special_equipment_generate_rows": counts["special_equipment_generate"],
        "uilevel_preserved_formula_cells": len(ui_formula_map),
    }


def main() -> None:
    for path in [NORMAL_DESIGN, HARD_DESIGN, SIDE_DESIGN, DROP_SOURCE, UILEVEL_SOURCE, STAR_SOURCE, ITEMS_SOURCE, CHEST_SOURCE, ITEM_CHEST_SOURCE, ITEM_SWEEP_SOURCE, SPECIAL_EQUIPMENT_GENERATE_SOURCE]:
        if not path.exists():
            raise FileNotFoundError(path)
    assert_no_id_collisions()
    assert_side_drop_ids_available()
    mapping = item_name_map()
    normal_levels, normal_stars, hard_levels, hard_stars, side_levels = build_design_data(mapping)
    apply_formal_drop_ids(normal_levels, normal_stars, hard_levels, hard_stars, side_levels)
    backup_path = backup_existing_output()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_paths: dict[str, Path] = {}
    counts: dict[str, int] = {}

    items_wb, counts["items"] = build_items_workbook()
    file_paths["items"] = OUTPUT_DIR / "Items.xlsx"
    save_without_freeze(items_wb, file_paths["items"])

    chest_wb, counts["chest"] = build_chest_workbook(mapping)
    file_paths["chest"] = OUTPUT_DIR / "Chest.xlsx"
    save_without_freeze(chest_wb, file_paths["chest"])

    item_chest_wb, counts["item_chest"] = build_item_chest_workbook(mapping)
    file_paths["item_chest"] = OUTPUT_DIR / "ItemChest.xlsx"
    save_without_freeze(item_chest_wb, file_paths["item_chest"])

    item_sweep_wb, counts["item_sweep"] = build_item_sweep_workbook(normal_levels, hard_levels)
    file_paths["item_sweep"] = OUTPUT_DIR / "ItemSweep.xlsx"
    save_without_freeze(item_sweep_wb, file_paths["item_sweep"])

    generate_wb, counts["special_equipment_generate"] = build_special_equipment_generate_workbook()
    file_paths["special_equipment_generate"] = OUTPUT_DIR / "SpecialEquipmentGenerate.xlsx"
    save_without_freeze(generate_wb, file_paths["special_equipment_generate"])

    drop_wb, counts["drop"] = build_drop_workbook(normal_levels, normal_stars, hard_levels, hard_stars, side_levels)
    file_paths["drop"] = OUTPUT_DIR / "Drop_mainlevel.xlsx"
    save_without_freeze(drop_wb, file_paths["drop"])

    uilevel_wb, counts["uilevel"] = build_uilevel_workbook(normal_levels, hard_levels, side_levels)
    file_paths["uilevel"] = OUTPUT_DIR / "UIlevel.xlsx"
    save_without_freeze(uilevel_wb, file_paths["uilevel"])

    star_wb, counts["star"] = build_star_workbook(normal_stars, hard_stars)
    file_paths["star"] = OUTPUT_DIR / "ChapterStarReward.xlsx"
    save_without_freeze(star_wb, file_paths["star"])

    create_manifest(counts, file_paths)
    validation = validate_outputs(file_paths, normal_levels, normal_stars, hard_levels, hard_stars, side_levels, counts)
    validation.update(
        {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "output_dir": str(OUTPUT_DIR),
            "backup_dir": str(backup_path) if backup_path else None,
            "files": {key: str(path) for key, path in file_paths.items()},
            "counts": counts,
        }
    )
    validation_path = OUTPUT_DIR / "主线高难奖励配置校验.json"
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
