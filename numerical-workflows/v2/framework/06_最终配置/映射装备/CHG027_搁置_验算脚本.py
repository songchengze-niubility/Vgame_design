# -*- coding: utf-8 -*-
"""对候选表做独立完整验算（decade -> {attr: (rid, vm, vn)}）"""
import openpyxl, os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(__file__).resolve().parent / "SpecialEquipmentEffect_CHG027_等级词条定价对齐.xlsx"
SRC = Path(os.environ["VGAME_CONFIG_DATAS"]) / "SpecialEquipment" / "SpecialEquipmentEffect.xlsx"
COEF = {"CritLevel": 90.0, "CritDmgBonusLevel": 110.0,
        "EnergyPreAddBonusLevel": 90.0, "CoolDownReduceLevel": 130.0}
BASE = "AttackBonus"

def decade(rid):
    return (rid // 100 - 500) * 10 + (rid % 100) // 10

def load(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb["SpecialEquipment"]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    hdr = {c: i for i, c in enumerate(rows[0])}
    d = {}
    for r in rows[3:]:
        rid = r[hdr["Id"]]
        if isinstance(rid, int) and 50000 <= rid <= 50700 and r[hdr["ValueMax"]] is not None:
            d.setdefault(decade(rid), {})[r[hdr["Attribute"]]] = (rid, float(r[hdr["ValueMax"]]))
    return d

new = load(OUT)
old = load(SRC)

# 验算1：逐档等价
bad1 = []
for d in sorted(new):
    if BASE not in new[d]:
        continue
    ref = new[d][BASE][1] * 100.0  # 该档%词条满roll（%值）
    for attr, c in COEF.items():
        if attr in new[d]:
            r_ = new[d][attr][1] / ref
            if abs(r_ - c) > 0.05:
                bad1.append((d, attr, r_, c))
print(f"[验算1] 60档×4属性逐档定价等价: {'240/240 全部通过' if not bad1 else bad1}")

# 验算2：品质段内单调递增
bad2 = []
for attr in COEF:
    series = [(d, new[d][attr][1]) for d in sorted(new) if attr in new[d]]
    for (d1, v1), (d2, v2) in zip(series, series[1:]):
        if d2 - d1 == 1 and not v2 > v1:
            bad2.append((attr, d1, v1, d2, v2))
print(f"[验算2] 段内逐级递增: {'全部通过' if not bad2 else bad2}")

# 验算3：档顶未动（每品质 decade%12==11）
bad3 = []
n_top = 0
for d in sorted(new):
    if d % 12 != 11:
        continue
    for attr in COEF:
        if attr in new[d] and attr in old.get(d, {}):
            n_top += 1
            if abs(new[d][attr][1] - old[d][attr][1]) > 0.01:
                bad3.append((d, attr, old[d][attr][1], new[d][attr][1]))
print(f"[验算3] 档顶锚点（{n_top} 行）: {'全部未动 ✓' if not bad3 else bad3}")

# 验算4：改动统计
diffs = []
for d in sorted(new):
    for attr in COEF:
        if attr in new[d] and attr in old.get(d, {}):
            o, n = old[d][attr][1], new[d][attr][1]
            if abs(n - o) > 0.01:
                diffs.append((d, attr, o, n, n / o))
import statistics
f = sorted(x[4] for x in diffs)
print(f"[验算4] 改动 {len(diffs)} 行（240 目标行）倍数: min={f[0]:.3f} 中位={statistics.median(f):.3f} max={f[-1]:.3f}")

print("\n[抽样] 红档（品质4，decade48~59）暴伤等级 旧→新：")
for d in range(48, 60):
    o_c = old[d].get("CritDmgBonusLevel")
    n_c = new[d].get("CritDmgBonusLevel")
    ab = new[d][BASE][1] * 100
    if o_c and n_c:
        print(f"  红 tier{d%12:2d}: {o_c[1]:9.2f} → {n_c[1]:9.2f}  (攻击%VM={ab:6.3f}%, 定价应=110×{ab:.3f}={110*ab:7.1f})")

print("\n[抽样] 蓝档（品质1，decade12~23）暴伤等级 旧→新：")
for d in range(12, 24):
    o_c = old[d].get("CritDmgBonusLevel")
    n_c = new[d].get("CritDmgBonusLevel")
    ab = new[d][BASE][1] * 100
    if o_c and n_c:
        print(f"  蓝 tier{d%12:2d}: {o_c[1]:9.2f} → {n_c[1]:9.2f}  (攻击%VM={ab:6.3f}%)")
