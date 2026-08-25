# -*- coding: utf-8 -*-
"""
shared_reader.py — 读取共享参数 MD 的通用函数

所有子模块需要标准人、投放系数时调用这里。
"""
from .md_parameter_reader import load_parameter_workbook, parameter_md_path


SHARED_PARAM = parameter_md_path('共享')


def read_standard():
    """读取标准人属性，返回 dict {'生命': 5000, '攻击': 1500, '防御': 1000}。"""
    wb = load_parameter_workbook(SHARED_PARAM, data_only=True)
    ws = wb['标准人']
    std = {}
    for r in range(2, ws.max_row + 1):
        k = ws.cell(r, 1).value
        v = ws.cell(r, 2).value
        if k and v is not None:
            std[k] = v
    wb.close()
    return std


def read_coefficients():
    """读取投放系数，返回 dict {'角色升级': None, '角色星盘': 2.3, ...}。"""
    wb = load_parameter_workbook(SHARED_PARAM, data_only=True)
    ws = wb['投放系数']
    coef = {}
    for r in range(2, ws.max_row + 1):
        k = ws.cell(r, 1).value
        v = ws.cell(r, 2).value
        t = ws.cell(r, 3).value
        if k:
            coef[k] = {'value': v, 'type': t}
    wb.close()
    return coef


def read_coef_value(name):
    """读取指定模块的投放系数值。"""
    coefs = read_coefficients()
    entry = coefs.get(name, {})
    return entry.get('value') if isinstance(entry, dict) else entry
