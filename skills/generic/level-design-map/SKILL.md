---
name: level-design-map
description: Generic methodology for level design mapping — covering the two-layer architecture (config table vs scene/editor), encounter pacing, wave/spawn systems, game mode variations, and difficulty tuning applicable to any game with discrete levels or stages.
---

# Level Design Mapping Skill

## Load Order
1. Read this SKILL.md for architecture and methodology.
2. Identify the project's level editor tooling and config schema.
3. Apply the two-layer model when planning or reviewing level content.

## Scope
- Two-layer architecture (config vs scene).
- Terrain/environment patterns. Encounter pacing.
- Wave/spawn system design. Level editor workflows.
- Game mode structural implications. Difficulty tuning knobs.
- Level ID conventions.

## 双层架构模型 (Two-Layer Architecture)

| Layer | Contents | Owned By |
|-------|----------|----------|
| Config Table Layer | Level ID, difficulty params, rewards, unlock conditions, mode type, time limits | Systems/Numeric designers |
| Scene/Editor Layer | Terrain layout, spawn points, camera paths, trigger volumes, visual scripting | Level/Content designers |

Separation principle: Config layer controls **what** and **how much**; Scene layer controls **where** and **how it feels**.

## 地形/环境设计模式 (Terrain & Environment Patterns)

- **Arena** — bounded space, boss fights, wave defense.
- **Corridor** — linear progression, pacing control via gates.
- **Hub-and-spoke** — central area with branching paths, exploration.
- **Open zone** — large area with scattered encounters, free traversal.
- **Vertical** — multi-floor, elevation mechanics matter.

## 战斗节奏方法论 (Encounter Pacing Methodology)

```
Tension curve: Intro(low) → Build(medium) → Peak(high) → Rest(low) → Climax(highest)
```

- Combat-to-exploration ratio target (e.g., 60/40 for action games, 40/60 for adventure).
- Rest points: safe zones, treasure, narrative beats.
- Escalation: each wave or encounter slightly harder until boss.

## 波次/刷怪系统 (Wave / Spawn System Patterns)

- **Timed waves** — fixed interval spawns.
- **Condition-triggered** — spawn on enemy count threshold, player position, or event.
- **Infinite escalation** — survival modes; difficulty ramps per wave.
- **Scripted sequence** — cutscene-integrated, phase-transition spawns.

Each wave definition: `{ waveIndex, spawnDelay, entityList[], triggerCondition, completionCondition }`

## 关卡编辑器工作流 (Level Editor Workflow)

1. **Block-out** — gray-box geometry, placeholder spawns.
2. **Gameplay pass** — place triggers, spawn points, camera zones.
3. **Art pass** — replace with final assets, lighting, VFX.
4. **Polish** — audio, particles, feedback tuning.
5. **Serialize** — export to engine-readable format.
6. **Validate** — automated checks (reachability, spawn inside geometry, missing refs).

## 游戏模式与关卡结构 (Game Mode Variations)

| Mode Type | Level Structure Implication |
|-----------|-----------------------------|
| Story/Campaign | Linear chapters, gated progression, narrative triggers |
| Roguelike | Procedural room selection, modular encounters |
| Tower/Abyss | Fixed floors, escalating difficulty, reset cycles |
| PvP Arena | Symmetric layout, fixed spawn points, no PvE |
| Raid/Co-op | Larger arenas, multi-phase boss, role-specific zones |

## 难度调节旋钮 (Difficulty Tuning Knobs)

**Config layer knobs**: enemy level, stat multipliers, time limit, wave count, reward tier.
**Scene layer knobs**: spawn density, arena size, obstacle placement, safe zone availability.

## 关卡ID命名惯例模板 (Level ID Convention Template)

```
{ModePrefix}_{ChapterOrZone}_{StageNumber}_{DifficultyTier}
Example: STORY_C01_S03_NORMAL, ABYSS_F12_HARD, EVENT_SUMMER_W05
```

## Standard Workflow
1. Define level in config table (ID, mode, difficulty params, rewards).
2. Build scene in editor following block-out → gameplay → art pipeline.
3. Configure wave/spawn data referencing entity table.
4. Set difficulty knobs per config layer.
5. Run validation tools; fix broken references.
6. Playtest pacing; adjust tension curve.

## Output Contract
- Level config entry with all required fields populated.
- Scene file with validated spawn points and trigger volumes.
- Pacing diagram showing tension curve.
- Difficulty parameter table per tier.
