"""CHG-025: named red skills use SpecialEffect -> one-entry EffectDrop pools."""
import json
from pathlib import Path

RULES = json.loads((Path(__file__).parent / "mapping-named-chg024/rules.json").read_text(encoding="utf-8"))
EFFECT_IDS = set(RULES["skills"].values())
POOL_IDS = set(EFFECT_IDS)


def named_effect_id(quality, name):
    if quality != RULES["quality"]:
        return None
    return RULES["skills"].get(RULES["aliases"].get(name, name))


def add_named_effects(rows, cols):
    existing = {r[cols["Id"]]: r for r in rows}
    template = existing[RULES["effectTemplateId"]]
    for effect_id in sorted(EFFECT_IDS):
        row = list(template)
        row[cols["Id"]] = effect_id
        row[cols["SkillList"]] = effect_id
        if effect_id in existing:
            if existing[effect_id] != row:
                raise ValueError(f"CHG-024 EffectId冲突: {effect_id}")
        else:
            rows.append(row)
    return rows


def add_named_pools(rows, cols):
    existing = {r[cols["Id"]]: r for r in rows}
    for pool_id in sorted(POOL_IDS):
        row = [None] * len(rows[0])
        row[cols["Id"]] = pool_id
        row[cols["EffectList"]] = f"{pool_id},100"
        if pool_id in existing:
            if existing[pool_id] != row:
                raise ValueError(f"CHG-025 named PoolId冲突: {pool_id}")
        else:
            rows.append(row)
    return rows
