# -*- coding: utf-8 -*-
"""爬塔首通与挂机奖励 QA 数值表生成器。

面向 QA 交付：把 `06_最终配置/爬塔` 评审镜像展开成可直接对照测试的
逐层表格（1-100 层首通奖励、逐层挂机日产、节点展示字段），并内置
CHG-044 验收基准断言。不做产销核算、不做汇总账本。
"""

import io
import os
import sys
from collections import defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

HERE = os.path.dirname(os.path.abspath(__file__))
ECONOMY_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(ECONOMY_DIR)
sys.path.insert(0, HERE)

# gen_economy_ledger 会在导入时统一包裹 UTF-8 stdout，这里不再重复包裹。
import gen_economy_ledger as ledger

OUT = os.path.join(ECONOMY_DIR, "生成_爬塔首通挂机奖励.xlsx")
REPORT = os.path.join(ECONOMY_DIR, "_reports", "P爬塔QA奖励表_生成与对照.md")

SHOW_ITEM_NAMES = {106: "旅券", 103: "熔晶"}
REWARD_COLUMNS = [
    (1074, "房车零件"),
    (2, "元晶"),
    (106, "旅券"),
    (103, "熔晶"),
    (3027, "指南材料自选箱"),
    (1156, "高阶课程笔记"),
    (1157, "精英课程笔记"),
]


def mirror_item_name(item_id, resolved):
    if resolved and not str(resolved).startswith("ItemId "):
        return resolved
    return ledger.TOWER_ITEM_FALLBACK_NAMES.get(item_id, resolved)


def build_first_clear_rows():
    first_path = os.path.join(ledger.TOWER_MIRROR_DIR, "TowerFirstReward.xlsx")
    drop_path = os.path.join(ledger.TOWER_MIRROR_DIR, "Drop_dungeon.xlsx")
    entries = ledger.drop_entries_by_id(drop_path)
    first_rows = [r for r in ledger.row_dicts(first_path, "Sheet1") if r.get("ID") not in (None, "")]
    if len(first_rows) != 200:
        raise RuntimeError("TowerFirstReward 镜像应为 200 层，实际 %s" % len(first_rows))
    totals = defaultdict(float)
    detail = {}
    for row in sorted(first_rows, key=lambda r: ledger.to_int(r.get("Layer"))):
        layer = ledger.to_int(row.get("Layer"))
        drop_id = ledger.to_int(row.get("DropId"))
        items = defaultdict(float)
        notes = []
        for entry in entries.get(drop_id, []):
            if entry["invalid"]:
                continue
            qty = entry["qty"]
            try:
                amount = float(str(qty).rstrip("+")) if isinstance(qty, str) else float(qty)
            except (TypeError, ValueError):
                continue
            items[int(entry["item_id"])] += amount
            totals[int(entry["item_id"])] += amount
            notes.append("%s(%s)×%s" % (
                mirror_item_name(entry["item_id"], entry["item"]), entry["item_id"], qty))
        show_id = ledger.to_int(row.get("ShowRewardItemsId"))
        detail[layer] = {
            "items": items,
            "detail": "；".join(notes),
            "show": "%s(%s)" % (SHOW_ITEM_NAMES.get(show_id, str(show_id or "")), show_id) if show_id else "",
            "drop_id": drop_id,
        }
    expected = {str(k): float(v) for k, v in ledger.TOWER_FIRST_CLEAR_TOTALS.items()}
    actual_ids = {str(k) for k in totals}
    if actual_ids != set(expected) or any(abs(totals[int(k)] - v) > 1e-6 for k, v in expected.items()):
        raise RuntimeError(
            "首通总量与 CHG-044 验收不一致: %s" % {k: totals[int(k)] for k in sorted(expected, key=int)}
        )
    valid_rows = sum(1 for layer in detail for _ in detail[layer]["items"])
    return detail, totals, valid_rows


def build_idle_rows():
    idle_path = os.path.join(ledger.TOWER_MIRROR_DIR, "TowerIdleRewards.xlsx")
    drop_path = os.path.join(ledger.TOWER_MIRROR_DIR, "Drop_dungeon.xlsx")
    entries = ledger.drop_entries_by_id(drop_path)
    pool_entries = [e for e in entries.get(ledger.TOWER_IDLE_POOL_DROP_ID, []) if not e["invalid"]]
    if len(pool_entries) != 5:
        raise RuntimeError("挂机材料池应为 5 个等权项，实际 %s" % len(pool_entries))
    idle_rows = [r for r in ledger.row_dicts(idle_path, "TowerIdleRewards") if r.get("ID") not in (None, "")]
    if len(idle_rows) != 200:
        raise RuntimeError("TowerIdleRewards 镜像应为 200 层，实际 %s" % len(idle_rows))
    result = {}
    for row in idle_rows:
        layer = ledger.to_int(row.get("LayerLimitMin"))
        gold_per_day = None
        parts_per_day = None
        for item_text, num_text, time_text in zip(
            [p for p in str(row.get("IdleRewards") or "").split(";") if p],
            [p for p in str(row.get("IdleRewardsNum") or "").split(";") if p],
            [p for p in str(row.get("IdleRewardsTime") or "").split(";") if p],
        ):
            per_day = float(num_text) * 86400.0 / float(time_text)
            if item_text == "1":
                gold_per_day = int(per_day)
            elif item_text == "1074":
                parts_per_day = int(per_day)
        pool_per_cycle = ledger.to_int(row.get("DropIdNum"))
        pool_per_day = None
        if row.get("DropId") and pool_per_cycle:
            cycle_seconds = float(str(row.get("DropIdTimes") or "").split(";")[0])
            pool_per_day = round(pool_per_cycle * 86400.0 / cycle_seconds, 2)
        result[layer] = {
            "gold": gold_per_day,
            "parts": parts_per_day,
            "pool_times": pool_per_day,
            "pool_expect": round(pool_per_day / 5, 2) if pool_per_day else 0,
        }
    return result, pool_entries


def append_sheet(wb, title, headers, rows):
    ws = wb.create_sheet(title)
    ws.append(headers)
    fill = PatternFill("solid", fgColor="D9E1F2")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in rows:
        ws.append(row)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.column_dimensions["A"].width = 10
    for idx in range(2, len(headers) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = 16
    if "奖励明细" in headers:
        ws.column_dimensions[openpyxl.utils.get_column_letter(headers.index("奖励明细") + 1)].width = 58
    if "说明" in headers:
        ws.column_dimensions[openpyxl.utils.get_column_letter(headers.index("说明") + 1)].width = 44
    return ws


def main():
    detail, totals, valid_rows = build_first_clear_rows()
    idle, pool_entries = build_idle_rows()
    if valid_rows != ledger.TOWER_FIRST_CLEAR_ROWS:
        raise RuntimeError("首通有效行应为 %s，实际 %s" % (ledger.TOWER_FIRST_CLEAR_ROWS, valid_rows))

    headers = ["层"] + ["%s(%s)" % (name, item_id) for item_id, name in REWARD_COLUMNS] + ["奖励明细", "节点展示", "首通DropId"]
    rows = []
    for layer in sorted(detail):
        info = detail[layer]
        rows.append(
            [layer]
            + [int(info["items"].get(item_id, 0)) or "" for item_id, _name in REWARD_COLUMNS]
            + [info["detail"], info["show"], info["drop_id"]]
        )

    idle_headers = ["层", "金币/日(1)", "房车零件/日(1074)", "材料池抽取次数/日", "单材料期望/日", "说明"]
    idle_sheet_rows = []
    for layer in sorted(idle):
        info = idle[layer]
        note = ""
        if info["pool_times"]:
            note = "材料池%s等权五选一（1075-1079各20%%），单材料期望=次数/5" % ledger.TOWER_IDLE_POOL_DROP_ID
        idle_sheet_rows.append([
            layer,
            info["gold"] if info["gold"] is not None else "",
            info["parts"] if info["parts"] is not None else "",
            info["pool_times"] if info["pool_times"] else "不产出",
            info["pool_expect"] if info["pool_times"] else "",
            note,
        ])

    basis_rows = [
        ["数据来源", "06_最终配置/爬塔（TowerFirstReward + Drop_dungeon + TowerIdleRewards 评审镜像；1-100层CHG-044 + 101-200层2026-09-20扩展）"],
        ["奖励结构", "账号级 1-200 层一次性首通（101-200层按第100层面额平推）；挂机按历史最高层结算"],
        ["首通有效行数", "%s（生成器已断言）" % ledger.TOWER_FIRST_CLEAR_ROWS],
    ]
    for item_id, name in REWARD_COLUMNS:
        basis_rows.append(["全塔首通合计·%s(%s)" % (name, item_id), int(totals.get(item_id, 0))])
    basis_rows += [
        ["验收基准", "2026-09-20全塔200层：元晶17,300/熔晶17/旅券120/房车零件12,600/自选箱1,550/高阶课程笔记350/精英课程笔记25；逐项断言已通过（1-100层CHG-044口径不变）"],
        ["节点展示规则", "ShowRewardItemsId：尾数5层展示旅券(106)，尾数0层展示熔晶(103)，其余层为空；仅控制左侧节点展示（101-200层同规则）"],
        ["挂机说明", "1-100层逐层日产不变；101-200层金币每层+400、房车零件每5层+1、材料每10层+2（200层=230,000金币/270零件/80材料）"],
        ["停用口径", "旧每周到达/通关扫荡/爬塔商店/赛季奖励已删除，镜像##停用行不计入；UIlevel 首通预览与 TowerFirstReward 发放链路一致，不双发"],
    ]

    wb = openpyxl.Workbook()
    del wb[wb.sheetnames[0]]
    append_sheet(wb, "首通奖励_逐层", headers, rows)
    append_sheet(wb, "挂机产出_逐层", idle_headers, idle_sheet_rows)
    append_sheet(wb, "验收基准", ["项目", "值/说明"], basis_rows)
    wb.save(OUT)

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    lines = [
        "# 爬塔 QA 奖励表 · 生成与对照",
        "",
        "> 从 `06_最终配置/爬塔` 评审镜像生成 QA 逐层测试表；内置 200 层全塔验收断言（1-100层CHG-044 + 101-200层2026-09-20平推扩展）。",
        "",
        "- 首通：1-200 层逐层表 %d 行；全塔合计 房车零件12,600/元晶17,300/旅券120/熔晶17/自选箱1,550/高阶课程笔记350/精英课程笔记25。" % len(rows),
        "- 挂机：1-100层逐层日产不变；101-200层金币+400/层、零件+1每5层、材料+2每10层（200层=230,000/270/80）。",
        "- 本表不做产销核算与汇总账本；经济视角仍在 `经济/模块产销表/08_玩法_爬塔.xlsx`（内部）。",
        "",
        "## 产物",
        "",
        "- `经济/生成_爬塔首通挂机奖励.xlsx`",
    ]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("爬塔QA奖励表生成完成：首通 %d 层，挂机 %d 层，验收断言全部通过" % (len(rows), len(idle_sheet_rows)))
    print("[生成表] %s" % OUT)
    print("[报告] %s" % REPORT)


if __name__ == "__main__":
    main()
