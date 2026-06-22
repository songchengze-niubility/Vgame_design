# AI & Behavior Config Map

## AI 系统定位

Vgame 中 AI 控制怪物/Boss 的行为决策：选择技能、移动、阶段转换、仇恨管理等。

## AI 架构（待确认精确实现）

可能的架构模式：

### 方案A：行为树 (Behavior Tree)

```
BehaviorTree
├─ Selector（选择节点）
│  ├─ Sequence: 阶段转换检查
│  │  ├─ Condition: HP < 阈值
│  │  └─ Action: 切换阶段/播放演出
│  ├─ Sequence: 技能释放
│  │  ├─ Condition: 冷却好了 && 距离合适
│  │  └─ Action: 释放技能
│  └─ Sequence: 默认行为
│     └─ Action: 移动/巡逻/待机
```

### 方案B：状态机 + 优先级表

```
AIState
├─ Idle（待机）
├─ Chase（追击）
├─ Attack（攻击）
├─ Skill（技能）
├─ PhaseTransition（阶段切换）
└─ Retreat（撤退）

SkillPriority
├─ Skill A: priority=10, condition=HP<50%
├─ Skill B: priority=5, condition=distance<3
└─ Skill C: priority=1, condition=always
```

## AI 配置关键字段（待确认）

| 字段 | 说明 |
|---|---|
| AIConfigId | AI配置ID |
| BehaviorType | 行为类型（近战/远程/Boss/召唤） |
| AggroRange | 仇恨范围 |
| AttackRange | 攻击范围 |
| SkillPriorities | 技能优先级列表 |
| PhaseThresholds | 阶段血量阈值 |
| MovePattern | 移动模式（追击/保持距离/巡逻） |
| RetreatCondition | 撤退条件 |
| SpecialBehavior | 特殊行为标记 |

## Boss AI 特殊性

### 多阶段 Boss

| 阶段 | 配置要点 |
|---|---|
| P1 (100%-70% HP) | 基础技能组，较少攻击频率 |
| P2 (70%-30% HP) | 增加技能，提高频率，可能召唤小怪 |
| P3 (30%-0% HP) | 狂暴，全技能解锁，高攻击频率 |

### 阶段转换

- 血量阈值触发
- 转换时可能：无敌帧 + 演出 + 清场 + Buff施加
- 转换后：刷新技能冷却 + 切换技能优先级 + 改变移动模式

## 不同怪物类型的 AI 模式

| 类型 | AI特点 |
|---|---|
| 普通近战怪 | 追击→到达距离→普攻循环 |
| 普通远程怪 | 保持距离→射击→被接近时后退 |
| 精英怪 | 有技能释放逻辑，可能有简单阶段 |
| Boss | 多阶段、多技能优先级、演出事件 |
| 召唤物 | 跟随主人或固定位置，简单攻击 |
| 环境怪 | 不移动，周期性攻击/触发 |

## 与 Vgame 跑酷特性的结合

Vgame 是跑酷游戏，AI 需要考虑：
- 玩家持续前进，怪物需要在玩家前方/侧方刷出
- 怪物可能需要跟随地形移动
- Boss 战可能有固定场景（Loop 停止时进入 Boss 区域）
- 远程怪可能需要在高台/平台上射击
- 飞行怪不受地形限制

## 仇恨系统（待确认）

可能的仇恨规则：
- PVE 中怪物默认仇恨最近的玩家角色
- 竞技场中怪物可能攻击双方
- 一些Boss机制可能切换仇恨目标
- 召唤物仇恨继承施法者的目标

## 待确认项

- AI 系统的具体实现方式（行为树 vs 状态机 vs 混合）
- AI 配置表的精确表名和字段
- Boss 阶段转换的配置格式
- 仇恨系统的实现细节
- AI 与 Lockstep 帧同步的关系
- 怪物移动与地形的交互规则
