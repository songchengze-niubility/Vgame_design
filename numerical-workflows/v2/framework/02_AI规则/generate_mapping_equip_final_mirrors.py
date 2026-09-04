#!/usr/bin/env python3
"""把映射装备 P02 审计底稿整理为一表一文件的最终配置镜像。只写 06_最终配置。"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from mapping_rare_rules import add_rare_effects, add_rare_pools, rare_pool_id
from mapping_named_rules import add_named_effects, add_named_pools, named_effect_id, EFFECT_IDS as NAMED_EFFECT_IDS

ROOT = Path(os.environ.get("VGAME_NUMERICAL_RUNTIME_ROOT", str(Path(__file__).resolve().parents[1])))
P02 = ROOT / "04_数值文档" / "配置粘贴包" / "映射装备全链路配置包_P02.xlsx"
OUT = Path(os.environ.get("MAPPING_EQUIP_FINAL_OUT", str(ROOT / "06_最终配置" / "映射装备")))
REPORT = Path(os.environ.get("MAPPING_EQUIP_FINAL_REPORT", str(ROOT / "05_验算核算" / "mapping-equip-final-mirrors-F01.json")))
CONFIG = Path(os.environ.get("VGAME_CONFIG_DATAS", ""))
CRAFT_UNLOCK_ID = 1198
CRAFT_UNLOCK_LEVEL_ID = 250061

# 养成属性唯一权威口径：03_沉淀MD/养成/映射装备养成数值沉淀-2026-07-07.md
MAIN_FIT_A = 0.6238763354456975
MAIN_FIT_B = 1.083083786770521
MAIN_FIT_C = -0.6257103438710419
MAIN_TARGET_BY_PART = {
    "SEPart_Weapon": ("Attack", 11250),
    "SEPart_Head": ("Hp", 18750),
    "SEPart_Armour": ("Hp", 18750),
    "SEPart_Glove": ("Armor", 2500),
    "SEPart_Belt": ("Armor", 2500),
    "SEPart_Shoe": ("Armor", 2500),
    "SEPart_Device": ("CritDmgBonusLevel", 8800),
    "SEPart_Decoration": ("CritLevel", 7200),
}
QUALITY_MAIN_COEF = {"Green": .20, "Blue": .30, "Purple": .45, "Orange": .70, "Red": 1.00}
QUALITY_SUB_COEF = {"Green": .35, "Blue": .50, "Purple": .65, "Orange": .85, "Red": 1.00}
QUALITY_SUB_COUNT = {"Green": (2, 2), "Blue": (2, 3), "Purple": (4, 4), "Orange": (4, 4), "Red": (4, 4)}
PERCENT_SUB_ATTRS = {"AttackBonus", "ArmorBonus", "HpBonus"}
FIXED_SUB_ATTRS = {
    "Attack", "Armor", "Hp", "CritLevel", "CritDmgBonusLevel",
    "EnergyPreAddBonusLevel", "CoolDownReduceLevel",
}
SUB_CURRENT_CAP = {
    "AttackBonus": .329,
    "ArmorBonus": .329,
    "HpBonus": .329,
    "Attack": 3701,
    "Armor": 2468,
    "Hp": 12338,
    "CritLevel": 2961,
    "CritDmgBonusLevel": 3619,
    "EnergyPreAddBonusLevel": 2961,
    "CoolDownReduceLevel": 4277,
}
SUB_STANDARD = {attr: cap * .50 for attr, cap in SUB_CURRENT_CAP.items()}
SUB_RANDOM_MULTIPLIER = {
    "Green": (1.00, 1.00),
    "Blue": (1.00, 1.00),
    "Purple": (1.00, 1.00),
    "Orange": (1.00, 1.20),
    "Red": (1.20, 1.40),
}
SUB_RANDOM_STEP = {attr: (.001 if attr in PERCENT_SUB_ATTRS else 1) for attr in SUB_CURRENT_CAP}
SUB_PERCENT_LEVEL_COEF = {level: .45 + .55 * ((level - 5) / 55) for level in range(5, 61, 5)}
SUB_FIXED_LEVEL_COEF = {level: .03 + .97 * (((level - 5) / 55) ** 1.35) for level in range(5, 61, 5)}
# 当前正式装备覆盖完整5品质×12等级。现有单列SubAttrCoef无法表达百分比/固定值双曲线，
# 因此为60个组合各建独立词条池，把对应类别等级倍率预乘进Effect数值，SubAttrCoef统一写1。
QUALITY_LEVEL_COMBOS = tuple(
    (quality, level)
    for quality in ("Green", "Blue", "Purple", "Orange", "Red")
    for level in range(5, 61, 5)
)
# 5001~5060为60个品质等级池；50001~50600为60组×10类新普通副属性定义。
SUB_POOL_ID_BY_COMBO = {combo: 5001 + index for index, combo in enumerate(QUALITY_LEVEL_COMBOS)}
SUB_EFFECT_IDS_BY_COMBO = {
    combo: tuple(50001 + index * 10 + slot for slot in range(10))
    for index, combo in enumerate(QUALITY_LEVEL_COMBOS)
}
NEW_SUB_POOL_IDS = set(SUB_POOL_ID_BY_COMBO.values())
NEW_SUB_EFFECT_IDS = {effect_id for ids in SUB_EFFECT_IDS_BY_COMBO.values() for effect_id in ids}
SUB_ATTR_ORDER = (
    "AttackBonus", "ArmorBonus", "HpBonus", "CoolDownReduceLevel",
    "EnergyPreAddBonusLevel", "CritLevel", "CritDmgBonusLevel",
    "Attack", "Armor", "Hp",
)
LEGACY_TEMPLATE_OFFSET = {"Green": 300, "Blue": 300, "Purple": 200, "Orange": 100, "Red": 0}
LEGACY_SLOT_BY_ATTR = {
    "AttackBonus": 1, "ArmorBonus": 3, "HpBonus": 4, "CoolDownReduceLevel": 5,
    "EnergyPreAddBonusLevel": 6, "CritLevel": 7, "CritDmgBonusLevel": 8,
    "Attack": 9, "Armor": 11, "Hp": 12,
}
ORDINARY_EFFECT_IDS = {offset + slot for offset in (0, 100, 200, 300) for slot in range(1, 13)}
REMOVED_DAMAGE_EFFECT_IDS = {offset + slot for offset in (0, 100, 200, 300) for slot in (13, 14)}

# 输出文件 -> (正式工作表名, P02数据分页, 状态, 正式相对路径)
SPECS = {
    "Items.xlsx": ("items", ["21_层级宝箱Items150", "23_主材Items72", "24_副材Items4", "24A_预览占位Items22"], "可粘贴", "items/Items.xlsx"),
    "Drop_dungeon.xlsx": ("Drop", ["25_Drop常规根110", "26_Drop宝箱池150", "27_Drop额外箱池", "28_Drop主材池", "29_Drop副材池4", "30A_首通Drop纯值"], "可粘贴", "Drop/Drop_dungeon.xlsx"),
    "EquipmentLevel.xlsx": ("EquipmentLevel", ["31_EquipmentLevel150"], "可粘贴", "level/EquipmentLevel.xlsx"),
    "UIlevel.xlsx": ("level", ["32_UIlevel150"], "可粘贴", "level/UIlevel.xlsx"),
    "ItemAccess.xlsx": ("ItemAccess", ["34_ItemAccess"], "需按建议列替换", "items/ItemAccess.xlsx"),
    "PortableExp.xlsx": ("PortableExp", ["01_PortableExp"], "可粘贴", "SpecialEquipment/Portable/PortableExp.xlsx"),
    "PortableLvUp.xlsx": ("PortableLvUp", ["03_PortableLvUp"], "可粘贴", "SpecialEquipment/Portable/PortableLvUp.xlsx"),
}

BLOCKED = {}

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def copy_cell(src, dst):
    dst.value = src.value
    if src.has_style:
        dst._style = copy(src._style)
    if src.number_format:
        dst.number_format = src.number_format
    dst.alignment = copy(src.alignment)

def add_note(wb, file_name, status, formal_path, sources, rows, note=""):
    ws = wb.active
    ws.title = "中文说明"
    data = [
        ("配置镜像文件", file_name), ("交付批次", "MAPEQUIP-20260713-F01 / 1.2（Drop稳定排序）"),
        ("落表状态", status), ("正式配置位置", str(CONFIG / formal_path) if formal_path else "建议新增表，正式路径待定"),
        ("数据来源", "、".join(sources) if sources else "仅复制正式Schema"), ("有效数据行", rows),
        ("使用方式", "确认后，复制配置页第5行起的数据到同名正式表；不得整表覆盖正式文件。"),
        ("重要提醒", note or "正式配置当前保持只读；中文表头用于审阅，英文名用于字段对应。"),
    ]
    ws.append(["项目", "内容"])
    for row in data: ws.append(row)
    ws.column_dimensions["A"].width = 24; ws.column_dimensions["B"].width = 100
    ws.freeze_panes = "A2"
    for cell in ws[1]: cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="17365D")
    for row in ws.iter_rows():
        for c in row: c.alignment = Alignment(vertical="top", wrap_text=True)

def copy_p02_sheet(dst, src, start_row, include_header):
    if include_header:
        for r in range(1, 5):
            for c in range(1, src.max_column + 1): copy_cell(src.cell(r,c), dst.cell(r,c))
        start_row = 5
    for r in range(5, src.max_row + 1):
        if all(src.cell(r,c).value is None for c in range(1,src.max_column+1)): continue
        for c in range(1, src.max_column + 1): copy_cell(src.cell(r,c), dst.cell(start_row,c))
        start_row += 1
    return start_row

def copy_drop_sheets_sorted(dst, p02, source_sheets):
    first=p02[source_sheets[0]]
    for r in range(1,5):
        for c in range(1,first.max_column+1): copy_cell(first.cell(r,c),dst.cell(r,c))
    records=[]; sequence=0
    for sheet_name in source_sheets:
        src=p02[sheet_name]
        for r in range(5,src.max_row+1):
            if all(src.cell(r,c).value is None for c in range(1,src.max_column+1)): continue
            drop_id=src.cell(r,2).value
            if not isinstance(drop_id,int): raise ValueError(f"{sheet_name}!B{r} DropId={drop_id}")
            # Vgame一级DropId为8位、二级池为5位：先一级后二级，各自升序；同ID保持原生成顺序。
            tier=0 if drop_id>=10_000_000 else 1
            records.append(((tier,drop_id,sequence),src,r))
            sequence+=1
    next_row=5
    for _,src,r in sorted(records,key=lambda item:item[0]):
        for c in range(1,src.max_column+1): copy_cell(src.cell(r,c),dst.cell(next_row,c))
        next_row+=1
    return next_row

def find_col(ws, field):
    for c in range(1, ws.max_column + 1):
        if field in str(ws.cell(4, c).value or ""):
            return c
    raise KeyError(f"{ws.title}: missing {field}")

def find_var_col(ws, field):
    for c in range(1, ws.max_column + 1):
        if ws.cell(1, c).value == field:
            return c
    raise KeyError(f"{ws.title}: missing ##var {field}")

def normalize_preview(value, valid_item_ids, context):
    """校验展示物品存在，并把“不显示数量”统一规范为 -1。"""
    if value in (None, ""):
        return value
    parts=[]
    for part in str(value).split(";"):
        if not part:
            continue
        try:
            item_id, quantity=(int(x) for x in part.split(","))
        except ValueError as exc:
            raise ValueError(f"{context}: invalid PropType {part!r}") from exc
        if item_id not in valid_item_ids:
            raise ValueError(f"{context}: ItemId={item_id} does not exist in formal Items.xlsx")
        parts.append(f"{item_id},{-1 if quantity < 0 else quantity}")
    return ";".join(parts)

def build_mapping_uilevel_file(p02, file_name, sheet_name, formal_rel):
    """把P02的150行提案落为正式UIlevel Schema，并校验奖励预览。"""
    proposal=p02["32_UIlevel150"]
    pcols={field:find_col(proposal, field) for field in (
        "LevelId","TierNum","Variant","Reward","FirstReward","FirstRewardDrop",
        "FallRewardDrop","MultiSettlementTimes","Vitality",
    )}
    source=CONFIG/formal_rel
    fw=load_workbook(source, data_only=False); fs=fw[sheet_name]
    fcols={field:find_var_col(fs, field) for field in (
        "LevelId","Reward","FirstReward","FirstRewardDrop",
        "FallRewardDrop","MultiSettlementTimes","Vitality",
    )}
    source_rows={fs.cell(r, fcols["LevelId"]).value:r for r in range(5, fs.max_row+1)
                 if fs.cell(r, fcols["LevelId"]).value is not None}
    records=[]
    for r in range(5, proposal.max_row+1):
        level_id=proposal.cell(r, pcols["LevelId"]).value
        if level_id is None:
            continue
        if level_id not in source_rows:
            raise KeyError(f"UIlevel source missing LevelId={level_id}")
        records.append({field:proposal.cell(r, col).value for field,col in pcols.items()})
    if len(records) != 150:
        raise ValueError(f"expected 150 mapping UIlevel rows, got {len(records)}")
    iw=load_workbook(CONFIG/"items/Items.xlsx",read_only=False,data_only=True); isheet=iw["items"]
    item_id_col=find_var_col(isheet,"Id")
    formal_item_ids={cell.value for (row,col),cell in isheet._cells.items()
                     if row>=5 and col==item_id_col and isinstance(cell.value,int)}
    iw.close()
    for rec in records:
        level_id=rec["LevelId"]
        rec["Reward"]=normalize_preview(rec["Reward"],formal_item_ids,f"UIlevel[{level_id}].Reward")
        rec["FirstReward"]=normalize_preview(rec["FirstReward"],formal_item_ids,f"UIlevel[{level_id}].FirstReward")

    wb=Workbook(); add_note(wb, file_name, "可粘贴：150行 Reward / FirstReward 展示已核对", formal_rel,
                            ["32_UIlevel150", "正式UIlevel行"], len(records),
                            "游戏展示读取 Reward（普通）和 FirstReward（首通）。所有引用已按正式 Items.xlsx 校验；负数数量表示不显示数量，统一写为 -1。LevelFPDrop/LevelPPDrop 保留正式源表原值，不作为本次交付字段。")
    ws=wb.create_sheet(sheet_name); wb._sheets=[ws, wb["中文说明"]]
    width=schema_width(fs)
    for r in range(1,5):
        for c in range(1,width+1): copy_cell(fs.cell(r,c), ws.cell(r,c))
    for out_row,rec in enumerate(records,5):
        source_row=source_rows[rec["LevelId"]]
        for c in range(1,width+1): copy_cell(fs.cell(source_row,c), ws.cell(out_row,c))
        for field in ("Reward","FirstReward","FirstRewardDrop","FallRewardDrop","MultiSettlementTimes","Vitality"):
            ws.cell(out_row, fcols[field]).value=rec[field]
    ws.freeze_panes="A5"; ws.auto_filter.ref=f"A4:{get_column_letter(width)}{4+len(records)}"
    for c in range(1,width+1): ws.column_dimensions[get_column_letter(c)].width=max(12,min(28,len(str(ws.cell(4,c).value or ""))+4))
    fw.close(); wb.save(OUT/file_name)
    return len(records)

def build_data_file(p02, file_name, sheet_name, source_sheets, status, formal_rel):
    if file_name=="UIlevel.xlsx":
        return build_mapping_uilevel_file(p02, file_name, sheet_name, formal_rel)
    wb=Workbook(); add_note(wb,file_name,status,formal_rel,source_sheets,0,
        "SpecialEquipmentQuality 为原子变更的一部分，未完成主属性迁移前严禁单独落表。" if file_name=="SpecialEquipmentQuality.xlsx" else "")
    ws=wb.create_sheet(sheet_name); wb._sheets = [ws, wb["中文说明"]]; next_row=5
    if file_name=="Drop_dungeon.xlsx":
        next_row=copy_drop_sheets_sorted(ws,p02,source_sheets)
    else:
        for i,s in enumerate(source_sheets): next_row=copy_p02_sheet(ws,p02[s],next_row,i==0)
    rows=next_row-5
    wb["中文说明"][7][1].value=rows
    ws.freeze_panes="A5"; ws.auto_filter.ref=ws.dimensions
    for c in range(1,ws.max_column+1): ws.column_dimensions[get_column_letter(c)].width=min(42,max(12,len(str(ws.cell(4,c).value or ""))+2))
    wb.save(OUT/file_name)
    return rows

def build_blocked(file_name,sheet_name,reason,formal_rel):
    wb=Workbook(); add_note(wb,file_name,"阻断：不可粘贴",formal_rel,[],0,reason)
    ws=wb.create_sheet(sheet_name); wb._sheets = [ws, wb["中文说明"]]
    src=CONFIG/formal_rel
    if src.exists():
        fw=load_workbook(src,read_only=False,data_only=False); fs=fw[sheet_name]
        for r in range(1,5):
            for c in range(1,fs.max_column+1): copy_cell(fs.cell(r,c),ws.cell(r,c))
        fw.close()
    ws.freeze_panes="A5"; wb.save(OUT/file_name)

def schema_width(ws):
    return max(c for c in range(1, ws.max_column + 1) if any(ws.cell(r,c).value is not None for r in range(1,5)))

def build_formal_rows(file_name, sheet_name, formal_rel, rows, status, note):
    src=CONFIG/formal_rel; fw=load_workbook(src,data_only=False); fs=fw[sheet_name]
    wb=Workbook(); add_note(wb,file_name,status,formal_rel,[],len(rows),note)
    ws=wb.create_sheet(sheet_name); wb._sheets=[ws,wb["中文说明"]]
    width=schema_width(fs)
    for r in range(1,5):
        for c in range(1,width+1): copy_cell(fs.cell(r,c),ws.cell(r,c))
    for rr,values in enumerate(rows,5):
        for c,v in enumerate(values,1): ws.cell(rr,c).value=v
    ws.freeze_panes="A5"; ws.auto_filter.ref=f"A4:{get_column_letter(width)}{max(4,4+len(rows))}"
    for c in range(1,width+1): ws.column_dimensions[get_column_letter(c)].width=max(12,min(28,len(str(ws.cell(4,c).value or ''))+4))
    fw.close(); wb.save(OUT/file_name)


def sub_level_coef(attr, level):
    if attr in PERCENT_SUB_ATTRS:
        return SUB_PERCENT_LEVEL_COEF[level]
    if attr in FIXED_SUB_ATTRS:
        return SUB_FIXED_LEVEL_COEF[level]
    raise KeyError(f"未知副属性类型：{attr}")


def sub_effect_range(attr, quality, level):
    standard = SUB_STANDARD[attr]
    level_coef = sub_level_coef(attr, level)
    quality_coef = QUALITY_SUB_COEF[quality]
    random_min, random_max = SUB_RANDOM_MULTIPLIER[quality]
    # 保留足够精度，最终展示仍按百分比0.001、固定值整数取整。
    # 当前可见消费代码直接读取Effect数值；QualityCoefficient用于参数门槛/评分，不在取值时二次缩放。
    # 因此品质系数必须在配置生成时预乘，确保Effect里就是玩家最终获得的副属性区间。
    value_min = round(standard * level_coef * quality_coef * random_min, 9 if attr in PERCENT_SUB_ATTRS else 6)
    value_max = round(standard * level_coef * quality_coef * random_max, 9 if attr in PERCENT_SUB_ATTRS else 6)
    return value_max, value_min, SUB_RANDOM_STEP[attr]


def attribute_delivery_records():
    # 程序式：Value * Grow^(装备等级/5) + Param。
    # 转换规则：Lv5/Lv60精确命中设计目标，并对Lv10~55完整精度目标曲线做最小二乘拟合。
    # 沿用正式SpecialEquipment每件装备原Attribute1List的独立ID，只撤销Attribute2List。
    eqw=load_workbook(CONFIG/"SpecialEquipment/SpecialEquipment.xlsx",data_only=False); eqs=eqw["SpecialEquipment"]
    eq_cols={eqs.cell(1,c).value:c for c in range(1,eqs.max_column+1) if eqs.cell(1,c).value}
    main_rule_by_id={}
    for r in range(5,eqs.max_row+1):
        if eqs.cell(r,eq_cols["Id"]).value is None: continue
        main_id=int(str(eqs.cell(r,eq_cols["Attribute1List"]).value).split(",")[0])
        attr,target=MAIN_TARGET_BY_PART[eqs.cell(r,eq_cols["Part"]).value]
        candidate=(attr,target)
        if main_id in main_rule_by_id and main_rule_by_id[main_id] != candidate:
            raise ValueError(f"MainId={main_id} 被不同部位口径复用")
        main_rule_by_id[main_id]=candidate
    eqw.close()
    mp="SpecialEquipment/SpecialEquipmentMain.xlsx"; mw=load_workbook(CONFIG/mp,data_only=False); ms=mw["SpecialEquipment"]
    width=schema_width(ms); main_cols={ms.cell(1,c).value:c-1 for c in range(1,width+1)}; main_rows=[]
    target_by_attr={attr:target for attr,target in MAIN_TARGET_BY_PART.values()}
    for r in range(5,ms.max_row+1):
        vals=[ms.cell(r,c).value for c in range(1,width+1)]
        main_id=vals[main_cols["Id"]]
        if main_id is None: continue
        attr,target=main_rule_by_id.get(main_id,(vals[main_cols["Attribute"]],None))
        if target is None:
            if attr not in target_by_attr:
                raise ValueError(f"未引用MainId={main_id} 的属性 {attr} 无兼容目标值")
            target=target_by_attr[attr]
        vals[main_cols["Attribute"]]=attr
        vals[main_cols["Value"]]=round(target*MAIN_FIT_A,12)
        vals[main_cols["Grow"]]=round(MAIN_FIT_B,12)
        vals[main_cols["Param"]]=round(target*MAIN_FIT_C,12)
        main_rows.append(vals)
    mw.close()
    build_formal_rows("SpecialEquipmentMain.xlsx","SpecialEquipment","SpecialEquipment/SpecialEquipmentMain.xlsx",main_rows,"可粘贴：190条独立主属性参数",
        f"以当前正式{sum(1 for _ in main_rule_by_id)}个在用Main ID校验部位映射，并保留SpecialEquipmentMain完整{len(main_rows)}行兼容定义。每件只保留一条主属性。部位口径：武器攻击、头盔/护甲生命、手套/腰带/鞋子防御、装置暴伤等级、饰品暴击等级。公式：Value×Grow^(装备等级/5)+Param，品质差异由GradeCoefficient相乘。")

    # 保留正式普通/特殊/历史定义，并追加60组“品质×等级”的十类普通副属性。
    # 双等级曲线预乘进Effect：百分比前期高且慢成长，固定值前期低且快成长。
    ep="SpecialEquipment/SpecialEquipmentEffect.xlsx"; ew=load_workbook(CONFIG/ep,data_only=False); es=ew["SpecialEquipment"]
    width=schema_width(es); effect_rows=[]
    effect_cols={es.cell(1,c).value:c-1 for c in range(1,width+1)}
    source_effect_by_id={}
    for r in range(5,es.max_row+1):
        vals=[es.cell(r,c).value for c in range(1,width+1)]
        effect_id=vals[effect_cols["Id"]]
        if effect_id is None: continue
        # 正式表可能已经同步过上一版06；新ID段按当前规则覆盖重建，不重复追加。
        if effect_id in NEW_SUB_EFFECT_IDS: continue
        source_effect_by_id[effect_id]=vals
        effect_rows.append(vals)
    existing_ids={row[effect_cols["Id"]] for row in effect_rows}
    new_effect_rows=[]
    for combo in QUALITY_LEVEL_COMBOS:
        quality,level=combo
        for attr,new_id in zip(SUB_ATTR_ORDER,SUB_EFFECT_IDS_BY_COMBO[combo]):
            if new_id in existing_ids:
                raise ValueError(f"新增副属性EffectId冲突：{new_id}")
            template_id=LEGACY_TEMPLATE_OFFSET[quality]+LEGACY_SLOT_BY_ATTR[attr]
            if template_id not in source_effect_by_id:
                raise ValueError(f"副属性模板EffectId不存在：{template_id}")
            vals=list(source_effect_by_id[template_id])
            value_max,value_min,random_min=sub_effect_range(attr,quality,level)
            vals[effect_cols["Id"]]=new_id
            vals[effect_cols["Attribute"]]=attr
            vals[effect_cols["ValueMax"]]=value_max
            vals[effect_cols["ValueMin"]]=value_min
            vals[effect_cols["RandomMin"]]=random_min
            new_effect_rows.append(vals)
    effect_rows.extend(new_effect_rows)
    add_rare_effects(effect_rows, effect_cols)
    add_named_effects(effect_rows, effect_cols)
    ew.close(); build_formal_rows("SpecialEquipmentEffect.xlsx","SpecialEquipment",ep,effect_rows,"可粘贴：双曲线分品质等级副属性",
        "保留正式历史定义，新增50001~50600共600条普通副属性。百分比/固定值等级倍率与0.35/0.50/0.65/0.85/1.00品质系数均已预乘进ValueMin/ValueMax，使Effect直接存最终值。绿/蓝/紫ValueMin=ValueMax；金为标准值100%~120%；红为120%~140%。QualityCoefficient保留作参数门槛/评分，取值时不得再次缩放；SubAttrCoef统一为1。CHG-023补72条稀有增伤Effect。CHG-025：21条具名Effect经同号单技能池供红装SpecialEffect引用，不使用FixEffect；普通副属性不变。")

    sp="SpecialEquipment/SpecialEquipmentSubAttrCoef.xlsx"; sw=load_workbook(CONFIG/sp,data_only=False); ss=sw["SpecialEquipmentSubAttrCoef"]
    width=schema_width(ss); sub_rows=[]
    sub_cols={ss.cell(1,c).value:c-1 for c in range(1,width+1)}
    for r in range(5,ss.max_row+1):
        vals=[ss.cell(r,c).value for c in range(1,width+1)]
        if vals[sub_cols["Id"]] is None: continue
        equip_lv=vals[sub_cols["EquipLv"]]
        if equip_lv not in SUB_PERCENT_LEVEL_COEF: raise ValueError(f"未知副属性等级档：{equip_lv}")
        vals[sub_cols["SubAttrCoef"]]=1.0
        sub_rows.append(vals)
    if {row[sub_cols["EquipLv"]] for row in sub_rows} != set(SUB_PERCENT_LEVEL_COEF):
        raise ValueError("SpecialEquipmentSubAttrCoef 未覆盖沉淀MD的12个等级档")
    sw.close(); build_formal_rows("SpecialEquipmentSubAttrCoef.xlsx","SpecialEquipmentSubAttrCoef",sp,sub_rows,"可粘贴：12档副属性公共倍率",
        "现有Schema只有一列SubAttrCoef，无法同时承载百分比/固定值双曲线；双曲线已预乘进分品质等级Effect，故12档统一写1.00，避免重复缩放。")

    qp="SpecialEquipment/SpecialEquipmentQuality.xlsx"; qw=load_workbook(CONFIG/qp,data_only=False); qs=qw["SpecialEquipment"]
    width=schema_width(qs); quality_rows=[]
    quality_cols={qs.cell(1,c).value:c-1 for c in range(1,width+1)}
    for r in range(5,qs.max_row+1):
        vals=[qs.cell(r,c).value for c in range(1,width+1)]
        quality=vals[quality_cols["Quality"]]
        if quality is None: continue
        effect_min,effect_max=QUALITY_SUB_COUNT[quality]
        vals[quality_cols["EffectNumMin"]]=effect_min
        vals[quality_cols["EffectNumMax"]]=effect_max
        vals[quality_cols["GradeCoefficient"]]=QUALITY_MAIN_COEF[quality]
        vals[quality_cols["QualityCoefficient"]]=QUALITY_SUB_COEF[quality]
        quality_rows.append(vals)
    qw.close(); build_formal_rows("SpecialEquipmentQuality.xlsx","SpecialEquipment",qp,quality_rows,"可粘贴：品质系数与副属性条数",
        "主属性系数保持0.20/0.30/0.45/0.70/1.00；副属性品质系数为0.35/0.50/0.65/0.85/1.00，并已预乘进新Effect最终值；条数为绿2、蓝2~3、紫4、金4、红4。红色随机上限相对绿色定值为1.40/0.35=4倍。QualityCoefficient继续保留作参数门槛/评分。必须与 Equipment/Main/Effect/EffectDrop/SubAttrCoef 原子评审。")
    return [
        {"file":"SpecialEquipmentMain.xlsx","sheet":"SpecialEquipment","status":"可粘贴：190条独立主属性参数","rows":len(main_rows),"formal":str(CONFIG/"SpecialEquipment/SpecialEquipmentMain.xlsx")},
        {"file":"SpecialEquipmentEffect.xlsx","sheet":"SpecialEquipment","status":"可粘贴：双曲线分品质等级副属性","rows":len(effect_rows),"formal":str(CONFIG/ep)},
        {"file":"SpecialEquipmentSubAttrCoef.xlsx","sheet":"SpecialEquipmentSubAttrCoef","status":"可粘贴：12档副属性公共倍率","rows":len(sub_rows),"formal":str(CONFIG/sp)},
        {"file":"SpecialEquipmentQuality.xlsx","sheet":"SpecialEquipment","status":"可粘贴：品质系数与副属性条数","rows":len(quality_rows),"formal":str(CONFIG/qp)},
    ]

def equipment_template_records(records):
    ep="SpecialEquipment/SpecialEquipment.xlsx"; ew=load_workbook(CONFIG/ep,data_only=False); es=ew["SpecialEquipment"]
    width=schema_width(es); equip_rows=[]
    equip_cols={es.cell(1,c).value:c-1 for c in range(1,width+1)}
    for r in range(5,es.max_row+1):
        vals=[es.cell(r,c).value for c in range(1,width+1)]
        if vals[equip_cols["Id"]] is None: continue
        # Attribute1List保留每件正式装备原有的独立Main ID。
        vals[equip_cols["Attribute2List"]]=None
        quality=vals[equip_cols["Quality"]]; level=vals[equip_cols["Grade"]]
        combo=(quality,level)
        if combo not in QUALITY_LEVEL_COMBOS:
            raise ValueError(f"正式装备出现未登记品质等级组合：{combo}")
        vals[equip_cols["Effect"]]=SUB_POOL_ID_BY_COMBO[combo]
        rare_pool=rare_pool_id(quality,level)
        vals[equip_cols["RareEffect"]]=rare_pool
        vals[equip_cols["SpecialEffect"]]=named_effect_id(quality, vals[equip_cols["Name"]])
        if vals[equip_cols["FixEffect"]] in NAMED_EFFECT_IDS:
            vals[equip_cols["FixEffect"]]=None
        equip_rows.append(vals)
    ew.close()
    equip_ids=[row[equip_cols["Id"]] for row in equip_rows]
    build_formal_rows("SpecialEquipment.xlsx","SpecialEquipment",ep,equip_rows,f"可粘贴：{len(equip_rows)}条正式装备属性改造",
        f"以当前正式SpecialEquipment {min(equip_ids)}~{max(equip_ids)}为底稿；Attribute1List保留既有Main ID并清空Attribute2List。全部装备Effect按品质×等级改指向5001~5060；CHG-025绿蓝紫RareEffect为空，金红仍按5~20/25~40/45~60级指向6001~6006。SpecialEffect仅红装按名称引用21个同号单技能池；三组别名、同名35/55级手套共用30602，虚空不绑定。撤回具名FixEffect；刷新数量不改。")

    dp="SpecialEquipment/SpecialEquipmentEffectDrop.xlsx"; dw=load_workbook(CONFIG/dp,data_only=False); ds=dw["SpecialEquipment"]
    active_pool_ids={row[equip_cols["Effect"]] for row in equip_rows if row[equip_cols["Effect"]] is not None}
    width=schema_width(ds); pool_rows=[]
    pool_cols={ds.cell(1,c).value:c-1 for c in range(1,width+1)}
    existing_pool_ids=set()
    for r in range(5,ds.max_row+1):
        vals=[ds.cell(r,c).value for c in range(1,width+1)]
        pool_id=vals[pool_cols["Id"]]
        if pool_id is None: continue
        # 5001~5060为本设计受控ID段；正式表已有旧版时跳过并在下方全量重建。
        if pool_id in NEW_SUB_POOL_IDS: continue
        existing_pool_ids.add(pool_id)
        if pool_id in (101,201,301):
            # 旧通用品质池退出在用引用但继续清理伤害类与语义重复，兼容历史数据。
            offset={101:100,201:200,301:300}[pool_id]
            vals[pool_cols["EffectList"]]=";".join(
                f"{offset+LEGACY_SLOT_BY_ATTR[attr]},100" for attr in SUB_ATTR_ORDER
            )
        elif pool_id in active_pool_ids:
            kept=[]; seen_attrs=set()
            for token in str(vals[pool_cols["EffectList"]] or "").split(";"):
                if not token: continue
                effect_id=int(token.split(",")[0])
                if effect_id in REMOVED_DAMAGE_EFFECT_IDS: continue
                kept.append(token)
            vals[pool_cols["EffectList"]]=";".join(kept)
        pool_rows.append(vals)
    for combo,pool_id in SUB_POOL_ID_BY_COMBO.items():
        if pool_id in existing_pool_ids:
            raise ValueError(f"新增副属性池ID冲突：{pool_id}")
        effect_list=";".join(f"{effect_id},100" for effect_id in SUB_EFFECT_IDS_BY_COMBO[combo])
        vals=[None]*width
        vals[pool_cols["Id"]]=pool_id
        vals[pool_cols["EffectList"]]=effect_list
        pool_rows.append(vals)
    add_rare_pools(pool_rows, pool_cols)
    add_named_pools(pool_rows, pool_cols)
    dw.close()
    build_formal_rows("SpecialEquipmentEffectDrop.xlsx","SpecialEquipment",dp,pool_rows,"可粘贴：分品质等级十类副属性池",
        "保留正式历史池和5001~5060共60个品质等级池。6001~6006六个稀有增伤池只供金红RareEffect使用。CHG-025新增21个具名池30101~30802（按技能编号保留间隔），每池仅同号Effect、权重100，供红装SpecialEffect按名称引用。")
    return [
        {"file":"SpecialEquipment.xlsx","sheet":"SpecialEquipment","status":f"可粘贴：{len(equip_rows)}条正式装备属性改造","rows":len(equip_rows),"formal":str(CONFIG/ep)},
        {"file":"SpecialEquipmentEffectDrop.xlsx","sheet":"SpecialEquipment","status":"可粘贴：分品质等级十类副属性池","rows":len(pool_rows),"formal":str(CONFIG/dp)},
    ]

def portable_range_records():
    # 用户确认：范围就是对应合成结果的等级范围；投入下限固定比结果下限低 5 级。
    # 用户确认：本模块不得复用既有解锁条件，使用正式表连续空闲段 1190~1197 全量新增。
    result_levels=[(10,10,1190),(15,20,1191),(25,30,1192),(35,40,1193),(40,45,1194),(45,50,1195),(50,55,1196),(55,60,1197)]
    rows=[[None,range_id,level_min,level_max,unlock_id,level_min-5]
          for range_id,(level_min,level_max,unlock_id) in enumerate(result_levels,1)]
    build_formal_rows("PortableRange.xlsx","PortableRange","SpecialEquipment/Portable/PortableRange.xlsx",rows,"可粘贴：8个已确认合成区间",
        "已确认：LevelMin~LevelMax等于该档合成结果等级范围；EquipMinLv=LevelMin-5；UnlockId为本模块新增的同等级玩家等级解锁条件。RangeId 1~8 分别对应 Generate 4401~4408。")
    unlock_rows=[
        [None,1190,"映射装备合成等级解锁","UnLock_UUT_player_Grade",10,None],
        [None,1191,"映射装备合成等级解锁","UnLock_UUT_player_Grade",15,None],
        [None,1192,"映射装备合成等级解锁","UnLock_UUT_player_Grade",25,None],
        [None,1193,"映射装备合成等级解锁","UnLock_UUT_player_Grade",35,None],
        [None,1194,"映射装备合成等级解锁","UnLock_UUT_player_Grade",40,None],
        [None,1195,"映射装备合成等级解锁","UnLock_UUT_player_Grade",45,None],
        [None,1196,"映射装备合成等级解锁","UnLock_UUT_player_Grade",50,None],
        [None,1197,"映射装备合成等级解锁","UnLock_UUT_player_Grade",55,None],
        [None,CRAFT_UNLOCK_ID,"映射装备打造通关解锁","UnLock_UUT_Level",CRAFT_UNLOCK_LEVEL_ID,None],
    ]
    build_formal_rows("Unlock.xlsx","Unlock","unlock/Unlock.xlsx",unlock_rows,"可粘贴：新增8条合成档条件+1条打造条件",
        "PortableRange.RangeId 1~8 继续引用 UnlockId=1190~1197；打造单独使用 UnlockId=1198，条件为通关映射装备第6层 LevelId=250061。不修改合成开放链，不复用既有解锁记录。")

    system_rel="system_open/SystemOpen.xlsx"; sw=load_workbook(CONFIG/system_rel,data_only=False); ss=sw["SystemOpen"]
    width=schema_width(ss); id_col=find_var_col(ss,"Id"); unlock_col=find_var_col(ss,"UnlockId"); note_col=find_var_col(ss,"##")
    source_row=next(r for r in range(5,ss.max_row+1) if ss.cell(r,id_col).value==54)
    system_row=[ss.cell(source_row,c).value for c in range(1,width+1)]
    system_row[unlock_col-1]=CRAFT_UNLOCK_ID
    system_row[note_col-1]="通关映射装备第6层"
    sw.close()
    build_formal_rows("SystemOpen.xlsx","SystemOpen",system_rel,[system_row],"可粘贴：打造开启条件改为通关映射装备第6层",
        "仅修改 SystemOpen.Id=54（装备打造）的 UnlockId 为1198及条件备注；ParentId、UIViewName、JumpParams等其余字段逐格保留正式源表值。")
    return [
        {"file":"PortableRange.xlsx","sheet":"PortableRange","status":"可粘贴：8个已确认合成区间","rows":len(rows),"formal":str(CONFIG/"SpecialEquipment/Portable/PortableRange.xlsx")},
        {"file":"Unlock.xlsx","sheet":"Unlock","status":"可粘贴：新增8条合成档条件+1条打造条件","rows":len(unlock_rows),"formal":str(CONFIG/"unlock/Unlock.xlsx")},
        {"file":"SystemOpen.xlsx","sheet":"SystemOpen","status":"可粘贴：打造通关第6层开启","rows":1,"formal":str(CONFIG/system_rel)},
    ]

def portable_probability_records(p02):
    specs=[
        ("PortableCompoundProb.xlsx","04_CompoundProb","SpecialEquipment/Portable/PortableCompoundProb.xlsx",300,"合成成品品质概率"),
        ("PortableCraftProb.xlsx","05_CraftProb","SpecialEquipment/Portable/PortableCraftProb.xlsx",180,"打造成品品质概率"),
    ]
    records=[]
    for file_name,source_sheet,formal_rel,expected,note in specs:
        src=p02[source_sheet]; rows=[]
        for r in range(5,src.max_row+1):
            vals=[src.cell(r,c).value for c in range(1,5)]
            if vals[0] is not None: rows.append([None,*vals])
        if len(rows)!=expected: raise ValueError(f"{source_sheet} rows={len(rows)}, expected={expected}")
        build_formal_rows(file_name,"PortableCompoundProb",formal_rel,rows,"可粘贴：完整正式Schema",
            f"正式5列表头完整复制；{note}仅由QualityList承载，权重和固定为1000。")
        records.append({"file":file_name,"sheet":"PortableCompoundProb","status":"可粘贴：完整正式Schema","rows":len(rows),"formal":str(CONFIG/formal_rel)})
    return records

def portable_compound_craft_generate_records(p02):
    tier_levels=[
        [(10,1000)],[(15,700),(20,300)],[(25,700),(30,300)],[(35,700),(40,300)],
        [(40,650),(45,350)],[(45,650),(50,350)],[(50,650),(55,350)],[(55,650),(60,350)],
    ]
    # 打造只选择主材档位，不选择具体装备等级：同档位 Generate 使用同一等级概率池。
    # 保留现有 120 个 Generate / 360 条 Craft 引用，避免改变既有 CraftId 映射。
    craft_levels=[[10],[15,20],[25,30],[35,40],[40,45],[45,50],[50,55],[55,60]]
    all_parts="1;2;3;4;5;6;7;8"

    # 正式Generate Schema：保留两列策划备注位(C/D)，配置字段从E开始。
    src=p02["22_Generate150"]; generate_rows=[]
    for r in range(5,src.max_row+1):
        vals=[src.cell(r,c).value for c in range(1,11)]
        if vals[0] is None: continue
        generate_rows.append([None,vals[0],vals[1],None,vals[2],vals[3],vals[4],vals[5],vals[6],vals[7],vals[8]])

    compound_generate={}
    for tier,levels in enumerate(tier_levels,1):
        gid=4400+tier; compound_generate[tier]=gid
        grade_list=";".join(f"{lv},{weight}" for lv,weight in levels)
        generate_rows.append([None,gid,f"映射装备合成档{tier}等级池",None,grade_list,None,None,all_parts,None,1,1])

    parts=[
        ("SEPart_Weapon",1,0,(1152,1153)),("SEPart_Head",2,1,(1153,1154)),
        ("SEPart_Armour",3,1,(1153,1154)),("SEPart_Glove",4,1,(1153,1154)),
        ("SEPart_Belt",5,1,(1153,1154)),("SEPart_Shoe",6,1,(1153,1154)),
        ("SEPart_Device",7,2,(1154,1155)),("SEPart_Decoration",8,2,(1154,1155)),
    ]
    craft_generate={}; gid=4501
    for tier,levels in enumerate(craft_levels,1):
        grade_list=";".join(f"{lv},{weight}" for lv,weight in tier_levels[tier-1])
        for level in levels:
            for part_enum,part_num,_,_ in parts:
                craft_generate[(tier,level,part_enum)]=gid
                generate_rows.append([None,gid,f"映射装备打造档{tier}-{part_enum}-等级池(兼容Lv{level}引用)",None,grade_list,None,None,str(part_num),None,1,1])
                gid+=1
    build_formal_rows("SpecialEquipmentGenerate.xlsx","SpecialEquipment","SpecialEquipment/SpecialEquipmentGenerate.xlsx",generate_rows,
        "可粘贴：完整正式Schema及等级池",
        "正式11列表头完整复制；4201~4350为副本宝箱并在QualityList配置开装品质权重，4401~4408为合成等级概率，4501~4620为打造档位等级概率池。")

    qualities=["Green","Blue","Purple","Orange","Red"]
    costs=[
        [100,140,200,280,400],
        [350,490,700,980,1400],
        [1000,1400,2000,2800,4000],
        [2500,3500,5000,7000,10000],
        [3800,5320,7600,10640,15200],
        [5500,7700,11000,15400,22000],
        [7500,10500,15000,21000,30000],
        [10000,14000,20000,28000,40000],
    ]
    rows=[]; row_id=1
    for range_id in range(1,9):
        for quality_index,quality in enumerate(qualities):
            rows.append([None,row_id,range_id,quality,compound_generate[range_id],costs[range_id-1][quality_index]])
            row_id+=1
    build_formal_rows("PortableEquipCompound.xlsx","PortableEquipCompound",
        "SpecialEquipment/Portable/PortableEquipCompound.xlsx",rows,"可粘贴：40行完整合成配置",
        "8档×5投入品质；EquipResult按档引用Generate 4401~4408取得等级概率，成品品质概率由PortableCompoundProb读取。RangeId区间已确认，需与PortableRange原子更新。")

    craft_gold=[500,1200,2800,6200,9000,13000,18000,24000]
    assist_qty=[(1,2,3),(2,4,6),(4,6,9),(6,10,15),(8,12,18),(10,15,23),(13,19,29),(16,24,36)]
    material_qualities=["Purple","Orange","Red"]
    craft_rows=[]; craft_id=1
    for tier,levels in enumerate(craft_levels,1):
        for level in levels:
            for part_enum,_,category_index,assist_items in parts:
                for quality_index,_ in enumerate(material_qualities):
                    main_item=1080+(tier-1)*9+category_index*3+quality_index
                    qty=assist_qty[tier-1][quality_index]
                    craft_rows.append([None,craft_id,part_enum,craft_generate[(tier,level,part_enum)],f"{main_item},1",
                                       f"{assist_items[0]},{qty};{assist_items[1]},{qty}",craft_gold[tier-1]])
                    craft_id+=1
    build_formal_rows("PortableEquipCraft.xlsx","PortableEquipCraft","SpecialEquipment/Portable/PortableEquipCraft.xlsx",craft_rows,
        "可粘贴：360行完整打造配置",
        "完整7列表头；8部位×3主材品质×15个历史引用位。相同打造档的EquipResult均指向同一等级概率池；成品品质概率由PortableCraftProb读取。")
    return [
        {"file":"SpecialEquipmentGenerate.xlsx","sheet":"SpecialEquipment","status":"可粘贴：完整正式Schema及等级池","rows":len(generate_rows),"formal":str(CONFIG/"SpecialEquipment/SpecialEquipmentGenerate.xlsx")},
        {"file":"PortableEquipCompound.xlsx","sheet":"PortableEquipCompound","status":"可粘贴：40行完整合成配置","rows":len(rows),"formal":str(CONFIG/"SpecialEquipment/Portable/PortableEquipCompound.xlsx")},
        {"file":"PortableEquipCraft.xlsx","sheet":"PortableEquipCraft","status":"可粘贴：360行完整打造配置","rows":len(craft_rows),"formal":str(CONFIG/"SpecialEquipment/Portable/PortableEquipCraft.xlsx")},
    ]

def build_index(records):
    wb=Workbook(); ws=wb.active; ws.title="配置清单"
    ws.append(["序号","镜像文件","配置页签","状态","数据行数","正式配置路径","说明"])
    for i,r in enumerate(records,1): ws.append([i,r["file"],r["sheet"],r["status"],r["rows"],r["formal"],r.get("note","")])
    ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
    for c in ws[1]: c.font=Font(bold=True,color="FFFFFF"); c.fill=PatternFill("solid",fgColor="17365D")
    widths=[8,38,32,28,12,90,60]
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
    for row in ws.iter_rows():
        for c in row: c.alignment=Alignment(vertical="top",wrap_text=True)
    wb.save(OUT/"00_配置清单.xlsx")

def main_attributes_only():
    """只重建映射装备属性六表，供正式装备模板变化后的原子重基使用。"""
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    before={str(p.relative_to(CONFIG)):sha(p) for p in CONFIG.rglob('*.xlsx') if not p.name.startswith('~$')}
    records=attribute_delivery_records()
    records.extend(equipment_template_records(records))
    build_index(records)
    after={str(p.relative_to(CONFIG)):sha(p) for p in CONFIG.rglob('*.xlsx') if not p.name.startswith('~$')}
    report={"generated_at":datetime.now().astimezone().isoformat(),"mode":"attributes-only","output":str(OUT),"files":len(records)+1,"records":records,"formal_datas_unchanged":before==after}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    before={str(p.relative_to(CONFIG)):sha(p) for p in CONFIG.rglob('*.xlsx') if not p.name.startswith('~$')}
    p02=load_workbook(P02,data_only=False)
    records=[]
    for fn,(sn,ss,status,rel) in SPECS.items():
        rows=build_data_file(p02,fn,sn,ss,status,rel)
        records.append({"file":fn,"sheet":sn,"status":status,"rows":rows,"formal":str(CONFIG/rel) if rel else "待定"})
    for fn,(sn,reason,rel) in BLOCKED.items():
        build_blocked(fn,sn,reason,rel)
        records.append({"file":fn,"sheet":sn,"status":"阻断：不可粘贴","rows":0,"formal":str(CONFIG/rel),"note":reason})
    records.extend(attribute_delivery_records())
    records.extend(equipment_template_records(records))
    records.extend(portable_range_records())
    records.extend(portable_probability_records(p02))
    records.extend(portable_compound_craft_generate_records(p02))
    build_index(records)
    after={str(p.relative_to(CONFIG)):sha(p) for p in CONFIG.rglob('*.xlsx') if not p.name.startswith('~$')}
    report={"generated_at":datetime.now().astimezone().isoformat(),"output":str(OUT),"files":len(records)+1,"records":records,"formal_datas_unchanged":before==after}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    if "--attributes-only" in sys.argv:
        main_attributes_only()
    else:
        main()
