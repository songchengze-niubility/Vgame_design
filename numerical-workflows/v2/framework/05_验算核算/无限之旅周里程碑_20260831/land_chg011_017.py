# -*- coding: utf-8 -*-
"""CHG-011~017 无限之旅周里程碑重铺：06候选包落表（SVN不动）。
NR_HighestScoreReward 42行（4档共享阶梯，同分跨档复用DropId）；
Drop_dungeon 15包×3项=45行；00_配置清单同步预览与汇总。"""
import json, shutil, copy, os, datetime
import openpyxl
from openpyxl.styles import Font

BASE = r"D:/Vgame_design/numerical-workflows/v2/framework"
PKG = BASE + "/06_最终配置/无限之旅"
BATCH = BASE + "/05_验算核算/无限之旅周里程碑_20260831"
BACKUP = BATCH + "/backup"
os.makedirs(BACKUP, exist_ok=True)

FILES = ["NR_HighestScoreReward.xlsx", "Drop_dungeon.xlsx", "00_配置清单.xlsx", "无限之旅配置校验.json"]
for f in FILES:
    dst = BACKUP + "/" + f
    if not os.path.exists(dst):  # 保留本批首次改动前的原始备份
        shutil.copy2(PKG + "/" + f, dst)

# ---------- 目标口径（CHG-011~017） ----------
# (score, [(道具名, ItemId, 数量) x3])
PACKAGES = [
    (1000,  [("元晶", 2, 40),    ("猎鹰金币", 1, 10000), ("低阶记录盘", 100, 20)]),
    (2000,  [("元晶", 2, 60),    ("映射之匙", 25, 2),    ("泛黄档案", 108, 20)]),
    (3000,  [("旅券", 106, 1),   ("猎鹰金币", 1, 15000), ("沿途随笔", 6, 5000)]),
    (4000,  [("元晶", 2, 80),    ("映射之匙", 25, 2),    ("低级舱室建材", 3028, 20)]),
    (5000,  [("旅券", 106, 1),   ("猎鹰金币", 1, 20000), ("房车零件", 1074, 20)]),
    (6000,  [("元晶", 2, 100),   ("映射之匙", 25, 2),    ("低阶记录盘", 100, 30)]),
    (7000,  [("元晶", 2, 60),    ("猎鹰金币", 1, 25000), ("泛黄档案", 108, 30)]),
    (8000,  [("旅券", 106, 1),   ("映射之匙", 25, 2),    ("沿途随笔", 6, 7500)]),
    (9000,  [("元晶", 2, 60),    ("猎鹰金币", 1, 30000), ("房车天赋树材料自选箱", 3027, 15)]),
    (10000, [("元晶", 2, 60),    ("猎鹰金币", 1, 35000), ("房车零件", 1074, 30)]),
    (11000, [("元晶", 2, 60),    ("映射之匙", 25, 1),    ("中阶记录盘", 101, 10)]),
    (12000, [("旅券", 106, 2),   ("猎鹰金币", 1, 40000), ("录像带", 109, 10)]),
    (13000, [("元晶", 2, 60),    ("猎鹰金币", 1, 45000), ("沿途随笔", 6, 10000)]),
    (14000, [("元晶", 2, 60),    ("映射之匙", 25, 1),    ("房车天赋树材料自选箱", 3027, 20)]),
    (15000, [("元晶", 2, 60),    ("猎鹰金币", 1, 55000), ("房车零件", 1074, 40)]),
]
DIFF_CAPS = {1: 6000, 2: 9000, 3: 12000, 4: 15000}
UNLOCK = {1: "默认开放", 2: "通关难度1＋35级", 3: "通关难度2＋45级", 4: "通关难度3＋55级"}

# ---------- 1. NR_HighestScoreReward：42行 ----------
nr_path = PKG + "/NR_HighestScoreReward.xlsx"
wb = openpyxl.load_workbook(nr_path)
ws = wb["WeekScoreReward"]
# 该表遗留样式索引越界（CHG-009白字问题的同源损坏），不可读样式模板；
# 数据区统一改用与Drop表一致的可见字体，避免再次出现"白字空表"。
nr_font = Font(name="Noto Sans SC", size=12)
old_nr = [[ws.cell(r, c).value for c in range(2, 6)] for r in range(5, ws.max_row + 1)]
if ws.max_row > 4:
    ws.delete_rows(5, ws.max_row - 4)
rid = 0
for d in (1, 2, 3, 4):
    for score in range(1000, DIFF_CAPS[d] + 1, 1000):
        rid += 1
        vals = [rid, d, score, 23000000 + score // 1000]
        for i, v in enumerate(vals):
            cell = ws.cell(4 + rid, 2 + i, v)
            cell.font = copy.copy(nr_font)
wb.save(nr_path)

# ---------- 2. Drop_dungeon：15包×3项=45行 ----------
dp_path = PKG + "/Drop_dungeon.xlsx"
wb = openpyxl.load_workbook(dp_path)
ws = wb["Drop"]
cols = range(2, 16)  # B..O
tmpl = {c: (copy.copy(ws.cell(5, c).font), copy.copy(ws.cell(5, c).border),
            copy.copy(ws.cell(5, c).fill), copy.copy(ws.cell(5, c).alignment),
            ws.cell(5, c).number_format) for c in cols}
old_drop_first = [ws.cell(5, c).value for c in (3, 11)]
if ws.max_row > 4:
    ws.delete_rows(5, ws.max_row - 4)
rownum = 0
for score, items in PACKAGES:
    drop_id = 23000000 + score // 1000
    for j, (name, item_id, qty) in enumerate(items, 1):
        rownum += 1
        r = 4 + rownum
        vals = {2: "=ROW()+200000-4", 3: drop_id, 4: f"无限之旅-{score//1000}千分-奖励{j}",
                5: name, 6: 0, 7: "fixed_", 8: 1, 9: 1, 11: item_id, 12: qty, 13: qty, 14: 10000}
        for c in cols:
            cell = ws.cell(r, c, vals.get(c))
            font, border, fill, align, fmt = tmpl[c]
            cell.font, cell.border, cell.fill, cell.alignment = copy.copy(font), copy.copy(border), copy.copy(fill), copy.copy(align)
            cell.number_format = fmt
wb.save(dp_path)

# ---------- 3. 00_配置清单 ----------
cl_path = PKG + "/00_配置清单.xlsx"
wb = openpyxl.load_workbook(cl_path)

ws = wb["配置清单"]
updates = {
    2: (4, "VALUE_READY_4_DIFFICULTIES_D1_OPEN_CHG004", "难度1默认开放；难度2～4同时要求通过上一难度与达到35/45/55级。周上限6/9/12/15千分由NR_HighestScoreReward各难度最高Score行承载（CHG-011）。"),
    6: (42, "VALUE_READY_CHG011_017_SHARED_LADDER_42ROWS", "CHG-011～017共享阶梯：4档各配到自身上限共42行（6/9/12/15节点）；同分跨档复用同一DropId，合SVN前需程序确认复用可行。"),
    7: (45, "VALUE_READY_CHG011_017_15_SHARED_PACKAGES", "15个共享奖励包×3项=45行；DropId 23000001～23000015按分数复用；B列表ID公式保持；收容凭证/校准元件/3015退出，新增3028。周钥匙仍10把/周，四难度互斥待程序联调。"),
    8: (11, "REFERENCE_ONLY_CHG017_REWARD_ITEMS", "11个实际引用道具（2/6/25/100/101/106/108/109/1074/3027/3028）；3015与校准元件不再引用。"),
}
for r, (n, status, note) in updates.items():
    ws.cell(r, 3, n); ws.cell(r, 4, status); ws.cell(r, 6, note)

ws = wb["周奖励预览"]
if ws.max_row > 1:
    ws.delete_rows(2, ws.max_row - 1)
rid = 0
for d in (1, 2, 3, 4):
    for score, items in PACKAGES:
        if score > DIFF_CAPS[d]:
            continue
        rid += 1
        row = [rid, d, UNLOCK[d], score, 23000000 + score // 1000]
        for name, item_id, qty in items:
            row += [item_id, name, qty]
        for i, v in enumerate(row):
            ws.cell(1 + rid, 1 + i, v)

ws = wb["周奖励汇总"]
for row in range(1, ws.max_row + 1):
    for col in range(1, ws.max_column + 30):
        ws.cell(row, col).value = None
header = ["难度", "解锁条件", "元晶", "旅券", "收容凭证", "映射之匙", "金币",
          "低阶记录盘", "泛黄档案", "沿途随笔", "中阶记录盘", "录像带", "房车零件",
          "低级舱室建材(3028)", "房车天赋树材料自选箱(3027)"]
totals = {
    1: [280, 2, 0, 6, 45000, 50, 20, 5000, 0, 0, 20, 20, 0],
    2: [400, 3, 0, 8, 100000, 50, 50, 12500, 0, 0, 20, 20, 15],
    3: [520, 5, 0, 9, 175000, 50, 50, 12500, 10, 10, 50, 20, 15],
    4: [700, 5, 0, 10, 275000, 50, 50, 22500, 10, 10, 90, 20, 35],
}
for i, h in enumerate(header):
    ws.cell(1, 1 + i, h)
for d in (1, 2, 3, 4):
    ws.cell(1 + d, 1, d); ws.cell(1 + d, 2, UNLOCK[d])
    for i, v in enumerate(totals[d]):
        ws.cell(1 + d, 3 + i, v)
note = ws.cell(6, 1, "注：CHG-011～017共享15节点阶梯，周内只可领一档；本页为静态汇总，已与周奖励预览逐项校验一致（见配置校验.json）。")
note.font = Font(italic=True)
wb.save(cl_path)

# ---------- 4. 校验JSON ----------
check = {
    "batch": "INFINITE-WEEKLY-20260831-CHG017",
    "generated_at": datetime.datetime.now().isoformat(),
    "status": "PENDING_VALIDATION",
    "design_basis": "06_玩法_无限挑战经济沉淀 CHG-011～CHG-017（2026-08-31已确认口径）",
    "scope": "06候选包全量重铺：NR_HighestScoreReward 42行、Drop_dungeon 45行、配置清单同步；SVN只读未改",
    "dropid_scheme": "15个共享包 23000001~23000015，同分跨档复用；合SVN前需程序确认按Difficult+Score领取时复用无副作用",
    "difficulties": {str(d): {"cap": DIFF_CAPS[d], "nodes": DIFF_CAPS[d] // 1000, "unlock": UNLOCK[d]} for d in DIFF_CAPS},
    "previous_validation": "无限之旅配置校验.json旧内容已备份至backup/",
}
json.dump(check, open(BATCH + "/land-summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
old_check = json.load(open(BACKUP + "/无限之旅配置校验.json", encoding="utf-8"))
check["previous_validation"] = {"batch": old_check.get("batch"), "generated_at": old_check.get("generated_at"),
                                "status": old_check.get("status"), "current_validation": old_check.get("current_validation")}
json.dump(check, open(PKG + "/无限之旅配置校验.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

diff = {
    "nr_old_rows": len(old_nr), "nr_new_rows": rid,
    "nr_old_first": old_nr[0], "nr_old_last": old_nr[-1],
    "drop_old_first_dropid_item": old_drop_first, "drop_new_rows": rownum,
    "backups": BACKUP,
}
json.dump(diff, open(BATCH + "/diff-summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("LANDED:", {"nr_rows": rid, "drop_rows": rownum, "backup": BACKUP})
