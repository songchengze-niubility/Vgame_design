# -*- coding: utf-8 -*-
"""根据「Vgame英雄设计(5)-收容物上阵技能数值修正版.xlsx」技能设计，
填「收容物属性分配」页签 S 级(SSR)13 行的：D职业细分、H/I/J专武三比、O二级属性，
并补 E~G/L~N 公式（与 A/B 行一致）。
"""
import openpyxl, shutil, time

import vgame_paths

SRC = str(vgame_paths.source_docs_root() / "框架v2" / "01_源表" / "养成属性分配.xlsx")
BAK = str(vgame_paths.design_root() / "备份" / "养成属性分配-备份-20260806-1544.xlsx")
shutil.copy(SRC, BAK)

# 51001~51013: (职业细分, 专武生命比H, 专武攻击比I, 专武防御比J, 二级属性名)
# 定位依据：修正版技能设计「队伍中所有X型角色…」；H/I/J 套 A 级同定位模板；二级属性按技能设计修正。
S_ROWS = {
    51001: ("坦克（生命）", 1.3, 0.7, 1.2, "生命百分比"),          # 防御型·最大生命提升
    51002: ("输出（法师）", 0.9, 1.05, 1.0, "必杀伤害加成"),        # 攻击型·必杀暴击伤害
    51003: ("输出（法师）", 0.9, 1.05, 1.0, "必杀伤害加成"),        # 攻击型·必杀伤害
    51004: ("辅助（均衡）", 1.1, 0.85, 1.05, "能量回复等级"),       # 辅助型·友军暴击回能
    51005: ("坦克（防御）", 1.2, 0.75, 1.3, "生命百分比"),          # 防御型·受击护盾(吃生命)
    51006: ("输出（战士）", 0.9, 1.05, 1.0, "技能伤害加成"),        # 源表DPS·技能文本空
    51007: ("输出（战士）", 0.9, 1.15, 0.8, "攻击百分比"),          # 攻击型·血契增伤
    51008: ("坦克（防御）", 1.2, 0.75, 1.3, "生命百分比"),          # 防御型·反击吃生命
    51009: ("输出（法师）", 0.8, 1.2, 1.0, "攻击百分比"),           # 攻击型·霜冻魔法增伤
    51010: ("坦克（防御）", 1.2, 0.75, 1.3, "技能伤害加成"),        # 源表Tank·技能文本空
    51011: ("输出（射手）", 0.9, 1.15, 0.8, "普攻伤害加成"),        # 技能为普攻暴击流(源表Heal不匹配，修正)
    51012: ("输出（战士）", 0.9, 1.15, 0.8, "攻击百分比"),          # 攻击型·流血增伤
    51013: ("输出（射手）", 0.9, 1.05, 1.0, "普攻伤害加成"),        # 攻击型·普攻必定暴击
}

wb = openpyxl.load_workbook(SRC, data_only=False)
ws = wb["收容物属性分配"]
assert ws["B4"].value == "虚妄之镜" and ws["B16"].value == "六芒圣楔", "S级行位置异常，停止写入"

def col_ref(col):
    return {"E": "E", "F": "F", "G": "G"}[col]

for r in range(4, 17):
    wid = ws.cell(r, 1).value
    job, h, i, j, sec = S_ROWS[wid]
    ws.cell(r, 4).value = job          # D 职业细分
    ws.cell(r, 8).value = h            # H 专武生命比
    ws.cell(r, 9).value = i            # I 专武攻击比
    ws.cell(r, 10).value = j           # J 专武防御比
    ws.cell(r, 15).value = sec         # O 二级属性
    # E~G 职业比公式（照 A 级结构）
    for col in ("E", "F", "G"):
        ws[f"{col}{r}"] = (
            f"=VLOOKUP($D{r},角色属性分配!$B$3:$E$14,"
            f"COLUMN(角色属性分配!{col}$26)-COLUMN(角色属性分配!$C$26),0)"
        )
    # K 品质系数公式（SSR→1.0，与 A/B 行一致）
    ws[f"K{r}"] = f"=VLOOKUP(C{r},角色属性分配!$B$19:$C$21,2,0)"
    # L~N 最终比公式
    ws[f"L{r}"] = f"=E{r}*H{r}*$K{r}"
    ws[f"M{r}"] = f"=F{r}*I{r}*$K{r}"
    ws[f"N{r}"] = f"=G{r}*J{r}*$K{r}"

wb.save(SRC)
print("已填充 S 级 13 行并补全公式，备份:", BAK)

# 验证
wb2 = openpyxl.load_workbook(SRC, data_only=False)
ws2 = wb2["收容物属性分配"]
for r in (4, 8, 11, 16):
    print("r%d: %s D=%s H=%s I=%s J=%s K=%s O=%s" % (
        r, ws2.cell(r, 2).value, ws2.cell(r, 4).value, ws2.cell(r, 8).value,
        ws2.cell(r, 9).value, ws2.cell(r, 10).value, ws2.cell(r, 11).value, ws2.cell(r, 15).value))
    print("   E=%s" % str(ws2[f"E{r}"].value)[:80])
    print("   L=%s" % ws2[f"L{r}"].value)
