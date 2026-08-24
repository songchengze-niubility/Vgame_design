---
name: outer-loop-progression-pacing
description: Use when designing or reviewing outer-loop level progression, feature unlock schedules, reward-per-level tables, daily income pacing, upgrade thresholds, idle/dispatch/economy systems, or Excel/MD numerical plans where unlock content, capacity, subsidy/supply, price modifiers, event rewards, income, and progression time must stay synchronized.
---

# Outer Loop Progression Pacing

Use this skill to keep outer-loop progression tables readable, tunable, and testable. The core rule is:

`A level table is a player cognition pacing table, not a reward pile.`

## Workflow

1. Define the loop purpose.
   - Identify whether the system is retention, economy, social, shop support, monetization support, or combat verification support.
   - Name the loop currency, real rewards, virtual-only goods, daily cadence, reset time, and maximum meaningful completion horizon.
   - For Vgame tasks, read `vgame-core-understanding` first and treat outer-loop systems as support loops unless the source design says otherwise.
   - Route Vgame pacing facts through `knowledge-base/numerical/` and cite the selected atom/source locator; external workbooks are exact-value evidence, not a second planning authority.

2. Define the unlock atom before filling levels.
   - Count each of these as one unlock atom: new feature, new station/area, new shop tier, new goods group, capacity increase, daily supply/subsidy increase, price modifier, probability modifier, reward quality tier, automation slot, event rule, milestone title.
   - Do not allow one level to contain two unlock atoms unless the user explicitly asks for bundle rewards.
   - If a new content node also needs a numerical boost, place the numerical boost on a later level.

3. Separate state, unlock, income, and experience.
   - State columns describe current values after reaching the level: capacity, supply, modifiers, unlocked content count.
   - Unlock columns describe the single thing that changed this level.
   - Income is what the player receives or can spend today.
   - Progression experience is the value that advances the system level.
   - Do not assume all income should count as progression experience.

4. Build the level table.
   - Use one explicit column named like `本级唯一解锁项` or `唯一解锁类型`.
   - Use separate current-state columns such as `载货量`, `每日补给`, `价格增益`, `已开放站点`.
   - Make each row independently audit-able: the row should show both current state and the only new unlock.
   - Prefer clean rhythm over mathematical smoothness. Example pattern: content unlock -> capacity -> supply -> content unlock -> capacity -> modifier.

5. Recalculate income and upgrade time after every reward rearrangement.
   - If capacity, content breadth, price modifiers, or income cadence changes, recalculate daily profit.
   - If daily profit changes, recalculate cumulative thresholds or expected days.
   - Never only move unlock text in the table and leave old upgrade-time numbers untouched.

6. Verify the design.
   - Check each level has exactly one unlock atom.
   - Check content unlock rows do not also increase capacity, supply, or price modifiers.
   - Check income and progression experience are explicitly separated.
   - Check target completion time still lands where intended.
   - Check high-value real rewards have caps or low-frequency placement.

## Recommended Tables

For MD or Excel delivery, use these sheets or sections:

| Table | Purpose |
|---|---|
| Global Parameters | Daily cadence, reset time, initial currency, price/probability assumptions |
| Content Unlocks | Areas, goods, shop tiers, features, unlock level |
| Level Schedule | Level, cumulative experience, current state, one unlock item |
| Unlock Detail | Level, unlock type, capacity change, supply change, modifier change, content unlock |
| Income Simulation | Daily base income, support income, event income, total income |
| Upgrade Simulation | Target day, cumulative threshold, expected day reached, key unlock |
| Formula Notes | Assumptions and reusable formulas |
| Pending Items | Rewards, IDs, caps, shop prices, unresolved economy risks |

## Calculation Rules

Use formulas or reproducible simulation whenever the deliverable is a spreadsheet.

Common structure:

```text
daily_total_income = base_loop_profit + fixed_supply + event_currency_expectation
progression_exp = allowed_exp_source_only
next_level_day = first day cumulative_exp >= level_threshold
```

Recommended separation:

| Value | Counts As Player Income | Counts As Level Experience |
|---|---:|---:|
| Core loop positive profit | Yes | Usually yes |
| Fixed daily supply/subsidy | Yes | Usually no |
| Random event currency | Yes | Usually no |
| Random event real rewards | Yes | No |
| Shop exchange rewards | Yes | No, unless designed as a separate spend loop |

When the target graduation time is fixed:

1. Simulate daily experience under the current level state.
2. Pick target reach days for each key level.
3. Set cumulative thresholds inside the experience window for those days.
4. Re-simulate to confirm all levels land on the intended days.

## Design Heuristics

- Use content unlocks to expand choice space.
- Use capacity or slot increases to raise earning power.
- Use fixed supply to protect daily startup, not to accelerate progression.
- Use price or efficiency modifiers as milestone rewards.
- Keep high-sensitivity rewards outside infinite uncapped loops.
- Prefer a few visible milestones over many tiny invisible increments.
- Put the rule in the table structure, not only in prose. A column like `唯一解锁类型` prevents accidental reward bundling.

## Review Checklist

Before calling the design ready:

- Every level has one and only one unlock atom.
- New content rows do not also give capacity/supply/price growth.
- The same term is used consistently across MD and Excel.
- Daily income and level experience use different columns or formulas.
- Thresholds were recalculated after the latest level reward changes.
- Key milestone days are stated with concrete day numbers.
- Spreadsheet formulas recalculate without `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, or `#NAME?`.
