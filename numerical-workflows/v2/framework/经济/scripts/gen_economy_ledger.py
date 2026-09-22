# -*- coding: utf-8 -*-
"""
gen_economy_ledger.py — P4b 经济层全资源产销总表

读取 Vgame经济框架.xlsx，生成 v2 的经济账本首版：
  - 产销明细：可直接观察的产出、消耗、商店兑换和奖励引用
  - 资源汇总：按资源/方向聚合数量口径与钻石价值
  - 道具定价锚点：来自 `01_源表/道具定价.xlsx`，仅脚本内部使用
  - 覆盖状态：经济母表所有页签的首版处理状态

只读源表。DropId / RewardId 首版登记为引用，后续交奖励同步链路展开。
"""
import io
import math
import os
import re
import sys
import warnings
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ECONOMY_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(ECONOMY_DIR)
NUM_DIR = os.path.dirname(V2_DIR)
sys.path.insert(0, V2_DIR)
from _shared.md_parameter_reader import load_parameter_workbook, parameter_md_path

SRC = os.path.join(NUM_DIR, "Vgame经济框架.xlsx")
PRICE_SRC = os.path.join(V2_DIR, "01_源表", "道具定价.xlsx")
OUT = os.path.join(ECONOMY_DIR, "全资源产销总表.xlsx")
ECONOMY_PARAM_FILE = parameter_md_path("经济")
MODULE_DIR = os.path.join(ECONOMY_DIR, "模块产销表")
REPORT = os.path.join(ECONOMY_DIR, "_reports", "P4b_经济总账_生成与覆盖.md")
CONFIG_ROOT = os.environ.get("VGAME_CONFIG_DATAS", "")

LEDGER_HEADERS = [
    "系统",
    "分组",
    "方向",
    "资源/道具",
    "道具ID",
    "数量",
    "价值(钻石)",
    "货币/成本",
    "货币数量",
    "货币价值(钻石)",
    "折扣/倍率",
    "周期/限制",
    "进度/条件",
    "来源页",
    "来源行",
    "口径",
    "备注",
]

COVER_HEADERS = ["页签", "行数", "列数", "处理状态", "说明"]
SUMMARY_HEADERS = ["资源/道具", "道具ID", "方向", "记录数", "数量合计(可加总)", "价值合计(钻石)", "主要系统"]
SPLIT_HEADERS = [
    "分组",
    "方向",
    "资源/道具",
    "数量",
    "价值(钻石)",
    "货币/成本",
    "货币数量",
    "周期/限制",
    "进度/条件",
    "来源页",
    "来源行",
    "口径",
    "备注",
]

ERROR_VALUES = {"#N/A", "#DIV/0!", "#REF!", "#VALUE!", "#NAME?", "#NUM!", "#NULL!"}
STAT_ONLY_RESOURCES = {"角色经验", "专武经验"}
DEPRECATED_ECONOMY_SYSTEMS = {"共鸣装备"}
NON_LEDGER_SYSTEMS = {"抽卡"}
FORMAL_ITEMS_BY_ID = None
MODULE_WRITE_WARNINGS = []
ECONOMY_PARAMS = None
LOGICAL_DROP_ENTRIES = None


def is_num(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def clean_text(value):
    if value is None:
        return ""
    if is_num(value):
        return value
    text = str(value).strip()
    if text in ERROR_VALUES:
        return "待定"
    return text


def clean_value(value):
    if value is None or value == "":
        return ""
    if is_num(value):
        return value
    text = str(value).strip()
    if text in ERROR_VALUES:
        return ""
    return text


def has_observed_value(value):
    return clean_text(value) not in ("", "待定")


def error_note(*values):
    return "源值含 Excel 错误，已按待定/空值处理" if any(str(v).strip() in ERROR_VALUES for v in values if v is not None) else ""


def qty_range(low, high):
    low = clean_value(low)
    high = clean_value(high)
    if low == "" and high == "":
        return ""
    if low == high or high == "":
        return low
    return "%s-%s" % (low, high)


def nearby_title(ws, header_row, col=2):
    for r in range(header_row - 1, 0, -1):
        value = clean_text(ws.cell(r, col).value)
        if value and value not in ("商品id", "暂不开启"):
            extra = clean_text(ws.cell(r, col + 1).value)
            return "%s%s" % (value, "（%s）" % extra if extra and extra != value else "")
    return ws.title


def cfg_path(*parts):
    return os.path.join(CONFIG_ROOT, *parts)


def to_int(value):
    value = clean_value(value)
    if value == "":
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
    value = clean_value(value)
    if value == "":
        return None
    if is_num(value):
        return int(value) if isinstance(value, float) and value.is_integer() else value
    text = str(value).strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", text):
        num = float(text)
        return int(num) if num.is_integer() else num
    return None


def load_economy_params():
    global ECONOMY_PARAMS
    if ECONOMY_PARAMS is not None:
        return ECONOMY_PARAMS
    ECONOMY_PARAMS = {}
    if not os.path.exists(ECONOMY_PARAM_FILE):
        return ECONOMY_PARAMS
    wb = load_parameter_workbook(ECONOMY_PARAM_FILE, data_only=True, read_only=True)
    for ws in wb.worksheets:
        for r in range(1, ws.max_row + 1):
            key = clean_text(ws.cell(r, 1).value)
            value = clean_value(ws.cell(r, 2).value)
            if key and key != "参数" and value != "":
                ECONOMY_PARAMS[str(key)] = value
    wb.close()
    return ECONOMY_PARAMS


def economy_param(name, default):
    value = load_economy_params().get(name, default)
    num = to_num(value)
    return default if num is None else num


def header_values(ws, row_idx, max_probe=256):
    values = []
    last_non_empty = 0
    for row in ws.iter_rows(min_row=row_idx, max_row=row_idx, max_col=max_probe, values_only=True):
        for col, value in enumerate(row, start=1):
            value = clean_text(value)
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
        if str(clean_text(ws.cell(3, 1).value)).startswith("##"):
            start = 5
        elif clean_text(ws.cell(3, 1).value) not in ("##group", "##"):
            start = 3
        blank_streak = 0
        for row_idx, values in enumerate(ws.iter_rows(min_row=start, max_col=max_col, values_only=True), start=start):
            values = [clean_text(v) for v in values]
            first = values[0] if values else ""
            if str(first).startswith("##"):
                continue
            if all(v == "" for v in values):
                blank_streak += 1
                if blank_streak >= 200:
                    break
                continue
            blank_streak = 0
            row = {"_row": row_idx}
            for idx, header in enumerate(data_headers, start=2):
                if header:
                    row[str(header)] = values[idx - 1] if idx - 1 < len(values) else ""
            rows.append(row)
        wb.close()
        return rows
    max_col = max(len(headers), 1)
    blank_streak = 0
    for row_idx, values in enumerate(ws.iter_rows(min_row=2, max_col=max_col, values_only=True), start=2):
        values = [clean_text(v) for v in values]
        if all(v == "" for v in values):
            blank_streak += 1
            if blank_streak >= 200:
                break
            continue
        blank_streak = 0
        row = {"_row": row_idx}
        for col, header in enumerate(headers, start=1):
            if header:
                row[str(header)] = values[col - 1] if col - 1 < len(values) else ""
        rows.append(row)
    wb.close()
    return rows


def formal_items_by_id():
    global FORMAL_ITEMS_BY_ID
    if FORMAL_ITEMS_BY_ID is not None:
        return FORMAL_ITEMS_BY_ID
    result = {}
    path = cfg_path("items", "Items.xlsx")
    if os.path.exists(path):
        for row in row_dicts(path, "items"):
            item_id = to_int(row.get("Id"))
            if item_id is not None:
                result[item_id] = row
    FORMAL_ITEMS_BY_ID = result
    return result


def formal_item_name(item_id):
    item_id = to_int(item_id)
    if item_id is None:
        return ""
    return clean_text(formal_items_by_id().get(item_id, {}).get("Name")) or "ItemId %s" % item_id


def prop_entries(value):
    value = clean_text(value)
    if not value:
        return []
    result = []
    for part in str(value).split(";"):
        part = part.strip()
        if not part:
            continue
        bits = [p.strip() for p in part.split(",")]
        if len(bits) < 2:
            continue
        item_id = to_int(bits[0])
        qty = to_num(bits[1])
        if item_id is None or qty is None:
            continue
        result.append((formal_item_name(item_id), item_id, qty))
    return result


def int_list(value):
    text = clean_text(value)
    if not text:
        return []
    result = []
    for part in re.split(r"[;；,，]", str(text)):
        value = to_int(part)
        if value is not None:
            result.append(value)
    return result


def drop_entries_by_id(path):
    result = defaultdict(list)
    if not os.path.exists(path):
        return result
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    headers = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    cols = {str(header): idx for idx, header in enumerate(headers) if header}
    blank_streak = 0
    max_idx = max(cols.values()) + 1 if cols else 1
    for row_idx, values in enumerate(ws.iter_rows(min_row=5, max_col=max_idx, values_only=True), start=5):
        values = [clean_text(value) for value in values]
        if all(value == "" for value in values):
            blank_streak += 1
            if blank_streak >= 200:
                break
            continue
        blank_streak = 0
        drop_id = to_int(values[cols["DropId"]]) if "DropId" in cols and cols["DropId"] < len(values) else None
        item_id = to_int(values[cols["DropItem_id"]]) if "DropItem_id" in cols and cols["DropItem_id"] < len(values) else None
        if drop_id is None or item_id is None:
            continue
        low = clean_value(values[cols["DropItemNumMin"]]) if "DropItemNumMin" in cols and cols["DropItemNumMin"] < len(values) else ""
        high = clean_value(values[cols["DropItemNumMax"]]) if "DropItemNumMax" in cols and cols["DropItemNumMax"] < len(values) else ""
        qty = qty_range(low, high)
        if qty == "":
            continue
        marker = clean_text(values[0] if values else "")
        result[drop_id].append({
            "item": formal_item_name(item_id),
            "item_id": item_id,
            "qty": qty,
            "row": row_idx,
            "invalid": str(marker).startswith("##"),
            "name": clean_text(values[cols["DropName"]]) if "DropName" in cols and cols["DropName"] < len(values) else "",
        })
    wb.close()
    return result


def logical_drop_entries_by_id():
    global LOGICAL_DROP_ENTRIES
    if LOGICAL_DROP_ENTRIES is not None:
        return LOGICAL_DROP_ENTRIES
    result = defaultdict(list)
    drop_dir = cfg_path("Drop")
    if os.path.isdir(drop_dir):
        for name in os.listdir(drop_dir):
            if not name.endswith(".xlsx") or name.startswith("~$"):
                continue
            path = os.path.join(drop_dir, name)
            for drop_id, entries in drop_entries_by_id(path).items():
                for entry in entries:
                    copied = dict(entry)
                    copied["source"] = "正式:Drop/%s" % name
                    result[drop_id].append(copied)
    LOGICAL_DROP_ENTRIES = result
    return result


def formal_prop_entries_by_key(path, key_field, value_field):
    result = defaultdict(list)
    seen = defaultdict(set)
    if not os.path.exists(path):
        return result
    for row in row_dicts(path):
        key = to_int(row.get(key_field))
        if key is None:
            continue
        for item, item_id, qty in prop_entries(row.get(value_field)):
            marker = (item_id, qty)
            if marker in seen[key]:
                continue
            seen[key].add(marker)
            result[key].append((item, item_id, qty))
    return result


def formal_num_map(path, key_field, value_field, sheet_name=None, row_filter=None):
    result = {}
    if not os.path.exists(path):
        return result
    for row in row_dicts(path, sheet_name):
        if row_filter and not row_filter(row):
            continue
        key = to_int(row.get(key_field))
        if key is None:
            continue
        result[key] = to_num(row.get(value_field))
    return result


QUALITY_NAMES = {4: "SSR", 3: "SR", 2: "R"}


def scaled_qty(value, factor):
    num = to_num(value)
    if num is None:
        return clean_value(value)
    result = round(num * factor, 6)
    return int(result) if isinstance(result, float) and result.is_integer() else result


def quality_name(quality):
    quality = to_int(quality)
    return QUALITY_NAMES.get(quality, "Quality%s" % clean_value(quality))


def formal_num_map_by_quality(path, key_field, value_field, sheet_name=None):
    result = defaultdict(dict)
    if not os.path.exists(path):
        return result
    for row in row_dicts(path, sheet_name):
        quality = to_int(row.get("Quality"))
        key = to_int(row.get(key_field))
        if quality is None or key is None:
            continue
        result[quality][key] = to_num(row.get(value_field))
    return result


def score_condition(min_score, max_score=""):
    min_score = clean_value(min_score)
    max_score = clean_value(max_score)
    if min_score == "" and max_score == "":
        return ""
    if max_score in ("", 99999, "99999"):
        return "积分≥%s" % min_score
    return "积分%s-%s" % (min_score, max_score)


def arena_source_rank_condition(ws, row):
    rank_name = clean_text(ws.cell(row, 2).value)
    cond = score_condition(ws.cell(row, 3).value)
    if not rank_name:
        return ""
    return "达到%s%s" % (rank_name, "｜%s" % cond if cond else "")


def arena_formal_rank_condition(row):
    rank_name = clean_text(row.get("RankName"))
    cond = score_condition(row.get("MinScore"), row.get("MaxScore"))
    return "达到%s%s" % (rank_name, "｜%s" % cond if cond else "")


def mark_external(b, source, status, note, rows="", cols=""):
    b.coverage[source] = [source, rows, cols, status, note]


class EconomyLedger:
    def __init__(self, wb, price_wb):
        self.wb = wb
        self.price_wb = price_wb
        self.ledger = []
        self.price_rows = []
        self.price_by_name = {}
        self.price_by_id = {}
        self.coverage = {}
        self.stat_excluded_counts = Counter()
        self.stat_only_rows = []
        self.deprecated_excluded_counts = Counter()
        self.non_ledger_excluded_counts = Counter()
        self._build_price_index()

    def mark(self, sheet, status, note):
        if sheet in self.wb.sheetnames:
            ws = self.wb[sheet]
            self.coverage[sheet] = [sheet, ws.max_row, ws.max_column, status, note]

    def _build_price_index(self):
        ws = self.price_wb["资源定价"]
        category = ""
        for r in range(3, ws.max_row + 1):
            row_category = clean_text(ws.cell(r, 1).value) or clean_text(ws.cell(r, 2).value)
            if row_category:
                category = row_category
            item = clean_text(ws.cell(r, 3).value)
            if not item or item == "道具":
                continue
            item_id = clean_value(ws.cell(r, 4).value)
            rmb = clean_value(ws.cell(r, 5).value)
            diamond = clean_value(ws.cell(r, 6).value)
            note = clean_text(ws.cell(r, 8).value)
            row = [category, item, item_id, rmb, diamond, note, r]
            self.price_rows.append(row)
            self.price_by_name[str(item)] = {"id": item_id, "rmb": rmb, "diamond": diamond, "category": category}
            if item_id != "":
                self.price_by_id[str(item_id)] = {"name": item, "rmb": rmb, "diamond": diamond, "category": category}
        self.coverage["01_源表/道具定价.xlsx"] = [
            "01_源表/道具定价.xlsx", ws.max_row, ws.max_column,
            "source_owned", "内部定价锚点；不导出独立索引页。",
        ]

    def item_id_of(self, item, explicit=""):
        item = str(clean_text(item))
        explicit = clean_value(explicit)
        if item == "B炮台" and str(explicit) in ("", "96003"):
            return 96303
        if explicit != "":
            return explicit
        if item in self.price_by_name:
            return self.price_by_name[item]["id"]
        aliases = {
            "角色抽卡券": "角色抽卡券普通",
            "专武抽卡券": "专武抽卡券普通",
            "万能星盘点": "额外星盘点",
            "映射装备经验": "主角装备经验",
            "邮票经验": "旅券经验",
            "武将经验": "角色经验",
        }
        if item in aliases and aliases[item] in self.price_by_name:
            return self.price_by_name[aliases[item]]["id"]
        for formal_id, formal_row in formal_items_by_id().items():
            if clean_text(formal_row.get("Name")) == item:
                return formal_id
        return ""

    def unit_value(self, item):
        item = str(clean_text(item))
        if not item or item == "待定":
            return None
        if item in self.price_by_name and is_num(self.price_by_name[item]["diamond"]):
            return self.price_by_name[item]["diamond"]
        aliases = {
            "角色抽卡券": "角色抽卡券普通",
            "专武抽卡券": "专武抽卡券普通",
            "万能星盘点": "额外星盘点",
            "映射装备经验": "主角装备经验",
            "邮票经验": "旅券经验",
            "武将经验": "角色经验",
        }
        if item in aliases and aliases[item] in self.price_by_name and is_num(self.price_by_name[aliases[item]]["diamond"]):
            return self.price_by_name[aliases[item]]["diamond"]
        for base in ("角色经验", "专武经验", "旅券经验", "主角装备经验", "金币", "钻石"):
            if item.startswith(base) and base in self.price_by_name and is_num(self.price_by_name[base]["diamond"]):
                match = re.search(r"(\d+)", item)
                if match:
                    return self.price_by_name[base]["diamond"] * int(match.group(1))
                return self.price_by_name[base]["diamond"]
        if "抽卡券" in item:
            return 150
        return None

    def total_value(self, item, qty, source_value=""):
        source_value = clean_value(source_value)
        if is_num(source_value):
            return source_value
        if is_num(qty):
            unit = self.unit_value(item)
            if unit is not None:
                return round(unit * qty, 6)
        return ""

    def item_from_id(self, item_id):
        key = str(clean_value(item_id))
        if key in self.price_by_id:
            return self.price_by_id[key]["name"]
        return "ItemId %s" % key if key else ""

    def parse_prop(self, value):
        if value is None or value == "":
            return "", "", ""
        text = str(value).strip()
        match = re.match(r"^(\d+)\s*[,;]\s*([\d.]+)$", text)
        if not match:
            return "", "", ""
        item_id = match.group(1)
        qty = float(match.group(2))
        if qty.is_integer():
            qty = int(qty)
        return self.item_from_id(item_id), item_id, qty

    def add(self, system, group, direction, item, qty="", value="", item_id="", cost_item="", cost_qty="",
            cost_value="", ratio="", period="", condition="", sheet="", row="", basis="", note=""):
        item = clean_text(item)
        if not item:
            return
        item_id = self.item_id_of(item, item_id)
        qty = clean_value(qty)
        value = self.total_value(item, qty, value)
        cost_item = clean_text(cost_item)
        cost_qty = clean_value(cost_qty)
        cost_value = clean_value(cost_value)
        if cost_item and cost_value == "" and is_num(cost_qty):
            cost_value = self.total_value(cost_item, cost_qty, "")
        ratio = clean_value(ratio)
        period = clean_text(period)
        condition = clean_text(condition)
        note = clean_text(note)
        err = error_note(item, qty, value, item_id, cost_item, cost_qty, cost_value)
        if err:
            note = "%s；%s" % (note, err) if note else err
        self.ledger.append({
            "系统": clean_text(system),
            "分组": clean_text(group),
            "方向": clean_text(direction),
            "资源/道具": item,
            "道具ID": item_id,
            "数量": qty,
            "价值(钻石)": clean_value(value),
            "货币/成本": cost_item,
            "货币数量": cost_qty,
            "货币价值(钻石)": cost_value,
            "折扣/倍率": ratio,
            "周期/限制": period,
            "进度/条件": condition,
            "来源页": sheet,
            "来源行": row,
            "口径": clean_text(basis),
            "备注": note,
        })

    def add_reward(self, system, group, item, qty, sheet, row, value="", item_id="", period="", condition="", basis="直接奖励", note=""):
        self.add(system, group, "产出", item, qty, value, item_id, "", "", "", "", period, condition, sheet, row, basis, note)

    def add_cost(self, system, group, item, qty, sheet, row, value="", period="", condition="", basis="消耗", note="", item_id=""):
        self.add(system, group, "消耗", item, qty, value, item_id, "", "", "", "", period, condition, sheet, row, basis, note)

    def add_ref(self, system, group, item, qty, sheet, row, item_id="", condition="", note=""):
        self.add(system, group, "引用", item, qty, "", item_id, "", "", "", "", "", condition, sheet, row, "奖励包/配置引用，待 DropId/RewardId 展开", note)

    def add_shop(self, system, group, item, qty, currency, currency_qty, sheet, row, item_value="", currency_value="",
                 ratio="", period="", condition="", item_id="", note=""):
        self.add(system, group, "产出", item, qty, item_value, item_id, currency, currency_qty, currency_value,
                 ratio, period, condition, sheet, row, "商店兑换商品", note)
        if currency:
            self.add(system, group, "消耗", currency, currency_qty, currency_value, "", "", "", "", ratio,
                     period, condition, sheet, row, "商店兑换货币", "兑换 %sx%s" % (item, qty))


def parse_shop_blocks(b, sheet, system):
    ws = b.wb[sheet]
    for r in range(1, ws.max_row + 1):
        if clean_text(ws.cell(r, 2).value) != "商品id":
            continue
        block = nearby_title(ws, r)
        rr = r + 1
        while rr <= ws.max_row:
            goods_id = ws.cell(rr, 2).value
            item = ws.cell(rr, 3).value
            if clean_text(item) == "" and clean_text(goods_id) == "":
                break
            if clean_text(ws.cell(rr, 2).value) == "商品id":
                break
            if item:
                limit = clean_text(ws.cell(rr, 10).value)
                limit_num = clean_value(ws.cell(rr, 11).value)
                if limit_num != "":
                    limit = "%s%s" % (limit, limit_num)
                b.add_shop(
                    system, block, item, ws.cell(rr, 4).value, ws.cell(rr, 6).value, ws.cell(rr, 7).value,
                    sheet, rr, ws.cell(rr, 5).value, ws.cell(rr, 8).value, ws.cell(rr, 9).value,
                    limit, "商品ID %s" % clean_value(goods_id), note=clean_text(ws.cell(rr, 12).value)
                )
            rr += 1
    if sheet == "商店":
        for r in range(5, 13):
            if ws.cell(r, 14).value:
                b.add_shop("商店", "体力购买", "体力", ws.cell(r, 15).value, "钻石", ws.cell(r, 16).value,
                           sheet, r, "", ws.cell(r, 16).value, ws.cell(r, 17).value,
                           "购买次数%s" % clean_value(ws.cell(r, 14).value), "每日购买体力")
    b.mark(sheet, "已结构化", "商店商品产出与货币消耗已拆成产出/消耗双行。")


def parse_signin(b):
    ws = b.wb["签到"]

    daily_rewards = formal_prop_entries_by_key(
        cfg_path("SignInReward", "DailySign.xlsx"), "day", "rewardItems"
    )
    monthly_rewards = formal_prop_entries_by_key(
        cfg_path("SignInReward", "MonthlyAccumulate.xlsx"), "AccumulateDay", "rewardItems"
    )
    travel_rewards = formal_prop_entries_by_key(
        cfg_path("SignInReward", "TravelAccumulate.xlsx"), "AccumulateDay", "rewardItems"
    )

    def add_signin_entries(entries, group, row, period, condition, note):
        for item, item_id, qty in entries:
            b.add_reward("签到", group, item, qty, "签到", row, item_id=item_id,
                         period=period, condition=condition, basis="正式配置直接奖励", note=note)

    for r in range(3, ws.max_row + 1):
        day = to_int(ws.cell(r, 2).value)
        if day is not None and ws.cell(r, 3).value:
            entries = daily_rewards.get(day)
            if entries:
                add_signin_entries(entries, "每日签到", r, "每日/月签", "第%s天" % day,
                                   "按正式 DailySign.rewardItems 覆盖旧设计值。")
            else:
                b.add_reward("签到", "每日签到", ws.cell(r, 3).value, ws.cell(r, 4).value, "签到", r,
                             ws.cell(r, 5).value, ws.cell(r, 6).value, "每日/月签", "第%s天" % day)

        acc_day = to_int(ws.cell(r, 10).value)
        if acc_day is not None:
            cond = "累计签到%s天" % acc_day
            entries = monthly_rewards.get(acc_day) if r <= 5 else travel_rewards.get(acc_day)
            source = "MonthlyAccumulate" if r <= 5 else "TravelAccumulate"
            if entries:
                add_signin_entries(entries, "累计签到", r, "累计", cond,
                                   "按正式 SignInReward/%s.rewardItems 覆盖旧设计值。" % source)
            else:
                b.add_reward("签到", "累计签到", ws.cell(r, 11).value, ws.cell(r, 12).value, "签到", r,
                             ws.cell(r, 13).value, period="累计", condition=cond)
                b.add_reward("签到", "累计签到", ws.cell(r, 14).value, ws.cell(r, 15).value, "签到", r,
                             ws.cell(r, 16).value, period="累计", condition=cond)
    b.mark("签到", "已结构化", "每日签到、累计签到、生涯累计签到奖励已登记；已按正式 DailySign/MonthlyAccumulate/TravelAccumulate 覆盖旧设计差异。")


def parse_seven_day_tasks(b):
    ws = b.wb["7日任务"]
    for r in range(14, ws.max_row + 1):
        day = clean_text(ws.cell(r, 1).value)
        task = clean_text(ws.cell(r, 4).value)
        if not day or not task:
            continue
        condition = "%s｜%s" % (day, task)
        b.add_reward("7日任务", "任务点数", ws.cell(r, 7).value, ws.cell(r, 8).value, "7日任务", r,
                     period="新手7日", condition=condition, basis="任务点数")
        b.add_reward("7日任务", "任务奖励", ws.cell(r, 9).value, ws.cell(r, 10).value, "7日任务", r,
                     period="新手7日", condition=condition, note=clean_text(ws.cell(r, 14).value))
        b.add_reward("7日任务", "任务奖励", ws.cell(r, 11).value, ws.cell(r, 12).value, "7日任务", r,
                     period="新手7日", condition=condition, note=clean_text(ws.cell(r, 14).value))
    b.mark("7日任务", "已结构化", "70条任务的点数与直接奖励已登记。")


def parse_task_sheet(b):
    ws = b.wb["任务"]
    for r in range(5, 10):
        cond = "每日活跃%s分箱" % clean_value(ws.cell(r, 3).value)
        for item_col, qty_col in [(4, 5), (6, 7), (8, 9)]:
            b.add_reward("任务", "每日任务箱", ws.cell(r, item_col).value, ws.cell(r, qty_col).value, "任务", r,
                         period="每日", condition=cond)
    for r in range(5, 14):
        task = ws.cell(r, 13).value
        if task:
            cond = "%s %s" % (clean_text(task), clean_value(ws.cell(r, 14).value))
            b.add_reward("任务", "每日任务完成", ws.cell(r, 15).value, ws.cell(r, 16).value, "任务", r,
                         period="每日", condition=cond)
            b.add_reward("任务", "每日任务完成", ws.cell(r, 17).value, ws.cell(r, 18).value, "任务", r,
                         period="每日", condition=cond)
    for r in range(17, 23):
        cond = "每周活跃%s分箱" % clean_value(ws.cell(r, 3).value)
        for item_col, qty_col in [(4, 5), (6, 7)]:
            b.add_reward("任务", "每周任务箱", ws.cell(r, item_col).value, ws.cell(r, qty_col).value, "任务", r,
                         period="每周", condition=cond)
    for r in range(17, 41):
        task = ws.cell(r, 13).value
        if task:
            cond = "%s %s" % (clean_text(task), clean_value(ws.cell(r, 14).value))
            b.add_reward("任务", "每周任务完成", ws.cell(r, 15).value, ws.cell(r, 16).value, "任务", r,
                         period="每周", condition=cond)
            b.add_reward("任务", "每周任务完成", ws.cell(r, 17).value, ws.cell(r, 18).value, "任务", r,
                         period="每周", condition=cond)
    stage = ""
    for r in range(42, ws.max_row + 1):
        if ws.cell(r, 2).value:
            stage = "阶段%s" % clean_value(ws.cell(r, 2).value)
        if ws.cell(r, 3).value:
            b.add_reward("任务", "阶段里程碑奖励", ws.cell(r, 3).value, ws.cell(r, 4).value, "任务", r,
                         period="一次性", condition=stage)
        if ws.cell(r, 5).value:
            b.add_reward("任务", "阶段任务奖励", ws.cell(r, 6).value, ws.cell(r, 7).value, "任务", r,
                         ws.cell(r, 8).value, period="一次性", condition="%s｜%s" % (stage, clean_text(ws.cell(r, 5).value)))
    b.mark("任务", "已结构化", "每日/每周任务、活跃箱、阶段任务和阶段里程碑奖励已登记。")


def parse_battlepass(b):
    ws = b.wb["通行证"]
    for r in range(17, ws.max_row + 1):
        lv = ws.cell(r, 2).value
        if is_num(lv):
            cond = "等级%s" % int(lv)
            b.add_reward("通行证", "免费线", ws.cell(r, 3).value, ws.cell(r, 4).value, "通行证", r,
                         ws.cell(r, 5).value, period="通行证周期", condition=cond)
            b.add_reward("通行证", "付费线", ws.cell(r, 6).value, ws.cell(r, 7).value, "通行证", r,
                         ws.cell(r, 8).value, period="通行证周期", condition=cond)
            b.add_reward("通行证", "付费线额外", ws.cell(r, 9).value, ws.cell(r, 10).value, "通行证", r,
                         ws.cell(r, 11).value, period="通行证周期", condition=cond)
        if ws.cell(r, 17).value:
            b.add_reward("通行证", "付费一次性奖励", ws.cell(r, 17).value, ws.cell(r, 18).value, "通行证", r,
                         period="付费一次性", condition="高级通行证")
    b.mark("通行证", "已结构化", "免费/付费等级奖励与付费一次性奖励已登记。")


def parse_battlepass_config(b):
    ws = b.wb["配置页-通行证"]
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 7).value:
            b.add_ref("通行证", "配置页免费奖励", ws.cell(r, 8).value, ws.cell(r, 10).value, "配置页-通行证", r,
                      ws.cell(r, 9).value, note="RewardId %s" % clean_value(ws.cell(r, 7).value))
        if ws.cell(r, 11).value:
            b.add_ref("通行证", "配置页付费奖励", ws.cell(r, 12).value, ws.cell(r, 14).value, "配置页-通行证", r,
                      ws.cell(r, 13).value, note="RewardId %s" % clean_value(ws.cell(r, 11).value))
    b.mark("配置页-通行证", "已登记引用", "BattlePassReward 的 RewardId 与直接道具预览已登记，真实 Drop 内容待展开。")


def parse_mainline(b):
    ws = b.wb["主线副本"]
    for r in range(6, ws.max_row + 1):
        if not is_num(ws.cell(r, 1).value) or not is_num(ws.cell(r, 2).value):
            continue
        cond = "章节%s-%s" % (clean_value(ws.cell(r, 1).value), clean_value(ws.cell(r, 2).value))
        b.add_cost("主线", "普通主线", "体力", ws.cell(r, 3).value, "主线副本", r, condition=cond)
        for item_col, qty_col in [(4, 5), (6, 7), (8, 9), (12, 13), (14, 15)]:
            b.add_reward("主线", "普通主线首通", ws.cell(r, item_col).value, ws.cell(r, qty_col).value, "主线副本", r,
                         period="一次性", condition=cond)
        b.add_reward("主线", "普通主线重复", ws.cell(r, 16).value, ws.cell(r, 17).value, "主线副本", r,
                     period="可重复", condition=cond)
        b.add_reward("主线", "普通主线重复", ws.cell(r, 20).value, qty_range(ws.cell(r, 21).value, ws.cell(r, 22).value),
                     "主线副本", r, ws.cell(r, 24).value, period="可重复", condition=cond,
                     note="概率 %s" % clean_value(ws.cell(r, 23).value))
        if ws.cell(r, 27).value is not None and str(ws.cell(r, 27).value).strip() != "":
            star_cond = "章节%s 星级%s" % (clean_value(ws.cell(r, 27).value), clean_value(ws.cell(r, 28).value))
            for item_col, qty_col in [(29, 30), (31, 32), (33, 34)]:
                b.add_reward("主线", "主线星级奖励", ws.cell(r, item_col).value, ws.cell(r, qty_col).value, "主线副本", r,
                             period="一次性", condition=star_cond)
    b.mark("主线副本", "已结构化", "体力消耗、首通、重复掉落、章节星级奖励已登记。")


def parse_hard_mainline(b):
    ws = b.wb["高难主线关卡"]
    for r in range(8, ws.max_row + 1):
        if not is_num(ws.cell(r, 3).value):
            continue
        cond = "高难关卡%s" % clean_value(ws.cell(r, 3).value)
        gem = "%s%s" % (clean_text(ws.cell(r, 5).value), "（%s）" % clean_text(ws.cell(r, 7).value) if ws.cell(r, 7).value else "")
        b.add_cost("困难主线", "高难主线", "体力", ws.cell(r, 8).value, "高难主线关卡", r, condition=cond)
        b.add_reward("困难主线", "高难主线重复", "玩家经验", ws.cell(r, 9).value, "高难主线关卡", r,
                     period="可重复", condition=cond)
        b.add_reward("困难主线", "高难主线重复", gem, ws.cell(r, 10).value, "高难主线关卡", r,
                     ws.cell(r, 24).value, period="可重复", condition=cond, note="权重串 %s" % clean_text(ws.cell(r, 15).value))
        b.add_reward("困难主线", "高难主线首通", "钻石", ws.cell(r, 29).value, "高难主线关卡", r,
                     period="一次性", condition=cond)
        b.add_reward("困难主线", "高难主线首通", "%s Lv%s" % (clean_text(ws.cell(r, 5).value), clean_value(ws.cell(r, 20).value)),
                     ws.cell(r, 21).value, "高难主线关卡", r, ws.cell(r, 28).value, period="一次性", condition=cond)
    b.mark("高难主线关卡", "已结构化", "体力、玩家经验、宝石重复掉落、首通钻石/宝石奖励已登记。")


def parse_resource_dungeons(b):
    ws = b.wb["资源、装备副本"]
    for r in range(6, 15):
        cond = "金币副本难度%s" % clean_value(ws.cell(r, 2).value)
        b.add_cost("资源副本", "金币副本", "体力", ws.cell(r, 3).value, "资源、装备副本", r, condition=cond)
        b.add_reward("资源副本", "金币副本重复", "玩家经验", ws.cell(r, 5).value, "资源、装备副本", r, period="可重复", condition=cond)
        b.add_reward("资源副本", "金币副本重复", "金币", ws.cell(r, 6).value, "资源、装备副本", r, period="可重复", condition=cond)
        b.add_reward("资源副本", "金币副本首通", "金币", ws.cell(r, 7).value, "资源、装备副本", r, period="一次性", condition=cond)
    for label, rows, exp_item in [("武将经验副本", range(20, 29), "角色经验"), ("专武经验副本", range(35, 44), "专武经验")]:
        for r in rows:
            cond = "%s难度%s" % (label, clean_value(ws.cell(r, 2).value))
            b.add_cost("资源副本", label, "体力", ws.cell(r, 3).value, "资源、装备副本", r, condition=cond)
            b.add_reward("资源副本", "%s重复" % label, "玩家经验", ws.cell(r, 5).value, "资源、装备副本", r, period="可重复", condition=cond)
            b.add_reward("资源副本", "%s重复" % label, exp_item, ws.cell(r, 6).value, "资源、装备副本", r, period="可重复", condition=cond)
            b.add_reward("资源副本", "%s首通" % label, exp_item, ws.cell(r, 7).value, "资源、装备副本", r, period="一次性", condition=cond)
            b.add_reward("资源副本", "%s重复金币" % label, "金币", ws.cell(r, 8).value, "资源、装备副本", r, period="可重复", condition=cond)
            for item_col, low_col, high_col in [(9, 10, 11), (12, 13, 14), (15, 16, 17)]:
                b.add_reward("资源副本", "%s随机包" % label, ws.cell(r, item_col).value,
                             qty_range(ws.cell(r, low_col).value, ws.cell(r, high_col).value),
                             "资源、装备副本", r, period="可重复", condition=cond)
            b.add_reward("资源副本", "%s首通道具" % label, ws.cell(r, 19).value, ws.cell(r, 20).value,
                         "资源、装备副本", r, ws.cell(r, 21).value, period="一次性", condition=cond)
    b.mark("资源、装备副本", "已结构化", "金币/角色经验/专武经验副本的体力、首通、重复与随机包已登记。")


def collect_voucher_stamp_pools(ws):
    pools = []
    for r in range(1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            label = clean_text(ws.cell(r, c).value)
            if not isinstance(label, str) or not re.match(r"^邮票本\d+$", label):
                continue
            stamps = []
            for cc in range(c + 1, ws.max_column + 1):
                stamp = clean_text(ws.cell(r, cc).value)
                if isinstance(stamp, str) and stamp and not stamp.startswith("="):
                    stamps.append(stamp)
            if stamps:
                pools.append((label, r, stamps))
            break
    return pools


def parse_voucher_dungeon(b):
    ws = b.wb["旅券副本"]
    for r in range(6, 16):
        cond = "旅券副本难度%s" % clean_value(ws.cell(r, 3).value)
        b.add_cost("旅券副本", "旅券副本", "体力", ws.cell(r, 4).value, "旅券副本", r, condition=cond)
        b.add_reward("旅券副本", "旅券副本重复", "玩家经验", ws.cell(r, 6).value, "旅券副本", r, period="可重复", condition=cond)
        b.add_reward("旅券副本", "旅券副本重复", "金币", ws.cell(r, 7).value, "旅券副本", r, period="可重复", condition=cond)
        b.add_reward("旅券副本", "旅券随机掉落", "旅券随机件数", ws.cell(r, 8).value, "旅券副本", r,
                     ws.cell(r, 21).value, period="可重复", condition=cond)
        for name, qty_col, value_col in [("蓝色旅券期望", 13, 17), ("紫色旅券期望", 14, 18), ("金色旅券期望", 15, 19), ("红色旅券期望", 16, 20)]:
            b.add_reward("旅券副本", "旅券随机掉落", name, ws.cell(r, qty_col).value, "旅券副本", r,
                         ws.cell(r, value_col).value, period="可重复", condition=cond)
        for col in (22, 23, 24):
            b.add_reward("旅券副本", "旅券副本首通", ws.cell(r, col).value, 1, "旅券副本", r, period="一次性", condition=cond)
        b.add_reward("旅券副本", "旅券副本首通", ws.cell(r, 25).value, ws.cell(r, 26).value, "旅券副本", r,
                     period="一次性", condition=cond)
    pool_count = 0
    for label, row, stamps in collect_voucher_stamp_pools(ws):
        for idx, stamp in enumerate(stamps, start=1):
            before = len(b.ledger)
            b.add(
                "旅券副本",
                "邮票本具体掉落池",
                "引用",
                stamp,
                sheet="旅券副本",
                row=row,
                period="可重复候选池",
                condition=label,
                basis="手填邮票本具体掉落池",
                note="源表列出该本可掉落具体邮票；未给单件概率/权重，不计入固定产出。",
            )
            if len(b.ledger) > before:
                b.ledger[-1]["_源内顺序"] = idx
                pool_count += 1
    note = "体力、玩家经验、金币、旅券期望掉落与首通旅券/经验已登记。"
    if pool_count:
        note += " 邮票本具体掉落池已登记 %s 项，作为候选池引用不计固定产量。" % pool_count
    b.mark("旅券副本", "已结构化", note)


def parse_mapping_dungeon(b):
    ws = b.wb["映射装备副本"]
    for r in range(5, ws.max_row + 1):
        if not is_num(ws.cell(r, 2).value):
            continue
        cond = "映射装备副本层%s" % clean_value(ws.cell(r, 2).value)
        b.add_cost("映射装备副本", "映射装备副本", "体力", ws.cell(r, 3).value, "映射装备副本", r, condition=cond)
        b.add_reward("映射装备副本", "重复奖励", "玩家经验", ws.cell(r, 4).value, "映射装备副本", r, period="可重复", condition=cond)
        b.add_reward("映射装备副本", "装备随机掉落", "映射装备随机件数", ws.cell(r, 5).value, "映射装备副本", r,
                     ws.cell(r, 29).value, period="可重复", condition=cond)
        for name, qty_col, value_col in [("蓝色映射装备期望", 12, 16), ("紫色映射装备期望", 13, 17), ("金色映射装备期望", 14, 18), ("红色映射装备期望", 15, 19)]:
            b.add_reward("映射装备副本", "装备随机掉落", name, ws.cell(r, qty_col).value, "映射装备副本", r,
                         ws.cell(r, value_col).value, period="可重复", condition=cond)
        b.add_reward("映射装备副本", "重复奖励", "主角装备经验", ws.cell(r, 27).value, "映射装备副本", r,
                     ws.cell(r, 28).value, period="可重复", condition=cond)
    b.mark("映射装备副本", "已结构化", "体力、经验、映射装备期望、主角装备经验已登记。")


def add_formal_shopgoods(b, system, group, shop_id, source_label):
    path = cfg_path("Shop", "ShopGoods.xlsx")
    if not os.path.exists(path):
        return 0
    count = 0
    for row in row_dicts(path, "Goods"):
        if to_int(row.get("ShopId")) != shop_id:
            continue
        if clean_text(row.get("IsValid")).lower() == "false":
            continue
        item_id = to_int(row.get("ItemId"))
        price = prop_entries(row.get("Price"))
        if not item_id or not price:
            continue
        cost_item, _cost_id, cost_qty = price[0]
        item = formal_item_name(item_id)
        b.add_shop(system, group, item, to_num(row.get("Num")), cost_item, cost_qty,
                   source_label, row.get("_row"), item_id=item_id,
                   period="%s%s" % (clean_text(row.get("LimitType")), clean_value(row.get("LimitNum"))),
                   condition="ShopGoods %s｜ShopId %s" % (clean_value(row.get("Id")), shop_id),
                   note="正式 ShopGoods.Price=%s" % clean_text(row.get("Price")))
        count += 1
    if count:
        mark_external(b, source_label, "已补强", "%s 正式商店商品已登记。" % group, count, "")
    return count


TOWER_MIRROR_DIR = os.path.join(V2_DIR, "06_最终配置", "爬塔")
# 2026-09-20 扩展 101-200 层后全塔验收：1-100 层 CHG-044 口径不变，101-200 层按第 100 层面额平推
# （首通新增 元晶10,000/熔晶10/旅券60/零件8,600/箱900/1156×200/1157×15；见 design/爬塔扩展101-200层Design Doc.md）。
TOWER_FIRST_CLEAR_TOTALS = {2: 17300, 103: 17, 106: 120, 1074: 12600, 3027: 1550, 1156: 350, 1157: 25}
TOWER_FIRST_CLEAR_ROWS = 446
TOWER_IDLE_POOL_DROP_ID = 24003001
TOWER_ITEM_FALLBACK_NAMES = {
    1: "猎鹰金币",
    2: "元晶",
    103: "熔晶",
    106: "旅券",
    1074: "房车零件",
    1075: "行程便签",
    1076: "安途清单",
    1077: "探路标记",
    1078: "见闻手札",
    1079: "调律灯片",
    1156: "高阶课程笔记",
    1157: "精英课程笔记",
    3027: "指南材料自选箱",
}


def parse_tower_mirror(b):
    """爬塔经济改读 06 评审镜像（CHG-044 口径），替代旧经济母表「配置页-爬塔」。

    来源：TowerFirstReward(100层首通DropId) + Drop_dungeon(包内容/挂机池)
    + TowerIdleRewards(逐层挂机)。旧每周到达/通关/扫荡、爬塔商店与赛季
    奖励已随改版删除；镜像中 ## 停用行不计入产出。
    """

    first_path = os.path.join(TOWER_MIRROR_DIR, "TowerFirstReward.xlsx")
    drop_path = os.path.join(TOWER_MIRROR_DIR, "Drop_dungeon.xlsx")
    idle_path = os.path.join(TOWER_MIRROR_DIR, "TowerIdleRewards.xlsx")
    source_mirror = "评审镜像:06_最终配置/爬塔"
    missing = [p for p in (first_path, drop_path, idle_path) if not os.path.exists(p)]
    if missing:
        mark_external(b, source_mirror, "待生成", "爬塔评审镜像缺失：%s" % "、".join(missing))
        return

    def mirror_item_name(item_id, resolved):
        if resolved and not str(resolved).startswith("ItemId "):
            return resolved
        return TOWER_ITEM_FALLBACK_NAMES.get(item_id, resolved)

    drop_entries = drop_entries_by_id(drop_path)
    first_rows = [r for r in row_dicts(first_path, "Sheet1") if r.get("ID") not in (None, "")]
    if len(first_rows) != 100:
        raise RuntimeError("爬塔首通镜像应为 200 层，实际 %s" % len(first_rows))
    first_totals = defaultdict(float)
    expanded = 0
    disabled = 0
    for row in first_rows:
        layer = to_int(row.get("Layer"))
        drop_id = to_int(row.get("DropId"))
        if layer is None or drop_id is None:
            continue
        cond = "第%s层｜账号级首通｜DropId %s" % (layer, drop_id)
        entries = drop_entries.get(drop_id, [])
        if not entries:
            b.add_ref("爬塔", "首通奖励引用", "TowerFirstReward.DropId", drop_id,
                      "%s/TowerFirstReward.xlsx" % source_mirror, row.get("_row"),
                      condition=cond, note="首通 DropId 未在镜像 Drop_dungeon 展开")
            continue
        for entry in entries:
            if entry["invalid"]:
                disabled += 1
                continue
            qty = entry["qty"]
            try:
                first_totals[int(entry["item_id"])] += float(str(qty).rstrip("+")) if isinstance(qty, str) else float(qty)
            except (TypeError, ValueError):
                pass
            b.add_reward(
                "爬塔",
                "首通奖励",
                mirror_item_name(entry["item_id"], entry["item"]),
                qty,
                "%s/TowerFirstReward.xlsx + Drop_dungeon.xlsx" % source_mirror,
                row.get("_row"),
                item_id=entry["item_id"],
                period="常驻一次性（账号级）",
                condition=cond,
                basis="评审镜像首通展开（CHG-044口径）",
                note="Drop_dungeon 行%s" % entry["row"],
            )
            expanded += 1
    if expanded != TOWER_FIRST_CLEAR_ROWS:
        raise RuntimeError("爬塔首通有效行应为 %s，实际 %s" % (TOWER_FIRST_CLEAR_ROWS, expanded))
    expected_totals = {str(k): float(v) for k, v in TOWER_FIRST_CLEAR_TOTALS.items()}
    actual_totals = {str(k) for k in first_totals}
    if actual_totals != set(expected_totals) or any(abs(first_totals[int(k)] - v) > 1e-6 for k, v in expected_totals.items()):
        raise RuntimeError(
            "爬塔首通总量与 CHG-044 验收不一致: %s" % {k: first_totals[int(k)] for k in sorted(expected_totals, key=int)}
        )

    pool_entries = [e for e in drop_entries.get(TOWER_IDLE_POOL_DROP_ID, []) if not e["invalid"]]
    if len(pool_entries) != 5:
        raise RuntimeError("挂机材料池 %s 应为 5 个等权项，实际 %s" % (TOWER_IDLE_POOL_DROP_ID, len(pool_entries)))
    idle_rows = [r for r in row_dicts(idle_path, "TowerIdleRewards") if r.get("ID") not in (None, "")]
    if len(idle_rows) != 100:
        raise RuntimeError("爬塔挂机镜像应为 200 层，实际 %s" % len(idle_rows))
    idle_expanded = 0
    for row in idle_rows:
        layer = to_int(row.get("LayerLimitMin"))
        cond = "第%s层挂机｜按历史最高层结算" % layer
        items = [p for p in str(row.get("IdleRewards") or "").split(";") if p]
        nums = [p for p in str(row.get("IdleRewardsNum") or "").split(";") if p]
        times = [p for p in str(row.get("IdleRewardsTime") or "").split(";") if p]
        for item_text, num_text, time_text in zip(items, nums, times):
            item_id = to_int(item_text)
            per_day = float(num_text) * 86400.0 / float(time_text)
            per_day = int(per_day) if per_day == int(per_day) else round(per_day, 2)
            b.add_reward(
                "爬塔",
                "挂机产出",
                mirror_item_name(item_id, formal_item_name(item_id)),
                per_day,
                "%s/TowerIdleRewards.xlsx" % source_mirror,
                row.get("_row"),
                item_id=item_id,
                period="每日（挂机）",
                condition=cond,
                basis="挂机按历史最高层逐层累计",
                note="IdleRewards %s×%s / %s秒" % (item_text, num_text, time_text),
            )
            idle_expanded += 1
        pool_drop_id = to_int(row.get("DropId"))
        pool_per_cycle = to_int(row.get("DropIdNum"))
        pool_cycle_text = str(row.get("DropIdTimes") or "").split(";")[0]
        if pool_drop_id is not None and pool_per_cycle:
            cycle_seconds = float(pool_cycle_text)
            drops_per_day = pool_per_cycle * 86400.0 / cycle_seconds
            for entry in pool_entries:
                expect = round(drops_per_day / len(pool_entries), 2)
                b.add_reward(
                    "爬塔",
                    "挂机材料池",
                    mirror_item_name(entry["item_id"], entry["item"]),
                    expect,
                    "%s/TowerIdleRewards.xlsx + Drop_dungeon.xlsx" % source_mirror,
                    row.get("_row"),
                    item_id=entry["item_id"],
                    period="每日（挂机·期望）",
                    condition=cond,
                    basis="等权五选一期望值（池%s）" % pool_drop_id,
                    note="池 %s×%s次/%s秒，五项等权各20%%" % (pool_drop_id, pool_per_cycle, pool_cycle_text),
                )
                idle_expanded += 1
    mark_external(
        b,
        source_mirror,
        "已结构化",
        "CHG-044口径：账号级1-100层一次性首通 %s 行，总量 元晶7,300/熔晶7/旅券60/房车零件4,000/自选箱650/高阶课程笔记150/精英课程笔记10；"
        "挂机金币+房车零件逐层日产，第30层起材料池等权五选一期望；镜像##停用 %s 行与旧每周/扫荡/商店/赛季奖励不计入。" % (expanded, disabled),
        len(first_rows) + len(idle_rows),
        "",
    )
    b.mark("配置页-爬塔", "已由镜像承接", "旧经济母表配置页-爬塔与爬塔商店口径已废弃；爬塔产销改读 06_最终配置/爬塔 评审镜像（CHG-044）。")


def parse_verification_configs(b):
    ws = b.wb["配置页-无限挑战"]
    for r in range(4, ws.max_row + 1):
        if ws.cell(r, 7).value:
            b.add_reward("无限挑战", "生涯奖励", ws.cell(r, 7).value, ws.cell(r, 9).value, "配置页-无限挑战", r,
                         item_id=ws.cell(r, 8).value, period="生涯一次性",
                         condition="分数%s" % clean_value(ws.cell(r, 11).value),
                         note="DropId %s｜%s" % (clean_value(ws.cell(r, 10).value), clean_text(ws.cell(r, 12).value)))
    b.mark("配置页-无限挑战", "已结构化", "生涯奖励直接道具与 DropId 引用已登记。")

    arena_ws = b.wb["竞技场"]
    arena_attempt_note = "每日免费刷新%s次｜体力次数%s次｜购买%s次｜赛季%s天" % (
        clean_value(arena_ws.cell(25, 3).value),
        clean_value(arena_ws.cell(26, 3).value),
        clean_value(arena_ws.cell(27, 3).value),
        clean_value(arena_ws.cell(30, 3).value),
    )
    for item_col, qty_col, value_col in [(2, 3, 4), (5, 6, 7)]:
        if has_observed_value(arena_ws.cell(40, item_col).value):
            b.add_reward("竞技场(PVPVE)", "单场胜利奖励", arena_ws.cell(40, item_col).value,
                         arena_ws.cell(40, qty_col).value, "竞技场", 40, arena_ws.cell(40, value_col).value,
                         period="每场胜利", condition=arena_attempt_note)
        if has_observed_value(arena_ws.cell(44, item_col).value):
            b.add_reward("竞技场(PVPVE)", "单场失败奖励", arena_ws.cell(44, item_col).value,
                         arena_ws.cell(44, qty_col).value, "竞技场", 44, arena_ws.cell(44, value_col).value,
                         period="每场失败", condition=arena_attempt_note)

    season_days = clean_value(arena_ws.cell(30, 3).value) or 14
    season_period = "%s天赛季" % season_days
    cumulative_conditions = {}
    for idx, src_row in enumerate(range(100, 109), start=2):
        win_num = clean_value(arena_ws.cell(src_row, 2).value)
        if win_num != "":
            cumulative_conditions[idx] = "赛季累胜≥%s胜" % win_num
    first_reach_conditions = {
        cfg_row: arena_source_rank_condition(arena_ws, src_row)
        for cfg_row, src_row in enumerate(range(50, 71), start=2)
    }
    season_rank_conditions = {}
    for cfg_row in range(2, 46):
        src_row = 49 + ((cfg_row - 2) // 2)
        if src_row <= 73:
            season_rank_conditions[cfg_row] = arena_source_rank_condition(arena_ws, src_row)

    ws = b.wb["配置页-竞技场"]
    for r in range(2, ws.max_row + 1):
        if has_observed_value(ws.cell(r, 6).value):
            b.add_reward("竞技场(PVPVE)", "赛季累胜", ws.cell(r, 6).value, ws.cell(r, 8).value,
                         "配置页-竞技场", r, item_id=ws.cell(r, 7).value, period=season_period,
                         condition=cumulative_conditions.get(r, "赛季累胜奖励行%s" % r))
        if has_observed_value(ws.cell(r, 10).value):
            b.add_reward("竞技场(PVPVE)", "首次到达奖励", ws.cell(r, 10).value, ws.cell(r, 12).value,
                         "配置页-竞技场", r, item_id=ws.cell(r, 11).value, period="生涯一次性",
                         condition=first_reach_conditions.get(r, "段位首次行%s" % r))
        if has_observed_value(ws.cell(r, 14).value):
            b.add_reward("竞技场(PVPVE)", "赛季结算奖励", ws.cell(r, 14).value, ws.cell(r, 16).value,
                         "配置页-竞技场", r, item_id=ws.cell(r, 15).value, period=season_period,
                         condition=season_rank_conditions.get(r, "赛季结算奖励行%s" % r))

    arena_formal_count = 0
    arena_win_reward = cfg_path("Arena", "ArenaWinReward.xlsx")
    if os.path.exists(arena_win_reward):
        rows = row_dicts(arena_win_reward, "WinReward")
        arena_formal_count += len(rows)
        for row in rows:
            if clean_text(row.get("IsValid")).lower() == "false":
                continue
            cond = "玩家等级%s-%s｜%s" % (
                clean_value(row.get("PlayerLvMin")),
                clean_value(row.get("PlayerLvMax")),
                arena_attempt_note,
            )
            add_drop_ref_period(b, "竞技场(PVPVE)", "正式单场胜利奖励引用", "ArenaWinReward.DropId",
                                row.get("DropId"), "正式:Arena/ArenaWinReward.xlsx", row.get("_row"),
                                period="每场胜利", condition=cond)
    arena_win_streak = cfg_path("Arena", "ArenaWinStreak.xlsx")
    if os.path.exists(arena_win_streak):
        rows = row_dicts(arena_win_streak, "ArenaReward")
        arena_formal_count += len(rows)
        for row in rows:
            if clean_text(row.get("IsValid")).lower() == "false":
                continue
            cond = "赛季累胜≥%s胜" % clean_value(row.get("WinNum"))
            add_drop_ref_period(b, "竞技场(PVPVE)", "正式赛季累胜引用", "ArenaWinStreak.DropId",
                                row.get("DropId"), "正式:Arena/ArenaWinStreak.xlsx", row.get("_row"),
                                period=season_period, condition=cond)
    arena_rank = cfg_path("Arena", "ArenaRank.xlsx")
    if os.path.exists(arena_rank):
        rows = row_dicts(arena_rank, "Rank")
        arena_formal_count += len(rows)
        for row in rows:
            if clean_text(row.get("IsValid")).lower() == "false":
                continue
            cond = arena_formal_rank_condition(row)
            add_drop_ref_period(b, "竞技场(PVPVE)", "正式段位首次奖励引用", "ArenaRank.RankAchieveReward",
                                row.get("RankAchieveReward"), "正式:Arena/ArenaRank.xlsx", row.get("_row"),
                                period="生涯一次性", condition=cond)
            add_drop_ref_period(b, "竞技场(PVPVE)", "正式段位赛季结算引用", "ArenaRank.RankSeasonReward",
                                row.get("RankSeasonReward"), "正式:Arena/ArenaRank.xlsx", row.get("_row"),
                                period=season_period, condition=cond)
    arena_rank_reward = cfg_path("Arena", "ArenaRankReward.xlsx")
    if os.path.exists(arena_rank_reward):
        rows = row_dicts(arena_rank_reward, "ScoreReward")
        arena_formal_count += len(rows)
        for row in rows:
            if clean_text(row.get("IsValid")).lower() == "false":
                continue
            cond = "排名%s-%s｜基础分%s" % (
                clean_value(row.get("RankMin")),
                clean_value(row.get("RankMax")),
                clean_value(row.get("BasicScore")),
            )
            add_drop_ref_period(b, "竞技场(PVPVE)", "正式排行赛季结算引用", "ArenaRankReward.DropId",
                                row.get("DropId"), "正式:Arena/ArenaRankReward.xlsx", row.get("_row"),
                                period=season_period, condition=cond)
    formal_arena_shop = add_formal_shopgoods(
        b, "竞技场(PVPVE)", "竞技场商店", 1109, "正式:Shop/ShopGoods.xlsx#Arena"
    )
    b.mark("配置页-竞技场", "已结构化",
           "单场胜负、赛季累胜、首次到达、赛季结算已登记，并补充达成条件与%s天赛季周期；竞技场商店改读正式 ShopGoods%s%s。" %
           (season_days,
            "，共 %s 个商品" % formal_arena_shop if formal_arena_shop else "",
            "；正式 Arena 奖励引用 %s 行" % arena_formal_count if arena_formal_count else ""))

    parse_tower_mirror(b)


def parse_mythic(b):
    ws = b.wb["大秘境"]
    for r in range(8, 33):
        if ws.cell(r, 12).value:
            cond = "层数%s" % clean_value(ws.cell(r, 12).value)
            b.add_reward("大秘境", "每周层数奖励", ws.cell(r, 13).value, ws.cell(r, 14).value, "大秘境", r,
                         period="每周", condition=cond)
            b.add_reward("大秘境", "每周层数奖励", ws.cell(r, 15).value, ws.cell(r, 16).value, "大秘境", r,
                         period="每周", condition=cond)
    for r in range(43, 53):
        if ws.cell(r, 11).value:
            b.add_reward("大秘境", "每周积分奖励", ws.cell(r, 12).value, ws.cell(r, 13).value, "大秘境", r,
                         period="每周", condition="积分%s" % clean_value(ws.cell(r, 11).value))
        if ws.cell(r, 15).value:
            b.add_reward("大秘境", "赛季积分奖励", ws.cell(r, 16).value, ws.cell(r, 17).value, "大秘境", r,
                         period="赛季", condition="积分%s" % clean_value(ws.cell(r, 15).value))
        if ws.cell(r, 20).value:
            b.add_reward("大秘境", "排行奖励", ws.cell(r, 20).value, ws.cell(r, 21).value, "大秘境", r,
                         period="赛季排行", condition="档位%s" % clean_value(ws.cell(r, 19).value))
    formal_count = 0
    season_rank_reward = cfg_path("mythic_dungeon", "SeasonRankReward.xlsx")
    if os.path.exists(season_rank_reward):
        rows = row_dicts(season_rank_reward, "ScoreReward")
        for row in rows:
            rank_per = clean_value(row.get("RankPer"))
            rank = clean_value(row.get("Rank"))
            cond = "排名比例%s/10000｜人数不足时具体排名%s" % (rank_per, rank)
            add_drop_ref_period(b, "大秘境", "正式赛季排行奖励引用", "SeasonRankReward.DropId",
                                row.get("DropId"), "正式:mythic_dungeon/SeasonRankReward.xlsx", row.get("_row"),
                                period="赛季排行", condition=cond)
            formal_count += 1
        if formal_count:
            mark_external(b, "正式:mythic_dungeon/SeasonRankReward.xlsx", "已补强",
                          "大秘境正式赛季排行奖励 DropId 引用已登记；真实包内容待 Drop 展开。", formal_count, "")
    b.mark("大秘境", "已结构化", "每周层数、每周积分、赛季积分、旧设计排行入口%s已登记。" %
           ("和正式赛季排行奖励引用" if formal_count else ""))


def parse_boss_challenge(b):
    ws = b.wb["世界boss"]
    legacy_bosses = sorted({
        clean_text(ws.cell(r, 2).value)
        for r in range(6, ws.max_row + 1)
        if is_num(ws.cell(r, 1).value) and clean_text(ws.cell(r, 2).value)
    })
    b.mark(
        "世界boss",
        "历史参考，不计入产销",
        "页签名为世界boss，内容仅覆盖%s个旧boss（%s）；BOSS挑战真实产出改按正式 BossDungeon/Boss_Dungeon.xlsx 的7个boss展开。"
        % (len(legacy_bosses), "、".join(legacy_bosses)),
    )


def parse_guild(b):
    ws = b.wb["公会数值"]
    for r in range(40, 45):
        cond = "%s｜%s" % (clean_text(ws.cell(r, 2).value), clean_text(ws.cell(r, 3).value))
        b.add_reward("公会", "公会任务", "公会个人代币", ws.cell(r, 5).value, "公会数值", r, period="每日", condition=cond)
        b.add_reward("公会", "公会任务", "贡献值", ws.cell(r, 6).value, "公会数值", r, period="每日", condition=cond)
        b.add_reward("公会", "公会任务", "公会集体代币", ws.cell(r, 7).value, "公会数值", r, period="每日", condition=cond)
    for r in range(49, 53):
        cond = "派遣%s" % clean_text(ws.cell(r, 2).value)
        b.add_reward("公会", "公会派遣基础", "公会个人代币", ws.cell(r, 4).value, "公会数值", r, period="每日", condition=cond)
        b.add_reward("公会", "公会派遣基础", "贡献值", ws.cell(r, 5).value, "公会数值", r, period="每日", condition=cond)
        b.add_reward("公会", "公会派遣基础", "公会集体代币", ws.cell(r, 6).value, "公会数值", r, period="每日", condition=cond)
    for r in range(57, 61):
        cond = "派遣%s" % clean_text(ws.cell(r, 2).value)
        for item_col, qty_col, value_col in [(3, 4, 5), (6, 7, 8), (9, 10, 11)]:
            b.add_reward("公会", "公会派遣额外奖励", ws.cell(r, item_col).value, ws.cell(r, qty_col).value, "公会数值", r,
                         ws.cell(r, value_col).value, period="每日随机", condition=cond)
    for r in range(77, 84):
        b.add_shop("公会", "公会商店", ws.cell(r, 3).value, ws.cell(r, 4).value, ws.cell(r, 6).value, ws.cell(r, 7).value,
                   "公会数值", r, ws.cell(r, 5).value, ws.cell(r, 8).value, ws.cell(r, 9).value,
                   "%s%s" % (clean_text(ws.cell(r, 10).value), clean_value(ws.cell(r, 11).value)),
                   "商品ID %s" % clean_value(ws.cell(r, 2).value))
    b.mark("公会数值", "已结构化", "公会任务、派遣、派遣额外奖励、公会商店已登记；心愿墙/建设保留为规则口径。")


def parse_growth_sinks(b):
    ws = b.wb["角色升级"]
    hero_lv_costs = formal_num_map(cfg_path("Hero", "HeroLv.xlsx"), "Lv", "UpgradeCost")
    for r in range(7, 67):
        lv = to_int(ws.cell(r, 2).value)
        if lv is not None:
            if hero_lv_costs and lv in hero_lv_costs and hero_lv_costs[lv] is None:
                continue
            cond = "角色Lv%s" % lv
            b.add_cost("角色养成", "角色升级", "角色经验", ws.cell(r, 4).value, "角色升级", r, condition=cond)
            b.add_cost("角色养成", "角色升级", "金币", ws.cell(r, 6).value, "角色升级", r, condition=cond)
    b.mark("角色升级", "已结构化", "角色逐级经验与金币消耗已登记；角色升级不按品质缩放，正式满级无下一等级消耗的行已跳过。")

    ws = b.wb["角色升阶"]
    for r in range(4, 8):
        cond = "突破%s次/Lv%s" % (clean_value(ws.cell(r, 3).value), clean_value(ws.cell(r, 2).value))
        b.add_cost("角色养成", "角色升阶", ws.cell(r, 4).value, ws.cell(r, 5).value, "角色升阶", r,
                   ws.cell(r, 6).value, condition=cond)
        b.add_cost("角色养成", "角色升阶", ws.cell(r, 7).value, ws.cell(r, 8).value, "角色升阶", r,
                   ws.cell(r, 9).value, condition=cond)
    b.mark("角色升阶", "已结构化", "角色突破材料与金币消耗已登记。")

    ws = b.wb["专武"]
    weapon_gold_ratio = economy_param("专武升级金币比", 0.1)
    weapon_lv_costs_by_quality = formal_num_map_by_quality(
        cfg_path("ExclusiveWeapon", "ExclWeaponLv.xlsx"), "Lv", "UpgradeCostExp", "EqptLv"
    )
    for r in range(7, 67):
        lv = to_int(ws.cell(r, 2).value)
        if lv is not None:
            quality_maps = weapon_lv_costs_by_quality or {4: formal_num_map(
                cfg_path("ExclusiveWeapon", "ExclWeaponLv.xlsx"), "Lv", "UpgradeCostExp", "EqptLv",
                row_filter=lambda row: to_int(row.get("Quality")) == 4
            )}
            for quality in sorted(quality_maps.keys(), reverse=True):
                cost_map = quality_maps[quality]
                if lv in cost_map and cost_map[lv] is None:
                    continue
                label = quality_name(quality)
                factor = 1.0 if quality == 4 else (0.8 if quality == 3 else 0.7 if quality == 2 else 1.0)
                exp_cost = cost_map.get(lv, scaled_qty(ws.cell(r, 4).value, factor))
                cond = "%s｜专武Lv%s" % (label, lv)
                b.add_cost("专武养成", "专武升级", "专武经验", exp_cost, "专武", r,
                           condition=cond, note="按专武品质%s计入升级成本" % label)
                b.add_cost("专武养成", "专武升级", "金币", scaled_qty(exp_cost, weapon_gold_ratio), "专武", r,
                           condition=cond, note="金币=UpgradeCostExp×专武升级金币比%s" % weapon_gold_ratio)
        if ws.cell(r, 12).value:
            cond = "专武突破%s次/Lv%s" % (clean_value(ws.cell(r, 13).value), clean_value(ws.cell(r, 12).value))
            b.add_cost("专武养成", "专武突破", ws.cell(r, 14).value, ws.cell(r, 15).value, "专武", r,
                       ws.cell(r, 16).value, condition=cond)
            b.add_cost("专武养成", "专武突破", ws.cell(r, 17).value, ws.cell(r, 18).value, "专武", r,
                       ws.cell(r, 19).value, condition=cond)
    b.mark("专武", "已结构化", "专武升级经验/金币已按品质登记，突破材料/金币已登记；正式满级无下一等级消耗的行已跳过。")

    ws = b.wb["旅券"]
    for r in range(5, 10):
        if is_num(ws.cell(r, 2).value):
            cond = "旅券Lv%s" % clean_value(ws.cell(r, 2).value)
            b.add_cost("旅券养成", "旅券升级", "旅券经验", ws.cell(r, 4).value, "旅券", r, condition=cond)
            b.add_cost("旅券养成", "旅券升级", "金币", ws.cell(r, 6).value, "旅券", r, condition=cond)
    b.mark("旅券", "已结构化", "旅券升级经验与金币消耗已登记。")

    ws = b.wb["角色星盘"]
    for r in range(7, ws.max_row + 1):
        if not is_num(ws.cell(r, 2).value):
            continue
        cond = "星盘点%s" % clean_value(ws.cell(r, 2).value)
        for item_col, qty_col in [(4, 5), (6, 7), (8, 9), (10, 11)]:
            b.add_cost("角色养成", "角色星盘", ws.cell(r, item_col).value, ws.cell(r, qty_col).value, "角色星盘", r, condition=cond)
        b.add_cost("角色养成", "角色星盘", "金币", ws.cell(r, 12).value, "角色星盘", r, condition=cond)
    b.mark("角色星盘", "已结构化", "星盘逐点材料与金币消耗已登记。")

    ws = b.wb["角色升星、角色抽卡"]
    b.add_cost("抽卡", "角色抽卡", "钻石", ws.cell(8, 7).value, "角色升星、角色抽卡", 8,
               condition="单抽定价", basis="抽卡消耗")
    for r in range(3, 6):
        b.add_reward("抽卡", "角色重复转化", ws.cell(r, 10).value, ws.cell(r, 12).value, "角色升星、角色抽卡", r,
                     period="抽卡重复", condition="%s非首次抽到" % clean_text(ws.cell(r, 7).value))
    b.mark("角色升星、角色抽卡", "已结构化（首版）", "单抽钻石消耗与重复转化代币已登记；概率/保底完整模型保留在原页。")

    ws = b.wb["专武升星、抽卡"]
    b.add_cost("抽卡", "专武抽卡", "钻石", ws.cell(11, 3).value, "专武升星、抽卡", 11,
               condition="单抽定价", basis="抽卡消耗")
    for r in range(3, 6):
        b.add_reward("抽卡", "专武重复转化", ws.cell(r, 6).value, ws.cell(r, 8).value, "专武升星、抽卡", r,
                     period="抽卡重复", condition="%s非首次抽到" % clean_text(ws.cell(r, 3).value))
    for r in range(15, 20):
        if ws.cell(r, 10).value:
            cond = "专武升星%s" % clean_value(ws.cell(r, 10).value)
            b.add_cost("专武养成", "专武升星", "同名专武", ws.cell(r, 11).value, "专武升星、抽卡", r, condition=cond)
            b.add_cost("专武养成", "专武升星金币", "金币", ws.cell(r, 12).value, "专武升星、抽卡", r, condition=cond)
    b.mark("专武升星、抽卡", "已结构化（首版）", "专武抽卡消耗、重复转化、升星同名专武和金币已登记。")

    ws = b.wb["炮台养成"]
    for r in range(17, ws.max_row + 1):
        if not is_num(ws.cell(r, 1).value):
            continue
        cond = "炮台目标Lv%s" % clean_value(ws.cell(r, 1).value)
        small_qty = ws.cell(r, 2).value
        b.add_cost("炮台养成", "炮台逐级升级", "炮台升级小材料", small_qty, "炮台养成", r, condition=cond)
        for col, label in [(4, "S炮台升级大材料"), (5, "A炮台升级大材料"), (6, "B炮台升级大材料")]:
            b.add_cost("炮台养成", "炮台节点突破", label, ws.cell(r, col).value, "炮台养成", r, condition=cond)
    b.mark("炮台养成", "已结构化（首版）", "炮台逐级小材料与节点大材料已登记；赛季进度测算仍保留原页。")

    ws = b.wb["共鸣装备"]
    for r in range(7, 67):
        if is_num(ws.cell(r, 2).value):
            cond = "共鸣装备Lv%s" % clean_value(ws.cell(r, 2).value)
            b.add_cost("共鸣装备", "装备升级", "收容物经验", ws.cell(r, 4).value, "共鸣装备", r, condition=cond)
            b.add_cost("共鸣装备", "装备升级", "金币", ws.cell(r, 6).value, "共鸣装备", r, condition=cond)
        if ws.cell(r, 12).value:
            cond = "共鸣装备星级%s" % clean_value(ws.cell(r, 12).value)
            b.add_cost("共鸣装备", "装备升星", ws.cell(r, 14).value, ws.cell(r, 15).value, "共鸣装备", r,
                       ws.cell(r, 16).value, condition=cond)
            b.add_cost("共鸣装备", "装备升星", ws.cell(r, 17).value, ws.cell(r, 18).value, "共鸣装备", r,
                       ws.cell(r, 19).value, condition=cond)
    b.mark("共鸣装备", "已结构化（首版）", "装备升级经验/金币与升星材料/金币已登记。")


RV_GUIDE_ITEM_IDS = {"行程指南": 1075, "安行指南": 1076, "探路指南": 1077, "见闻指南": 1078, "共鸣指南": 1079}
RV_ITEM_FALLBACK_NAMES = {
    1: "金币",
    1074: "房车零件",
    1156: "高阶课程笔记",
    1157: "精英课程笔记",
}


def parse_rv_growth(b):
    """房车消耗改读 `生成_房车.xlsx` 的结构化页签（2026-09-04 起）。

    04 交付版房车工作簿不再携带「经济消耗明细」账本页；本函数直接消费
    「房车整备曲线」与「出行指南节点等级」两页 QA 数值表。
    """

    source = "养成/生成_房车.xlsx"
    path = os.path.join(V2_DIR, "养成", "生成_房车.xlsx")
    if not os.path.exists(path):
        mark_external(b, source, "待生成", "房车养成生成表不存在；先运行 养成/scripts/gen_rv_growth.py。")
        return
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    for sheet in ("房车整备曲线", "出行指南节点等级"):
        if sheet not in wb.sheetnames:
            wb.close()
            mark_external(b, source, "缺少结构化页", "未找到 `%s` 页，无法写入经济总账。" % sheet)
            return

    def rv_item_name(item_id):
        resolved = formal_item_name(item_id)
        if resolved and not str(resolved).startswith("ItemId "):
            return resolved
        return RV_ITEM_FALLBACK_NAMES.get(item_id, resolved)

    count = 0
    ws = wb["房车整备曲线"]
    headers = [clean_text(c.value) for c in ws[1]]
    for row_idx, values in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        row = {headers[i]: values[i] if i < len(values) else "" for i in range(len(headers))}
        target_lv = to_int(row.get("目标等级"))
        if target_lv is None or target_lv <= 1:
            continue
        cond = "房车目标Lv%s" % target_lv
        for column, item_id in (("房车零件", 1074), ("金币", 1)):
            qty = row.get(column)
            if qty in (None, ""):
                continue
            b.add_cost("房车养成", "房车整备", rv_item_name(item_id), qty,
                       "%s:房车整备曲线" % source, row_idx,
                       condition=cond, basis="房车整备逐级强化消耗", item_id=item_id)
            count += 1
    ws = wb["出行指南节点等级"]
    headers = [clean_text(c.value) for c in ws[1]]
    for row_idx, values in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        row = {headers[i]: values[i] if i < len(values) else "" for i in range(len(headers))}
        guide = clean_text(row.get("指南"))
        career = clean_text(row.get("职业"))
        node_name = clean_text(row.get("节点名"))
        node_id = clean_value(row.get("NodeId"))
        target_lv = clean_value(row.get("目标等级"))
        if not guide or not career:
            continue
        career_item = RV_GUIDE_ITEM_IDS.get(guide)
        if career_item is None:
            wb.close()
            raise RuntimeError("生成_房车.xlsx 出现未知指南: %s" % guide)
        cond = "%s｜%s｜%s（Node %s）｜升到Lv%s" % (guide, career, node_name, node_id, target_lv)
        basis = "出行指南多级节点升级消耗（CHG-053后口径）"
        for column, item_id in (("职业基础材料", career_item), ("高级指南材料", 1156), ("超高级指南材料", 1157)):
            qty = row.get(column)
            if qty in (None, "", 0):
                continue
            b.add_cost("房车养成", "出行指南", rv_item_name(item_id), qty,
                       "%s:出行指南节点等级" % source, row_idx,
                       condition=cond, basis=basis, item_id=item_id)
            count += 1
        qty = row.get("金币")
        if qty not in (None, "", 0):
            b.add_cost("房车养成", "出行指南", rv_item_name(1), qty,
                       "%s:出行指南节点等级" % source, row_idx,
                       condition=cond, basis=basis, item_id=1)
            count += 1
    wb.close()
    mark_external(b, source, "已结构化", "房车整备曲线与出行指南多级节点消耗已登记（出行指南读06评审镜像，CHG-053口径）。", count, "")


def parse_formal_boss_challenge(b):
    source = "正式:BossDungeon/Boss_Dungeon.xlsx"
    path = cfg_path("BossDungeon", "Boss_Dungeon.xlsx")
    drop_path = cfg_path("Drop", "Drop_dungeon.xlsx")
    if not os.path.exists(path):
        return
    rows = row_dicts(path)
    drop_entries = drop_entries_by_id(drop_path)
    boss_names = set()
    expanded = 0
    reward_refs = 0
    for row in rows:
        boss = clean_text(row.get("BossName"))
        if boss:
            boss_names.add(boss)
        layer = clean_value(row.get("Layer"))
        level_id = clean_value(row.get("LevelId"))
        layer_name = clean_text(row.get("LayerName"))
        cond = "%s｜%s｜Layer %s｜LevelId %s" % (boss, layer_name, layer, level_id)
        reward = to_int(row.get("Reward"))
        best_reward = clean_value(row.get("BestReward"))
        entries = drop_entries.get(reward, [])
        if entries:
            for entry in entries:
                item = b.item_from_id(entry["item_id"])
                if item.startswith("ItemId "):
                    item = entry["item"]
                note = "BossDungeon.Reward=%s；Drop_dungeon 行%s。" % (reward, entry["row"])
                if entry["invalid"]:
                    note += " Drop 行当前为 ## 标记。"
                b.add_reward(
                    "BOSS挑战",
                    "正式Boss通关奖励",
                    item,
                    entry["qty"],
                    "正式:BossDungeon/Boss_Dungeon.xlsx + Drop_dungeon.xlsx",
                    row.get("_row"),
                    item_id=entry["item_id"],
                    period="一次性首通",
                    condition=cond,
                    basis="正式BossDungeon.Reward展开",
                    note=note,
                )
                expanded += 1
        elif reward:
            b.add_ref("BOSS挑战", "正式Boss通关奖励引用", "BossDungeon.Reward", reward,
                      source, row.get("_row"), condition=cond, note="Reward DropId %s 未在 Drop_dungeon 展开" % reward)
            reward_refs += 1
        if best_reward:
            b.add_ref("BOSS挑战", "正式最高奖励预览", "BossDungeon.BestReward", best_reward,
                      source, row.get("_row"), condition=cond, note="BestReward 是当前boss显示最高奖励预览，避免与通关产出重复计入。")
    mark_external(
        b,
        source,
        "已补强",
        "正式 BossDungeon 的7个boss已按 Reward 展开产出；BestReward 保留为最高奖励预览引用。boss=%s；展开%s行，未展开引用%s行。"
        % ("、".join(sorted(boss_names)), expanded, reward_refs),
        len(rows),
        "",
    )


def parse_formal_neural_roam(b):
    source = "正式:neural_roam"
    reward_path = cfg_path("neural_roam", "NR_HighestScoreReward.xlsx")
    rank_path = cfg_path("neural_roam", "NR_RankReward.xlsx")
    layer_path = cfg_path("neural_roam", "NR_Layer.xlsx")
    count = 0
    if os.path.exists(reward_path):
        rows = row_dicts(reward_path)
        count += len(rows)
        for row in rows:
            drop_id = clean_value(row.get("DropId"))
            if drop_id:
                b.add_ref("无限挑战", "无限之旅最高分奖励", "无限之旅最高分奖励包", drop_id,
                          "正式:neural_roam/NR_HighestScoreReward.xlsx", row.get("_row"),
                          condition="Score %s" % clean_value(row.get("Score")),
                          note="neural_roam 已按用户裁决归入无限挑战（无限之旅）。")
    if os.path.exists(rank_path):
        rows = row_dicts(rank_path)
        count += len(rows)
        for row in rows:
            drop_id = clean_value(row.get("DropId"))
            if drop_id:
                b.add_ref("无限挑战", "无限之旅排行奖励", "无限之旅排行奖励包", drop_id,
                          "正式:neural_roam/NR_RankReward.xlsx", row.get("_row"),
                          condition="Rank %s / RankPer %s" % (clean_value(row.get("Rank")), clean_value(row.get("RankPer"))),
                          note="neural_roam 已按用户裁决归入无限挑战（无限之旅）。")
    if os.path.exists(layer_path):
        rows = row_dicts(layer_path)
        count += len(rows)
        for row in rows:
            cond = "Layer %s" % clean_value(row.get("Layer"))
            point = clean_value(row.get("Point"))
            battle_point = clean_value(row.get("BattlePointGain"))
            if point:
                b.add_reward("无限挑战", "无限之旅层收益", "无限之旅积分", point,
                             "正式:neural_roam/NR_Layer.xlsx", row.get("_row"),
                             period="每层", condition=cond, basis="玩法积分",
                             note="neural_roam 已按用户裁决归入无限挑战（无限之旅）。")
            if battle_point:
                b.add_reward("无限挑战", "无限之旅层收益", "无限之旅战斗积分", battle_point,
                             "正式:neural_roam/NR_Layer.xlsx", row.get("_row"),
                             period="每层", condition=cond, basis="玩法积分",
                             note="neural_roam 已按用户裁决归入无限挑战（无限之旅）。")
    if count:
        mark_external(b, source, "已并入无限挑战", "NR_HighestScoreReward/NR_Layer 已登记到无限挑战（无限之旅）；空 DropId 的排行档位保留为空。", count, "")


def parse_formal_mapping_equipment_growth(b):
    lv_path = cfg_path("SpecialEquipment", "SpecialEquipmentLvUp.xlsx")
    quality_path = cfg_path("SpecialEquipment", "SpecialEquipmentQuality.xlsx")
    effect_path = cfg_path("SpecialEquipment", "SpecialEquipmentEffectDrop.xlsx")
    count = 0
    upgrade_gold_ratio = economy_param("映射装备升级金币比", 1)
    if os.path.exists(lv_path):
        rows = row_dicts(lv_path)
        count += len(rows)
        for row in rows:
            qty = clean_value(row.get("CostExp"))
            if qty:
                cond = "%s TargetLv %s" % (clean_text(row.get("Quality")), clean_value(row.get("TargetLv")))
                b.add_cost("映射装备养成", "正式装备升级", "主角装备经验", qty,
                           "正式:SpecialEquipment/SpecialEquipmentLvUp.xlsx", row.get("_row"),
                           condition=cond, note="CostExp")
                b.add_cost("映射装备养成", "正式装备升级金币", "金币", scaled_qty(qty, upgrade_gold_ratio),
                           "正式:SpecialEquipment/SpecialEquipmentLvUp.xlsx", row.get("_row"),
                           condition=cond, note="金币=CostExp×映射装备升级金币比%s；正式表无金币字段，经济表按参数计入。" % upgrade_gold_ratio)
    if os.path.exists(quality_path):
        rows = row_dicts(quality_path)
        count += len(rows)
        for row in rows:
            cond = "%s 品质" % clean_text(row.get("Quality"))
            for field, group in [
                ("IdentifyCost", "正式鉴定消耗"),
                ("IdentifyCostCurrency", "正式鉴定货币"),
                ("HoleCost", "正式打孔消耗"),
                ("HoleCostCurrency", "正式打孔货币"),
            ]:
                for item, item_id, qty in prop_entries(row.get(field)):
                    b.add_cost("映射装备养成", group, item, qty,
                               "正式:SpecialEquipment/SpecialEquipmentQuality.xlsx", row.get("_row"),
                               condition=cond, note="%s: %s,%s" % (field, item_id, qty))
            for item, item_id, qty in prop_entries(row.get("ExtraItemList")):
                b.add_ref("映射装备养成", "正式品质额外道具", item, qty,
                          "正式:SpecialEquipment/SpecialEquipmentQuality.xlsx", row.get("_row"),
                          item_id=item_id, condition=cond, note="ExtraItemList")
    if os.path.exists(effect_path):
        rows = row_dicts(effect_path)
        count += len(rows)
        for row in rows:
            if row.get("EffectList"):
                b.add("映射装备养成", "正式词条池", "引用", "映射装备词条池", clean_value(row.get("Id")),
                      sheet="正式:SpecialEquipment/SpecialEquipmentEffectDrop.xlsx", row=row.get("_row"),
                      condition="EffectDropId %s" % clean_value(row.get("Id")),
                      basis="词条池引用，EffectList 不按 DropId/RewardId 展开",
                      note="EffectList %s" % clean_text(row.get("EffectList")))
    if count:
        mark_external(b, "正式:SpecialEquipment", "已补强", "映射装备正式升级、鉴定、打孔、品质额外道具与词条池入口已登记。", count, "")


def parse_formal_strategy_growth(b):
    lv_path = cfg_path("strategy", "StrategyLv.xlsx")
    resolve_path = cfg_path("strategy", "StrategyResolve.xlsx")
    craft_path = cfg_path("item_craft", "StrategyCraft.xlsx")
    shop_path = cfg_path("Shop", "StrategyCardShop.xlsx")
    count = 0
    upgrade_gold_ratio = economy_param("旅券升级金币比", 10)
    if os.path.exists(lv_path):
        rows = row_dicts(lv_path)
        count += len(rows)
        for row in rows:
            qty = clean_value(row.get("UpgradeCostExp"))
            if qty not in ("", 0):
                cond = "Quality %s / Lv %s" % (clean_value(row.get("Quality")), clean_value(row.get("Lv")))
                b.add_cost("旅券养成", "正式旅券升级", "旅券经验", qty,
                           "正式:strategy/StrategyLv.xlsx", row.get("_row"), condition=cond, note="UpgradeCostExp")
                b.add_cost("旅券养成", "正式旅券升级金币", "金币", scaled_qty(qty, upgrade_gold_ratio),
                           "正式:strategy/StrategyLv.xlsx", row.get("_row"), condition=cond,
                           note="金币=UpgradeCostExp×旅券升级金币比%s；正式表无金币字段，经济表按参数计入。" % upgrade_gold_ratio)
    if os.path.exists(resolve_path):
        rows = row_dicts(resolve_path)
        count += len(rows)
        for row in rows:
            cond = "Quality %s" % clean_value(row.get("Quality"))
            exp = clean_value(row.get("Exp"))
            if exp:
                b.add_reward("旅券养成", "正式旅券分解", "旅券经验", exp,
                             "正式:strategy/StrategyResolve.xlsx", row.get("_row"),
                             period="分解", condition=cond, note="Exp")
            for item, item_id, qty in prop_entries(row.get("ResolveGetItem")):
                b.add_reward("旅券养成", "正式旅券分解", item, qty,
                             "正式:strategy/StrategyResolve.xlsx", row.get("_row"),
                             item_id=item_id, period="分解", condition=cond, note="ResolveGetItem")
    if os.path.exists(craft_path):
        rows = row_dicts(craft_path)
        count += len(rows)
        for row in rows:
            cond = "CraftId %s / Suit %s / %s" % (clean_value(row.get("Id")), clean_value(row.get("StrategySuitId")), clean_text(row.get("StrategyType")))
            for field, group in [
                ("RandomCostItem", "正式旅券随机制作"),
                ("CostItem", "正式旅券指定制作"),
                ("FixMainAttrCostItem", "正式旅券定主属性制作"),
                ("CostCurrency", "正式旅券制作货币"),
            ]:
                for item, item_id, qty in prop_entries(row.get(field)):
                    b.add_cost("旅券养成", group, item, qty,
                               "正式:item_craft/StrategyCraft.xlsx", row.get("_row"),
                               condition=cond, note="%s: %s,%s" % (field, item_id, qty))
    if os.path.exists(shop_path):
        rows = row_dicts(shop_path)
        count += len(rows)
        for row in rows:
            price = prop_entries(row.get("Price"))
            item_name = clean_text(row.get("Name")) or "StrategyCard %s" % clean_value(row.get("ItemId"))
            item_label = "%s（StrategyCardId %s）" % (item_name, clean_value(row.get("ItemId")))
            if price:
                cost_item, _cost_id, cost_qty = price[0]
                b.add_shop("旅券养成", "正式旅券商店", item_label, clean_value(row.get("Num")),
                           cost_item, cost_qty, "正式:Shop/StrategyCardShop.xlsx", row.get("_row"),
                           period="LimitNum %s" % clean_value(row.get("LimitNum")),
                           condition="ShopItem %s" % clean_value(row.get("Id")),
                           note="Price %s" % clean_text(row.get("Price")))
    if count:
        mark_external(b, "正式:strategy/item_craft/StrategyCardShop", "已补强", "旅券正式升级、分解、制作和正式旅券商店已登记。", count, "")


def add_formal_props(b, system, group, direction, prop_value, sheet, row, period="", condition="", basis="", note=""):
    for item, item_id, qty in prop_entries(prop_value):
        if direction == "消耗":
            b.add_cost(system, group, item, qty, sheet, row, period=period, condition=condition,
                       basis=basis or "正式配置消耗", note=note)
        else:
            b.add_reward(system, group, item, qty, sheet, row, item_id=item_id, period=period,
                         condition=condition, basis=basis or "正式配置直接奖励", note=note)


def add_drop_ref(b, system, group, label, drop_id, sheet, row, condition="", note=""):
    drop_id = clean_value(drop_id)
    if drop_id in ("", 0):
        return
    b.add_ref(system, group, label, drop_id, sheet, row, condition=condition, note=note)


def add_drop_ref_period(b, system, group, label, drop_id, sheet, row, period="", condition="", note=""):
    drop_id = clean_value(drop_id)
    if drop_id in ("", 0):
        return
    b.add(system, group, "引用", label, drop_id, "", "", "", "", "", "", period, condition, sheet, row,
          "奖励包/配置引用，待 DropId/RewardId 展开", note)


def parse_formal_task_and_seven_day(b):
    task_path = cfg_path("task", "Task.xlsx")
    daily_active_path = cfg_path("task", "DailyActiveReward.xlsx")
    weekly_reward_path = cfg_path("task", "WeeklyReward.xlsx")
    seven_path = cfg_path("SignInReward", "SevenDaySign.xlsx")
    count = 0
    if os.path.exists(task_path):
        rows = row_dicts(task_path, "Task")
        count += len(rows)
        for row in rows:
            cond = "TaskId %s｜%s｜%s" % (clean_value(row.get("Id")), clean_text(row.get("TaskType")), clean_text(row.get("TaskName")))
            add_drop_ref(b, "任务", "正式Task奖励", "Task.DropId奖励包", row.get("DropId"),
                         "正式:task/Task.xlsx", row.get("_row"), condition=cond)
    if os.path.exists(daily_active_path):
        rows = row_dicts(daily_active_path)
        count += len(rows)
        for row in rows:
            cond = "DailyActivePoint %s" % clean_value(row.get("ActivePoint"))
            add_drop_ref(b, "任务", "正式日活跃奖励", "DailyActiveReward.RewardId奖励包", row.get("RewardId"),
                         "正式:task/DailyActiveReward.xlsx", row.get("_row"), condition=cond)
    if os.path.exists(weekly_reward_path):
        rows = row_dicts(weekly_reward_path)
        count += len(rows)
        for row in rows:
            cond = "WeeklyActivePoint %s" % clean_value(row.get("ActivePoint"))
            add_drop_ref(b, "任务", "正式周活跃奖励", "WeeklyReward.RewardId奖励包", row.get("RewardId"),
                         "正式:task/WeeklyReward.xlsx", row.get("_row"), condition=cond)
    if os.path.exists(seven_path):
        rows = row_dicts(seven_path)
        count += len(rows)
        for row in rows:
            cond = "ActivityId %s｜OpenDay %s" % (clean_value(row.get("ActivityId")), clean_value(row.get("OpenDay")))
            add_formal_props(b, "7日任务", "正式七日签到奖励", "产出", row.get("ItemReward"),
                             "正式:SignInReward/SevenDaySign.xlsx", row.get("_row"),
                             period="新手7日", condition=cond, note="用户回答：补充正式七日奖励入口。")
    if count:
        mark_external(b, "正式:task/SevenDaySign", "已补充", "Task/日周活跃/七日签到正式奖励入口已登记。", count, "")


LEVEL_TYPE_TO_SYSTEM = {
    "LevelType_Main": ("主线", "正式普通主线"),
    "LevelType_None": ("主线", "正式序章"),
    "LevelType_SubLevel": ("主线", "正式支线关"),
    "LevelType_ExtraLevel": ("主线", "正式额外关"),
    "LevelType_Chest": ("主线", "正式章节宝箱关"),
    "LevelType_CircuitConnect": ("主线", "正式章节电路关"),
    "LevelType_Fish": ("主线", "正式章节钓鱼关"),
    "LevelType_Klotski": ("主线", "正式章节华容道关"),
    "LevelType_Question": ("主线", "正式章节答题关"),
    "LevelType_Main_Difficult": ("困难主线", "正式困难主线"),
    "LevelType_Gold": ("资源副本", "正式金币副本"),
    "LevelType_Exp": ("资源副本", "正式角色经验副本"),
    "LevelType_WeaponExp": ("资源副本", "正式专武经验副本"),
    "LevelType_Material_First": ("资源副本", "正式材料副本1"),
    "LevelType_Material_Second": ("资源副本", "正式材料副本2"),
    "LevelType_Material_Three": ("资源副本", "正式材料副本3"),
    "LevelType_WeaponMaterial_First": ("资源副本", "正式专武材料副本1"),
    "LevelType_WeaponMaterial_Second": ("资源副本", "正式专武材料副本2"),
    "LevelType_WeaponMaterial_Three": ("资源副本", "正式专武材料副本3"),
    "LevelType_EnergyEfficiency_First": ("资源副本", "正式能效副本1"),
    "LevelType_EnergyEfficiency_Second": ("资源副本", "正式能效副本2"),
    "LevelType_EnergyEfficiency_Three": ("资源副本", "正式能效副本3"),
    "LevelType_RvCabin": ("资源副本", "正式房车舱室副本"),
    "LevelType_Strategy_First": ("旅券副本", "正式旅券副本1"),
    "LevelType_Strategy_Second": ("旅券副本", "正式旅券副本2"),
    "LevelType_Strategy_Three": ("旅券副本", "正式旅券副本3"),
    "LevelType_Strategy_Four": ("旅券副本", "正式旅券副本4"),
    "LevelType_SpecialEquipment": ("映射装备副本", "正式映射装备副本"),
    "LevelType_SpecialEquipmentGem": ("映射装备副本", "正式映射装备宝石副本"),
    "LevelType_SpecialEquipmentChip": ("映射装备副本", "正式映射装备铭文副本"),
    "LevelType_Equip_First": ("映射装备副本", "正式装备副本1"),
    "LevelType_Equip_Second": ("映射装备副本", "正式装备副本2"),
    "LevelType_Equip_Three": ("映射装备副本", "正式装备副本3"),
    "LevelType_Equip_Four": ("映射装备副本", "正式装备副本4"),
}


def parse_formal_level_reward_refs(b):
    uilevel_path = cfg_path("level", "UIlevel.xlsx")
    chapter_star_path = cfg_path("level", "ChapterStarReward.xlsx")
    chapter_tasks_path = cfg_path("level", "ChapterTasks.xlsx")
    jottings_path = cfg_path("task", "Jottings.xlsx")
    jottings_task_path = cfg_path("task", "JottingsTask.xlsx")
    task_path = cfg_path("task", "Task.xlsx")
    drop_other_path = cfg_path("Drop", "Drop_other.xlsx")
    count = 0
    if os.path.exists(uilevel_path):
        rows = row_dicts(uilevel_path, "level")
        drop_entries = logical_drop_entries_by_id()
        expanded_rows = 0
        for row in rows:
            level_type = clean_text(row.get("LevelType"))
            if level_type not in LEVEL_TYPE_TO_SYSTEM:
                continue
            count += 1
            system, group = LEVEL_TYPE_TO_SYSTEM[level_type]
            chapter_id = to_int(row.get("ChapterId"))
            chapter_note = "｜章节%s" % (chapter_id - 10000) if chapter_id is not None and chapter_id >= 10000 else ""
            cond = "LevelId %s｜%s%s｜%s" % (
                clean_value(row.get("LevelId")), clean_text(row.get("Name")), chapter_note, level_type)
            for field, kind, period in [
                ("FirstRewardDrop", "首通", "一次性首通"),
                ("FallRewardDrop", "重复", "可重复通关"),
                ("ThreeStarRewardDrop", "三星", "一次性三星达成"),
                ("HighRewardDrop", "高额", "高额结算"),
            ]:
                drop_id = to_int(row.get(field))
                if drop_id is None:
                    continue
                entries = [
                    e for e in drop_entries.get(drop_id, [])
                    if not e["invalid"] and to_int(e.get("item_id")) not in (None, 0)
                    and to_num(e.get("qty")) not in (None, 0)
                ]
                if not entries:
                    add_drop_ref(b, system, "%s奖励引用" % group, "UIlevel.%s" % kind, drop_id,
                                 "正式:level/UIlevel.xlsx", row.get("_row"), condition=cond)
                    continue
                for entry in entries:
                    note = "UIlevel.%s=%s；来源 %s#%s。" % (field, drop_id, entry.get("source"), entry.get("row"))
                    b.add_reward(system, "%s%s奖励" % (group, kind), entry["item"], entry["qty"],
                                 "正式:level/UIlevel.xlsx + %s" % entry.get("source"),
                                 row.get("_row"), item_id=entry["item_id"], period=period,
                                 condition=cond, basis="正式UIlevel+Drop展开", note=note)
                    expanded_rows += 1
            add_formal_props(b, system, "%s体力消耗" % group, "消耗", row.get("Vitality"),
                             "正式:level/UIlevel.xlsx", row.get("_row"), period="关卡进入", condition=cond,
                             basis="正式UIlevel体力消耗")
        mark_external(
            b,
            "正式:level/UIlevel.xlsx",
            "已结构化",
            "主线/困难主线/资源副本/旅券副本/映射装备副本按正式UIlevel直读：关卡 %s 行，首通/重复/三星/高额Drop已逐项展开 %s 行（##停用与ItemId=0占位行不计）；未展开的Drop保留为引用。旧经济母表设计页不再作为这五个系统的产销源。" % (count, expanded_rows),
            count,
            "",
        )
        for sheet in ("主线副本", "高难主线关卡", "资源、装备副本", "旅券副本", "映射装备副本"):
            b.mark(sheet, "已由正式承接", "2026-09-04起该设计页口径停用；产销改读正式 level/UIlevel.xlsx + Drop 展开（当前游戏口径）。")
    if os.path.exists(chapter_star_path):
        rows = row_dicts(chapter_star_path)
        count += len(rows)
        for row in rows:
            cond = "ChapterId %s｜Star %s｜IsDifficult %s" % (
                clean_value(row.get("ChapterId")), clean_value(row.get("Star")), clean_value(row.get("IsDifficult")))
            add_drop_ref(b, "主线", "正式章节星级奖励", "ChapterStarReward.DropId", row.get("DropId"),
                         "正式:level/ChapterStarReward.xlsx", row.get("_row"), condition=cond)
    if os.path.exists(jottings_path) and os.path.exists(jottings_task_path) and os.path.exists(task_path):
        jottings_rows = row_dicts(jottings_path)
        jottings_task_rows = row_dicts(jottings_task_path)
        task_rows = row_dicts(task_path, "Task")
        jottings_task_by_id = {to_int(row.get("ID")): row for row in jottings_task_rows if to_int(row.get("ID")) is not None}
        task_by_id = {to_int(row.get("Id")): row for row in task_rows if to_int(row.get("Id")) is not None}
        drop_entries = drop_entries_by_id(drop_other_path)
        referenced_jottings_task_ids = set()
        for row in jottings_rows:
            jottings_task_ids = int_list(row.get("JottingsTasks"))
            referenced_jottings_task_ids.update(jottings_task_ids)
            task_ids = []
            for jt_id in jottings_task_ids:
                task_ids.extend(int_list(jottings_task_by_id.get(jt_id, {}).get("TaskID")))
            drop_id = to_int(row.get("DropID"))
            cond = "%s｜JottingsTask %s｜Task %s" % (
                clean_text(row.get("Name")), ";".join(str(v) for v in jottings_task_ids), ";".join(str(v) for v in task_ids))
            for entry in drop_entries.get(drop_id, []):
                note = "DropID %s；Jottings 阶段奖励，任务链来自 JottingsTask/Task。" % drop_id
                if entry["invalid"]:
                    note += " Drop_other 行当前为 ## 标记。"
                b.add_reward("主线", "正式章节任务阶段奖励", entry["item"], entry["qty"],
                             "正式:task/Jottings.xlsx + Drop_other.xlsx", row.get("_row"),
                             item_id=entry["item_id"], period="一次性", condition=cond,
                             basis="章节任务阶段奖励展开", note=note)
        candidate_ids = [jt_id for jt_id in sorted(jottings_task_by_id) if jt_id not in referenced_jottings_task_ids and 10 <= jt_id < 20]
        if candidate_ids:
            task_ids = []
            drop_ids = []
            for jt_id in candidate_ids:
                for task_id in int_list(jottings_task_by_id[jt_id].get("TaskID")):
                    task_ids.append(task_id)
                    drop_id = to_int(task_by_id.get(task_id, {}).get("DropId"))
                    if drop_id is not None and drop_id not in drop_ids:
                        drop_ids.append(drop_id)
            cond = "星海手札（序章，Jottings未配置）｜JottingsTask %s｜Task %s" % (
                ";".join(str(v) for v in candidate_ids), ";".join(str(v) for v in task_ids))
            for drop_id in drop_ids:
                for entry in drop_entries.get(drop_id, []):
                    note = "候选序章奖励；Jottings 未挂载，DropID %s 仅作待确认展示。" % drop_id
                    if entry["invalid"]:
                        note += " Drop_other 行当前为 ## 标记。"
                    b.add("主线", "候选章节任务序章奖励", "引用", entry["item"], entry["qty"], "",
                          entry["item_id"], "", "", "", "", "待确认", cond,
                          "正式:task/JottingsTask.xlsx + Drop_other.xlsx", "",
                          "章节任务候选奖励，未计为正式产出", note)
        count += len(jottings_rows)
    if os.path.exists(chapter_tasks_path):
        rows = row_dicts(chapter_tasks_path)
        count += len(rows)
        for row in rows:
            cond = "ChapterId %s｜TaskIdList %s" % (clean_value(row.get("ChapterId")), clean_text(row.get("TaskIdList")))
            add_drop_ref(b, "主线", "正式章节任务奖励", "ChapterTasks.DropId", row.get("DropId"),
                         "正式:level/ChapterTasks.xlsx", row.get("_row"), condition=cond,
                         note="旧 ChapterTasks 链路保留为异常参考；当前正确章节任务链来自 task/Jottings。")
    if count:
        mark_external(b, "正式:level/UIlevel/Chapter", "已补充", "主线/困难/资源/旅券/映射副本的正式 UIlevel Drop 引用、体力和章节奖励入口已登记。", count, "")


def parse_formal_drawcard(b):
    draw_path = cfg_path("Activity", "DrawCard", "DrawCard.xlsx")
    pool_path = cfg_path("Activity", "DrawCard", "DrawCardPool.xlsx")
    count = 0
    if os.path.exists(draw_path):
        rows = row_dicts(draw_path, "DrawCard")
        count += len(rows)
        for row in rows:
            cond = "DrawId %s｜%s" % (clean_value(row.get("Id")), clean_text(row.get("Name")))
            add_drop_ref(b, "抽卡", "正式卡池奖励", "DrawCard.DropId", row.get("DropId"),
                         "正式:Activity/DrawCard/DrawCard.xlsx", row.get("_row"), condition=cond)
            add_drop_ref(b, "抽卡", "正式十连保底", "DrawCard.TenDropId", row.get("TenDropId"),
                         "正式:Activity/DrawCard/DrawCard.xlsx", row.get("_row"), condition=cond)
            add_drop_ref(b, "抽卡", "正式小保底", "DrawCard.XiaoBaoDiId", row.get("XiaoBaoDiId"),
                         "正式:Activity/DrawCard/DrawCard.xlsx", row.get("_row"), condition=cond)
            add_drop_ref(b, "抽卡", "正式大保底", "DrawCard.DaBaoDiId", row.get("DaBaoDiId"),
                         "正式:Activity/DrawCard/DrawCard.xlsx", row.get("_row"), condition=cond)
            add_formal_props(b, "抽卡", "正式单抽消耗", "消耗", row.get("OnePrice"),
                             "正式:Activity/DrawCard/DrawCard.xlsx", row.get("_row"), condition=cond,
                             basis="正式DrawCard.OnePrice")
            add_formal_props(b, "抽卡", "正式十连消耗", "消耗", row.get("TenPrice"),
                             "正式:Activity/DrawCard/DrawCard.xlsx", row.get("_row"), condition=cond,
                             basis="正式DrawCard.TenPrice")
    if os.path.exists(pool_path):
        rows = row_dicts(pool_path, "DrawCardPool")
        count += len(rows)
        for row in rows:
            if row.get("Pool"):
                cond = "DrawId %s｜PoolType %s｜UpItem %s" % (
                    clean_value(row.get("DrawId")), clean_text(row.get("PoolType")), clean_value(row.get("UpItemId")))
                b.add("抽卡", "正式卡池内容", "引用", "卡池角色/道具池", clean_text(row.get("Pool")),
                      sheet="正式:Activity/DrawCard/DrawCardPool.xlsx", row=row.get("_row"),
                      condition=cond, basis="卡池内容引用，概率/保底另查 DrawCardWeight")
    if count:
        mark_external(b, "正式:Activity/DrawCard", "已补充", "正式 DrawCard 卡池、消耗、保底和卡池内容入口已登记。", count, "")


def parse_formal_guild(b):
    mission_path = cfg_path("Guild", "GuildMission.xlsx")
    commission_path = cfg_path("Guild", "GuildComission.xlsx")
    lv_path = cfg_path("Guild", "GuildLv.xlsx")
    building_path = cfg_path("Guild", "GuildBuilding.xlsx")
    bargaining_path = cfg_path("Guild", "GuildBargaining.xlsx")
    count = 0
    if os.path.exists(mission_path):
        rows = row_dicts(mission_path)
        count += len(rows)
        for row in rows:
            cond = "MissionId %s｜%s" % (clean_value(row.get("Id")), clean_text(row.get("Mission")))
            add_drop_ref(b, "公会", "正式公会任务", "GuildMission.Reward", row.get("Reward"),
                         "正式:Guild/GuildMission.xlsx", row.get("_row"), condition=cond)
    if os.path.exists(commission_path):
        rows = row_dicts(commission_path)
        count += len(rows)
        for row in rows:
            cond = "CommissionId %s｜Diff %s｜Time %s" % (
                clean_value(row.get("Id")), clean_value(row.get("CommissionDiff")), clean_value(row.get("CommissionTime")))
            add_drop_ref(b, "公会", "正式公会委托固定奖励", "GuildComission.Reward", row.get("Reward"),
                         "正式:Guild/GuildComission.xlsx", row.get("_row"), condition=cond)
            for drop_id in str(clean_text(row.get("RandomReward"))).split(";"):
                add_drop_ref(b, "公会", "正式公会委托随机奖励", "GuildComission.RandomReward", drop_id,
                             "正式:Guild/GuildComission.xlsx", row.get("_row"), condition=cond)
    if os.path.exists(lv_path):
        rows = row_dicts(lv_path)
        count += len(rows)
        for row in rows:
            if row.get("GuildWeeklyDropNum") not in ("", None):
                b.add_reward("公会", "正式公会等级", "公会周拍品掉落次数上限", row.get("GuildWeeklyDropNum"),
                             "正式:Guild/GuildLv.xlsx", row.get("_row"), period="每周",
                             condition="GuildLv %s" % clean_value(row.get("Level")),
                             basis="正式公会等级字段", note="GuildWeeklyDropNum")
    if os.path.exists(building_path):
        rows = row_dicts(building_path, "GuildBuilding")
        count += len(rows)
        for row in rows:
            if row.get("Price"):
                b.add("公会", "正式公会建筑", "引用", "公会建筑解锁价格", clean_text(row.get("Price")),
                      sheet="正式:Guild/GuildBuilding.xlsx", row=row.get("_row"),
                      condition="Building %s｜%s" % (clean_value(row.get("Id")), clean_text(row.get("Name"))),
                      basis="正式配置价格字段引用", note="Price")
    if os.path.exists(bargaining_path):
        rows = row_dicts(bargaining_path, "GuildBargaining")
        count += len(rows)
        for row in rows:
            cond = "BargainingId %s｜GuildMinLv %s" % (clean_value(row.get("Id")), clean_value(row.get("GuildMinLv")))
            add_formal_props(b, "公会", "正式公会议价商品", "产出", row.get("Goods"),
                             "正式:Guild/GuildBargaining.xlsx", row.get("_row"), condition=cond,
                             basis="正式公会议价商品")
            add_formal_props(b, "公会", "正式公会议价价格", "消耗", row.get("InitialPrice"),
                             "正式:Guild/GuildBargaining.xlsx", row.get("_row"), condition=cond,
                             basis="正式公会议价价格")
    if count:
        mark_external(b, "正式:Guild", "已补充", "公会任务、委托、等级、建筑、议价正式入口已登记。", count, "")


def parse_formal_legacy_equipment(b):
    equipment_level_path = cfg_path("level", "EquipmentLevel.xlsx")
    eqpt_lv_path = cfg_path("equipment", "EqptLv.xlsx")
    eqpt_star_path = cfg_path("equipment", "EqptStar.xlsx")
    eqpt_resolve_path = cfg_path("equipment", "EqptResolve.xlsx")
    eqpt_ascend_path = cfg_path("equipment", "EqptAscendMaterial.xlsx")
    count = 0
    if os.path.exists(equipment_level_path):
        rows = row_dicts(equipment_level_path, "EquipmentLevel")
        count += len(rows)
        for row in rows:
            b.add_ref("共鸣装备", "正式旧装备副本映射", "EquipmentLevel.UiLevelId", row.get("UiLevelId"),
                      "正式:level/EquipmentLevel.xlsx", row.get("_row"),
                      condition="Quality %s｜LevelId %s" % (clean_text(row.get("EquipmentQuality")), clean_value(row.get("LevelId"))),
                      note="旧 equipment 入口，需确认是否当前正式。")
    if os.path.exists(eqpt_lv_path):
        rows = row_dicts(eqpt_lv_path)
        count += len(rows)
        for row in rows:
            if row.get("UpgradeCostExp"):
                b.add_cost("共鸣装备", "正式旧装备升级", "旧装备经验", row.get("UpgradeCostExp"),
                           "正式:equipment/EqptLv.xlsx", row.get("_row"),
                           condition="Quality %s｜Lv %s" % (clean_value(row.get("Quality")), clean_value(row.get("Lv"))),
                           note="旧 equipment 入口，需确认是否当前正式。")
    for path, label, fields in [
        (eqpt_star_path, "正式旧装备升星", ["StarCostItem", "ItemCost"]),
        (eqpt_ascend_path, "正式旧装备突破", ["ItemConsume", "ItemCost"]),
    ]:
        if os.path.exists(path):
            rows = row_dicts(path)
            count += len(rows)
            for row in rows:
                cond = "Quality %s｜Star/Ascend %s/%s" % (
                    clean_value(row.get("Quality")), clean_value(row.get("Star")), clean_value(row.get("AscendId")))
                for field in fields:
                    add_formal_props(b, "共鸣装备", label, "消耗", row.get(field),
                                     "正式:%s" % os.path.relpath(path, CONFIG_ROOT).replace("\\", "/"),
                                     row.get("_row"), condition=cond, note="旧 equipment 入口，需确认是否当前正式。")
    if os.path.exists(eqpt_resolve_path):
        rows = row_dicts(eqpt_resolve_path)
        count += len(rows)
        for row in rows:
            add_formal_props(b, "共鸣装备", "正式旧装备分解", "产出", row.get("ResolveGetItem"),
                             "正式:equipment/EqptResolve.xlsx", row.get("_row"),
                             condition="Quality %s｜Star %s" % (clean_value(row.get("Quality")), clean_value(row.get("Star"))),
                             note="旧 equipment 入口，需确认是否当前正式。")
    if count:
        mark_external(b, "正式:level/EquipmentLevel+equipment", "已补充入口/待确认正式性",
                      "按用户回答补充共鸣装备候选入口；该链路属于旧 equipment，是否当前正式仍需最终裁决。", count, "")


def finalize_coverage(b):
    mirrored = {
        "角色、专武、旅券掉落池": "P4a 已镜像；概率池/价值工具页首版不展开为总账明细。",
        "讨论页-玩法定位和产出": "P4a 已镜像；作为玩法经济职责知识页保留。",
    }
    pending = {
        "前7天钻石抽卡券统计": "统计复盘页，未作为源头产销表。",
        "玩法钻石抽卡券统计": "统计复盘页，未作为源头产销表。",
        "角色养成汇总": "汇总页，明细已从角色升级/升阶/星盘等页读取。",
        "映射装备": "含宝石合成/装备升级/分解等复杂链路，首版待单独深挖。",
        "主角等级（从新手引导复制）": "节奏层已有主角等级单源；经济层首版不重复读取。",
        "配置页-主线副本": "关卡配置导出页，首版先从主线副本设计页登记奖励。",
        "高难关卡Drop引用&Drop配置": "Drop 引用与包内容待奖励同步链路展开。",
        "无限挑战": "设计说明页；奖励明细已从配置页-无限挑战登记。",
        "竞技场": "设计说明页；奖励明细已从配置页-竞技场登记。",
        "竞技场分层": "分层测算页，难度/竞技分层已在节奏层处理；经济层首版不作为产销源。",
        "爬塔": "设计说明/测算页；奖励明细已改读 06_最终配置/爬塔 评审镜像（CHG-044）。",
        "映射装备副本配置": "配置导出页，首版先从映射装备副本设计页登记期望奖励。",
        "肉鸽（废弃）": "废弃玩法，不纳入当前正式经济层。",
    }
    for sheet, note in mirrored.items():
        if sheet in b.wb.sheetnames:
            b.mark(sheet, "已镜像", note)
    for sheet, note in pending.items():
        if sheet in b.wb.sheetnames and sheet not in b.coverage:
            status = "不纳入" if "废弃" in note else "待深挖/已由其他页承接"
            b.mark(sheet, status, note)
    for sheet in b.wb.sheetnames:
        if sheet not in b.coverage:
            ws = b.wb[sheet]
            b.coverage[sheet] = [sheet, ws.max_row, ws.max_column, "待深挖", "首版未结构化，需后续按系统单独确认。"]


def build_summary_rows(b):
    stats = {}
    systems = defaultdict(set)
    for row in b.ledger:
        key = (row["资源/道具"], row["道具ID"], row["方向"])
        if key not in stats:
            stats[key] = {"count": 0, "qty": 0, "qty_addable": True, "value": 0, "value_addable": True}
        s = stats[key]
        s["count"] += 1
        systems[key].add(str(row["系统"]))
        qty = row["数量"]
        value = row["价值(钻石)"]
        if is_num(qty):
            s["qty"] += qty
        elif qty not in ("", None):
            s["qty_addable"] = False
        if is_num(value):
            s["value"] += value
        elif value not in ("", None):
            s["value_addable"] = False
    rows = []
    for key, s in sorted(stats.items(), key=lambda item: (str(item[0][0]), str(item[0][2]))):
        qty = round(s["qty"], 6) if s["qty_addable"] else "含区间/非数值"
        value = round(s["value"], 6) if s["value_addable"] else "含非数值"
        rows.append([key[0], key[1], key[2], s["count"], qty, value, "、".join(sorted(systems[key]))[:120]])
    return rows


def exclude_stat_only_resources(b):
    kept = []
    excluded = []
    for row in b.ledger:
        if clean_text(row.get("资源/道具")) in STAT_ONLY_RESOURCES:
            excluded.append(row)
        else:
            kept.append(row)
    b.ledger = kept
    b.stat_excluded_counts = Counter(clean_text(row.get("资源/道具")) for row in excluded)
    for row in excluded:
        row["口径"] = "统计口径:经验计算值（仅人读展示，不入总表/资源汇总）"
        old_note = clean_text(row.get("备注"))
        row["备注"] = "仅用于升级成本阅读，不作为实物道具统计%s" % ("；%s" % old_note if old_note else "")
    b.stat_only_rows = excluded
    if excluded:
        detail = "；".join("%s:%s行" % (name, count) for name, count in sorted(b.stat_excluded_counts.items()))
        mark_external(
            b,
            "统计口径:经验计算值",
            "已排除",
            "角色经验/专武经验为升级经验计算口径，不是实物道具；从产销统计中排除，保留角色经验高/专武经验高等真实道具。%s" % detail,
            len(excluded),
            "",
        )


def exclude_policy_systems(b):
    kept = []
    deprecated = []
    non_ledger = []
    for row in b.ledger:
        system = clean_text(row.get("系统"))
        if system in DEPRECATED_ECONOMY_SYSTEMS:
            deprecated.append(row)
        elif system in NON_LEDGER_SYSTEMS:
            non_ledger.append(row)
        else:
            kept.append(row)
    b.ledger = kept
    b.deprecated_excluded_counts = Counter(clean_text(row.get("系统")) for row in deprecated)
    b.non_ledger_excluded_counts = Counter(clean_text(row.get("系统")) for row in non_ledger)
    if deprecated:
        if "共鸣装备" in b.coverage:
            b.coverage["共鸣装备"][3] = "废弃/不纳入"
            b.coverage["共鸣装备"][4] = "用户裁决：共鸣装备已废弃，已从产销统计和炮台模块中移除。"
        mark_external(
            b,
            "统计口径:废弃系统",
            "已排除",
            "用户裁决：共鸣装备已废弃，不纳入当前产销统计；炮台养成仅保留炮台自身升级/突破材料。",
            len(deprecated),
            "",
        )
        mark_external(
            b,
            "正式:legacy equipment",
            "废弃/不纳入",
            "共鸣装备/旧 equipment 入口已按废弃系统处理，不再进入产销模块。",
            len(deprecated),
            "",
        )
    if non_ledger:
        mark_external(
            b,
            "统计口径:抽卡概率",
            "概率表承接/不纳入产销",
            "抽卡不计算产销消耗；正式 DrawCard/DrawCardPool 改由模块内抽卡概率表承接。",
            len(non_ledger),
            "",
        )
        mark_external(
            b,
            "正式:Activity/DrawCard",
            "概率表承接/不纳入产销",
            "抽卡正式配置不再写入产销明细，改输出完整卡池概率、保底与权重信息。",
            len(non_ledger),
            "",
        )


def write_sheet(wb, title, headers, rows):
    ws = wb.create_sheet(title)
    ws.append(headers)
    header_fill = PatternFill("solid", fgColor="D9E1F2")
    bold = Font(bold=True)
    for cell in ws[1]:
        cell.font = bold
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row in rows:
        if isinstance(row, dict):
            ws.append([clean_value(row.get(h, "")) for h in headers])
        else:
            ws.append([clean_value(v) for v in row])
    ws.freeze_panes = "A2"
    widths = [16, 18, 10, 20, 10, 14, 14, 16, 12, 14, 12, 16, 26, 18, 10, 28, 36]
    for idx, width in enumerate(widths[:len(headers)], start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    return ws


SPLIT_DEFS = [
    ("玩法_主线", ["主线"], "正式UIlevel普通主线/序章/支线/章节玩法关的首通/重复/三星/高额奖励展开与体力；章节任务独立模块。"),
    ("玩法_困难主线", ["困难主线"], "正式UIlevel困难主线首通/重复奖励展开与体力。"),
    ("玩法_资源副本", ["资源副本"], "正式UIlevel金币/经验/专武经验/材料/专武材料/能效/房车舱室副本奖励展开；经验计算值不计入道具产销。"),
    ("玩法_旅券副本", ["旅券副本"], "正式UIlevel旅券副本1-4首通/重复奖励展开。"),
    ("玩法_映射副本", ["映射装备副本"], "正式UIlevel映射装备/宝石/铭文副本首通/重复奖励展开。"),
    ("玩法_无限挑战", ["无限挑战"], "无限挑战/无限之旅生涯奖励、正式 neural_roam 最高分奖励与玩法积分。"),
    ("玩法_竞技场", ["竞技场(PVPVE)"], "竞技场单场胜负、14天赛季累胜、首次到达、赛季结算、排行结算和商店。"),
    ("玩法_爬塔", ["爬塔"], "账号级1-100层一次性首通（CHG-044：元晶/熔晶/旅券/房车零件/自选箱/指南材料）与按历史最高层挂机产出；旧每周到达、通关/扫荡、商店与赛季奖励已删除。"),
    ("玩法_大秘境", ["大秘境"], "大秘境周层数、周积分、赛季积分和排行奖励。"),
    ("玩法_BOSS挑战", ["BOSS挑战"], "Boss 挑战正式7个boss的一次性通关奖励展开；BestReward 作为最高奖励预览引用。"),
    ("外循环_任务", ["任务", "7日任务"], "每日/每周/阶段任务与新手 7 日任务。"),
    ("外循环_签到", ["签到"], "每日签到、累计签到、生涯累计签到奖励。"),
    ("外循环_通行证", ["通行证"], "通行证免费线、付费线和 RewardId 引用。"),
    ("外循环_商店公会", ["商店", "公会"], "通用商店、公会任务、派遣和公会商店。"),
    ("养成_角色", ["角色养成"], "角色升级、升阶、星盘消耗。"),
    ("养成_专武", ["专武养成"], "专武升级、突破、升星消耗。"),
    ("养成_旅券", ["旅券养成"], "旅券正式升级、分解、制作和商店消耗。"),
    ("养成_映射装备", ["映射装备养成"], "映射装备正式升级、鉴定、打孔、品质额外道具和词条池入口。"),
    ("养成_炮台", ["炮台养成"], "炮台逐级升级与节点突破材料；共鸣装备已废弃，不纳入产销。"),
    ("养成_房车", ["房车养成"], "房车整备逐级强化与出行指南职业节点消耗。"),
    ("抽卡_概率", [], "抽卡不计算产销消耗，仅输出正式卡池概率、保底和权重。"),
    ("外循环_章节任务", ["主线"], "主线章节任务链与章节任务完成奖励入口，来自正式 Jottings/JottingsTask/Task，并保留旧 ChapterTasks 异常参考。"),
]

TABLE_NAME_BY_TITLE = {
    "玩法_主线": "mainline",
    "外循环_章节任务": "chapter_task",
    "玩法_困难主线": "hard_mainline",
    "玩法_资源副本": "resource_dungeon",
    "玩法_旅券副本": "voucher_dungeon",
    "玩法_映射副本": "mapping_dungeon",
    "玩法_无限挑战": "infinite_challenge",
    "玩法_竞技场": "arena",
    "玩法_爬塔": "tower",
    "玩法_大秘境": "mythic",
    "玩法_BOSS挑战": "boss_challenge",
    "外循环_任务": "task",
    "外循环_签到": "signin",
    "外循环_通行证": "battlepass",
    "外循环_商店公会": "shop_guild",
    "养成_角色": "growth_hero",
    "养成_专武": "growth_weapon",
    "养成_旅券": "growth_voucher",
    "养成_映射装备": "growth_mapping_equipment",
    "养成_炮台": "growth_turret",
    "养成_房车": "growth_rv",
    "抽卡_概率": "gacha_probability",
}

DISPLAY_SYSTEMS_BY_TITLE = {
    "外循环_章节任务": ["章节任务"],
    "抽卡_概率": ["抽卡概率"],
}


def split_row(row):
    return [
        row["分组"],
        row["方向"],
        row["资源/道具"],
        row["数量"],
        row["价值(钻石)"],
        row["货币/成本"],
        row["货币数量"],
        row["周期/限制"],
        row["进度/条件"],
        row["来源页"],
        row["来源行"],
        row["口径"],
        row["备注"],
    ]


def is_chapter_task_row(row):
    source = row["来源页"]
    group = row["分组"]
    return (
        source == "正式:level/ChapterTasks.xlsx"
        or "Jottings" in source
        or group in ("正式章节任务奖励", "正式章节任务阶段奖励", "候选章节任务序章奖励")
    )


def rows_for_split(b, title, systems):
    wanted = set(systems)
    rows = [row for row in b.ledger if row["系统"] in wanted]
    if title == "玩法_主线":
        return [row for row in rows if not is_chapter_task_row(row)]
    if title == "外循环_章节任务":
        return [row for row in rows if is_chapter_task_row(row)]
    return rows


def display_systems(title, systems):
    return DISPLAY_SYSTEMS_BY_TITLE.get(title, systems)


def split_metrics(rows):
    direction_counts = defaultdict(int)
    value_by_direction = defaultdict(float)
    value_non_numeric = defaultdict(int)
    resources = set()
    source_sheets = set()
    for row in rows:
        direction_counts[row["方向"]] += 1
        resources.add(row["资源/道具"])
        source_sheets.add(row["来源页"])
        value = row["价值(钻石)"]
        if is_num(value):
            value_by_direction[row["方向"]] += value
        elif value not in ("", None):
            value_non_numeric[row["方向"]] += 1
    return {
        "direction_counts": dict(direction_counts),
        "value_by_direction": dict(value_by_direction),
        "value_non_numeric": dict(value_non_numeric),
        "resource_count": len(resources),
        "source_count": len(source_sheets),
    }


def write_split_sheet(wb, title, rows, note):
    ws = wb.create_sheet(title)
    metrics = split_metrics(rows)
    ws.append([title, note])
    ws.append(["记录数", len(rows), "资源数", metrics["resource_count"], "来源页数", metrics["source_count"]])
    ws.append([
        "方向分布",
        "；".join("%s:%s" % (k, v) for k, v in sorted(metrics["direction_counts"].items())),
        "价值合计",
        "；".join("%s:%s" % (k, round(v, 2)) for k, v in sorted(metrics["value_by_direction"].items())),
    ])
    ws.append([])
    ws.append(SPLIT_HEADERS)

    title_font = Font(bold=True, size=13)
    header_fill = PatternFill("solid", fgColor="D9E1F2")
    sub_fill = PatternFill("solid", fgColor="E2EFDA")
    ws.cell(1, 1).font = title_font
    for cell in ws[5]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in rows:
        ws.append([clean_value(v) for v in split_row(row)])
        if row["方向"] == "消耗":
            ws.cell(ws.max_row, 2).fill = PatternFill("solid", fgColor="FCE4D6")
        elif row["方向"] == "产出":
            ws.cell(ws.max_row, 2).fill = sub_fill
        elif row["方向"] == "引用":
            ws.cell(ws.max_row, 2).fill = PatternFill("solid", fgColor="FFF2CC")

    ws.freeze_panes = "A6"
    widths = [18, 10, 22, 14, 14, 18, 12, 16, 32, 18, 10, 28, 38]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    return ws


def safe_table_name(title, idx):
    if title in TABLE_NAME_BY_TITLE:
        return "T%02d_%s" % (idx, TABLE_NAME_BY_TITLE[title])
    text = re.sub(r"[^0-9A-Za-z_]", "_", title)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text or text[0].isdigit():
        text = "T_%s" % text
    return "T%02d_%s" % (idx, text[:40])


def write_split_tables_sheet(wb, split_rows_by_title):
    ws = wb.create_sheet("模块拆表")
    title_font = Font(bold=True, size=13)
    header_fill = PatternFill("solid", fgColor="D9E1F2")
    title_fill = PatternFill("solid", fgColor="1F4E79")
    title_font_white = Font(bold=True, color="FFFFFF", size=12)
    metric_fill = PatternFill("solid", fgColor="E2EFDA")
    style = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)

    ws.append(["P4 经济层 · 模块拆表", "所有玩法/外循环/养成资源先按模块拆成独立表格，最后看总汇总_资源。"])
    ws.cell(1, 1).font = title_font
    ws.append([])
    ws.append(["模块", "系统", "记录数", "资源数", "方向分布", "价值分布(钻石)", "说明"])
    for cell in ws[3]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    overview_start = 4
    for title, systems, note in SPLIT_DEFS:
        rows = split_rows_by_title[title]
        metrics = split_metrics(rows)
        shown_systems = display_systems(title, systems)
        ws.append([
            title,
            "、".join(shown_systems),
            len(rows),
            metrics["resource_count"],
            "；".join("%s:%s" % (k, v) for k, v in sorted(metrics["direction_counts"].items())),
            "；".join("%s:%s" % (k, round(v, 2)) for k, v in sorted(metrics["value_by_direction"].items())),
            note,
        ])
    overview_end = ws.max_row
    overview_table = Table(displayName="T00_split_overview", ref="A3:G%s" % overview_end)
    overview_table.tableStyleInfo = style
    ws.add_table(overview_table)

    current_row = overview_end + 3
    for idx, (title, systems, note) in enumerate(SPLIT_DEFS, start=1):
        rows = split_rows_by_title[title]
        metrics = split_metrics(rows)
        shown_systems = display_systems(title, systems)
        ws.cell(current_row, 1, title)
        ws.cell(current_row, 2, note)
        ws.cell(current_row, 1).font = title_font_white
        ws.cell(current_row, 2).font = Font(color="FFFFFF")
        for c in range(1, len(SPLIT_HEADERS) + 1):
            ws.cell(current_row, c).fill = title_fill
        current_row += 1
        ws.cell(current_row, 1, "记录数")
        ws.cell(current_row, 2, len(rows))
        ws.cell(current_row, 3, "资源数")
        ws.cell(current_row, 4, metrics["resource_count"])
        ws.cell(current_row, 5, "方向")
        ws.cell(current_row, 6, "；".join("%s:%s" % (k, v) for k, v in sorted(metrics["direction_counts"].items())))
        ws.cell(current_row, 7, "价值")
        ws.cell(current_row, 8, "；".join("%s:%s" % (k, round(v, 2)) for k, v in sorted(metrics["value_by_direction"].items())))
        for c in range(1, 9):
            ws.cell(current_row, c).fill = metric_fill
        current_row += 1
        header_row = current_row
        for col, header in enumerate(SPLIT_HEADERS, start=1):
            ws.cell(header_row, col, header)
            ws.cell(header_row, col).font = Font(bold=True)
            ws.cell(header_row, col).fill = header_fill
            ws.cell(header_row, col).alignment = Alignment(horizontal="center", vertical="center")
        current_row += 1
        for row in rows:
            for col, value in enumerate(split_row(row), start=1):
                ws.cell(current_row, col, clean_value(value))
            if row["方向"] == "消耗":
                ws.cell(current_row, 2).fill = PatternFill("solid", fgColor="FCE4D6")
            elif row["方向"] == "产出":
                ws.cell(current_row, 2).fill = PatternFill("solid", fgColor="E2EFDA")
            elif row["方向"] == "引用":
                ws.cell(current_row, 2).fill = PatternFill("solid", fgColor="FFF2CC")
            current_row += 1
        last_row = current_row - 1
        table = Table(displayName=safe_table_name(title, idx),
                      ref="A%s:%s%s" % (header_row, openpyxl.utils.get_column_letter(len(SPLIT_HEADERS)), last_row))
        table.tableStyleInfo = style
        ws.add_table(table)
        current_row += 2

    ws.freeze_panes = "A4"
    widths = [18, 14, 22, 14, 14, 18, 12, 16, 32, 18, 10, 28, 38]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    return ws


def safe_filename(title, idx):
    text = re.sub(r'[<>:"/\\|?*]+', "_", title).strip("._ ")
    if not text:
        text = "module"
    return "%02d_%s.xlsx" % (idx, text[:80])


def clean_module_dir():
    os.makedirs(MODULE_DIR, exist_ok=True)
    for name in os.listdir(MODULE_DIR):
        if name.startswith("~$"):
            continue
        path = os.path.join(MODULE_DIR, name)
        if os.path.isfile(path) and name.lower().endswith(".xlsx"):
            try:
                os.remove(path)
            except PermissionError:
                MODULE_WRITE_WARNINGS.append("模块旧文件被占用，保留原文件: %s" % path)


MODULE_HEAD_FILL = PatternFill("solid", fgColor="1F4E78")
MODULE_SUB_FILL = PatternFill("solid", fgColor="D9EAF7")
MODULE_METRIC_FILL = PatternFill("solid", fgColor="E2EFDA")
MODULE_WARN_FILL = PatternFill("solid", fgColor="FFF2CC")
MODULE_COST_FILL = PatternFill("solid", fgColor="FCE4D6")
MODULE_REF_FILL = PatternFill("solid", fgColor="FFF2CC")
MODULE_THIN = Side(style="thin", color="D9E2F3")
MODULE_BORDER = Border(left=MODULE_THIN, right=MODULE_THIN, top=MODULE_THIN, bottom=MODULE_THIN)


def readable_text(value):
    if value is None:
        return ""
    if is_num(value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return ("%.4f" % value).rstrip("0").rstrip(".")
    text = str(value).strip()
    if text in ERROR_VALUES or text == "None":
        return ""
    return text


def natural_sort_key(value):
    text = readable_text(value)
    parts = re.split(r"(\d+(?:\.\d+)?)", text)
    key = []
    for part in parts:
        if part == "":
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", part):
            num = float(part)
            key.append((0, int(num) if num.is_integer() else num))
        else:
            key.append((1, part.lower()))
    return tuple(key)


def readable_row_sort_key(row):
    return (
        natural_sort_key(row.get("系统")),
        natural_sort_key(row.get("分组")),
        natural_sort_key(row.get("周期/限制")),
        natural_sort_key(row.get("条件/阶段")),
        natural_sort_key(row.get("来源")),
    )


def ledger_row_sort_key(row):
    return (
        natural_sort_key(row.get("系统")),
        natural_sort_key(row.get("分组")),
        natural_sort_key(row.get("周期/限制")),
        natural_sort_key(row.get("进度/条件")),
        natural_sort_key(row.get("来源页")),
        natural_sort_key(row.get("来源行")),
        natural_sort_key(row.get("资源/道具")),
    )


def machine_row_sort_key(row):
    return (
        natural_sort_key(row.get("分组")),
        natural_sort_key(row.get("周期/限制")),
        natural_sort_key(row.get("进度/条件")),
        natural_sort_key(row.get("来源页")),
        natural_sort_key(row.get("来源行")),
        natural_sort_key(row.get("方向")),
        natural_sort_key(row.get("资源/道具")),
    )


def fmt_num(value):
    num = to_num(value)
    if num is None:
        return readable_text(value)
    if isinstance(num, float) and not num.is_integer():
        return ("%.2f" % num).rstrip("0").rstrip(".")
    return str(int(num))


def readable_item_text(name, item_id="", qty="", prefix=""):
    name = readable_text(name)
    item_id = readable_text(item_id)
    qty = readable_text(qty)
    base = name or ("ItemId %s" % item_id if item_id else "")
    if item_id:
        base = "%s(%s)" % (base, item_id)
    if qty:
        base = "%s x%s" % (base, fmt_num(qty))
    if prefix:
        return "%s：%s" % (prefix, base)
    return base


def compact_list(values, limit=8, show_counts=True):
    values = [readable_text(v) for v in values if readable_text(v)]
    if not values:
        return ""
    counts = Counter(values)
    ordered = []
    for value, count in counts.most_common():
        ordered.append("%s%s" % (value, " x%s" % count if show_counts and count > 1 else ""))
    if len(ordered) > limit:
        ordered = ordered[:limit] + ["另%s项" % (len(ordered) - limit)]
    return "；".join(ordered)


def module_category_of(row):
    text = " ".join(readable_text(row.get(key)) for key in ("资源/道具", "道具ID", "系统", "分组", "口径"))
    if any(key in text for key in ("钻石", "金币", "元晶", "储能", "体力")):
        return "基础货币/体力"
    if any(key in text for key in ("抽卡", "招募", "收容凭证", "券", "票")):
        return "抽卡/角色获取"
    if any(key in text for key in ("经验", "升级", "突破", "星盘", "旅券", "映射", "装备", "宝石", "材料", "炮台", "共鸣")):
        return "养成材料"
    if any(key in text for key in ("积分", "代币", "勋章", "贡献", "货币")):
        return "外循环代币"
    if readable_text(row.get("方向")) == "引用":
        return "奖励包/配置引用"
    return "其他资源"


def module_risk_tags(rows):
    text = " ".join(readable_text(value) for row in rows for value in row.values())
    tags = []
    if any(key in text for key in ("钻石", "元晶", "抽卡", "付费")):
        tags.append("高敏感")
    if any(key in text for key in ("每日", "每周", "赛季", "限购", "不限购", "可重复", "BuyLimit")):
        tags.append("周期/重复")
    if any(readable_text(row.get("方向")) == "引用" for row in rows):
        tags.append("需展开Drop/Reward")
    if any(key in text for key in ("随机", "权重", "Drop", "RewardId", "DropId")):
        tags.append("随机/引用")
    return "；".join(tags) if tags else "常规"


def grouped_item_text(row):
    return readable_item_text(
        row.get("资源/道具"),
        row.get("道具ID"),
        row.get("数量"),
        readable_text(row.get("分组")),
    )


def cost_item_text(row):
    if readable_text(row.get("方向")) == "消耗":
        return grouped_item_text(row)
    cost_name = readable_text(row.get("货币/成本"))
    cost_qty = readable_text(row.get("货币数量"))
    if cost_name or cost_qty:
        return readable_item_text(cost_name, "", cost_qty, readable_text(row.get("分组")))
    return ""


def summarize_items(rows, direction, limit=8):
    grouped = defaultdict(lambda: {"qty": 0.0, "numeric": True, "count": 0, "name": "", "id": ""})
    for row in rows:
        if readable_text(row.get("方向")) != direction:
            continue
        key = (readable_text(row.get("资源/道具")), readable_text(row.get("道具ID")))
        rec = grouped[key]
        rec["name"], rec["id"] = key
        rec["count"] += 1
        qty = to_num(row.get("数量"))
        if qty is None:
            rec["numeric"] = False
        else:
            rec["qty"] += qty
    ordered = sorted(grouped.values(), key=lambda rec: (-rec["count"], rec["name"], rec["id"]))
    parts = []
    for rec in ordered[:limit]:
        label = readable_item_text(rec["name"], rec["id"])
        if rec["numeric"] and rec["qty"]:
            label += " 合计x%s" % fmt_num(rec["qty"])
        else:
            label += " %s条" % rec["count"]
        parts.append(label)
    if len(ordered) > limit:
        parts.append("另%s项" % (len(ordered) - limit))
    return "；".join(parts)


def aggregate_module_readable_rows(rows):
    buckets = defaultdict(list)
    for row in rows:
        key = (
            readable_text(row.get("系统")),
            readable_text(row.get("周期/限制")),
            readable_text(row.get("进度/条件")),
            readable_text(row.get("来源页")),
            readable_text(row.get("来源行")),
        )
        buckets[key].append(row)

    out = []
    for key, group_rows in buckets.items():
        system, period, condition, source, source_row = key
        rewards = [grouped_item_text(row) for row in group_rows if readable_text(row.get("方向")) == "产出"]
        costs = [cost_item_text(row) for row in group_rows if readable_text(row.get("方向")) == "消耗"]
        if not costs:
            costs = [cost_item_text(row) for row in group_rows if cost_item_text(row)]
        refs = [grouped_item_text(row) for row in group_rows if readable_text(row.get("方向")) == "引用"]
        notes = [readable_text(row.get("备注")) for row in group_rows if readable_text(row.get("备注"))]
        basis = [readable_text(row.get("口径")) for row in group_rows if readable_text(row.get("口径"))]
        groups = [readable_text(row.get("分组")) for row in group_rows if readable_text(row.get("分组"))]
        out.append({
            "系统": system,
            "分组": compact_list(groups, 6, show_counts=False),
            "周期/限制": period,
            "条件/阶段": condition,
            "获得/产出": compact_list(rewards, 12),
            "消耗/花费": compact_list(costs, 12),
            "奖励包/引用": compact_list(refs, 8),
            "来源": "%s%s" % (source, ":%s" % source_row if source_row else ""),
            "口径": compact_list(basis, 4, show_counts=False),
            "备注": compact_list(notes, 4, show_counts=False),
        })
    return sorted(out, key=readable_row_sort_key)


def build_module_resource_rows(rows):
    grouped = defaultdict(list)
    for row in rows:
        key = (
            readable_text(row.get("资源/道具")),
            readable_text(row.get("道具ID")),
            readable_text(row.get("方向")),
        )
        grouped[key].append(row)

    out = []
    for (name, item_id, direction), group_rows in grouped.items():
        qty_total = 0.0
        qty_numeric = True
        value_total = 0.0
        value_numeric = True
        for row in group_rows:
            qty = to_num(row.get("数量"))
            if qty is None:
                if readable_text(row.get("数量")):
                    qty_numeric = False
            else:
                qty_total += qty
            value = to_num(row.get("价值(钻石)"))
            if value is None:
                if readable_text(row.get("价值(钻石)")):
                    value_numeric = False
            else:
                value_total += value
        out.append({
            "资源分类": module_category_of(group_rows[0]),
            "资源/道具": name,
            "道具ID": item_id,
            "方向": direction,
            "记录数": len(group_rows),
            "数量合计": fmt_num(qty_total) if qty_numeric else "含区间/非数值",
            "价值合计(钻石)": fmt_num(value_total) if value_numeric else "含非数值",
            "出现位置": compact_list([readable_text(row.get("分组")) for row in group_rows], 8),
            "来源页": compact_list([readable_text(row.get("来源页")) for row in group_rows], 8),
            "阅读提示": module_risk_tags(group_rows),
        })
    return sorted(out, key=lambda row: (row["资源分类"], row["方向"], -int(row["记录数"]), row["资源/道具"]))


def append_table_sheet(wb, title, headers, rows, widths, table_name=None, direction_col=None):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = MODULE_HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = MODULE_BORDER
    for row in rows:
        if isinstance(row, dict):
            values = [clean_value(row.get(header, "")) for header in headers]
        else:
            values = [clean_value(value) for value in row]
        ws.append(values)
        if direction_col:
            direction = readable_text(ws.cell(ws.max_row, direction_col).value)
            if direction == "产出":
                ws.cell(ws.max_row, direction_col).fill = MODULE_METRIC_FILL
            elif direction == "消耗":
                ws.cell(ws.max_row, direction_col).fill = MODULE_COST_FILL
            elif direction == "引用":
                ws.cell(ws.max_row, direction_col).fill = MODULE_REF_FILL
    ws.freeze_panes = "A2"
    if ws.max_row >= 1:
        ws.auto_filter.ref = ws.dimensions
    if table_name and rows:
        last_col = openpyxl.utils.get_column_letter(len(headers))
        table = Table(displayName=table_name, ref="A1:%s%s" % (last_col, ws.max_row))
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False,
                                              showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        ws.add_table(table)
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = MODULE_BORDER
    return ws


def human_freeze_pane(headers):
    if headers[:4] == ["阶段/条件", "奖励/产出类型", "周期/限制", "奖励包/引用"]:
        freeze_cols = 4
    elif headers[:3] == ["阶段/条件", "分组", "周期/限制"]:
        freeze_cols = 3
    elif "商品ID/条件" in headers:
        freeze_cols = headers.index("商品ID/条件") + 1
    elif "周期/限制" in headers:
        freeze_cols = headers.index("周期/限制") + 1
    else:
        freeze_cols = 0
    if freeze_cols == 0:
        freeze_cols = min(2, len(headers))
    freeze_cols = min(freeze_cols, max(1, len(headers) - 1))
    return openpyxl.utils.get_column_letter(freeze_cols + 1) + "4"


def append_human_table_sheet(wb, title, subtitle, headers, rows, widths, table_name=None):
    ws = wb.create_sheet(title)
    ws.append([title, subtitle])
    ws.cell(1, 1).font = Font(bold=True, color="FFFFFF", size=13)
    ws.cell(1, 2).font = Font(color="FFFFFF")
    for col_idx in range(1, max(3, min(len(headers), 10)) + 1):
        ws.cell(1, col_idx).fill = MODULE_HEAD_FILL
        ws.cell(1, col_idx).border = MODULE_BORDER
    ws.append([])
    ws.append(headers)
    header_row = 3
    for cell in ws[header_row]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = MODULE_HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = MODULE_BORDER
    for row in rows:
        if isinstance(row, dict):
            values = [clean_value(row.get(header, "")) for header in headers]
        else:
            values = [clean_value(value) for value in row]
            if len(values) < len(headers):
                values += [""] * (len(headers) - len(values))
        ws.append(values[:len(headers)])
    ws.freeze_panes = human_freeze_pane(headers)
    if table_name and rows:
        last_col = openpyxl.utils.get_column_letter(len(headers))
        table = Table(displayName=table_name, ref="A3:%s%s" % (last_col, ws.max_row))
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False,
                                              showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        ws.add_table(table)
    ws.auto_filter.ref = "A3:%s%s" % (openpyxl.utils.get_column_letter(len(headers)), max(ws.max_row, 3))
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = MODULE_BORDER
    return ws


MODULE_READABLE_HEADERS = ["系统", "分组", "周期/限制", "条件/阶段", "获得/产出", "消耗/花费", "奖励包/引用", "来源", "口径", "备注"]
MODULE_READABLE_WIDTHS = [14, 22, 16, 28, 56, 56, 42, 26, 28, 48]


def module_detail_specs(title):
    if title == "养成_角色":
        return [
            ("升级", ["升级"]),
            ("升阶", ["升阶", "突破"]),
            ("升星", ["升星"]),
            ("星盘能效", ["星盘", "能效"]),
        ]
    if title == "养成_专武":
        return [
            ("升级", ["升级"]),
            ("升阶", ["升阶", "突破"]),
            ("升星", ["升星"]),
        ]
    if title == "养成_旅券":
        return [
            ("制作", ["制作"]),
            ("升级", ["升级"]),
            ("商店", ["商店"]),
            ("分解", ["分解"]),
        ]
    if title == "养成_映射装备":
        return [
            ("升级", ["升级"]),
            ("打孔", ["打孔"]),
            ("宝石", ["宝石"]),
            ("鉴定", ["鉴定"]),
            ("词条", ["词条"]),
            ("品质额外", ["品质额外"]),
        ]
    return []


def detail_row_matches(row, keywords):
    text = " ".join(
        readable_text(row.get(key))
        for key in ("系统", "分组", "周期/限制", "进度/条件", "来源页", "口径", "备注")
    )
    return any(keyword in text for keyword in keywords)


def empty_detail_rows(label):
    return [{
        "系统": "",
        "分组": label,
        "周期/限制": "",
        "条件/阶段": "",
        "获得/产出": "",
        "消耗/花费": "",
        "奖励包/引用": "",
        "来源": "",
        "口径": "",
        "备注": "当前未从源表或正式配置观察到该子模块数据；保留页签方便后续补数。",
    }]


def source_label(row):
    source = readable_text(row.get("来源页"))
    source_row = readable_text(row.get("来源行"))
    return "%s%s" % (source, ":%s" % source_row if source_row else "")


def resource_column_name(row):
    name = readable_text(row.get("资源/道具"))
    item_id = readable_text(row.get("道具ID"))
    return name or ("ItemId %s" % item_id if item_id else "未命名资源")


def append_qty(bucket, key, qty):
    if key not in bucket:
        bucket[key] = []
    if readable_text(qty):
        bucket[key].append(qty)


def render_qty(values):
    nums = []
    for value in values:
        num = to_num(value)
        if num is None:
            return compact_list(values, 6, show_counts=False)
        nums.append(num)
    return fmt_num(sum(nums)) if nums else ""


def row_item_text_no_group(row):
    return readable_item_text(row.get("资源/道具"), row.get("道具ID"), row.get("数量"))


def build_shop_human_table(rows, sheet_name):
    groups = {}
    for row in sorted(rows, key=machine_row_sort_key):
        key = (
            readable_text(row.get("进度/条件")),
            readable_text(row.get("周期/限制")),
            readable_text(row.get("来源页")),
            readable_text(row.get("来源行")),
        )
        if key not in groups:
            groups[key] = {"outputs": [], "costs": [], "notes": [], "basis": [], "groups": [], "source": source_label(row)}
        rec = groups[key]
        direction = readable_text(row.get("方向"))
        if direction == "产出":
            rec["outputs"].append(row_item_text_no_group(row))
        elif direction == "消耗":
            rec["costs"].append(row_item_text_no_group(row))
        if readable_text(row.get("备注")):
            rec["notes"].append(readable_text(row.get("备注")))
        if readable_text(row.get("口径")):
            rec["basis"].append(readable_text(row.get("口径")))
        if readable_text(row.get("分组")):
            rec["groups"].append(readable_text(row.get("分组")))

    out = []
    for (condition, period, _source, _source_row), rec in sorted(groups.items(), key=lambda item: natural_sort_key(item[0][0])):
        out.append({
            "商品/获得": compact_list(rec["outputs"], 8, show_counts=False),
            "价格": compact_list(rec["costs"], 8, show_counts=False),
            "限购/周期": period,
            "商品ID/条件": condition,
            "分组": compact_list(rec["groups"], 4, show_counts=False),
            "来源": rec["source"],
            "备注": compact_list(rec["notes"], 4, show_counts=False),
        })
    headers = ["商品/获得", "价格", "限购/周期", "商品ID/条件", "分组", "来源", "备注"]
    widths = [42, 26, 14, 24, 20, 34, 44]
    return headers, out, widths, "%s：商店兑换表，按商品聚合价格和限购。" % sheet_name


def build_stage_human_table(rows, sheet_name):
    groups = {}
    resource_order = []
    has_stat_only = any("统计口径:经验计算值" in readable_text(row.get("口径")) for row in rows)
    for row in sorted(rows, key=machine_row_sort_key):
        key = (
            readable_text(row.get("进度/条件")),
            readable_text(row.get("周期/限制")),
            readable_text(row.get("来源页")),
            readable_text(row.get("来源行")),
        )
        if key not in groups:
            groups[key] = {
                "groups": [],
                "costs": {},
                "outputs": [],
                "refs": [],
                "notes": [],
                "basis": [],
                "value": 0.0,
                "value_numeric": True,
                "source": source_label(row),
            }
        rec = groups[key]
        direction = readable_text(row.get("方向"))
        if readable_text(row.get("分组")):
            rec["groups"].append(readable_text(row.get("分组")))
        if direction == "消耗":
            name = resource_column_name(row)
            if name not in resource_order:
                resource_order.append(name)
            append_qty(rec["costs"], name, row.get("数量"))
            value = to_num(row.get("价值(钻石)"))
            if value is None:
                if readable_text(row.get("价值(钻石)")):
                    rec["value_numeric"] = False
            else:
                rec["value"] += value
        elif direction == "产出":
            rec["outputs"].append(row_item_text_no_group(row))
        elif direction == "引用":
            rec["refs"].append(row_item_text_no_group(row))
        note = readable_text(row.get("备注"))
        if note and not note.startswith("仅用于升级成本阅读"):
            rec["notes"].append(readable_text(row.get("备注")))
        if readable_text(row.get("口径")):
            rec["basis"].append(readable_text(row.get("口径")))

    headers = ["阶段/条件", "分组", "周期/限制"] + resource_order + ["获得/产出", "奖励包/引用", "价值(钻石)", "来源", "备注"]
    out = []
    for (condition, period, _source, _source_row), rec in sorted(groups.items(), key=lambda item: (natural_sort_key(item[0][0]), natural_sort_key(item[0][2]), natural_sort_key(item[0][3]))):
        line = {
            "阶段/条件": condition,
            "分组": compact_list(rec["groups"], 5, show_counts=False),
            "周期/限制": period,
            "获得/产出": compact_list(rec["outputs"], 10, show_counts=False),
            "奖励包/引用": compact_list(rec["refs"], 8, show_counts=False),
            "价值(钻石)": fmt_num(rec["value"]) if rec["value_numeric"] and rec["value"] else ("含非数值" if not rec["value_numeric"] else ""),
            "来源": rec["source"],
            "备注": compact_list(rec["notes"], 5, show_counts=False),
        }
        for name in resource_order:
            line[name] = render_qty(rec["costs"].get(name, []))
        out.append(line)
    widths = [26, 24, 14] + [14 for _ in resource_order] + [36, 34, 12, 34, 44]
    subtitle = "%s：一行一个等级/阶段，资源拆成列；机器流水保留在最后用于追溯。" % sheet_name
    if has_stat_only:
        subtitle += " 经验计算值仅人读展示，不入总表/资源汇总。"
    return headers, out, widths, subtitle


def build_empty_human_table(sheet_name):
    headers = ["阶段/条件", "说明"]
    rows = [{"阶段/条件": sheet_name, "说明": "当前未从源表或正式配置观察到该子模块数据；保留页签方便后续补数。"}]
    widths = [22, 80]
    return headers, rows, widths, "%s：当前无正式产销数据。" % sheet_name


def build_detail_human_table(sheet_name, rows):
    if not rows:
        return build_empty_human_table(sheet_name)
    if sheet_name == "商店" or any("商店兑换" in readable_text(row.get("口径")) for row in rows):
        return build_shop_human_table(rows, sheet_name)
    return build_stage_human_table(rows, sheet_name)


def is_play_module(title):
    return title.startswith("玩法_")


def play_row_sort_key(row):
    return (
        natural_sort_key(row.get("分组")),
        natural_sort_key(row.get("周期/限制")),
        natural_sort_key(row.get("进度/条件")),
        natural_sort_key(row.get("来源页")),
        natural_sort_key(row.get("来源行")),
        natural_sort_key(row.get("方向")),
        to_int(row.get("_源内顺序")) or 0,
        natural_sort_key(row.get("资源/道具")),
    )


def play_group_priority(condition, rec):
    text = " ".join(
        [readable_text(condition)]
        + [readable_text(v) for key in ("groups", "periods") for v in rec.get(key, [])]
    )
    conclusion_keys = (
        "Score",
        "分数",
        "最高分",
        "生涯奖励",
        "首通",
        "首次",
        "结算",
        "排行",
        "排名",
        "累胜",
        "积分奖励",
        "层数奖励",
    )
    if any(key in text for key in conclusion_keys):
        return 0
    if rec.get("outputs"):
        return 1
    if rec.get("refs"):
        return 2
    if rec.get("costs"):
        return 3
    return 4


def play_group_sort_key(item):
    (condition, source, source_row), rec = item
    return (
        play_group_priority(condition, rec),
        natural_sort_key(condition),
        natural_sort_key(source),
        natural_sort_key(source_row),
    )


def build_play_output_table(rows):
    groups = {}
    output_order = []
    cost_order = []
    for row in sorted(rows, key=play_row_sort_key):
        key = (
            readable_text(row.get("进度/条件")),
            readable_text(row.get("来源页")),
            readable_text(row.get("来源行")),
        )
        if key not in groups:
            groups[key] = {
                "groups": [],
                "periods": [],
                "outputs": {},
                "costs": {},
                "refs": [],
                "notes": [],
                "source": source_label(row),
                "output_value": 0.0,
                "output_value_numeric": True,
                "cost_value": 0.0,
                "cost_value_numeric": True,
            }
        rec = groups[key]
        direction = readable_text(row.get("方向"))
        name = resource_column_name(row)
        if readable_text(row.get("分组")):
            rec["groups"].append(readable_text(row.get("分组")))
        if readable_text(row.get("周期/限制")):
            rec["periods"].append(readable_text(row.get("周期/限制")))
        if direction == "产出":
            if name not in output_order:
                output_order.append(name)
            append_qty(rec["outputs"], name, row.get("数量"))
            value = to_num(row.get("价值(钻石)"))
            if value is None:
                if readable_text(row.get("价值(钻石)")):
                    rec["output_value_numeric"] = False
            else:
                rec["output_value"] += value
        elif direction == "消耗":
            if name not in cost_order:
                cost_order.append(name)
            append_qty(rec["costs"], name, row.get("数量"))
            value = to_num(row.get("价值(钻石)"))
            if value is None:
                if readable_text(row.get("价值(钻石)")):
                    rec["cost_value_numeric"] = False
            else:
                rec["cost_value"] += value
        elif direction == "引用":
            rec["refs"].append(row_item_text_no_group(row))
        note = readable_text(row.get("备注"))
        if note:
            rec["notes"].append(note)

    output_headers = ["产出_%s" % name for name in output_order]
    cost_headers = ["消耗_%s" % name for name in cost_order]
    headers = ["阶段/条件", "奖励/产出类型", "周期/限制", "奖励包/引用"] + cost_headers + output_headers + [
        "产出价值(钻石)", "消耗价值(钻石)", "来源", "备注"
    ]
    out = []
    for (condition, _source, _source_row), rec in sorted(groups.items(), key=play_group_sort_key):
        line = {
            "阶段/条件": condition,
            "奖励/产出类型": compact_list(rec["groups"], 5, show_counts=False),
            "周期/限制": compact_list(rec["periods"], 5, show_counts=False),
            "奖励包/引用": compact_list(rec["refs"], 8, show_counts=False),
            "产出价值(钻石)": fmt_num(rec["output_value"]) if rec["output_value_numeric"] and rec["output_value"] else ("含非数值" if not rec["output_value_numeric"] else ""),
            "消耗价值(钻石)": fmt_num(rec["cost_value"]) if rec["cost_value_numeric"] and rec["cost_value"] else ("含非数值" if not rec["cost_value_numeric"] else ""),
            "来源": rec["source"],
            "备注": compact_list(rec["notes"], 5, show_counts=False),
        }
        for name in output_order:
            line["产出_%s" % name] = render_qty(rec["outputs"].get(name, []))
        for name in cost_order:
            line["消耗_%s" % name] = render_qty(rec["costs"].get(name, []))
        out.append(line)
    widths = [32, 24, 16, 40] + [14 for _ in cost_headers] + [14 for _ in output_headers] + [14, 14, 34, 44]
    return headers, out, widths


def write_play_output_sheet(wb, title, rows):
    if not is_play_module(title):
        return
    headers, readable_rows, widths = build_play_output_table(rows)
    append_human_table_sheet(
        wb,
        "玩法产出",
        "玩法产出：先放分数/首通/结算/排行等产出结论节点，再放过程收益和奖励引用；Drop/Reward 暂保留为奖励包入口。",
        headers,
        readable_rows,
        widths,
        "T_play_output",
    )


def module_read_order(title):
    if is_play_module(title):
        return "先看 玩法产出；该页先放分数/首通/结算/排行等产出结论节点，再放过程收益和奖励引用；再看资源汇总，产销阅读和机器明细用于追溯。"
    if module_detail_specs(title):
        return "先看分类页签（如升级/升阶/制作/商店），这些页已按阶段做成宽表；再看资源汇总；产销阅读和机器明细用于追溯。"
    return "先看 产销阅读；需要看资源级合计时看 资源汇总；需要追溯脚本校验时看 机器明细。"


def write_module_detail_sheets(wb, title, rows):
    for idx, (sheet_name, keywords) in enumerate(module_detail_specs(title), start=1):
        detail_rows = [row for row in rows if detail_row_matches(row, keywords)]
        headers, readable_rows, widths, subtitle = build_detail_human_table(sheet_name, detail_rows)
        append_human_table_sheet(
            wb,
            sheet_name,
            subtitle,
            headers,
            readable_rows,
            widths,
            "T_detail_%02d" % idx,
        )


def split_id_list(value):
    text = readable_text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"[;；,，]", text) if part.strip()]


def parse_percent(text):
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", readable_text(text))
    return float(match.group(1)) if match else ""


def load_gacha_probability_data():
    draw_path = cfg_path("Activity", "DrawCard", "DrawCard.xlsx")
    pool_path = cfg_path("Activity", "DrawCard", "DrawCardPool.xlsx")
    weight_path = cfg_path("Activity", "DrawCard", "DrawCardWeight.xlsx")
    choose_path = cfg_path("Activity", "DrawCard", "DrawSpecialChooseGacha.xlsx")

    draw_rows = row_dicts(draw_path, "DrawCard") if os.path.exists(draw_path) else []
    draw_by_id = {readable_text(row.get("Id")): row for row in draw_rows}
    pool_rows = row_dicts(pool_path, "DrawCardPool") if os.path.exists(pool_path) else []
    weight_rows = row_dicts(weight_path) if os.path.exists(weight_path) else []
    choose_rows = row_dicts(choose_path) if os.path.exists(choose_path) else []

    overview = []
    guarantee = []
    for row in draw_rows:
        draw_id = readable_text(row.get("Id"))
        name = readable_text(row.get("Name"))
        source = "正式:Activity/DrawCard/DrawCard.xlsx#%s" % readable_text(row.get("_row"))
        overview.append({
            "抽卡ID": draw_id,
            "卡池名": name,
            "页签": readable_text(row.get("Tab")),
            "抽卡类型": readable_text(row.get("DrawType")),
            "是否有效": readable_text(row.get("IsValid")),
            "限抽次数": readable_text(row.get("LimitDrawCount")),
            "DropId": readable_text(row.get("DropId")),
            "TenDropId": readable_text(row.get("TenDropId")),
            "小保底DropId": readable_text(row.get("XiaoBaoDiId")),
            "小保底触发": readable_text(row.get("XiaoBaoDiTriggerNum")),
            "大保底DropId": readable_text(row.get("DaBaoDiId")),
            "大保底UP列表": readable_text(row.get("DaBaoDiUPList")),
            "大保底触发": readable_text(row.get("DaBaoDiTriggerNum")),
            "来源": source,
        })
        guarantee.append({
            "抽卡ID": draw_id,
            "卡池名": name,
            "十连保底DropId": readable_text(row.get("TenDropId")),
            "十连AI类型": readable_text(row.get("TenDropAIType")),
            "单抽权重数组": readable_text(row.get("OneDropArraysID")),
            "小保底DropId": readable_text(row.get("XiaoBaoDiId")),
            "小保底触发": readable_text(row.get("XiaoBaoDiTriggerNum")),
            "小保底AI类型": readable_text(row.get("XiaoBaoDiAIType")),
            "大保底DropId": readable_text(row.get("DaBaoDiId")),
            "大保底UP列表": readable_text(row.get("DaBaoDiUPList")),
            "大保底触发": readable_text(row.get("DaBaoDiTriggerNum")),
            "规则ID": readable_text(row.get("RuleId")),
            "特殊规则ID": readable_text(row.get("SpecialRuleId")),
            "来源": source,
        })

    probability = []
    pool_item_ids = set()
    for row in pool_rows:
        ids = split_id_list(row.get("Pool"))
        pool_item_ids.update(ids)
        draw_id = readable_text(row.get("DrawId"))
        draw = draw_by_id.get(draw_id, {})
        base_prob = parse_percent(row.get("Desc"))
        up_prob = parse_percent(row.get("UpItemDesc"))
        probability.append({
            "PoolId": readable_text(row.get("Id")),
            "抽卡ID": draw_id,
            "卡池名": readable_text(draw.get("Name")),
            "品质": readable_text(row.get("PoolType")),
            "基础概率%": base_prob,
            "UP道具ID": readable_text(row.get("UpItemId")),
            "UP概率%": up_prob,
            "奖池数量": len(ids),
            "单个均分概率%": round(base_prob / len(ids), 6) if is_num(base_prob) and ids else "",
            "奖池ID列表": "；".join(ids),
            "概率描述": readable_text(row.get("Desc")),
            "UP描述": readable_text(row.get("UpItemDesc")),
            "是否有效": readable_text(row.get("IsValid")),
            "来源": "正式:Activity/DrawCard/DrawCardPool.xlsx#%s" % readable_text(row.get("_row")),
        })

    weight = [{
        "抽数": readable_text(row.get("ID")),
        "权重": readable_text(row.get("DrawWeight")),
        "来源": "正式:Activity/DrawCard/DrawCardWeight.xlsx#%s" % readable_text(row.get("_row")),
    } for row in weight_rows]

    choose = []
    for row in choose_rows:
        ids = split_id_list(row.get("DrawIDList"))
        choose.append({
            "Id": readable_text(row.get("Id")),
            "对应Draw/SSR列表": "；".join(ids),
            "数量": len(ids),
            "是否有效": readable_text(row.get("IsValid")),
            "来源": "正式:Activity/DrawCard/DrawSpecialChooseGacha.xlsx#%s" % readable_text(row.get("_row")),
        })

    return {
        "overview": overview,
        "probability": probability,
        "guarantee": guarantee,
        "weight": weight,
        "choose": choose,
        "pool_item_count": len(pool_item_ids),
    }


def write_gacha_probability_workbook(title, systems, note, idx):
    path = os.path.join(MODULE_DIR, safe_filename(title, idx))
    data = load_gacha_probability_data()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "阅读摘要"
    ws.append([title, note])
    ws.cell(1, 1).font = Font(bold=True, color="FFFFFF", size=14)
    ws.cell(1, 2).font = Font(color="FFFFFF")
    for col_idx in range(1, 5):
        ws.cell(1, col_idx).fill = MODULE_HEAD_FILL
        ws.cell(1, col_idx).border = MODULE_BORDER
    summary_rows = [
        ["系统", "、".join(systems)],
        ["产销口径", "不计算抽卡消耗；不进入全资源产销总表。"],
        ["卡池数", len(data["overview"])],
        ["品质概率行", len(data["probability"])],
        ["奖池唯一ID数", data["pool_item_count"]],
        ["保底规则行", len(data["guarantee"])],
        ["权重曲线行", len(data["weight"])],
        ["自选池行", len(data["choose"])],
        ["阅读提示", "基础概率来自 DrawCardPool.Desc；单个均分概率按同品质 Pool ID 数均分，仅用于阅读。"],
    ]
    ws.append([])
    for key, value in summary_rows:
        ws.append([key, value])
    for row_idx in range(3, ws.max_row + 1):
        ws.cell(row_idx, 1).font = Font(bold=True)
        ws.cell(row_idx, 1).fill = MODULE_SUB_FILL
        for col_idx in range(1, 3):
            ws.cell(row_idx, col_idx).border = MODULE_BORDER
            ws.cell(row_idx, col_idx).alignment = Alignment(vertical="top", wrap_text=True)
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 100
    ws.freeze_panes = "A3"

    append_table_sheet(
        wb,
        "卡池总览",
        ["抽卡ID", "卡池名", "页签", "抽卡类型", "是否有效", "限抽次数", "DropId", "TenDropId", "小保底DropId", "小保底触发", "大保底DropId", "大保底UP列表", "大保底触发", "来源"],
        data["overview"],
        [10, 18, 10, 24, 10, 10, 10, 10, 14, 12, 14, 24, 12, 42],
        "T_gacha_overview",
    )
    append_table_sheet(
        wb,
        "品质概率",
        ["PoolId", "抽卡ID", "卡池名", "品质", "基础概率%", "UP道具ID", "UP概率%", "奖池数量", "单个均分概率%", "奖池ID列表", "概率描述", "UP描述", "是否有效", "来源"],
        data["probability"],
        [10, 10, 18, 10, 12, 12, 12, 10, 16, 48, 56, 36, 10, 42],
        "T_gacha_probability",
    )
    append_table_sheet(
        wb,
        "保底规则",
        ["抽卡ID", "卡池名", "十连保底DropId", "十连AI类型", "单抽权重数组", "小保底DropId", "小保底触发", "小保底AI类型", "大保底DropId", "大保底UP列表", "大保底触发", "规则ID", "特殊规则ID", "来源"],
        data["guarantee"],
        [10, 18, 16, 14, 16, 14, 12, 14, 14, 24, 12, 10, 12, 42],
        "T_gacha_guarantee",
    )
    append_table_sheet(
        wb,
        "权重曲线",
        ["抽数", "权重", "来源"],
        data["weight"],
        [10, 10, 42],
        "T_gacha_weight",
    )
    append_table_sheet(
        wb,
        "自选池",
        ["Id", "对应Draw/SSR列表", "数量", "是否有效", "来源"],
        data["choose"],
        [10, 56, 10, 10, 42],
        "T_gacha_choose",
    )

    try:
        wb.save(path)
    except PermissionError:
        if not os.path.exists(path):
            raise
        MODULE_WRITE_WARNINGS.append("抽卡概率文件被占用，已沿用现有文件: %s" % path)
    metrics = {
        "direction_counts": {
            "概率": len(data["probability"]),
            "保底": len(data["guarantee"]),
            "权重": len(data["weight"]),
            "自选": len(data["choose"]),
        },
        "value_by_direction": {},
        "resource_count": data["pool_item_count"],
        "source_count": 4,
    }
    row_count = len(data["overview"]) + len(data["probability"]) + len(data["guarantee"]) + len(data["weight"]) + len(data["choose"])
    return path, metrics, row_count


def write_module_summary_sheet(wb, title, systems, rows, note, metrics):
    ws = wb.active
    ws.title = "阅读摘要"
    direction_text = "；".join("%s:%s" % (k, v) for k, v in sorted(metrics["direction_counts"].items()))
    value_text = "；".join("%s:%s" % (k, round(v, 2)) for k, v in sorted(metrics["value_by_direction"].items()))
    source_text = compact_list([row.get("来源页") for row in rows], 12)
    summary_rows = [
        ["模块", title],
        ["系统", "、".join(systems)],
        ["说明", note],
        ["阅读顺序", module_read_order(title)],
        ["记录数", len(rows)],
        ["资源数", metrics["resource_count"]],
        ["来源页数", metrics["source_count"]],
        ["方向分布", direction_text],
        ["价值分布(钻石)", value_text],
        ["主要产出", summarize_items(rows, "产出", 10)],
        ["主要消耗", summarize_items(rows, "消耗", 10)],
        ["奖励包/引用", summarize_items(rows, "引用", 8)],
        ["来源页", source_text],
        ["阅读提示", module_risk_tags(rows)],
    ]

    ws.append([title, note])
    ws.cell(1, 1).font = Font(bold=True, color="FFFFFF", size=14)
    ws.cell(1, 2).font = Font(color="FFFFFF")
    for c in range(1, 5):
        ws.cell(1, c).fill = MODULE_HEAD_FILL
        ws.cell(1, c).border = MODULE_BORDER
    ws.append([])
    for key, value in summary_rows:
        ws.append([key, value])
    for row_idx in range(3, ws.max_row + 1):
        ws.cell(row_idx, 1).font = Font(bold=True)
        ws.cell(row_idx, 1).fill = MODULE_SUB_FILL
        for col_idx in range(1, 3):
            ws.cell(row_idx, col_idx).border = MODULE_BORDER
            ws.cell(row_idx, col_idx).alignment = Alignment(vertical="top", wrap_text=True)

    system_counts = Counter(readable_text(row.get("系统")) for row in rows if readable_text(row.get("系统")))
    group_counts = Counter(readable_text(row.get("分组")) for row in rows if readable_text(row.get("分组")))
    start = ws.max_row + 3
    ws.cell(start, 1, "高频系统")
    ws.cell(start, 2, "记录数")
    ws.cell(start, 4, "高频分组")
    ws.cell(start, 5, "记录数")
    for cell in (ws.cell(start, 1), ws.cell(start, 2), ws.cell(start, 4), ws.cell(start, 5)):
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = MODULE_HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = MODULE_BORDER
    max_len = max(len(system_counts.most_common(8)), len(group_counts.most_common(8)), 1)
    for offset in range(max_len):
        row_idx = start + 1 + offset
        if offset < len(system_counts):
            system, count = system_counts.most_common(8)[offset]
            ws.cell(row_idx, 1, system)
            ws.cell(row_idx, 2, count)
        if offset < len(group_counts):
            group, count = group_counts.most_common(8)[offset]
            ws.cell(row_idx, 4, group)
            ws.cell(row_idx, 5, count)
        for col_idx in (1, 2, 4, 5):
            ws.cell(row_idx, col_idx).border = MODULE_BORDER
            ws.cell(row_idx, col_idx).alignment = Alignment(vertical="top", wrap_text=True)

    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 100
    ws.column_dimensions["C"].width = 4
    ws.column_dimensions["D"].width = 26
    ws.column_dimensions["E"].width = 12
    ws.freeze_panes = "A3"
    return ws


MAINLINE_SUMMARY_TITLES = ("玩法_主线", "玩法_困难主线")
_CN_CHAPTER = {0: "序章", 1: "第一章", 2: "第二章", 3: "第三章", 4: "第四章", 5: "第五章", 6: "第六章", 7: "第七章"}
_SUMMARY_FOCUS = ("元晶", "金币", "低阶记录盘", "中阶记录盘", "高阶记录盘")
_SUMMARY_OTHER_LIMIT = 6


def _mainline_chapter_name(condition, hard_only=None):
    text = str(condition or "")
    if "IsDifficult" in text:
        is_hard = "IsDifficult True" in text
        if hard_only is not None and is_hard != hard_only:
            return None
    m = re.search(r"LevelId\s+(\d{6})", text)
    if m:
        lid = m.group(1)
        if lid.startswith("100") or lid.startswith("110"):
            return _CN_CHAPTER.get(int(lid[3]))
        if lid.startswith("120"):
            return "支线"
        if lid.startswith("15"):
            return "章节玩法关(华容道)"
        if lid.startswith("17"):
            return "章节玩法关(电路)"
        return None
    m = re.search(r"ChapterId\s+(\d+)", text)
    if m:
        return _CN_CHAPTER.get(int(m.group(1)) - 10000)
    return None


def _summary_add(bundle, resource, value):
    if value is None:
        return False
    bundle[resource] = bundle.get(resource, 0) + value
    return True


def _summary_text_pair(name, qty):
    return "%s×%s" % (name, fmt_num(qty) if isinstance(qty, (int, float)) else qty)


def build_chapter_summary_sheet(wb, title, rows):
    """主线/困难主线模块的章节汇总阅读页：每章一行，置顶。解析失败时不产出该页。"""
    hard_only = True if title == "玩法_困难主线" else (False if title == "玩法_主线" else None)
    chapters = {}
    order = []
    for row in rows:
        condition = str(row.get("进度/条件") or "")
        chapter = _mainline_chapter_name(condition, hard_only)
        if chapter is None:
            continue
        group = str(row.get("分组") or "")
        is_level_row = any(key in group for key in ("首通奖励", "重复奖励", "体力消耗", "高额奖励"))
        is_star_row = condition.startswith("ChapterId")
        if not is_level_row and not is_star_row:
            continue
        if chapter not in chapters:
            chapters[chapter] = {
                "levels": set(),
                "repeat_costs": set(),
                "first_out": {},
                "first_out_text": [],
                "repeat_per_level": {},
                "star_nodes": 0,
                "star_out": {},
                "star_value": 0.0,
                "value": 0.0,
            }
            order.append(chapter)
        rec = chapters[chapter]
        direction = str(row.get("方向") or "")
        resource = str(row.get("资源/道具") or "")
        period = str(row.get("周期/限制") or "")
        qty = to_num(row.get("数量"))
        m = re.search(r"LevelId\s+(\d{6})", condition)
        level_id = m.group(1) if m else condition[:40]
        if is_star_row:
            rec["star_nodes"] += 1
            value = to_num(row.get("价值(钻石)")) or 0.0
            rec["star_value"] += value
            if direction == "产出" and resource and qty is not None:
                rec["star_out"][resource] = rec["star_out"].get(resource, 0) + qty
            continue
        rec["levels"].add(level_id)
        if direction == "消耗" and "储能" in resource:
            if "重复" in period or "进入" in period:
                rec["repeat_costs"].add(qty if qty is not None else str(row.get("数量")))
        elif direction == "产出":
            value = to_num(row.get("价值(钻石)")) or 0.0
            if "一次性" in period or "首通" in period:
                if resource and qty is not None:
                    rec["first_out"][resource] = rec["first_out"].get(resource, 0) + qty
                if resource and resource not in _SUMMARY_FOCUS:
                    rec["first_out_text"].append(_summary_text_pair(resource, row.get("数量")))
                rec["value"] += value
            elif "重复" in period:
                per = rec["repeat_per_level"].setdefault(level_id, {})
                if resource and qty is not None:
                    per[resource] = per.get(resource, 0) + qty
    if not order:
        return None

    chapter_order = sorted(order, key=lambda n: (n not in _CN_CHAPTER.values(), list(_CN_CHAPTER.values()).index(n) if n in _CN_CHAPTER.values() else 0, n))
    headers = ["章节", "关数", "进入体力/次", "首通元晶", "首通金币", "首通记录盘(低/中/高)",
               "首通其他产出(要点)", "重复产出(每关区间)", "星级奖励", "首通+星级价值(钻石)"]

    def _focus_sum(bundle, keyword):
        return sum(v for k, v in bundle.items() if keyword in k)

    out_rows = []
    totals = {"levels": 0, "value": 0.0, "yuan": 0, "gold": 0, "disk": [0, 0, 0], "star": 0.0}
    for name in chapter_order:
        rec = chapters[name]
        first = rec["first_out"]
        disks = "/".join(fmt_num(first.get(key, 0)) if first.get(key) is not None else "0" for key in _SUMMARY_FOCUS[2:])
        others = [t for t in rec["first_out_text"] if not any(key in t for key in _SUMMARY_FOCUS)][: _SUMMARY_OTHER_LIMIT]
        repeat_bits = []
        for resource in sorted({k for per in rec["repeat_per_level"].values() for k in per}):
            values = [per[resource] for per in rec["repeat_per_level"].values() if resource in per]
            if not values:
                continue
            lo, hi = min(values), max(values)
            repeat_bits.append("%s %s/关" % (resource, fmt_num(lo) if lo == hi else "%s~%s" % (fmt_num(lo), fmt_num(hi))))
        star_bits = []
        if rec["star_nodes"]:
            star_bits.append("%d 档" % rec["star_nodes"])
            for resource in ("元晶", "金币"):
                if _focus_sum(rec["star_out"], resource):
                    star_bits.append("%s %s" % (resource, fmt_num(_focus_sum(rec["star_out"], resource))))
        cost_repeat = "/".join(str(c) for c in sorted(rec["repeat_costs"])) if rec["repeat_costs"] else "-"
        yuan = _focus_sum(first, "元晶")
        gold = _focus_sum(first, "金币")
        out_rows.append([
            name,
            len(rec["levels"]),
            cost_repeat,
            fmt_num(yuan) or "0",
            fmt_num(gold) or "0",
            disks,
            "；".join(others) if others else "-",
            "；".join(repeat_bits[:4]) if repeat_bits else "-",
            "；".join(star_bits) if star_bits else "-",
            fmt_num(round(rec["value"] + rec["star_value"], 2)) if (rec["value"] or rec["star_value"]) else "-",
        ])
        totals["levels"] += len(rec["levels"])
        totals["value"] += rec["value"] + rec["star_value"]
        totals["yuan"] += yuan
        totals["gold"] += gold
        for i, key in enumerate(_SUMMARY_FOCUS[2:]):
            totals["disk"][i] += first.get(key, 0) or 0
        totals["star"] += rec["star_value"]
    out_rows.append([
        "合计", totals["levels"], "-", fmt_num(totals["yuan"]),
        fmt_num(totals["gold"]), "/".join(fmt_num(v) for v in totals["disk"]),
        "见各章", "见各章", "星级价值 %s" % fmt_num(round(totals["star"], 2)), fmt_num(round(totals["value"], 2)),
    ])

    ws = wb.create_sheet("章节汇总", 0)
    ws.append(["章节汇总（阅读版）：每章一行；" + ("困难主线" if title == "玩法_困难主线" else "普通主线（含序章/支线/章节玩法关/星级）") + "。逐关明细见「玩法产出」页。"])
    ws.append(headers)
    for row in out_rows:
        ws.append(row)
    widths = [16, 8, 12, 12, 14, 18, 40, 34, 22, 18]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width
    for cell in ws[2]:
        cell.font = openpyxl.styles.Font(bold=True)
    ws.freeze_panes = "A3"
    return ws


def write_module_workbook(title, systems, rows, note, idx, display_rows=None):
    path = os.path.join(MODULE_DIR, safe_filename(title, idx))
    rows = sorted(rows, key=ledger_row_sort_key)
    display_rows = sorted(display_rows if display_rows is not None else rows, key=ledger_row_sort_key)
    wb = openpyxl.Workbook()
    metrics = split_metrics(rows)
    readable_rows = aggregate_module_readable_rows(display_rows)
    resource_rows = build_module_resource_rows(rows)

    write_module_summary_sheet(wb, title, systems, rows, note, metrics)
    append_table_sheet(
        wb,
        "产销阅读",
        MODULE_READABLE_HEADERS,
        readable_rows,
        MODULE_READABLE_WIDTHS,
        "T_readable",
    )
    write_play_output_sheet(wb, title, display_rows)
    write_module_detail_sheets(wb, title, display_rows)
    append_table_sheet(
        wb,
        "资源汇总",
        ["资源分类", "资源/道具", "道具ID", "方向", "记录数", "数量合计", "价值合计(钻石)", "出现位置", "来源页", "阅读提示"],
        resource_rows,
        [16, 24, 10, 10, 10, 14, 16, 42, 34, 24],
        "T_resources",
        direction_col=4,
    )
    append_table_sheet(
        wb,
        "机器明细",
        SPLIT_HEADERS,
        [split_row(row) for row in sorted(rows, key=machine_row_sort_key)],
        [18, 10, 22, 14, 14, 18, 12, 16, 32, 18, 10, 28, 38],
        "T_%s" % TABLE_NAME_BY_TITLE.get(title, "module"),
        direction_col=2,
    )
    if title in MAINLINE_SUMMARY_TITLES:
        try:
            build_chapter_summary_sheet(wb, title, rows)
        except Exception as error:  # 阅读页失败不阻塞数值生产
            MODULE_WRITE_WARNINGS.append("章节汇总页生成失败(%s): %s" % (title, error))
    try:
        wb.save(path)
    except PermissionError:
        if not os.path.exists(path):
            raise
        MODULE_WRITE_WARNINGS.append("模块文件被占用，已沿用现有文件: %s" % path)
    return path, metrics


def write_module_files(split_rows_by_title, display_extra_rows_by_title=None):
    clean_module_dir()
    display_extra_rows_by_title = display_extra_rows_by_title or {}
    outputs = []
    for idx, (title, systems, note) in enumerate(SPLIT_DEFS, start=1):
        rows = split_rows_by_title[title]
        display_rows = rows + display_extra_rows_by_title.get(title, [])
        shown_systems = display_systems(title, systems)
        if title == "抽卡_概率":
            path, metrics, record_count = write_gacha_probability_workbook(title, shown_systems, note, idx)
        else:
            path, metrics = write_module_workbook(title, shown_systems, rows, note, idx, display_rows=display_rows)
            record_count = len(rows)
        outputs.append([
            title,
            "、".join(shown_systems),
            record_count,
            metrics["resource_count"],
            "；".join("%s:%s" % (k, v) for k, v in sorted(metrics["direction_counts"].items())),
            "；".join("%s:%s" % (k, round(v, 2)) for k, v in sorted(metrics["value_by_direction"].items())),
            note,
            path,
        ])
    return outputs


def build_split_overview(b):
    rows = []
    split_rows_by_title = {}
    for title, systems, note in SPLIT_DEFS:
        module_rows = rows_for_split(b, title, systems)
        shown_systems = display_systems(title, systems)
        split_rows_by_title[title] = module_rows
        metrics = split_metrics(module_rows)
        rows.append([
            title,
            "、".join(shown_systems),
            len(module_rows),
            metrics["resource_count"],
            "；".join("%s:%s" % (k, v) for k, v in sorted(metrics["direction_counts"].items())),
            "；".join("%s:%s" % (k, round(v, 2)) for k, v in sorted(metrics["value_by_direction"].items())),
            note,
        ])
    return rows, split_rows_by_title


def build_display_extra_rows_by_title(b):
    extras = {}
    for title, systems, _note in SPLIT_DEFS:
        wanted = set(systems)
        extra_rows = [row for row in b.stat_only_rows if row["系统"] in wanted]
        if title == "玩法_主线":
            extra_rows = [row for row in extra_rows if not is_chapter_task_row(row)]
        elif title == "外循环_章节任务":
            extra_rows = [row for row in extra_rows if is_chapter_task_row(row)]
        if extra_rows:
            extras[title] = extra_rows
    return extras


def write_report(b, summary_rows, module_outputs):
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    direction_counts = defaultdict(int)
    system_counts = defaultdict(int)
    source_sheets = set()
    for row in b.ledger:
        direction_counts[row["方向"]] += 1
        system_counts[row["系统"]] += 1
        source_sheets.add(row["来源页"])
    lines = [
        "# P4b · 经济总账生成与覆盖",
        "",
        "> 首版目标：把经济框架中可直接观察的产出、消耗、商店兑换和奖励引用先按玩法/外循环/养成模块拆成独立 Excel 文件，再汇总到资源总表；不直接修改源表，不强行展开 DropId/RewardId。",
        "",
        "## 结论",
        "",
        f"- 源表: `{SRC}`",
        f"- 汇总表: `{OUT}`",
        f"- 模块表目录: `{MODULE_DIR}`",
        f"- 产销明细: {len(b.ledger)} 行。",
        f"- 模块 Excel: {len(module_outputs)} 个；普通产销模块包含 `阅读摘要`、`产销阅读`、`资源汇总`、`机器明细`；玩法模块新增 `玩法产出` 宽表，角色/专武/旅券/映射装备分类页签改为阶段宽表；抽卡模块只输出概率表。",
        f"- 资源汇总: {len(summary_rows)} 行。",
        f"- 道具定价锚点: `01_源表/道具定价.xlsx` 共 {len(b.price_rows)} 行，仅脚本内部估值使用。",
        f"- 已触达来源页: {len(source_sheets)} 个。",
        "- 产物不写公式，不写 Excel 错误值；源表中的 `#N/A/#DIV/0!` 已按待定或空值处理。",
    ]
    excluded_total = sum(b.stat_excluded_counts.values())
    if excluded_total:
        excluded_detail = "；".join("%s:%s行" % (name, count) for name, count in sorted(b.stat_excluded_counts.items()))
        lines.append("- 统计口径排除: %s 行（%s）；仅排除精确同名计算值，带品质/数量后缀的真实经验道具保留。" % (excluded_total, excluded_detail))
    deprecated_total = sum(b.deprecated_excluded_counts.values())
    if deprecated_total:
        deprecated_detail = "；".join("%s:%s行" % (name, count) for name, count in sorted(b.deprecated_excluded_counts.items()))
        lines.append("- 废弃系统排除: %s 行（%s）；共鸣装备已废弃，不进入当前产销统计。" % (deprecated_total, deprecated_detail))
    non_ledger_total = sum(b.non_ledger_excluded_counts.values())
    if non_ledger_total:
        non_ledger_detail = "；".join("%s:%s行" % (name, count) for name, count in sorted(b.non_ledger_excluded_counts.items()))
        lines.append("- 非产销系统排除: %s 行（%s）；抽卡不计算消耗，改由 `21_抽卡_概率.xlsx` 承接概率、保底和权重。" % (non_ledger_total, non_ledger_detail))
    lines.append("- 阅读排序: 模块 `产销阅读`、拆分页签和 `机器明细` 已按 Lv/TargetLv/来源行等数字做自然排序，避免 Lv10 排在 Lv2 前。")
    lines.append("- 分类页排版: 养成分类页签已从流水文本改为宽表，一行一个等级/阶段/商品，资源拆成列；角色经验/专武经验仅在人读表展示，不进入总表和资源汇总。")
    lines.append("- 玩法表排版: 所有 `玩法_*` 模块新增 `玩法产出`，分数/首通/结算/排行等产出结论节点优先置顶，再放过程收益和奖励引用。")
    lines.append("- 旅券副本: `旅券副本` 页手填的 `邮票本1-4` 具体掉落邮票已写入 `04_玩法_旅券副本.xlsx`，作为候选掉落池引用追溯，不伪造成固定产量。")
    lines.append("- 宽表冻结: `玩法产出` 冻结到 `奖励包/引用`，商店冻结到 `商品ID/条件`，养成阶段宽表冻结到 `周期/限制`，横向滚动时保留识别列。")
    if MODULE_WRITE_WARNINGS:
        lines += ["", "## 写入提示", ""]
        for warning in MODULE_WRITE_WARNINGS:
            lines.append("- %s" % warning)
    lines += [
        "",
        "## 方向分布",
        "",
        "| 方向 | 行数 |",
        "|---|---:|",
    ]
    for key, count in sorted(direction_counts.items()):
        lines.append(f"| {key} | {count} |")
    lines += ["", "## 系统分布", "", "| 系统 | 行数 |", "|---|---:|"]
    for key, count in sorted(system_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {key} | {count} |")
    lines += ["", "## 模块文件", "", "| 模块文件 | 系统 | 行数 | 资源数 | 说明 |", "|---|---|---:|---:|---|"]
    for title, systems, count, resource_count, _direction, _value, note, path in module_outputs:
        lines.append(f"| `{os.path.basename(path)}` | {systems} | {count} | {resource_count} | {note} |")
    lines += [
        "",
        "## 首版边界",
        "",
        "- `DropId / RewardId / CommonReward / PassAdditionReward` 当前只登记引用关系；真实包内容后续接 `vgame-reward-drop-sync` 展开。",
        "- `道具定价` 改由 `01_源表/道具定价.xlsx` 提供；其余系统明细仍按正式配置或已声明旧源读取。",
        "- `世界boss` 页按其表头说明处理为 `BOSS挑战` 一次性首通奖励，不作为正式世界 boss 玩法恢复。",
        "- `neural_roam` 已按用户裁决归入 `无限挑战（无限之旅）`，不再单拆“神经漫游”模块。",
        "- 当前阶段没有商业化内容；月卡、付费商品、充值、通行证付费档等不列为当前 P0 待办。",
        "- `肉鸽（废弃）` 不纳入当前正式经济层。",
        "",
        "## 本轮正式配置补强",
        "",
        "- BOSS挑战：补正式 `BossDungeon/Boss_Dungeon.xlsx` 的 `Reward/BestReward` 引用。",
        "- 无限挑战（无限之旅）：并入正式 `neural_roam/NR_HighestScoreReward.xlsx` 与 `NR_Layer.xlsx`；`NR_RankReward` 当前 DropId 为空，仅记录边界。",
        "- 映射装备养成：新增 `养成_映射装备` 独立模块，补 `SpecialEquipmentLvUp/Quality/EffectDrop` 的升级、鉴定、打孔、额外道具和词条池入口。",
        "- 旅券养成：扩展 `养成_旅券`，补 `StrategyLv/StrategyResolve/StrategyCraft/StrategyCardShop` 的升级、分解、制作和商店兑换。",
        "- 抽卡概率：`抽卡_概率` 改读正式 DrawCard/DrawCardPool/DrawCardWeight/DrawSpecialChooseGacha，只输出概率、保底、权重和自选池；不再计算抽卡消耗产销。",
        "- 炮台养成：`养成_炮台` 仅保留炮台自身逐级升级与节点突破材料；共鸣装备按废弃系统排除。",
        "- 房车养成：新增 `养成_房车`，来自 `养成/生成_房车.xlsx` 的房车整备和出行指南职业节点消耗。",
        "- 校验回答补充：按用户在 P4c `需要确认` 页的回答，补正式 Task/SevenDaySign、UIlevel/Chapter、DrawCard 概率入口、Guild；旧设计 B炮台 ID 纠偏为 96303，竞技场商店则改读正式 ShopGoods#1109。",
        "- 真实差异修正：签到改由正式 DailySign/MonthlyAccumulate/TravelAccumulate 覆盖旧设计值；角色/专武满级无下一等级消耗的旧行不再写入；竞技场商店不再使用旧设计行。",
        "- 工具页索引修正：旧经济框架的 `道具定价` 不再作为定价输入，统一读取 `01_源表/道具定价.xlsx`。",
        "- 2026-09-04 爬塔改读评审镜像（CHG-043/044）：`玩法_爬塔` 产销改读 `06_最终配置/爬塔`（TowerFirstReward + Drop_dungeon + TowerIdleRewards），并按 CHG-044 验收总量断言（首通223行：元晶7,300/熔晶7/旅券60/房车零件4,000/自选箱650/高阶课程笔记150/精英课程笔记10）；旧经济母表配置页-爬塔、每周/扫荡、爬塔商店与正式 TowerReward 赛季引用不再计入。",
        "- 2026-09-04 房车多级节点接入（CHG-053）：`养成_房车` 改为消费 `养成/生成_房车.xlsx` 的多级节点经济明细（每职业66节点/360条升级记录，1156拆分落Lv2/Lv3），并携带道具ID列。",
        "- 2026-09-04 副本五族直读正式配置：主线/困难主线/资源副本/旅券副本/映射装备副本停用经济母表2026-07设计页，改读正式 level/UIlevel.xlsx + Drop 全表展开（首通/重复/三星/高额；##停用与ItemId=0占位行不计），与当前游戏口径一致。",
        "",
        "## 待后续深挖",
        "",
        "- Drop/Reward 包真实内容展开与反查。",
        "- P1 非商业漏项：角色技能/能效、专武分解/重复奖励、旁支/见闻/系统引导任务、UIlevel 与 Drop 包逐行强展开。",
        "- Luban 导出链路接入后，按真实配置表字段复验 ItemId/DropId/RewardId。",
    ]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def verify_no_error_literals(path):
    wb = openpyxl.load_workbook(path, data_only=False)
    errors = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.strip() in ERROR_VALUES:
                    errors.append("%s!%s=%s" % (ws.title, cell.coordinate, cell.value))
    wb.close()
    return errors


def main():
    if not os.path.exists(SRC):
        raise FileNotFoundError(SRC)
    if not os.path.exists(PRICE_SRC):
        raise FileNotFoundError(PRICE_SRC)
    src_wb = openpyxl.load_workbook(SRC, data_only=True)
    price_wb = openpyxl.load_workbook(PRICE_SRC, data_only=True)
    b = EconomyLedger(src_wb, price_wb)

    parse_shop_blocks(b, "商店", "商店")
    parse_signin(b)
    parse_seven_day_tasks(b)
    parse_task_sheet(b)
    parse_battlepass(b)
    parse_battlepass_config(b)
    # 2026-09-04：主线/困难主线/资源副本/旅券副本/映射装备副本不再读经济母表
    # 设计页，统一由 parse_formal_level_reward_refs 直读正式 UIlevel + Drop 展开。
    parse_verification_configs(b)
    parse_mythic(b)
    parse_boss_challenge(b)
    parse_guild(b)
    parse_growth_sinks(b)
    parse_rv_growth(b)
    parse_formal_boss_challenge(b)
    parse_formal_neural_roam(b)
    parse_formal_mapping_equipment_growth(b)
    parse_formal_strategy_growth(b)
    parse_formal_task_and_seven_day(b)
    parse_formal_level_reward_refs(b)
    parse_formal_drawcard(b)
    parse_formal_guild(b)
    parse_formal_legacy_equipment(b)
    finalize_coverage(b)
    exclude_stat_only_resources(b)
    exclude_policy_systems(b)

    summary_rows = build_summary_rows(b)
    _split_overview, split_rows_by_title = build_split_overview(b)
    display_extra_rows_by_title = build_display_extra_rows_by_title(b)
    module_outputs = write_module_files(split_rows_by_title, display_extra_rows_by_title)

    out_wb = openpyxl.Workbook()
    del out_wb[out_wb.sheetnames[0]]
    write_sheet(
        out_wb,
        "模块文件总览",
        ["模块", "系统", "记录数", "资源数", "方向分布", "价值分布(钻石)", "说明", "文件路径"],
        module_outputs,
    )
    write_sheet(out_wb, "总汇总_资源", SUMMARY_HEADERS, summary_rows)
    coverage_rows = [b.coverage[name] for name in src_wb.sheetnames]
    for name in sorted(k for k in b.coverage if k not in src_wb.sheetnames):
        coverage_rows.append(b.coverage[name])
    write_sheet(out_wb, "覆盖状态", COVER_HEADERS, coverage_rows)
    note_rows = [
        ["源表", SRC],
        ["生成时间口径", "系统明细从 Vgame经济框架.xlsx/正式配置只读；价值锚点从 01_源表/道具定价.xlsx 读取"],
        ["模块表目录", MODULE_DIR],
        ["模块文件", "每个模块独立 Excel；普通产销模块内含阅读摘要、产销阅读、资源汇总、机器明细；玩法模块新增玩法产出宽表；角色/专武/旅券/映射装备另拆阶段宽表子页签；机器明细保留校验追溯。"],
        ["玩法产出", "所有玩法模块按关卡/层/档位/奖励节点做宽表，分数/首通/结算/排行等产出结论节点优先置顶，再放过程收益和奖励引用；Drop/Reward 暂保留为奖励包入口。"],
        ["宽表冻结", "玩法产出冻结到奖励包/引用列，商店冻结到商品ID/条件列，养成阶段宽表冻结到周期/限制列，横向滚动时保留识别列。"],
        ["阅读排序", "模块产销阅读页、拆分页签和机器明细按 Lv/TargetLv/来源行等数字做自然排序，避免 Lv10 排在 Lv2 前。"],
        ["Drop/Reward", "登记引用；固定包内容可校验，随机包权重后续专项展开"],
        ["世界boss页", "历史设计页仍保留；BOSS挑战已补正式 BossDungeon Reward/BestReward 引用"],
        ["无限挑战", "neural_roam 已按用户裁决归入无限挑战（无限之旅）"],
        ["商业化", "用户裁决当前无商业化内容；月卡/付费商品/充值等暂不纳入当前 P4 补强"],
        ["道具定价", "01_源表/道具定价.xlsx 是唯一内部定价锚点，不导出独立索引页"],
        ["统计口径排除", "角色经验/专武经验为计算值，不是实物道具；从产销统计中排除，保留角色经验高/专武经验高等真实道具"],
        ["旅券副本邮票池", "旅券副本页手填的邮票本1-4具体掉落邮票已纳入玩法产出和机器明细，按候选掉落池引用处理，不计固定产出数量"],
        ["抽卡", "不计算产销消耗；由 21_抽卡_概率.xlsx 输出正式卡池总览、品质概率、保底规则、权重曲线和自选池。"],
        ["共鸣装备", "用户裁决为废弃系统；不进入产销总表，炮台模块仅保留炮台自身升级/突破材料。"],
        ["废弃玩法", "肉鸽（废弃）不纳入正式经济层"],
    ]
    write_sheet(out_wb, "口径说明", ["项目", "说明"], note_rows)
    write_sheet(out_wb, "追溯_全明细", LEDGER_HEADERS, b.ledger)
    out_wb.save(OUT)
    src_wb.close()
    price_wb.close()

    errors = verify_no_error_literals(OUT)
    if errors:
        raise RuntimeError("产物存在 Excel 错误值: %s" % "; ".join(errors[:10]))
    module_errors = []
    for output in module_outputs:
        module_path = output[-1]
        module_errors.extend(verify_no_error_literals(module_path))
    if module_errors:
        raise RuntimeError("模块产物存在 Excel 错误值: %s" % "; ".join(module_errors[:10]))

    write_report(b, summary_rows, module_outputs)
    print("合并表: 全资源产销总表生成完成，模块 Excel %d 个，明细 %d 行，资源汇总 %d 行" % (len(module_outputs), len(b.ledger), len(summary_rows)))
    print("[生成表] %s" % OUT)
    print("[模块目录] %s" % MODULE_DIR)
    print("[报告] %s" % REPORT)


if __name__ == "__main__":
    main()
