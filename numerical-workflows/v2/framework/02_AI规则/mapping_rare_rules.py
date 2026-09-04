"""CHG-023 pure data rules shared with the existing mirror generator; no file writes."""
import json
from pathlib import Path

RULES = json.loads((Path(__file__).parent / "mapping-rare-chg023/rules.json").read_text(encoding="utf-8"))
EFFECT_IDS = {c["base"] + t["suffix"] for c in RULES["categories"] for t in RULES["tiers"]}
POOL_IDS = {t["poolId"] for t in RULES["tiers"]}


def rare_pool_id(quality, grade):
    if quality not in ("Orange", "Red"):
        return None
    matches = [t for t in RULES["tiers"] if t["quality"] == quality and t["min"] <= grade <= t["max"]]
    if len(matches) != 1 or grade % 5:
        raise ValueError(f"CHG-023 未登记金红装备等级: {quality}/{grade}")
    return matches[0]["poolId"]


def add_rare_effects(rows, cols):
    existing = {r[cols["Id"]]: r for r in rows}
    template = existing[RULES["effectTemplateId"]]
    for effect_id in sorted(EFFECT_IDS):
        row = list(template)
        row[cols["Id"]] = effect_id
        row[cols["SkillList"]] = effect_id
        if effect_id in existing:
            if existing[effect_id] != row:
                raise ValueError(f"CHG-023 EffectId冲突: {effect_id}")
        else:
            rows.append(row)
    return rows


def add_rare_pools(rows, cols):
    existing = {r[cols["Id"]]: r for r in rows}
    for tier in RULES["tiers"]:
        row = [None] * len(rows[0])
        row[cols["Id"]] = tier["poolId"]
        row[cols["EffectList"]] = ";".join(f"{c['base'] + tier['suffix']},{RULES['weight']}" for c in RULES["categories"])
        if tier["poolId"] in existing:
            if existing[tier["poolId"]] != row:
                raise ValueError(f"CHG-023 PoolId冲突: {tier['poolId']}")
        else:
            rows.append(row)
    return rows
