# -*- coding: utf-8 -*-
"""
gen_difficulty_all.py — 全玩法难度线 合并总表

输出一张统一入口:
  节奏/全玩法难度线.xlsx

规则:
  - 不回写任何源表。
  - 能拿到怪物等级的玩法，记录怪物等级和战斗系数。
  - 只有手填难度、奖励难度档或分层模型的玩法，也纳入总表，但标记口径。
  - 世界boss按当前项目口径不作为正式玩法；原「世界boss」页只抽取为 Boss挑战奖励难度档。
"""
import io
import os
import sys
import warnings
from collections import Counter, OrderedDict, defaultdict

warnings.filterwarnings("ignore")

import openpyxl
from openpyxl.styles import Font, PatternFill

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
PACE_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(PACE_DIR)
NUM_DIR = os.path.dirname(V2_DIR)

OUT = os.path.join(PACE_DIR, "全玩法难度线.xlsx")
REPORT = os.path.join(PACE_DIR, "_reports", "P难度线_全玩法合并.md")
BATTLE_SRC = os.path.join(NUM_DIR, "Vgame基本战斗框架.xlsx")
ECON_SRC = os.path.join(NUM_DIR, "Vgame经济框架.xlsx")

HEADERS = [
    "玩法",
    "玩法分组",
    "进度单位",
    "进度",
    "对应主角等级",
    "怪物等级",
    "难度系数/档位",
    "生命系数",
    "攻击系数",
    "防御系数",
    "来源页",
    "口径",
    "备注",
]


def blank(v):
    return "" if v is None else v


def add(rows, play, group, unit, progress, player_lv=None, monster_lv=None, difficulty=None,
        hp=None, atk=None, dfs=None, source="", basis="", note=""):
    rows.append([
        play, group, unit, progress, blank(player_lv), blank(monster_lv), blank(difficulty),
        blank(hp), blank(atk), blank(dfs), source, basis, note
    ])


def collect_mainline(wb, rows):
    ws = wb["玩法难度线"]
    for r in range(18, ws.max_row + 1):
        ch, stage = ws.cell(r, 2).value, ws.cell(r, 3).value
        if stage is not None:
            add(rows, "主线", "主线", "主线关卡", f"第{ch}章-{stage}关",
                ws.cell(r, 4).value, ws.cell(r, 5).value, None,
                ws.cell(r, 6).value, ws.cell(r, 7).value, ws.cell(r, 8).value,
                "Vgame基本战斗框架.xlsx/玩法难度线", "怪物等级线", "")

        hard_ch, hard_stage = ws.cell(r, 10).value, ws.cell(r, 11).value
        if hard_stage is not None:
            add(rows, "困难主线", "主线", "困难关卡", f"第{hard_ch}章-{hard_stage}关",
                None, ws.cell(r, 14).value, None,
                ws.cell(r, 15).value, ws.cell(r, 16).value, ws.cell(r, 17).value,
                "Vgame基本战斗框架.xlsx/玩法难度线", "怪物等级线",
                f"对应主线章节{ws.cell(r, 12).value}")


def collect_difficulty_block(ws, rows, play, group, start_row, end_row, source, note=""):
    for r in range(start_row, end_row + 1):
        difficulty = ws.cell(r, 20).value
        if difficulty is None:
            continue
        add(rows, play, group, "难度档", f"难度{int(difficulty)}",
            ws.cell(r, 21).value, ws.cell(r, 22).value, difficulty,
            ws.cell(r, 23).value, ws.cell(r, 24).value, ws.cell(r, 25).value,
            source, "怪物等级线", note)


def collect_battle_mode_lines(wb, rows):
    ws = wb["玩法难度线"]
    src = "Vgame基本战斗框架.xlsx/玩法难度线"
    collect_difficulty_block(ws, rows, "资源副本-金币", "稳定成长玩法", 18, 26, src, "与武将经验副本共用战斗难度线")
    collect_difficulty_block(ws, rows, "资源副本-角色经验", "稳定成长玩法", 18, 26, src, "与金币副本共用战斗难度线")
    collect_difficulty_block(ws, rows, "资源副本-专武经验", "稳定成长玩法", 32, 40, src, "")
    collect_difficulty_block(ws, rows, "旅券副本", "稳定成长玩法", 45, 54, src, "")
    collect_difficulty_block(ws, rows, "映射装备副本", "稳定成长玩法", 59, 68, src, "源页旧名为主角装备本")

    # 大秘境在同一页使用独立区块：Z:AE = 难度/主角等级/怪物等级/系数。
    for r in range(18, 43):
        difficulty = ws.cell(r, 27).value
        if difficulty is None:
            continue
        add(rows, "大秘境", "验证玩法", "层数", f"第{int(difficulty)}层",
            ws.cell(r, 28).value, ws.cell(r, 29).value, difficulty,
            ws.cell(r, 30).value, ws.cell(r, 31).value, ws.cell(r, 32).value,
            src, "怪物等级线", "28天季节制爬升玩法，源表当前给 25 层战斗等级")


def collect_infinite(wb, rows):
    ws = wb["无限挑战难度线"]
    r = 11
    while r <= ws.max_row:
        wave, lv = ws.cell(r, 2).value, ws.cell(r, 3).value
        if isinstance(wave, (int, float)) and lv is not None:
            add(rows, "无限挑战", "验证玩法", "大波数", f"第{int(wave)}波",
                None, lv, None, None, None, None,
                "Vgame基本战斗框架.xlsx/无限挑战难度线", "怪物等级线", "怪物用标准模型")
        r += 1


def collect_tower(wb, rows):
    ws = wb["爬塔难度线"]
    type_name = {0: "小层", 1: "中层", 2: "大层"}
    for r in range(20, 120):
        floor, lv = ws.cell(r, 12).value, ws.cell(r, 22).value
        if floor is None or lv is None:
            continue
        layer_type = type_name.get(ws.cell(r, 11).value, "")
        add(rows, "爬塔", "验证玩法", "层数", f"第{int(floor)}层",
            ws.cell(r, 14).value, lv, None, None, None, None,
            "Vgame基本战斗框架.xlsx/爬塔难度线", "怪物等级线",
            f"层型:{layer_type} 奖励系数{ws.cell(r, 19).value}")


def collect_arena(econ_wb, rows):
    ws = econ_wb["竞技场分层"]
    for r in range(20, 24):
        player_type = ws.cell(r, 1).value
        if not player_type:
            continue
        add(rows, "竞技场（PVPVE）", "验证玩法", "玩家分层", player_type,
            ws.cell(r, 4).value, None, ws.cell(r, 11).value, None, None, None,
            "Vgame经济框架.xlsx/竞技场分层", "手填分层模型",
            f"{ws.cell(r, 5).value}; 预计段位:{ws.cell(r, 12).value}; {ws.cell(r, 13).value}")


def collect_boss_challenge(econ_wb, rows):
    ws = econ_wb["世界boss"]
    for r in range(6, ws.max_row + 1):
        boss_id, boss_name, difficulty = ws.cell(r, 1).value, ws.cell(r, 2).value, ws.cell(r, 3).value
        if boss_id is None or difficulty is None:
            continue
        add(rows, "BOSS挑战", "验证玩法", "Boss难度", f"{boss_name}-难度{int(difficulty)}",
            None, None, difficulty, None, None, None,
            "Vgame经济框架.xlsx/世界boss", "奖励难度档",
            f"原页名世界boss，按当前口径仅抽取为Boss挑战奖励难度档；综合价值{blank(ws.cell(r, 16).value)}；战斗怪物等级待补")


def collect_resource_reward_layers(econ_wb, rows):
    ws = econ_wb["资源、装备副本"]
    blocks = [
        ("资源副本-金币", 6, 14),
        ("资源副本-角色经验", 20, 28),
        ("资源副本-专武经验", 35, 43),
    ]
    for play, start, end in blocks:
        for r in range(start, end + 1):
            diff = ws.cell(r, 2).value
            if diff is None:
                continue
            add(rows, play, "稳定成长玩法", "奖励难度", f"奖励档{int(diff)}",
                ws.cell(r, 4).value, None, ws.cell(r, 1).value, None, None, None,
                "Vgame经济框架.xlsx/资源、装备副本", "手填奖励难度",
                f"消耗体力{blank(ws.cell(r, 3).value)}; 玩家经验{blank(ws.cell(r, 5).value)}")

    ws = econ_wb["旅券副本"]
    for r in range(6, 16):
        diff = ws.cell(r, 3).value
        if diff is None:
            continue
        add(rows, "旅券副本", "稳定成长玩法", "奖励难度", f"奖励档{int(diff)}",
            ws.cell(r, 5).value, None, ws.cell(r, 2).value, None, None, None,
            "Vgame经济框架.xlsx/旅券副本", "手填奖励难度",
            f"体力{blank(ws.cell(r, 4).value)}; 总价值{blank(ws.cell(r, 21).value)}")

    ws = econ_wb["映射装备副本"]
    for r in range(5, 35):
        floor = ws.cell(r, 2).value
        if floor is None:
            continue
        add(rows, "映射装备副本", "稳定成长玩法", "奖励层", f"第{int(floor)}层",
            None, None, floor, None, None, None,
            "Vgame经济框架.xlsx/映射装备副本", "手填奖励层",
            f"体力{blank(ws.cell(r, 3).value)}; 掉落装备总数{blank(ws.cell(r, 5).value)}")


def build_status(rows):
    formal = OrderedDict([
        ("主线", ("主线", "已覆盖怪物等级")),
        ("困难主线", ("主线", "已覆盖怪物等级")),
        ("资源副本-金币", ("稳定成长玩法", "已覆盖怪物等级 + 奖励难度")),
        ("资源副本-角色经验", ("稳定成长玩法", "已覆盖怪物等级 + 奖励难度")),
        ("资源副本-专武经验", ("稳定成长玩法", "已覆盖怪物等级 + 奖励难度")),
        ("旅券副本", ("稳定成长玩法", "已覆盖怪物等级 + 奖励难度")),
        ("映射装备副本", ("稳定成长玩法", "已覆盖怪物等级 + 奖励层")),
        ("无限挑战", ("验证玩法", "已覆盖怪物等级")),
        ("竞技场（PVPVE）", ("验证玩法", "已覆盖手填分层模型，未见怪物等级线")),
        ("爬塔", ("验证玩法", "已覆盖怪物等级")),
        ("大秘境", ("验证玩法", "已覆盖怪物等级")),
        ("BOSS挑战", ("验证玩法", "已覆盖奖励难度档，战斗怪物等级待补")),
    ])
    cnt = Counter(r[0] for r in rows)
    monster_cnt = Counter(r[0] for r in rows if r[5] not in ("", None))
    out = []
    for play, (group, status) in formal.items():
        out.append([play, group, cnt.get(play, 0), monster_cnt.get(play, 0), status])
    out.append(["世界boss", "非当前正式玩法", 0, 0, "按 vgame-core-understanding 标记为非正式/历史内容，不单独纳入"])
    out.append(["肉鸽", "废弃玩法", 0, 0, "源页已标记废弃，不纳入"])
    return out


def write_workbook(rows, status_rows):
    wb = openpyxl.Workbook()
    bold = Font(bold=True)
    hf = PatternFill("solid", fgColor="D9E1F2")
    note_fill = PatternFill("solid", fgColor="FFF2CC")

    ws = wb.active
    ws.title = "总览"
    ws.append(["全玩法难度线 (一行=玩法×进度; 怪物等级/手填难度/奖励档统一入口)"])
    ws.append([])
    ws.append(HEADERS)
    for c in range(1, len(HEADERS) + 1):
        ws.cell(3, c).font = bold
        ws.cell(3, c).fill = hf
    for row in rows:
        ws.append(row)
        if row[5] in ("", None):
            for c in range(1, len(HEADERS) + 1):
                ws.cell(ws.max_row, c).fill = note_fill
    ws.freeze_panes = "A4"
    widths = [16, 14, 12, 18, 12, 10, 14, 10, 10, 10, 30, 14, 58]
    for width, col in zip(widths, "ABCDEFGHIJKLM"):
        ws.column_dimensions[col].width = width

    ws_status = wb.create_sheet("覆盖状态")
    ws_status.append(["玩法", "分组", "总行数", "含怪物等级行数", "状态"])
    for c in range(1, 6):
        ws_status.cell(1, c).font = bold
        ws_status.cell(1, c).fill = hf
    for row in status_rows:
        ws_status.append(row)
    for width, col in zip([18, 14, 10, 14, 58], "ABCDE"):
        ws_status.column_dimensions[col].width = width

    by_play = OrderedDict()
    for row in rows:
        by_play.setdefault(row[0], []).append(row)
    for play, play_rows in by_play.items():
        title = play.replace("（", "(").replace("）", ")")[:31]
        ws_p = wb.create_sheet(title)
        ws_p.append(HEADERS)
        for c in range(1, len(HEADERS) + 1):
            ws_p.cell(1, c).font = bold
            ws_p.cell(1, c).fill = hf
        for row in play_rows:
            ws_p.append(row)
        ws_p.freeze_panes = "A2"
        for width, col in zip(widths, "ABCDEFGHIJKLM"):
            ws_p.column_dimensions[col].width = width

    wb.save(OUT)


def write_report(rows, status_rows):
    cnt = Counter(r[0] for r in rows)
    rng = defaultdict(lambda: [10 ** 9, -10 ** 9])
    for r in rows:
        lv = r[5]
        if isinstance(lv, (int, float)):
            rng[r[0]][0] = min(rng[r[0]][0], lv)
            rng[r[0]][1] = max(rng[r[0]][1], lv)

    lines = [
        "# 全玩法难度线 合并总表",
        "",
        "> 各正式玩法难度线汇成一张长表(`节奏/全玩法难度线.xlsx`)。怪物等级、手填难度档、竞技场分层和 Boss挑战奖励难度档统一入口；源表只读。",
        "",
        "## 覆盖状态",
        "",
        "| 玩法 | 分组 | 总行数 | 含怪物等级行数 | 状态 |",
        "|---|---|---:|---:|---|",
    ]
    for play, group, total, monster_total, status in status_rows:
        lines.append(f"| {play} | {group} | {total} | {monster_total} | {status} |")

    lines += ["", "## 怪物等级范围", "", "| 玩法 | 行数 | 怪物等级范围 |", "|---|---:|---|"]
    for play in cnt:
        if rng[play][0] != 10 ** 9:
            lines.append(f"| {play} | {cnt[play]} | {rng[play][0]}~{rng[play][1]} |")
    lines += [
        "",
        f"合计 {len(rows)} 行。",
        "",
        "- 黄色行表示当前没有怪物等级，属于手填奖励难度、竞技场分层或 Boss挑战奖励难度档。",
        "- `BOSS挑战` 已纳入奖励难度档，但还缺战斗怪物等级/系数源。",
        "- `竞技场（PVPVE）` 已纳入赛季分层模型，但战斗难度需要后续回到 PVPVE 关卡/怪物配置补齐。",
    ]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    for line in lines:
        print(line)
    print(f"\n[合并表] {OUT}")


def main():
    battle_wb = openpyxl.load_workbook(BATTLE_SRC, data_only=True)
    econ_wb = openpyxl.load_workbook(ECON_SRC, data_only=True)
    rows = []
    collect_mainline(battle_wb, rows)
    collect_battle_mode_lines(battle_wb, rows)
    collect_infinite(battle_wb, rows)
    collect_tower(battle_wb, rows)
    collect_arena(econ_wb, rows)
    collect_boss_challenge(econ_wb, rows)
    collect_resource_reward_layers(econ_wb, rows)
    battle_wb.close()
    econ_wb.close()

    status_rows = build_status(rows)
    write_workbook(rows, status_rows)
    write_report(rows, status_rows)


if __name__ == "__main__":
    main()
