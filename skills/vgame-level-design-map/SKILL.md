---
name: vgame-level-design-map
description: Use for Vgame level design, terrain layout, encounter pacing, loop zone design, moving platform configuration, camera boundary setup, level editor workflow, scene serialization pipeline, spawn placement, gameplay mode differences, level ID conventions, and the relationship between Excel config and Unity scene authoring. Trigger when asked how to design a new level, how terrain is structured, how loop zones work, how spawns are placed, how the level editor works, how to adjust encounter pacing, how level data flows from Excel to runtime, or how different gameplay modes affect level structure.
---

# Vgame Level Design Map

Use this skill to answer: how Vgame levels are designed, authored, configured, and loaded at runtime — covering the full pipeline from Excel config to Unity scene editing to runtime streaming.

This is a project mapping skill. It is read-only by default.

## Load Order

1. Read `vgame-core-understanding` first for project identity (parkour combat shooter) and formal gameplay structure.
2. Read `references/level-architecture-overview.md` for the two-layer model (Excel config vs Unity scene) and runtime flow.
3. Read `references/terrain-and-loop-design.md` when the request involves terrain types, loop zones, kill conditions, moving platforms, or destructible terrain.
4. Read `references/encounter-pacing-guide.md` when the request involves spawn placement, enemy density, difficulty pacing, or loop tuning.
5. Read `references/level-editor-pipeline.md` when the request involves the Unity level editor workflow, serialization, or scene data structure.
6. Use `vgame-battle-content-map` for monster/skill/buff/AI configuration within levels.
7. Use `vgame-battle-tuning-helper` for DPS/TTK/difficulty calculations at a specific level.
8. Use `vgame-level-progression-map` for LevelId, LevelType, unlock chains, SystemOpen, and progression context.
9. Use `vgame-config-schema` for exact Excel table schemas and export pipeline.

## Scope

Covered:

- Two-layer architecture: Excel config (level.xlsx/UIlevel.xlsx) vs Unity scene (terrain/spawns/triggers)
- Terrain system: static terrain, destructible terrain, moving platforms, terrain types
- Loop terrain: repeating combat zones, kill-count exit conditions (Boss/Elite/Ordinary)
- Entity streaming: X-position-based loading/unloading as camera scrolls
- Level follower (camera scroll) and speed control
- Encounter pacing: enemy placement, density, rhythm between combat and platforming
- Level editor workflow: editing, saving, serialization to MessagePack bytes
- Game mode differences: how NormalMode/CoinMode/TowerMode/PVPVEMode affect level structure
- Level ID conventions (6-digit system)
- Monster attribute coefficient system (HP/ATK/DEF per-level tuning)
- Camera boundary configuration
- Scene data structure (LogicData / VisualData / StringTable)

Not covered:

- Exact monster skill/AI configuration (route to `vgame-battle-content-map`)
- DPS/TTK numerical calculations (route to `vgame-battle-tuning-helper`)
- Reward/Drop configuration for levels (route to `vgame-reward-drop-sync`)
- Unlock/progression chain details (route to `vgame-level-progression-map`)

## Standard Workflow

1. Identify what level design question the user is asking (new level? terrain? pacing? editor? mode?).
2. Determine which layer is relevant: Excel config, Unity scene, or both.
3. For Excel config questions → reference level-config-map from `vgame-level-progression-map`.
4. For scene/terrain questions → reference terrain-and-loop-design and level-editor-pipeline.
5. For pacing/tuning questions → reference encounter-pacing-guide + route numbers to `vgame-battle-tuning-helper`.
6. Separate confirmed pipeline facts from items needing scene file inspection.

## Output Contract

For level design analysis, include:

- `Level type`: gameplay mode and its structural implications.
- `Config layer`: which Excel tables and fields are involved.
- `Scene layer`: terrain structure, loop zones, spawn points, triggers.
- `Pacing`: combat vs platforming ratio, enemy density, loop duration.
- `Tuning knobs`: what can be adjusted in Excel vs what requires scene re-edit.
- `Pipeline`: how changes flow from edit to runtime.
- `Risks`: terrain/spawn misalignment, loop condition bugs, camera boundary issues.

Use `待确认` for scene-level details not directly observable without opening Unity.
