# 怪物与 Boss 系统 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 怪物与 Boss 系统（Monster/Boss System） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | LOW |
| 关联 Proposal | — |

## 背景与目标
### 背景
Vgame 的怪物系统采用三层属性叠加模型：`MonsterAttribute[level] × MonsterAttributeType[type] × MonsterAttributeCorrect[system]`。Monster.xlsx 定义了每条怪物的基础信息（ID、战斗单位类型 Common/Elite/Boss、AI、技能组、模型等）。Boss 额外支持多阶段血量阈值和阶段转换机制。

### 目标
- 定义怪物三层属性计算流程
- 规范 Elite/Boss 的特殊机制（多阶段、阶段转换）
- 明确 AI 行为树与怪物数据的关联方式
- 梳理怪物相关配置表（UIMonster、SummonMonster）

### 非目标
- AI 行为树的具体节点逻辑（属 AI 系统）
- 关卡中怪物波次/刷新逻辑（属关卡编辑器）
- 网络同步下的怪物 AI 复制

## 核心规则

### R-01: 怪物三层属性叠加计算
- **触发条件**：任何需要怪物战斗属性的时机（关卡加载时、进入战斗时、属性查询时）
- **前置限制**：Monster.xlsx 设置了有效 AttrId、AttrTypeId、MonsterId
- **操作流程**：
  1. 根据 Monster.AttrId 查询 `MonsterAttribute.xlsx`（1000 行，按等级索引）获得 Lv 基础属性（Hp/PhysicsAttack/MagicAttack/Armor 等）
  2. 根据 Monster.AttrTypeId 查询 `MonsterAttributeType.xlsx`（17 套类型系数）获得类型系数（区分 Tank/DPS/Boss 等定位差异）
  3. 根据关卡所属系统（Rogue/Story/Dungeon）查询 `MonsterAttributeCorrect.xlsx`（212 行）获得系统倍率
  4. 最终属性 = MonsterAttribute[level] × MonsterAttributeType[type] × MonsterAttributeCorrect[system]
  5. 额外叠加 level.xlsx 的 HpCoefficient/AttackCoefficient/ArmorCoefficient 作为等级精细修正
- **状态变化**：属性计算完成 → 存入怪物 Entity 属性组件
- **资源变化**：根据最终属性初始化 HP 最大值，当前 HP = HP 最大值
- **UI 反馈**：血条长度反映最终属性；若策划调试模式开启，显示各层修正明细
- **异常边界**：AttrId 在 MonsterAttribute 中查无数据 → 使用 ID=1 的默认属性并报错；系数乘积超出 uint32 范围时 clamp
- **落地点**：`MonsterConfig.LoadMonsterAttribute(monsterId, level)` 方法完成查询链

### R-02: 战斗单位类型（BattleUnitType）
- **触发条件**：创建怪物实例时读取 BattleUnitType 决定行为模板
- **前置限制**：Monster.xlsx 已设置有效 BattleUnitType
- **操作流程**：
  - `Common`：普通小怪，单体无特殊机制，标准 AI
  - `Elite`：精英怪，属性倍率更高，可能带 1-2 个特殊技能，有精英出场特效
  - `Boss`：Boss 怪，支持多阶段、阶段转换、专属 UI 展示（UIMonster.xlsx）
- **状态变化**：按类型初始化不同的 AI 模板和技能组
- **资源变化**：Elite/Boss 额外加载入场特效和 Boss UI 资源
- **UI 反馈**：Elite/Boss 有独立血条样式和名称展示
- **异常边界**：未知 BattleUnitType 降级为 Common 处理
- **落地点**：`Monster.xlsx` BattleUnitType 字段驱动，`MonsterManager.CreateMonster()` 分支

### R-03: Boss 多阶段机制
- **触发条件**：Boss 血量首次进入某阶段阈值时
- **前置限制**：Boss 的阶段阈值和阶段技能组已在配置中定义
- **操作流程**：
  1. Boss 当前 HP 降至 Phase 2 阈值（如 60%）→ 触发阶段转换
  2. 阶段转换动画播放 → Boss 进入短暂无敌（防止转换期间死亡）
  3. 切换至新阶段的 SkillGroup（技能组更换，可能增加新技能）
  4. 阶段转换结束后移除无敌，恢复正常战斗
  5. 重复至所有阶段结束或 Boss 死亡
- **状态变化**：Phase1 → Transition → Phase2 → Transition → ... → PhaseN
- **资源变化**：技能组切换、阶段转换动画播放
- **UI 反馈**：Boss 血条在阶段节点有分段标记，阶段转换时播放 CutIn 动画
- **异常边界**：HP 在转换动画期间若继续受伤，伤害缓存在无敌移除后计算；若 HP 一次性跨越多个阶段阈值，依次播放转换但压缩动画时长
- **落地点**：`BossPhaseComponent.OnHpThresholdReached(phaseIndex)` 驱动阶段切换

### R-04: Boss 专属 UI 与演出
- **触发条件**：Boss 进入战斗、阶段转换、释放技能时
- **前置限制**：UIMonster.xlsx 已配置该 Boss 的展示信息
- **操作流程**：
  - 入场：读取 MonsterSpine（骨骼动画）和 MonsterModal（模型展示），播放 Boss 登场演出
  - 阶段转换：读取 MonsterSkill 列表中的阶段技能图标，高亮当前阶段可用技能
  - UI 持久：Boss 专属血条样式（与普通怪区分）、技能提示预警区域
- **状态变化**：UI 层 BossHUD 进入/退出
- **资源变化**：加载 MonsterSpine 动画资源、专用 UI 预制体
- **UI 反馈**：大面积 Boss 血条、技能预警红圈/箭头、阶段转换 CutIn 全屏动画
- **异常边界**：UIMonster 未配置 → 使用默认 Boss UI 模板；MonsterSpine 资源缺失 → 降级为静态图
- **落地点**：`UIMonster.xlsx` → `BossUIController` → 运行时 BossHUD

### R-05: AI 行为树关联
- **触发条件**：怪物实例化后激活 AI 组件
- **前置限制**：Monster.xlsx 中 MonsterAi 字段指向有效 AI 配置 ID
- **操作流程**：
  1. 怪物创建时，根据 MonsterAi 字段加载对应的 AI 配置（BehaviorTree / AIConfig）
  2. AI 行为树接管怪物的决策循环：Idle → Patrol → DetectTarget → Chase → Attack → 返回 Idle
  3. 行为树中的技能释放节点引用 Monster.SkillGroup 中的技能
- **状态变化**：AI 状态机随条件切换（巡逻 → 发现玩家 → 追击 → 攻击 → 脱离 → 回归）
- **资源变化**：AI 内部计时器运转
- **UI 反馈**：巡逻/警戒/战斗状态在怪物头顶有对应图标（可选）
- **异常边界**：MonsterAi 指向不存在的 AI 配置 → 使用默认 AI 模板（基础巡逻+攻击）；AI 行为树陷入死循环时，watchdog 检测并强制重置 AI 状态
- **落地点**：`MonsterAi` 字段 → `AIManager.LoadBehaviorTree(aiConfigId)` → 怪物实体挂载 AIComponent

### R-06: 召唤怪物配置
- **触发条件**：Boss 或精英怪释放 SummonMonster 技能时
- **前置限制**：SummonMonster.xlsx 中已配置召唤物信息，召唤力能动作指向有效 MonsterId
- **操作流程**：技能中 SummonAction 触发 → 读取 SummonMonster.xlsx 获取召唤物属性与行为 → 在指定位置实例化怪物 → 召唤物继承召唤者的阵营
- **状态变化**：召唤物 Idle → 按自身 AI 行动
- **资源变化**：场景中新增怪物实体，消耗内存和渲染资源
- **UI 反馈**：召唤物出现播放召唤特效，召唤物血条样式与普通怪一致
- **异常边界**：召唤物 MonsterId 无效 → 跳过召唤并记 warning；召唤上限（如 5 个）达到时新召唤替换最旧的
- **落地点**：`SummonMonster.xlsx` → `SummonAction.Execute()` → `MonsterManager.CreateMonster()`

### R-07: 系统定制属性修正
- **触发条件**：怪物进入特定玩法系统（Rogue / Story / Dungeon）时
- **前置限制**：MonsterAttributeCorrect.xlsx 中已配置该系统对该怪物类型的倍率
- **操作流程**：关卡启动时读取该系统所有怪物修正倍率 → 加载入内存字典（Key = 系统枚举 + 怪物类型）→ 怪物创建时结合基础属性计算最终属性
- **状态变化**：无
- **资源变化**：无（纯计算）
- **UI 反馈**：调试面板可显示系统修正后属性与原始属性的对比
- **异常边界**：系统无对应修正 → 使用倍率 1.0（等于不修正）；同一怪物在多个系统中不存在（怪物实例仅绑定一个关卡系统）
- **落地点**：`MonsterAttributeCorrect.xlsx` → `SystemMultiplierManager.GetMultiplier(system, monsterType)`
