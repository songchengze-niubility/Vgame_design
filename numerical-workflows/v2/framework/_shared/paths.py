# -*- coding: utf-8 -*-
"""
paths.py — 框架v2 路径常量（各子模块 import 此文件获取路径）

用法: 在子目录脚本里:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from _shared.paths import *
"""
import os

from .md_parameter_reader import parameter_md_path

# 框架v2 根目录
V2_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数值文档根目录（框架v2 的上级）
NUM_DIR = os.path.dirname(V2_ROOT)

# 共享参数 MD
SHARED_DIR = os.path.join(V2_ROOT, '_shared')
SHARED_PARAM = parameter_md_path('共享')

# 4大类目录
GROWTH_DIR = os.path.join(V2_ROOT, '养成')
COMBAT_DIR = os.path.join(V2_ROOT, '战斗')
ECONOMY_DIR = os.path.join(V2_ROOT, '经济')
PACE_DIR = os.path.join(V2_ROOT, '节奏')

# 各类参数 MD
GROWTH_PARAM = parameter_md_path('养成')
COMBAT_PARAM = parameter_md_path('战斗')
ECONOMY_PARAM = parameter_md_path('经济')
PACE_PARAM = parameter_md_path('节奏')

# 源表（旧5表，只读对照用）
SRC_GROWTH = os.path.join(NUM_DIR, 'Vgame养成数值.xlsx')
SRC_COMBAT = os.path.join(NUM_DIR, 'Vgame基本战斗框架.xlsx')
SRC_ECONOMY = os.path.join(NUM_DIR, 'Vgame经济框架.xlsx')
SRC_PACE = os.path.join(NUM_DIR, 'Vgame新手引导以及开启节奏.xlsx')

# 汇总
SUMMARY = os.path.join(V2_ROOT, '汇总总览.xlsx')
