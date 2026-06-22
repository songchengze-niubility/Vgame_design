---
name: vgame-outer-loop-system-map
description: Use for Vgame outer-loop system mapping across gacha/draw-card, shop, tasks, daily/weekly active rewards, sign-in, battle pass, activities, mail, month card, sweep, player level rewards, social loops, paid products, quick purchase, retention cadence, monetization support, and resource-supplement relationships. Trigger when asked how Vgame's non-combat systems connect, which systems drive retention or monetization, how rewards are organized across daily/weekly/seasonal/activity loops, or how outer-loop systems supplement growth and verification gameplay.
---

# Vgame Outer Loop System Map

Use this skill to answer: how Vgame's outer-loop systems organize retention, resource supplements, box expansion, monetization support, and activity cadence.

This skill maps systems and responsibilities. It is not a replacement for exact item source/sink tracing or reward-package expansion.

## Load Order

1. Read `vgame-core-understanding` first for Vgame's formal gameplay and outer-loop boundary.
2. Read `references/outer-loop-overview.md` for the system relationship model.
3. Read `references/outer-loop-config-map.md` when locating source tables and fields.
4. Read `references/cycle-monetization-map.md` when the task touches daily/weekly/seasonal cadence, paid resources, shop refresh, battle pass, month card, gacha, or activity pressure.
5. Read `references/outer-loop-audit-checklist.md` before reporting an outer-loop review as complete.
6. Use `vgame-economy-source-map` for exact ItemId source/sink tracing.
7. Use `vgame-reward-drop-sync` for DropId, reward package content, UIlevel reward previews, or random reward packages.
8. Use `vgame-level-progression-map` for SystemOpen, Unlock, LevelType, sweep, stamina, and gameplay-opening chains.
9. Use `vgame-config-schema` for source table discovery, schema, Luban export, or validation.
10. Use `senior-game-economy` and `game-numerical-analysis` for value reasonableness and quantitative balance.

## Scope

Covered in v1:

- gacha and draw-card entry systems
- shops, shop goods, paid products, quick purchase
- tasks, daily tasks, weekly tasks, daily/weekly active rewards
- sign-in and cumulative sign-in
- battle pass
- activities and activity active rewards
- mail and presend mail
- month card
- sweep, player level rewards, and resource supplement loops
- social/retention systems at the responsibility level

Not covered directly:

- detailed source/sink ledger for a specific ItemId
- exact Drop package content
- exact gacha probability or expected cost
- direct editing of config tables

## Standard Workflow

1. Identify which outer-loop system or resource loop the user is asking about.
2. Classify the system's responsibility: retention, resource supplement, box expansion, monetization support, social retention, or compensation.
3. Locate likely config tables from `outer-loop-config-map.md`.
4. Identify cadence: one-time, daily, weekly, season, activity, paid recurring, or refresh-based.
5. Separate display fields from real reward or cost fields.
6. Route item ledgers, Drop package content, unlock chains, and value judgments to downstream skills.

## Output Contract

For outer-loop work, include:

- `System`: outer-loop system or group.
- `Responsibility`: retention, monetization, resource supplement, box expansion, social, or compensation.
- `Cadence`: one-time/daily/weekly/seasonal/activity/paid/refresh, with `待确认` if not read.
- `Source tables`: source workbook, sheet, and key fields.
- `Reward/cost references`: direct PropType fields and DropId/RewardId references to expand.
- `Risks`: paid sensitivity, repeated supply, preview-vs-real ambiguity, unlock ambiguity, obsolete-system confusion.
- `Next skill`: exact downstream skill if deeper proof is required.
