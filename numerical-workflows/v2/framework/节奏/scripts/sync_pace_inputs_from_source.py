# -*- coding: utf-8 -*-
"""
sync_pace_inputs_from_source.py — 节奏输入锚点同步

把旧源 `Vgame新手引导以及开启节奏.xlsx` 中已经存在的主线章节和
天数锚点补入节奏参数基线 MD 的 `主角等级_输入`。

规则:
  - 章节只补空值；天数按旧源有效逐日表重算，清掉误读的查找区数值。
  - 对应主线章节来自 `养成进度预估`。
  - 对应天数来自旧源 `主角等级` 的天数等级表，取首次达到该等级的天数。
  - 旧源后半段有“总经验→实际等级”查找区，不属于天数表；只读取每天经验非空的逐日表。
"""
import argparse
import io
import os
import sys
import warnings

warnings.filterwarnings("ignore")

import openpyxl
from openpyxl.styles import Font, PatternFill

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
PACE_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(PACE_DIR)
NUM_DIR = os.path.dirname(V2_DIR)
sys.path.insert(0, V2_DIR)
from _shared.md_parameter_reader import (
    load_parameter_workbook,
    parameter_md_path,
    save_parameter_workbook,
)

PACE_PARAM = parameter_md_path("节奏")
SRC_FILE = os.path.join(NUM_DIR, "Vgame新手引导以及开启节奏.xlsx")
REPORT = os.path.join(PACE_DIR, "_reports", "P节奏_输入锚点同步.md")


def is_empty(v):
    return v is None or v == ""


def read_growth_context():
    wb = openpyxl.load_workbook(SRC_FILE, data_only=True)
    ws = wb["养成进度预估"]
    out = {}
    for r in range(2, ws.max_row + 1):
        lv = ws.cell(r, 1).value
        if not isinstance(lv, (int, float)):
            continue
        out[int(lv)] = {
            "chapter": ws.cell(r, 2).value,
            "stage": ws.cell(r, 3).value,
            "level_id": ws.cell(r, 4).value,
            "monster_lv": ws.cell(r, 5).value,
        }
    wb.close()
    return out


def read_day_curve():
    wb = openpyxl.load_workbook(SRC_FILE, data_only=True)
    ws = wb["主角等级"]
    rows = []
    for r in range(21, ws.max_row + 1):
        day = ws.cell(r, 14).value
        lv = ws.cell(r, 15).value
        exp = ws.cell(r, 16).value
        daily_exp = ws.cell(r, 17).value
        if not isinstance(day, (int, float)) or not isinstance(lv, (int, float)):
            continue
        if daily_exp in (None, ""):
            continue
        rows.append({
            "day": int(day),
            "level": int(lv),
            "exp": exp,
            "daily_exp": daily_exp,
        })
    wb.close()
    return rows


def earliest_day_for_level(level, day_curve):
    for row in day_curve:
        if row["level"] >= level:
            return row["day"]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="确认把源表锚点写入节奏参数 MD")
    args = parser.parse_args()
    growth = read_growth_context()
    day_curve = read_day_curve()

    wb = load_parameter_workbook(PACE_PARAM, data_only=False)
    ws = wb["主角等级_输入"]

    bold = Font(bold=True)
    hf = PatternFill("solid", fgColor="D9E1F2")
    source_fill = PatternFill("solid", fgColor="E2EFDA")

    ws.cell(4, 1, "等级")
    ws.cell(4, 2, "每级成长")
    ws.cell(4, 3, "升级返还体力")
    ws.cell(4, 4, "对应主线章节")
    ws.cell(4, 5, "对应天数")
    for c in range(1, 6):
        ws.cell(4, c).font = bold
        ws.cell(4, c).fill = hf

    chapter_filled = 0
    day_filled = 0
    day_missing = []
    for r in range(5, ws.max_row + 1):
        lv = ws.cell(r, 1).value
        if not isinstance(lv, (int, float)):
            continue
        lv = int(lv)

        ctx = growth.get(lv, {})
        if is_empty(ws.cell(r, 4).value) and not is_empty(ctx.get("chapter")):
            ws.cell(r, 4, ctx["chapter"])
            ws.cell(r, 4).fill = source_fill
            chapter_filled += 1

        day = earliest_day_for_level(lv, day_curve)
        if day is not None:
            ws.cell(r, 5, day)
            ws.cell(r, 5).fill = source_fill
            day_filled += 1
        elif is_empty(ws.cell(r, 5).value):
            day_missing.append(lv)

    ws.column_dimensions["E"].width = 12
    if args.write:
        save_parameter_workbook(PACE_PARAM, wb)
    wb.close()

    md = [
        "# 节奏输入锚点同步",
        "",
        "> 从 `Vgame新手引导以及开启节奏.xlsx` 补充 `03_沉淀MD/参数基线/节奏参数基线.md` 的章节/天数上下文锚点；章节只补空值，天数按有效逐日表重算。",
        "",
        "## 同步结果",
        "",
        "| 项目 | 数量 |",
        "|---|---:|",
        f"| 补入对应主线章节 | {chapter_filled} |",
        f"| 补入对应天数 | {day_filled} |",
        f"| 旧源天数曲线覆盖天数 | {len(day_curve)} |",
        "",
        "## 仍缺",
        "",
        "- 旧源逐日表当前覆盖到 Day%d / Lv%d；更高等级已保留为空，等待后续玩家进度模拟或正式日程参数补齐。" % (day_curve[-1]["day"], day_curve[-1]["level"]),
        "",
        "## 来源",
        "",
        "- `Vgame新手引导以及开启节奏.xlsx / 主角等级`",
        "- `Vgame新手引导以及开启节奏.xlsx / 养成进度预估`",
    ]
    if day_missing:
        md.append("")
        md.append("缺少天数的等级: " + ", ".join("Lv%d" % lv for lv in day_missing))

    if args.write:
        os.makedirs(os.path.dirname(REPORT), exist_ok=True)
        with open(REPORT, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

    print("节奏输入锚点同步预演: 章节补入%d, 天数同步%d" % (chapter_filled, day_filled))
    if args.write:
        print("[参数MD] %s" % PACE_PARAM)
        print("[报告]   %s" % REPORT)
    else:
        print("[DRY-RUN] 未修改 MD；确认后使用 --write")


if __name__ == "__main__":
    main()
