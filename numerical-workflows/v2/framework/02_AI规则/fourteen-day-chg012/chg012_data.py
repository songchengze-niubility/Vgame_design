# -*- coding: utf-8 -*-
"""CHG-012 任务数据：第 8~14 天 70 条任务、活跃里程碑与奖励明细。

target: (描述, TargetType, ParamList, Hint可选)
reward: 玩法奖励 (item_id, num, 中文名)；每条另含挑战积分(32)×10。
"""

# 每天任务列表：day -> [(task_id, target tuple, reward tuple)]
DAYS = {
    8: {
        "tasks": 5801,
        "drop": 91000102,
        "rows": [
(5801, ("累计消耗1800点储能", "Target_TTT_Item_Consume", "3,1800"), (102, 5, "高阶记录盘")),
(5802, ("映射装备副本最高通过第11层", "Target_TTT_WeaponLevel_PassMax", "0,11"), (25, 1, "映射之匙")),
(5803, ("爬塔最高通过第25层", "Target_TTT_Tower_MaxPassLayer", "0,25"), (1074, 150, "房车零件")),
(5804, ("通关高难2-5", "Target_TTT_pass_Level", "110205,1"), (3011, 1, "2级宝石掉落箱")),
(5805, ("邮票副本最高通过第2层", "Target_TTT_StrategyCardLevel_PassMax", "0,2"), (6, 10000, "沿途随笔")),
(5806, ("行商等级达到6级", "Target_TTT_Trade_Level", "0,6"), (301, 10000, "商品筹码")),
        ],
    },
    9: {
        "tasks": 5901,
        "drop": 91000108,
        "rows": [
(5901, ("累计消耗2100点储能", "Target_TTT_Item_Consume", "3,2100"), (102, 10, "高阶记录盘")),
(5902, ("映射装备副本最高通过第12层", "Target_TTT_WeaponLevel_PassMax", "0,12"), (25, 1, "映射之匙")),
(5903, ("爬塔最高通过第28层", "Target_TTT_Tower_MaxPassLayer", "0,28"), (1074, 50, "房车零件")),
(5904, ("通关高难3-1", "Target_TTT_pass_Level", "110301,1"), (3011, 2, "2级宝石掉落箱")),
(5905, ("玩家等级达到39级", "Target_TTT_PlayerLevel", "0,39"), (3015, 10, "普通能效自选箱")),
(5906, ("邮票副本最高通过第3层", "Target_TTT_StrategyCardLevel_PassMax", "0,3"), (6, 10000, "沿途随笔")),
        ],
    },
    10: {
        "tasks": 6101,
        "drop": 91000114,
        "rows": [
(6101, ("累计消耗2450点储能", "Target_TTT_Item_Consume", "3,2450"), (3010, 2, "1级宝石掉落箱")),
(6102, ("映射装备副本最高通过第13层", "Target_TTT_WeaponLevel_PassMax", "0,13"), (25, 1, "映射之匙")),
(6103, ("爬塔最高通过第31层", "Target_TTT_Tower_MaxPassLayer", "0,31"), (1074, 50, "房车零件")),
(6104, ("通关高难3-2", "Target_TTT_pass_Level", "110302,1"), (3011, 2, "2级宝石掉落箱")),
(6105, ("任意Boss挑战通关难度3", "Target_TTT_BossChallenge_AnyBossDifficulty", "0,3"), (106, 1, "旅券")),
(6106, ("行商等级达到7级", "Target_TTT_Trade_Level", "0,7"), (3027, 10, "指南材料自选箱")),
        ],
    },
    11: {
        "tasks": 6201,
        "drop": 91000120,
        "rows": [
(6201, ("累计消耗2750点储能", "Target_TTT_Item_Consume", "3,2750"), (3010, 3, "1级宝石掉落箱")),
(6202, ("映射装备副本最高通过第14层", "Target_TTT_WeaponLevel_PassMax", "0,14"), (25, 1, "映射之匙")),
(6203, ("爬塔最高通过第34层", "Target_TTT_Tower_MaxPassLayer", "0,34"), (1074, 50, "房车零件")),
(6204, ("通关高难3-3", "Target_TTT_pass_Level", "110303,1"), (3011, 2, "2级宝石掉落箱")),
(6205, ("历史最高通关肉鸽难度2", "Target_TTT_Roguelike_MaxPassLevel", "0,2"), (107, 3, "收容凭证")),
(6206, ("玩家等级达到40级", "Target_TTT_PlayerLevel", "0,40"), (3027, 10, "指南材料自选箱")),
        ],
    },
    12: {
        "tasks": 6301,
        "drop": 91000126,
        "rows": [
(6301, ("累计消耗3050点储能", "Target_TTT_Item_Consume", "3,3050"), (3011, 2, "2级宝石掉落箱")),
(6302, ("映射装备副本最高通过第15层", "Target_TTT_WeaponLevel_PassMax", "0,15"), (25, 1, "映射之匙")),
(6303, ("爬塔最高通过第37层", "Target_TTT_Tower_MaxPassLayer", "0,37"), (1074, 50, "房车零件")),
(6304, ("通关高难3-4", "Target_TTT_pass_Level", "110304,1"), (3011, 2, "2级宝石掉落箱")),
(6305, ("邮票副本最高通过第4层", "Target_TTT_StrategyCardLevel_PassMax", "0,4"), (6, 10000, "沿途随笔")),
(6306, ("任意Boss挑战通关难度4", "Target_TTT_BossChallenge_AnyBossDifficulty", "0,4"), (106, 1, "旅券")),
        ],
    },
    13: {
        "tasks": 6401,
        "drop": 91000132,
        "rows": [
(6401, ("累计消耗3350点储能", "Target_TTT_Item_Consume", "3,3350"), (3010, 6, "1级宝石掉落箱")),
(6402, ("映射装备副本最高通过第16层", "Target_TTT_WeaponLevel_PassMax", "0,16"), (25, 1, "映射之匙")),
(6403, ("爬塔最高通过第40层", "Target_TTT_Tower_MaxPassLayer", "0,40"), (1074, 50, "房车零件")),
(6404, ("通关高难3-5", "Target_TTT_pass_Level", "110305,1"), (3011, 2, "2级宝石掉落箱")),
(6405, ("玩家等级达到41级", "Target_TTT_PlayerLevel", "0,41"), (1, 50000, "猎鹰金币")),
(6406, ("邮票副本最高通过第5层", "Target_TTT_StrategyCardLevel_PassMax", "0,5"), (6, 10000, "沿途随笔")),
        ],
    },
    14: {
        "tasks": 6501,
        "drop": 91000138,
        "rows": [
(6501, ("累计消耗3650点储能", "Target_TTT_Item_Consume", "3,3650"), (33, 10, "漫游邮戳")),
(6502, ("映射装备副本最高通过第17层", "Target_TTT_WeaponLevel_PassMax", "0,17"), (25, 2, "映射之匙")),
(6503, ("爬塔最高通过第43层", "Target_TTT_Tower_MaxPassLayer", "0,43"), (3027, 10, "指南材料自选箱")),
(6504, ("通关高难4-1", "Target_TTT_pass_Level", "110401,1"), (3011, 2, "2级宝石掉落箱")),
(6505, ("行商等级达到8级", "Target_TTT_Trade_Level", "0,8"), (1156, 1, "高级指南材料")),
(6506, ("历史最高通关肉鸽难度3", "Target_TTT_Roguelike_MaxPassLevel", "0,3"), (107, 3, "收容凭证")),
        ],
    },
}

# 活跃里程碑：ActivePoint -> (RewardId, 额外奖励 (item_id, num, 名称))
MILESTONES = [
    (800, 91001008, (106, 5, "旅券")),
    (900, 91001009, (111, 5, "限时旅券")),
    (1000, 91001010, (107, 20, "收容凭证")),
    (1100, 91001011, (51001, 1, "虚妄之镜")),
]

SCORE_ITEM = 32       # 挑战积分
SCORE_NUM = 10        # 每条任务固定 ×10
DROP_ROW_ID_START = 400369  # 修订后任务Drop仅84行(400369~400452)

ITEM_NAMES = {
    1: "猎鹰金币", 2: "元晶", 6: "沿途随笔", 19: "勇士勋章", 25: "映射之匙",
    28: "校准元件", 32: "挑战积分", 33: "漫游邮戳", 100: "低阶记录盘",
    102: "高阶记录盘", 106: "旅券", 107: "收容凭证", 108: "泛黄档案",
    109: "录像带", 111: "限时旅券", 301: "商品筹码", 1074: "房车零件",
    1156: "高级指南材料", 3010: "1级宝石掉落箱", 3011: "2级宝石掉落箱",
    3015: "普通能效自选箱", 3027: "指南材料自选箱", 51001: "虚妄之镜",
    311003: "塔拉夏", 311029: "凯兰",
}


def iter_tasks():
    for day in sorted(DAYS):
        spec = DAYS[day]
        for i, (tid, target, reward) in enumerate(spec["rows"]):
            yield day, spec["tasks"] + i, spec["drop"] + i, tid, target, reward


def totals():
    """70条任务+里程碑的总投放（不含挑战积分以外的重复计算）。"""
    from collections import Counter
    c = Counter()
    for _, _, _, _, _, (iid, num, _) in iter_tasks():
        c[iid] += num
    c[SCORE_ITEM] += 70 * SCORE_NUM
    for _, _, (iid, num, _) in MILESTONES:
        c[iid] += num
    c[2] += 1000 + 500 * 8 + 500
    return c
