# -*- coding: utf-8 -*-
"""
validate_economy_against_config.py — P4c 经济模块产销表 vs 正式配置只读校验

验证目标：
  - P4 模块产销表里的 ItemId 是否存在于正式 Items。
  - DropId / RewardId 引用是否存在于逻辑 Drop，并尽量校验道具与数量。
  - 已能明确映射的正式表（签到、通行证、角色升级、专武、炮台、商店、抽卡）做值对照。

边界：
  - 只读正式配置，不修改 Datas。
  - 设计页没有 LevelId / DropId / 配置主键的内容，只能标记为口径不确定或未找到正式入口。
"""
import io
import os
import re
import sys
import warnings
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ECONOMY_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(ECONOMY_DIR)
NUM_DIR = os.path.dirname(V2_DIR)
CONFIG_ROOT = os.environ.get("VGAME_CONFIG_DATAS", "")

SUMMARY = os.path.join(ECONOMY_DIR, "全资源产销总表.xlsx")
REPORT_XLSX = os.path.join(ECONOMY_DIR, "正式配置校验报告.xlsx")
REPORT_MD = os.path.join(ECONOMY_DIR, "_reports", "P4c_正式配置校验.md")

RESULT_HEADERS = [
    "结果",
    "模块/系统",
    "分组",
    "方向",
    "资源/道具",
    "道具ID",
    "数量",
    "来源页",
    "来源行",
    "校验项",
    "正式配置",
    "正式值",
    "设计值",
    "说明",
]

QUESTION_HEADERS = ["问题类型", "模块/系统", "来源", "需要确认的问题", "样例"]
REAL_DIFF_STATUSES = {"不一致", "未找到"}

ALIASES = {
    "金币": "猎鹰金币",
    "钻石": "元晶",
    "体力": "储能",
    "体力药": "元能核心",
    "玩家经验": "行旅帧片",
    "角色抽卡券": "旅券",
    "角色抽卡券普通": "旅券",
    "专武抽卡券": "收容凭证",
    "专武抽卡券普通": "收容凭证",
    "角色抽卡券限时": "限时旅券",
    "专武抽卡券限时": "应急收容凭证",
    "万能星盘点": "熔晶",
    "额外星盘点": "熔晶",
    "映射装备经验": "合淬喷剂",
    "邮票经验": "沿途随笔",
    "抽卡大代币": "印象余音",
    "抽卡小代币": "残留余响",
    "竞技场代币": "勇士勋章",
    "爬塔代币": "梦境碎片",
    "公会个人代币": "聚集地兑换币",
    "公会集体代币": "奉献之核",
    "传说装备兑换材料": "高阶零件",
    "史诗装备兑换材料": "低阶零件",
    "角色经验中2000": "中阶记录盘",
    "角色经验高10000": "高阶记录盘",
    "专武经验中4000": "录像带",
    "专武经验高20000": "未知笔记",
    "旅券经验": "沿途随笔",
    "主角装备经验": "合淬喷剂",
    "炮台升级小材料": "校准元件",
    "红色装备打孔器": "红色精密打孔器",
    "金色装备打孔器": "金色精密打孔器",
    "紫色装备打孔器": "紫色精密打孔器",
    "蓝色装备打孔器": "蓝色精密打孔器",
    "映射装备金色": "随机史诗装备",
    "映射装备红色": "随机传说装备",
    "主角装备红色": "随机传说装备",
    "B炮台": "特供装置·穿透",
    "3级宝石": "3级宝石掉落箱",
    "4级宝石": "4级宝石掉落箱",
    "5级宝石": "5级宝石掉落箱",
    "6级宝石": "6级宝石掉落箱",
}


def cfg_path(*parts):
    return os.path.join(CONFIG_ROOT, *parts)


def clean(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return value


def is_num(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def to_int(value):
    if value in (None, ""):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    text = str(value).strip()
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.0+", text):
        return int(float(text))
    return None


def to_num(value):
    if value in (None, ""):
        return None
    if is_num(value):
        return value
    text = str(value).strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", text):
        num = float(text)
        return int(num) if num.is_integer() else num
    return None


def prop_list(value):
    value = clean(value)
    if not value:
        return []
    result = []
    for part in str(value).split(";"):
        part = part.strip()
        if not part:
            continue
        bits = [p.strip() for p in part.split(",")]
        if len(bits) >= 2 and to_int(bits[0]) is not None and to_num(bits[1]) is not None:
            result.append((to_int(bits[0]), to_num(bits[1])))
    return result


def header_values(ws, row_idx, max_probe=256):
    values = []
    last_non_empty = 0
    for idx, row in enumerate(ws.iter_rows(min_row=row_idx, max_row=row_idx, max_col=max_probe, values_only=True), start=1):
        for col, value in enumerate(row, start=1):
            value = clean(value)
            values.append(value)
            if value != "":
                last_non_empty = col
        break
    return values[:last_non_empty]


def row_dicts(path, sheet_name=None):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[sheet_name] if sheet_name else wb[wb.sheetnames[0]]
    headers = header_values(ws, 1)
    rows = []
    if headers and headers[0] == "##var":
        data_headers = headers[1:]
        max_col = max(len(headers), 2)
        start = 5
        if str(clean(ws.cell(3, 1).value)).startswith("##"):
            start = 5
        elif clean(ws.cell(3, 1).value) not in ("##group", "##"):
            start = 3
        blank_streak = 0
        for offset, values in enumerate(ws.iter_rows(min_row=start, max_col=max_col, values_only=True), start=start):
            values = [clean(v) for v in values]
            first = values[0] if values else ""
            if str(first).startswith("##"):
                continue
            if all(v == "" for v in values):
                blank_streak += 1
                if blank_streak >= 200:
                    break
                continue
            blank_streak = 0
            row = {"_row": offset}
            for idx, header in enumerate(data_headers, start=2):
                if header:
                    row[str(header)] = values[idx - 1] if idx - 1 < len(values) else ""
            rows.append(row)
        wb.close()
        return rows
    max_col = max(len(headers), 1)
    blank_streak = 0
    for offset, values in enumerate(ws.iter_rows(min_row=2, max_col=max_col, values_only=True), start=2):
        values = [clean(v) for v in values]
        if all(v == "" for v in values):
            blank_streak += 1
            if blank_streak >= 200:
                break
            continue
        blank_streak = 0
        row = {"_row": offset}
        for c, header in enumerate(headers, start=1):
            if header:
                row[str(header)] = values[c - 1] if c - 1 < len(values) else ""
        rows.append(row)
    wb.close()
    return rows


def load_ledger():
    wb = openpyxl.load_workbook(SUMMARY, data_only=True, read_only=True)
    ws = wb["追溯_全明细"]
    headers = header_values(ws, 1)
    max_col = max(len(headers), 1)
    rows = []
    blank_streak = 0
    for offset, values in enumerate(ws.iter_rows(min_row=2, max_col=max_col, values_only=True), start=2):
        values = [clean(v) for v in values]
        if all(v == "" for v in values):
            blank_streak += 1
            if blank_streak >= 200:
                break
            continue
        blank_streak = 0
        row = {headers[c - 1]: values[c - 1] if c - 1 < len(values) else "" for c in range(1, len(headers) + 1)}
        row["_row"] = offset
        if row.get("资源/道具"):
            rows.append(row)
    wb.close()
    return rows


def load_items():
    rows = row_dicts(cfg_path("items", "Items.xlsx"), "items")
    by_id = {}
    by_name = {}
    for row in rows:
        item_id = to_int(row.get("Id"))
        if item_id is None:
            continue
        by_id[item_id] = row
        name = clean(row.get("Name"))
        if name:
            by_name[name] = row
    return by_id, by_name


def load_drops():
    drop_dir = cfg_path("Drop")
    result = defaultdict(list)
    source_by_drop = defaultdict(set)
    for name in os.listdir(drop_dir):
        if not name.startswith("Drop_") or not name.endswith(".xlsx") or ".bak" in name:
            continue
        path = os.path.join(drop_dir, name)
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        sheet_name = "Drop" if "Drop" in wb.sheetnames else wb.sheetnames[0]
        wb.close()
        for row in row_dicts(path, sheet_name):
            drop_id = to_int(row.get("DropId"))
            if drop_id is None:
                continue
            item_id = to_int(row.get("DropItem_id"))
            min_num = to_num(row.get("DropItemNumMin"))
            max_num = to_num(row.get("DropItemNumMax"))
            item = {
                "file": name,
                "row": row.get("_row"),
                "drop_id": drop_id,
                "item_id": item_id,
                "min": min_num,
                "max": max_num,
                "type": row.get("DropType"),
                "weight": row.get("DropWeight"),
                "name": row.get("DropName") or row.get("None"),
            }
            result[drop_id].append(item)
            source_by_drop[drop_id].add(name)
    return result, source_by_drop


def add_result(results, row, status, check, cfg, formal, design, note):
    results.append({
        "结果": status,
        "模块/系统": row.get("系统", ""),
        "分组": row.get("分组", ""),
        "方向": row.get("方向", ""),
        "资源/道具": row.get("资源/道具", ""),
        "道具ID": row.get("道具ID", ""),
        "数量": row.get("数量", ""),
        "来源页": row.get("来源页", ""),
        "来源行": row.get("来源行", ""),
        "校验项": check,
        "正式配置": cfg,
        "正式值": formal,
        "设计值": design,
        "说明": note,
    })


def add_question(questions, kind, row, question, sample):
    questions.append({
        "问题类型": kind,
        "模块/系统": row.get("系统", ""),
        "来源": "%s:%s" % (row.get("来源页", ""), row.get("来源行", "")),
        "需要确认的问题": question,
        "样例": sample,
    })


def item_name_ok(design_name, formal_name):
    design_name = str(clean(design_name))
    formal_name = str(clean(formal_name))
    if not design_name or not formal_name:
        return True
    if design_name == formal_name:
        return True
    if ALIASES.get(design_name) == formal_name:
        return True
    if design_name.startswith("角色经验") and formal_name.startswith("角色经验"):
        return True
    if design_name.startswith("角色经验") and formal_name in ("中阶记录盘", "高阶记录盘"):
        return True
    if design_name.startswith("专武经验") and formal_name.startswith("专武经验"):
        return True
    if design_name.startswith("专武经验") and formal_name in ("泛黄档案", "录像带", "未知笔记"):
        return True
    return False


def formal_value_str(item_id, qty):
    return "%s,%s" % (item_id, qty)


def drop_contains(drop_map, drop_id, item_id, qty):
    items = drop_map.get(drop_id, [])
    if not items:
        return False, "DropId 不存在", ""
    if item_id is None:
        return True, "DropId 存在，未校验道具数量", ";".join(formal_value_str(x["item_id"], x["min"]) for x in items)
    for item in items:
        if item["item_id"] == item_id:
            if qty is None:
                return True, "DropId 含目标道具，未校验数量", formal_value_str(item_id, "%s-%s" % (item["min"], item["max"]))
            if item["min"] == qty and item["max"] == qty:
                return True, "DropId 道具数量一致", formal_value_str(item_id, qty)
            return False, "DropId 含目标道具但数量不同", formal_value_str(item_id, "%s-%s" % (item["min"], item["max"]))
    return False, "DropId 不含目标道具", ";".join(formal_value_str(x["item_id"], x["min"]) for x in items)


def extract_ref_id(row):
    text = "%s %s %s" % (row.get("备注", ""), row.get("进度/条件", ""), row.get("口径", ""))
    m = re.search(r"(?<![A-Za-z])(?:DropId|RewardId)\s*(\d+)", text)
    return to_int(m.group(1)) if m else None


def validate_item_ids(rows, items_by_id, results, questions):
    seen = set()
    for row in rows:
        for field, name_field in [("道具ID", "资源/道具")]:
            item_id = to_int(row.get(field))
            if item_id is None:
                continue
            if item_id == 0 and row.get(name_field) in ("头像", "头像框"):
                add_result(results, row, "按回答忽略", "ItemId 存在性", "items/Items.xlsx",
                           "头像/头像框暂未进 Items", item_id,
                           "用户回答：头像和头像框暂时没有，当前经济校验先忽略。")
                continue
            if row.get(name_field) == "B炮台" and item_id == 96003:
                add_result(results, row, "已按回答修正", "ItemId 存在性", "Arena/Battery.xlsx + items/Items.xlsx",
                           "正式第三个炮台 ItemId=96303", item_id,
                           "用户回答：炮台 ID 已改，使用第三个炮台 ID；生成器已将 B炮台映射为 96303。")
                continue
            key = (item_id, row.get(name_field))
            if key in seen:
                continue
            seen.add(key)
            if item_id not in items_by_id:
                add_result(results, row, "未找到", "ItemId 存在性", "items/Items.xlsx", "缺失", item_id, "设计表道具ID在正式 Items 中未找到。")
                add_question(questions, "ItemId缺失", row, "这个道具 ID 是否还没进正式 Items？", "%s / %s" % (row.get(name_field), item_id))
            else:
                formal_name = items_by_id[item_id].get("Name")
                if item_name_ok(row.get(name_field), formal_name):
                    add_result(results, row, "通过", "ItemId 存在性", "items/Items.xlsx", "%s:%s" % (item_id, formal_name), "%s:%s" % (item_id, row.get(name_field)), "ItemId 存在；名称差异已按别名口径接受。" if formal_name != row.get(name_field) else "ItemId 与名称一致。")
                else:
                    add_result(results, row, "口径不确定", "ItemId 名称", "items/Items.xlsx", "%s:%s" % (item_id, formal_name), "%s:%s" % (item_id, row.get(name_field)), "ItemId 存在，但设计名与正式名不同，且不在已知别名中。")
                    add_question(questions, "名称口径", row, "这个设计名是否应该映射到正式道具名？", "%s -> %s:%s" % (row.get(name_field), item_id, formal_name))


def validate_refs(rows, drop_map, results, questions):
    for row in rows:
        ref_id = extract_ref_id(row)
        if ref_id is None:
            continue
        item_id = to_int(row.get("道具ID"))
        qty = to_num(row.get("数量"))
        ok, note, formal = drop_contains(drop_map, ref_id, item_id, qty)
        status = "通过" if ok and "一致" in note else ("仅引用存在" if ok else "不一致")
        add_result(results, row, status, "DropId/RewardId 内容", "逻辑Drop", formal, "%s,%s via %s" % (item_id, qty, ref_id), note)
        if not ok:
            add_question(questions, "奖励包不一致", row, "设计行引用的 DropId/RewardId 与正式 Drop 内容不一致，是否设计页未同步到配置？", "%s / %s" % (row.get("资源/道具"), row.get("备注") or row.get("进度/条件")))


def validate_signin(rows, results, questions):
    daily = row_dicts(cfg_path("SignInReward", "DailySign.xlsx"))
    monthly = row_dicts(cfg_path("SignInReward", "MonthlyAccumulate.xlsx"))
    travel = row_dicts(cfg_path("SignInReward", "TravelAccumulate.xlsx"))
    daily_map = defaultdict(list)
    for r in daily:
        day = to_int(r.get("day"))
        for item_id, qty in prop_list(r.get("rewardItems")):
            daily_map[day].append((item_id, qty))
    monthly_map = defaultdict(list)
    for r in monthly:
        day = to_int(r.get("AccumulateDay"))
        for item_id, qty in prop_list(r.get("rewardItems")):
            monthly_map[day].append((item_id, qty))
    travel_map = defaultdict(list)
    for r in travel:
        day = to_int(r.get("AccumulateDay"))
        for item_id, qty in prop_list(r.get("rewardItems")):
            travel_map[day].append((item_id, qty))
    def compact(pairs):
        return sorted(set(pairs))
    for row in rows:
        if row.get("来源页") != "签到" or row.get("方向") != "产出":
            continue
        cond = str(row.get("进度/条件", ""))
        item_id = to_int(row.get("道具ID"))
        qty = to_num(row.get("数量"))
        if item_id is None or qty is None:
            continue
        day_match = re.search(r"第(\d+)天", cond)
        acc_match = re.search(r"累计签到(\d+)天", cond)
        if day_match:
            day = int(day_match.group(1))
            formal = compact(daily_map.get(day, []))
            status = "通过" if (item_id, qty) in formal else "不一致"
            note = "按 day + rewardItems 校验。"
            if status != "通过":
                note = "用户要求复查：确认不一致。正式 DailySign day=%s 为 %s；设计为 %s,%s。" % (day, formal, item_id, qty)
            add_result(results, row, status, "每日签到", "SignInReward/DailySign.xlsx", formal, (item_id, qty), note)
        elif acc_match:
            day = int(acc_match.group(1))
            source_row = to_int(row.get("来源行")) or 0
            if source_row <= 5:
                formal = compact(monthly_map.get(day, []))
                cfg = "SignInReward/MonthlyAccumulate.xlsx"
                check = "月累计签到"
            else:
                formal = compact(travel_map.get(day, []))
                cfg = "SignInReward/TravelAccumulate.xlsx"
                check = "生涯累计签到"
            status = "通过" if (item_id, qty) in formal else "不一致"
            note = "按 AccumulateDay + rewardItems 校验。"
            if status != "通过":
                note = "用户要求复查：确认不一致。正式 %s AccumulateDay=%s 为 %s；设计为 %s,%s。" % (cfg, day, formal, item_id, qty)
            add_result(results, row, status, check, cfg, formal, (item_id, qty), note)


def validate_battlepass(rows, drop_map, results, questions):
    bp_rows = row_dicts(cfg_path("Battlepass", "BattlePassReward.xlsx"))
    by_lv = {}
    for r in bp_rows:
        lv = to_int(r.get("TargetParam"))
        if lv is not None:
            by_lv[lv] = r
    for row in rows:
        if row.get("系统") != "通行证" or row.get("来源页") not in ("通行证", "配置页-通行证"):
            continue
        cond = str(row.get("进度/条件", ""))
        lv_match = re.search(r"等级(\d+)", cond)
        ref_id = extract_ref_id(row)
        if ref_id is None and lv_match:
            lv = int(lv_match.group(1))
            bp = by_lv.get(lv)
            if not bp:
                add_result(results, row, "未找到", "通行证等级", "Battlepass/BattlePassReward.xlsx", "缺等级%s" % lv, cond, "正式配置缺少该等级。")
                continue
            ref_id = to_int(bp.get("CommonReward") if "免费" in row.get("分组", "") else bp.get("PassAdditionReward"))
        if ref_id is None:
            continue
        item_id = to_int(row.get("道具ID"))
        qty = to_num(row.get("数量"))
        ok, note, formal = drop_contains(drop_map, ref_id, item_id, qty)
        status = "通过" if ok and "一致" in note else ("仅引用存在" if ok else "不一致")
        add_result(results, row, status, "通行证奖励包", "Battlepass/BattlePassReward.xlsx + Drop_BattlePass", formal, "%s,%s via %s" % (item_id, qty, ref_id), note)
        if not ok:
            add_question(questions, "通行证奖励不一致", row, "通行证设计值与正式 BattlePassReward/Drop_BattlePass 不一致，是否需要同步配置？", "%s %s" % (row.get("进度/条件"), row.get("资源/道具")))


def validate_growth(rows, results, questions):
    hero_lv = {to_int(r.get("Lv")): to_num(r.get("UpgradeCost")) for r in row_dicts(cfg_path("Hero", "HeroLv.xlsx"))}
    weapon_lv = {(to_int(r.get("Lv")), to_int(r.get("Quality"))): to_num(r.get("UpgradeCostExp")) for r in row_dicts(cfg_path("ExclusiveWeapon", "ExclWeaponLv.xlsx"), "EqptLv")}
    battery_lv = {}
    for r in row_dicts(cfg_path("Arena", "BatteryLv.xlsx")):
        lv = to_int(r.get("Lv"))
        q = to_int(r.get("Quality"))
        props = prop_list(r.get("UpgradeCost"))
        if props:
            battery_lv[(lv, q)] = props[0]
    for row in rows:
        src = row.get("来源页")
        cond = str(row.get("进度/条件", ""))
        qty = to_num(row.get("数量"))
        if qty is None:
            continue
        if src == "角色升级" and row.get("资源/道具") == "角色经验":
            m = re.search(r"Lv(\d+)", cond)
            if m:
                lv = int(m.group(1))
                formal = hero_lv.get(lv)
                status = "通过" if formal == qty else "不一致"
                add_result(results, row, status, "角色升级经验", "Hero/HeroLv.xlsx", formal, qty, "按 Lv -> UpgradeCost 校验。")
        elif src == "专武" and row.get("资源/道具") == "专武经验":
            m = re.search(r"Lv(\d+)", cond)
            if m:
                lv = int(m.group(1))
                formal = weapon_lv.get((lv, 4))
                status = "通过" if formal == qty else "不一致"
                add_result(results, row, status, "SSR专武升级经验", "ExclusiveWeapon/ExclWeaponLv.xlsx", formal, qty, "按 Quality=4, Lv -> UpgradeCostExp 校验。")
        elif src == "炮台养成" and row.get("资源/道具") == "炮台升级小材料":
            m = re.search(r"Lv(\d+)", cond)
            if m:
                target_lv = int(m.group(1))
                formal = battery_lv.get((target_lv - 1, 4))
                formal_text = formal_value_str(*formal) if formal else ""
                status = "通过" if formal and formal[1] == qty else "不一致"
                add_result(results, row, status, "S炮台升级材料", "Arena/BatteryLv.xlsx", formal_text, "28,%s" % qty, "设计目标LvN 对应正式 Lv=N-1 的 UpgradeCost。")


def validate_shop(rows, items_by_name, results, questions):
    goods = row_dicts(cfg_path("Shop", "ShopGoods.xlsx"), "Goods")
    exact = set()
    for g in goods:
        item_id = to_int(g.get("ItemId"))
        num = to_num(g.get("Num"))
        price = prop_list(g.get("Price"))
        if price:
            exact.add((item_id, num, price[0][0], price[0][1]))
        else:
            exact.add((item_id, num, None, None))
    for row in rows:
        if row.get("口径") != "商店兑换商品":
            continue
        item_id = to_int(row.get("道具ID"))
        qty = to_num(row.get("数量"))
        cost_name = clean(row.get("货币/成本"))
        cost_id = None
        formal_cost_name = ALIASES.get(cost_name, cost_name)
        if formal_cost_name in items_by_name:
            cost_id = to_int(items_by_name[formal_cost_name].get("Id"))
        cost_qty = to_num(row.get("货币数量"))
        if item_id is None:
            continue
        if (item_id, qty, cost_id, cost_qty) in exact:
            add_result(results, row, "通过", "商店商品", "Shop/ShopGoods.xlsx", (item_id, qty, cost_id, cost_qty), (item_id, qty, cost_id, cost_qty), "ItemId/Num/Price 完全匹配。")
        elif any(g[0] == item_id and g[1] == qty for g in exact):
            formal_matches = [g for g in exact if g[0] == item_id and g[1] == qty]
            add_result(results, row, "按正式配置", "商店商品价格", "Shop/ShopGoods.xlsx", formal_matches, (item_id, qty, cost_id, cost_qty), "用户回答：商店价差以正式配置为准；设计价不再作为待确认问题。")
        else:
            add_result(results, row, "未找到", "商店商品", "Shop/ShopGoods.xlsx", "无匹配商品", (item_id, qty, cost_id, cost_qty), "正式 ShopGoods 未找到同 ItemId/Num 的商品。")


def validate_draw(rows, results, questions):
    draw_rows = row_dicts(cfg_path("Activity", "DrawCard", "DrawCard.xlsx"), "DrawCard")
    one_prices = []
    for r in draw_rows:
        for item_id, qty in prop_list(r.get("OnePrice")):
            one_prices.append((item_id, qty, r.get("Name")))
    for row in rows:
        if row.get("系统") != "抽卡" or row.get("方向") != "消耗":
            continue
        if str(row.get("来源页", "")).startswith("正式:Activity/DrawCard"):
            continue
        item_id = to_int(row.get("道具ID"))
        qty = to_num(row.get("数量"))
        if (item_id, qty) in [(x[0], x[1]) for x in one_prices]:
            add_result(results, row, "通过", "抽卡单抽消耗", "Activity/DrawCard/DrawCard.xlsx", one_prices, (item_id, qty), "OnePrice 中存在同消耗。")
        elif item_id == 2 and qty == 150:
            add_result(results, row, "按回答接受", "抽卡单抽消耗", "Activity/DrawCard/DrawCard.xlsx",
                       one_prices, (item_id, qty),
                       "用户回答：150 钻为实际消耗，抽卡券可用钻石换；正式 OnePrice 中抽卡券消耗视为同一实际付费口径的配置实现。")
        else:
            add_result(results, row, "口径不确定", "抽卡单抽消耗", "Activity/DrawCard/DrawCard.xlsx", one_prices, (item_id, qty), "正式配置单抽消耗通常是抽卡券 PropType；设计表这里可能是钻石价值锚点。")
            add_question(questions, "抽卡消耗口径", row, "设计表的“钻石150”是实际消耗还是价值锚点？正式 DrawCard.OnePrice 当前是抽卡券。", "%s,%s" % (item_id, qty))


def validate_missing_formal_entries(rows, results, questions):
    uncertain_sources = {
        "主线副本": "用户回答：补充。已登记正式 level/UIlevel/Chapter 的 Drop 与体力入口；逐行 Drop 内容仍待奖励包展开。",
        "高难主线关卡": "用户回答：补充。已登记正式 UIlevel 中困难主线 LevelType_Main_Difficult 的 Drop 与体力入口。",
        "资源、装备副本": "用户回答：补充。已登记正式 UIlevel 中金币/角色经验/专武经验副本的 Drop 与体力入口。",
        "旅券副本": "用户回答：补充。已登记正式 UIlevel 中 LevelType_Strategy_* 的 Drop 与体力入口。",
        "映射装备副本": "用户回答：补充。已登记正式 UIlevel 中 LevelType_SpecialEquipment 的 Drop 与体力入口。",
        "任务": "用户回答：补充。已登记正式 Task、DailyActiveReward、WeeklyReward 的奖励包入口。",
        "7日任务": "用户回答：补充。已登记正式 SevenDaySign 入口；若七日任务另有活动任务链，后续继续按 Activity/Task 展开。",
        "公会数值": "用户回答：补充。已登记 GuildMission/GuildComission/GuildLv/GuildBuilding/GuildBargaining 入口。",
        "共鸣装备": "用户回答：补充。已登记 level/EquipmentLevel 与 equipment 旧装备入口；因项目口径旧装备可能非正式，仍标注为候选入口。",
        "角色升星、角色抽卡": "用户回答：补充。已登记 DrawCard 卡池、消耗、保底和 DrawCardPool 入口；概率仍需 DrawCardWeight 专项。",
        "专武升星、抽卡": "用户回答：补充。已登记 DrawCard 卡池、消耗、保底和 DrawCardPool 入口；专武升星仍按专武正式表专项展开。",
        "旅券": "用户回答：补充。已登记 StrategyLv/StrategyResolve/StrategyCraft/StrategyCardShop 正式入口。",
    }
    seen = set()
    for row in rows:
        src = row.get("来源页")
        if src in uncertain_sources and src not in seen:
            seen.add(src)
            status = "已补充入口/待确认正式性" if src == "共鸣装备" else "已补充入口"
            add_result(results, row, status, "正式表主键映射", "见全资源产销总表正式来源行", "已登记入口", src, uncertain_sources[src])


def write_xlsx(results, questions, summary_rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "校验总览"
    ws.append(["P4c 正式配置校验总览"])
    ws.cell(1, 1).font = Font(bold=True, size=14)
    ws.append([])
    ws.append(["结果", "数量"])
    counts = Counter(r["结果"] for r in results)
    for status, count in counts.most_common():
        ws.append([status, count])
    ws.append([])
    ws.append(["模块/系统", "结果", "数量"])
    for key, count in sorted(summary_rows.items()):
        ws.append([key[0], key[1], count])

    def excel_value(value):
        if isinstance(value, (list, tuple, set)):
            return "; ".join(str(v) for v in value)
        if isinstance(value, dict):
            return "; ".join("%s=%s" % (k, v) for k, v in value.items())
        return value

    def add_sheet(name, headers, rows):
        s = wb.create_sheet(name)
        s.append(headers)
        for cell in s[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="D9E1F2")
            cell.alignment = Alignment(horizontal="center")
        for row in rows:
            s.append([excel_value(row.get(h, "")) for h in headers])
        s.freeze_panes = "A2"
        widths = [12, 16, 18, 10, 20, 10, 12, 18, 10, 18, 32, 40, 32, 48]
        for i, width in enumerate(widths[:len(headers)], start=1):
            s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
        for row in s.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        return s

    real_diffs = [r for r in results if r.get("结果") in REAL_DIFF_STATUSES]
    add_sheet("校验明细", RESULT_HEADERS, results)
    add_sheet("真实差异", RESULT_HEADERS, real_diffs)
    add_sheet("需要确认", QUESTION_HEADERS, questions)
    wb.save(REPORT_XLSX)


def write_md(results, questions):
    os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
    counts = Counter(r["结果"] for r in results)
    module_counts = Counter((r["模块/系统"], r["结果"]) for r in results)
    real_diffs = [r for r in results if r.get("结果") in REAL_DIFF_STATUSES]
    lines = [
        "# P4c · 经济层正式配置校验",
        "",
        "> 只读校验 `经济/模块产销表/*.xlsx` 与正式配置 `${VGAME_CONFIG_DATAS}`。不修改 SVN 配置。",
        "",
        "## 结论",
        "",
        f"- 正式配置根: `{CONFIG_ROOT}`",
        f"- 汇总表: `{SUMMARY}`",
        f"- 校验报告: `{REPORT_XLSX}`",
        f"- 校验项: {len(results)} 条。",
        f"- 需要确认问题: {len(questions)} 条。",
        f"- 真实差异: {len(real_diffs)} 条，详见 Excel `真实差异` 页。",
        "",
        "| 结果 | 数量 |",
        "|---|---:|",
    ]
    for status, count in counts.most_common():
        lines.append(f"| {status} | {count} |")
    lines += ["", "## 模块分布", "", "| 模块 | 结果 | 数量 |", "|---|---|---:|"]
    for (module, status), count in sorted(module_counts.items()):
        lines.append(f"| {module} | {status} | {count} |")
    if real_diffs:
        lines += ["", "## 真实差异", "", "| 模块 | 结果 | 校验项 | 正式值 | 设计值 | 说明 |", "|---|---|---|---|---|---|"]
        for r in real_diffs:
            lines.append(
                "| {module} | {result} | {check} | {formal} | {design} | {note} |".format(
                    module=str(r.get("模块/系统", "")).replace("|", "/"),
                    result=str(r.get("结果", "")).replace("|", "/"),
                    check=str(r.get("校验项", "")).replace("|", "/"),
                    formal=str(r.get("正式值", "")).replace("|", "/"),
                    design=str(r.get("设计值", "")).replace("|", "/"),
                    note=str(r.get("说明", "")).replace("|", "/"),
                )
            )
    if questions:
        lines += ["", "## 需要你确认", ""]
        for idx, q in enumerate(questions[:40], start=1):
            lines.append(f"{idx}. **{q['问题类型']} / {q['模块/系统']} / {q['来源']}**：{q['需要确认的问题']}  \n   样例：{q['样例']}")
        if len(questions) > 40:
            lines.append("")
            lines.append(f"> 还有 {len(questions) - 40} 条详见 Excel 报告 `需要确认` 页。")
    lines += [
        "",
        "## 校验边界",
        "",
        "- 优先按 ItemId / PropType / DropId 校验；中文资源名只做辅助。",
        "- UIlevel/Drop 的随机包权重、展示代表项与期望价值仍需专门做 Drop 展开校验。",
        "- 设计页未保留正式主键（LevelId/TaskId/DropId）的模块，本轮不做逐行强判错，只列为口径不确定。",
    ]
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    if not os.path.exists(SUMMARY):
        raise FileNotFoundError(SUMMARY)
    rows = load_ledger()
    items_by_id, items_by_name = load_items()
    drop_map, _drop_sources = load_drops()
    results = []
    questions = []

    validate_item_ids(rows, items_by_id, results, questions)
    validate_refs(rows, drop_map, results, questions)
    validate_signin(rows, results, questions)
    validate_battlepass(rows, drop_map, results, questions)
    validate_growth(rows, results, questions)
    validate_shop(rows, items_by_name, results, questions)
    validate_draw(rows, results, questions)
    validate_missing_formal_entries(rows, results, questions)

    # 去重问题，保留首个样例。
    dedup_questions = []
    seen_q = set()
    for q in questions:
        key = (q["问题类型"], q["模块/系统"], q["来源"], q["需要确认的问题"])
        if key in seen_q:
            continue
        seen_q.add(key)
        dedup_questions.append(q)
    questions = dedup_questions

    summary_rows = Counter((r["模块/系统"], r["结果"]) for r in results)
    write_xlsx(results, questions, summary_rows)
    write_md(results, questions)

    counts = Counter(r["结果"] for r in results)
    print("正式配置校验完成: %s" % " / ".join("%s=%s" % (k, v) for k, v in counts.most_common()))
    print("[报告Excel] %s" % REPORT_XLSX)
    print("[报告MD] %s" % REPORT_MD)
    if questions:
        print("需要确认: %d 条" % len(questions))


if __name__ == "__main__":
    main()
