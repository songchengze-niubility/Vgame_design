# Skill & Buff Config Map

## 技能系统架构

### 技能配置层级

```
Skill（技能定义）
├─ SkillLine（技能执行线）
│  └─ SkillActionClip（动作片段）
│     ├─ DamageEffect（伤害效果）
│     ├─ BuffEffect（施加Buff）
│     ├─ BulletSpawn（发射子弹）
│     ├─ SummonSpawn（召唤实体）
│     ├─ Movement（位移效果）
│     └─ VFX/SFX（视觉/音效反馈）
└─ SkillCondition（释放条件）
   ├─ Cooldown（冷却）
   ├─ Energy/Resource（资源消耗）
   ├─ Range（距离判断）
   └─ State（状态限制）
```

### 技能表关键字段（待确认精确字段名）

| 字段 | 说明 |
|---|---|
| SkillId | 技能唯一ID |
| SkillName | 技能名 |
| SkillType | 普攻/主动/被动/终结技/连招 |
| Owner | 谁拥有这个技能（Monster/Player） |
| SkillLine | 执行线配置（时间轴） |
| Cooldown | 冷却时间 |
| CastCondition | 释放条件 |
| TargetType | 目标选择方式 |
| Range | 有效范围 |
| Priority | AI优先级（怪物用） |

### SkillActionClip

ActionClip 是技能的最小执行单元，在时间轴上按帧触发：

| 时间点 | 动作类型 | 配置内容 |
|---|---|---|
| 前摇帧 | Animation | 播放动画 |
| 命中帧 | DamageEffect | 造成伤害 |
| 命中帧 | BuffApply | 施加Buff |
| 命中帧 | BulletSpawn | 发射子弹 |
| 后摇帧 | Recovery | 恢复可操作 |

### 已知 Runtime 映射

| 配置 | Runtime | 文件线索 |
|---|---|---|
| Skill | `SkillInstance` | SkillInstance.cs |
| SkillLine | `SkillLine` | SkillLine.cs |
| ActionClip | `SkillActionClip` | SkillActionBase.cs |
| DamageEffect | `DamageEffectRuntime` | DamageEffect.cs |

从代码堆栈可知：
- `SkillInstance.Tick` → `SkillLine.Tick` → `SkillActionClip.Execute` → `DamageEffectRuntime.Execute`
- `DamageEffectRuntime.TryCastDamage` → `DamageUtility.CastDamage` → `DamageUtility.Calculate`

---

## Buff 系统架构

### Buff 配置层级

```
Buff（Buff定义）
├─ BuffEffect（Buff效果，可多个）
│  ├─ AttributeModify（属性修改）
│  ├─ DamageOverTime（持续伤害）
│  ├─ HealOverTime（持续治疗）
│  ├─ Shield（护盾）
│  ├─ Control（控制：眩晕/冻结/击退）
│  ├─ Mark（标记：用于触发其他效果）
│  ├─ Immunity（免疫）
│  └─ Special（特殊机制）
├─ Duration（持续时间）
├─ StackRule（叠加规则）
├─ TriggerCondition（触发/刷新条件）
└─ RemoveCondition（移除条件）
```

### Buff 表关键字段（待确认）

| 字段 | 说明 |
|---|---|
| BuffId | Buff唯一ID |
| BuffName | Buff名 |
| BuffType | 增益/减益/控制/标记/特殊 |
| Duration | 持续时间（帧或秒） |
| MaxStack | 最大叠加层数 |
| StackBehavior | 叠加时刷新/独立/替换 |
| EffectList | 效果列表 |
| RemoveOnDeath | 死亡移除 |
| Dispellable | 可驱散 |
| Icon/VFX | 显示资源 |

### 已知特殊 Buff

| BuffId | 用途 | 来源 |
|---|---|---|
| 1005 | 通关无敌 (WinInvincibleBuff) | PlayerRuntimeSettings |

### 已知 Runtime 映射

| 配置 | Runtime | 说明 |
|---|---|---|
| Buff | `LBuffComponent` | 管理实体上所有Buff |
| BuffEffect | 各 Effect 实现类 | `RemoveBuffEffect` 等 |
| AddBuff | `LBuffComponent.AddBuff(id, caster)` | 添加 |
| RemoveBuff | `LBuffComponent.RemoveBuff(id)` | 移除 |

---

## 伤害系统

### DamageEffect 配置（待确认精确字段）

| 字段 | 说明 |
|---|---|
| DamageType | 物理/魔法/真实 |
| DamageTag | 伤害标签（用于加成区分） |
| BaseDamage | 基础伤害值或倍率 |
| ScaleAttribute | 缩放属性（ATK/MaxHP等） |
| ScaleRatio | 缩放比例 |
| CanCrit | 是否可暴击 |
| CanBlock | 是否可格挡 |
| IgnoreDefRatio | 无视防御比例 |
| ElementType | 元素类型 |

### 伤害公式核心（已知）

从代码 `DamageUtility.cs` 可知：
- 防御常数 = 2400
- 命中下限 = 10%
- 格挡基础减伤 = 50%
- 所有同 Tag 的伤害加成共享一个乘区

---

## 子弹系统

### Bullet 配置（待确认）

| 字段 | 说明 |
|---|---|
| BulletId | 子弹ID |
| Trajectory | 轨迹类型（直线/抛物线/追踪/扇形） |
| Speed | 飞行速度 |
| Lifetime | 存活时间 |
| HitCount | 可命中次数 |
| Penetration | 穿透数 |
| AOERadius | AOE半径 |
| OnHitEffect | 命中效果（DamageEffect/Buff） |

### 已知 Runtime

- `LBullet` 实体处理弹道和碰撞
- 命中时通过 `DamageEffect` 造成伤害或施加 Buff

---

## 召唤系统

### Summon 配置（待确认）

| 字段 | 说明 |
|---|---|
| SummonId | 召唤物ID |
| OwnerCamp | 继承施法者阵营 |
| Duration | 存活时间 |
| AI | 行为配置 |
| Attributes | 属性（可能继承/独立） |
| Skills | 召唤物技能 |

### 已知 Runtime

- `LSummon` 实体
- 可属于 Monster 阵营（`e is LSummon && e.Camp == EntityCamp.Monster`）
- 战斗胜利时被清除

## 常见问题

| 问题 | 定位思路 |
|---|---|
| 技能伤害不对 | 查 DamageEffect 倍率 + ScaleAttribute + DamageTag |
| Buff不生效 | 查 BuffId 引用链 + TriggerCondition + Duration |
| 子弹穿墙/不命中 | 查 Bullet 碰撞配置 + HitCount + Penetration |
| 召唤物不攻击 | 查 Summon AI配置 + Camp + Skill列表 |
| 技能释放时机错误 | 查 AI 优先级 + CastCondition + Cooldown |
