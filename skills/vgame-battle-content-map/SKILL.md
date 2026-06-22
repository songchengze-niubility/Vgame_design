---
name: vgame-battle-content-map
description: Use for Vgame battle content configuration mapping across monsters, bosses, skills, buffs, AI behavior trees, level wave spawns, elite/boss mechanics, combat events, bullet patterns, damage effects, summons, environmental hazards, and battle feedback configuration. Trigger when asked which tables control monster stats, how a boss is configured, where skill/buff data lives, how waves are spawned in a level, what AI drives enemy behavior, how damage formulas reference config, or how battle content is authored from Excel to runtime.
---

# Vgame Battle Content Map

Use this skill to answer: how Vgame's battle content is configured, which source tables define monsters/bosses/skills/buffs/AI/waves, and how the content authoring pipeline flows from Excel to combat runtime.

This is a project mapping skill. It is read-only by default and does not edit config tables.

## Load Order

1. Read `vgame-core-understanding` first for project identity and formal gameplay structure.
2. Read `references/battle-content-overview.md` for the full battle content layer model.
3. Read `references/monster-boss-config-map.md` when the request involves monster stats, boss mechanics, elite types, or enemy creation.
4. Read `references/skill-buff-config-map.md` when the request involves skill timelines, buff effects, damage effects, bullet configs, summon configs, or action clips.
5. Read `references/wave-level-config-map.md` when the request involves wave spawns, level terrain, loop triggers, spawn conditions, or encounter pacing.
6. Read `references/ai-behavior-config-map.md` when the request involves AI behavior trees, decision logic, state machines, aggro, or patrol patterns.
7. Use `vgame-config-schema` for exact source table discovery, Luban schema, export pipeline, or JSON tracing.
8. Use `vgame-level-progression-map` for LevelId, LevelType, chapter, Unlock, SystemOpen, and stamina context.
9. Use `vgame-growth-combat-conversion-map` for how player growth converts into combat performance against this content.
10. Use `vgame-reward-drop-sync` for DropId and reward references tied to battle outcomes.
11. Use `game-numerical-analysis` for enemy HP/ATK scaling curves, DPS checks, and difficulty balance.

## Scope

Covered in v1:

- monster/elite/boss entity config: stats, type, camp, visual, spawn parameters
- skill system config: skill tables, action clips, timelines, cast conditions, cooldowns, targeting
- buff system config: buff tables, effect types, stacking, duration, trigger conditions, removal
- damage pipeline config: damage effects, damage types, tags, multipliers, critical, block, shield interaction
- bullet/projectile config: bullet tables, trajectory, hit detection, penetration, AOE
- summon config: summon tables, AI assignment, lifetime, ownership
- AI behavior: behavior tree tables, decision nodes, aggro logic, phase transitions
- wave/encounter config: wave tables, spawn timing, spawn conditions, loop mechanics, terrain triggers
- environmental hazard config: traps, obstacles, moving platforms, damage zones
- battle event/feedback: camera shake, hit stop, VFX triggers, audio cues, slow motion

Not covered directly:

- player character skill balance or numerical tuning (route to `game-numerical-analysis`)
- exact reward for clearing content (route to `vgame-reward-drop-sync`)
- unlock conditions for content access (route to `vgame-level-progression-map`)
- long-term economy impact of battle content (route to `senior-game-economy`)
- source table schema details (route to `vgame-config-schema`)

## Standard Workflow

1. Identify which battle content element the user is asking about (monster? boss? skill? buff? wave? AI?).
2. Locate the relevant config layer from references.
3. Map source tables, key fields, and cross-table references.
4. Identify the authoring pipeline: which Excel workbook → which Luban logical table → which runtime system reads it.
5. Separate confirmed project facts from items needing source-file verification.
6. Route numerical balance, rewards, progression, and schema questions to downstream skills.

## Output Contract

For battle content analysis, include:

- `Content element`: monster/boss/skill/buff/AI/wave/bullet/summon/hazard/event.
- `Source tables`: workbook, sheet, logical table name, key fields.
- `Cross-table references`: which other tables this element references or is referenced by.
- `Runtime consumer`: which Lockstep/Logic system reads this config at runtime.
- `Authoring flow`: Excel → Luban → JSON → runtime load path.
- `Evidence to read`: specific files or sheets needed for exact proof.
- `Risk`: missing references, deprecated tables, naming inconsistencies, or pipeline gaps.

Use `待确认` for any mapping not directly observed from project docs or source files.
