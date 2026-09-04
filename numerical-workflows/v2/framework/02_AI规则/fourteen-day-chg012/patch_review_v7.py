# -*- coding: utf-8 -*-
"""make_review_xlsx.py 升版 v7：5209/5210/5310 真实类型 + CHG-018 说明。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "make_review_xlsx.py"
t = p.read_text(encoding="utf-8")
pairs = [
 ('("获得8件15级以上的装备","Target_TTT_Invaild","15,8",(100,40))',
  '("8件装备达到15级","Target_TTT_SpecialEquipmentLevelUp_Num","15,8",(100,40))'),
 ('("领取1次爬塔挂机奖励","Target_TTT_Invaild","0,1",(102,5))',
  '("领取1次爬塔挂机奖励","Target_TTT_RvDevice_IdleCollect_Times","0,1",(102,5))'),
 ('("获得4件20级以上的装备","Target_TTT_Invaild","20,4",(3027,2))',
  '("4件装备达到20级","Target_TTT_SpecialEquipmentLevelUp_Num","20,4",(3027,2))'),
 ('path = out / "14日任务总表-评审v6-2026-08-31.xlsx"',
  'path = out / "14日任务总表-评审v7-2026-08-31.xlsx"'),
 ('【CHG-017修订】前7天以用户v2评审表定稿；',
  '【CHG-018修订】爬塔后7天+3层/日；5209/5210/5310已配真实类型；'),
]
for old, new in pairs:
    assert old in t, old[:50]
    t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("patched")
