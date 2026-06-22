---
name: vgame-growth-combat-conversion-map
description: Use for Vgame growth-to-combat conversion analysis across character level/breakthrough, star map, star-up, signature weapon, travel-ticket equipment, mapping equipment, gems, inscriptions, turret/base-related growth, battle attributes, panel conversion, standard player model, power curve, and formal gameplay verification. Trigger when asked how a growth system affects combat performance, which gameplay modes verify a growth line, what a resource or module ultimately improves, or how mainline/resource dungeons/gacha/equipment progression converts into DPS, survival, uptime, boss handling, endurance, PVPVE efficiency, tower depth, or mythic-dungeon readiness.
---

# Vgame Growth Combat Conversion Map

Use this skill to answer: a Vgame growth system improves what, which battle attributes or mechanics it touches, and which formal gameplay modes should feel the impact.

This is a project mapping skill. It is read-only by default and does not edit config tables.

## Load Order

1. Read `vgame-core-understanding` first for project identity and formal gameplay boundaries.
2. Read `references/growth-combat-overview.md` for the whole growth-to-combat chain.
3. Read `references/growth-module-map.md` when the request names a growth module, item family, or equipment system.
4. Read `references/combat-conversion-fields.md` when the request involves attributes, formulas, panel stats, DPS, survival, uptime, or battle mechanics.
5. Read `references/verification-mode-map.md` when the request asks which gameplay mode verifies the growth line.
6. Use `vgame-config-schema` for exact source tables, fields, Luban schema, generated JSON, or validation.
7. Use `vgame-economy-source-map` for resource source/sink tracing before judging a growth line's supply.
8. Use `vgame-level-progression-map` for unlock timing, LevelType, LevelId, chapter, stamina, sweep, or system-open chains.
9. Use `vgame-reward-drop-sync` for DropId/UIlevel reward content.
10. Use `senior-game-economy` for reward value, long-term economy pressure, and Excel landing design.
11. Use `game-numerical-analysis` for quantitative curves, expected days, combat balance, and model calculations.

## Scope

Covered in v1:

- character base growth: level, breakthrough, star map, star-up
- signature weapon growth
- travel-ticket equipment growth
- mapping equipment, gems, inscriptions, red-equipment refinement and over-limit concepts
- growth attribute categories: base attributes, base attribute %, level attributes, secondary attributes, skill/talent effects
- conversion into combat performance: damage, survival, energy/ultimate cadence, cooldown, block, critical output, shield/heal value, environment fit
- verification gameplay mapping: mainline, boss challenge, infinite challenge, PVPVE, tower, mythic dungeon

Not covered directly:

- exact numerical tuning or final balance judgment
- exact Drop package content
- exact source/sink ledger for every item
- generated JSON edits

## Standard Workflow

1. Identify the growth module or resource named by the user.
2. Map the module to its growth responsibility: base stats, percentage stats, secondary stats, skill mechanics, random-depth equipment, or gameplay-specific support.
3. Map those outputs to combat-facing attributes or mechanics.
4. Identify which formal gameplay modes should verify the improvement.
5. Separate known project facts from table-level facts that still need source-file reading.
6. Route exact config, reward, economy, or numerical questions to the matching downstream skill.

## Output Contract

For growth-combat analysis, include:

- `Growth module`: system, item family, or config area being discussed.
- `Growth output`: attributes, mechanics, or progression gates it owns.
- `Combat conversion`: how the output becomes DPS, survival, uptime, control, burst, endurance, or environment adaptation.
- `Verification modes`: formal gameplay modes expected to reflect the change.
- `Evidence to read`: source docs, Excel workbooks, or specialist skills needed for exact proof.
- `Risk`: overlap, value inflation, obsolete-system confusion, or missing source evidence.

Use `待确认` for any link not directly observed from project docs or source files.
