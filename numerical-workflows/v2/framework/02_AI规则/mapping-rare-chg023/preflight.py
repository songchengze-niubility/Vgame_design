"""Read-only source/candidate checks and analysis JSON; never authors Excel."""
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
FRAMEWORK = HERE.parent.parent
OUT = FRAMEWORK / "06_最终配置/映射装备"
CONFIG = Path(os.environ["VGAME_CONFIG_DATAS"])
SOURCE = Path(sys.argv[1])
rules = json.loads((HERE / "rules.json").read_text(encoding="utf-8"))
ids = {c["base"] + t["suffix"] for c in rules["categories"] for t in rules["tiers"]}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p, width, sheet=None, data_only=False):
    w = openpyxl.load_workbook(p, read_only=True, data_only=data_only)
    s = w[sheet] if sheet else w.worksheets[0]
    s.reset_dimensions()
    result = [list(r) for r in s.iter_rows(max_col=width, values_only=True)]
    w.close()
    return result


source_rows = rows(SOURCE, 9, "映射装备包装、技能")
source = {r[0]: r[1] for r in source_rows[19:91]}
assert set(source) == ids
formal_skills = rows(CONFIG / "Skill/Skill.xlsx", 14, data_only=True)
skill_rows = {r[1]: r for r in formal_skills[4:] if r[0] != "##" and r[1] in ids}
assert set(skill_rows) == ids, ids - set(skill_rows)
for c in rules["categories"]:
    for t in rules["tiers"]:
        skill = c["base"] + t["suffix"]
        percent = f"{t['bonus']:.0%}"
        assert percent in source[skill]
        assert skill_rows[skill][5] == f"{c['name']};{percent}"
        assert skill_rows[skill][9] == "SkillsSpecialEquipment"

files = {"SpecialEquipment.xlsx": 13, "SpecialEquipmentEffect.xlsx": 9, "SpecialEquipmentEffectDrop.xlsx": 3}
data = {name: rows(OUT / name, width) for name, width in files.items()}
equipment = data["SpecialEquipment.xlsx"]
head = equipment[0]
count = Counter()
for r in equipment[4:]:
    if r[head.index("Quality")] not in ("Orange", "Red"):
        continue
    q, g = r[head.index("Quality")], r[head.index("Grade")]
    ts = [t for t in rules["tiers"] if t["quality"] == q and t["min"] <= g <= t["max"]]
    assert len(ts) == 1
    assert not (isinstance(r[head.index("RareEffect")], str) and r[head.index("RareEffect")].startswith("="))
    count[ts[0]["name"]] += 1
assert dict(count) == {t["name"]: 32 for t in rules["tiers"]}
for name, wanted in [("SpecialEquipmentEffect.xlsx", ids), ("SpecialEquipmentEffectDrop.xlsx", {t["poolId"] for t in rules["tiers"]})]:
    for p in [OUT/name, CONFIG/"SpecialEquipment"/name]:
        rs = rows(p, files[name])
        assert not wanted.intersection(r[1] for r in rs[4:]), f"ID collision: {p}"

tracked = [CONFIG/"SpecialEquipment"/n for n in files] + [CONFIG/"Skill/Skill.xlsx", SOURCE]
result = {
    "source": str(SOURCE), "sourceSkills": source, "skillCount": len(ids), "tierCounts": dict(count),
    "formalHashes": {str(p): sha(p) for p in tracked},
    "candidateHashes": {p.name: sha(p) for p in OUT.glob("*.xlsx")},
    "before": data,
}
(HERE / "preflight.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"skillCount": len(ids), "tierCounts": dict(count), "collisions": 0}, ensure_ascii=False))
