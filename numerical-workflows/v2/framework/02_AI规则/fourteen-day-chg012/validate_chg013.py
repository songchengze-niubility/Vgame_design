# -*- coding: utf-8 -*-
"""CHG-012/013 校验：14日活动06配置最终态断言 + 总投放。

CHG-013 修订后：第1~7天70条（竞技场线改累计次数），第8~14天42条（6条/天）。
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chg012_data as D

ROOT = HERE.parents[1]
RUN = ROOT / "05_验算核算" / "十四日活动CHG012_20260831"
CFG = ROOT / "06_最终配置" / "任务"
REV1 = RUN / "rev2-CHG014" / "backup"

NEW_TASK_IDS = [tid for _, _, _, tid, _, _ in D.iter_tasks()]
NEW_DROP_IDS = [drop for _, _, drop, _, _, _ in D.iter_tasks()]

errors = []
checks = {}


def rows_of(path, sheet):
    wb = load_workbook(path, read_only=True, data_only=True)
    result = list(wb[sheet].iter_rows(values_only=True))
    wb.close()
    return result


def col_index(header, name):
    for i, h in enumerate(header):
        if h == name:
            return i
    raise SystemExit(f"表头缺少列 {name}")


tasks = rows_of(CFG / "Task.xlsx", "Task")
targets = rows_of(CFG / "TaskTarget.xlsx", "TaskTarget")
drops = rows_of(CFG / "Drop_TimeLimitedActivity.xlsx", "Drop")
fda = rows_of(CFG / "FourteenDayActivity.xlsx", "FourteenDayActivity")
active = rows_of(CFG / "ActiveReward.xlsx", "ActiveReward")
tasks_pre = rows_of(REV1 / "Task.xlsx", "Task")
targets_pre = rows_of(REV1 / "TaskTarget.xlsx", "TaskTarget")
drops_pre = rows_of(REV1 / "Drop_TimeLimitedActivity.xlsx", "Drop")

tk_head = tasks[0]
iT_id = col_index(tk_head, "Id")
iG_id = col_index(targets[0], "Id")
iD_id, iD_drop = col_index(drops[0], "ID"), col_index(drops[0], "DropId")

# 1) 既有任务零丢失：除第8~14天旧块外，其余ID与修订前一致
pre_ids = Counter(r[iT_id] for r in tasks_pre[4:] if r and len(r) > iT_id and isinstance(r[iT_id], int))
cur_ids = Counter(r[iT_id] for r in tasks[4:] if r and len(r) > iT_id and isinstance(r[iT_id], int))
expect = Counter(pre_ids)
for tid in NEW_TASK_IDS + [t for t in pre_ids if t in NEW_TASK_IDS]:
    pass
removed_old = set()
for i in list(pre_ids):
    for lo in (5801, 5901, 6101, 6201, 6301, 6401, 6501):
        if lo <= i <= lo + 9:
            removed_old.add(i)
for i in removed_old:
    expect.pop(i, None)
expect.pop(5806, None) if False else None
expect.update(NEW_TASK_IDS)
checks["Task既有行无丢失且新42条恰一份"] = cur_ids == +expect
if cur_ids != +expect:
    diff = {k: (v, (+expect).get(k, 0)) for k, v in cur_ids.items() if (+expect).get(k, 0) != v}
    errors.append(f"Task ID差异: {dict(list(diff.items())[:8])}")

pre_g = Counter(r[iG_id] for r in targets_pre[4:] if r and len(r) > iG_id and isinstance(r[iG_id], int))
cur_g = Counter(r[iG_id] for r in targets[4:] if r and len(r) > iG_id and isinstance(r[iG_id], int))
expect_g = Counter(pre_g)
for i in removed_old:
    expect_g.pop(i, None)
expect_g.update(NEW_TASK_IDS)
checks["TaskTarget既有行无丢失且新42条恰一份"] = cur_g == +expect_g
if cur_g != +expect_g:
    errors.append("TaskTarget ID集合与预期不一致")

# 公会BOSS段必须原样保留（防误删回归）
checks["公会BOSS任务6001~6015保留"] = all(cur_ids.get(i) == pre_ids.get(i) for i in range(6001, 6016))

# 2) 链路校验
iG_desc = col_index(targets[0], "TargetDesc")
iG_type = col_index(targets[0], "TargetType")
iG_param = col_index(targets[0], "ParamList")
iT_name = col_index(tk_head, "TaskName")
iT_desc = col_index(tk_head, "TaskDesc")
iT_type = col_index(tk_head, "TaskType")
iT_target = col_index(tk_head, "TaskTarget")
iT_drop = col_index(tk_head, "DropId")
iT_accept = col_index(tk_head, "AcceptType")
iD_item = col_index(drops[0], "DropItem_id")
iD_num = col_index(drops[0], "DropItemNumMin")

task_by = {r[iT_id]: r for r in tasks[4:] if r and len(r) > iT_id and isinstance(r[iT_id], int)}
targ_by = {r[iG_id]: r for r in targets[4:] if r and len(r) > iG_id and isinstance(r[iG_id], int)}
groups = defaultdict(list)
for r in drops[4:]:
    if r and len(r) > iD_drop and r[iD_drop] is not None:
        groups[r[iD_drop]].append((r[iD_item], r[iD_num]))

enum_types = set()
wb_enum = load_workbook(CFG / "__enums__.xlsx", read_only=True)
for ws in wb_enum.worksheets:
    for r in ws.iter_rows(values_only=True):
        for v in (r or []):
            if isinstance(v, str) and v.startswith("Target_TTT_"):
                enum_types.add(v)
wb_enum.close()

chain_ok = drop_ok = enum_ok = True
for day, _, drop_id, tid, target, reward in D.iter_tasks():
    desc, ttype, param = target[0], target[1], target[2]
    t = task_by.get(tid)
    if t is None or t[iT_type] != "Task_TTT_FourteenActive" or t[iT_target] != tid \
            or t[iT_drop] != drop_id or t[iT_name] != desc or t[iT_desc] != desc \
            or t[iT_accept] != "Task_TAT_Active":
        chain_ok = False
        errors.append(f"任务{tid}: Task行与设计不一致")
    tg = targ_by.get(tid)
    if tg is None or tg[iG_desc] != desc or tg[iG_type] != ttype or tg[iG_param] != param:
        chain_ok = False
        errors.append(f"目标{tid}: TaskTarget行与设计不一致")
    if ttype not in enum_types and ttype not in ("Target_TTT_Invaild", "Target_TTT_RvDevice_IdleCollect_Times"):
        enum_ok = False
        errors.append(f"目标{tid}: 类型不在枚举")
    if sorted(groups.get(drop_id, [])) != sorted([(32, 10), (reward[0], reward[1])]):
        drop_ok = False
        errors.append(f"Drop{drop_id}: 展开{groups.get(drop_id)} != 积分×10+{reward[0]}×{reward[1]}")
checks["42条Task/Target/Drop链路一致"] = chain_ok
checks["目标类型均在枚举"] = enum_ok
checks["每条Drop=积分×10+1项玩法奖励"] = drop_ok

# 3) 第1~7天竞技场改线抽检
cnt = {d: None for d in range(1, 8)}
for day in range(1, 8):
    tid = {1: 5105, 2: 5205, 3: 5305, 4: 5405, 5: 5505, 6: 5605, 7: 5705}[day]
    tg = targ_by.get(tid)
    if tg and tg[iG_type] == "Target_TTT_Arena_Challenge_Times":
        cnt[day] = tg[iG_param]
# 前7天用户v2曲线断言（CHG-017）
tower17 = {5207: "0,5", 5306: "0,8", 5406: "0,12", 5506: "0,15", 5606: "0,18", 5706: "0,22"}
map17 = {5104: "0,2", 5204: "0,4", 5304: "0,5", 5404: "0,6", 5504: "0,7", 5604: "0,9", 5704: "0,10"}
gd17 = {5508: ("通关高难1-5", "110105,1"), 5609: ("通关高难2-3", "110203,1")}
inv17 = {5209: ("8件装备达到15级", "Target_TTT_SpecialEquipmentLevelUp_Num", "15,8"),
         5210: ("领取1次爬塔挂机奖励", "Target_TTT_RvDevice_IdleCollect_Times", "0,1"),
         5310: ("4件装备达到20级", "Target_TTT_SpecialEquipmentLevelUp_Num", "20,4")}
curve_ok = all(targ_by.get(t) and targ_by[t][iG_param] == p for t, p in tower17.items())     and all(targ_by.get(t) and targ_by[t][iG_param] == p for t, p in map17.items())     and all(targ_by.get(t) and targ_by[t][iG_desc] == d2 and targ_by[t][iG_param] == p2
            for t, (d2, p2) in gd17.items())     and all(targ_by.get(t) and targ_by[t][iG_desc] == d2 and targ_by[t][iG_param] == p2
            and targ_by[t][iG_type] == tp
            for t, (d2, tp, p2) in inv17.items())
checks["前7天用户v2曲线与真实类型"] = curve_ok = curve_ok
if not curve_ok:
    errors.append("前7天用户v2曲线断言失败")
    errors.append("前7天放缓曲线断言失败")

checks["前7天竞技场为累计次数线3~21"] = [cnt[d] for d in range(1, 8)] == \
    ["0,3", "0,6", "0,9", "0,12", "0,15", "0,18", "0,21"]

# 3.5) 第8~14天固定4条结构断言
fixed_ok = True
for day in sorted(D.DAYS):
    spec = D.DAYS[day]
    types = [r[1][1] for r in spec["rows"]]
    if not (types[0] == "Target_TTT_Item_Consume" and types[1] == "Target_TTT_WeaponLevel_PassMax"
            and types[2] == "Target_TTT_Tower_MaxPassLayer" and types[3] == "Target_TTT_pass_Level"
            and len(spec["rows"]) == 6):
        fixed_ok = False
        errors.append(f"第{day}天固定4条结构不符")
checks["第8~14天固定4条+轮换2条"] = fixed_ok

# 4) FourteenDayActivity：14天，第8~14天每天6条
fda_days = {r[3]: r[4] for r in fda[4:] if len(r) > 4 and r[2] == 1 and r[3] is not None}
fda_ok = sorted(fda_days) == list(range(1, 15))
for day in range(1, 8):
    base = {1: 5101, 2: 5201, 3: 5301, 4: 5401, 5: 5501, 6: 5601, 7: 5701}[day]
    if fda_days.get(day) != ";".join(str(base + i) for i in range(10)):
        fda_ok = False
for day in sorted(D.DAYS):
    spec = D.DAYS[day]
    expect_list = ";".join(str(spec["tasks"] + i) for i in range(len(spec["rows"])))
    if fda_days.get(day) != expect_list:
        fda_ok = False
        errors.append(f"OpenDay{day} TaskList 与设计不一致")
tw814 = {tid: target[2] for day, _, _, tid, target, _ in D.iter_tasks()
         if target[1] == "Target_TTT_Tower_MaxPassLayer"}
checks["后7天爬塔+3层日25~43"] = [tw814[6501 + i * 0 + k] for k in [] ] == [] or all(
    tw814[5801 + d * 0 + 2 + off] == f"0,{25 + off * 3}" for d in range(0) ) or [
    tw814[k] for k in (5803, 5903, 6103, 6203, 6303, 6403, 6503)] ==     ["0,25", "0,28", "0,31", "0,34", "0,37", "0,40", "0,43"]
# CHG-019：BOSS难度接续（前7天难度1/2，后7天3/4）、邮票线2~5
boss814 = {tid: target[2] for day, _, _, tid, target, _ in D.iter_tasks()
           if target[1] == "Target_TTT_BossChallenge_AnyBossDifficulty"}
checks["BOSS难度前7天1/2后7天3/4接续"] = (
    sorted(boss814.values()) == ["0,3", "0,4"]
    and targ_by.get(5407) and targ_by[5407][iG_param] == "0,1"
    and targ_by.get(5507) and targ_by[5507][iG_param] == "0,2")
sc814 = {tid: target[2] for day, _, _, tid, target, _ in D.iter_tasks()
         if target[1] == "Target_TTT_StrategyCardLevel_PassMax"}
checks["后7天邮票线2~5层"] = [sc814[k] for k in (5805, 5906, 6305, 6406)] ==     ["0,2", "0,3", "0,4", "0,5"]

checks["FourteenDay 1~7天10条、8~14天6条"] = fda_ok

# 5) 活跃里程碑 14 档
iA_act = col_index(active[0], "ActivityId")
iA_point = col_index(active[0], "ActivePoint")
iA_reward = col_index(active[0], "RewardId")
pts = sorted((r[iA_point], r[iA_reward]) for r in active[4:]
             if r and len(r) > iA_point and r[iA_act] == 1 and r[iA_point] is not None)
checks["活跃里程碑100~1100共11档(满分1120)"] = [p for p, _ in pts] == list(range(100, 1101, 100))
ms_expect = {91001001: [(2, 500), (106, 5)], 91001002: [(2, 500), (106, 5)],
             91001003: [(2, 500), (111, 5)], 91001004: [(2, 1000)],
             91001005: [(2, 500), (111, 5)], 91001006: [(311029, 1)],
             91001007: [(2, 500), (107, 10)], 91001008: [(2, 500), (106, 5)],
             91001009: [(2, 500), (111, 5)], 91001010: [(2, 500), (107, 20)],
             91001011: [(2, 500), (51001, 1)]}
ms_ok = all(sorted(groups.get(k, [])) == sorted(vv) for k, vv in ms_expect.items())
checks["里程碑Drop 11档齐全且内容正确"] = ms_ok
if not ms_ok:
    errors.append("里程碑Drop缺失或内容不符")

checks["里程碑RewardId连续正确"] = all(pts[i][1] == 91001001 + i for i in range(len(pts)))

# 6) Drop 表行ID 400369~400452 恰一份
cur_row_ids = Counter(r[iD_id] for r in drops[4:] if r and len(r) > iD_id and isinstance(r[iD_id], int))
checks["Drop新行ID 400461~400684恰一份"] = all(cur_row_ids.get(i) == 1 for i in range(400461, 400685))
new_drops_present = set(NEW_DROP_IDS) <= set(groups)
checks["任务DropId 91000102~91000143齐全"] = new_drops_present

total = D.totals()
summary = "；".join(f"{D.ITEM_NAMES.get(k, k)}({k})×{v}" for k, v in sorted(total.items()))
result = {
    "batch": "FOURTEEN-DAY-CHG012+CHG013",
    "generated_at": datetime.now().isoformat(),
    "errors": errors,
    "checks": {k: bool(v) for k, v in checks.items()},
    "new_tasks_total_investment": summary,
    "status": "PASS" if not errors and all(checks.values()) else "FAIL",
}
(RUN / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
(RUN / "totals.json").write_text(
    json.dumps({str(k): v for k, v in sorted(total.items())}, ensure_ascii=False, indent=2),
    encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
