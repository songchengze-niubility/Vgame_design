---
name: vgame-core-understanding
description: Use as the Vgame project-level master skill and default project adapter for all Vgame planning, economy, progression, combat, configuration, reward, item/source-sink, feature, and gameplay-analysis tasks. Apply this first for any Vgame request to establish project facts, route to the right specialist skill, protect source-table and evidence rules, and decide whether the task is high-level design, read-only analysis, config implementation, validation, or delivery review.
---

# Vgame Core Understanding

Use this skill as the Vgame project master skill.

It owns project-level understanding, task routing, evidence rules, and delivery gates. Specialist skills are downstream tools; they do not replace this skill as the entry point.

Vgame is not a traditional idle card battler. It is a `5-character squad progression-driven parkour combat shooter` with:
- auto normal attacks
- auto skills
- player-timed ult usage
- gameplay value strongly affected by encounter rhythm, uptime, and environment fit

## Project Master Role

This skill is the entry project adapter for `${VGAME_DESIGN_ROOT}`.

When called by the generic `game-planning-control` skill:

1. Read this skill first to align on Vgame's gameplay identity.
2. Read `references/project-profile.md` for project paths and known facts.
3. Read `references/project-control-workflow.md` to classify the task and choose the route.
4. Read `references/evidence-map.md` before making file-level claims.
5. Read `references/config-index.md` before reviewing or changing Excel, JSON, DropId, UIlevel, reward, task, shop, activity, or unlock configuration.
6. Read `references/delivery-gates.md` before declaring anything ready for delivery or acceptance.
7. Call downstream skills only when the task crosses their boundary.

## Default Control Flow

1. Identify the task type: project explanation, design discussion, read-only analysis, config implementation, validation, or delivery review.
2. Anchor the answer in Vgame's confirmed project identity and formal gameplay structure.
3. Decide whether source files must be read. Do not inspect Excel or JSON when the user only asks for high-level project framing.
4. If file evidence is needed, follow `references/evidence-map.md` and prefer source Excel over generated JSON.
5. If config tables are involved, route through `vgame-config-schema` before trusting table or field meaning.
6. If rewards, DropId, UIlevel, source/sink, LevelId, Unlock, SystemOpen, tutorial/onboarding, level design, character kit design, growth-to-combat conversion, outer-loop structure, config QA, battle formulas, or economy value are involved, call the matching specialist skill.
7. Before claiming completion, check `references/delivery-gates.md`.

## Specialist Routing

| Task signal | Route |
|---|---|
| source-table discovery, Luban schema, export flow, generated JSON tracing, config validation, new table onboarding | `vgame-config-schema` |
| resource ledgers, ItemId, item/currency source and sink tracing, shop/task/activity/mail/battle-pass/sign-in/draw-card economy references | `vgame-economy-source-map` |
| DropId, Drop/UIlevel, first-clear rewards, repeat rewards, reward previews, random weighted drops | `vgame-reward-drop-sync` |
| LevelId, LevelType, chapter progression, Unlock/SystemOpen, stamina, sweep, gameplay opening, level config chains | `vgame-level-progression-map` |
| character kit design, hero role positioning, normal/auto/ultimate/talent loops, common passives, star-up nodes, signature weapons, travel-ticket set skills, mapping-equipment affixes, skill implementation risks | `vgame-character-kit-design-map` |
| hero definition config, Hero/Skill/Buff tables, hero attributes, ascension, star-up, exclusive weapon config, skill editor workflow, skill runtime serialization | `vgame-hero-skill-config-map` |
| character growth, star map, star-up, signature weapon, travel-ticket equipment, mapping equipment, battle attribute conversion, formal gameplay verification | `vgame-growth-combat-conversion-map` |
| hero definition, hero attributes, hero ascension/star, exclusive weapon, skill config, skill editor, skill actions, buff system, buff effects, hero-skill-buff cross-references, efficiency/star-map nodes | `vgame-hero-skill-config-map` |
| gacha, shop, task, sign-in, battle pass, activity, mail, month card, sweep, paid products, retention cadence, monetization-support loops | `vgame-outer-loop-system-map` |
| read-only config QA, delivery audit, broken references, registered table inputs, ItemId/DropId/RewardId integrity, PropType formats, common config quality gates | `vgame-config-quality-audit` |
| planning UI prototype, interactive HTML, rendered page/component PNG, UI asset manifest, rule-to-UI traceability | `vgame-ui-prototype` |
| monster, boss, elite, skill, buff, AI, behavior tree, wave spawn, bullet, summon, damage effect, encounter pacing, battle content authoring | `vgame-battle-content-map` |
| level design, terrain layout, loop zones, moving platforms, encounter pacing, spawn placement, level editor, scene serialization, camera boundaries, gameplay mode level structure | `vgame-level-design-map` |
| tutorial, newbie guide, battle guide, ZoneShowGuide, guide sequences/steps, SystemOpen, feature unlock gating, unlock conditions, onboarding timeline, guide editor | `vgame-tutorial-onboarding-map` |
| DPS calculation, TTK estimation, monster stat lookup, player power curve, difficulty coefficient, combat what-if, survival analysis, battle tuning | `vgame-battle-tuning-helper` |
| version milestone, feature release state, feature switch, SystemOpen runtime, AB test, gray release, hotfix, rollback, deprecated lifecycle | `vgame-version-release-map` |
| player progression simulation, day-by-day resource projection, growth milestone estimation, bottleneck detection, economy validation, scenario comparison, stamina budget | `vgame-player-progression-simulator` |
| reward value, long-term economy, Excel landing design, economy risk judgment | `senior-game-economy` |
| broad numerical experience audits, growth curves, resource balance, combat balance, probability, player experience pacing | `game-numerical-analysis` |

## Core Interpretation Rules

- Treat `主线` as the main progression axis.
- Treat `资源副本 / 旅券副本 / 映射装备副本` as the main stable growth supply layer.
- Treat `无限挑战 / 竞技场（PVPVE） / 爬塔 / 大秘境 / BOSS挑战` as the main verification gameplay layer.
- Treat `任务 / 抽卡 / 商店 / 通行证 / 签到 / 公会 / 好友聊天` as outer-loop systems, not the main combat gameplay layer.
- Do not reintroduce deprecated gameplay unless the user explicitly says the project is reviving it.

## Current Formal Gameplay Structure

### 1. Main Combat Axis

- `主线`
  Main game axis. Carries story, onboarding, feature unlocks, early combat teaching, and early-to-mid progression.

### 2. Stable Growth Gameplay

- `资源副本-金币`
  Daily gold supply.
- `资源副本-角色经验`
  Daily character EXP supply.
- `资源副本-专武经验`
  Daily signature-weapon EXP supply.
- `旅券副本`
  Four boss-style stages with clearly different combat pacing and style. Main stable source for `旅券`.
- `映射装备副本`
  Short, high-frequency farming gameplay with a "loot burst" feel similar to a dungeon grind. Main source of `映射装备`, related EXP, tokens, gems, and inscriptions.

### 3. Verification Gameplay

- `无限挑战`
  Endless parkour challenge. Every 3 stages cycle through `normal -> elite -> boss`. Used for long-run endurance and comprehensive account-depth verification.
- `竞技场（PVPVE）`
  Not direct player-vs-player shooting. Two players race through the same stage; uncleared enemies damage the player's base. The side whose base dies first loses. `炮台` affects base HP and damage taken from enemies.
- `爬塔`
  Hybrid one-time plus periodic-refresh gameplay. Early floors are one-time; later floors refresh on a cycle. Mainly verifies single-team DPS depth.
- `大秘境`
  28-day seasonal multi-environment climbing gameplay. Late-game hardcore verification focused on box breadth, environment fit, and endgame depth.
- `BOSS挑战`
  One-time boss challenge gameplay. Bosses from main/side content are reused as standalone difficulty gates.

## Current Formal Outer-Loop Systems

- `章节任务`
- `每日任务`
- `每周任务`
- `抽卡 / 新手卡池`
- `专武抽卡 / 专武系统`
- `主线扫荡`
- `邮件`
- `签到`
- `商店`
- `通行证`
- `公会`
- `好友 / 聊天`

These are formal systems, but they should usually be discussed as:
- retention loops
- economy loops
- social loops
- monetization support loops

not as core combat gameplay.

## Current Deprecated Or Non-Formal Content

Treat the following as not part of the current formal gameplay structure:

- `世界boss`
- `能效本`
- `主角装备本 / 宝石本 / 铭文本（铭文已删除）`
- `肉鸽`

Treat the following as draft only:

- `BOSS无限挑战`

## Progression Understanding

When reasoning about account growth, default to this path:

`主线`
-> unlocks systems and early growth
-> daily supply gameplay feeds account growth
-> outer-loop systems supplement resources and box expansion
-> verification gameplay checks whether growth has converted into real combat power

### Growth Responsibilities by Layer

- `主线`
  Unlock and early growth.
- `资源副本`
  Base resource stability.
- `旅券副本`
  Stable midgame equipment growth.
- `映射装备副本`
  Endgame random-depth growth.
- `抽卡 / 专武`
  Box breadth and role-mechanic depth.
- `竞技场 / 爬塔 / 大秘境 / 无限挑战 / BOSS挑战`
  Verify different kinds of combat readiness.

## Validation Dimensions

Default verification focus by gameplay:

- `主线`
  overall account readiness
- `BOSS挑战`
  stage-gated boss handling
- `无限挑战`
  long-run endurance and comprehensive depth
- `竞技场（PVPVE）`
  confrontation efficiency, survivability, and competitive seasonal retention
- `爬塔`
  single-team DPS and vertical progression
- `大秘境`
  box breadth, environment adaptation, and late-game hardcore readiness

## Use This Skill Instead Of Re-reading Excel When

- the user asks what Vgame is
- the user asks what the formal gameplay modes are
- the user asks how gameplay layers relate to progression
- the user asks whether a system is core gameplay, outer-loop, draft, or deprecated
- the user asks for a high-level explanation of how growth converts into combat verification

## When To Read More Sources

Read deeper project sources only if the task needs:

- exact reward numbers
- exact formulas
- exact unlock timing details
- exact battle constants
- exact sheet-level dependencies

Use `vgame-config-schema` for exact config source and export dependencies. Use `vgame-economy-source-map` for resource source/sink tracing and economy reference maps. Use `vgame-reward-drop-sync` for exact Drop/UIlevel reward dependencies.
Use `vgame-level-progression-map` for exact level, chapter, unlock, SystemOpen, stamina, sweep, and gameplay-opening dependencies.
Use `vgame-character-kit-design-map` for hero role positioning, skill kits, talents, star-up design, signature weapons, travel-ticket set skills, mapping-equipment affixes, common passives, and character design workbook evidence.
Use `vgame-hero-skill-config-map` for exact hero definition config, Hero/Skill/Buff tables, hero attributes, ascension, star-up, exclusive weapon config, skill editor workflow, and runtime skill serialization.
Use `vgame-growth-combat-conversion-map` for growth-module responsibility, combat attribute conversion, and formal gameplay verification mapping.
Use `vgame-outer-loop-system-map` for gacha/shop/task/sign-in/battle-pass/activity/mail/month-card outer-loop relationships, cadence, and monetization support.
Use `vgame-config-quality-audit` for read-only config QA, registered-source checks, ID/reference integrity, and delivery-gate audit reports.
Use `vgame-ui-prototype` for planning UI specifications, interactive HTML prototypes, rendered page/component screenshots, and UI-to-rule asset traceability.
Use `vgame-battle-content-map` for monster/boss/skill/buff/AI/wave/bullet/summon configuration mapping and battle content authoring pipeline.
Use `vgame-level-design-map` for level design, terrain layout, loop zones, moving platforms, spawn placement, encounter pacing, camera boundaries, level editor workflow, scene serialization, and Excel-to-Unity-scene relationships.
Use `vgame-battle-tuning-helper` for DPS, TTK, monster stat lookup, player power curve comparison, difficulty coefficient checks, survival analysis, and battle what-if tuning.
Use `vgame-tutorial-onboarding-map` for newbie guide systems, battle tutorial triggers, guide sequences/steps, SystemOpen feature gating, Unlock chains, guide editor workflow, onboarding timeline, and first-hour experience structure.
Use `vgame-version-release-map` for feature release states, version milestones, feature switches, AB tests, gray releases, hotfixes, and deprecated lifecycle tracking.
Use `vgame-player-progression-simulator` for day-by-day resource projection, growth milestone estimation, bottleneck detection, economy validation, and scenario comparison.

For gameplay understanding and project framing, this skill should usually be enough.

## References

- [references/project-control-workflow.md](references/project-control-workflow.md)
- [references/project-profile.md](references/project-profile.md)
- [references/evidence-map.md](references/evidence-map.md)
- [references/config-index.md](references/config-index.md)
- [references/delivery-gates.md](references/delivery-gates.md)
- [references/current-gameplay.md](references/current-gameplay.md)
- [references/character-kit-routing.md](references/character-kit-routing.md)
