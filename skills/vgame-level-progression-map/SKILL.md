---
name: vgame-level-progression-map
description: Use for Vgame level progression, chapter mapping, LevelId and LevelType tracing, gameplay unlock chains, SystemOpen/Unlock references, stamina and sweep checks, and formal gameplay config chains across mainline, resource dungeons, travel-ticket dungeons, special-equipment dungeons, infinite challenge, PVPVE, tower, mythic dungeon, and boss challenge. Use when asked where a gameplay mode is configured, when it unlocks, which level tables it touches, or how UIlevel/mainline/chapter/system-open configs connect.
---

# Vgame Level Progression Map

Use this skill to trace Vgame's formal gameplay progression chain: which level table owns a gameplay mode, how a LevelId maps to LevelType and chapter/UI entries, how unlocks are represented, and where stamina, sweep, first-clear, repeat, and system-open references appear.

This skill is pure documentation in v1. It does not run scripts and does not edit source Excel.

## Load Order

1. Read `vgame-core-understanding` first for the formal gameplay boundary.
2. Read `references/progression-overview.md` for the progression-layer model.
3. Read `references/level-config-map.md` when tracing LevelId, LevelType, chapter, UIlevel, stamina, sweep, or gameplay source tables.
4. Read `references/unlock-system-map.md` when tracing `Unlock`, `UnlockDesc`, `SystemOpen`, feature opening, or system entrance behavior.
5. Read `references/progression-audit-checklist.md` before reporting a level-progression review as complete.
6. Use `vgame-config-schema` for exact table schema, Luban export, source-vs-generated decisions, or validation commands.
7. Use `vgame-reward-drop-sync` for real reward package changes, DropId allocation, reward preview consistency, or first-clear/repeat reward implementation.
8. Use `senior-game-economy` when the task asks whether an unlock timing, stamina cost, supply amount, or progression pace is economically appropriate.

## Scope

Covered in v1:

- `主线`
- `资源副本`
- `旅券副本`
- `映射装备副本`
- `无限挑战`
- `竞技场（PVPVE）`
- `爬塔`
- `大秘境`
- `BOSS挑战`

Not covered by default in v1:

- `肉鸽`
- `神经漫游`
- 小游戏
- 历史玩法、草稿玩法、废弃玩法

Only include these excluded areas when the user explicitly asks for them.

## Boundaries

- Do not decide reward values here; route reward implementation to `vgame-reward-drop-sync`.
- Do not decide combat difficulty or formulas here; route battle tuning to future combat-specific skill or `game-numerical-analysis`.
- Do not treat generated JSON as source; use `vgame-config-schema` before making source-table claims.
- Do not infer unlock timing from memory when `Unlock` or `SystemOpen` needs to be checked.

## Standard Workflow

1. Identify the gameplay mode, LevelId, LevelType, chapter, or system ID in the user request.
2. Confirm whether the request is about formal gameplay or an excluded/draft system.
3. Use `level-config-map.md` to pick the relevant source tables.
4. Use `unlock-system-map.md` if the question involves feature opening, entrance visibility, or preconditions.
5. If rewards are mentioned, separate progression references from reward-package content.
6. Report evidence paths, fields, known facts, and `待确认` gaps.
7. End with a progression impact matrix for any proposed change.

## Output Contract

For level-progression work, include:

- gameplay mode or LevelId/LevelType
- source table and sheet
- key fields used for progression, unlock, stamina, sweep, chapter, or UI mapping
- related SystemOpen/Unlock IDs when observed
- reward fields as references only, unless routed to reward sync
- verification checklist result or remaining `待确认` items
