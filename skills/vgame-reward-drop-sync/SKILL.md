---
name: vgame-reward-drop-sync
description: Use for Vgame reward implementation and validation across Drop and UIlevel source Excel configs, including first-clear rewards, repeat drops, fixed rewards, random weighted packages, DropId allocation, UI preview Reward/FirstReward fields, and logical Drop reference checks.
---

# Vgame Reward Drop Sync

Use this skill when reward design must become real Vgame configuration.

This is the project-specific replacement for generic Drop/UIlevel handling. It uses the live Vgame source paths and the logical `Drop` table defined by `__tables__.xlsx`.

## Load Order

1. Read `vgame-core-understanding` for project context.
2. Read `vgame-config-schema` when the task requires source-table discovery, schema confirmation, or export validation.
3. Read `senior-game-economy` when the task affects economy pacing, reward value, long-term supply, or infinite reward loops.
4. Read `references/drop-uilevel-rules.md` before editing or auditing Drop/UIlevel rewards.
5. Read `references/id-ranges-and-tables.md` before allocating new DropIds.
6. Read `references/validation.md` before reporting completion.

## Decision Flow

1. First-clear reward:
   Update the real Drop package, then update `UIlevel.FirstRewardDrop` and `UIlevel.FirstReward`.
2. Normal or repeat reward:
   Update the real Drop package, then update `UIlevel.FallRewardDrop` and `UIlevel.Reward`.
3. Three-star or high reward:
   Confirm local convention first, then update `ThreeStarRewardDrop` or `HighRewardDrop`.
4. Random weighted reward:
   Use multiple rows under one `DropId`; validate quantity ranges and weight design.
5. Preview-only change:
   Update only `Reward` or `FirstReward`; do not change Drop rows unless the real reward changes.

## Safety Rules

- Do not assume `Drop_dungeon.xlsx` is the only Drop source. `UIlevel` references the logical `Drop` table, which merges multiple Drop workbooks.
- Do not edit generated `server_json/drop.json` or `server_json/uilevel.json` as source.
- Do not replace unrelated rows sharing nearby IDs.
- Preserve the `ID` formula convention in Drop rows.
- Preserve unrelated UIlevel fields such as level type, vitality, plot, monster, lineup, and unlock columns.
- Report existing validation gaps instead of silently treating them as success.

### Formula Protection (Critical)

Drop_dungeon.xlsx 中 Col 2(ID)、Col 3(DropId)、Col 6(DropId2) 含有公式：

| 列 | 公式 | 含义 |
|---|---|---|
| Col 2 (ID) | `=ROW()+200000-4` | 行号自动生成唯一ID |
| Col 3 (DropId) | `=C<prev>+1` 等 | DropId 递增/偏移 |
| Col 6 (DropId2) | `=F<n>+3` 等 | 二级DropId偏移 |

**必须遵守：**
1. **绝不写入 Col 2/3/6** — 这些列由公式自动维护
2. **绝不插入或删除行** — ROW() 会自动调整，但其他相对引用可能错位
3. **只写入 Col 7 起的纯数据列** — DropType(7), DropMinNum(8), DropMaxNum(9), DropItem_id(11), DropItemNumMin(12), DropItemNumMax(13), DropWeight(14), ShowItemID(15), IsValid(16)
4. **写入前用 `data_only=False` 打开** — 保留所有公式原样
5. **需要新增 Drop 行时** → 不自动执行，输出手动操作指令：
   - 告知用户在哪一行后插入几行
   - 提供插入后需要填入的纯数据列值
   - 说明 ID/DropId 列公式会自动处理（用户只需复制上一行公式下拉）

UIlevel.xlsx 无公式，全部列可安全写入。

## Standard Workflow

1. Read the reward design source and identify item IDs, quantities, probability/weight, target LevelIds, and reward timing.
2. Locate the correct Drop source workbook from `__tables__.xlsx` and the ID range convention.
3. Inspect the target DropId package and UIlevel rows.
4. Prepare a config impact matrix.
5. Back up source workbooks before editing.
6. Edit Drop rows for the real reward package.
7. Edit UIlevel reference and preview fields.
8. Validate logical Drop references across every Drop source workbook.
9. Export and run checks when the user wants the change applied.

## Output Contract

For reward work, include:

- affected LevelIds and LevelTypes
- affected DropIds and source workbook
- first-clear/repeat/preview/random classification
- before/after reward rows
- validation result, including any project-level check not covered by current scripts
