---
name: player-progression-simulator
description: Generic framework for simulating player progression day-by-day — modeling income sources, growth costs, bottleneck detection, and what-if analysis applicable to any RPG or gacha game economy.
---

# Player Progression Simulator Skill

## Load Order
1. Read this SKILL.md for simulation framework and methodology.
2. Identify the project's specific income sources and cost tables.
3. Build or adapt the day-by-day loop for the target economy.

## Scope
- Day-by-day simulation loop structure.
- Player profile archetypes.
- Income model and cost model templates.
- Bottleneck detection. Scenario comparison.
- What-if analysis patterns. Excel auto-read.
- Output format standards.

## 模拟框架 (Simulation Framework)

```
For each day in [Day 1 … Day N]:
  1. INCOME  — Calculate all resource gains for the day
  2. SPEND   — Apply optimal or prescribed spending strategy
  3. GROW    — Update character/account stats based on spending
  4. RECORD  — Log milestones, resource balances, power level
```

Loop terminates at target day count or when target milestone is reached.

## 玩家画像模型 (Player Profile Archetypes)

| Profile | Daily Play Time | Spending | Behavior |
|---------|----------------|----------|----------|
| F2P Casual | 15–30 min | $0 | Misses some daily tasks, no optimization |
| F2P Active | 60–90 min | $0 | Completes all dailies, optimizes spending |
| Light Spender (Goldfish) | 60 min | Monthly pass only | Completes dailies + pass rewards |
| Medium Spender (Dolphin) | 60–90 min | Monthly + battle pass + occasional top-up | Targets specific banners |
| Whale | 90+ min | Unlimited | Maxes all available content immediately |

## 每日收入模型模板 (Daily Income Model Template)

```
Sources:
- Main story progression (one-time, converted to daily amortization)
- Daily dungeons / stamina spend
- Daily/weekly tasks and achievements
- Sign-in calendar
- Shop refreshes (free currency section)
- Gacha pity / spark system contributions
- Events (amortized over event duration)
- Guild/social rewards
- Mail / compensation / codes
```

For each source: define `{resource_type, amount, frequency, unlock_condition}`.

## 成长消耗模型模板 (Growth Cost Model Template)

```
Growth axes:
- Character level (EXP + currency per level)
- Breakthrough / Ascension (materials + currency per tier)
- Star / Constellation (duplicate currency or universal shards)
- Skill level (books + boss materials per level)
- Equipment level + refinement
- Passive / talent tree (generic + specific materials)
```

For each axis: define `{level_range, material_list[], currency_cost, time_gate}`.

## 瓶颈检测方法论 (Bottleneck Detection)

A bottleneck exists when:
1. A resource is the **binding constraint** preventing the next growth milestone.
2. The player has excess of other resources but cannot progress.

Detection: At each day, identify which resource has the highest `(required - owned) / daily_income` ratio.

## 场景对比框架 (Scenario Comparison Framework)

- **Baseline**: Current live economy parameters.
- **Variant A/B/C**: Modified parameters (e.g., +20% dungeon drops, new event, cost reduction).
- Compare: Days to milestone, resource surplus/deficit, bottleneck shift.

## What-If 分析模式 (What-If Analysis Patterns)

- "What if we add a new income source worth X per day?"
- "What if we reduce cost of breakthrough tier 5 by 30%?"
- "What if a new character is released requiring new materials?"
- For each: re-run simulation, compare milestone dates and bottlenecks.

## Excel 自动读取模式 (Excel Auto-Read Patterns)

- Use library (openpyxl, pandas, or equivalent) to read planning workbooks.
- Locate data by header row matching, not hard-coded cell positions.
- Validate expected columns exist before processing.
- Handle merged cells and empty rows gracefully.
- Never modify source workbooks; read-only access.

## Standard Workflow
1. Define player profile(s) to simulate.
2. Build income model from project's economy tables.
3. Build cost model from project's growth tables.
4. Run day-by-day loop for target duration (e.g., 90 days).
5. Record milestones, bottlenecks, and daily snapshots.
6. Compare scenarios if evaluating a design change.

## Output Contract
- **Milestones**: Table showing day reached for each growth milestone per profile.
- **Bottlenecks**: Ranked list of binding resources at key checkpoints.
- **Comparisons**: Delta table between baseline and variant scenarios.
- **Daily snapshot** (optional): CSV/chart of resource balances over time.
- All assumptions and input parameters documented explicitly.
