# 技能系统 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 技能系统（Skill System） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | LOW |
| 关联 Proposal | — |

## 背景与目标
### 背景
技能系统是 Vgame 战斗框架的核心，承载全部角色的主动与被动技能逻辑。目前 Skill.xlsx 已配置 1356 条技能，通过 Unity 技能编辑器（SkillEditorWindow）以节点图方式编辑，序列化为 MessagePack .bytes 文件供运行时加载。技能类型涵盖近战/异能/天赋/装备/专属/增强等，共计 63 种 ActionClip 类型支撑技能表现。

### 目标
- 建立从编辑到运行时的完整技能管线
- 统一技能状态机、事件监听、打断策略的执行模型
- 支持技能冷却、能量消耗、条件触发等战斗约束
- 提供跨表格的技能——目标/升级/战斗道具关联能力

### 非目标
- 技能平衡性数值调整（属策划迭代范畴）
- 63 种 ActionClip 逐一详细说明（仅分类归纳）
- 多人联机下的技能同步机制

## 核心规则

### R-01: 技能编辑与序列化管线
- **触发条件**：策划通过 Unity 菜单打开技能编辑器窗口
- **前置限制**：需已安装 Luban 导出工具链，Skill.xlsx 中已注册新技能条目
- **操作流程**：SkillEditorWindow（节点图编辑器）→ 策划拖拽 ActionClip 节点构建技能 → 保存为 SkillEditorAsset（ScriptableObject）→ 序列化为 .bytes（MessagePack 格式）
- **状态变化**：编辑器内 `Dirty` → Save 后 `Clean`
- **资源变化**：生成 `Chips/chipstest` 等 SkillData 路径下的 .bytes 文件
- **UI 反馈**：节点图实时预览连线、Inspector 面板显示选中节点参数
- **异常边界**：SkillId 在 Skill.xlsx 中未找到对应条目时序列化报错；循环引用节点图阻止保存
- **落地点**：`Config/GameConfig/Datas/Skill.xlsx` → 编辑器 → `.bytes` 资源包

### R-02: 运行时技能加载与实例化
- **触发条件**：角色释放技能（主动）或战斗事件触发（被动/自动）
- **前置限制**：技能资源 .bytes 已正确打包，角色满足 SP 消耗、冷却、解锁等释放条件
- **操作流程**：`SkillUtility.Deserialize()` 反序列化 .bytes → 构造 `SkillRuntimeData` → 创建 `SkillInstance` → 启动 `SkillLine`（状态机）
- **状态变化**：Idle → Casting → Active → Finish（可通过 Interrupt 提前终止）
- **资源变化**：SP 扣除（ChangeEnergyAction），冷却开始计时（CooldownAction），技能计数变化
- **UI 反馈**：技能图标进入冷却遮罩，SP 条即时更新，命中和伤害数字飘出
- **异常边界**：.bytes 文件缺失时回退到默认技能配置并记录错误；SP 不足时技能不触发且 UI 灰显
- **落地点**：`SkillInstance` 由角色的 SkillComponent 持有并管理生命周期

### R-03: SkillLine 状态机与打断策略
- **触发条件**：SkillInstance 创建后自动进入 SkillLine 状态机
- **前置限制**：SkillRuntimeData 已加载完整 ActionClip 列表
- **操作流程**：SkillLine 按时间轴依次执行 ActionClip 节点 → 遇到 Interrupt 标记时查询打断策略 → 决定当前节点行为
- **状态变化**：Normal → Interrupted（StateInterrupt 暂停/恢复 或 ResetInterrupt 从头重播）
- **资源变化**：StateInterrupt 暂存当前进度（LBlackboard），ResetInterrupt 清空进度重新开始
- **UI 反馈**：中断时技能特效/动画按策略响应（暂停或重置）
- **异常边界**：不支持的打断类型静默 fallback 为 StateInterrupt
- **落地点**：`SkillLine` 类管理状态迁移，`InterruptStrategy` 枚举决定分支

### R-04: 技能事件监听与条件触发
- **触发条件**：战斗事件发生时（OnHit、OnDeath、HP 阈值、Timer、能量满等），由 `SkillEventListener` 检测
- **前置限制**：技能中已注册对应 `LEventType` 监听，条件满足 `SkillEventConditionBase` 子类判定（如 `CheckHp`）
- **操作流程**：事件广播 → Listener 匹配 eventType → 运行 condition.Check() → 满足则触发关联的 `SkillActionClip`
- **状态变化**：等待触发 → 条件满足 → 执行链接技能或 buff
- **资源变化**：无直接消耗（触发链接技能本身可能消耗 SP）
- **UI 反馈**：被动触发式技能通常无 UI 预警，但可配置触发特效
- **异常边界**：事件在 SkillLine 未激活期间丢失（不回溯）；同一帧内多次事件合并去重
- **落地点**：`SkillEventListener` 挂载在 SkillInstance 上，全局事件由 `LEventSystem` 广播

### R-05: 技能冷却管理
- **触发条件**：技能释放完成或被打断后，`SkillCooldown` 组件启动冷却计时
- **前置限制**：技能在 Skill.xlsx 中定义了 CooldownTime
- **操作流程**：释放技能 → SkillCooldown.StartCooldown(skillId, cdTime) → 每帧 tick 减少剩余时间 → 剩余时间归零后技能可用
- **状态变化**：Ready → OnCooldown → Ready
- **资源变化**：无资源消耗（冷却为时间约束）
- **UI 反馈**：技能图标半透明遮罩 + 剩余秒数倒计时文字
- **异常边界**：同技能 ID 重复进冷却时刷新计时（非叠加）；死亡时所有冷却强制重置；CooldownAction 可主动缩减冷却
- **落地点**：`SkillCooldown` 组件挂载在角色 Entity 上

### R-06: 跨表技能关联
- **触发条件**：战斗生效期间各系统查询技能相关配置
- **前置限制**：各 Excel 表已正确引用 SkillId
- **操作流程**：
  - `TargetSkill.xlsx`（405 行）SkillId → ModifierTargetType，决定技能修饰目标
  - `LevelSkill.xlsx`（199 行）装备技能参数：RecoverRate/Storage/Cost
  - `HeroSkillLv.xlsx` 按职业+技能类型+等级查升级消耗（CostItem + MoneyCost + HeroLv）
  - `FightItem` 中的 `UseHeroSkill.xlsx`、`UseUltimateSkill.xlsx` 为战斗道具触发的技能
- **状态变化**：无状态变化（纯查询）
- **资源变化**：升级消耗对应 Item 和货币
- **UI 反馈**：升级面板显示消耗预览，道具描述显示触发技能名
- **异常边界**：SkillId 引用了不存在的技能时返回空配置并打 warning
- **落地点**：`Config/GameConfig/Datas/` 下各关联表

### R-07: ActionClip 类型体系
- **触发条件**：SkillLine 运行时按时间轴顺序执行节点
- **前置限制**：63 种 ActionClip 均实现 `SkillActionClip` 基类
- **操作流程**：时间轴推进 → 到达某节点 startTime → 执行对应 ActionClip.Execute() → 到达 endTime 或执行完毕 → 进入下一节点
- **状态变化**：按 ActionClip 类型各异（施放伤害/加 Buff/移除 Buff/治疗/护盾/子弹/召唤/移动/冲刺/无敌/反击/能量/冷却/动画/特效/震屏/子弹时间/CutIn 等）
- **资源变化**：CastDamageAction 扣血、HealAction 回血、ShieldAction 加盾、ChangeEnergyAction 改能量、CooldownAction 改冷却
- **UI 反馈**：CutInAction 切入动画、CameraShakeAction 震屏、PlayBulletTimeAction 慢镜头、PlayEffect 特效播放
- **异常边界**：ActionClip 依赖的目标实体已死亡时，伤害类跳过、Buff 类可选加至队友
- **落地点**：`SkillActionClip` 子类各自实现，均位于 `Skill/ActionClip/` 目录
