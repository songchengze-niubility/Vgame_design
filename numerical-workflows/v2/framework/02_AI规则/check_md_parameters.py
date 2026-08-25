# -*- coding: utf-8 -*-
"""校验五域 MD 参数块可解析、结构完整且能被生成器加载。"""

from __future__ import annotations

import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
V2_DIR = os.path.dirname(HERE)
sys.path.insert(0, V2_DIR)

from _shared.md_parameter_reader import load_parameter_workbook, read_parameter_payload


SCOPES = ("共享", "养成", "战斗", "经济", "节奏")


def validate_scope(scope: str) -> tuple[int, int, int]:
    payload = read_parameter_payload(scope)
    if payload.get("scope") != scope:
        raise ValueError("%s 参数域标记不一致: %s" % (scope, payload.get("scope")))
    sheets = payload.get("sheets")
    if not isinstance(sheets, list) or not sheets:
        raise ValueError("%s 没有参数页" % scope)
    names = [sheet.get("name") for sheet in sheets]
    if len(names) != len(set(names)) or any(not name for name in names):
        raise ValueError("%s 存在空页名或重复页名" % scope)

    nonempty = formulas = 0
    for sheet in sheets:
        rows = sheet.get("rows")
        if not isinstance(rows, list):
            raise ValueError("%s/%s rows 不是数组" % (scope, sheet["name"]))
        for row in rows:
            if not isinstance(row, list):
                raise ValueError("%s/%s 存在非数组行" % (scope, sheet["name"]))
            for value in row:
                if value is not None:
                    nonempty += 1
                if isinstance(value, dict) and "formula" in value:
                    if "value" not in value or not str(value["formula"]).startswith("="):
                        raise ValueError("%s/%s 存在无确定值或无效公式记录" % (scope, sheet["name"]))
                    formulas += 1

    formula_wb = load_parameter_workbook(scope, data_only=False)
    value_wb = load_parameter_workbook(scope, data_only=True)
    if formula_wb.sheetnames != names or value_wb.sheetnames != names:
        raise ValueError("%s 内存工作簿页签与 MD 不一致" % scope)
    formula_wb.close()
    value_wb.close()
    return len(sheets), nonempty, formulas


def main() -> int:
    total_sheets = total_cells = total_formulas = 0
    for scope in SCOPES:
        sheets, cells, formulas = validate_scope(scope)
        total_sheets += sheets
        total_cells += cells
        total_formulas += formulas
        print("[%s] OK sheets=%d nonempty=%d formulas=%d" % (scope, sheets, cells, formulas))
    print("[OK] scopes=5 sheets=%d nonempty=%d formulas=%d" % (
        total_sheets, total_cells, total_formulas
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
