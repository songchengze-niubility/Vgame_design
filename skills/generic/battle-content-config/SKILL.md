---
name: battle-content-config
description: Generic methodology for configuring battle content layers — from level structure down to individual entity skills, buffs, bullets, and AI behaviors. Provides frameworks and checklists applicable to any action/RPG combat system.
---

# Battle Content Configuration Skill

## Load Order
1. Read this SKILL.md for methodology and checklists.
2. Identify the project's specific table schemas and editor tooling.
3. Apply the layer model top-down when authoring new content.

## Scope
- Battle content layer decomposition and cross-references.
- Monster, boss, elite configuration methodology.
- Skill, buff, bullet, AI architecture patterns.
- Authoring pipeline from editor to runtime.

## 内容层级模型 (Content Layer Model)

```
Level / Stage
  └─ Wave (spawn timing, conditions)
       └─ Entity (monster/boss/elite instance)
            ├─ Stat Block (HP, ATK, DEF, speed…)
            ├─ Skill Set (references to skill table)
            │    ├─ Timeline (action clips, events)
            │    ├─ Conditions (trigger rules)
            │    └─ Bullet/Projectile/Summon refs
            ├─ Buff Slots (passive/on-hit/on-spawn)
            └─ AI Profile (behavior tree or state machine ref)
```

## 怪物/Boss/精英配置方法论 (Monster Configuration Methodology)

1. **Base template** — define archetype (melee, ranged, support, boss phase).
2. **Stat derivation** — inherit from level-curve formula; override only exceptional values.
3. **Skill assignment** — reference shared skill pool; boss-exclusive skills marked clearly.
4. **AI binding** — assign behavior profile; difficulty variants share base tree with parameter overrides.
5. **Visual/audio cue** — ensure every dangerous skill has a telegraph window.

## 技能系统架构 (Skill System Architecture Patterns)

| Component | Purpose |
|-----------|---------|
| Timeline | Ordered sequence of action clips with frame data |
| Action Clip | Atomic unit (animation, hit-box, VFX, SFX) |
| Event | Point-in-time trigger (spawn bullet, apply buff, camera shake) |
| Condition | Gate logic (cooldown, resource, state, distance) |

## Buff 系统模式 (Buff System Patterns)

- **Effect types**: stat modifier, DOT, HOT, shield, CC, special flag.
- **Stacking rules**: independent, refresh duration, add stack count, replace.
- **Duration model**: timed, permanent-until-removed, charge-based.
- **Removal conditions**: expire, dispel, on-hit-count, on-state-change.

## 弹道/召唤物 (Bullet / Projectile / Summon)

- Define trajectory type (linear, homing, arc, chain).
- On-hit payload (damage instance, buff apply, knockback).
- Lifetime and max-hit-count.
- Summon entities reuse the entity config model with limited AI.

## AI/行为配置 (AI / Behavior Patterns)

- Behavior Tree or Hierarchical State Machine.
- Standard nodes: patrol, chase, attack, flee, idle, phase-transition.
- Parameters exposed for difficulty tuning (aggression, cooldown multiplier).

## 交叉引用关系 (Cross-Reference Map)

```
Monster → SkillSet[] → Skill → Buff[], Bullet[]
                       Skill → Condition[]
Level   → Wave[]     → EntitySpawn → Monster + overrides
```

## 作战内容创作流水线 (Authoring Pipeline)

1. **Editor** — visual skill/AI editor; WYSIWYG timeline.
2. **Serialize** — export to config tables (JSON/binary/Excel).
3. **Validate** — automated checks (missing refs, orphan buffs, cycle detection).
4. **Runtime** — engine loads serialized data; hot-reload in dev builds.

## Standard Workflow
1. Define level/wave structure.
2. Configure entities with stat blocks and AI profiles.
3. Author skills using timeline editor; attach buffs and bullets.
4. Run cross-reference validator.
5. Playtest; iterate on AI parameters and skill timing.

## Output Contract
- Completed entity configs with no broken references.
- Skill timelines with frame-accurate hit windows.
- AI profiles parameterized for difficulty scaling.
- Validation report: zero errors, warnings listed.
