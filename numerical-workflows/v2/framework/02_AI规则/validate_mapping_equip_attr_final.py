#!/usr/bin/env python3
"""只读校验映射装备属性最终配置镜像，不检查掉落、解锁等非属性表。"""
from __future__ import annotations

import json
import os
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(os.environ.get("VGAME_NUMERICAL_RUNTIME_ROOT", str(Path(__file__).resolve().parents[1])))
OUT = Path(os.environ.get("MAPPING_EQUIP_FINAL_OUT", str(ROOT / "06_最终配置" / "映射装备")))
CONFIG = Path(os.environ.get("VGAME_CONFIG_DATAS", ""))
REPORT = ROOT / "05_验算核算" / "mapping-equip-attr-final-validation.json"

FILES = {
    "SpecialEquipment.xlsx": ("SpecialEquipment", "SpecialEquipment/SpecialEquipment.xlsx"),
    "SpecialEquipmentMain.xlsx": ("SpecialEquipment", "SpecialEquipment/SpecialEquipmentMain.xlsx"),
    "SpecialEquipmentEffect.xlsx": ("SpecialEquipment", "SpecialEquipment/SpecialEquipmentEffect.xlsx"),
    "SpecialEquipmentEffectDrop.xlsx": ("SpecialEquipment", "SpecialEquipment/SpecialEquipmentEffectDrop.xlsx"),
    "SpecialEquipmentQuality.xlsx": ("SpecialEquipment", "SpecialEquipment/SpecialEquipmentQuality.xlsx"),
    "SpecialEquipmentSubAttrCoef.xlsx": ("SpecialEquipmentSubAttrCoef", "SpecialEquipment/SpecialEquipmentSubAttrCoef.xlsx"),
}
MAIN_TARGET = {
    "SEPart_Weapon": ("Attack", 11250),
    "SEPart_Head": ("Hp", 18750),
    "SEPart_Armour": ("Hp", 18750),
    "SEPart_Glove": ("Armor", 2500),
    "SEPart_Belt": ("Armor", 2500),
    "SEPart_Shoe": ("Armor", 2500),
    "SEPart_Device": ("CritDmgBonusLevel", 8800),
    "SEPart_Decoration": ("CritLevel", 7200),
}
SUB_RANGE = {
    "AttackBonus": (.329, .0987, .001),
    "ArmorBonus": (.329, .0987, .001),
    "HpBonus": (.329, .0987, .001),
    "Attack": (3701, 1110, 1),
    "Armor": (2468, 740, 1),
    "Hp": (12338, 3701, 1),
    "CritLevel": (2961, 888, 1),
    "CritDmgBonusLevel": (3619, 1086, 1),
    "EnergyPreAddBonusLevel": (2961, 888, 1),
    "CoolDownReduceLevel": (4277, 1283, 1),
}
ORDINARY_EFFECT_IDS = {offset + slot for offset in (0, 100, 200, 300) for slot in range(1, 13)}
QUALITY = {
    "Green": (2, 2, .20, .50),
    "Blue": (2, 3, .30, .60),
    "Purple": (4, 4, .45, .70),
    "Orange": (4, 4, .70, .85),
    "Red": (4, 4, 1.00, 1.00),
}
SUB_LEVEL = {5: .400, 10: .455, 15: .509, 20: .564, 25: .618, 30: .673, 35: .727, 40: .782, 45: .836, 50: .891, 55: .945, 60: 1.000}


def headers(ws):
    return {value: index for index, value in enumerate(next(ws.iter_rows(min_row=1, max_row=1, values_only=True))) if value is not None}


def rows(ws, id_field="Id"):
    cols = headers(ws)
    return cols, [row for row in ws.iter_rows(min_row=5, values_only=True) if row[cols[id_field]] is not None]


def schema(ws):
    # 个别正式表存在远端空格式导致 max_column 异常膨胀；Schema 实际均在前100列内。
    width = max(c for c in range(1, min(ws.max_column, 100) + 1) if any(ws.cell(r, c).value is not None for r in range(1, 5)))
    return [[ws.cell(r, c).value for c in range(1, width + 1)] for r in range(1, 5)]


def main():
    checks = []

    def check(name, ok, actual=None, expected=True):
        checks.append({"name": name, "result": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})

    opened = {}
    for file_name, (sheet_name, formal_rel) in FILES.items():
        path = OUT / file_name
        check(f"存在:{file_name}", path.exists(), path.exists(), True)
        if not path.exists():
            continue
        wb = load_workbook(path, data_only=False, read_only=True)
        formal_wb = load_workbook(CONFIG / formal_rel, data_only=False, read_only=True)
        ws, formal_ws = wb[sheet_name], formal_wb[sheet_name]
        check(f"正式Schema:{file_name}", schema(ws) == schema(formal_ws), schema(ws), schema(formal_ws))
        formulas = errors = 0
        for row in ws.iter_rows(values_only=True):
            for value in row:
                formulas += isinstance(value, str) and value.startswith("=")
                errors += isinstance(value, str) and value.startswith(("#REF!", "#DIV/0!", "#VALUE!", "#N/A", "#NAME?"))
        check(f"公式与错误值:{file_name}", formulas == 0 and errors == 0, {"formulas": formulas, "errors": errors}, {"formulas": 0, "errors": 0})
        opened[file_name] = (wb, ws, formal_wb, formal_ws)

    if len(opened) != len(FILES):
        result = {"status": "FAIL", "checks": len(checks), "pass": sum(c["result"] == "PASS" for c in checks), "fail": sum(c["result"] == "FAIL" for c in checks), "details": checks}
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("status", "checks", "pass", "fail")}, ensure_ascii=False))
        raise SystemExit(1)

    _, equip_ws, _, formal_equip_ws = opened["SpecialEquipment.xlsx"]
    ec, equips = rows(equip_ws); fec, formal_equips_rows = rows(formal_equip_ws)
    formal_equips = {row[fec["Id"]]: row for row in formal_equips_rows}
    preserve = [field for field in fec if field != "Attribute2List"]
    equip_errors = []
    for row in equips:
        equip_id = row[ec["Id"]]; formal = formal_equips.get(equip_id)
        if formal is None or row[ec["Attribute2List"]] is not None or any(row[ec[field]] != formal[fec[field]] for field in preserve):
            equip_errors.append(equip_id)
    check("190件装备仅清空主属性2", len(equips) == 190 and not equip_errors, {"rows": len(equips), "errors": equip_errors}, {"rows": 190, "errors": []})

    _, main_ws, _, _ = opened["SpecialEquipmentMain.xlsx"]
    mc, main_rows = rows(main_ws); main_by_id = {row[mc["Id"]]: row for row in main_rows}
    main_errors = []; lv5_errors = []; lv60_errors = []
    for equip in equips:
        main_id = int(str(equip[ec["Attribute1List"]]).split(",")[0]); row = main_by_id.get(main_id)
        attr, target = MAIN_TARGET[equip[ec["Part"]]]
        if row is None or row[mc["Attribute"]] != attr:
            main_errors.append((equip[ec["Id"]], main_id, None if row is None else row[mc["Attribute"]], attr)); continue
        value, grow, param = row[mc["Value"]], row[mc["Grow"]], row[mc["Param"]]
        lv5_errors.append(abs(value * grow + param - target * .05))
        lv60_errors.append(abs(value * grow ** 12 + param - target))
    check("190条独立Main及部位映射", len(main_rows) == 190 and not main_errors, {"rows": len(main_rows), "errors": main_errors}, {"rows": 190, "errors": []})
    check("主属性Lv5与Lv60锚点", max(lv5_errors, default=999) < 1e-5 and max(lv60_errors, default=999) < 1e-5, {"lv5_max_error": max(lv5_errors, default=None), "lv60_max_error": max(lv60_errors, default=None)}, "均<1e-5")

    _, effect_ws, _, _ = opened["SpecialEquipmentEffect.xlsx"]
    fc, effect_rows = rows(effect_ws); effect_by_id = {row[fc["Id"]]: row for row in effect_rows}
    effect_errors = []
    for effect_id in sorted(ORDINARY_EFFECT_IDS):
        row = effect_by_id.get(effect_id)
        if row is None:
            effect_errors.append((effect_id, "missing")); continue
        attr = row[fc["Attribute"]]; actual = (row[fc["ValueMax"]], row[fc["ValueMin"]], row[fc["RandomMin"]]); expected = SUB_RANGE.get(attr)
        if expected is None or any(abs(float(a) - float(e)) > 1e-9 for a, e in zip(actual, expected)) or not actual[1] < actual[0]:
            effect_errors.append((effect_id, attr, actual, expected))
    check("48条普通副属性保持随机并使用新范围", not effect_errors, effect_errors, [])

    _, pool_ws, _, _ = opened["SpecialEquipmentEffectDrop.xlsx"]
    pc, pool_rows = rows(pool_ws); pools = {row[pc["Id"]]: row[pc["EffectList"]] for row in pool_rows}
    active_pools = {row[ec["Effect"]] for row in equips}; pool_errors = []
    for pool_id in sorted(active_pools):
        ids = [int(token.split(",")[0]) for token in str(pools.get(pool_id, "")).split(";") if token]
        attrs = [effect_by_id[i][fc["Attribute"]] for i in ids if i in effect_by_id and effect_by_id[i][fc["Attribute"]] is not None]
        if not ids or any(attr not in SUB_RANGE for attr in attrs) or len(attrs) != len(set(attrs)):
            pool_errors.append((pool_id, ids, attrs))
    check("在用副属性池闭环且语义不重复", not pool_errors, pool_errors, [])
    generic_attrs = {pool_id: {effect_by_id[int(token.split(",")[0])][fc["Attribute"]] for token in str(pools[pool_id]).split(";") if token} for pool_id in (101, 201, 301)}
    check("通用品质池各10类且无物理魔法伤害", all(value == set(SUB_RANGE) for value in generic_attrs.values()), {k: sorted(v) for k, v in generic_attrs.items()}, sorted(SUB_RANGE))
    red_pools = {row[ec["Effect"]] for row in equips if row[ec["Quality"]] == "Red"}
    red_errors = []
    for pool_id in sorted(red_pools):
        ids = [int(token.split(",")[0]) for token in str(pools.get(pool_id, "")).split(";") if token]
        attrs = [effect_by_id[i][fc["Attribute"]] for i in ids if i in effect_by_id]
        if len(ids) != 10 or set(attrs) != set(SUB_RANGE) or any(attr is None for attr in attrs):
            red_errors.append((pool_id, ids, attrs))
    check("37个红装池取消专属效果并从十类随机4条", len(red_pools) == 37 and not red_errors, {"pool_count": len(red_pools), "errors": red_errors}, {"pool_count": 37, "errors": []})

    _, quality_ws, _, _ = opened["SpecialEquipmentQuality.xlsx"]
    qc, quality_rows = rows(quality_ws)
    quality_actual = {row[qc["Quality"]]: (row[qc["EffectNumMin"]], row[qc["EffectNumMax"]], row[qc["GradeCoefficient"]], row[qc["QualityCoefficient"]]) for row in quality_rows}
    check("五品质系数与副属性条数", quality_actual == QUALITY, quality_actual, QUALITY)

    _, sub_ws, _, _ = opened["SpecialEquipmentSubAttrCoef.xlsx"]
    sc, sub_rows = rows(sub_ws)
    sub_actual = {row[sc["EquipLv"]]: row[sc["SubAttrCoef"]] for row in sub_rows}
    check("副属性12档等级倍率", sub_actual == SUB_LEVEL, sub_actual, SUB_LEVEL)

    for wb, _, formal_wb, _ in opened.values():
        wb.close(); formal_wb.close()
    failed = [item for item in checks if item["result"] == "FAIL"]
    result = {"status": "PASS" if not failed else "FAIL", "checks": len(checks), "pass": len(checks) - len(failed), "fail": len(failed), "output": str(OUT), "details": checks}
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "checks", "pass", "fail")}, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
