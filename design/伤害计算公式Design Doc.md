# 伤害计算公式 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 伤害计算公式（Damage Formula） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | LOW |
| 关联 Proposal | — |

## 背景与目标
### 背景
Vgame 的伤害计算是分层流水线：防御减伤 → 暴击判定 → 格挡判定 → 伤害加成/减免乘法区。公式中包含防御常数 24000、格挡基础减伤 50%、免伤上限 75%、命中下限 10% 等硬编码常量。此外支持真实伤害（跳过多层直接扣血）和标签型增伤共享乘法区。

### 目标
- 完整记录伤害计算链的每一步及其数学公式
- 明确各乘法区的叠加关系（加法区 vs 乘法区）
- 定义暴击、格挡、命中的判定公式
- 说明治疗、护盾、真实伤害与标准伤害的差异

### 非目标
- 具体数值平衡调整（属策划决策）
- 属性来源追踪（属属性系统/Buff 系统）
- 网络同步下的伤害计算时机

## 核心规则

### R-01: 标准伤害计算流水线
- **触发条件**：任何伤害型效果（普攻/技能伤害/Buff DoT）生效时
- **前置限制**：攻击方和目标方均已获取完整属性快照
- **操作流程**：
  1. **基础伤害**：`DamageBase` = 由技能参数/攻击力决定的基础值
  2. **防御减伤**：`DefEff` = Defender 防御力。`PostDefDmg = DamageBase × max(0.05, 1 - DefEff / (DefEff + 24000))`。伤害不低于 DamageBase 的 5%
  3. **暴击判定**：`rand(0,1) < Attacker.CritRate` → 暴击。`PostCritDmg = PostDefDmg × Attacker.CritDmgMultiplier`。未暴击则 PostCritDmg = PostDefDmg
  4. **格挡判定**：`BlockRate = Defender.Block - Attacker.BlockBreak`。`rand(0,1) < BlockRate` → 格挡成功。`PostBlockDmg = PostCritDmg × (1 - 0.5 - Defender.BlockStrength)`。基础减伤 50%，BlockStrength 额外叠加
  5. **乘法区一（增伤）**：`PostBonus1 = PostBlockDmg × (1 + DmgBonus)`
  6. **乘法区二（减伤）**：`PostBonus2 = PostBonus1 × (1 - min(0.75, DmgReduction))`。免伤上限 75%
  7. **乘法区三（目标易伤）**：`PostBonus3 = PostBonus2 × (1 + TargetDmgIncrease)`
  8. **乘法区四（玩法加成）**：`PostBonus4 = PostBonus3 × (1 + GameplayDmgBonus)`
  9. **乘法区五（玩法减免）**：`FinalDmg = PostBonus4 × (1 - GameplayDmgReduction)`
- **状态变化**：目标 HP 减少 FinalDmg
- **资源变化**：目标 HP、可能触发反击能量回复
- **UI 反馈**：伤害数字飘出（含暴击放大/颜色变化、格挡字样提示）
- **异常边界**：FinalDmg 为负值时 clamp 为 0；防御力为 0 时跳过防御减伤（原始伤害完整进入下一步）
- **落地点**：`DamageCalculator.CalculateDamage(attacker, defender, damageBase)`

### R-02: 命中率判定
- **触发条件**：每次伤害/效果计算前
- **前置限制**：攻击方 Hit 属性、防御方 Miss 属性已确定
- **操作流程**：`HitRate = Attacker.Hit - Defender.Miss`。若 HitRate < 10%，则固定为 10%。`rand(0,1) < HitRate` → 命中；否则 Miss
- **状态变化**：Miss 时不进入伤害计算流水线
- **资源变化**：无
- **UI 反馈**：Miss 时目标头顶飘 "Miss" 字样
- **异常边界**：Attacker.Hit 和 Defender.Miss 均覆盖 buff 实时影响；HitRate > 100% 时 clamp 为 100%
- **落地点**：`HitChecker.CheckHit(attacker, defender)` 在伤害流水线入口处调用

### R-03: 标签增伤共享乘法区
- **触发条件**：当技能/Buff 携带 Tag 类型伤害加成时（如火伤加成、近战加成等）
- **前置限制**：攻击方和目标的 Tag 加成列表已汇总
- **操作流程**：所有同类型标签的伤害加成先在各自的组内加法叠加 → 各标签组结果统一汇总到一个乘法区 → 再乘以当前伤害值。即 `TotalTagBonus = (1 + ΣTagBonus_A) + (1 + ΣTagBonus_B) + ... - N = 1 + Σ(所有标签 bonus)`。最终：`DmgAfterTag = Damage × TotalTagBonus`
- **状态变化**：无
- **资源变化**：无（纯计算）
- **UI 反馈**：无单独 UI 反馈
- **异常边界**：标签枚举未知时不计入 bonus（值为 0）；同一 bonus 同时出现在多个标签组时仅计一次
- **落地点**：`TagBonusCalculator.AggregateAndApply()`，在乘法区阶段生效

### R-04: 真实伤害
- **触发条件**：技能/Buff 标记为 TrueDamage 类型时
- **前置限制**：伤害源已标记为 TrueDamage
- **操作流程**：
  1. 跳过防御减伤（R-01 步骤 2）
  2. 跳过护盾吸收（直接作用于 HP）
  3. 不触发暴击和格挡判定（跳过 R-01 步骤 3、4）
  4. 直接使用基础伤害值进入乘法区（R-01 步骤 5-9）
- **状态变化**：目标 HP 直接扣除
- **资源变化**：目标 HP 减少，护盾值不变
- **UI 反馈**：真实伤害数字为白色/特殊字体，区别于物理/魔法伤害色
- **异常边界**：真实伤害数值为负时不处理；真实伤害仍受免伤上限 75% 约束（乘法区二）
- **落地点**：`DamageCalculator.CalculateTrueDamage()` 独立分支

### R-05: 治疗公式
- **触发条件**：治疗型技能/Buff HoT tick 生效时
- **前置限制**：治疗源和目标方属性已获取
- **操作流程**：`HealValue = Base × (1 + CasterHealBonus + TargetHealReceiveBonus)`。治疗可以暴击（`rand() < Caster.HealCritRate` → HealValue × HealCritMultiplier）。Recover 类型不可暴击
- **状态变化**：目标 HP 增加 HealValue（不超过 HP 最大值）
- **资源变化**：目标 HP 增加
- **UI 反馈**：绿色治疗数字飘出，暴击时放大
- **异常边界**：治疗值为负（如 Buff 反转）时 clamp 为 0 不扣血；目标死亡时不治疗
- **落地点**：`HealCalculator.CalculateHeal(caster, target, baseHeal)`

### R-06: 护盾公式
- **触发条件**：护盾型技能/Buff 效果生效时
- **前置限制**：护盾生成源属性已确定
- **操作流程**：`ShieldValue = Base × (1 + CasterShieldBonus)`。护盾不暴击。护盾在角色受击时优先于 HP 扣除（物理/魔法伤害），真实伤害穿透护盾
- **状态变化**：目标 Shield 值增加
- **资源变化**：Shield 槽增加；受击时 Shield 减少而非 HP
- **UI 反馈**：HP 条上叠加白色护盾段
- **异常边界**：多个护盾共存时按生成顺序吸收伤害（FIFO）；Buff 移除护盾效果时 Shield 值同步扣除
- **落地点**：`ShieldCalculator.ApplyShield(target, baseValue, casterBonus)`

### R-07: 公式常量与精度规范
- **触发条件**：系统初始化时注册，计算时引用
- **前置限制**：无
- **操作流程**：
  - 防御常数 `DEFENSE_CONSTANT = 24000`
  - 最小伤害比例 `MIN_DMG_RATIO = 0.05`
  - 免伤上限 `MAX_DMG_REDUCTION = 0.75`
  - 命中下限 `MIN_HIT_RATE = 0.10`
  - 格挡基础减伤比例 `BLOCK_BASE_REDUCTION = 0.50`
  - 所有中间计算结果使用 float 浮点运算
  - 最终伤害值截断为 int（向下取整），最小伤害为 1（>
- **状态变化**：无
- **资源变化**：无
- **UI 反馈**：无
- **异常边界**：浮点精度导致计算结果为极小正数（如 0.00001）时，int 截断为 0，此时若原始伤害 > 0 则 clamp 为 1
- **落地点**：`DamageConst` 静态类定义所有常量，`CalculationHelper.ClampDamage(value)` 统一处理精度
