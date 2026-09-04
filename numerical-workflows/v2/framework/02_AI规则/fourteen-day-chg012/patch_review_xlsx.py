# -*- coding: utf-8 -*-
"""修订 make_review_xlsx.py 的前7天数据并重新生成评审表 v2。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "make_review_xlsx.py"
t = p.read_text(encoding="utf-8")

pairs = [
    ('("竞技场历史最高达到黄金Ⅱ","Target_TTT_Arena_RankScore","0,1100",(19,10))',
     '("累计挑战竞技场3次","Target_TTT_Arena_Challenge_Times","0,3",(19,10))'),
    ('("竞技场历史最高达到黄金Ⅰ","Target_TTT_Arena_RankScore","0,1200",(19,10))',
     '("累计挑战竞技场6次","Target_TTT_Arena_Challenge_Times","0,6",(19,10))'),
    ('("竞技场历史最高达到铂金Ⅲ","Target_TTT_Arena_RankScore","0,1300",(19,10))',
     '("累计挑战竞技场10次","Target_TTT_Arena_Challenge_Times","0,10",(19,10))'),
    ('("竞技场历史最高达到铂金Ⅱ","Target_TTT_Arena_RankScore","0,1400",(19,10))',
     '("累计挑战竞技场14次","Target_TTT_Arena_Challenge_Times","0,14",(19,10))'),
    ('("竞技场历史最高达到铂金Ⅰ","Target_TTT_Arena_RankScore","0,1500",(19,10))',
     '("累计挑战竞技场18次","Target_TTT_Arena_Challenge_Times","0,18",(19,10))'),
    ('("竞技场历史最高达到钻石Ⅲ","Target_TTT_Arena_RankScore","0,1600",(19,10))',
     '("累计挑战竞技场22次","Target_TTT_Arena_Challenge_Times","0,22",(19,10))'),
    ('("竞技场历史最高达到钻石Ⅱ","Target_TTT_Arena_RankScore","0,1700",(19,20))',
     '("累计挑战竞技场26次","Target_TTT_Arena_Challenge_Times","0,26",(19,20))'),
    ('("任意卡池累计抽卡10次","Target_TTT_DrawCard_AnyGachaTimes","0,10",(1,50000)),("累计挑战竞技场3次","Target_TTT_Arena_Challenge_Times","0,3",(19,10)),("累计完成扫荡3次"',
     '("任意卡池累计抽卡10次","Target_TTT_DrawCard_AnyGachaTimes","0,10",(1,50000)),("累计通关BOSS挑战1次","Target_TTT_Type_LevelClearNum","23,1",(106,1)),("累计完成扫荡3次"'),
    ('("无限之旅本周最高分达到1000分","Target_TTT_InfiniteChallenge_Score","0,1000",(100,40)),("累计挑战竞技场6次","Target_TTT_Arena_Challenge_Times","0,6",(19,10))',
     '("无限之旅本周最高分达到1000分","Target_TTT_InfiniteChallenge_Score","0,1000",(100,40)),("累计击败BOSS敌人6个","Target_TTT_BossMonster_Kill_Times","0,6",(102,5))'),
    ('竞技场段位分界（ArenaRank.xlsx 有效段位）：',
     '【CHG-013修订】前7天竞技场已改为累计挑战次数线3/6/10/14/18/22/26次；第8~14天为6条/天（只保留挑战线）。\n\n竞技场段位分界（ArenaRank.xlsx 有效段位，第8~11天段位线用）：'),
    ('path = out / "14日任务总表-评审-2026-08-31.xlsx"',
     'path = out / "14日任务总表-评审v2-2026-08-31.xlsx"'),
]
for old, new in pairs:
    if old not in t:
        print("MISS:", old[:60])
    else:
        t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("patched")
