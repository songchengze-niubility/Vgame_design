---
name: battle-tuning-framework
description: Generic framework for tuning battle math — damage formulas, DPS models, TTK estimation, survival analysis, difficulty assessment, stat scaling curves, and peer comparison methodology applicable to any RPG/action combat system.
---

# Battle Tuning Framework Skill

## Load Order
1. Read this SKILL.md for frameworks and methodology.
2. Read `references/peer-comparison-rules.md` for peer comparison protocol.
3. Identify the project's specific formula constants and stat tables.
4. Apply frameworks to calculate, validate, and compare.

## Scope
- Damage formula decomposition. DPS and TTK models.
- Survival analysis. Difficulty assessment criteria.
- Monster and player stat scaling curves.
- Peer comparison methodology.
- Mechanic value conversion to DPS-equivalent.

## 伤害公式框架 (Damage Formula Framework)

```
RawDmg = ATK * SkillMultiplier
DefReduction = DEF / (DEF + DefConstant)
PostDef = RawDmg * (1 - DefReduction) * (1 - PenetrationBypass excluded portion)
CritFactor = 1 + CritRate * (CritDmg - 1)
FinalDmg = PostDef * CritFactor * ElementBonus * FinalMultipliers
```

Key tuning knobs: DefConstant, CritDmg cap, penetration formula, final multiplier sources.

## DPS 计算模型 (DPS Calculation Model)

```
DPS = (TotalDamageInRotation + DOT + Summon + Proc) / RotationDuration
EffectiveDPS = DPS * Uptime * (1 - InterruptionLoss)
```

## TTK 估算方法 (TTK Estimation)

```
TTK = EnemyEffectiveHP / EffectiveDPS
EnemyEffectiveHP = HP / (1 - DefReduction_applied_to_enemy) [if enemy has armor]
```

## 生存分析模型 (Survival Analysis)

```
EHP = HP / (1 - DefReduction_of_player) + ShieldValue + HealPerSec * Duration
SurvivalTime = EHP / IncomingDPS
```

## 难度评估标准 (Difficulty Assessment Criteria)

| Rating | Condition |
|--------|-----------|
| Too Easy | TTK < 0.5 * ExpectedTime |
| Normal | 0.8 * Expected <= TTK <= 1.2 * Expected |
| Hard | TTK > 1.5 * Expected OR SurvivalTime < ClearTime |
| Overtuned | Player cannot survive one rotation |

## 怪物属性缩放模型 (Monster Stat Scaling)

- Base stats defined at reference level.
- Growth per level: linear or exponential segment by tier.
- Elite/Boss multipliers applied on top of base scaling.

## 玩家战力曲线 (Player Power Curve)

- Define expected stats at each progression milestone (e.g., chapter clear, rank threshold).
- Include gear, level, skill level, breakthrough, star contributions.
- Track both floor (F2P casual) and ceiling (whale) envelopes.

## 同行比较规则 (Peer Comparison Rules)

See `references/peer-comparison-rules.md` for full protocol. Summary:
1. Same role/archetype. 2. Same investment level. 3. Same scenario/enemy. 4. Transparent assumptions.

## 角色强度基准 (Character Strength Benchmarks by Role)

| Role | Primary Metric | Secondary Metric |
|------|---------------|-----------------|
| DPS | Damage per rotation | Burst window DPS |
| Tank | EHP * Aggro uptime | Party damage reduction contribution |
| Support | Buff uptime * buff value | Heal per second |

## 机制价值换算 (Mechanic Value Conversion)

- Shield → EHP gain → equivalent DPS time saved.
- Heal → sustain extension → effective DPS uptime gain.
- DOT → raw damage over full duration (apply DEF at target).
- Summon → summon DPS * uptime.
- Control (CC) → enemy DPS negated * CC duration.

## Standard Workflow
1. Establish formula constants for the project.
2. Build player power curve at key milestones.
3. Build monster stat curve aligned to content schedule.
4. For each character/encounter: calculate DPS, TTK, Survival.
5. Compare against benchmarks; flag outliers.
6. Run peer comparison when making strength claims.

## Output Contract
- Numeric results with full formula trace.
- Difficulty rating per scenario.
- Peer comparison table (if strength claim made).
- Identified outliers with recommended adjustment direction.
