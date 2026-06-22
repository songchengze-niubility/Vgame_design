---
name: vgame-economy-source-map
description: Use for Vgame resource-ledger and economy source/sink tracing across Items, Drop, UIlevel, level, Shop, Task, BattlePass, SignInReward, Activity, MonthCard, Mail, DrawCard, PlayerLv, ItemAccess, and related source Excel configs. Trigger when the task asks where a currency, item, ticket, stamina, growth material, equipment resource, reward package, shop cost, task reward, activity reward, gacha cost, or paid/economy resource is produced, consumed, previewed, unlocked, or economically risky.
---

# Vgame Economy Source Map

Use this skill to answer: a Vgame resource is what, where it comes from, where it is spent, which source tables reference it, and what economy risks must be checked.

This is a pure documentation skill. Do not modify real config tables from this skill alone.

## Load Order

1. Read `vgame-core-understanding` first for project context.
2. Read `references/resource-ledger-overview.md` for the resource-ledger model.
3. Read `references/economy-config-map.md` when locating source tables and fields.
4. Read `references/source-sink-audit-checklist.md` before answering a source/sink or risk audit.
5. Read `references/economy-risk-notes.md` when the task touches paid currency, gacha, shop, infinite/repeatable rewards, activity rewards, or stamina.

Use related skills for their own domains:

- Use `vgame-config-schema` for exact schema, Luban logical table mapping, generated JSON tracing, and export validation.
- Use `vgame-reward-drop-sync` for actual Drop package content, DropId allocation, UIlevel reward preview, first-clear rewards, repeat rewards, and random weighted reward implementation.
- Use `vgame-level-progression-map` for LevelId, LevelType, chapter, Unlock/SystemOpen, stamina/sweep, and gameplay-opening chains.
- Use `senior-game-economy` for value judgment, pacing, long-term supply, monetization pressure, reward reasonableness, and Excel delivery design.
- Use `game-numerical-analysis` for quantitative resource income/outflow models, curves, probabilities, and multi-system numerical audits.

## Scope

This skill covers read-only economy tracing for:

- currencies: gold, premium currency, stamina, shop currencies, activity points, arena currency, guild currency, tickets
- growth resources: account EXP, character EXP, equipment EXP, signature-weapon resources, upgrade and breakthrough materials
- equipment resources: travel-ticket resources, mapping-equipment resources, gems/chips/tokens, decomposition outputs
- production channels: levels, UIlevel reward references, Drop packages, tasks, active rewards, battle pass, sign-in, month card, activity, mail, shop purchase, draw/gacha, player level-up
- consumption channels: shop goods, level stamina, gacha price, upgrade/craft systems, item chest/opening, quick purchase, paid products

## Boundaries

- Do not treat `Items.AccessList` as proof of real production. It is an acquisition-display and jump clue; confirm real source tables.
- Do not treat `Reward`, `FirstReward`, `RewardItemPreview`, or other preview fields as the real reward package unless the field is explicitly a direct `PropType` reward.
- Do not assume one Drop workbook owns all rewards. Vgame logical `Drop` merges multiple files.
- Do not decide final reward value, economy amount, or balance pacing here. Route those judgments to `senior-game-economy` or `game-numerical-analysis`.
- Do not edit `server_json`; generated JSON is not the source of truth.

## Output Contract

When answering with this skill, include:

- `Resource`: item ID/name/type if observed.
- `Sources`: production tables and fields, with source workbook and sheet.
- `Sinks`: consumption tables and fields, with source workbook and sheet.
- `References`: DropId/RewardId/UIlevel/Shop/Task/Activity/Mail references that still need expansion.
- `Unlock/Progression`: only if relevant, and route through `vgame-level-progression-map`.
- `Risk`: repeatability, paid/gacha sensitivity, preview-vs-real ambiguity, activity duration, and validation gaps.
- `Next Skill`: which skill should handle reward-package content, schema/export, or value judgment.

Use `待确认` for any relationship not directly observed in source files.
