#!/usr/bin/env python3
"""生成旅券副本的 UIlevel 奖励展示镜像；只写 06_最终配置。"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT=Path(os.environ.get("VGAME_NUMERICAL_RUNTIME_ROOT", str(Path(__file__).resolve().parents[1])))
CONFIG=Path(os.environ.get("VGAME_CONFIG_DATAS", ""))
OUT=Path(os.environ.get("TRAVEL_DUNGEON_FINAL_OUT",str(ROOT/"06_最终配置"/"旅券副本")))
REPORT=ROOT/"05_验算核算"/"travel-dungeon-uilevel-display-F01.json"
TYPES={"LevelType_Strategy_First","LevelType_Strategy_Second","LevelType_Strategy_Three","LevelType_Strategy_Four"}

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def copy_cell(src,dst):
    dst.value=src.value
    if src.has_style: dst._style=copy(src._style)
    dst.number_format=src.number_format
    dst.alignment=copy(src.alignment)

def find_col(ws,field):
    for c in range(1,ws.max_column+1):
        if ws.cell(1,c).value==field: return c
    raise KeyError(f"{ws.title}: missing {field}")

def normalize_preview(value, valid_item_ids, context):
    if value in (None, ""):
        return value
    parts=[]
    for part in str(value).split(";"):
        if not part:
            continue
        try:
            item_id,quantity=(int(x) for x in part.split(","))
        except ValueError as exc:
            raise ValueError(f"{context}: invalid PropType {part!r}") from exc
        if item_id not in valid_item_ids:
            raise ValueError(f"{context}: ItemId={item_id} does not exist in formal Items.xlsx")
        parts.append(f"{item_id},{-1 if quantity < 0 else quantity}")
    return ";".join(parts)

def schema_width(ws):
    return max(c for c in range(1,ws.max_column+1) if any(ws.cell(r,c).value is not None for r in range(1,5)))

def write_note(wb,rows):
    ws=wb.create_sheet("中文说明")
    data=[
        ("配置镜像文件","UIlevel.xlsx"),
        ("交付批次","TRAVEL-20260724-F01"),
        ("落表状态","可粘贴：40行旅券副本 Reward / FirstReward 展示已核对"),
        ("正式配置位置",str(CONFIG/"level/UIlevel.xlsx")),
        ("数据来源","正式 UIlevel 的 4 个旅券副本 LevelType；真实 Drop 引用保持不变"),
        ("有效数据行",rows),
        ("配置规则","游戏展示读取 FirstReward（首通）和 Reward（普通）。本包保留正式 DropId 字段原值，并核对两项预览的 ItemId 与数量显示规则。"),
        ("使用方式","确认后，按 LevelId 定位正式 UIlevel 同行，仅粘贴 Reward 与 FirstReward 两列；不得整表覆盖正式文件。"),
    ]
    ws.append(["项目","内容"])
    for row in data: ws.append(row)
    ws.freeze_panes="A2"; ws.column_dimensions["A"].width=30; ws.column_dimensions["B"].width=110
    for cell in ws[1]: cell.font=Font(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="17365D")
    for row in ws.iter_rows():
        for cell in row: cell.alignment=Alignment(vertical="top",wrap_text=True)

def write_index(records):
    wb=Workbook(); ws=wb.active; ws.title="配置清单"
    ws.append(["序号","镜像文件","配置页签","状态","数据行数","正式配置路径","说明"])
    for i,record in enumerate(records,1): ws.append([i,*record])
    ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
    for cell in ws[1]: cell.font=Font(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="17365D")
    for col,width in enumerate([8,32,18,42,12,80,80],1): ws.column_dimensions[get_column_letter(col)].width=width
    for row in ws.iter_rows():
        for cell in row: cell.alignment=Alignment(vertical="top",wrap_text=True)
    wb.save(OUT/"00_配置清单.xlsx")

def main():
    before={str(p.relative_to(CONFIG)):sha(p) for p in CONFIG.rglob("*.xlsx") if not p.name.startswith("~$")}
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    source=CONFIG/"level/UIlevel.xlsx"
    fw=load_workbook(source,data_only=False); fs=fw["level"]
    cols={field:find_col(fs,field) for field in ("LevelId","LevelType","LevelFPDrop","LevelPPDrop","Reward","FirstReward","FirstRewardDrop","FallRewardDrop")}
    selected=[r for r in range(5,fs.max_row+1) if fs.cell(r,cols["LevelType"]).value in TYPES]
    if len(selected)!=40: raise ValueError(f"expected 40 travel dungeon levels, got {len(selected)}")
    if any(fs.cell(r,cols["FirstRewardDrop"]).value is None or fs.cell(r,cols["FallRewardDrop"]).value is None for r in selected):
        raise ValueError("travel dungeon has missing real drop references")
    iw=load_workbook(CONFIG/"items/Items.xlsx",read_only=False,data_only=True); isheet=iw["items"]
    item_id_col=find_col(isheet,"Id")
    formal_item_ids={cell.value for (row,col),cell in isheet._cells.items()
                     if row>=5 and col==item_id_col and isinstance(cell.value,int)}
    iw.close()

    wb=Workbook(); ws=wb.active; ws.title="level"
    width=schema_width(fs)
    for r in range(1,5):
        for c in range(1,width+1): copy_cell(fs.cell(r,c),ws.cell(r,c))
    for out_row,source_row in enumerate(selected,5):
        for c in range(1,width+1): copy_cell(fs.cell(source_row,c),ws.cell(out_row,c))
        level_id=fs.cell(source_row,cols["LevelId"]).value
        for field in ("Reward","FirstReward"):
            ws.cell(out_row,cols[field]).value=normalize_preview(fs.cell(source_row,cols[field]).value,formal_item_ids,f"UIlevel[{level_id}].{field}")
    ws.freeze_panes="A5"; ws.auto_filter.ref=f"A4:{get_column_letter(width)}{4+len(selected)}"
    for c in range(1,width+1): ws.column_dimensions[get_column_letter(c)].width=max(12,min(28,len(str(ws.cell(4,c).value or ""))+4))
    write_note(wb,len(selected)); wb._sheets=[ws,wb["中文说明"]]
    wb.save(OUT/"UIlevel.xlsx"); fw.close()
    records=[("UIlevel.xlsx","level","可粘贴：40行 Reward / FirstReward 展示已核对",len(selected),str(source),"仅交付奖励预览字段；真实Drop与DropId不变")]
    write_index(records)
    after={str(p.relative_to(CONFIG)):sha(p) for p in CONFIG.rglob("*.xlsx") if not p.name.startswith("~$")}
    report={"generated_at":datetime.now().astimezone().isoformat(),"output":str(OUT),"files":2,"records":records,"formal_datas_unchanged":before==after}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
