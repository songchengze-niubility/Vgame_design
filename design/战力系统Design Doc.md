# 战力系统 — Design Doc

## 元信息

| 项 | 内容 |
|----|------|
| 功能名称 | 战力系统（Power Formula） |
| 作者 | Codex 反推整理 |
| 创建日期 | 2026-07-01 |
| 状态 | `Draft` |
| 风险档位 | MEDIUM |
| 关联 Proposal | — |

## 背景与目标

### 背景
Vgame 需要一个统一、可配置、可扩展的战力公式，用于角色、怪物或其他战斗单位的属性估值。当前口径不做技能机制折算，不按角色差异拆公式，只根据属性快照计算。

### 目标
- 所有角色使用同一套属性战力公式。
- 基础属性与二级属性分区间计算，再按区间乘法汇总。
- 支持后续继续追加区间3、区间4，而不重写公式结构。
- 将战力区间和属性系数落到 `Attribute.xlsx` 的 `PowerInterval`、`PowerPara` 两列。
- 将各区间整体调参倍数落到 `globals_conf.xlsx` 的 `PowerIntervalNMulti` 参数。

### 非目标
- 不计算技能机制、输出手法、AI、弹道命中率等实际战斗表现。
- 不使用角色实际平均属性反推系数。
- 不把等级属性重复计入战力；等级属性已通过 `Bonusattribute` 转化成实际属性。
- 不把生命/攻击/防御百分比在二级属性区间重复计入。

## 核心规则

### R-01: 总战力公式

- **触发条件**：战斗单位属性快照完成后，需要刷新或展示战力时。
- **前置限制**：属性百分比、等级属性、装备/旅券/星盘等来源已经合并进最终属性快照。
- **操作流程**：
  1. 按 `Attribute.xlsx` 读取每个属性的 `PowerInterval` 和 `PowerPara`。
  2. 按 `globals_conf.xlsx` 读取对应区间的全局倍数：`PowerInterval1Multi`、`PowerInterval2Multi`；缺失的高阶区间默认按 1 处理。
  3. `PowerInterval = 0` 的属性不参与战力计算。
  4. 区间1为基础战力底盘：`区间1战力 = Σ(属性值 × PowerPara × PowerInterval1Multi)`。
  5. 区间2及以后为乘法区间：`区间N战力 = 1 + Σ(属性值 × PowerPara × PowerIntervalNMulti)`，其中 `N >= 2`。
  6. 最终战力：`最终战力 = round(区间1战力 × 区间2战力 × 区间3战力 × 区间4战力...)`。
- **状态变化**：角色/怪物/单位战力数值刷新。
- **资源变化**：无，纯展示与评估数值。
- **UI 反馈**：属性变化后展示新的战力值；若有对比界面，可显示战力增减。
- **异常边界**：不存在区间2及以后时，该区间默认视为 1；最终结果小于 0 时钳制为 0。
- **落地点**：`${VGAME_CONFIG_DATAS}\Attribute\Attribute.xlsx`，运行时战力计算模块。

### R-02: 区间1基础属性

- **触发条件**：计算区间1战力时。
- **前置限制**：基础属性投放比例采用 `生命:攻击:防御 = 10:3:2`，以攻击系数 1 为锚点。
- **操作流程**：
  - `生命系数 = 3 / 10 = 0.3`
  - `攻击系数 = 1`
  - `防御系数 = 3 / 2 = 1.5`
  - `区间1战力 = (生命 × 0.3 + 攻击 × 1 + 防御 × 1.5) × PowerInterval1Multi`
- **状态变化**：形成基础战力底盘。
- **资源变化**：无。
- **UI 反馈**：无单独 UI 反馈，只影响最终战力。
- **异常边界**：当前只使用统一攻击 `Attack`。`PhysicsAttack`、`MagicAttack` 不直接计战力，避免与 `Attack` 重复计算。
- **落地点**：`Attribute.xlsx` 中 `Hp`、`Attack`、`Armor` 的 `PowerInterval = 1`。

### R-03: 区间2二级属性

- **触发条件**：计算区间2战力时。
- **前置限制**：只使用已经转化后的实际二级属性；等级属性不直接参与。
- **操作流程**：
  1. 读取 `PowerInterval = 2` 的属性。
  2. 对每个属性计算 `属性值 × PowerPara × PowerInterval2Multi`。
  3. 汇总为 `区间2战力 = 1 + Σ(属性值 × PowerPara × PowerInterval2Multi)`。
  4. 二级属性系数由属性定价反推：`PowerPara = 0.01 / 属性定价值`。
- **状态变化**：形成二级属性乘法区间。
- **资源变化**：无。
- **UI 反馈**：无单独 UI 反馈，只影响最终战力。
- **异常边界**：生命加成、攻击加成、防御加成已经体现在区间1最终基础属性中，不进入区间2。
- **落地点**：`Attribute.xlsx` 中 `PowerInterval = 2` 的属性。

### R-04: 明确排除规则

- **触发条件**：属性存在但不应直接参与战力时。
- **前置限制**：属性仍可用于战斗、展示或转化，只是不直接计战力。
- **操作流程**：
  - `PhysicsAttack`、`MagicAttack`：因已有统一 `Attack`，置为 `PowerInterval = 0`。
  - `HpBonus`、`AttackBonus`、`PhysicsAttackBonus`、`MagicAttackBonus`、`ArmorBonus`：已通过最终生命/攻击/防御体现，置为 0。
  - `CritLevel`、`CritDmgBonusLevel`、`EnergyPreAddBonusLevel`、`CoolDownReduceLevel`、`BlockLevel`：等级属性已转化到对应实际属性，置为 0。
  - 未在属性定价中明确给价的命中、闪避、效果命中、效果抵抗、免伤、护盾、受治疗等属性，当前置为 0，后续补定价后再开放。
- **状态变化**：排除属性不会改变战力。
- **资源变化**：无。
- **UI 反馈**：无。
- **异常边界**：若未来某个被排除属性成为核心养成投放，必须先补属性定价，再改 `PowerInterval` 和 `PowerPara`。
- **落地点**：`Attribute.xlsx` 中对应属性的 `PowerInterval = 0`、`PowerPara = 0`。

## 当前配置结果

### 全局区间倍数

| 参数 | 当前值 | 用途 |
|------|--------|------|
| PowerInterval1Multi | 1 | 区间1基础属性贡献的全局倍数 |
| PowerInterval2Multi | 1 | 区间2二级属性贡献的全局倍数 |

### 区间1配置

| 属性 | 中文名 | PowerInterval | PowerPara | 说明 |
|------|--------|---------------|-----------|------|
| Hp | 生命 | 1 | 0.3 | 由 10:3:2 反推 |
| Attack | 攻击 | 1 | 1 | 统一攻击口径 |
| Armor | 防御 | 1 | 1.5 | 由 10:3:2 反推 |

### 区间2配置

| 属性 | 中文名 | 属性定价值 | PowerPara |
|------|--------|------------|-----------|
| Crit | 暴击率 | 0.0018 | 5.5556 |
| CritDmgBonus | 暴击伤害 | 0.0054 | 1.8519 |
| EnergyPreAddBonus | 能量回复 | 0.0033 | 3.0303 |
| CoolDownReduce | 冷却缩减 | 0.0025 | 4 |
| DmgBonus | 伤害加成 | 0.0033 | 3.0303 |
| ExtraDmgBonus | 玩法伤害加成 | 0.0033 | 3.0303 |
| NormalAttackDmgBonus | 普攻伤害 | 0.009 | 1.1111 |
| SkillDmgBonus | 技能伤害 | 0.012 | 0.8333 |
| UltimateDmgBonus | 必杀伤害 | 0.012 | 0.8333 |
| SingleTargetDmgBonus | 单体伤害 | 0.0033 | 3.0303 |
| PenetrationDmgBonus | 穿透伤害 | 0.0033 | 3.0303 |
| AOEDmgBonus | 范围伤害 | 0.0033 | 3.0303 |
| DurationDmgBonus | 持续伤害 | 0.0033 | 3.0303 |
| BleedDmgBonus | 流血伤害 | 0.0033 | 3.0303 |
| BurnDmgBonus | 灼烧伤害 | 0.0033 | 3.0303 |
| PoisonDmgBonus | 中毒伤害 | 0.0033 | 3.0303 |
| PhysicsDmgBonus | 物理伤害 | 0.0042 | 2.381 |
| MagicDmgBonus | 魔法伤害 | 0.0042 | 2.381 |
| Heal | 治疗效率 | 0.005 | 2 |
| Block | 格挡率 | 0.0033333333 | 3 |

## 技术方案

### 架构影响
需要一个通用战力计算入口，按属性配置动态聚合各区间。公式不需要硬编码二级属性列表，只依赖 `Attribute.xlsx` 的 `PowerInterval`、`PowerPara`，以及 `globals_conf.xlsx` 中对应区间的 `PowerIntervalNMulti`。

推荐伪代码：

```text
interval1 = 0
intervalSum = {}
intervalMulti = {
    1: globals.PowerInterval1Multi,
    2: globals.PowerInterval2Multi,
}

for attr in finalAttributes:
    config = Attribute[attr.Name]
    if config.PowerInterval <= 0 or config.PowerPara == 0:
        continue

    multi = intervalMulti.get(config.PowerInterval, 1)
    contribution = attr.Value * config.PowerPara * multi

    if config.PowerInterval == 1:
        interval1 += contribution
    else:
        intervalSum[config.PowerInterval] += contribution

power = interval1
for interval in sorted(intervalSum.keys()):
    power *= 1 + intervalSum[interval]

return round(max(0, power))
```

### 数据变更
- 修改 `${VGAME_CONFIG_DATAS}\Attribute\Attribute.xlsx`
- `PowerInterval`：`0` 不参与；`1` 基础属性区间；`2` 二级属性区间；`3+` 预留扩展区间。
- `PowerPara`：战力计算系数。
- 新增/使用 `${VGAME_CONFIG_DATAS}\globals_conf\globals_conf.xlsx`
- `PowerInterval1Multi`：区间1属性贡献全局倍数，当前值 `1`。
- `PowerInterval2Multi`：区间2属性贡献全局倍数，当前值 `1`。

### 接口变更
暂无协议变更。若服务器也需要校验或排行战力，需要保证客户端与服务器读取同一份属性配置并使用同一套公式。

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 物攻/魔攻与统一攻击重复计战力 | 中 | 高 | 当前配置只给 `Attack` 计区间1，`PhysicsAttack`、`MagicAttack` 置 0 |
| 未定价属性暂不计战力导致部分养成显示偏低 | 中 | 中 | 先保持 0，待补齐属性定价后再开放 |
| 二级属性为乘法区，极端堆叠会放大战力 | 中 | 中 | 后续可按区间增加上限、衰减或拆新区间 |
| 客户端/服务器公式不一致 | 低 | 高 | 战力公式封装为共享实现或同源配置校验 |

## 工作假设

| 假设 | 状态 | 澄清结论 |
|------|------|----------|
| 基础属性投放比例为 `生命:攻击:防御 = 10:3:2` | 已确认 | 用户明确要求按该比例反推，不使用实际平均值 |
| `Attack` 是当前战力计算使用的统一攻击口径 | 已确认 | 当前属性表和成长表已存在统一 `Attack` 字段 |
| 等级属性不直接参与战力 | 已确认 | 等级属性已经转化成实际二级属性 |
| 区间2使用乘法结构 | 已确认 | `区间2战力 = 1 + Σ(属性值 × PowerPara × PowerInterval2Multi)` |
| 区间倍数用于调节属性贡献 | 已确认 | `PowerIntervalNMulti` 乘在该区间每个属性贡献上；区间2不把默认值 1 乘大 |
| 后续可能增加区间3、区间4 | 已确认 | 总公式按动态区间乘法预留 |
