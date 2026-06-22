# Monster & Boss Config Map

## 怪物配置层级

### 基础怪物

| 配置项 | 说明 | 来源表（待确认精确表名） |
|---|---|---|
| Monster ID | 唯一标识 | Monster表 |
| Monster Name | 显示名 | Monster表 |
| Monster Type | 普通/精英/Boss/小Boss | Monster表 |
| Camp | 阵营（Monster/Player/Neutral） | Monster表 |
| Base Attributes | HP/ATK/DEF/Speed/暴击等 | MonsterAttribute 或 Monster表内嵌 |
| Level Scaling | 属性随关卡等级缩放 | 待确认（可能是公式或系数表） |
| Skill List | 拥有的技能ID列表 | Monster表字段 |
| AI Config | 行为树/AI配置ID | Monster表字段 |
| Visual Config | 模型/动画/特效引用 | Monster表字段 |
| Spawn Parameters | 出生动画/无敌时间 | Monster表或Wave表 |

### 精英怪

精英怪通常是普通怪的变体：
- 共享基础Monster配置
- 属性倍率放大（或独立属性行）
- 可能附加额外Buff/技能
- 可能有独立AI配置

### Boss

Boss 配置特殊性：
- 多阶段血量阈值
- 每阶段不同技能组
- 阶段转换演出/无敌
- 专属机制Buff
- 可能有召唤/环境互动
- 独立AI行为树（带阶段判断）

## 属性系统

### 怪物属性分类

| 类别 | 属性 | 说明 |
|---|---|---|
| 基础 | HP, ATK, DEF | 核心三维 |
| 战斗 | 暴击率, 暴击伤害, 命中, 闪避 | 二级属性 |
| 机动 | 移动速度, 攻击速度 | 行为速率 |
| 特殊 | 元素属性, 抗性, 护盾 | 特殊机制 |

### 属性缩放（待确认）

可能的缩放方式：
- 按关卡推荐等级的线性/指数公式
- 按难度系数的乘数表
- Boss独立数值行（不缩放）

## EntityType 与 Runtime 映射

| Config Type | Runtime Class | 说明 |
|---|---|---|
| 普通怪 | `LMonster` | EntityType.Monster |
| 精英怪 | `LMonster`（带Elite标记） | 待确认是否有独立EntityType |
| Boss | `LMonster`（带Boss标记） | 可能有 `LBossUnity` 聚合体 |
| 召唤物 | `LSummon` | EntityType.Summon |

## 已知代码线索

从异常堆栈和代码可知：
- `LMonster` 实体走 `AttributeComponent` 管理属性
- `LMonster` 死亡触发 `LEventType.EntityDeath`
- `LLevelMgr.OnEntityDestroy` 监听怪物死亡判断波次结束
- `LBossUnity` 存在多体聚合机制（Boss由多个子体组成）
- `DamageUtility.Calculate` 统一处理伤害计算

## 常见问题

| 问题 | 定位思路 |
|---|---|
| 怪物太硬/太脆 | 查 MonsterAttribute HP/DEF + Level Scaling |
| Boss某阶段卡死 | 查阶段血量阈值 + AI阶段转换条件 |
| 精英怪没有区分度 | 查精英额外Buff/技能/属性倍率 |
| 怪物不攻击 | 查AI配置 + Skill触发条件 |
| 怪物动作异常 | 查Skill ActionClip + 动画状态机 |
