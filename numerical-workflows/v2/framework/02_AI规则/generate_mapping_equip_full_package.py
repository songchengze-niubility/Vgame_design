#!/usr/bin/env python3
"""生成映射装备全链路映射配置包 P02。

权威数值只从沉淀 MD 读取；正式 Vgame Datas 只读取 Schema、现状引用和
ID 占用情况。本脚本不修改任何正式配置，也不执行 Luban。

P02 的目标是同时交付：
1. 已有 Schema 能承载的精确纯值块；
2. 数值已完整但需新 Schema/程序的映射表；
3. 可评审的 ID 分配和首通重配提案；
4. 正式落表前必须解除的阻断和验收断言。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path
from typing import Iterable, Sequence

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import generate_mapping_equip_paste_package as p01


PACKAGE_ID = "MAPEQUIP-20260710-P02"
PACKAGE_VERSION = "2.4"
WEIGHT_SCALE = 10_000

FRAME_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = FRAME_ROOT / "04_数值文档" / "配置粘贴包" / "映射装备全链路配置包_P02.xlsx"
DEFAULT_REPORT = FRAME_ROOT / "05_验算核算" / "mapping-equip-full-package-P02-generation.json"
DEFAULT_CONFIG_ROOT = Path(os.environ.get("VGAME_CONFIG_DATAS", ""))

ATTR_MD = FRAME_ROOT / "03_沉淀MD" / "养成" / "映射装备养成数值沉淀-2026-07-07.md"
DROP_MD = FRAME_ROOT / "03_沉淀MD" / "经济" / "05_玩法_映射副本经济沉淀-2026-07-08.md"
ECON_MD = FRAME_ROOT / "03_沉淀MD" / "经济" / "21_养成_映射装备经济消耗沉淀-2026-07-09.md"
PARAM_MD = FRAME_ROOT / "03_沉淀MD" / "养成" / "映射装备数值总表生成参数-2026-07-10.md"

TARGET_FILES = [
    "Attribute/Attribute.xlsx",
    "SpecialEquipment/SpecialEquipment.xlsx",
    "SpecialEquipment/SpecialEquipmentMain.xlsx",
    "SpecialEquipment/SpecialEquipmentQuality.xlsx",
    "SpecialEquipment/SpecialEquipmentSubAttrCoef.xlsx",
    "SpecialEquipment/SpecialEquipmentEffect.xlsx",
    "SpecialEquipment/SpecialEquipmentEffectDrop.xlsx",
    "SpecialEquipment/SpecialEquipmentGenerate.xlsx",
    "SpecialEquipment/SpecialEquipmentLvUp.xlsx",
    "SpecialEquipment/SpecialEquipmentLvLimit.xlsx",
    "SpecialEquipment/Portable/PortableExp.xlsx",
    "SpecialEquipment/Portable/PortableLvUp.xlsx",
    "SpecialEquipment/Portable/PortableCompoundProb.xlsx",
    "SpecialEquipment/Portable/PortableCraftProb.xlsx",
    "SpecialEquipment/Portable/PortableEquipCompound.xlsx",
    "SpecialEquipment/Portable/PortableEquipCraft.xlsx",
    "SpecialEquipment/Portable/PortableRange.xlsx",
    "items/Items.xlsx",
    "items/ItemAccess.xlsx",
    "items/ItemChest.xlsx",
    "Drop/Drop_dungeon.xlsx",
    "level/UIlevel.xlsx",
    "level/EquipmentLevel.xlsx",
    "level/SpecialLevel.xlsx",
    "level/LevelType.xlsx",
    "level/level.xlsx",
    "system_open/SystemOpen.xlsx",
    "unlock/Unlock.xlsx",
    "globals_conf/globals_conf.xlsx",
]

LEVELS = list(range(5, 61, 5))
QUALITIES = ["Green", "Blue", "Purple", "Orange", "Red"]
QUALITY_CN = {"Green": "绿", "Blue": "蓝", "Purple": "紫", "Orange": "金", "Red": "红"}
QUALITY_MAIN = {"Green": Decimal("0.20"), "Blue": Decimal("0.30"), "Purple": Decimal("0.45"), "Orange": Decimal("0.70"), "Red": Decimal("1.00")}
QUALITY_SUB = {"Green": Decimal("0.50"), "Blue": Decimal("0.60"), "Purple": Decimal("0.70"), "Orange": Decimal("0.85"), "Red": Decimal("1.00")}

PARTS = [
    ("武器", "SEPart_Weapon", "攻击", "Attack", Decimal("11250"), "数值"),
    ("头盔", "SEPart_Head", "生命", "Hp", Decimal("18750"), "数值"),
    ("护甲（衣服）", "SEPart_Armour", "生命", "Hp", Decimal("18750"), "数值"),
    ("手套", "SEPart_Glove", "防御", "Armor", Decimal("2500"), "数值"),
    ("腰带", "SEPart_Belt", "防御", "Armor", Decimal("2500"), "数值"),
    ("鞋子", "SEPart_Shoe", "防御", "Armor", Decimal("2500"), "数值"),
    ("装置", "SEPart_Device", "暴击伤害等级", "CritDmgBonusLevel", Decimal("8800"), "等级"),
    ("饰品", "SEPart_Decoration", "暴击等级", "CritLevel", Decimal("7200"), "等级"),
]

SUB_ATTRIBUTES = [
    ("攻击百分比", "AttackBonus", Decimal("0.329"), "比例"),
    ("防御百分比", "ArmorBonus", Decimal("0.329"), "比例"),
    ("生命百分比", "HpBonus", Decimal("0.329"), "比例"),
    ("攻击", "Attack", Decimal("3701"), "数值"),
    ("防御", "Armor", Decimal("2468"), "数值"),
    ("生命", "Hp", Decimal("12338"), "数值"),
    ("暴击等级", "CritLevel", Decimal("2961"), "等级"),
    ("暴击伤害等级", "CritDmgBonusLevel", Decimal("3619"), "等级"),
    ("能量回复等级", "EnergyPreAddBonusLevel", Decimal("2961"), "等级"),
    ("技能冷却等级", "CoolDownReduceLevel", Decimal("4277"), "等级"),
]

CRAFT_TIERS = [10, 20, 30, 40, 45, 50, 55, 60]
MATERIAL_CATEGORIES = [("武器", "Weapon", Decimal("0.20")), ("防具", "Armor", Decimal("0.55")), ("首饰", "Accessory", Decimal("0.25"))]
MATERIAL_QUALITIES = [("紫", "Purple"), ("金", "Orange"), ("红", "Red")]
CATEGORY_CN = {enum: cn for cn, enum, _ in MATERIAL_CATEGORIES}
MATERIAL_QUALITY_CN = {enum: cn for cn, enum in MATERIAL_QUALITIES}

BOX_ITEM_BASE = 4201
MATERIAL_ITEM_BASE = 1080
SUB_MATERIAL_ITEM_BASE = 1152
PREVIEW_ITEM_BASE = 4351
GENERATE_ID_BASE = 4201
REGULAR_BOX_POOL_BASE = 22101
EXTRA_BOX_POOL_BASE = 22201
MAIN_MATERIAL_POOL_BASE = 22301
SUB_MATERIAL_POOL_ID = 22400
FIRST_RANDOM_POOL_BASE = 22451
CRAFT_UNLOCK_LAYER = 6
CRAFT_UNLOCK_LEVEL_ID = 250061
CRAFT_MATERIAL_START_LAYER = CRAFT_UNLOCK_LAYER

PREVIEW_GRADE_BOX_ITEM_IDS = {
    5: PREVIEW_ITEM_BASE,
    10: PREVIEW_ITEM_BASE + 1,
    15: PREVIEW_ITEM_BASE + 2,
    20: PREVIEW_ITEM_BASE + 3,
    25: PREVIEW_ITEM_BASE + 14,
    30: PREVIEW_ITEM_BASE + 15,
    35: PREVIEW_ITEM_BASE + 16,
    40: PREVIEW_ITEM_BASE + 17,
    45: PREVIEW_ITEM_BASE + 18,
    50: PREVIEW_ITEM_BASE + 19,
    55: PREVIEW_ITEM_BASE + 20,
    60: PREVIEW_ITEM_BASE + 21,
}
PREVIEW_MAIN_ITEM_IDS = {
    (10, "Purple"): PREVIEW_ITEM_BASE + 4,
    (20, "Purple"): PREVIEW_ITEM_BASE + 5,
    (30, "Purple"): PREVIEW_ITEM_BASE + 6,
    (30, "Orange"): PREVIEW_ITEM_BASE + 7,
    (40, "Orange"): PREVIEW_ITEM_BASE + 8,
    (45, "Orange"): PREVIEW_ITEM_BASE + 9,
    (50, "Red"): PREVIEW_ITEM_BASE + 10,
    (55, "Red"): PREVIEW_ITEM_BASE + 11,
    (60, "Red"): PREVIEW_ITEM_BASE + 12,
}
PREVIEW_SUB_ITEM_ID = PREVIEW_ITEM_BASE + 13

# 可见表头采用“中文业务含义\n正式英文字段”。英文名保留在第二行，
# 便于与 Vgame ##var 逐列对照，不改数据起始行和复制坐标。
HEADER_CN = {
    "RowId": "行序号",
    "Id": "配置ID",
    "ID(公式列留空)": "表ID（公式列留空）",
    "Name": "名称",
    "##Name": "策划备注名",
    "Part": "部位枚举",
    "Attribute": "属性枚举",
    "Quality": "品质枚举",
    "EquipLv": "装备等级",
    "Red60Target": "60级红装目标",
    "QualityCoef": "品质系数",
    "FormulaLevelCoef": "公式等级系数",
    "MDDisplayCoef3": "MD三位展示系数",
    "TargetValue": "目标数值",
    "Unit": "单位",
    "Status": "状态",
    "Layer": "副本层数",
    "KeyItemId": "消耗匙道具ID",
    "FixedBoxes": "固定宝箱数",
    "ExtraBoxProb": "额外宝箱概率",
    "ExpectedBoxes": "期望宝箱数",
    "GreenBox": "绿宝箱概率",
    "BlueBox": "蓝宝箱概率",
    "PurpleBox": "紫宝箱概率",
    "OrangeBox": "金宝箱概率",
    "RedBox": "红宝箱概率",
    "GradeList1000": "装备等级池（千分权重）",
    "MaterialLevel": "MD主材等级",
    "CraftTier": "打造档位",
    "MainMatProb": "主材掉率",
    "PurpleMat": "紫主材品质概率",
    "OrangeMat": "金主材品质概率",
    "RedMat": "红主材品质概率",
    "SubMatCount": "副材总量",
    "FirstArchive": "首通旧奖励留档",
    "ParaList": "参数列表",
    "ItemType": "道具类型",
    "ItemSubType": "道具子类型",
    "ChestOpenMode": "宝箱开启方式",
    "Icon": "图标",
    "LittleIcon": "小图标",
    "ItemQuality": "道具品质",
    "Description": "描述",
    "##": "控制/备注列",
    "AccessList": "获取途径列表",
    "ShopId": "商店ID",
    "NumLimit": "持有上限",
    "RelatedId": "关联ID",
    "IsValid": "是否有效",
    "GradeList": "等级权重列表",
    "QualityList": "品质权重列表",
    "UnidentifiedList": "未鉴定列表",
    "PartList": "部位列表",
    "SpecialEquipmentId": "指定映射装备ID",
    "GenerateMax": "生成数量上限",
    "GenerateMin": "生成数量下限",
    "Category": "主材大类",
    "MaterialQuality": "主材品质",
    "SubMaterialIndex": "副材序号",
    "DropId": "掉落包ID",
    "DropName": "掉落包名称",
    "DropId2": "二级掉落包ID",
    "DropType": "掉落类型",
    "DropMinNum": "掉落次数下限",
    "DropMaxNum": "掉落次数上限",
    "DropItem_id": "掉落道具ID",
    "DropItemNumMin": "道具数量下限",
    "DropItemNumMax": "道具数量上限",
    "DropWeight": "掉落权重",
    "ShowItemID": "掉落预览道具ID",
    "FirstRewardDrop": "首通掉落包ID",
    "FallRewardDrop": "通关掉落包ID",
    "EquipmentQuality": "装备品质",
    "UiLevelId": "UI关卡ID",
    "LevelId": "关卡ID",
    "LevelType": "关卡类型",
    "TierNum": "层数",
    "Variant": "多倍结算变体",
    "Unlock": "解锁条件",
    "Reward": "常规奖励预览",
    "FirstReward": "首通奖励预览",
    "MultiSettlementTimes": "可多倍结算次数",
    "Vitality": "挑战消耗",
    "CurrentGotoId": "当前跳转ID",
    "ProposedGotoId": "建议跳转ID",
    "SaoDangSupport": "是否支持扫荡",
    "Note": "备注",
    "Step": "步骤",
    "P02 Sheet": "P02工作表",
    "Exp": "提供经验",
    "SubAttrCoef": "副属性等级系数",
    "TargetLv": "目标等级",
    "CostExp": "所需经验",
    "Grade": "锻造台等级",
    "PortableLv": "锻造台等级",
    "Green": "绿品质权重",
    "Blue": "蓝品质权重",
    "Purple": "紫品质权重",
    "Orange": "金品质权重",
    "Red": "红品质权重",
    "CostCurrency": "金币消耗",
    "ExtraItemList": "额外道具列表",
    "GradeCoefficient": "主属性品质系数",
    "QualityCoefficient": "品质参数系数",
}


def bilingual_header(value: object) -> object:
    if value is None or not isinstance(value, str) or "\n" in value:
        return value
    chinese = HEADER_CN.get(value)
    return f"{chinese}\n{value}" if chinese else value


def apply_bilingual_headers(ws, row: int = 4) -> None:
    has_bilingual = False
    for cell in ws[row]:
        new_value = bilingual_header(cell.value)
        if new_value != cell.value:
            cell.value = new_value
            has_bilingual = True
        if isinstance(cell.value, str) and "\n" in cell.value:
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if has_bilingual:
        ws.row_dimensions[row].height = 44


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_records(config_root: Path) -> list[dict]:
    records = []
    for relative_path in TARGET_FILES:
        path = config_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append({"relative_path": relative_path, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return records


def md_records() -> list[dict]:
    rows = []
    for path in [ATTR_MD, DROP_MD, ECON_MD, PARAM_MD]:
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def split_md_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def md_table(text: str, required_headers: Sequence[str]) -> list[dict[str, str]]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        headers = split_md_row(line)
        if all(header in headers for header in required_headers):
            rows: list[dict[str, str]] = []
            for raw in lines[index + 2 :]:
                if not raw.lstrip().startswith("|"):
                    break
                cells = split_md_row(raw)
                if len(cells) < len(headers):
                    cells += [""] * (len(headers) - len(cells))
                rows.append(dict(zip(headers, cells)))
            if rows:
                return rows
    raise ValueError(f"未在MD中找到表: {required_headers}")


def decimal_number(value: str) -> Decimal:
    cleaned = value.strip().replace(",", "")
    if cleaned.endswith("%"):
        return Decimal(cleaned[:-1]) / Decimal(100)
    return Decimal(cleaned)


def percent_list(value: str, expected: int) -> list[Decimal]:
    parts = [decimal_number(item.strip()) for item in value.split("/")]
    if len(parts) != expected:
        raise ValueError((value, expected))
    if sum(parts) != Decimal(1):
        raise ValueError(f"权重和不为1: {value}")
    return parts


def grade_list(value: str) -> list[tuple[int, Decimal]]:
    result = []
    for level, probability in re.findall(r"(\d+)\s*:\s*([\d.]+)%", value):
        result.append((int(level), Decimal(probability) / Decimal(100)))
    if not result or sum(probability for _, probability in result) != Decimal(1):
        raise ValueError(f"等级池非法: {value}")
    return result


def allocate_weights(entries: Sequence[tuple[object, Decimal]], scale: int = WEIGHT_SCALE) -> list[tuple[object, int]]:
    """最大余数法，保证权重严格合计 scale。"""
    if sum(probability for _, probability in entries) != Decimal(1):
        raise ValueError(f"概率和不为1: {entries}")
    raw = [(key, probability * scale) for key, probability in entries]
    floors = [(key, int(value.to_integral_value(rounding=ROUND_FLOOR))) for key, value in raw]
    remain = scale - sum(weight for _, weight in floors)
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i][1] - floors[i][1]), i))
    weights = [weight for _, weight in floors]
    for index in order[:remain]:
        weights[index] += 1
    return [(raw[index][0], weights[index]) for index in range(len(raw))]


def as_number(value: Decimal, places: int = 9) -> int | float:
    quant = Decimal(1).scaleb(-places)
    rounded = value.quantize(quant)
    if rounded == rounded.to_integral_value():
        return int(rounded)
    return float(rounded)


def main_formula_coef(level: int) -> Decimal:
    if level == 5:
        return Decimal("0.05")
    if level == 60:
        return Decimal(1)
    # Decimal 没有可移植的小数幂；用 float 求幂后立即转回 Decimal。
    value = 0.05 + 0.95 * (((level - 5) / 55) ** 1.35)
    return Decimal(str(value))


def sub_formula_coef(level: int) -> Decimal:
    return Decimal("0.40") + Decimal("0.60") * Decimal(level - 5) / Decimal(55)


def box_item_id(layer: int, quality: str) -> int:
    return BOX_ITEM_BASE + (layer - 1) * len(QUALITIES) + QUALITIES.index(quality)


def generate_id(layer: int, quality: str) -> int:
    return GENERATE_ID_BASE + (layer - 1) * len(QUALITIES) + QUALITIES.index(quality)


def craft_tier(material_level: int) -> int:
    mapping = {10: 10, 15: 20, 20: 20, 25: 30, 30: 30, 35: 40, 40: 40, 45: 45, 50: 50, 55: 55, 60: 60}
    return mapping[material_level]


def material_item_id(tier: int, category: str, quality: str) -> int:
    tier_index = CRAFT_TIERS.index(tier)
    category_index = [item[1] for item in MATERIAL_CATEGORIES].index(category)
    quality_index = [item[1] for item in MATERIAL_QUALITIES].index(quality)
    return MATERIAL_ITEM_BASE + tier_index * 9 + category_index * 3 + quality_index


def sub_material_item_id(index: int) -> int:
    if index not in (1, 2, 3, 4):
        raise ValueError(index)
    return SUB_MATERIAL_ITEM_BASE + index - 1


def load_md_model() -> dict:
    attr_text = ATTR_MD.read_text(encoding="utf-8")
    drop_text = DROP_MD.read_text(encoding="utf-8")

    # 除数值外，还对 MD 内的部位、属性和品质集合做同步断言。
    part_rows = md_table(attr_text, ["部位", "主属性", "口径"])
    if [(row["部位"], row["主属性"]) for row in part_rows] != [(row[0], row[2]) for row in PARTS]:
        raise AssertionError("MD部位/主属性与映射字典不一致")

    quality_rows = md_table(attr_text, ["品质", "主属性品质系数", "副属性品质系数"])
    quality_model = {}
    for row in quality_rows:
        quality = next(key for key, cn in QUALITY_CN.items() if cn == row["品质"])
        quality_model[quality] = (decimal_number(row["主属性品质系数"]), decimal_number(row["副属性品质系数"]))
    if quality_model != {quality: (QUALITY_MAIN[quality], QUALITY_SUB[quality]) for quality in QUALITIES}:
        raise AssertionError(quality_model)

    main_coef_rows = md_table(attr_text, ["等级", "主属性等级倍率"])
    sub_coef_rows = md_table(attr_text, ["等级", "副属性等级倍率"])
    main_display_coef = {int(row["等级"]): decimal_number(row["主属性等级倍率"]) for row in main_coef_rows}
    sub_display_coef = {int(row["等级"]): decimal_number(row["副属性等级倍率"]) for row in sub_coef_rows}
    if sorted(main_display_coef) != LEVELS or sorted(sub_display_coef) != LEVELS:
        raise AssertionError("属性等级系数不是12档")

    main_target_rows = md_table(attr_text, ["主属性", "目标值", "说明"])
    parsed_main_targets = {row["主属性"]: decimal_number(row["目标值"].replace("%", "")) for row in main_target_rows}
    # 百分比在MD中同时给出80%与“按0.80参与计算”，实际用小数口径由PARTS锁定。
    for part in PARTS:
        if part[2] not in parsed_main_targets:
            raise AssertionError(f"MD缺主属性目标: {part[2]}")

    sub_target_rows = md_table(attr_text, ["副属性", "60级红装单条下限", "60级红装单条上限", "换算说明"])
    parsed_sub_names = [row["副属性"] for row in sub_target_rows]
    if parsed_sub_names != [row[0] for row in SUB_ATTRIBUTES]:
        raise AssertionError("副属性集合/顺序与MD不一致")

    dungeon_rows = md_table(drop_text, ["层", "消耗", "固定宝箱", "额外宝箱概率", "宝箱档位概率(绿/蓝/紫/金/红)", "装备等级池"])
    material_rows = md_table(drop_text, ["层", "主材等级", "主材掉率", "主材品质权重(紫/金/红)", "副材总量"])
    first_rows = md_table(drop_text, ["层", "固定返还", "首通额外奖励", "周期口径"])
    if not (len(dungeon_rows) == len(material_rows) == len(first_rows) == 30):
        raise AssertionError("副本MD不是30层")

    layers = []
    for dungeon, material, first in zip(dungeon_rows, material_rows, first_rows):
        layer = int(dungeon["层"])
        if int(material["层"]) != layer or int(first["层"]) != layer:
            raise AssertionError("副本MD表层号错位")
        chest_probs = percent_list(dungeon["宝箱档位概率(绿/蓝/紫/金/红)"], 5)
        material_quality_probs = percent_list(material["主材品质权重(紫/金/红)"], 3)
        grade_probs = grade_list(dungeon["装备等级池"])
        material_level = int(material["主材等级"])
        layers.append(
            {
                "layer": layer,
                "fixed_boxes": int(dungeon["固定宝箱"]),
                "extra_box_prob": decimal_number(dungeon["额外宝箱概率"]),
                "expected_boxes": decimal_number(dungeon["期望宝箱"]),
                "chest_probs": dict(zip(QUALITIES, chest_probs)),
                "grade_probs": grade_probs,
                "material_level": material_level,
                "craft_tier": craft_tier(material_level),
                "main_material_prob": decimal_number(material["主材掉率"]),
                "main_quality_probs": dict(zip([row[1] for row in MATERIAL_QUALITIES], material_quality_probs)),
                "sub_material_count": int(material["副材总量"]),
                "first_archive": first["首通额外奖励"],
            }
        )
    if any(layer["main_material_prob"] != 0 or layer["sub_material_count"] != 0 for layer in layers[:CRAFT_MATERIAL_START_LAYER - 1]):
        raise AssertionError("映射装备第1～5层不应投放打造主材/副材")
    if layers[CRAFT_MATERIAL_START_LAYER - 1]["main_material_prob"] <= 0 or layers[CRAFT_MATERIAL_START_LAYER - 1]["sub_material_count"] <= 0:
        raise AssertionError("映射装备第6层应开始投放打造主材/副材")
    if [layer["craft_tier"] for layer in layers[5:8]] != [10, 10, 10]:
        raise AssertionError("映射装备第6～8层应统一投放10档主材")
    if layers[8]["craft_tier"] != 20:
        raise AssertionError("映射装备第9层应恢复20档主材节奏")
    if any(layer["chest_probs"]["Purple"] <= 0 for layer in layers):
        raise AssertionError("每层紫箱概率都必须为正")
    if any(layer["chest_probs"]["Orange"] != 0 for layer in layers[:9]) or any(layer["chest_probs"]["Orange"] <= 0 for layer in layers[9:]):
        raise AssertionError("金箱必须从第10层开始出现")
    if any(layer["chest_probs"]["Red"] != 0 for layer in layers[:19]) or any(layer["chest_probs"]["Red"] <= 0 for layer in layers[19:]):
        raise AssertionError("红箱必须从第20层开始出现")
    if [layers[-1]["chest_probs"][quality] for quality in ["Purple", "Orange", "Red"]] != [Decimal("0.37"), Decimal("0.19"), Decimal("0.04")]:
        raise AssertionError("第30层紫/金/红箱终值应为37%/19%/4%")
    if [layers[0]["chest_probs"][quality] for quality in QUALITIES] != [Decimal("0.515"), Decimal("0.30"), Decimal("0.185"), Decimal("0"), Decimal("0")]:
        raise AssertionError("第1层绿/蓝/紫/金/红箱应为51.5%/30%/18.5%/0%/0%")
    if [layers[9]["chest_probs"][quality] for quality in ["Orange", "Red"]] != [Decimal("0.01"), Decimal("0")]:
        raise AssertionError("第10层金/红箱应为1%/0%")
    if [layers[19]["chest_probs"][quality] for quality in ["Orange", "Red"]] != [Decimal("0.10"), Decimal("0.005")]:
        raise AssertionError("第20层金/红箱应为10%/0.5%")
    actual_gold = [layer["chest_probs"]["Purple"] * Decimal("0.10") + layer["chest_probs"]["Orange"] * Decimal("0.98") for layer in layers]
    actual_red = [layer["chest_probs"]["Orange"] * Decimal("0.02") + layer["chest_probs"]["Red"] for layer in layers]
    if any(curr <= prev for prev, curr in zip(actual_gold, actual_gold[1:])):
        raise AssertionError("实际金装概率必须逐层严格上升")
    if any(value != 0 for value in actual_red[:9]) or any(curr <= prev for prev, curr in zip(actual_red[9:], actual_red[10:])):
        raise AssertionError("实际红装应在第1～9层为0，并从第10层起逐层严格上升")
    return {
        "main_display_coef": main_display_coef,
        "sub_display_coef": sub_display_coef,
        "layers": layers,
    }


def main_attribute_rows(model: dict) -> list[list]:
    rows = []
    row_id = 1
    for part_cn, part_enum, attr_cn, attr_enum, red_target, unit in PARTS:
        for quality in QUALITIES:
            for level in LEVELS:
                formula_coef = main_formula_coef(level)
                display_coef = model["main_display_coef"][level]
                value = red_target * QUALITY_MAIN[quality] * formula_coef
                rows.append(
                    [
                        row_id,
                        part_cn,
                        part_enum,
                        attr_cn,
                        attr_enum,
                        QUALITY_CN[quality],
                        quality,
                        level,
                        as_number(red_target),
                        as_number(QUALITY_MAIN[quality]),
                        as_number(formula_coef, 12),
                        as_number(display_coef, 3),
                        as_number(value, 9),
                        unit,
                        "VALUE_READY_SCHEMA_BLOCKED",
                    ]
                )
                row_id += 1
    if len(rows) != 480:
        raise AssertionError(len(rows))
    return rows


def sub_attribute_rows(model: dict) -> list[list]:
    rows = []
    row_id = 1
    for attr_cn, attr_enum, red_target, unit in SUB_ATTRIBUTES:
        for quality in QUALITIES:
            for level in LEVELS:
                formula_coef = sub_formula_coef(level)
                display_coef = model["sub_display_coef"][level]
                value = red_target * QUALITY_SUB[quality] * formula_coef
                rows.append(
                    [
                        row_id,
                        attr_cn,
                        attr_enum,
                        QUALITY_CN[quality],
                        quality,
                        level,
                        as_number(red_target),
                        as_number(QUALITY_SUB[quality]),
                        as_number(formula_coef, 12),
                        as_number(display_coef, 3),
                        as_number(value, 9),
                        unit,
                        "VALUE_READY_SCHEMA_BLOCKED",
                    ]
                )
                row_id += 1
    if len(rows) != 600:
        raise AssertionError(len(rows))
    return rows


def layer_input_rows(model: dict) -> list[list]:
    rows = []
    for layer in model["layers"]:
        rows.append(
            [
                layer["layer"],
                25,
                layer["fixed_boxes"],
                as_number(layer["extra_box_prob"]),
                as_number(layer["expected_boxes"]),
                *[as_number(layer["chest_probs"][quality]) for quality in QUALITIES],
                ";".join(f"{level},{int(probability * 1000)}" for level, probability in layer["grade_probs"]),
                layer["material_level"],
                layer["craft_tier"],
                as_number(layer["main_material_prob"]),
                *[as_number(layer["main_quality_probs"][quality]) for quality in ["Purple", "Orange", "Red"]],
                layer["sub_material_count"],
                layer["first_archive"],
                "MD_AUTHORITY",
            ]
        )
    return rows


def box_item_rows(model: dict) -> list[list]:
    rows = []
    icon = "UIRes/UIAtlas/Icon/Items/item_specialequipment.png"
    for layer in model["layers"]:
        for quality in QUALITIES:
            item_id = box_item_id(layer["layer"], quality)
            rows.append(
                [
                    item_id,
                    f"第{layer['layer']}层{QUALITY_CN[quality]}色宝箱",
                    generate_id(layer["layer"], quality),
                    "ItemType_Other",
                    "ItemSubType_SpecialEquip_Box",
                    None,
                    icon,
                    None,
                    quality,
                    f"开启后按第{layer['layer']}层等级池获得1件映射装备。",
                    "P02层级来源宝箱候选",
                    26,
                    None,
                    None,
                    None,
                    True,
                    "PROPOSED_ID_RUNTIME_BLOCKED",
                ]
            )
    if len(rows) != 150:
        raise AssertionError(len(rows))
    return rows


def generate_rows(model: dict) -> list[list]:
    box_quality_lists = {
        "Green": "Green,800;Blue,200",
        "Blue": "Blue,850;Purple,150",
        "Purple": "Purple,900;Orange,100",
        "Orange": "Orange,980;Red,20",
        "Red": "Red,1000",
    }
    rows = []
    for layer in model["layers"]:
        grades = ";".join(f"{level},{int(probability * 1000)}" for level, probability in layer["grade_probs"])
        for quality in QUALITIES:
            rows.append(
                [
                    generate_id(layer["layer"], quality),
                    f"第{layer['layer']}层{QUALITY_CN[quality]}色宝箱开装",
                    grades,
                    box_quality_lists[quality],
                    None,
                    "1;2;3;4;5;6;7;8",
                    None,
                    1,
                    1,
                    "PROPOSED_ID_RUNTIME_BLOCKED",
                ]
            )
    return rows


def main_material_item_rows() -> list[list]:
    rows = []
    icon = "UIRes/UIAtlas/Icon/Items/item_specialequipment.png"
    for tier in CRAFT_TIERS:
        for category_cn, category, _ in MATERIAL_CATEGORIES:
            for quality_cn, quality in MATERIAL_QUALITIES:
                item_id = material_item_id(tier, category, quality)
                rows.append(
                    [
                        item_id,
                        f"{tier}档{quality_cn}色{category_cn}主材",
                        None,
                        "ItemType_Prop",
                        None,
                        None,
                        icon,
                        None,
                        quality,
                        f"用于打造{tier}档{category_cn}映射装备的{quality_cn}色主材。",
                        "P02主材候选ID；需程序消费协议",
                        26,
                        None,
                        None,
                        None,
                        True,
                        tier,
                        category,
                        quality,
                        "PROPOSED_ID_SCHEMA_BLOCKED",
                    ]
                )
    if len(rows) != 72:
        raise AssertionError(len(rows))
    return rows


def sub_material_item_rows() -> list[list]:
    icon = "UIRes/UIAtlas/Icon/Items/item_specialequipment.png"
    rows = []
    for index in range(1, 5):
        rows.append(
            [
                sub_material_item_id(index),
                f"映射装备副材{index}",
                None,
                "ItemType_Prop",
                None,
                None,
                icon,
                None,
                "Blue",
                f"映射装备打造通用副材{index}。",
                "P02副材候选ID；需程序消费协议",
                26,
                None,
                None,
                None,
                True,
                index,
                "PROPOSED_ID_SCHEMA_BLOCKED",
            ]
        )
    return rows


def preview_placeholder_item_rows() -> list[list]:
    """仅供UIlevel奖励展示的等级箱/随机材料占位道具，不进入任何真实掉落或背包产销。"""
    rows = []
    quality_cn = {"Blue": "蓝", "Purple": "紫", "Orange": "金", "Red": "红"}
    # 预览占位必须表达“类别随机”，不能借用某一件具体主材或帮助按钮。
    # 使用根据现有映射装备美术风格生成的两张专用透明道具图。
    main_icon = "UIRes/UIAtlas/Icon/Items/item_mappingequip_random_mainmaterial.png"
    sub_icon = "UIRes/UIAtlas/Icon/Items/item_mappingequip_random_submaterial.png"
    for grade, item_id in PREVIEW_GRADE_BOX_ITEM_IDS.items():
        rows.append([
            item_id, f"{grade}级映射装备箱", None,
            "ItemType_Other", None, None, "UIRes/UIAtlas/Icon/Items/item_specialequipment.png", None, "Blue",
            f"本层宝箱可能开出{grade}级映射装备。",
            "UI展示占位；不可掉落、不可获得", None, None, None, None, True, "UI_PREVIEW_ONLY",
        ])
    for (tier, quality), item_id in PREVIEW_MAIN_ITEM_IDS.items():
        rows.append([
            item_id, f"{tier}级随机打造主材", None,
            "ItemType_Other", None, None, main_icon, None, quality,
            f"本层可能掉落{tier}级随机打造主材，最高为{quality_cn[quality]}色品质。",
            "UI展示占位；不可掉落、不可获得", None, None, None, None, True, "UI_PREVIEW_ONLY",
        ])
    rows.append([
        PREVIEW_SUB_ITEM_ID, "随机映射装备副材", None,
        "ItemType_Other", None, None, sub_icon, None, "Purple",
        "本层可能掉落一种随机映射装备副材。",
        "UI展示占位；不可掉落、不可获得", None, None, None, None, True, "UI_PREVIEW_ONLY",
    ])
    if len(rows) != 22:
        raise AssertionError(len(rows))
    return rows


DROP_HEADERS = [
    "ID(公式列留空)",
    "DropId",
    "##备注",
    "DropName",
    "DropId2",
    "DropType",
    "DropMinNum",
    "DropMaxNum",
    "##分隔",
    "DropItem_id",
    "DropItemNumMin",
    "DropItemNumMax",
    "DropWeight",
    "ShowItemID",
    "IsValid",
    "状态",
]


def drop_row(
    drop_id: int,
    note: str,
    drop_name: str,
    drop_id2: int,
    drop_type: str,
    drop_min: int,
    drop_max: int,
    item_id: int,
    item_min: int,
    item_max: int,
    weight: int,
    status: str,
) -> list:
    return [None, drop_id, note, drop_name, drop_id2, drop_type, drop_min, drop_max, None, item_id, item_min, item_max, weight, None, "true", status]


def regular_root_drop_rows(model: dict) -> list[list]:
    rows = []
    for layer in model["layers"]:
        root = 20005100 + layer["layer"]
        name = f"映射装备副本第{layer['layer']}层常规掉落"
        branches = [
            (REGULAR_BOX_POOL_BASE + layer["layer"] - 1, layer["fixed_boxes"], "固定宝箱"),
            (EXTRA_BOX_POOL_BASE + layer["layer"] - 1, 1, "额外宝箱独立判定"),
        ]
        if layer["main_material_prob"] > 0:
            branches.append((MAIN_MATERIAL_POOL_BASE + layer["layer"] - 1, 1, "主材独立判定"))
        if layer["sub_material_count"] > 0:
            branches.append((SUB_MATERIAL_POOL_ID, layer["sub_material_count"], "副材固定总次数"))
        for pool_id, count, note in branches:
            rows.append(drop_row(root, note, name, pool_id, "fixed__random", count, count, 0, 0, 0, 0, "VALUE_READY_FORMULA_MANUAL"))
    if len(rows) != 110:
        raise AssertionError(len(rows))
    return rows


def regular_box_pool_rows(model: dict) -> list[list]:
    rows = []
    for layer in model["layers"]:
        pool_id = REGULAR_BOX_POOL_BASE + layer["layer"] - 1
        weights = allocate_weights([(quality, layer["chest_probs"][quality]) for quality in QUALITIES])
        for quality, weight in weights:
            rows.append(
                drop_row(
                    pool_id,
                    f"第{layer['layer']}层{QUALITY_CN[quality]}箱",
                    f"第{layer['layer']}层宝箱档位池",
                    0,
                    "random",
                    1,
                    1,
                    box_item_id(layer["layer"], quality),
                    1,
                    1,
                    weight,
                    "VALUE_READY_RUNTIME_BLOCKED",
                )
            )
    return rows


def extra_box_pool_rows(model: dict) -> list[list]:
    rows = []
    for layer in model["layers"]:
        pool_id = EXTRA_BOX_POOL_BASE + layer["layer"] - 1
        extra = layer["extra_box_prob"]
        entries: list[tuple[tuple[str, str | None], Decimal]] = [(('no_drop', None), Decimal(1) - extra)]
        entries.extend((("box", quality), extra * layer["chest_probs"][quality]) for quality in QUALITIES)
        for (kind, quality), weight in allocate_weights(entries):
            if (kind == "no_drop" and extra >= 1) or (kind == "box" and extra <= 0):
                continue
            item_id = 0 if kind == "no_drop" else box_item_id(layer["layer"], str(quality))
            note = "未触发额外宝箱" if kind == "no_drop" else f"额外{QUALITY_CN[str(quality)]}箱"
            rows.append(
                drop_row(
                    pool_id,
                    note,
                    f"第{layer['layer']}层额外宝箱池",
                    0,
                    "random",
                    1,
                    1,
                    item_id,
                    0 if item_id == 0 else 1,
                    0 if item_id == 0 else 1,
                    weight,
                    "VALUE_READY_RUNTIME_BLOCKED",
                )
            )
    return rows


def main_material_pool_rows(model: dict) -> list[list]:
    rows = []
    for layer in model["layers"]:
        if layer["main_material_prob"] <= 0:
            continue
        pool_id = MAIN_MATERIAL_POOL_BASE + layer["layer"] - 1
        chance = layer["main_material_prob"]
        entries: list[tuple[tuple[str, str | None, str | None], Decimal]] = [(('no_drop', None, None), Decimal(1) - chance)]
        for _, category, category_probability in MATERIAL_CATEGORIES:
            for _, quality in MATERIAL_QUALITIES:
                probability = chance * category_probability * layer["main_quality_probs"][quality]
                entries.append((("item", category, quality), probability))
        for (kind, category, quality), weight in allocate_weights(entries):
            if weight <= 0:
                continue
            if kind == "no_drop":
                item_id = 0
                note = "主材未命中"
            else:
                item_id = material_item_id(layer["craft_tier"], str(category), str(quality))
                note = f"{layer['craft_tier']}档{CATEGORY_CN[str(category)]}{MATERIAL_QUALITY_CN[str(quality)]}主材"
            rows.append(
                drop_row(
                    pool_id,
                    note,
                    f"第{layer['layer']}层主材池",
                    0,
                    "random",
                    1,
                    1,
                    item_id,
                    0 if item_id == 0 else 1,
                    0 if item_id == 0 else 1,
                    weight,
                    "PROPOSED_ID_FORMULA_MANUAL",
                )
            )
    return rows


def sub_material_pool_rows() -> list[list]:
    return [
        drop_row(
            SUB_MATERIAL_POOL_ID,
            f"副材{index}等权",
            "映射装备副材等权池",
            0,
            "random",
            1,
            1,
            sub_material_item_id(index),
            1,
            1,
            2500,
            "PROPOSED_ID_FORMULA_MANUAL",
        )
        for index in range(1, 5)
    ]


FIRST_BOX_ARCHIVE = {
    1: ("Blue", 1),
    2: ("Blue", 1),
    3: ("Blue", 1),
    4: ("Blue", 1),
    5: ("Blue", 1),
    6: ("Blue", 1),
    8: ("Blue", 2),
    9: ("Blue", 2),
    10: ("Blue", 1),
    12: ("Blue", 2),
    13: ("Blue", 1),
    14: ("Purple", 1),
    15: ("Purple", 1),
    17: ("Purple", 1),
    18: ("Purple", 1),
    19: ("Purple", 2),
    20: ("Purple", 1),
    22: ("Purple", 2),
    23: ("Purple", 1),
    24: ("Purple", 2),
    25: ("Purple", 1),
    28: ("Purple", 2),
}

FIRST_MATERIAL_CATEGORY = {
    6: "Weapon",
    7: "Armor",
    10: "Weapon",
    11: "Accessory",
    13: "Accessory",
    15: "Armor",
    16: "Accessory",
    18: "Weapon",
    20: "Accessory",
    21: "Weapon",
    23: "Weapon",
    25: "Armor",
    26: "Accessory",
    28: "Armor",
    30: "Weapon",
}

FIRST_RANDOM_BOX_LAYERS = [27, 29, 30]


def first_clear_rows(model: dict) -> tuple[list[list], list[list]]:
    """
    首通宝箱节奏沿用MD归档；第1～5层仅给宝箱，第6～8层统一按10档过渡，第9层起旧胚料映射为“当层打造档+同大类+紫主材”。
    这是可评审的 P02 新提案，不是已获得用户确认的MD最终值。
    """
    rows: list[list] = []
    summary: list[list] = []
    random_pool_by_layer = {layer: FIRST_RANDOM_POOL_BASE + index for index, layer in enumerate(FIRST_RANDOM_BOX_LAYERS)}
    for layer in model["layers"]:
        layer_no = layer["layer"]
        root = 20000009 + layer_no
        rows.append(drop_row(root, "映射之匙固定返还", f"第{layer_no}层首通", 0, "fixed_", 1, 1, 25, 1, 1, 10000, "VALUE_READY"))
        proposed = ["映射之匙(25)x1"]
        if layer_no in FIRST_BOX_ARCHIVE:
            quality, count = FIRST_BOX_ARCHIVE[layer_no]
            item_id = box_item_id(layer_no, quality)
            rows.append(drop_row(root, f"首通{QUALITY_CN[quality]}箱", f"第{layer_no}层首通", 0, "fixed_", 1, 1, item_id, count, count, 10000, "PROPOSED_RUNTIME_BLOCKED"))
            proposed.append(f"{QUALITY_CN[quality]}箱({item_id})x{count}")
        if layer_no in FIRST_RANDOM_BOX_LAYERS:
            pool_id = random_pool_by_layer[layer_no]
            rows.append(drop_row(root, "金/红首通随机箱", f"第{layer_no}层首通", pool_id, "fixed__random", 1, 1, 0, 0, 0, 0, "PROPOSED_RUNTIME_BLOCKED"))
            rows.append(drop_row(pool_id, "金箱82%", f"第{layer_no}层首通金红箱池", 0, "random", 1, 1, box_item_id(layer_no, "Orange"), 1, 1, 8200, "PROPOSED_RUNTIME_BLOCKED"))
            rows.append(drop_row(pool_id, "红箱18%", f"第{layer_no}层首通金红箱池", 0, "random", 1, 1, box_item_id(layer_no, "Red"), 1, 1, 1800, "PROPOSED_RUNTIME_BLOCKED"))
            proposed.append("金/红随机箱(82/18)x1")
        if layer_no in FIRST_MATERIAL_CATEGORY:
            category = FIRST_MATERIAL_CATEGORY[layer_no]
            item_id = material_item_id(layer["craft_tier"], category, "Purple")
            rows.append(drop_row(root, "旧胚料按新主材口径重配", f"第{layer_no}层首通", 0, "fixed_", 1, 1, item_id, 1, 1, 10000, "PROPOSED_DESIGN_APPROVAL"))
            proposed.append(f"{layer['craft_tier']}档{CATEGORY_CN[category]}紫主材({item_id})x1")
        summary.append([layer_no, root, layer["first_archive"], " + ".join(proposed), "PROPOSED_DESIGN_APPROVAL" if layer_no in FIRST_MATERIAL_CATEGORY else "PROPOSED_RUNTIME_BLOCKED"])
    return rows, summary


def equipment_level_rows() -> list[list]:
    """建议完整五品质映射：Green->x1, Blue->x2, Purple->x3, Orange->x4, Red->x5。"""
    rows = []
    row_id = 1
    for layer in range(1, 31):
        ui_level_id = 250000 + layer * 10 + 1
        for suffix, quality in enumerate(QUALITIES, start=1):
            rows.append([row_id, ui_level_id, quality, 250000 + layer * 10 + suffix, "CONDITIONAL_RUNTIME_REFERENCE_GATE"])
            row_id += 1
    return rows


def ui_preview_items(layer: dict, multiplier: int) -> str:
    # 宝箱预览按本层全部装备等级去重展示，品质不参与展示。
    # 主材仍取当前打造档和最高可掉品质；副材只显示随机类别图标。
    item_ids = [PREVIEW_GRADE_BOX_ITEM_IDS[grade] for grade, probability in layer["grade_probs"] if probability > 0]
    if layer["main_material_prob"] > 0:
        highest_material_quality = next(quality for _, quality in reversed(MATERIAL_QUALITIES) if layer["main_quality_probs"][quality] > 0)
        item_ids.append(PREVIEW_MAIN_ITEM_IDS[(layer["craft_tier"], highest_material_quality)])
    if layer["sub_material_count"] > 0:
        item_ids.append(PREVIEW_SUB_ITEM_ID)
    # 普通预览不展示数量，所有变体统一使用 -1。
    return ";".join(f"{item_id},-1" for item_id in item_ids)


def first_preview_items(layer: dict, multiplier: int) -> str:
    layer_no = layer["layer"]
    values = [f"25,{multiplier}"]
    if layer_no in FIRST_BOX_ARCHIVE or layer_no in FIRST_RANDOM_BOX_LAYERS:
        values.extend(
            f"{PREVIEW_GRADE_BOX_ITEM_IDS[grade]},-1"
            for grade, probability in layer["grade_probs"]
            if probability > 0
        )
    if layer_no in FIRST_MATERIAL_CATEGORY:
        category = FIRST_MATERIAL_CATEGORY[layer_no]
        values.append(f"{material_item_id(layer['craft_tier'], category, 'Purple')},{multiplier}")
    return ";".join(values)


def ui_level_rows(config_root: Path, model: dict) -> list[list]:
    path = config_root / "level/UIlevel.xlsx"
    wb = load_workbook(path, read_only=True, data_only=False)
    ws = wb["level"]
    headers = [cell.value for cell in ws[1]]
    index = {value: position for position, value in enumerate(headers) if value}
    official = []
    for row in ws.iter_rows(min_row=5, values_only=True):
        if row[index["LevelType"]] == "LevelType_SpecialEquipment":
            official.append(row)
    wb.close()
    if len(official) != 150:
        raise AssertionError(f"UIlevel映射装备行数={len(official)}")
    layer_by_number = {layer["layer"]: layer for layer in model["layers"]}
    result = []
    for row in official:
        level_id = int(row[index["LevelId"]])
        layer_no = int(row[index["TierNum"]])
        variant = level_id % 10
        layer = layer_by_number[layer_no]
        result.append(
            [
                level_id,
                row[index["Name"]],
                row[index["LevelType"]],
                layer_no,
                variant,
                row[index["Unlock"]],
                ui_preview_items(layer, variant),
                first_preview_items(layer, variant),
                20000009 + layer_no if variant == 1 else None,
                20005100 + layer_no if variant == 1 else None,
                row[index["MultiSettlementTimes"]],
                row[index["Vitality"]],
                "PROPOSED_ID_UI_SEMANTICS_GATE",
            ]
        )
    return result


def find_row_by_value(path: Path, sheet_name: str, field: str, value: object) -> tuple[dict, list]:
    wb = load_workbook(path, read_only=True, data_only=False)
    ws = wb[sheet_name]
    headers = [cell.value for cell in ws[1]]
    index = {header: position for position, header in enumerate(headers) if header}
    if field not in index:
        wb.close()
        raise KeyError((path, sheet_name, field))
    for row in ws.iter_rows(min_row=5, values_only=True):
        if row[index[field]] == value:
            result = {header: row[position] for header, position in index.items()}
            wb.close()
            return result, headers
    wb.close()
    raise KeyError((path, sheet_name, field, value))


def item_access_rows(config_root: Path) -> list[list]:
    current, _ = find_row_by_value(config_root / "items/ItemAccess.xlsx", "ItemAccess", "Id", 26)
    return [
        [
            current.get("Id"),
            current.get("Name"),
            current.get("Icon"),
            current.get("Description"),
            current.get("GotoId"),
            314,
            current.get("SaoDangSupport"),
            "PROPOSED_RUNTIME_ROUTE_GATE",
            "ItemAccess26当前跳转旧SystemOpen208；正式映射装备LevelType使用SystemId314。",
        ]
    ]


def entry_chain_rows(config_root: Path) -> list[list]:
    level_type, _ = find_row_by_value(config_root / "level/LevelType.xlsx", "LevelType", "Id", "LevelType_SpecialEquipment")
    system_open, _ = find_row_by_value(config_root / "system_open/SystemOpen.xlsx", "SystemOpen", "Id", 314)
    unlock_id = system_open.get("UnlockId") or system_open.get("Unlock")
    unlock_row, _ = find_row_by_value(config_root / "unlock/Unlock.xlsx", "Unlock", "Id", unlock_id)
    return [
        ["LevelType", "level/LevelType.xlsx", "LevelType_SpecialEquipment", "Reward", level_type.get("Reward"), "4001,-1;4002,-1;4003,-1;4004,-1;4005,-1", "PROPOSED_PREVIEW_ONLY", "只改全局代表预览，真实掉落读UIlevel DropId"],
        ["SystemOpen", "system_open/SystemOpen.xlsx", 314, "Unlock", unlock_id, unlock_id, "NO_CHANGE", "正式入口保留"],
        ["Unlock", "unlock/Unlock.xlsx", unlock_id, "UnlockCondition", json.dumps(unlock_row, ensure_ascii=False), json.dumps(unlock_row, ensure_ascii=False), "NO_CHANGE", "已对齐主线2-15，不应因数值落表改动"],
        ["SpecialLevel", "level/SpecialLevel.xlsx", "250011..250301", "TabQuality/IsChasm", "30条已存在", "保留", "NO_CHANGE", "仅入口行，不承载真实掉落"],
        ["level", "level/level.xlsx", "250011..250305", "150个战斗LevelId", "已存在", "保留", "NO_CHANGE_RUNTIME_SOURCE_GATE", "服务端是否读level.FirstReward/FallReward需联调"],
        ["globals", "globals_conf/globals_conf.xlsx", "DefaultSpecialEquipmentBox", "4001..4005", "现有5档默认箱", "保留为品质分组显示", "NO_CHANGE_RUNTIME_GATE", "层级箱不能直接替换该全局数组"],
        ["ItemChest", "items/ItemChest.xlsx", "4001..4350", "ItemId/ChestId", "未登记", "不强行新增", "N/A", "当前映射箱链是Items.ParaList->SpecialEquipmentGenerate，不是ItemChest"],
    ]


def full_chain_status_rows() -> list[list]:
    return [
        ["属性", "Attribute.xlsx", "10类在用副属性字典", "NO_CHANGE", "已存在", "10_主属性480 / 11_副属性600"],
        ["属性", "SpecialEquipment.xlsx", "单主属性、绿装模板", "NEEDS_ID_RUNTIME", "现F:G仍有双主属性，Green模板0条", "12_属性落表门禁"],
        ["属性", "SpecialEquipmentMain.xlsx", "8部位×12级×5品质", "NEEDS_SCHEMA", "现只有线性Value+Grow", "10_主属性480"],
        ["属性", "SpecialEquipmentEffect/EffectDrop", "10类副属性+语义去重", "NEEDS_ID_RUNTIME", "物理/魔法伤害加成已退出在用池", "11_副属性600 / 12_属性落表门禁"],
        ["品质", "SpecialEquipmentQuality.xlsx", "M:N系数", "ATOMIC_BLOCK_ONLY", "不可脱离Main/Effect/引用单贴", "原P01 11_QualityPatch已降级"],
        ["生成", "Items.xlsx", "150层级箱+72主材+4副材", "FORMAL_ID_SYNCED", "主材1080..1151；副材1152..1155；层级箱4201..4350", "21/23/24 Sheet"],
        ["生成", "SpecialEquipmentGenerate.xlsx", "30层×5箱", "NEEDS_RUNTIME", "需开箱请求传ItemId/层级来源", "22_Generate150"],
        ["关卡", "EquipmentLevel.xlsx", "30层×5品质", "CONDITIONAL", "Green->x1...Red->x5，需引用联调", "31_EquipmentLevel150"],
        ["关卡", "UIlevel.xlsx", "150行预览+入口DropId", "NEEDS_ID_UI", "30层×5变体", "32_UIlevel150"],
        ["掉落", "Drop_dungeon.xlsx", "固定箱/额外箱/主材/副材", "FORMULA_MANUAL", "数值已展开，公式列禁止覆盖", "25..29 Drop Sheet"],
        ["首通", "Drop_dungeon.xlsx", "匙返还+箱/新主材", "DESIGN_APPROVAL", "旧胚料表在MD明确非最终口径", "30_首通方案"],
        ["引导", "ItemAccess.xlsx", "映射装备本跳转", "RUNTIME_GATE", "ItemAccess26现指208，候选改314", "34_ItemAccess"],
        ["养成", "Portable系列", "经验/概率/消耗", "MIXED", "P01值块保留，Range/Craft/分解仍缺Schema", "35_合成打造覆盖+原P01 Sheet"],
        ["边界", "Shop/Task/ItemChest", "商店、匙来源、通用宝箱", "N/A", "最新MD未要求本期修改", "41_边界排除"],
    ]


def id_plan_rows() -> list[list]:
    return [
        ["Items", "打造主材", 1080, 1151, 72, "8档×3大类×3品质", "FORMAL_REGISTERED", "2026-07-13按正式Items名称逐项核对"],
        ["Items", "打造副材", 1152, 1155, 4, "副材1..4", "FORMAL_REGISTERED", "2026-07-13按正式Items名称逐项核对"],
        ["Items", "层级宝箱", 4201, 4350, 150, "30层×5品质", "FORMAL_REGISTERED", "正式Items已登记；开箱协议仍需传递确切ItemId"],
        ["SpecialEquipmentGenerate", "层级开装", 4201, 4350, 150, "与层级宝箱一对一", "FORMAL_REGISTERED", "2026-07-13正式表已登记同名ID"],
        ["DropId", "固定宝箱池", 22101, 22130, 30, "每层1池", "PROPOSED", "10000权重"],
        ["DropId", "额外宝箱池", 22201, 22230, 30, "每层1池", "PROPOSED", "含空掉落"],
        ["DropId", "主材池", 22301, 22330, 30, "每层1池", "PROPOSED", "含空掉落"],
        ["DropId", "副材共用池", 22400, 22400, 1, "4种等权", "PROPOSED", "根包按层重复调1..4次"],
        ["DropId", "首通金/红箱池", 22451, 22453, 3, "层27/29/30", "PROPOSED", "82%/18%"],
        ["DropId", "常规一级入口", 20005101, 20005130, 30, "复用现有", "REUSE", "UIlevel引用不需变"],
        ["DropId", "首通一级入口", 20000010, 20000039, 30, "复用现有", "REUSE", "UIlevel引用不需变"],
    ]


def attribute_gate_rows() -> list[list]:
    return [
        ["Attribute.xlsx", "10类在用目标属性", "已存在", "NO_CHANGE", "物理/魔法伤害定义可保留但不再引用"],
        ["SpecialEquipment.xlsx", "Attribute1List", "保留每部位唯一主属性", "NEEDS_ID", "190件旧模板与新绿装模板需原子迁移"],
        ["SpecialEquipment.xlsx", "Attribute2List", "目标为全清空", "RUNTIME_GATE", "客户端现仍读取该列；服务端消费链需确认"],
        ["SpecialEquipment.xlsx", "Green模板", "0条", "NEEDS_ID_CONTENT", "需名称/本地化/主属性引用/效果池"],
        ["SpecialEquipmentMain.xlsx", "Value/Grow/Param", "线性模型", "NEEDS_SCHEMA", "不能精确表达0.05+0.95*((Lv-5)/55)^1.35"],
        ["SpecialEquipmentQuality.xlsx", "GradeCoefficient", "0.20/0.30/0.45/0.70/1.00", "ATOMIC_BLOCK_ONLY", "旧Main值已预缩放，单贴会二次缩放"],
        ["SpecialEquipmentQuality.xlsx", "QualityCoefficient", "0.50/0.60/0.70/0.85/1.00", "ATOMIC_BLOCK_ONLY", "与当前沉淀MD一致"],
        ["SpecialEquipmentSubAttrCoef.xlsx", "EquipLv/SubAttrCoef", "12档已完整", "READY", "原P01 02_SubAttrCoef可复用"],
        ["SpecialEquipmentEffect.xlsx", "10类×5品质", "目标50条", "NEEDS_ID", "保持数值随机区间并移除两类伤害加成池引用"],
        ["SpecialEquipmentEffectDrop.xlsx", "词条池", "按属性语义不重复", "NEEDS_RUNTIME", "仅按ID无放回仍可抽到两个同语义词条"],
        ["SpecialEquipmentLvUp/LvLimit", "旧升级链", "新设计已废弃", "DEPRECATED_RUNTIME_GATE", "不可只清表，客户端调用需退出"],
        ["新建议表", "SpecialEquipmentMainCurve", "Part/Attribute/EquipLv/Quality/Value", "SCHEMA_PROPOSAL", "10_主属性480可直接作为新表输入"],
        ["新建议表", "SpecialEquipmentSubCurve", "Attribute/EquipLv/Quality/Value", "SCHEMA_PROPOSAL", "11_副属性600可直接作为新表输入"],
    ]


def portable_coverage_rows() -> list[list]:
    return [
        ["PortableExp.xlsx", "60行经验", "01_PortableExp", "READY", "P01保留"],
        ["SpecialEquipmentSubAttrCoef.xlsx", "12档系数", "02_SubAttrCoef", "READY", "P01保留"],
        ["PortableLvUp.xlsx", "59行锻造台升级经验", "03_PortableLvUp", "READY", "P01保留"],
        ["PortableCompoundProb.xlsx", "60级×5品质", "04_CompoundProb", "CONDITIONAL_RUNTIME", "1000权重"],
        ["PortableCraftProb.xlsx", "60级×3主材品质", "05_CraftProb", "CONDITIONAL_RUNTIME", "正式Sheet名与文件名不一致"],
        ["PortableEquipCompound.xlsx", "8档×5品质金币", "10_CompoundCost", "PARTIAL", "EquipResult仍依赖Generate/Range"],
        ["PortableRange.xlsx", "8档等级池/解锁", None, "NEEDS_SCHEMA_ID", "现只2行，不能表达8档权重池"],
        ["PortableEquipCraft.xlsx", "主材×档位×品质×部位", None, "NEEDS_SCHEMA_ID", "现Schema无法表达档内等级及72主材"],
        ["PortableResolve(建议新表)", "12等级×5品质分解", None, "NEEDS_SCHEMA", "现Quality.Basic只有品质维度"],
        ["globals.DefaultSpecialEquipmentCompoundNum", 9, None, "NO_CHANGE", "现值已对齐"],
    ]


def boundary_rows() -> list[list]:
    return [
        ["ItemChest.xlsx", "通用宝箱映射", "N/A", "当前映射箱走SpecialEquip_Box -> Items.ParaList -> Generate，无证据需配ItemChest"],
        ["Shop/ShopGoods", "匙/主材/副材售卖", "N/A", "最新沉淀MD未要求本期商店投放"],
        ["DailyActiveReward/WeeklyReward", "映射之匙25来源", "OUT_OF_SCOPE", "现Drop_other已有日2/周10观察；最新MD明确来源/购买/上限不在本表展开"],
        ["SpecialEquipmentLvUp", "装备升级", "DEPRECATED", "新版装备等级不在养成中升级，但需先退出运行时调用"],
        ["打孔/鉴定", "旧材料与字段", "DEPRECATED", "不进入本版本消耗，程序读取退出前不清空"],
        ["红装洗练", "高阶零件23", "OUT_OF_SCOPE", "本版本仅红装分解产出x1，不登记洗练消耗"],
    ]


def blocker_rows() -> list[list]:
    return [
        ["P0", "主属性Schema", "SpecialEquipmentMain只有线性Value/Grow", "新增12档曲线表或程序支持幂函数", "10_主属性480逐点与MD相等"],
        ["P0", "层级宝箱来源", "现5个可堆叠通用箱无法携带层级", "开箱请求传确切ItemId/来源层，或掉落时立即开箱", "层级等级池10000次分布符合MD"],
        ["P0", "开箱运行时", "PropSystem.OpenMappingBox观察为TODO，UI只传quality/num", "服务端实现并返回具体装备", "每箱1件、红箱必红、部位8等权"],
        ["P0", "绿色品质", "无Green装备模板/效果块/词条池", "分配模板与Effect ID，补本地化", "绿装可生成、穿戴、计算、分解"],
        ["P0", "打造材料消费协议", "72主材+4副材无正式ItemSubType/程序消费", "确认ID、背包类型、图标、堆叠上限和Craft Schema", "每个主材唯一定位大类/档位/基础品质池"],
        ["P0", "首通新主材重配", "MD明确旧I-VIII胚料仅留档", "用户批准“当层档+同大类+紫主材”提案或给新表", "30_首通方案审批"],
        ["P1", "Drop公式安全", "正式B/C/F列混有公式，新链需数百新行", "人工预建行+下拉公式+仅粘贴纯值列", "公式无#REF/外键全存在/权重10000"],
        ["P1", "EquipmentLevel五品质", "现是Blue->x1...Red->x4，x5未映射", "原子更新为Green->x1...Red->x5", "30层×5品质全部能进入正确难度"],
        ["P1", "副属性语义去重", "现有不放回只可能按ID去重", "服务端按Attribute语义去重", "生成/打造各10000次无重复语义词条"],
        ["P1", "分解Schema", "Quality.Basic无等级维度", "新增EquipLv×Quality分解表", "12×5金币/锻造台经验/红装零件23一致"],
        ["P1", "ItemAccess双入口", "ItemAccess26->208，LevelType->314", "联调后改26->314并退旧208/4108", "获取途径可正确跳转映射装备本"],
    ]


def status_fill(status: str) -> str:
    value = status.upper()
    if value in {"READY", "NO_CHANGE", "REUSE", "MD_AUTHORITY", "VALUE_READY"}:
        return p01.PALE_GREEN
    if "DEPRECATED" in value or value in {"N/A", "OUT_OF_SCOPE"}:
        return p01.PALE_GRAY
    if "BLOCKED" in value or "NEEDS_" in value or "P0" in value:
        return p01.PALE_RED
    return p01.PALE_YELLOW


def row_status(values: Sequence[object], default: str) -> str:
    candidates = [str(value) for value in values if isinstance(value, str)]
    for value in reversed(candidates):
        if any(token in value.upper() for token in ["READY", "BLOCKED", "NEEDS_", "PROPOSED", "GATE", "NO_CHANGE", "REUSE", "DEPRECATED", "N/A", "OUT_OF_SCOPE", "MANUAL", "AUTHORITY", "P0", "P1", "PARTIAL", "MIXED", "CONDITIONAL", "ATOMIC"]):
            return value
    return default


def add_table_sheet(
    wb,
    *,
    name: str,
    title: str,
    target: str,
    instruction: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    status: str,
    freeze: str = "A5",
) -> object:
    ws = wb.create_sheet(name)
    p01.apply_global_sheet_style(ws)
    ws.freeze_panes = freeze
    max_col = max(len(headers), 6)
    p01.style_title(ws, title, max_col)
    p01.set_info_row(ws, 2, "正式目标", target, max_col, p01.LIGHT_BLUE)
    p01.set_info_row(ws, 3, "操作/门禁", instruction, max_col, status_fill(status))
    p01.style_header(ws, headers)
    apply_bilingual_headers(ws)
    for row_number, values in enumerate(rows, start=5):
        fill = status_fill(row_status(values, status))
        for column, value in enumerate(values, start=1):
            cell = ws.cell(row_number, column, value)
            cell.font = Font(name="微软雅黑", size=9, color=p01.INPUT_BLUE if fill in {p01.PALE_GREEN, p01.PALE_YELLOW} else p01.BLACK)
            cell.fill = PatternFill("solid", fgColor=fill)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = p01.GRID_BORDER
        ws.row_dimensions[row_number].height = 24
    if rows:
        ws.auto_filter.ref = f"A4:{get_column_letter(len(headers))}{4 + len(rows)}"
    for column, header in enumerate(headers, start=1):
        values = [str(row[column - 1]) for row in rows[:200] if len(row) >= column and row[column - 1] is not None]
        observed = max([len(str(header))] + [min(len(value), 60) for value in values])
        width = min(max(observed * 1.35 + 2, 10), 48)
        if any(token in str(header) for token in ["说明", "备注", "门禁", "原始", "方案", "Description", "Reward"]):
            width = min(max(width, 28), 55)
        ws.column_dimensions[get_column_letter(column)].width = width
    ws.sheet_properties.tabColor = p01.PASS_GREEN if status in {"READY", "NO_CHANGE"} else ("C00000" if "BLOCK" in status or "NEEDS" in status else p01.WARN_ORANGE)
    return ws


def add_overview(wb, counts: dict, generated_at: str) -> None:
    ws = wb.create_sheet("00_P02总览")
    ws.sheet_view.showGridLines = False
    p01.style_title(ws, "映射装备全链路映射配置包 P02", 9)
    messages = [
        ("交付结论", "P02已覆盖主/副属性、装备生成、30层关卡、常规/首通Drop、UI预览、主副材、EquipmentLevel及Portable养成。", p01.LIGHT_BLUE),
        ("范围更正", "P01只是Portable局部子包，不再代表‘全部涉及配置’。P02是完整范围的评审主包。", p01.PALE_YELLOW),
        ("重要纠错", "P01的11_QualityPatch不得单独粘贴；GradeCoefficient会在旧Main预缩放值上二次缩放，QualityCoefficient现有观察语义也不是副属性数值乘区。", p01.PALE_RED),
        ("粘贴原则", "数据表头为上中文、下正式英文字段，数据仍从第5行开始；绿色READY可仅粘贴值，黄色须先过ID/运行时门禁，红色须先改Schema/程序或完成业务决策。", p01.PALE_GREEN),
        ("Drop安全", "Drop_dungeon是公式敏感表：先人工预建行并下拉正式公式，再粘贴C:P纯值；不自动插行/删行，不覆盖公式列。", p01.PALE_RED),
        ("正式工程", "本次未修改正式 Datas，未执行Luban，未标记用户验收。", p01.PALE_GRAY),
    ]
    for row, (label, value, fill) in enumerate(messages, start=2):
        p01.set_info_row(ws, row, label, value, 9, fill)
        ws.row_dimensions[row].height = 38

    headers = ["交付块", "数量", "状态", "对应Sheet", "说明", None, None, None, None]
    p01.style_header(ws, headers, row=9)
    summary = [
        ["主属性目标点", counts["main_attribute"], "VALUE_READY_SCHEMA_BLOCKED", "10_主属性480", "8部位×5品质×12等级"],
        ["副属性目标点", counts["sub_attribute"], "VALUE_READY_SCHEMA_BLOCKED", "11_副属性600", "10属性×5品质×12等级"],
        ["层级宝箱/Generate", counts["box_items"] + counts["generate"], "PROPOSED_RUNTIME_BLOCKED", "21/22", "用唯一ItemId保留来源层"],
        ["主材/副材Items", counts["main_material_items"] + counts["sub_material_items"], "PROPOSED_ID", "23/24", "72+4"],
        ["常规Drop纯值行", counts["regular_drop_rows"], "FORMULA_MANUAL", "25..29", "前5层两分支，第6层起四分支+二级池"],
        ["首通Drop纯值行", counts["first_drop_rows"], "DESIGN_APPROVAL", "30_首通方案", "前5层无材料；第6～8层10档过渡；第9层起按原档位"],
        ["EquipmentLevel", counts["equipment_level"], "CONDITIONAL_RUNTIME", "31_EquipmentLevel150", "Green->x1...Red->x5"],
        ["UIlevel预览", counts["ui_level"], "PROPOSED_UI_GATE", "32_UIlevel150", "30层×5倍变体"],
        ["Portable P01子包", 656, "MIXED", "原P01 Sheet", "保留值块，Quality单贴已降级"],
    ]
    for row_number, values in enumerate(summary, start=10):
        fill = status_fill(values[2])
        for column in range(1, 10):
            value = values[column - 1] if column <= len(values) else None
            cell = ws.cell(row_number, column, value)
            cell.fill = PatternFill("solid", fgColor=fill)
            cell.border = p01.GRID_BORDER
            cell.font = Font(name="微软雅黑", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        ws.row_dimensions[row_number].height = 34
    ws["A20"] = "生成时间"
    ws["B20"] = generated_at
    ws.merge_cells("B20:I20")
    for cell in ws[20]:
        cell.fill = PatternFill("solid", fgColor=p01.PALE_GRAY)
        cell.border = p01.GRID_BORDER
        cell.font = Font(name="微软雅黑")
    widths = [20, 12, 28, 28, 52, 8, 8, 8, 8]
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.freeze_panes = "A10"
    ws.sheet_properties.tabColor = p01.NAVY


def check_candidate_ids(config_root: Path) -> dict:
    items_wb = load_workbook(config_root / "items/Items.xlsx", read_only=True, data_only=True)
    items_ws = items_wb["items"]
    existing_items = {row[1]: row[2] for row in items_ws.iter_rows(min_row=5, values_only=True) if isinstance(row[1], int)}
    items_wb.close()
    expected_items = {}
    accepted_item_names: dict[int, set[str]] = {}
    legacy_material_quality = {"Purple": "初级", "Orange": "中级", "Red": "高级"}
    legacy_material_category = {"Weapon": "武器", "Armor": "防具", "Accessory": "配件"}
    for tier in CRAFT_TIERS:
        for category_cn, category, _ in MATERIAL_CATEGORIES:
            for quality_cn, quality in MATERIAL_QUALITIES:
                item_id = material_item_id(tier, category, quality)
                expected_items[item_id] = f"{tier}档{quality_cn}色{category_cn}主材"
                accepted_item_names[item_id] = {
                    expected_items[item_id],
                    f"{legacy_material_quality[quality]}{legacy_material_category[category]}胚料",
                }
    legacy_sub_material_names = ["调校垫片", "稳固铆钉", "导能晶片", "精修胶带"]
    for index in range(1, 5):
        item_id = sub_material_item_id(index)
        expected_items[item_id] = f"映射装备副材{index}"
        accepted_item_names[item_id] = {expected_items[item_id], legacy_sub_material_names[index - 1]}
    legacy_box_quality = {"Green": "简易", "Blue": "标准", "Purple": "精品", "Orange": "高级", "Red": "原型"}
    for layer in range(1, 31):
        for quality in QUALITIES:
            item_id = box_item_id(layer, quality)
            expected_items[item_id] = f"第{layer}层{QUALITY_CN[quality]}色宝箱"
            accepted_item_names[item_id] = {expected_items[item_id], f"第{layer}层{legacy_box_quality[quality]}装备补给箱"}
    quality_cn = {"Blue": "蓝", "Purple": "紫", "Orange": "金", "Red": "红"}
    legacy_box_quality_by_id = {4351: "蓝", 4352: "紫", 4353: "金", 4354: "红"}
    for grade, item_id in PREVIEW_GRADE_BOX_ITEM_IDS.items():
        expected_items[item_id] = f"{grade}级映射装备箱"
        accepted_item_names[item_id] = {expected_items[item_id]}
        if item_id in legacy_box_quality_by_id:
            color = legacy_box_quality_by_id[item_id]
            accepted_item_names[item_id].update({
                "随机映射装备箱",
                f"随机映射装备箱（最高{color}色）",
                f"随机装备箱（最高{color}色）",
            })
    for (tier, quality), item_id in PREVIEW_MAIN_ITEM_IDS.items():
        expected_items[item_id] = f"{tier}级随机打造主材"
        accepted_item_names[item_id] = {expected_items[item_id]}
    expected_items[PREVIEW_SUB_ITEM_ID] = "随机映射装备副材"
    accepted_item_names[PREVIEW_SUB_ITEM_ID] = {expected_items[PREVIEW_SUB_ITEM_ID]}

    gen_wb = load_workbook(config_root / "SpecialEquipment/SpecialEquipmentGenerate.xlsx", read_only=True, data_only=True)
    gen_ws = gen_wb["SpecialEquipment"]
    # 正式表可能含仅在首列留有格式/占位值的短行；只读取至少覆盖 Id、名称列的有效行。
    existing_generates = {
        row[1]: row[2]
        for row in gen_ws.iter_rows(min_row=5, values_only=True)
        if len(row) > 2 and isinstance(row[1], int)
    }
    gen_wb.close()
    expected_generates = {
        generate_id(layer, quality): f"第{layer}层{QUALITY_CN[quality]}色宝箱开装"
        for layer in range(1, 31)
        for quality in QUALITIES
    }

    existing_drop_ids = set()
    for path in (config_root / "Drop").glob("*.xlsx"):
        if path.name == "Drop_dungeon.xlsx":
            # 本包就是 Drop_dungeon 的完整替换候选；只拦截被其他 Drop 文件占用的 ID。
            continue
        wb = load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            headers = [cell.value for cell in ws[1]]
            if "DropId" not in headers:
                continue
            index = headers.index("DropId")
            for row in ws.iter_rows(min_row=5, values_only=True):
                if isinstance(row[index], int):
                    existing_drop_ids.add(row[index])
        wb.close()
    candidate_drop = set(range(22101, 22131)) | set(range(22201, 22231)) | set(range(22306, 22331)) | {22400, 22451, 22452, 22453}
    return {
        "item_collisions": sorted(item_id for item_id in expected_items if item_id in existing_items and existing_items[item_id] not in accepted_item_names[item_id]),
        "generate_collisions": sorted(generate_id_ for generate_id_, name in expected_generates.items() if generate_id_ in existing_generates and existing_generates[generate_id_] != name),
        "drop_collisions": sorted(candidate_drop & existing_drop_ids),
    }


def validation_rows(
    *,
    model: dict,
    main_rows: list[list],
    sub_rows: list[list],
    box_rows: list[list],
    generate_rows_data: list[list],
    material_rows: list[list],
    sub_material_rows_data: list[list],
    preview_item_rows: list[list],
    root_rows: list[list],
    box_pool_rows: list[list],
    extra_pool_rows: list[list],
    main_pool_rows: list[list],
    sub_pool_rows: list[list],
    first_rows: list[list],
    equipment_rows: list[list],
    ui_rows: list[list],
    collisions: dict,
) -> list[list]:
    checks: list[tuple[str, object, object, str]] = []
    checks.extend(
        [
            ("主属性行数", len(main_rows), 480, "8×5×12"),
            ("副属性行数", len(sub_rows), 600, "10×5×12"),
            ("副本层数", len(model["layers"]), 30, "MD三张30层表对齐"),
            ("层级宝箱Items", len(box_rows), 150, "30×5"),
            ("Generate行数", len(generate_rows_data), 150, "30×5"),
            ("主材Items", len(material_rows), 72, "8×3×3"),
            ("副材Items", len(sub_material_rows_data), 4, "副材1..4"),
            ("UI预览占位Items", len(preview_item_rows), 22, "12等级箱+9主材档位品质+1随机副材"),
            ("常规根Drop行", len(root_rows), 110, "第1～5层各2分支，第6～30层各4分支"),
            ("固定箱池行", len(box_pool_rows), 150, "保留30层×5品质稳定行结构，未开放品质权重为0"),
            ("副材池行", len(sub_pool_rows), 4, "4种等权"),
            ("EquipmentLevel行", len(equipment_rows), 150, "30×5"),
            ("UIlevel行", len(ui_rows), 150, "正式现状30×5"),
            ("Items候选ID冲突", len(collisions["item_collisions"]), 0, json.dumps(collisions["item_collisions"])),
            ("Generate候选ID冲突", len(collisions["generate_collisions"]), 0, json.dumps(collisions["generate_collisions"])),
            ("Drop候选ID冲突", len(collisions["drop_collisions"]), 0, json.dumps(collisions["drop_collisions"])),
        ]
    )
    for label, rows in [("固定箱池", box_pool_rows), ("额外箱池", extra_pool_rows), ("主材池", main_pool_rows)]:
        groups = defaultdict(int)
        for row in rows:
            groups[row[1]] += row[12]
        checks.append((f"{label}权重非10000池数", sum(1 for total in groups.values() if total != WEIGHT_SCALE), 0, f"{len(groups)}池"))
    checks.append(("副材池权重和", sum(row[12] for row in sub_pool_rows), WEIGHT_SCALE, "2500×4"))
    checks.append(("首通材料提案层数", len(FIRST_MATERIAL_CATEGORY), 15, "第1～5层已去材料，第6层保留"))
    early_material_pool_ids = set(range(MAIN_MATERIAL_POOL_BASE, MAIN_MATERIAL_POOL_BASE + CRAFT_MATERIAL_START_LAYER - 1)) | {SUB_MATERIAL_POOL_ID}
    checks.append(("前5层常规材料分支", sum(1 for row in root_rows if 20005101 <= row[1] <= 20005105 and row[4] in early_material_pool_ids), 0, "不引用主材/副材池"))
    checks.append(("首通根DropId覆盖", len({row[1] for row in first_rows if 20000010 <= row[1] <= 20000039}), 30, "20000010..39"))
    checks.append(("常规根DropId覆盖", len({row[1] for row in root_rows}), 30, "20005101..30"))
    result = []
    for label, actual, expected, note in checks:
        result.append([label, actual, expected, "PASS" if actual == expected else "FAIL", note])
    return result


def build_workbook(output_path: Path, config_root: Path, report_path: Path) -> dict:
    if not config_root.is_dir():
        raise NotADirectoryError(config_root)
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    official_before = source_records(config_root)
    official_before_map = {row["relative_path"]: row for row in official_before}
    md_snapshot = md_records()
    model = load_md_model()

    main_rows = main_attribute_rows(model)
    sub_rows = sub_attribute_rows(model)
    layer_rows = layer_input_rows(model)
    box_rows = box_item_rows(model)
    generate_rows_data = generate_rows(model)
    material_rows = main_material_item_rows()
    sub_material_rows_data = sub_material_item_rows()
    preview_item_rows = preview_placeholder_item_rows()
    root_rows = regular_root_drop_rows(model)
    box_pool_rows = regular_box_pool_rows(model)
    extra_pool_rows = extra_box_pool_rows(model)
    main_pool_rows = main_material_pool_rows(model)
    sub_pool_rows = sub_material_pool_rows()
    first_rows, first_summary = first_clear_rows(model)
    equipment_rows = equipment_level_rows()
    ui_rows = ui_level_rows(config_root, model)
    collisions = check_candidate_ids(config_root)
    if any(collisions.values()):
        raise AssertionError(f"候选ID与正式现状冲突: {collisions}")

    counts = {
        "main_attribute": len(main_rows),
        "sub_attribute": len(sub_rows),
        "layer_input": len(layer_rows),
        "box_items": len(box_rows),
        "generate": len(generate_rows_data),
        "main_material_items": len(material_rows),
        "sub_material_items": len(sub_material_rows_data),
        "preview_items": len(preview_item_rows),
        "regular_root": len(root_rows),
        "regular_box_pool": len(box_pool_rows),
        "extra_box_pool": len(extra_pool_rows),
        "main_material_pool": len(main_pool_rows),
        "sub_material_pool": len(sub_pool_rows),
        "regular_drop_rows": len(root_rows) + len(box_pool_rows) + len(extra_pool_rows) + len(main_pool_rows) + len(sub_pool_rows),
        "first_drop_rows": len(first_rows),
        "equipment_level": len(equipment_rows),
        "ui_level": len(ui_rows),
    }

    validation = validation_rows(
        model=model,
        main_rows=main_rows,
        sub_rows=sub_rows,
        box_rows=box_rows,
        generate_rows_data=generate_rows_data,
        material_rows=material_rows,
        sub_material_rows_data=sub_material_rows_data,
        preview_item_rows=preview_item_rows,
        root_rows=root_rows,
        box_pool_rows=box_pool_rows,
        extra_pool_rows=extra_pool_rows,
        main_pool_rows=main_pool_rows,
        sub_pool_rows=sub_pool_rows,
        first_rows=first_rows,
        equipment_rows=equipment_rows,
        ui_rows=ui_rows,
        collisions=collisions,
    )
    if any(row[3] != "PASS" for row in validation):
        raise AssertionError([row for row in validation if row[3] != "PASS"])

    # 以P01作为Portable数据子包，在同一工作簿前部增加P02全链路Sheet。
    base_report = report_path.with_name(report_path.stem + "-p01-base.json")
    p01.build_workbook(output_path, config_root, base_report)
    wb = load_workbook(output_path)
    wb.properties.title = "映射装备全链路配置包 P02"
    wb.properties.subject = "属性-生成-关卡-Drop-UI-打造/合成全链路映射"
    wb.properties.creator = "Codex / Vgame numerical workflow"

    if "00_说明" in wb.sheetnames:
        wb["00_说明"].title = "P01_原说明"
        wb["P01_原说明"]["A1"] = "P01 Portable子包原说明（P02主包内嵌）"
    if "11_QualityPatch" in wb.sheetnames:
        ws = wb["11_QualityPatch"]
        ws["A1"] = "SpecialEquipmentQuality：原P01补丁（P02更正：禁止单独粘贴）"
        ws["B3"] = "P02原子性门禁：必须与SpecialEquipmentMain、Effect、EffectDrop、装备主属性引用和运行时公式同批更新；不得单贴M:N。"
        for row in (1, 3):
            for cell in ws[row]:
                cell.fill = PatternFill("solid", fgColor=p01.PALE_RED)
    for sheet_name in ["01_PortableExp", "02_SubAttrCoef", "03_PortableLvUp", "04_CompoundProb", "05_CraftProb", "10_CompoundCost", "11_QualityPatch"]:
        if sheet_name in wb.sheetnames:
            apply_bilingual_headers(wb[sheet_name])

    add_overview(wb, counts, generated_at)
    add_table_sheet(
        wb,
        name="01_全链状态",
        title="映射装备全链路配置状态矩阵",
        target="Vgame正式配置跨表影响面",
        instruction="每一个涉及模块都必须在此有明确状态；NEEDS_*/BLOCKED不允许伪装成正式可贴。",
        headers=["链路", "正式表/模块", "目标内容", "状态", "当前事实", "P02交付"],
        rows=full_chain_status_rows(),
        status="MIXED",
    )
    add_table_sheet(
        wb,
        name="02_ID分配",
        title="P02候选ID分配（正式落表前须再查重）",
        target="Items / SpecialEquipmentGenerate / DropId",
        instruction="候选ID已对当前Datas做全局冲突扫描；本次不写入正式表。",
        headers=["命名空间", "用途", "起始ID", "结束ID", "数量", "编码规则", "状态", "说明"],
        rows=id_plan_rows(),
        status="PROPOSED",
    )
    main_ws = add_table_sheet(
        wb,
        name="10_主属性480",
        title="主属性完整目标矩阵（480点）",
        target="建议新表 SpecialEquipmentMainCurve；现SpecialEquipmentMain无法精确承载",
        instruction="数值来自MD公式精确计算；‘MD展示系数’仅为3位展示对照，目标值按公式系数计算。",
        headers=["RowId", "部位", "Part", "主属性", "Attribute", "品质", "Quality", "EquipLv", "Red60Target", "QualityCoef", "FormulaLevelCoef", "MDDisplayCoef3", "TargetValue", "Unit", "Status"],
        rows=main_rows,
        status="NEEDS_SCHEMA",
    )
    main_ws.freeze_panes = "A5"
    sub_ws = add_table_sheet(
        wb,
        name="11_副属性600",
        title="副属性完整目标矩阵（600点）",
        target="建议新表 SpecialEquipmentSubCurve；现Effect/EffectDrop需ID迁移与语义去重",
        instruction="10类×5品质×12等级全量输出；物理/魔法伤害加成不再进入在用池，正式生成必须按Attribute语义去重。",
        headers=["RowId", "副属性", "Attribute", "品质", "Quality", "EquipLv", "Red60Target", "QualityCoef", "FormulaLevelCoef", "MDDisplayCoef3", "TargetValue", "Unit", "Status"],
        rows=sub_rows,
        status="NEEDS_SCHEMA",
    )
    sub_ws.freeze_panes = "A5"
    add_table_sheet(
        wb,
        name="12_属性落表门禁",
        title="属性正式落表的原子更新门禁",
        target="SpecialEquipment / Main / Quality / SubAttrCoef / Effect / EffectDrop / LvUp",
        instruction="Quality系数、Main、Effect、主属性引用必须作为一个原子批次；禁止单表试贴。",
        headers=["正式表", "字段/范围", "目标", "状态", "原因/解除条件"],
        rows=attribute_gate_rows(),
        status="NEEDS_SCHEMA",
    )
    add_table_sheet(
        wb,
        name="20_副本30层",
        title="映射装备副本30层权威数值输入",
        target="Drop/UIlevel/Generate的共享参数层",
        instruction="本Sheet由05_玩法_映射副本经济沉淀MD三张30层表直接解析，不依赖参数Excel。",
        headers=["Layer", "KeyItemId", "FixedBoxes", "ExtraBoxProb", "ExpectedBoxes", "GreenBox", "BlueBox", "PurpleBox", "OrangeBox", "RedBox", "GradeList1000", "MaterialLevel", "CraftTier", "MainMatProb", "PurpleMat", "OrangeMat", "RedMat", "SubMatCount", "FirstArchive", "Status"],
        rows=layer_rows,
        status="READY",
    )
    item_headers = ["Id", "Name", "ParaList", "ItemType", "ItemSubType", "ChestOpenMode", "Icon", "LittleIcon", "ItemQuality", "Description", "##", "AccessList", "ShopId", "NumLimit", "RelatedId", "IsValid", "Status"]
    add_table_sheet(
        wb,
        name="21_层级宝箱Items150",
        title="Items：30层×5品质层级宝箱",
        target="items/Items.xlsx / items / B:Q（候选ID 4201..4350）",
        instruction="数据完整，但须先实现按确切ItemId/层级开箱；图标暂复用现有映射装备通用图标。",
        headers=item_headers,
        rows=box_rows,
        status="PROPOSED_RUNTIME_BLOCKED",
    )
    add_table_sheet(
        wb,
        name="22_Generate150",
        title="SpecialEquipmentGenerate：层级宝箱开装配置",
        target="SpecialEquipment/SpecialEquipmentGenerate.xlsx / SpecialEquipment / Id→B，GradeList..GenerateMin→E:K",
        instruction="每个层级宝箱生成1件装备；部位8等权，等级池和宝箱品质池都已按MD展开。",
        headers=["Id", "##Name", "GradeList", "QualityList", "UnidentifiedList", "PartList", "SpecialEquipmentId", "GenerateMax", "GenerateMin", "Status"],
        rows=generate_rows_data,
        status="PROPOSED_RUNTIME_BLOCKED",
    )
    material_headers = item_headers[:-1] + ["CraftTier", "Category", "MaterialQuality", "Status"]
    add_table_sheet(
        wb,
        name="23_主材Items72",
        title="Items：72种打造主材",
        target="items/Items.xlsx / items / B:Q（正式ID 1080..1151）",
        instruction="8档×3大类×3品质全部分配候选ID；ItemSubType/正式素材/堆叠上限需与程序和美术确认。",
        headers=material_headers,
        rows=material_rows,
        status="PROPOSED_ID_SCHEMA_BLOCKED",
    )
    sub_material_headers = item_headers[:-1] + ["SubMaterialIndex", "Status"]
    add_table_sheet(
        wb,
        name="24_副材Items4",
        title="Items：4种通用打造副材",
        target="items/Items.xlsx / items / B:Q（正式ID 1152..1155）",
        instruction="武器用1+2，防具用2+3，首饰用3+4；ItemSubType/正式素材需确认。",
        headers=sub_material_headers,
        rows=sub_material_rows_data,
        status="PROPOSED_ID_SCHEMA_BLOCKED",
    )
    add_table_sheet(
        wb,
        name="24A_预览占位Items22",
        title="Items：UIlevel等级箱与随机材料预览占位",
        target="items/Items.xlsx / items / B:Q（正式ID 4351..4364）",
        instruction="22个道具只供UIlevel奖励展示：12个装备等级箱、9个主材档位×最高品质、1个随机副材；等级箱同时用于Reward与FirstReward，不按品质区分；不得进入Drop、背包、商店或打造消耗。",
        headers=item_headers,
        rows=preview_item_rows,
        status="UI_PREVIEW_ONLY",
    )
    drop_instruction = "禁止覆盖公式列：按40_Drop粘贴规程先人工预建行/下拉公式，再粘贴对应纯值列。"
    add_table_sheet(wb, name="25_Drop常规根110", title="Drop_dungeon：前5层两分支、后25层四分支", target="Drop/Drop_dungeon.xlsx / Drop", instruction=drop_instruction + " 第1～5层仅有固定宝箱和额外宝箱分支；第6层开始有主材和副材。", headers=DROP_HEADERS, rows=root_rows, status="FORMULA_MANUAL")
    add_table_sheet(wb, name="26_Drop宝箱池150", title="Drop_dungeon：30层固定宝箱品质池", target="Drop/Drop_dungeon.xlsx / Drop", instruction=drop_instruction, headers=DROP_HEADERS, rows=box_pool_rows, status="FORMULA_MANUAL")
    add_table_sheet(wb, name="27_Drop额外箱池", title="Drop_dungeon：30层额外宝箱独立池", target="Drop/Drop_dungeon.xlsx / Drop", instruction=drop_instruction + " 每池含空掉落，权重合10000。", headers=DROP_HEADERS, rows=extra_pool_rows, status="FORMULA_MANUAL")
    add_table_sheet(wb, name="28_Drop主材池", title="Drop_dungeon：第6～30层主材独立池", target="Drop/Drop_dungeon.xlsx / Drop", instruction=drop_instruction + " 第1～5层不生成主材池；第6层起概率=主材命中×大类×品质，含空掉落。", headers=DROP_HEADERS, rows=main_pool_rows, status="PROPOSED_ID_FORMULA_MANUAL")
    add_table_sheet(wb, name="29_Drop副材池4", title="Drop_dungeon：副材1/2/3/4等权共用池", target="Drop/Drop_dungeon.xlsx / Drop", instruction=drop_instruction + " 根包按层固定调1..4次。", headers=DROP_HEADERS, rows=sub_pool_rows, status="PROPOSED_ID_FORMULA_MANUAL")
    add_table_sheet(
        wb,
        name="30_首通提案",
        title="30层首通重配提案（需用户确认）",
        target="DropId 20000010..20000039",
        instruction="匙x1和宝箱节奏沿用MD；第1～5层不投放主材/副材，原材料位改为蓝宝箱；第6～8层统一按10档过渡，第9层起旧胚料位按‘当层打造档+同大类+紫主材x1’映射。",
        headers=["Layer", "FirstRewardDrop", "MD旧额外奖励留档", "P02新提案", "Status"],
        rows=first_summary,
        status="PROPOSED_DESIGN_APPROVAL",
    )
    add_table_sheet(wb, name="30A_首通Drop纯值", title="Drop_dungeon：首通重配纯值行", target="Drop/Drop_dungeon.xlsx / Drop", instruction=drop_instruction + " 包含未批准的主材提案，批准前不得进正式表。", headers=DROP_HEADERS, rows=first_rows, status="PROPOSED_DESIGN_APPROVAL")
    add_table_sheet(
        wb,
        name="31_EquipmentLevel150",
        title="EquipmentLevel：30层×5品质战斗难度映射",
        target="level/EquipmentLevel.xlsx / EquipmentLevel / 建议原子替换B5:E124并追加B125:E154",
        instruction="候选口径为Green->x1, Blue->x2, Purple->x3, Orange->x4, Red->x5；不是只追加Green。替换前需检查Id1..120外部引用。",
        headers=["Id", "UiLevelId", "EquipmentQuality", "LevelId", "Status"],
        rows=equipment_rows,
        status="CONDITIONAL_RUNTIME_REFERENCE_GATE",
    )
    add_table_sheet(
        wb,
        name="32_UIlevel150",
        title="UIlevel：30层×5结算变体奖励预览",
        target="level/UIlevel.xlsx / level / 正式行247:396的指定字段",
        instruction="仅基准行(末位1)保留FirstRewardDrop/FallRewardDrop；Reward与FirstReward中的宝箱均按当层装备等级池逐级展示，品质不参与展示；主材/副材口径不变，负一数量表示仅展示图标。",
        headers=["LevelId", "Name", "LevelType", "TierNum", "Variant", "Unlock", "Reward", "FirstReward", "FirstRewardDrop", "FallRewardDrop", "MultiSettlementTimes", "Vitality", "Status"],
        rows=ui_rows,
        status="PROPOSED_ID_UI_SEMANTICS_GATE",
    )
    add_table_sheet(
        wb,
        name="33_关卡入口链",
        title="LevelType/SystemOpen/Unlock/SpecialLevel/level/globals链路",
        target="关卡入口、解锁、战斗关卡与全局宝箱分组",
        instruction="已对齐的表明确NO_CHANGE；不把没有数值变更的战斗Level强行改掉。",
        headers=["模块", "正式文件", "主键/范围", "字段", "现值", "P02目标", "状态", "说明"],
        rows=entry_chain_rows(config_root),
        status="MIXED",
    )
    add_table_sheet(
        wb,
        name="34_ItemAccess",
        title="ItemAccess：映射装备本获取途径跳转",
        target="items/ItemAccess.xlsx / ItemAccess / Id=26",
        instruction="当前GotoId=208是旧入口；候选改为314后，需联调并确认SystemOpen208/Unlock4108退场。",
        headers=["Id", "Name", "Icon", "Description", "CurrentGotoId", "ProposedGotoId", "SaoDangSupport", "Status", "Note"],
        rows=item_access_rows(config_root),
        status="PROPOSED_RUNTIME_ROUTE_GATE",
    )
    add_table_sheet(
        wb,
        name="35_合成打造覆盖",
        title="Portable合成/打造/锻造台/分解覆盖矩阵",
        target="SpecialEquipment/Portable及建议新分解表",
        instruction="P01数据页作为本包子页保留；Range、Craft、Resolve缺口仍不得伪装已配完。",
        headers=["正式表/建议表", "目标数据", "P02 Sheet", "状态", "说明"],
        rows=portable_coverage_rows(),
        status="MIXED",
    )
    add_table_sheet(
        wb,
        name="40_Drop粘贴规程",
        title="Drop_dungeon公式安全粘贴规程",
        target="Drop/Drop_dungeon.xlsx / Drop",
        instruction="该规程是正式进表的强制门禁；P02不会代替人工公式行处理。",
        headers=["Step", "操作", "允许", "禁止", "验收"],
        rows=[
            [1, "备份正式Drop_dungeon，记录当前文件hash", "只读检查", "未备份直改", "hash已记录"],
            [2, "按P02各Drop Sheet行数人工预建目标行", "在Excel内可见操作", "脚本自动insert/delete", "行数与包一致"],
            [3, "从邻接正式行下拉B/C/F等公式列", "保留相对引用", "粘贴值覆盖公式", "无#REF!/公式模式一致"],
            [4, "仅粘贴P02的纯值列", "仅粘贴值", "粘贴格式/表头/空白控制列", "DropId/DropId2/ItemId对齐"],
            [5, "检查每个随机池权重", "总和10000", "混用P01的1000权重", "所有池PASS"],
            [6, "检查UIlevel外键和预览", "入口DropId存在", "预览与真实包不一致", "30层常规/首通全存在"],
            [7, "运行Luban/CheckRules/客户端+服务端冒烟", "正式评审后执行", "只看Excel不导出", "导出、开箱、结算全通过"],
        ],
        status="FORMULA_MANUAL",
    )
    add_table_sheet(
        wb,
        name="41_边界排除",
        title="本期明确不落表/已废弃的配置",
        target="ItemChest / Shop / Task / 旧升级打孔鉴定 / 洗练",
        instruction="这些项不是忘了配，而是依据最新MD或现运行链明确标注N/A/OUT_OF_SCOPE/DEPRECATED。",
        headers=["正式表/模块", "主题", "状态", "证据/说明"],
        rows=boundary_rows(),
        status="MIXED",
    )
    add_table_sheet(
        wb,
        name="90_P02阻断",
        title="P02正式落表前的Schema/程序/业务阻断",
        target="正式Datas写入、Luban导出和上线验收门禁",
        instruction="P0未解除时，只能评审映射数据，不得宣称‘可直接上线’。",
        headers=["优先级", "阻断", "当前原因", "解除方式", "验收断言"],
        rows=blocker_rows(),
        status="NEEDS_SCHEMA",
    )
    add_table_sheet(
        wb,
        name="99_P02验算",
        title="P02生成时独立数量/权重/ID验算",
        target="P02工作簿内部门禁",
        instruction="本页是生成时固化结果；另有独立validator会从文件重新读取验证。",
        headers=["验算项", "实算", "期望", "结果", "口径"],
        rows=validation,
        status="READY",
    )

    meta = wb.create_sheet("__p02_meta__")
    meta.append(["key", "value"])
    metadata = {
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "generated_at": generated_at,
        "official_config_write": False,
        "luban_executed": False,
        "weight_scale_drop": WEIGHT_SCALE,
        "source_md_json": json.dumps(md_snapshot, ensure_ascii=False, separators=(",", ":")),
        "official_snapshot_json": json.dumps(official_before, ensure_ascii=False, separators=(",", ":")),
        "counts_json": json.dumps(counts, ensure_ascii=False, separators=(",", ":")),
        "id_collisions_json": json.dumps(collisions, ensure_ascii=False, separators=(",", ":")),
        "craft_unlock": f"SystemOpen.Id=54 -> UnlockId=1198 -> UnLock_UUT_Level({CRAFT_UNLOCK_LEVEL_ID})",
        "craft_material_start_layer": CRAFT_MATERIAL_START_LAYER,
        "first_clear_material_proposal": "layers 1-5 no material; layers 6-30 archived material slots map to same-layer-craft-tier + archived-category + Purple x1",
        "p01_quality_patch_status": "superseded_atomic_block_only",
    }
    for key, value in metadata.items():
        meta.append([key, value])
    meta.sheet_state = "veryHidden"

    p02_order = [
        "00_P02总览", "01_全链状态", "02_ID分配", "10_主属性480", "11_副属性600", "12_属性落表门禁",
        "20_副本30层", "21_层级宝箱Items150", "22_Generate150", "23_主材Items72", "24_副材Items4", "24A_预览占位Items22",
        "25_Drop常规根110", "26_Drop宝箱池150", "27_Drop额外箱池", "28_Drop主材池", "29_Drop副材池4",
        "30_首通提案", "30A_首通Drop纯值", "31_EquipmentLevel150", "32_UIlevel150", "33_关卡入口链", "34_ItemAccess",
        "35_合成打造覆盖", "40_Drop粘贴规程", "41_边界排除", "90_P02阻断", "99_P02验算",
    ]
    remaining = [ws for ws in wb.worksheets if ws.title not in p02_order]
    wb._sheets = [wb[name] for name in p02_order] + remaining
    try:
        wb.calculation.calcMode = "auto"
        wb.calculation.fullCalcOnLoad = True
        wb.calculation.forceFullCalc = True
    except Exception:
        pass
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    wb.close()

    official_after = source_records(config_root)
    official_after_map = {row["relative_path"]: row for row in official_after}
    if official_before_map != official_after_map:
        changed = [path for path in official_before_map if official_before_map[path] != official_after_map.get(path)]
        raise AssertionError(f"正式Datas发生非预期写入: {changed}")

    report = {
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "generated_at": generated_at,
        "workbook": str(output_path),
        "workbook_sha256": sha256_file(output_path),
        "official_config_root": str(config_root),
        "official_config_write": False,
        "luban_executed": False,
        "official_hashes_before": official_before,
        "official_hashes_after": official_after,
        "official_hashes_unchanged": True,
        "source_md": md_snapshot,
        "counts": counts,
        "id_collisions": collisions,
        "validation": validation,
        "first_clear_material_status": "PROPOSED_DESIGN_APPROVAL",
        "p01_quality_patch_status": "SUPERSEDED_ATOMIC_BLOCK_ONLY",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        base_report.unlink()
    except FileNotFoundError:
        pass
    return report


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成映射装备全链路映射配置包 P02")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--config-root", type=Path, default=DEFAULT_CONFIG_ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = build_workbook(args.output.resolve(), args.config_root.resolve(), args.report.resolve())
    print(json.dumps({"status": "PASS", "package_id": report["package_id"], "workbook": report["workbook"], "counts": report["counts"], "official_hashes_unchanged": report["official_hashes_unchanged"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
