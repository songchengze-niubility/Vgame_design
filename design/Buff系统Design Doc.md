# Buff 系统 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | Buff 系统（Buff System） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | LOW |
| 关联 Proposal | — |

## 背景与目标
### 背景
Buff 系统提供角色/怪物身上的持续性效果管理框架。与技能不同，Buff 不通过 Excel 配置，而是以 Buff 编辑器制作后序列化为 MessagePack .bytes 文件（`BuffData/Runtime/Buff_{id}.bytes`）。Buff 支持 14 种效果类型、多种叠加行为和持续时长的灵活组合，是战斗增益/减益的核心载体。

### 目标
- 建立 Buff 从编辑到序列化的完整管线
- 定义 Buff 数据模型（Duration / BuffType / RemoveType / Effects / Stacks）
- 规范运行时 Buff 组件的添加、刷新、移除、叠加逻辑
- 明确 14 种效果类型各自的作用域和行为

### 非目标
- Buff 图标资源配置（属美术/UI 范畴）
- Buff 与技能 ActionClip 的绑定逻辑（属技能系统）
- 网络同步下的 Buff 复制策略

## 核心规则

### R-01: Buff 数据模型定义
- **触发条件**：编辑器新建或编辑 Buff 配置
- **前置限制**：--- 无
- **操作流程**：Buff 编辑器设定以下字段 → 保存为 BuffDataRaw：cfgId（唯一 ID）、buffName、description、duration（BuffDuration 类型）、buffType（BuffType 枚举）、removeType（BuffRemoveType 枚举）、effects（List\<IBuffEffectData\>）、visualData、maxStacks、stackBehavior、infiniteStacks
- **状态变化**：编辑器中 `Dirty` → Save → 序列化为 `Buff_{id}.bytes`
- **资源变化**：生成/更新 `.bytes` 文件
- **UI 反馈**：编辑器内效果列表实时预览，参数修改即时反映
- **异常边界**：cfgId 重复时阻止保存；effects 列表为空时警告但允许保存
- **落地点**：`BuffData/Runtime/Buff_{id}.bytes`

### R-02: Buff 叠加行为
- **触发条件**：当一个新 Buff 尝试添加到已持有同 BuffId 的实体上时
- **前置限制**：目标实体上已有同 BuffId 的 Buff 实例
- **操作流程**：根据 `stackBehavior` 枚举决定行为：
  - `Refresh`：刷新已有 Buff 的持续时间至满值
  - `Stack`：叠加层数（不超过 maxStacks），每层独立计时或共享计时（依 infiniteStacks 决定）
  - `Replace`：移除旧 Buff，应用新 Buff（新 Buff 参数覆盖）
  - `Independent`：新旧 Buff 完全独立，各自计时
- **状态变化**：已有 Buff 的 stackCount 变化、duration 变化、或被移除
- **资源变化**：Stack 时 buff 内部计数器递增；Replace 时旧 buff 效果先移除再应用新效果
- **UI 反馈**：Buff 图标上显示层数角标，Refresh 时图标闪烁
- **异常边界**：maxStacks 为 0 时禁止叠加，静默转为 Refresh；infiniteStacks=true 时无视 maxStacks
- **落地点**：`LBuffComponent.AddBuff()` 中判断现有 Buff 并执行对应叠加策略

### R-03: Buff 持续时间管理
- **触发条件**：Buff 添加到实体后启动计时
- **前置限制**：BuffDuration 已定义类型和参数
- **操作流程**：按 BuffDuration 类型执行计时：
  - `FixedTime`：按定义秒数倒计时
  - `Permanent`：不自动消失，仅由 RemoveType 条件移除
  - `CountBased`：按受击/行动次数递减
  - `Conditional`：由特定条件触发移除（如 HP 阈值）
- **状态变化**：Active → 倒计时归零 / 次数耗尽 / 条件满足 → Expired → 触发移除
- **资源变化**：每帧 tick 更新剩余时间/剩余次数
- **UI 反馈**：固定时间型显示倒计时环，次数型显示剩余次数文字
- **异常边界**：计时器精度使用 float deltaTime，帧率波动不影响总时长；Permanent Buff 在角色死亡时统一移除
- **落地点**：`LBuff.Tick(deltaTime)` 处理，到时限后通知 `LBuffComponent` 移除

### R-04: Buff 移除条件
- **触发条件**：RemoveType 指定的移除条件满足时
- **前置限制**：Buff 当前为 Active 状态
- **操作流程**：`BuffRemoveType` 枚举触发：
  - `TimeOut`：持续时间结束自动移除
  - `OnDeath`：持有者死亡移除
  - `OnSkillCast`：持有者释放技能时移除
  - `OnHit`：持有者受到伤害时移除（按层数消耗）
  - `Manual`：仅由 RemoveBuffEffect / RemoveBuffAction 主动移除
- **状态变化**：Active → Removing → Removed
- **资源变化**：Buff 效果全部回滚（属性修正还原、状态解除等）
- **UI 反馈**：Buff 图标从状态栏消失（带淡出动画）
- **异常边界**：多个移除条件同时满足时仅处理一次移除逻辑；正在移除中不可再次移除
- **落地点**：`LBuff.CheckRemoveCondition()` 每帧或事件驱动时调用

### R-05: 14 种效果类型
- **触发条件**：Buff 添加到实体时应用 effects 列表；移除时回滚
- **前置限制**：effects 中每个 IBuffEffectData 类型有效且参数合法
- **操作流程**：
  - `AttributeModifyEffect`：按值/百分比修正目标属性
  - `AttrFixEffect`：将目标属性固定为某值（不受后续修正影响）
  - `MaxHpModifyEffect`：修改最大 HP（同时按比例调整当前 HP）
  - `CastDamageEffect`：每 tick 对持有者造成伤害（DoT）
  - `HealEffect`：每 tick 对持有者回复生命（HoT）
  - `ShieldEffect`：生成护盾吸收伤害
  - `BuffStateEffect`：赋予特定战斗状态标记（浮空/倒地/霸体等）
  - `StunBuffEffect`：眩晕，禁止行动
  - `SlowBuffEffect`：减速，修改移动速度
  - `PauseAnimEffect`：暂停当前动画播放
  - `PauseBuffEffect`：暂停其他 Buff 的计时/效果
  - `RemoveBuffEffect`：移除持有者身上的指定 Buff
  - `InterruptBuffEffect`：打断持有者当前技能
  - `SkillCastEffect`：触发一个技能释放
- **状态变化**：Add 时施加效果 → Remove 时回滚效果
- **资源变化**：属性型效果实时参与伤害公式计算
- **UI 反馈**：DoT 跳伤害数字，护盾条显示，眩晕/减速有对应状态动画
- **异常边界**：效果参数导致计算溢出（如治疗量为负）时 clamp 为 0
- **落地点**：`IBuffEffectData.Apply()` / `IBuffEffectData.Remove()` 定义操作对

### R-06: 运行时 LBuff 与 LBuffComponent
- **触发条件**：战斗实体的 Buff 生命周期管理
- **前置限制**：实体已挂载 `LBuffComponent`
- **操作流程**：
  - `LBuff`：单个 Buff 实例，管理效果列表和计时
  - `LBuffComponent`：实体上管理所有 Buff 的集线器，提供 Add / Remove / Has / Get 接口
  - Add 时按 stackBehavior 处理叠加
  - Remove 时先调用所有 IBuffEffectData.Remove()，再从列表移除
  - 每帧 Tick 遍历所有 Active Buff 更新剩余时间和持续效果
- **状态变化**：Buff 集新增/减少 → 属性重新计算
- **资源变化**：属性型 Buff 变化时触发属性重新计算
- **UI 反馈**：BuffComponent 通知 UI 层刷新 Buff 条
- **异常边界**：Add 时 cfgId 为 0 或无 .bytes 文件 → 跳过并报错；同一帧内对同一 BuffId 多次 Add/Remove 批量合并处理
- **落地点**：`LBuffComponent` 挂载在 `LEntity` 上

### R-07: 特殊 Buff（WinInvincibleBuff）
- **触发条件**：战斗胜利后，若配置了 Buff 1005
- **前置限制**：战斗胜利判定完成，角色处于存活状态
- **操作流程**：战斗结算后自动为存活角色添加 Buff ID 1005 = WinInvincibleBuff → 角色进入无敌状态 → 战斗场景完全卸载时移除
- **状态变化**：Normal → Invincible → Normal（场景卸载）
- **资源变化**：角色不再受到伤害（无敌）
- **UI 反馈**：无敌效果可能闪现金色护盾特效
- **异常边界**：若 Buff 1005 .bytes 缺失，角色结算时无保护但仍正常进行；移除通过场景卸载批量清
- **落地点**：`BuffData/Runtime/Buff_1005.bytes`，由战斗结束逻辑添加，场景卸载时清理
