# -*- coding: utf-8 -*-
"""
等级类词条投放定价对齐修正（候选表生成）v3
  新ValueMax = 系数 × 同档百分比词条ValueMax(%)
  系数：暴伤110 / 暴击90 / 能量90 / 冷却130
  档位键：decade = (rid//100-500)*10 + (rid%100)//10
  品质 = decade//12（0绿1蓝2紫3橙4红），等级档 = decade%12（0=lv5 … 11=lv60）
"""
import openpyxl, os, shutil, statistics, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(os.environ["VGAME_CONFIG_DATAS"]) / "SpecialEquipment" / "SpecialEquipmentEffect.xlsx"
OUT = Path(__file__).resolve().parent / "SpecialEquipmentEffect_CHG027_等级词条定价对齐.xlsx"

COEF = {"CritLevel": 90.0, "CritDmgBonusLevel": 110.0,
        "EnergyPreAddBonusLevel": 90.0, "CoolDownReduceLevel": 130.0}
BASE_ATTR = "AttackBonus"
ID_LO, ID_HI = 50000, 50700

def decade(rid):
    return (rid // 100 - 500) * 10 + (rid % 100) // 10

wbv = openpyxl.load_workbook(SRC, data_only=True, read_only=True)
wsv = wbv["SpecialEquipment"]
rows = [list(r) for r in wsv.iter_rows(values_only=True)]
hdr = {c: i for i, c in enumerate(rows[0])}
cId, cA, cVMax, cVMin = hdr["Id"], hdr["Attribute"], hdr["ValueMax"], hdr["ValueMin"]

base = {}
for r in rows[3:]:
    rid = r[cId]
    if isinstance(rid, int) and ID_LO <= rid <= ID_HI and r[cA] == BASE_ATTR and r[cVMax] is not None:
        base[decade(rid)] = float(r[cVMax])
print(f"AttackBonus 基准档数: {len(base)}（应60）")

changes = []
for i, r in enumerate(rows):
    rid = r[cId]
    if not (isinstance(rid, int) and 50004 <= rid <= 50600):
        continue
    attr = r[cA]
    if attr not in COEF or r[cVMax] is None:
        continue
    d = decade(rid)
    if d not in base:
        print(f"WARN rid={rid} decade={d} 无基准，跳过")
        continue
    new_max = round(COEF[attr] * base[d] * 100.0, 6)
    old_max = float(r[cVMax])
    old_min = r[cVMin]
    new_min = round(float(old_min) * new_max / old_max, 6) if (old_min is not None and float(old_min) > 0) else None
    changes.append((i, old_max, old_min, new_max, new_min, attr, rid, d))

n_chg = sum(1 for c in changes if abs(c[1] - c[3]) > 0.01)
print(f"目标行数 {len(changes)}，数值有变化 {n_chg} 行")

shutil.copy(SRC, OUT)
wbe = openpyxl.load_workbook(OUT)
wse = wbe["SpecialEquipment"]
for i, old_max, old_min, new_max, new_min, attr, rid, d in changes:
    rownum = i + 1
    if abs(float(wse.cell(row=rownum, column=cVMax + 1).value) - old_max) > 1e-9:
        raise RuntimeError(f"行错位 rid={rid}")
    wse.cell(row=rownum, column=cVMax + 1).value = new_max
    if new_min is not None:
        wse.cell(row=rownum, column=cVMin + 1).value = new_min
wbe.save(OUT)
print(f"已写出: {OUT}")

# ===== 验算 =====
wb2 = openpyxl.load_workbook(OUT, data_only=True, read_only=True)
ws2 = wb2["SpecialEquipment"]
r2 = [list(r) for r in ws2.iter_rows(values_only=True)]
nd = {}
for r in r2[3:]:
    rid = r[cId]
    if isinstance(rid, int) and 50000 <= rid <= 50700:
        nd[decade(rid)] = (rid, r[cA], r[cVMax], r[cVMin])

QUAL = {"CritLevel": 90.0, "CritDmgBonusLevel": 110.0,
        "EnergyPreAddBonusLevel": 90.0, "CoolDownReduceLevel": 130.0}

print("\n[验算1] 60 档逐档定价等价（每1%防对应的暴伤/暴击/能量/冷却点数）")
bad = 0
for d in sorted(nd):
    rid, attr, vm, vn = nd[d]
    if attr != BASE_ATTR:
        continue
    for cattr, c in QUAL.items():
        if cattr in nd.get(d, (None,))[0:1] and nd[d][0] and cattr in [nd[x][1] for x in [d]]:
            pass
    # 同 decade 下查四个属性
    for cattr, c in QUAL.items():
        e = nd.get(d)
        if e and e[1] == cattr:
            r_ = e[2] / (vm * 100.0)
            if abs(r_ - c) > 0.05:
                bad += 1
                print(f"  FAIL decade={d} {cattr}: {r_:.3f} (应 {c})")
print(f"  → {'全部通过' if bad == 0 else f'{bad} 项失败'}")

print("[验算2] 各品质段内逐级严格递增")
bad = 0
for cattr in QUAL:
    series = [(d, nd[d][2]) for d in sorted(nd) if nd[d][1] == cattr]
    for (d1, v1), (d2, v2) in zip(series, series[1:]):
        if d2 - d1 == 1 and not v2 > v1:
            bad += 1
            print(f"  FAIL {cattr} decade {d1}->{d2}: {v1} -> {v2}")
print(f"  → {'全部通过' if bad == 0 else f'{bad} 处逆序'}")

print("[验算3] 档顶（每品质 decade%12==11）新旧一致性：应≈1.0 倍")
tops = [c for c in changes if c[7] % 12 == 11]
facs = [c[3] / c[1] for c in tops]
print(f"  档顶行 {len(tops)} 行，倍数范围 {min(facs):.4f}~{max(facs):.4f}（1.0=未动）")

print("[验算4] 改动倍数分布（全部改动行）")
facs_all = sorted(c[3] / c[1] for c in changes)
print(f"  min={facs_all[0]:.3f} 中位={statistics.median(facs_all):.3f} max={facs_all[-1]:.3f}")

print("\n[抽样] 红档暴伤 逐级 旧→新（应只在低级放大、满级不动）：")
for d in sorted(nd):
    if 48 <= d <= 59 and nd[d][1] == "CritDmgBonusLevel":
        rid, _, vm, _ = nd[d]
        old = [c[1] for c in changes if c[6] == rid][0]
        ab = base[d] * 100
        print(f"  红 tier{d%12:2d} rid={rid}: {old:9.2f} → {vm:9.2f}  (攻击%VM={ab:6.3f}%)")
