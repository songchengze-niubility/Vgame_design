---
name: vgame-hero-skill-config-map
description: Use for Vgame hero/character definition, skill system configuration, buff system, hero attributes, hero ascension/breakthrough, hero star-up, exclusive weapon config, efficiency/star-map nodes, skill editor workflow, skill action types, buff effects, skill data serialization pipeline, hero-skill-buff cross-table relationships, and any task involving how characters and their abilities are configured from Excel to runtime. Trigger when asked how a hero is defined, how skills are configured, how buffs work, how the skill editor produces runtime data, how hero stats scale, how ascension/star/efficiency systems are configured, or how to add/modify a hero's skill or buff.
---

# Vgame Hero & Skill Config Map

Use this skill to answer: how Vgame heroes are defined and configured, how the skill/buff system works from config to runtime, and how all hero-related systems (ascension, star, efficiency, exclusive weapon) interconnect.

This is a project mapping skill. It is read-only by default.

## Load Order

1. Read `vgame-core-understanding` for project identity and growth layer context.
2. Read `references/hero-config-schema.md` for hero tables, attributes, ascension, star, and cross-table relationships.
3. Read `references/skill-system-architecture.md` for skill config, editor workflow, runtime execution, and action types.
4. Read `references/buff-system-config.md` for buff definition, effects, stacking, and storage.
5. Use `vgame-growth-combat-conversion-map` for how hero growth translates to combat performance.
6. Use `vgame-battle-content-map` for how monster skills/buffs are configured (same system, different owners).
7. Use `vgame-config-schema` for exact Luban schema, export pipeline, and formula safety rules.
8. Use `vgame-battle-tuning-helper` for DPS/TTK calculations involving hero stats.

## Scope

Covered:

- Hero definition (Hero.xlsx): ID, name, quality, class, camp, base stats, skill slots, collision
- Hero attributes (HeroAttribute.xlsx): per-hero per-level stat scaling (ID = HeroId*1000+Lv)
- Hero leveling (HeroLv.xlsx): EXP/gold cost per level
- Hero ascension (HeroAscendLv/Material.xlsx): level cap gates, material costs
- Hero star-up (HeroStarAttrUp.xlsx): shard costs, talent unlocks, stat multipliers
- Efficiency/star-map (HeroEnergyEfficiencyMap/Attr.xlsx): node graph, attribute bonuses
- Calibration points (CalibrationPoints/Attr.xlsx): crafting costs, flat stat gains
- Exclusive weapon (ExclWeapon.xlsx): weapon definition, level/ascend/star costs, linked skills
- Skin system (Skin.xlsx): visual resources per hero
- Skill config (Skill.xlsx): 1356 skills, type enum, SkillData path to editor asset
- Skill editor workflow: node-graph editor → ScriptableObject → MessagePack .bytes
- Skill runtime: SkillInstance → SkillLine → SkillActionClip (63 action types)
- Buff config (BuffDataRaw): cfgId, duration, type, effects, stacks, storage
- Buff effects: 14 types (attribute modify, damage, heal, shield, stun, slow, etc.)
- Buff storage: `BuffData/Runtime/Buff_{id}.bytes`
- Level/target skill (LevelSkill.xlsx, TargetSkill.xlsx): equipment skills, targeting
- Rouge/Tower buffs: roguelike skills, tower trial buffs/debuffs

Not covered:

- Specific skill balance tuning (route to `game-numerical-analysis`)
- Economy/material source tracing (route to `vgame-economy-source-map`)
- Level unlock chains for hero ascension (route to `vgame-level-progression-map`)

## Output Contract

For hero/skill analysis, include:

- `Entity`: hero ID / skill ID / buff ID
- `Config source`: which Excel table and fields (with column positions)
- `Runtime path`: which .bytes file or runtime class loads this data
- `Cross-references`: which other tables reference or are referenced by this config
- `Editor workflow`: if skill/buff, how it's authored (editor → serialize → runtime)
- `Risk`: formula columns, ID conventions, enum dependencies, breaking changes
