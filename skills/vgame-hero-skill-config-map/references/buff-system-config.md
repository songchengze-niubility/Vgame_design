# Buff System Config

## Buff 存储

- 编辑器产出: `Assets/GameResources/GameData/BuffData/Runtime/Buff_{id}.bytes`
- 序列化格式: MessagePack
- 运行时加载: `LBuffComponent.AddBuff(cfgId, caster)` → 反序列化 BuffDataRaw

## BuffDataRaw（Buff配置数据）

| 字段 | 类型 | 说明 |
|---|---|---|
| cfgId | int | Buff配置ID |
| buffName | string | Buff名称 |
| description | string | 描述 |
| duration | BuffDuration | 持续时间配置 |
| buffType | BuffType | Buff大类 |
| removeType | BuffRemoveType | 移除条件类型 |
| effects | List<IBuffEffectData> | 效果列表（可多个） |
| visualData | BuffDataVisual | 表现数据（图标/特效） |
| maxStacks | int | 最大叠加层数 |
| stackBehavior | BuffStackBehavior | 叠加行为 |
| infiniteStacks | bool | 无限叠加 |

## Buff 效果类型（14种）

| 效果类 | 说明 |
|---|---|
| **AttributeModifyEffect** | 修改属性（加/减/乘） |
| **AttrFixEffect** | 固定属性修改 |
| **MaxHpModifyEffect** | 修改最大HP |
| **CastDamageEffect** | 造成伤害（DOT等） |
| **HealEffect** | 治疗 |
| **ShieldEffect** | 护盾 |
| **BuffStateEffect** | 状态标记 |
| **StunBuffEffect** | 眩晕 |
| **SlowBuffEffect** | 减速 |
| **PauseAnimEffect** | 暂停动画 |
| **PauseBuffEffect** | 暂停其他Buff |
| **RemoveBuffEffect** | 移除指定Buff |
| **InterruptBuffEffect** | 打断 |
| **SkillCastEffect** | 触发技能释放 |

## 叠加行为 (BuffStackBehavior)

| 行为 | 说明 |
|---|---|
| Refresh | 刷新持续时间，不增加层数 |
| Stack | 增加层数，独立持续时间 |
| Replace | 新的替换旧的 |
| Independent | 每层独立实例 |

## 持续时间 (BuffDuration)

| 类型 | 说明 |
|---|---|
| 固定时间 | N帧/N秒后到期 |
| 永久 | 不会自动到期 |
| 次数型 | 触发N次后消失 |
| 条件型 | 条件不满足时消失 |

## 移除条件 (BuffRemoveType)

| 类型 | 说明 |
|---|---|
| 到期移除 | 持续时间结束 |
| 手动移除 | RemoveBuff 调用 |
| 驱散移除 | 被驱散效果移除 |
| 死亡移除 | 拥有者死亡时 |

## 已知特殊Buff

| ID | 用途 | 来源 |
|---|---|---|
| 1005 | 通关无敌 (WinInvincibleBuff) | PlayerRuntimeSettings 硬编码 |

## 运行时 (LBuff)

```csharp
LBuff:
  Receiver     // Buff持有者
  Creator      // Buff施加者
  CfgId        // 配置ID
  Stacks       // 当前层数
  Duration     // 剩余持续时间
  Effects[]    // 激活的效果列表
  
  Tick():      // 每帧更新持续时间/效果
  AddStack():  // 增加层数
  Remove():    // 移除
```

## LBuffComponent

管理实体上所有Buff的组件：

```csharp
LBuffComponent:
  AddBuff(cfgId, caster)    // 添加Buff（反序列化+初始化）
  RemoveBuff(cfgId)         // 按配置ID移除
  GetBuffById(cfgId)        // 查询
  HasBuff(cfgId)            // 是否存在
  Tick(deltaTime)           // 每帧更新所有Buff
```

## 与技能系统的关系

```
技能 Action → AddBuffAction(buffCfgId, target)
  → LBuffComponent.AddBuff(cfgId, caster)
    → 反序列化 Buff_{cfgId}.bytes → BuffDataRaw
      → 创建 LBuff 实例
        → 初始化 Effects[]
          → AttributeModify / Damage / Heal / Stun / ...
```

## 策划配置流程

1. **创建 Buff**: 在 Buff 编辑器中定义效果、持续时间、叠加规则
2. **序列化**: 保存为 `Buff_{id}.bytes`
3. **在技能中引用**: 技能编辑器中添加 `AddBuffAction`，填入 buffCfgId
4. **在配表中引用**: 某些系统直接引用 buffCfgId（如 PlayerRuntimeSettings.WinInvincibleBuff = 1005）
5. **运行时**: 技能释放 → Action执行 → AddBuff → 效果生效

## 注意事项

| 注意 | 说明 |
|---|---|
| Buff 不在 Excel 配表中 | 是 .bytes 文件，通过编辑器产出 |
| BuffIcon.xlsx 只管图标 | 不管 Buff 逻辑，逻辑在 .bytes 里 |
| 修改 Buff 需要编辑器 | 不能直接改 .bytes（二进制） |
| Buff ID 需要唯一 | 同一个 cfgId 全局唯一 |
| 控制抵抗 | LBuff 内置控制抵抗递减机制 |
