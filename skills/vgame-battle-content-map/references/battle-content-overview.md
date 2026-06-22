# Battle Content Overview

## 定位

战斗内容是 Vgame 最高频的策划配置工作。本文档建立战斗内容的全局配置层模型，帮助快速定位"某个战斗元素在哪配、谁引用它、改了影响什么"。

## 战斗内容层级模型

```
关卡层 (Level/Terrain)
├─ 波次层 (Wave/Spawn)
│  ├─ 怪物/精英/Boss实体 (Monster/Elite/Boss)
│  │  ├─ 属性层 (Attribute: HP/ATK/DEF/Speed...)
│  │  ├─ 技能层 (Skill: 普攻/主动/被动/连招)
│  │  │  ├─ 动作时间轴 (ActionClip/Timeline)
│  │  │  ├─ 伤害效果 (DamageEffect)
│  │  │  ├─ 子弹/弹道 (Bullet)
│  │  │  └─ 召唤物 (Summon)
│  │  ├─ Buff层 (Buff: 增益/减益/控制/标记)
│  │  │  └─ Buff效果 (BuffEffect: 属性修改/伤害/治疗/护盾/位移...)
│  │  └─ AI层 (Behavior: 行为树/状态机/阶段转换)
│  └─ 环境层 (Hazard: 陷阱/障碍/移动平台/伤害区域)
└─ 战斗事件层 (BattleEvent: 镜头/顿帧/特效/音效/慢动作)
```

## 配置来源分类

| 层级 | 主要来源 | 说明 |
|---|---|---|
| 关卡/地形 | Level表 + Terrain配置 | 定义关卡结构、地形分段、Loop机制 |
| 波次/刷怪 | Wave表 / SpawnGroup | 定义刷怪时机、位置、条件、数量 |
| 怪物属性 | Monster表 / MonsterAttribute | 定义怪物基础属性、等级缩放 |
| 技能 | Skill表 / SkillAction / SkillLine | 定义技能释放流程、时间轴、效果链 |
| 伤害 | DamageEffect / DamageConfig | 定义伤害计算、类型、Tag、倍率 |
| 子弹 | Bullet表 | 定义弹道、碰撞、穿透、范围 |
| Buff | Buff表 / BuffEffect | 定义增减益、持续时间、叠加、触发 |
| AI | BehaviorTree / AIConfig | 定义决策逻辑、仇恨、阶段切换 |
| 召唤 | Summon表 | 定义召唤物属性、AI、生命周期 |
| 环境 | Hazard / Trap / Platform | 定义地形机关、伤害区域 |
| 战斗反馈 | HitEffect / CameraShake / SlowMotion | 定义打击感反馈链 |

## 关键交叉引用

| 引用方 | 被引用方 | 关系 |
|---|---|---|
| Level/Wave | Monster ID | 刷什么怪 |
| Monster | Skill ID | 怪物拥有哪些技能 |
| Monster | AI/BehaviorTree ID | 怪物用什么AI |
| Skill | DamageEffect ID | 技能造成什么伤害 |
| Skill | Buff ID | 技能附带什么Buff |
| Skill | Bullet ID | 技能发射什么子弹 |
| Skill | Summon ID | 技能召唤什么 |
| Buff | BuffEffect | Buff产生什么效果 |
| Bullet | DamageEffect ID | 子弹命中时的伤害 |
| DamageEffect | DamageConfig | 伤害计算参数 |

## 常见配置工作流

### 新增一个怪物
1. Monster表新增一行（属性、模型、阵营）
2. 配技能（Skill表 + ActionClip）
3. 配AI（BehaviorTree）
4. 挂到Wave表对应关卡

### 新增一个Boss
1. Monster表新增（Boss类型标记）
2. 配多阶段技能组
3. 配阶段转换AI逻辑
4. 配专属Buff/机制
5. 配关卡演出事件
6. 挂到Wave表 + Level配置

### 修改技能效果
1. 定位Skill ID
2. 找到对应 ActionClip / DamageEffect
3. 修改数值/Tag/目标/范围
4. 检查引用方（哪些Monster用这个Skill）

### 调整关卡难度
1. 定位Level → Wave配置
2. 调整怪物数量/精英比例/刷新间隔
3. 或调整Monster属性缩放
4. 或调整Boss阶段血量阈值

## 与 Lockstep Runtime 的映射

| 配置表 | Runtime 消费者 |
|---|---|
| Monster/Attribute | `LMonster` / `AttributeComponent` |
| Skill/SkillAction | `LSkillComponent` / `SkillInstance` / `SkillLine` |
| DamageEffect | `DamageEffectRuntime` / `DamageUtility` |
| Buff/BuffEffect | `LBuffComponent` |
| Bullet | `LBullet` |
| Summon | `LSummon` |
| AI/BehaviorTree | AI系统（待确认具体Manager名） |
| Wave/Spawn | `LLevelMgr` / `LSpawnMgr`（待确认） |
| Level/Terrain | `LLevelMgr` / `TerrainSystem` |

## 待确认项

- 怪物属性缩放的具体公式和表结构
- AI 行为树的具体表名和字段
- Wave/Spawn 的精确表结构和条件字段
- 环境机关的配置来源
- Boss阶段转换的具体配置方式
- 战斗反馈（顿帧/慢动作/镜头）的配置表位置
