---
name: vgame-battle-tuning-helper
description: Use for Vgame battle difficulty tuning, character strength validation, benchmark-calibrated character comparison, full-max all-character visual quantification, peer comparison, role contribution benchmarks, standard validation scenarios, DPS calculation, TTK estimation, survival analysis, monster stat lookup by level, player power curve comparison, difficulty coefficient adjustment, mechanic value conversion, and what-if combat scenarios. Trigger when asked how long a player takes to kill a boss at stage X, whether a monster level is too hard/easy, what DPS a player needs to clear in time, whether a character is too strong or weak, how all characters compare in a quantified table, how characters compare against same-role peers or high-confidence benchmark characters, how attack/defense/support roles should be benchmarked, how changing a coefficient affects difficulty, or comparing expected vs actual combat performance at any progression point.
---

# Vgame Battle Tuning Helper

Use this skill to answer: given a player's progression stage and a monster/boss config, what does the combat math predict for DPS, TTK, survival, role contribution, and difficulty feel.

This is an executable project skill. It can run `scripts/battle_tuning.py` for quantitative calculations. It is read-only by default and does not edit game config tables.

## Load Order

1. Read `vgame-core-understanding` for project identity: Vgame is a 5-character squad progression-driven parkour combat shooter.
2. Read `references/combat-math-reference.md` for damage formula, multiplier zones, DPS, TTK, and survival models.
3. Read `references/monster-scaling-reference.md` for monster stat scaling by level and type.
4. Read `references/difficulty-line-reference.md` for gameplay-to-monster-level mappings.
5. Read `references/peer-comparison-rules.md` before giving any final character strength conclusion.
6. Read `references/role-strength-benchmarks.md` when comparing attack, defense, support, or mixed-role character strength.
7. Read `references/character-benchmark-set.md` when comparing character strength, explaining high/low confidence, or using benchmark-calibrated conclusions.
8. Read `references/standard-validation-scenarios.md` when validating a character, skill, equipment line, or team against formal gameplay modes.
9. Read `references/mechanic-value-conversion.md` when a kit includes shields, healing, summons, DOT, control, energy, cooldown, probability, or other non-direct-DPS mechanics.
10. Read `references/character-strength-report-template.md` when producing a full character strength report.
11. Read `references/character-fullmax-quantification.md` and run `scripts/character_fullmax_quant.py` when the user asks for all-character quantification, visual tables, full-max rankings, or concrete tuning priorities.
12. Run `scripts/battle_tuning.py` for quantitative calculations when stage, monster level, mode, floor, or coefficient input is available.
13. Use `vgame-character-kit-design-map` for character design intent and kit evidence.
14. Use `vgame-hero-skill-config-map` for exact Hero/Skill/Buff/exclusive-weapon config and runtime skill serialization.
15. Use `vgame-battle-content-map` for monster, boss, skill, buff, bullet, summon, AI, and battle-content config evidence.
16. Use `vgame-growth-combat-conversion-map` for how player growth converts into combat performance.
17. Use `vgame-level-progression-map` for stage, chapter, unlock, LevelId, LevelType, and gameplay-opening context.
18. Use `game-numerical-analysis` for long-term numerical experience, progression curve, economy pressure, and cross-system audits.

## Scope

Covered:

- monster stat lookup by level: HP, ATK, DEF, reduction, Boss/mob coefficients
- player expected power by stage: ATK, DEF, DPS, crit, damage bonus, reduction
- DPS calculation with the available multiplier chain
- TTK estimation: player to monster/Boss
- survival analysis: monster/Boss to player
- Boss control-immunity convention: control value is 0 in Boss scenarios; control score only represents non-Boss mob, wave, and PVPVE value
- difficulty coefficient comparison: HP coefficient and ATK coefficient by mode
- what-if scenarios, such as monster level, HP coefficient, or ATK coefficient changes
- cross-gameplay difficulty comparison: mainline, tower, mythic dungeon, infinite challenge
- peer comparison rules for same-role, same-investment, same-scenario character strength conclusions
- benchmark-calibrated character comparison using high-confidence anchors
- full-max all-character visual quantification workbook generation
- basic-attack loop approximation for attack-speed windows, extra shots after N basic attacks, basic-attack defense ignore, and basic-attack energy loops
- contextual percentage attribution for healing, shields, team buffs, and enemy vulnerability/defense-down so self buffs and raw damage coefficients are not counted as support/debuff value
- role contribution benchmarks for attack, defense, support, and mixed-role characters
- standard validation scenarios across mainline, Boss, resource dungeon, travel-ticket dungeon, mapping-equipment dungeon, infinite challenge, arena PVPVE, tower, and mythic dungeon
- first-pass conversion rules for shields, healing, summons, DOT, control, energy, cooldown, and probability mechanics
- character strength report structure for design review and tuning handoff

Not covered directly:

- exact skill rotation optimization when runtime behavior is unknown
- exact Buff uptime simulation without config/runtime evidence
- exact DOT duration, hit frequency, stack cap, and coefficient-modifier simulation without SkillData/runtime evidence
- complete multi-target or AOE battlefield simulation
- treating visual quantification scores as final runtime DPS without SkillData/runtime validation
- final balance approval without real config and scenario evidence
- final character strength ranking without peer comparison evidence
- actual config table editing

## Standard Workflow

1. Identify the validation target: stage difficulty, monster level, character, skill, equipment line, or team.
2. Gather context: gameplay mode, stage/floor/wave, player progression, monster level, role, and expected clear time.
3. If the target is a character or kit, classify role, choose peer comparison conditions, and read the role benchmark.
4. If the kit has non-direct-DPS mechanics, convert them into first-pass value assumptions and mark assumptions clearly.
5. If the target is a character, compare both against same-role peers and the high-confidence benchmark set when available.
6. If the user asks for all-character quantification or visual comparison, run `character_fullmax_quant.py` and report the generated workbook plus key outliers.
7. Run `battle_tuning.py` when a quantitative scenario is available.
8. Compare predicted TTK, survival, DPS, and role contribution against same-role peers, benchmark characters, and the expected scenario.
9. Separate observed evidence, assumptions, and unresolved config/runtime questions.
10. Route unresolved design, config, growth, economy, or long-term experience questions to the appropriate downstream skill.

## Output Contract

For battle tuning or character strength validation, include:

- `Context`: gameplay mode, stage/floor/wave, player level, monster level, role, and scenario.
- `Evidence`: source sheet, config file, script result, design workbook, or runtime/config evidence used.
- `Player stats`: ATK, DEF, DPS, crit, damage bonus, reduction, or current assumptions.
- `Monster stats`: HP, ATK, DEF, reduction, type, and coefficients.
- `Combat prediction`: TTK, survival time, DPS, and clear-time comparison.
- `Role benchmark`: expected contribution band for the character's role and validation context.
- `High-confidence benchmark`: benchmark character, benchmark delta, and confidence if available.
- `Peer comparison`: same-role/same-investment/same-scenario comparison group, or a clear statement that only single-character risk can be judged.
- `Visual quantification`: generated workbook/summary path when running full-max all-character quantification, including color-coded same-group deviation cells.
- `Scenario coverage`: standard scenarios checked and pending.
- `Mechanic conversion`: how non-direct-DPS mechanics were approximated, including Boss control immunity when control appears.
- `Difficulty assessment`: easy, normal, hard, extreme, or evidence-insufficient.
- `Adjustment suggestions`: coefficient, cooldown, duration, trigger rate, cap, or role-scope changes.
- `Unknowns`: missing config, runtime, formula, or live-test evidence.

## Script Usage

```bash
# Query monster level 50 stats
python battle_tuning.py --monster-level 50

# Query mainline stage 30 expectation
python battle_tuning.py --stage 30

# Compare stage 50 player against monster level 100
python battle_tuning.py --stage 50 --monster-level 100

# What-if: monster HP coefficient becomes 1.5
python battle_tuning.py --stage 30 --hp-coeff 1.5

# Query mythic dungeon layer 10 approximation
python battle_tuning.py --mode mythic --floor 10

# Query tower floor 50 approximation
python battle_tuning.py --mode tower --floor 50

# Generate full-max all-character quantification workbook
python character_fullmax_quant.py --config-root ${VGAME_ROOT}\Config\GameConfig\Datas --output-dir ${VGAME_ROOT}\codex_output
```

## References

- [references/combat-math-reference.md](references/combat-math-reference.md)
- [references/monster-scaling-reference.md](references/monster-scaling-reference.md)
- [references/difficulty-line-reference.md](references/difficulty-line-reference.md)
- [references/peer-comparison-rules.md](references/peer-comparison-rules.md)
- [references/role-strength-benchmarks.md](references/role-strength-benchmarks.md)
- [references/character-benchmark-set.md](references/character-benchmark-set.md)
- [references/standard-validation-scenarios.md](references/standard-validation-scenarios.md)
- [references/mechanic-value-conversion.md](references/mechanic-value-conversion.md)
- [references/character-strength-report-template.md](references/character-strength-report-template.md)
- [references/character-fullmax-quantification.md](references/character-fullmax-quantification.md)
