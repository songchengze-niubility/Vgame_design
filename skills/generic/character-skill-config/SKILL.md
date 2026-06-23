---
name: character-skill-config
description: Generic methodology for configuring characters and their skill systems — covering character data models, stat scaling, skill data architecture, buff systems, cross-references, and editor workflows applicable to any RPG or action game.
---

# Character & Skill Configuration Skill

## Load Order
1. Read this SKILL.md for data models and patterns.
2. Identify the project's specific table schemas, editors, and serialization format.
3. Apply models when authoring or reviewing character/skill configurations.

## Scope
- Character definition model and stat scaling.
- Skill system data architecture (table → editor → runtime).
- Skill type taxonomy. Buff data model.
- Cross-reference patterns. Exclusive/signature weapon model.
- Skill editor workflow.

## 角色定义模型 (Character Definition Model)

```
Character {
  characterId, name, class/role, quality/rarity, faction/element,
  baseStats: { HP, ATK, DEF, SPD, CritRate, CritDmg, ... },
  growthCurveRef,
  skillSlots[]: { slotType, skillId },
  passiveSlots[]: { passiveId },
  signatureWeaponId (optional),
  modelAssetRef, voiceAssetRef
}
```

## 角色属性缩放模式 (Character Stat Scaling Patterns)

| Growth Axis | Mechanism | Typical Impact |
|-------------|-----------|---------------|
| Level | Base stat * level curve multiplier | Linear or soft-exponential |
| Breakthrough / Ascension | Unlock stat ceiling + bonus stats | Step function (discrete jumps) |
| Star / Constellation | Flat or % stat bonus per star | Moderate per star |
| Equipment | Additive and multiplicative stats from gear | Major (often largest source) |
| Skill level | Multiplier increase on skill values | Incremental per level |

## 技能系统数据模型 (Skill System Data Model)

```
Skill Table (config) → Skill Editor Asset (visual authoring) → Serialized Runtime Data
```

### Skill Table Entry
```
Skill {
  skillId, characterId, slotType, skillName,
  baseCooldown, resourceCost, castTime,
  levelScaling[]: { level, multiplier, extraEffect },
  buffApplyList[]: { buffId, chance, target },
  bulletSpawnList[]: { bulletId, spawnRule },
  conditionList[]: { conditionType, params }
}
```

## 技能类型分类 (Skill Types Taxonomy)

| Type | Characteristics |
|------|----------------|
| Normal Attack | Auto-chain, low cooldown, resource generator |
| Active Skill | Cooldown-gated, resource consumer, main damage/utility |
| Passive | Always active, conditional trigger, no player input |
| Ultimate | High cost/long charge, high impact, invulnerability frames |
| Talent / Trait | Permanent character modifier, unlocked via progression |
| Equipment Skill | Granted by weapon/artifact, replaceable |

## Buff 系统数据模型 (Buff System Data Model)

```
Buff {
  buffId, buffName, icon,
  effectType (statMod/DOT/HOT/shield/CC/flag/custom),
  effectParams: { stat, value, isPercent },
  stackRule (independent/refresh/addStack/replace),
  maxStacks, duration,
  removalConditions[]: (expire/dispel/hitCount/stateChange/custom),
  vfxRef, sfxRef
}
```

## 交叉引用模式 (Cross-Reference Patterns)

```
Character → SkillSlot[] → Skill
                           Skill → Buff[] (apply on hit/cast/condition)
                           Skill → Bullet[] (projectile/AOE spawns)
Character → PassiveSlot[] → Passive (special buff with permanent duration)
Character → SignatureWeapon → WeaponSkill (treated as equipment skill)
```

Validation: All referenced IDs must resolve. Circular buff references prohibited.

## 专属/签名武器模型 (Exclusive / Signature Weapon Model)

- Signature weapon has unique passive that synergizes with owner's kit.
- Data: `{ weaponId, ownerCharacterId, baseStats, passiveBuffId, refinementLevels[] }`.
- Non-owner can equip but passive is weaker or disabled.
- Refinement increases passive values (not base stats).

## 技能编辑器工作流 (Skill Editor Workflow)

1. **Node graph / timeline** — Visual authoring of skill sequence.
   - Nodes: animation, hit-box, VFX, SFX, buff-apply, bullet-spawn, branch.
2. **Parameter binding** — Connect level-scaling values from skill table.
3. **Preview** — Play skill in isolated test scene with dummy target.
4. **Serialize** — Export to runtime format (binary/JSON).
5. **Validate** — Check: missing refs, timing conflicts, infinite loops.
6. **Integration test** — Run skill in full battle context.

## Standard Workflow
1. Define character entry (ID, class, stats, growth curve).
2. Design skill set; create skill table entries per slot.
3. Author skill sequences in editor; bind buffs and bullets.
4. Configure buff entries with stacking/duration rules.
5. Run cross-reference validator (no orphans, no cycles).
6. Test in combat; verify damage, timing, visual feedback.

## Output Contract
- Character config with all fields populated and references valid.
- Skill table entries with level scaling and effect lists complete.
- Buff entries with clear stacking and removal rules.
- Cross-reference integrity report: zero broken links.
- Editor asset exported and runtime-loadable.
