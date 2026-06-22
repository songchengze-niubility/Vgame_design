---
name: vgame-version-release-map
description: Use for Vgame version milestone tracking, feature release status, feature switches (SystemOpen/功能开关), AB test mapping, gray release tracking, hotfix history, deprecated feature lifecycle, and build/branch/environment mapping. Trigger when asked which features are live/gray/pending/deprecated, what version introduced a feature, how SystemOpen controls runtime availability, which features are behind AB flags, what the release cadence looks like, or how to plan content for an upcoming version.
---

# Vgame Version Release Map

Use this skill to answer: what is the current release state of Vgame features, which version introduced/deprecated/modified a feature, how feature switches control availability, and how versions relate to content milestones.

This is a project mapping and tracking skill. It is read-only by default and does not modify config or release systems.

## Load Order

1. Read `vgame-core-understanding` first for project identity, formal gameplay structure, and deprecated features.
2. Read `references/version-milestone-overview.md` for the version model, cadence, and naming conventions.
3. Read `references/feature-switch-map.md` when the request involves SystemOpen, feature flags, AB testing, or runtime gating.
4. Read `references/release-status-registry.md` when the request asks the current state (live/gray/pending/deprecated) of specific features.
5. Read `references/hotfix-and-rollback-log.md` when the request involves hotfix history, rollback events, or emergency changes.
6. Use `vgame-level-progression-map` for how SystemOpen/Unlock gates relate to level progression.
7. Use `vgame-config-schema` for how feature configs are exported per version/environment.
8. Use `vgame-outer-loop-system-map` for activity/season timing alignment with versions.
9. Use `vgame-config-quality-audit` for pre-release config validation.

## Scope

Covered in v1:

- version naming convention and milestone model
- feature release states: development / internal-test / gray / live / deprecated / removed
- SystemOpen / feature-flag mapping: which config table controls feature availability
- feature-to-version assignment: which features ship in which version
- AB test registry: active experiments, traffic allocation, observation metrics
- gray release tracking: staged rollout percentages, regions, user cohorts
- hotfix and emergency rollback log
- deprecated feature lifecycle: when deprecated, migration path, removal timeline
- build/branch/environment mapping: dev / staging / production
- content milestone planning: which content (levels, characters, events) targets which version

Not covered directly:

- exact config table schema (route to `vgame-config-schema`)
- exact reward values or economy impact of a version (route to `vgame-economy-source-map` or `senior-game-economy`)
- exact unlock/progression chain details (route to `vgame-level-progression-map`)
- code implementation of feature switches (route to project code reading)

## Core Concepts

### Version Model

```
Major.Minor.Patch[-Hotfix]
例: 1.2.0 / 1.2.1-hotfix1

Major: 大版本（核心玩法/商业模型变动）
Minor: 常规版本（新功能/新内容/系统迭代）
Patch: 修复版本（bug修复/数值调整）
Hotfix: 紧急修复（线上崩溃/严重bug）
```

### Feature Release Lifecycle

```
[PLAN] → [DEV] → [INTERNAL_TEST] → [GRAY] → [LIVE] → [MAINTAIN]
                                                          ↓
                                                    [DEPRECATED] → [REMOVED]
```

### Feature Switch Layers

| 层级 | 控制方式 | 说明 |
|---|---|---|
| Config层 | SystemOpen表 | 按玩家等级/主线进度开放 |
| Server层 | 功能开关/AB Flag | 按服务器/用户分组控制 |
| Client层 | 版本号判断 | 客户端版本不够则不显示入口 |
| 活动层 | Activity表时间范围 | 按活动周期开关 |

## Standard Workflow

1. Identify whether the user asks about: a specific feature's release state, a version's content scope, a feature switch mechanism, or a rollback/hotfix event.
2. Locate the relevant version/feature from references.
3. Map the feature to its switch mechanism (SystemOpen / server flag / version gate / activity time).
4. Identify cross-system impacts (e.g., new feature needs new Drop/UIlevel/Task configs).
5. Separate confirmed release facts from planned/pending items.
6. Route config details, economy impacts, and progression chains to downstream skills.

## Output Contract

For version/release analysis, include:

- `Feature/Content`: what is being tracked.
- `Version`: target or actual version number.
- `Release state`: PLAN / DEV / INTERNAL_TEST / GRAY / LIVE / DEPRECATED / REMOVED.
- `Switch mechanism`: how availability is controlled at runtime.
- `Config impact`: which config tables are added/modified for this feature.
- `Dependencies`: what other features or configs must be in place first.
- `Risk`: rollback complexity, data migration needs, player impact if reverted.
- `Evidence`: source of truth for this claim (config file, meeting notes, code branch).

Use `待确认` for any release state or version assignment not directly observed from project sources.

## Boundaries

- Do not invent version numbers or release dates not found in project evidence.
- Do not assume a feature is live just because config exists; check SystemOpen and server flags.
- Do not assume deprecated means removed; some deprecated features still have runtime code/config.
- Treat `vgame-core-understanding` deprecated list as the canonical deprecated source.
- For features in GRAY state, always note the rollout scope (%, regions, cohorts) if known.
