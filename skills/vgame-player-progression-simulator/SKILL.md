---
name: vgame-player-progression-simulator
description: Use for Vgame player progression simulation, resource accumulation modeling, day-by-day income/expense projection, growth milestone estimation, gacha expected pulls, stamina budget planning, bottleneck detection, economy validation, and what-if scenario comparison. Trigger when asked how long it takes to reach a growth milestone, how many days to max a character/weapon, what the daily/weekly resource income looks like, where players will get stuck, whether a reward change breaks the economy curve, or when comparing different economy scenarios.
---

# Vgame Player Progression Simulator

Use this skill to answer: given a set of player behavior assumptions, what does the resource accumulation and growth progression look like over N days, and where are the bottlenecks.

This is an **executable** skill. It provides both documentation for manual reasoning and Python scripts for quantitative simulation.

## Load Order

1. Read `vgame-core-understanding` first for project identity and formal gameplay structure.
2. Read `references/simulation-model-overview.md` for the simulation framework and assumptions.
3. Read `references/daily-income-model.md` for the per-source daily resource income parameters.
4. Read `references/growth-cost-model.md` for the growth system cost curves (character, weapon, equipment).
5. Read `references/scenario-templates.md` for pre-built simulation scenarios (F2P / light spender / dolphin / whale).
6. Run `scripts/simulate_progression.py` when quantitative output is needed.
7. Use `vgame-economy-source-map` for exact source/sink tracing when a source is unclear.
8. Use `vgame-growth-combat-conversion-map` for understanding what reaching a milestone means in combat terms.
9. Use `vgame-reward-drop-sync` for exact reward package content.
10. Use `senior-game-economy` for value judgment and risk assessment on simulation results.
11. Use `game-numerical-analysis` for deeper mathematical modeling beyond this simulation scope.

## Scope

Covered in v1:

- day-by-day resource accumulation simulation (gold, diamonds, EXP items, gacha tickets, materials)
- stamina budget: daily stamina income vs. spending allocation across content
- growth milestone estimation: days to Lv30/40/50/60 for character, weapon
- gacha simulation: expected pulls to SSR, diamond/ticket budget over time
- bottleneck detection: which resource runs out first, where players stall
- scenario comparison: F2P vs. spender progression curves
- what-if analysis: "if we increase mainline gold by 20%, how does it change day-14 progression?"
- economic validation: does planned income match planned consumption at key milestones?

Not covered directly:

- exact config editing (route to relevant config skills)
- combat balance or DPS simulation (route to `game-numerical-analysis`)
- detailed source table verification (route to `vgame-economy-source-map`)
- value/pricing judgment (route to `senior-game-economy`)

## Simulation Framework

### Core Loop

```
For each day (day 1 to day N):
  1. Calculate daily income from all sources
  2. Apply player behavior (spend stamina, do dailies, etc.)
  3. Allocate resources to growth priorities
  4. Track cumulative totals and milestone progress
  5. Record bottlenecks (resource insufficient for next growth step)
```

### Key Parameters

| Parameter | Description | Source |
|---|---|---|
| Daily stamina | Base + regen + purchases | 经济框架 |
| Stamina allocation | % to main / resource / equipment / other | Player behavior model |
| Daily task rewards | Gold, EXP, diamonds, tickets | 任务表 |
| Mainline first-clear | One-time resources per stage | 经济框架 配置页-主线副本 |
| Resource dungeon | Per-run rewards × daily runs | 经济框架 资源副本 |
| Sign-in | Daily cumulative | 签到表 |
| Battle pass | Daily/weekly progress | 通行证 |
| Shop refresh | Available purchases per cycle | 商店表 |
| Gacha budget | Diamond + ticket allocation | Player choice |
| Activity events | Bonus resources during events | Activity duration model |

### Growth Priority Model

Default priority (can be customized):
1. Main character to recommended level (avoid being stuck on mainline)
2. Team characters to functional level
3. Signature weapon to match character level
4. Equipment/accessories as materials allow
5. Star map and star-up as materials accumulate

## Standard Workflow

1. Identify what the user wants to simulate (milestone? comparison? validation? bottleneck?).
2. Confirm or assume player behavior parameters (F2P? spender? active? casual?).
3. Load income and cost models from references.
4. If quantitative output needed → run `scripts/simulate_progression.py` with parameters.
5. If qualitative reasoning → use references to estimate ranges.
6. Present results: timeline, bottlenecks, comparisons, recommendations.
7. Route deeper questions to downstream skills.

## Output Contract

For simulation results, include:

- `Scenario`: player profile and behavior assumptions.
- `Timeline`: key milestone dates (day N to reach X).
- `Daily income summary`: resource income breakdown by source.
- `Bottlenecks`: first resource to run out, stall points.
- `Comparison`: if multiple scenarios, side-by-side differences.
- `Validation`: does income match expected consumption at key points?
- `Risks`: assumptions that could be wrong, sensitivity to parameter changes.
- `Recommendations`: adjustments to improve player experience if bottlenecks found.

Use `待确认` for any parameter not sourced from actual config/economy framework.

## Script Usage

### Basic simulation
```bash
python scripts/simulate_progression.py --days 30 --scenario f2p
```

### Compare scenarios
```bash
python scripts/simulate_progression.py --days 60 --scenario f2p,light_spender --compare
```

### What-if analysis
```bash
python scripts/simulate_progression.py --days 30 --scenario f2p --override "mainline_gold_multiplier=1.2"
```

## Boundaries

- Simulation results are estimates based on model parameters, not exact predictions.
- Always state assumptions clearly; different behavior patterns produce different results.
- Do not present simulation output as definitive proof; use it as a planning and validation tool.
- Update parameters when economy framework changes (link to source workbook).
- For live game validation, compare simulation against actual player data if available.
