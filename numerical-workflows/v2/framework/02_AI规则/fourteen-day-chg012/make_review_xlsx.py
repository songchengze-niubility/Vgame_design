# -*- coding: utf-8 -*-
"""生成 14 日活动任务评审总表（可编辑）到 output/。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chg012_data as D

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

D17 = {
1: [("累计登录1天","Target_TTT_Login_Total","0,1",(102,3)),("累计消耗200点储能","Target_TTT_Item_Consume","3,200",(102,3)),("玩家等级达到22级","Target_TTT_PlayerLevel","0,22",(3015,5)),("映射装备副本最高通过第2层","Target_TTT_WeaponLevel_PassMax","0,2",(25,1)),("累计挑战竞技场3次","Target_TTT_Arena_Challenge_Times","0,3",(19,10)),("累计挑战资源副本3次","Target_TTT_Type_LevelClearNum","0,3",(102,3)),("任意卡池累计抽卡10次","Target_TTT_DrawCard_AnyGachaTimes","0,10",(1,50000)),("分解1次装备","Target_TTT_BreakdowntSpecialEquipment_Num","0,1",(1,50000)),("累计完成扫荡3次","Target_TTT_Sweep_Times","0,3",(1,50000)),("累计击败BOSS敌人3个","Target_TTT_BossMonster_Kill_Times","0,3",(102,3))],
2: [("累计登录2天","Target_TTT_Login_Total","0,2",(102,3)),("累计消耗400点储能","Target_TTT_Item_Consume","3,400",(102,3)),("玩家等级达到26级","Target_TTT_PlayerLevel","0,26",(1074,20)),("映射装备副本最高通过第4层","Target_TTT_WeaponLevel_PassMax","0,4",(25,1)),("累计挑战竞技场6次","Target_TTT_Arena_Challenge_Times","0,6",(19,10)),("累计挑战资源副本9次","Target_TTT_Type_LevelClearNum","0,9",(102,3)),("爬塔最高通过第5层","Target_TTT_Tower_MaxPassLayer","0,5",(1074,20)),("累计挑战无限之旅1次","Target_TTT_InfiniteChallenge_Times","0,1",(1,50000)),("8件装备达到15级","Target_TTT_SpecialEquipmentLevelUp_Num","15,8",(100,30)),("领取1次爬塔挂机奖励","Target_TTT_RvDevice_IdleCollect_Times","0,1",(102,5))],
3: [("累计登录3天","Target_TTT_Login_Total","0,3",(102,3)),("累计消耗600点储能","Target_TTT_Item_Consume","3,600",(102,3)),("玩家等级达到30级","Target_TTT_PlayerLevel","0,30",(3027,5)),("映射装备副本最高通过第5层","Target_TTT_WeaponLevel_PassMax","0,5",(25,1)),("累计挑战竞技场9次","Target_TTT_Arena_Challenge_Times","0,9",(19,10)),("爬塔最高通过第8层","Target_TTT_Tower_MaxPassLayer","0,8",(1074,20)),("累计挑战资源副本15次","Target_TTT_Type_LevelClearNum","0,15",(102,10)),("无限之旅本周最高分达到2000分","Target_TTT_InfiniteChallenge_Score","0,2000",(108,30)),("累计完成跑商1次","Target_TTT_Trade_CompleteTimes","0,1",(301,3000)),("4件装备达到20级","Target_TTT_SpecialEquipmentLevelUp_Num","20,4",(3027,5))],
4: [("累计登录4天","Target_TTT_Login_Total","0,4",(3010,2)),("累计消耗800点储能","Target_TTT_Item_Consume","3,800",(3010,2)),("玩家等级达到32级","Target_TTT_PlayerLevel","0,32",(3010,2)),("映射装备副本最高通过第6层","Target_TTT_WeaponLevel_PassMax","0,6",(25,1)),("累计挑战竞技场12次","Target_TTT_Arena_Challenge_Times","0,12",(19,10)),("爬塔最高通过第12层","Target_TTT_Tower_MaxPassLayer","0,12",(1074,30)),("通关BOSS最高通过难度1","Target_TTT_BossChallenge_AnyBossDifficulty","0,1",(106,1)),("累计通关高难主线1次","Target_TTT_Type_LevelClearNum","37,1",(3010,2)),("无限之旅本周最高分达到3000分","Target_TTT_InfiniteChallenge_Score","0,3000",(1,50000)),("行商等级达到2级","Target_TTT_Trade_Level","0,2",(301,5000))],
5: [("累计登录5天","Target_TTT_Login_Total","0,5",(3010,2)),("累计消耗1000点储能","Target_TTT_Item_Consume","3,1000",(3010,2)),("玩家等级达到34级","Target_TTT_PlayerLevel","0,34",(107,1)),("映射装备副本最高通过第7层","Target_TTT_WeaponLevel_PassMax","0,7",(25,1)),("累计挑战竞技场15次","Target_TTT_Arena_Challenge_Times","0,15",(19,10)),("爬塔最高通过第15层","Target_TTT_Tower_MaxPassLayer","0,15",(1074,30)),("通关BOSS最高通过难度2","Target_TTT_BossChallenge_AnyBossDifficulty","0,2",(3010,2)),("通关高难1-5","Target_TTT_pass_Level","110105,1",(3011,1)),("无限之旅本周最高分达到4000分","Target_TTT_InfiniteChallenge_Score","0,4000",(1,50000)),("行商等级达到3级","Target_TTT_Trade_Level","0,3",(3027,3))],
6: [("累计登录6天","Target_TTT_Login_Total","0,6",(107,2)),("累计消耗1200点储能","Target_TTT_Item_Consume","3,1200",(3010,2)),("玩家等级达到36级","Target_TTT_PlayerLevel","0,36",(109,5)),("映射装备副本最高通过第9层","Target_TTT_WeaponLevel_PassMax","0,9",(25,1)),("累计挑战竞技场18次","Target_TTT_Arena_Challenge_Times","0,18",(19,10)),("爬塔最高通过第18层","Target_TTT_Tower_MaxPassLayer","0,18",(3027,5)),("无限之旅本周最高分达到5000分","Target_TTT_InfiniteChallenge_Score","0,5000",(1074,40)),("行商等级达到4级","Target_TTT_Trade_Level","0,4",(1156,1)),("通关高难2-3","Target_TTT_pass_Level","110203,1",(3011,1)),("累计获得肉鸽积分2000分","Target_TTT_Roguelike_AccumulateScore","0,2000",(107,2))],
7: [("累计登录7天","Target_TTT_Login_Total","0,7",(107,2)),("累计消耗1500点储能","Target_TTT_Item_Consume","3,1500",(33,10)),("玩家等级达到38级","Target_TTT_PlayerLevel","0,38",(6,10000)),("映射装备副本最高通过第10层","Target_TTT_WeaponLevel_PassMax","0,10",(25,1)),("累计挑战竞技场21次","Target_TTT_Arena_Challenge_Times","0,21",(19,20)),("爬塔最高通过第22层","Target_TTT_Tower_MaxPassLayer","0,22",(3027,5)),("无限之旅本周最高分达到6000分","Target_TTT_InfiniteChallenge_Score","0,6000",(100,40)),("行商等级达到5级","Target_TTT_Trade_Level","0,5",(3027,5)),("累计获得肉鸽积分5000分","Target_TTT_Roguelike_AccumulateScore","0,5000",(107,2)),("邮票副本最高通过第1层","Target_TTT_StrategyCardLevel_PassMax","0,1",(6,10000))],
}
TID17 = {1: 5101, 2: 5201, 3: 5301, 4: 5401, 5: 5501, 6: 5601, 7: 5701}
DROP17 = {1: 91000001, 2: 91000011, 3: 91000021, 4: 91000031, 5: 91000041, 6: 91000051, 7: 91000061}
UNLOCK = {"Target_TTT_Arena_RankScore": 4112, "Target_TTT_Arena_Challenge_Times": 4112,
          "Target_TTT_InfiniteChallenge_Score": 4111, "Target_TTT_InfiniteChallenge_Times": 4111,
          "Target_TTT_WeaponLevel_PassMax": 4314, "Target_TTT_Tower_MaxPassLayer": 4101,
          "Target_TTT_pass_Level": 4041, "Target_TTT_Trade_Level": 4039,
          "Target_TTT_Trade_CompleteTimes": 4039, "Target_TTT_StrategyCardLevel_PassMax": 4106,
          "Target_TTT_Roguelike_AccumulateScore": 4103, "Target_TTT_Roguelike_ChallengeTimes": 4103,
          "Target_TTT_Roguelike_MaxPassLevel": 4103, "Target_TTT_Type_LevelClearNum": 4105,
          "Target_TTT_SpecialEquipDungeon_Challenge_Times": 4314}

wb = Workbook()
ws = wb.active
ws.title = "14日任务总表"
ws.append(["天", "序", "TaskId", "任务目标(描述)", "目标类型", "判分参数",
           "奖励1:固定", "奖励1道具ID", "奖励1数量",
           "奖励2:玩法", "奖励2道具ID", "奖励2数量", "UnlockId", "DropId", "备注/联调"])
hf = Font(bold=True, name="Arial", color="FFFFFF")
hfill = PatternFill("solid", start_color="2F5496")
thin = Border(*[Side(style="thin", color="B0B0B0")] * 4)
for c in ws[1]:
    c.font = hf; c.fill = hfill; c.alignment = Alignment(horizontal="center"); c.border = thin
blue = Font(name="Arial", color="0000FF")
dayfill = PatternFill("solid", start_color="DDEBF7")

rows = []
for day in range(1, 8):
    base, dbase = TID17[day], DROP17[day]
    for i, (desc, ttype, param, (item, num)) in enumerate(D17[day]):
        rows.append([day, i + 1, base + i, desc, ttype, param, D.ITEM_NAMES.get(item, ""),
                     item, num, UNLOCK.get(ttype, ""), dbase + i, "挑战积分(32)×10", ""])
for day in sorted(D.DAYS):
    spec = D.DAYS[day]
    for i, (tid, target, reward) in enumerate(spec["rows"]):
        note = "复用类型，需联调本周最高分" if target[1] == "Target_TTT_InfiniteChallenge_Score" else ""
        rows.append([day, i + 1, tid, target[0], target[1], target[2], D.ITEM_NAMES.get(reward[0], ""),
                     reward[0], reward[1], UNLOCK.get(target[1], ""), spec["drop"] + i,
                     "挑战积分(32)×10", note])
full = []
for day, i, tid, desc, ttype, param, rname, rid, rnum, unlock, drop, _txt, note in rows:
    full.append([day, i, tid, desc, ttype, param,
                 "挑战积分", 32, 10, rname, rid, rnum, unlock, drop, note])
for r in full:
    ws.append(r)
for ri in range(2, ws.max_row + 1):
    day = ws.cell(row=ri, column=1).value
    for ci in range(1, 16):
        c = ws.cell(row=ri, column=ci)
        c.font = Font(name="Arial")
        c.border = thin
        if day % 2 == 0:
            c.fill = dayfill
    for ci in (4, 6, 7, 8, 9, 10, 11, 12):
        ws.cell(row=ri, column=ci).font = blue
for col, w in zip("ABCDEFGHIJKLMNO", [5, 5, 8, 34, 40, 12, 12, 10, 10, 18, 10, 10, 9, 12, 26]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:O{ws.max_row}"

ms = wb.create_sheet("活跃里程碑")
ms.append(["档位", "ActivePoint", "元晶数量", "额外奖励", "额外道具ID", "额外数量", "RewardId", "备注"])
for c in ms[1]:
    c.font = hf; c.fill = hfill; c.alignment = Alignment(horizontal="center")
ms_rows = [(1, 100, "旅券", 106, 5, 91001001), (2, 200, "旅券", 106, 5, 91001002),
           (3, 300, "限时旅券", 111, 5, 91001003), (4, 400, "无", None, None, 91001004),
           (5, 500, "限时旅券", 111, 5, 91001005), (6, 600, "凯兰(角色)", 311029, 1, 91001006),
           (7, 700, "收容凭证", 107, 10, 91001007), (8, 800, "旅券", 106, 5, 91001008),
           (9, 900, "限时旅券", 111, 5, 91001009), (10, 1000, "收容凭证", 107, 20, 91001010),
           (11, 1100, "虚妄之镜", 51001, 1, 91001011)]
yj = {1: 500, 2: 500, 3: 500, 4: 1000, 5: 500, 6: 0, 7: 500, 8: 500, 9: 500, 10: 500, 11: 500}
for r in ms_rows:
    note = "角色=凯兰(311029)" if r[0] == 6 else ("仅元晶" if r[0] == 4 else "")
    ms.append([r[0], r[1], yj[r[0]], r[2], r[3], r[4], r[5], note])
for ri in range(2, ms.max_row + 1):
    for ci in range(1, 9):
        ms.cell(row=ri, column=ci).font = Font(name="Arial")
    for ci in (3, 4, 5, 6):
        ms.cell(row=ri, column=ci).font = blue
for col, w in zip("ABCDEFGH", [6, 12, 10, 14, 10, 8, 12, 40]):
    ms.column_dimensions[col].width = w
ms.freeze_panes = "A2"

info = wb.create_sheet("填写说明")
notes = [
    "14日活动任务评审表（2026-08-31，批次CHG-012）",
    "",
    "蓝色字体 = 可直接修改的单元格：任务目标描述、判分参数、奖励1(挑战积分)/奖励2(玩法奖励)的道具ID与数量、里程碑元晶数量与额外奖励（总表与里程碑表同）。",
    "其余列（TaskId/目标类型/DropId等）为配置关联键，如需改动请改完在对话里说明，不要直接改。",
    "",
    "判分参数格式：'数值,数值'。常见：登录/等级/层数等 0,X；储能 3,X；BOSS挑战 23,X；高难主线 37,X；通关指定关卡 关卡ID,1（如高难3-1=110301,1）。",
    "",
    "【CHG-023修订】里程碑11档、元晶非每档必有（600档无、1000档×1000，总额5500）、400档仅元晶；第8~14天每天固定4条进度线（储能/映射+1层日/爬塔+4层日/高难逐关）+轮换2条（邮票层/BOSS难度/行商等级/肉鸽难度/玩家等级）。前7天竞技场为累计挑战次数线3~26次。",
    "",
    "竞技场段位分界（ArenaRank.xlsx 有效段位，第8~11天段位线用）：黄金Ⅲ1000 黄金Ⅱ1100 黄金Ⅰ1200 铂金Ⅲ1300 铂金Ⅱ1400 铂金Ⅰ1500 钻石Ⅲ1600 钻石Ⅱ1700 钻石Ⅰ1800 大师Ⅲ1900 大师Ⅱ2000 大师Ⅰ2100。",
    "",
    "改完后把文件发我或告诉我路径，我会：",
    "  1) 逐行diff你的修改 vs 当前06配置；",
    "  2) 按批次协议（备份+plan+逐格校验）同步到06_最终配置；",
    "  3) 你确认后再落SVN。",
    "",
    "常见道具ID对照：1猎鹰金币 2元晶 6沿途随笔 19勇士勋章 25映射之匙 28校准元件 32挑战积分 33漫游邮戳",
    "100低阶记录盘 102高阶记录盘 106旅券 107收容凭证 108泛黄档案 109录像带 111限时旅券",
    "301商品筹码 1074房车零件 1156高级指南材料 3010 1级宝石掉落箱 3011 2级宝石掉落箱 3015普通能效自选箱 3027指南材料自选箱 51001虚妄之镜",
]
for i, n in enumerate(notes, 1):
    info.cell(row=i, column=1, value=n).font = Font(name="Arial", bold=(i == 1), size=12 if i == 1 else 10)
info.column_dimensions["A"].width = 110

out = Path(__file__).resolve().parents[5] / "output"
out.mkdir(exist_ok=True)
path = out / "14日任务总表-评审v16-2026-08-31.xlsx"
wb.save(path)
print("saved:", path, "| task rows:", ws.max_row - 1, "| milestone rows:", ms.max_row - 1)
