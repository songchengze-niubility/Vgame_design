---
name: vgame-tutorial-onboarding-map
description: Use for Vgame newbie guide system, battle tutorial triggers, out-of-battle guide sequences/steps, SystemOpen feature unlock gating, unlock condition chains, guide editor workflow, guide progression timeline, forced vs soft guide design, guide skip/failure logic, and the relationship between planning docs and runtime config. Trigger when asked how tutorials work, how to add a new guide step, how SystemOpen controls feature visibility, how unlock conditions chain, what the new player first-hour experience looks like, how to configure battle guides, or how guide data flows from editor to runtime.
---

# Vgame Tutorial & Onboarding Map

Use this skill to answer: how Vgame's tutorial and onboarding systems work, how guides are authored and triggered, how feature unlocks are gated, and how the new player experience is structured.

This is a project mapping skill. It is read-only by default.

## Load Order

1. Read `vgame-core-understanding` first for project identity and gameplay structure.
2. Read `references/tutorial-system-architecture.md` for the dual-system overview (battle guide + newbie guide).
3. Read `references/battle-guide-config.md` when the request involves in-combat tutorials, ZoneShowGuide triggers, or BattleGuide.xlsx.
4. Read `references/newbie-guide-config.md` when the request involves out-of-battle guides, sequences, steps, masks, or the guide editor.
5. Read `references/system-open-unlock-chain.md` when the request involves feature unlock gating, SystemOpen conditions, or progression-tied unlocks.
6. Use `vgame-level-progression-map` for LevelId, chapter/stage progression context that drives unlock timing.
7. Use `vgame-level-design-map` for how ZoneShowGuide triggers are placed in level scenes.
8. Use `vgame-config-schema` for exact table schema or Luban export details.

## Scope

Covered:

- Dual tutorial architecture: BattleGuide (C#) + NewbieGuide (Lua)
- BattleGuide config: 16 action types, zone triggers, pause/resume, skill teaching
- NewbieGuide config: sequences, steps, masks, bubbles, arrows, click/drag detection
- Guide editor workflow: Unity EditorWindow → JSON → Lua auto-export
- SystemOpen feature gating: 92 systems, UnlockId, CloseSys, popup control
- Unlock condition system: 682 conditions, level-clear/grade/task/tower/character triggers
- New player timeline: first-hour 24-step flow, feature unlock pacing
- Guide persistence: server sync, completion tracking, expire logic
- Planning docs: 开启节奏和引导, 新手流程, 养成进度预估

Not covered:

- Plot/cutscene system (separate Timeline-based system)
- Exact UI panel implementation details
- Game design decisions about pacing (route to `senior-game-economy` onboarding reference)

## Output Contract

For tutorial/onboarding analysis, include:

- `System`: which guide system (BattleGuide / NewbieGuide / SystemOpen)
- `Trigger`: what causes the guide to fire (zone position / unlock event / UI open)
- `Config source`: which file and fields define the behavior
- `Flow`: sequence of steps from trigger to completion
- `Persistence`: how completion is tracked (local / server / both)
- `Dependencies`: what must be unlocked or completed first
- `Risks`: guide not firing, target UI missing, timing issues, skip edge cases
