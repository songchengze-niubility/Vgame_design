"""Independent, read-only Excel verification for CHG-023."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
FRAMEWORK = HERE.parent.parent
OUT = FRAMEWORK / "06_最终配置/映射装备"
report = json.loads((FRAMEWORK / "05_验算核算/mapping-rare-CHG023.json").read_text(encoding="utf-8"))
backup = Path(report["backup"])
checks = []


def check(name, ok):
    checks.append({"name": name, "result": "PASS" if ok else "FAIL"})


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p, width, sheet=0, data_only=False):
    w = openpyxl.load_workbook(p, read_only=True, data_only=data_only)
    s = w.worksheets[sheet] if isinstance(sheet, int) else w[sheet]
    s.reset_dimensions()
    result = [list(r) for r in s.iter_rows(max_col=width, values_only=True)]
    w.close()
    return result


data = {}
for name, width in [("SpecialEquipment.xlsx", 13), ("SpecialEquipmentEffect.xlsx", 9), ("SpecialEquipmentEffectDrop.xlsx", 3)]:
    before, after = read(backup/name, width), read(OUT/name, width)
    data[name] = (before, after)
    check(f"{name}:headers", before[:4] == after[:4])
    check(f"{name}:uniqueIDs", len({r[1] for r in after[4:]}) == len(after)-4)
    check(f"{name}:noFormulaErrors", not any(isinstance(v, str) and v.startswith(("#REF!", "#DIV/0!", "#VALUE!", "#N/A", "#NAME?")) for r in after for v in r))
    if name != "SpecialEquipment.xlsx":
        check(f"{name}:originalRowsUnchanged", after[:len(before)] == before)
    # Only the recorded metadata cells may change on the existing notes sheet.
    bn, an = read(backup/name, 2, 1), read(OUT/name, 2, 1)
    check(f"{name}:notesScope", all(v == an[r][c] for r,row in enumerate(bn) for c,v in enumerate(row) if (r,c) not in {(2,1),(3,1),(6,1),(8,1)}))

before, after = data["SpecialEquipment.xlsx"]
counts = Counter()
for old, row in zip(before[4:], after[4:]):
    grade, quality = row[3], row[5]
    tier = 1 if grade <= 20 else 2 if grade <= 40 else 3
    expected = 6000 + tier + (3 if quality == "Red" else 0)
    if quality in ("Orange", "Red"):
        check(f"equipment{row[1]}:pool", row[9] == expected)
        check(f"equipment{row[1]}:otherFields", row[:9]+row[10:] == old[:9]+old[10:])
        counts[expected] += 1
    else:
        check(f"equipment{row[1]}:untouchedQuality", row == old)
check("480EquipmentRows", len(after) == len(before) == 484)
check("sixPools32EquipmentEach", dict(counts) == {i:32 for i in range(6001,6007)})
old, after = data["SpecialEquipmentEffect.xlsx"]
effects = {r[1]:r for r in after[4:]}
expected_ids = {b*100+s for b in range(311,323) for s in range(1,7)}
check("72NewEffects", set(effects)-{r[1] for r in old[4:]} == expected_ids)
template = next(r for r in old[4:] if r[1] == 3101)
for effect_id in sorted(expected_ids):
    expected = list(template)
    expected[1] = expected[7] = effect_id
    check(f"effect{effect_id}:singleSkillBinding", effects.get(effect_id) == expected)
old, after = data["SpecialEquipmentEffectDrop.xlsx"]
pools = {r[1]:r[2] for r in after[4:]}
check("sixNewPools", set(pools)-{r[1] for r in old[4:]} == set(range(6001,6007)))
for suffix in range(1,7):
    expected = ";".join(f"{base*100+suffix},100" for base in range(311,323))
    check(f"pool{6000+suffix}:12ExactIDsEqualWeights", pools.get(6000+suffix) == expected)
    check(f"pool{6000+suffix}:effectReferences", all(base*100+suffix in effects for base in range(311,323)))

for filename, before_hash in report["candidateHashes"].items():
    if filename not in report["files"]:
        check(f"unchangedCandidate:{filename}", sha(OUT/filename) == before_hash)
for filename, before_hash in report["formalHashes"].items():
    check(f"unchangedSource:{Path(filename).name}", sha(Path(filename)) == before_hash)

old, new = read(backup/"00_配置清单.xlsx",7), read(OUT/"00_配置清单.xlsx",7)
for i,row in enumerate(old):
    if row[1] in data:
        check(f"index:{row[1]}", new[i][4] == len(data[row[1]][1])-4)
        check(f"indexScope:{row[1]}", all(row[c] == new[i][c] for c in [0,1,2,5]))
    else:
        check(f"indexRow{i+1}:unchanged", row == new[i])
check("CHG019AuditUnchanged", read(backup/"00_配置清单.xlsx",13,1) == read(OUT/"00_配置清单.xlsx",13,1))
audit = read(OUT/"00_配置清单.xlsx",7,"CHG023稀有词条")
check("auditSixCounts", [r[6] for r in audit[3:9]] == [32]*6)

# Replay the shared pure-data generator rules without generating any workbook.
sys.path.insert(0, str(HERE.parent))
from mapping_rare_rules import add_rare_effects, add_rare_pools, rare_pool_id
for filename, fn in [("SpecialEquipmentEffect.xlsx",add_rare_effects),("SpecialEquipmentEffectDrop.xlsx",add_rare_pools)]:
    old, new = data[filename]
    cols = {v:c for c,v in enumerate(old[0])}
    generated = fn([list(r) for r in old[4:]], cols)
    check(f"generatorReplay:{filename}", generated == new[4:])
    check(f"generatorIdempotent:{filename}", fn([list(r) for r in generated],cols) == generated)
for quality, offset in [("Orange",0),("Red",3)]:
    for grade, tier in [(5,1),(20,1),(25,2),(40,2),(45,3),(60,3)]:
        check(f"generatorBoundary:{quality}/{grade}",rare_pool_id(quality,grade) == 6000+offset+tier)

result = {"revision":"CHG-023", "checks":len(checks), "pass":sum(c["result"]=="PASS" for c in checks), "fail":sum(c["result"]=="FAIL" for c in checks), "details":checks}
(FRAMEWORK/"05_验算核算/mapping-rare-CHG023-validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!='details'},ensure_ascii=False))
for c in checks:
    if c["result"] == "FAIL": print(c)
raise SystemExit(1 if result["fail"] else 0)
