# Vgame 项目级策划知识框架：战斗内知识域审查

> 审查日期：2026-08-14  
> 审查范围：Vgame「战斗内」策划知识域  
> 审查方式：先查知识图谱定位关系，再回源核验设计文档、Excel 源表、客户端源码、序列化资源和生产工具  
> 写入边界：本报告仅写入 `output/项目级策划知识框架/research/`，未修改 `design/`

## 1. 状态口径与证据层级

本报告不把“仓库里存在文件”直接等同于“当前正式玩法”，也不把逆向设计文档直接等同于最终策划口径。

| 标记 | 含义 | 判定依据 |
|---|---|---|
| 正式 | 项目入口或核心理解资料明确列为当前正式内容 | `AGENTS.md`、`skills/vgame-core-understanding/references/current-gameplay.md` |
| 已实现 | 当前客户端源码、真实配置源表或运行时资源直接证明存在 | `${VGAME_ROOT}` 下源码、`Config/GameConfig/Datas`、Runtime `.bytes` |
| 草案 | 文档头部为 Draft，或明确为逆向梳理、待评审 | `design/*Design Doc.md` 的状态栏 |
| 评审中 | 文档状态为 InReview，不能视为最终关闭 | 设计文档状态栏 |
| 废弃/非正式 | 核心理解资料明确标为已废弃或当前非正式玩法 | `current-gameplay.md` |
| 待确认 | 证据仅能证明残留、局部实现或目标值，不能证明完整上线/验收 | 需产品、策划、配置与实机联合确认 |

证据优先级如下：

1. 项目入口与已确认项目事实；
2. 真实配置源表、当前客户端源码、当前序列化资源；
3. 已落库并完成评审的设计/提案/任务；
4. Draft / InReview 文档；
5. Skill 参考、知识图谱关系、工具模型；
6. 文件名、代码残留和生成物只能作为线索。

知识图谱仅用于导航。`depends_on` 不等于已确认外键，图谱缺边也不等于没有使用关系。关键判断均已回到真实路径核验。

## 2. 执行摘要

Vgame 战斗内域已经形成一条可运行的实现链：

`关卡/玩法入口 -> BattleSystem/BattleContext -> GameMode -> LLevelMgr/场景流送 -> Hero/Monster/Skill/Buff -> DamageStrategy -> UIBattleView/UIBattlePanel -> 结算与奖励`

当前最稳定的项目级结论是：

- 战斗形态是五人小队、成长驱动、跑酷式战斗射击；普攻与普通技能自动释放，玩家主要把握大招时机。战斗判断不能只看面板 DPS，还必须看接敌节奏、覆盖率、环境适配与目标机制。
- Hero、Monster、Boss、Skill、Buff、level、UIlevel 等源表与客户端运行链真实存在；Skill/Buff/行为树/关卡空间还包含编辑器资产到 Runtime 二进制的第二条生产链。
- 多数战斗设计文档仍为 Draft。它们适合作为结构化说明和待评审设计意图，不适合作为最终项目事实；当前源码和源表反而比这些文档更新。
- 正式玩法边界已经由核心理解资料给出，但若要形成“项目级策划知识框架”，仍缺少一份完成评审的战斗总纲，把基础规则、玩法差异、配置入口、验证标准和跨域责任统一起来。
- 发现四类显著口径漂移：Skill 数量、Skill Action 类型数、Buff Effect 类型数、护甲公式常量。任何后续策划案若直接复制旧 Design Doc 或旧 Skill 参考，都可能产生错误结论。
- 局内 UI、战斗引导、Boss/Hero Cut-in、战斗掉落 Icon 表现均有当前实现证据；其中战斗掉落 Icon 的设计文档仍是 InReview，应标为“实现存在、设计验收未关闭”。

## 3. 战斗内知识域总览

| 子域 | 当前状态 | 最可靠事实 | 主要缺口 |
|---|---|---|---|
| 核心战斗规则 | 正式定位 + 已实现；细节文档草案 | 五人小队、自动普攻/普通技能、手动大招；确定性逻辑层与表现/结算层分离 | 缺正式战斗总纲与按玩法归档的胜负/超时规则 |
| 角色战斗能力 | 已实现；角色设计源有正式/历史混杂 | Hero 表定义职业、标签、能量、技能槽、成长入口；真实角色设计以 `角色技能设计` 为主 | 英雄工作簿存在重复 ID、合并单元格、公式与异常类型，需专项清洗 |
| 敌人与 AI | 已实现；说明文档草案 | Monster/Boss/属性三层表 + 行为树资源；Boss 有阶段技能、狂暴、出生/死亡技能 | MonsterAi 与行为树资产覆盖关系、通用怪/精英/Boss 的统一模板待审计 |
| Skill / Buff | 已实现；说明文档草案 | Skill Excel 元数据指向二进制技能数据；Buff Excel 元数据 + 二进制行为 | 文档计数已落后于源码；缺面向策划的当前 Action/Effect 白名单 |
| 关卡空间与节奏 | 已实现；说明文档草案 | `level/UIlevel` 管入口，SceneData/LogicData 管局内空间；按 X 轴流送，Loop 控制波次 | 各正式玩法的 Loop 模板、距离/时长/刷怪节奏尚未形成统一正式基线 |
| 玩法战斗规则 | 正式边界清楚；分玩法文档多为草案 | 主线、资源本、旅券、映射装备、无限挑战、竞技场、爬塔、大秘境、BOSS 挑战构成当前验证面 | 部分 GameMode 映射和塔玩法复用方式待源码级确认 |
| 战斗数值与验证 | 有真实公式和工具；验收体系待固化 | 伤害管线、24000 护甲常量、TTK/生存时长、同角色同投入同场景比较 | 缺统一基准角色集、日志指标、回归门禁和版本化实测结果 |
| 战斗内 UI / 反馈 | 已实现；部分设计评审中 | 5 个技能位、暂停/自动、Buff、计时、Boss/Hero Cut-in、引导、胜负页、掉落图标 | UI 信息优先级、弱引导、遮挡和掉落表现的最终验收待确认 |
| 配置与生产工具 | 已实现 | Excel -> CheckRules -> Luban -> 客户端 bytes/Lua；技能/Buff/关卡另有序列化工具 | 缺统一的战斗配置变更清单与跨链一致性检查 |
| 跨域输入输出 | 边界原则明确，接口分散 | 输入来自成长、玩法、关卡、配置；输出到结算、奖励、成长、任务、UI 和分析 | 缺跨域责任矩阵与变更影响模板 |

## 4. 核心战斗规则

### 4.1 战斗定位

项目级正式定位来自核心理解资料，而不是单份 Draft 文档：

- 五人小队；
- 成长驱动；
- 跑酷式战斗射击；
- 普攻自动、普通技能自动；
- 玩家在局内最关键的主动决策是大招释放时机；
- 角色强度必须同时考虑面板、接敌节奏、技能覆盖率、地形/目标适配和玩法机制。

证据：

- `D:/Vgame_design/skills/vgame-core-understanding/references/project-profile.md`
- `D:/Vgame_design/skills/vgame-core-understanding/references/current-gameplay.md`
- `D:/Vgame_design/skills/vgame-core-understanding/references/character-kit-routing.md`

### 4.2 运行分层

当前实现适合按四层理解：

1. **入口与意图层**：Lua `BattleSystem.lua`、`BattleContext.lua` 和各类 Battle Intent 负责战前请求、队伍/关卡上下文、切场、结算与奖励衔接。
2. **确定性战斗逻辑层**：Lockstep 中的 Entity、Skill、Buff、Damage、BehaviourTree、GameMode 和 Level Loop 承担战斗规则。
3. **表现与交互层**：Lua `UIBattleView`、C# `UIBattlePanel`、Cut-in、引导、掉落 Icon、特效和音效承担玩家反馈。
4. **局后层**：BattleSystem 接收胜负、统计和奖励结果，再进入外部成长、任务与玩法进度。

关键路径：

- `D:/Vgame/HorizonFlyProject/Lua/Logic/PlayerData/Systems/Battle/BattleSystem.lua`
- `D:/Vgame/HorizonFlyProject/Lua/Logic/PlayerData/Systems/Battle/BattleContext.lua`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.GameLogic/Runtime/Combat/BattleUI/UIBattlePanel.cs`

### 4.3 伤害与命中

当前真实源表中关键全局常量为：

| 配置 | 当前值 | 含义 |
|---|---:|---|
| `CombatArmorReduceX` | 24000 | 护甲转减伤公式参数 |
| `CombatMinAttackOffset` | 0.05 | 最低保底伤害 |
| `CombatMinHitRate` | 0.1 | 最低命中率 |
| `CombatBlockBaseX` | 0.5 | 格挡基础伤害系数 |
| `CombatMaxDmgImmune` | 0.75 | 最大减伤 |
| `MinimumDamageVariance` | 0.98 | 伤害浮动下限 |
| `MaximumDamageVariance` | 1.02 | 伤害浮动上限 |

护甲段在当前运行时以目标护甲和破甲后的有效护甲计算，核心形式为：

`减伤倍率 = 1 - Armor / (Armor + CombatArmorReduceX)`

随后进入最低伤害、暴击、格挡、伤害加成、伤害减免、承伤加成、额外加成/减免等乘区。真实伤害或无需常规结算的伤害分支会绕过普通管线的一部分。

证据：

- `D:/Vgame/Config/GameConfig/Datas/globals_conf/globals_conf_cs.xlsx`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Calculation/DamageUtility.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Calculation/DamageStrategy.cs`

`design/伤害计算公式Design Doc.md` 当前为 Draft。其中结构可供阅读，但最终参数必须以源表和运行时代码为准。

### 4.4 胜负、波次与场景推进

`LLevelMgr` 已实现沿场景推进的地形/实体流送、Loop 数据管理、死亡事件统计、Boss/精英/普通怪击杀计数以及最终胜利触发。可确认的结论是“关卡空间与波次由序列化场景数据驱动，运行时按跟随者/相机位置加载与回收”。

不同玩法的失败条件、超时、守护目标和分数结算由 GameMode 与玩法逻辑补充，不能只用主线规则概括全部战斗。

证据：

- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Managers/LLevelMgr.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Mode/`

## 5. 角色战斗能力

### 5.1 配置模型

`Hero.xlsx` 当前包含 77 行、41 列，能够直接看到以下战斗域信息：

- HeroId、名称、品质；
- HeroJob、HeroClass、标签；
- 普攻/技能槽和 `SkillsPower`；
- 强化被动/主动技能入口；
- 能效属性入口；
- 初始生命、攻击、能量和预充能；
- 碰撞、站位与 Cut-in 资源；
- SkillTag 等机制标签。

英雄成长还会通过 HeroAttribute、HeroStarAttrUp、HeroEnergyEfficiencyMap、ExclWeapon、装备等表进入战斗。战斗域负责消费最终属性与技能配置，不应自行定义外循环材料、升级成本和解锁节奏。

证据：

- `D:/Vgame/Config/GameConfig/Datas/Hero/Hero.xlsx`
- `D:/Vgame_design/skills/vgame-character-kit-design-map/references/kit-composition-map.md`
- `D:/Vgame_design/skills/vgame-character-kit-design-map/references/hero-design-workbook-map.md`
- `D:/Vgame_design/skills/vgame-growth-combat-conversion-map/`（跨域路由）

### 5.2 角色设计证据边界

角色设计源工作簿 `D:/数值文档/数值文档/Vgame英雄设计.xlsx` 应按 Sheet 区分：

- `角色技能设计`：当前角色设计的主要来源；
- `角色（留档）`：历史留档，不可直接作为当前配置；
- `角色技能备忘录（后期删除）`：实现风险与备忘，不是最终规则。

该工作簿存在重复 ID、合并单元格、公式和异常类型。对任何单英雄做策划结论前，应沿 `Hero -> Skill -> SkillData -> Buff/子技能/召唤物` 回源，不应只按单行表格判断。

### 5.3 完整战斗能力链

角色能力至少应拆为：

`基础属性 -> 普攻/自动技能 -> 大招 -> 被动/强化 -> Buff/Debuff -> 召唤/子技能 -> 能量循环 -> 对群/对单/移动环境适配 -> UI 可读性`

当前技能系统能够承载位移、子弹、范围、召唤、Buff、伤害、条件与控制等动作。策划审查必须同时追踪运行时 SkillData，避免只看 `Skill.xlsx` 的展示字段。

状态判断：**配置与运行能力已实现；角色总体设计源存在；项目级角色战斗模板尚未完成数据清洗和统一验收。**

## 6. 敌人与 AI

### 6.1 敌人配置分层

真实配置形成了清晰的三层模型：

| 层 | 主要表 | 责任 |
|---|---|---|
| 单位定义 | `Monster.xlsx` | 名称、模型、攻击类型、血条、技能组、AI、碰撞、基础战斗字段 |
| 基础属性 | `MonsterAttribute.xlsx` | HP、攻击、护甲、暴击、命中、效果命中/抵抗、攻速、增伤/减伤等 |
| 类型与玩法修正 | `MonsterAttributeType.xlsx`、`MonsterAttributeCorrect.xlsx` | 属性模板与系统/玩法系数 |
| Boss 规则 | `Boss.xlsx` | Boss 等级、时间、出生技能、阶段技能组、狂暴与死亡技能 |
| UI 展示 | `UIMonster.xlsx` | 面向关卡/界面的怪物展示信息 |

源表规模快照：`Monster.xlsx` 173×31，`MonsterAttribute.xlsx` 1004×22，`MonsterAttributeType.xlsx` 18×10，`MonsterAttributeCorrect.xlsx` 212×19，`Boss.xlsx` 14×12。

`MonsterAttributeCorrect.xlsx` 中存在 `ST_Rouge` 等旧玩法行，只能视为配置残留，不能据此恢复肉鸽的正式玩法身份。

### 6.2 AI 真实实现

当前源码明确存在 `LBehaviourTreeComponent`，怪物初始化时可启用行为树；行为树节点包含血量判断、距离判断、释放技能/技能组、Boss 狂暴等逻辑。编辑器、文本和 Runtime 资源路径均存在。

证据：

- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Entities/LMonster.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/BehaviourTree/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Editor/BehaviourTree/BehaviourTreeWindow.cs`
- `D:/Vgame/HorizonFlyProject/Assets/GameResources/GameData/BehaviorTreeData/`

因此旧参考中“行为树还是 FSM 待确认”的表述已经过时。当前可确认的是行为树实现存在；尚待确认的是每个 MonsterAi/怪物 ID 到具体行为树资产的完整覆盖关系。当前观察到的 Runtime 行为树 `.bytes` 数量较少，不能仅凭数量判断错误，需做 ID 映射审计。

### 6.3 敌人设计最小闭环

敌人/Boss 设计应至少同时定义：

- 战斗角色：普通、精英、Boss、机制目标；
- 生存：HP、护甲、减伤阶段、无敌/可打断窗口；
- 输出：碰撞、普攻、技能、持续伤害、召唤；
- 行为：寻路、距离、目标选择、技能序列、阶段切换、狂暴；
- 空间：出生点、运动范围、镜头和地形适配；
- 反馈：血条、预警、受击、Cut-in、阶段提示；
- 验证：命中率、TTK、压力曲线、失败原因可读性。

`design/怪物与Boss系统Design Doc.md` 为 Draft，可作为结构索引；具体字段和行为应以当前源表/源码为准。

## 7. Skill 与 Buff

### 7.1 Skill 双层数据

`Skill.xlsx` 当前为 1407×15，包含 SkillId、名称、描述、图标、等级、类型、SP、SkillData、展示介绍和自动技能类型。`SkillData` 将展示/索引数据连接到技能运行时资产。

真实运行时资源链为：

`Skill.xlsx -> SkillEditorAsset -> SkillSerializer -> Runtime .bytes -> SkillInstance/SkillLine`

当前观察到约 3803 个技能 Runtime `.bytes`。`SkillActionBase.cs` 的 MessagePack Union 索引为 0~72，即当前源码有 **73 类 Skill Action 数据类型**。

证据：

- `D:/Vgame/Config/GameConfig/Datas/Skill/Skill.xlsx`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/SkillSystem/Actions/SkillActionBase.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Editor/SkillSystem/SkillSerializer.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/SkillSystem/SkillInstance.cs`

### 7.2 Buff 元数据与行为分离

`Buff.xlsx` 当前为 4×4，且在 `__tables__.xlsx` 注册为客户端表，字段为 Id、BuffName、Description。它真实存在，但只承载少量元数据。

Buff 行为由二进制资源定义，`BuffDataRaw` 包含配置 ID、持续时间、Buff 类型、移除类型、效果列表、表现、最大层数与叠层行为。`IBuffEffectData.cs` 的 Union 索引为 0~14，即当前源码有 **15 类 Buff Effect 数据类型**。当前观察到约 961 个 Buff Runtime `.bytes`。

`LBuffComponent` 负责添加/移除、控制免疫判断以及死亡/复活时的移除逻辑。

证据：

- `D:/Vgame/Config/GameConfig/Datas/Skill/Buff.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/__tables__.xlsx`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Entities/Buff/BuffDataRaw.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Entities/Buff/Effects/IBuffEffectData.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Entities/Components/LBuffComponent.cs`

### 7.3 已确认的文档漂移

| 主题 | 旧文档/参考口径 | 当前回源结果 | 结论 |
|---|---:|---:|---|
| Skill 表规模 | 1356 条 | 源表 1407 行（含表头/说明行） | 旧统计不可再直接引用 |
| Skill Action 类型 | 63 类 | Union 0~72，共 73 类 | 以当前源码白名单为准 |
| Buff Effect 类型 | 14 类 | Union 0~14，共 15 类 | 以当前源码白名单为准 |
| Buff Excel | 被部分参考表述为“不在 Excel” | `Buff.xlsx` 已注册，但只存元数据 | 应改为“元数据在 Excel，行为在二进制” |
| 护甲公式常量 | 个别参考写 2400 | 源表为 24000 | 24000 是当前项目事实 |

这是战斗知识域的最高优先级治理问题之一：Design Doc、Skill 参考与源码需要建立版本同步或自动提取机制。

## 8. 关卡空间与节奏

### 8.1 两层关卡数据

战斗关卡不是一张 `level.xlsx` 能完整描述，至少包含两层：

1. **入口/玩法配置层**：
   - `level.xlsx`：LevelId、类型、解锁、难度、编队、扫荡、体力、出生位置、LevelDataPath、任务、Boss、等级、怪物系数、BossId、队伍、LevelSkillId 等；
   - `UIlevel.xlsx`：世界/章节、解锁、掉落显示与真实掉落、剧情、推荐等级、任务、怪物 UI 和视觉掉落等。
2. **局内空间/逻辑层**：
   - 编辑器采集 Terrain/Scene 信息；
   - SceneData/LogicData 序列化资源定义地形、实体、出生点、Loop、触发与空间关系；
   - `LLevelMgr` 运行时按跟随位置/镜头流送和推进。

源表快照：`level.xlsx` 1374×31，`UIlevel.xlsx` 2116×43，`CameraParameter.xlsx` 28×6，`BossBattleTime.xlsx` 9×6。当前观察到约 187 个 `LogicData.bytes`。

证据：

- `D:/Vgame/Config/GameConfig/Datas/level/level.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/level/UIlevel.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/level/CameraParameter.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/level/BossBattleTime.xlsx`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.GameLogic/Editor/TerrainEditor/TerrainInfoEditor.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.GameLogic/Editor/TerrainEditor/CombatSceneCollect/TerrainDataCollector.cs`

### 8.2 节奏分析框架

局内节奏应拆成：

`进入/教学 -> 接敌距离 -> 普通波 -> 精英/机制波 -> Boss/终局 -> 结算`

每段至少观察：移动时间、交战时间、空窗、同时存活敌人数、目标切换频率、技能覆盖率、受击压力、镜头可读性和掉落/奖励反馈。Skill 参考中的时间区间可以作为初始假设，但不是当前正式运行约束，必须由具体玩法、场景数据和实机日志回证。

### 8.3 关卡知识缺口

- `design/关卡编辑器Design Doc.md` 与 `design/主线关卡系统Design Doc.md` 都是 Draft；
- 尚未形成“玩法 -> Level Type -> GameMode -> SceneData 模板 -> 胜负条件”的完整矩阵；
- 塔玩法是否复用通用模式、如何映射，没有在本轮定位到独立 `TowerMode`，应标记待确认；
- 配置表中的路径、序列化资源和客户端实际加载关系需要自动一致性检查。

## 9. 玩法战斗规则

以下“正式/废弃”来自核心理解资料；具体 Design Doc 即使为 Draft，也不会推翻玩法当前身份，但其细节仍不能直接升格为最终规则。

| 玩法 | 项目身份 | 局内战斗关注点 | 当前证据/备注 |
|---|---|---|---|
| 主线 | 正式 | 推进、波次、Boss、剧情/教学、首次通关 | `level/UIlevel` + Normal Intent/Mode；设计文档 Draft |
| 金币副本 | 正式成长入口 | 限时/金币目标、刷怪与结算效率 | `CoinMode.cs` 存在；设计文档 Draft |
| 角色经验副本 | 正式成长入口 | 生存与清怪效率、奖励节奏 | 配置和设计文档存在；文档 Draft |
| 专武经验副本 | `CONFLICT / UNKNOWN` | 清怪/限时与旧专武成长材料产出 | 核心旧口径列为正式，配置和 Draft 文档存在；但较新专武→收容物迁移尚未裁决本体与经验本是否保留，不能无条件标正式 |
| 旅券副本 | 正式 | 四类 Boss 风格战斗 | 设计文档 Draft，需逐关回源 |
| 映射装备副本 | 正式 | 短局重复刷取、效率和掉落反馈 | 正式边界来自核心资料；需补玩法专属战斗矩阵 |
| 无限挑战 | 正式验证玩法 | 普通->精英->Boss，每 3 波循环，持续压力 | `NeuralMode`/NeuralRoam Intent；设计文档 Draft |
| 竞技场 PVPVE | 正式验证玩法 | 双方同步竞速/基地与怪物压力、非纯 PVP | `PVPVEMode.cs`、竞技场配置；设计文档 Draft |
| 爬塔 | 正式验证玩法 | 混合挑战、层级推进与 Buff/机制 | 配置存在；运行时模式复用方式待确认 |
| 大秘境 | 正式验证玩法 | 28 天、多环境、长周期构筑/挑战 | 设计文档 Draft，需按版本回源 |
| BOSS 挑战 | 正式验证玩法 | 一次性 Boss 验证、阶段与爆发窗口 | Boss 配置与模式资源存在 |
| 世界 Boss | 废弃/非正式 | 不应进入当前正式框架 | 代码/配置残留不改变身份 |
| 能效本 | 废弃/非正式 | 不应作为当前成长主路径 | 仅保留历史说明 |
| 主角装备/宝石/铭文本 | 废弃/非正式 | 铭文系统已移除 | 残留不得作为正式需求 |
| 肉鸽 | 废弃/非正式 | 即使存在 `RogueMode`、`ST_Rouge` 也不是正式玩法 | 仅作为历史/技术债线索 |
| BOSS 无限挑战草案 | 非正式草案 | 不可并入当前玩法集合 | 需另行批准 |

GameMode 源码可见 `NormalMode`、`CoinMode`、`PVPMode`、`PVPVEMode`、`NeuralMode`、`MysteryMode`、`AdvancedBossMode`、`RogueMode` 等。模式类存在只证明实现/残留存在，玩法身份仍以核心确认资料为准。

## 10. 战斗数值与验证

### 10.1 验证输入

战斗验证至少需要五类输入：

- 玩家：Hero 基础属性、星级、能效、专武/装备、技能等级、Buff 与队伍组合；
- 敌人：Monster/属性模板/玩法修正/Boss 阶段/AI；
- 场景：接敌距离、移动、同时目标数、目标类型、镜头和障碍；
- 玩法：时限、失败条件、增益、波次、结算；
- 运行表现：命中、技能覆盖、能量循环、有效输出、受击、控制与失败原因。

### 10.2 基础指标

推荐统一记录：

- 理论 DPS 与有效 DPS；
- Boss/精英/普通怪 TTK；
- 玩家生存时长和容错；
- 技能覆盖率、空转率、能量溢出；
- 多目标收益与转火损失；
- 接敌/移动/无敌阶段造成的非输出时间；
- 同角色、同投入、同场景下的版本差异；
- Boss 控制按 0 收益处理，除非项目规则明确允许。

### 10.3 工具现状

`skills/vgame-battle-tuning-helper/scripts/battle_tuning.py` 可以从 `D:/数值文档/数值文档/Vgame基本战斗框架.xlsx` 读取玩家曲线、怪物标准模型和玩法难度线，执行关卡/Boss/爬塔/无限等简化评估。本轮以 `--stage 30` 验证脚本可运行，返回了玩家/怪物等级、理论 DPS、Boss TTK、生存时长和难度判断。

该结果只证明工具链可用，**不能把单次简化模型输出当作当前版本平衡结论**。脚本没有自动覆盖全部运行时 SkillData、Buff 覆盖、召唤/DOT、AOE、移动损失、AI 和实机操作。

`character_fullmax_quant.py` 适合做配置层满配估算，同样不是运行时 DPS 仿真。

### 10.4 验证门禁建议

项目级战斗门禁应至少包含：

1. 源表/生成物/运行时资源引用完整；
2. 同角色同投入同场景基准；
3. 普通、精英、Boss、多目标、移动、控制免疫、长短轴等标准场景；
4. 玩法胜负和奖励链正常；
5. 实机日志与理论模型偏差可解释；
6. UI 预警、伤害反馈、胜负原因可读；
7. 修改前后回归结果留档。

## 11. 战斗内 UI 与反馈

### 11.1 当前已实现能力

Lua `UIBattleView` 与自动生成绑定文件、C# `UIBattlePanel` 显示当前 HUD 的主要构成：

- 5 个技能/角色技能位；
- 暂停、自动战斗；
- Frenzy/时间信息；
- Buff 列表；
- 关卡技能；
- Boss Cut-in；
- 1~5 号 Hero Cut-in；
- Boss 血条、角色血量与战斗时间；
- 胜利、失败、暂停、引导等独立界面；
- BattleGuide 配置驱动的局内引导、暂停、文本和手指/高亮位置。

`BattleGuide.xlsx` 当前为 32×10，字段包含 Type、SkillPos、NeedPause、Text、IntroductionId、CircleScale、CirclePos 和备用文本。

证据：

- `D:/Vgame/HorizonFlyProject/Lua/UI/Battle/UIBattleView.lua`
- `D:/Vgame/HorizonFlyProject/Lua/UI/Battle/UIBattleView_Auto.lua`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.GameLogic/Runtime/Combat/BattleUI/UIBattlePanel.cs`
- `D:/Vgame/Config/GameConfig/Datas/Guide/BattleGuide.xlsx`

### 11.2 战斗掉落 Icon

以下实现链已存在：

- UIlevel 生成模型含 `MidVisualDropItems`、`MidVisualDropChance`、`LevelEndVisualDropItems`；
- GameOverData/VisualEndpoint 发送怪物死亡和关卡结束视觉掉落消息；
- UIBattlePanel 建池、抽取表现、显示图标并在结束时清理；
- 表现层使用随机仅影响视觉展示，不应改变真实结算。

证据：

- `D:/Vgame_design/design/战斗掉落Icon表现Design Doc.md`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.GameLogic/Runtime/Combat/BattleUI/UIBattlePanel.cs`

状态：**当前实现存在；设计文档为 InReview；最终产品验收待确认。**

### 11.3 UI 仍需回答的问题

- 自动战斗下玩家为何仍需要看懂技能与大招窗口；
- Boss 技能预警、伤害来源、控制/免疫和失败原因是否清晰；
- 五角色技能位、Buff、Boss 条、Cut-in 和掉落表现是否互相遮挡；
- 新手引导是否覆盖操作选择、跳跃/切线、大招和关卡机制；
- 无障碍、低性能和高信息密度场景是否有降级方案。

## 12. 配置与生产工具

### 12.1 Excel/Luban 主链

真实工程中存在：

- `D:/Vgame/Config/GameConfig/luban.conf`；
- `D:/Vgame/Config/GameConfig/scripts/export_excel.py`；
- `D:/Vgame/Config/GameConfig/scripts/check_rules/CheckRules.py`；
- 客户端/服务端/全部导出批处理；
- `Datas/__tables__.xlsx` 的表注册；
- 客户端 ExcelData bytes 与生成 Lua Model。

主链可概括为：

`Excel 源表 -> CheckRules -> export_excel.py -> Luban -> TempDatas/客户端 bytes/生成 Lua -> 客户端加载`

`Hero`、`Monster`、`Skill`、`Buff`、`level`、`Boss`、`UIMonster`、`TargetSkill`、`LevelSkill` 等战斗相关表均可在注册源中找到。

`design/配置表管线Design Doc.md` 虽为 Draft，但上述脚本和配置文件已经过真实路径核验，因此“生产链存在”属于当前实现事实，文档中的具体流程说明仍需与现行脚本同步。

### 12.2 二进制资产链

战斗域还有三类不能被 Excel 主链替代的生产链：

| 资产 | 编辑来源 | 序列化/采集 | Runtime 消费 |
|---|---|---|---|
| Skill | SkillEditorAsset | `SkillSerializer` | Skill `.bytes`、SkillInstance/SkillLine |
| Buff | Buff 编辑数据 | Buff Serializer | Buff `.bytes`、LBuffComponent |
| 关卡/场景 | Terrain/Combat Scene Editor | TerrainDataCollector/SceneData 序列化 | LLevelMgr、地形/实体流送 |
| AI | BehaviourTree Editor/Text | 行为树序列化 | LBehaviourTreeComponent |

### 12.3 设计仓库工具

- 知识图谱：`scripts/build_vgame_graph.py`、`check_vgame_graph.py`、`merge_vgame_graph.py`、`watch_vgame_graph.py`；
- 战斗调优：`skills/vgame-battle-tuning-helper/scripts/battle_tuning.py`；
- 角色量化：`skills/vgame-battle-tuning-helper/scripts/character_fullmax_quant.py`；
- 仓库门禁：`scripts/check.ps1`。

建议新增但本轮未实施的自动检查：

- Skill.xlsx 的 SkillData 路径到 Runtime `.bytes` 完整性；
- Buff ID/元数据到行为资源完整性；
- MonsterAi 到行为树资源完整性；
- level/UIlevel 到 SceneData/LogicData 完整性；
- LevelSkill/TargetSkill/Boss/UIMonster 的引用有效性；
- 文档自动抽取当前 Skill Action、Buff Effect 和伤害全局常量，消除手工计数漂移。

## 13. 跨域输入输出

| 相邻域 | 输入战斗域 | 战斗域输出 | 责任边界 |
|---|---|---|---|
| 角色成长 | Hero 等级、星级、能效、专武/装备、技能等级 | 最终战斗表现、角色有效性数据 | 战斗消费最终属性，不定义培养成本 |
| 关卡/内容 | Level Type、场景、波次、Boss、任务、时限 | 胜负、完成度、击杀与耗时 | 关卡定义场景/目标，战斗执行规则 |
| 玩法系统 | GameMode、玩法增益、匹配/竞赛规则 | 分数、排名输入、玩法结算事件 | 玩法身份和周期不由战斗域单独决定 |
| 经济/奖励 | Drop、首通、体力、奖励池 | 战斗结果和可结算事件 | 视觉掉落不得改变真实奖励 |
| 任务/解锁 | 进入条件、任务目标、教程状态 | 通关、击杀、用时、行为事件 | 解锁和任务持久化在局外系统 |
| UI/UX | HUD 规格、引导、Cut-in、预警资源 | 实时状态、伤害、阶段、胜负原因 | 表现层不能改变确定性战斗结果 |
| 配置生产 | Excel、Luban、序列化资源 | 运行时数据加载结果 | 真实源表不可被生成物反向覆盖 |
| 数据分析 | 埋点规范、实验分组 | TTK、失败率、技能覆盖、受击来源 | 理论模型必须由实机数据回证 |
| 版本发布 | 版本范围、资源依赖、兼容要求 | 战斗回归结果、风险清单 | 未完成门禁不得视为发布完成 |

关键跨域链：

`Design -> Proposal -> Task -> Config/Code -> Export/Serialize -> Runtime -> Telemetry/Playtest -> Design 回证`

任何战斗改动都应明确影响：Hero/Monster/Skill/Buff、Level/GameMode、UI、奖励结算和版本回归中的哪些节点。

## 14. Design 文档映射

| 设计文档 | 文档状态 | 对应知识域 | 回源结论 |
|---|---|---|---|
| `design/技能系统Design Doc.md` | Draft、逆向梳理 | Skill | 系统已实现；数量与 Action 类型统计已落后 |
| `design/Buff系统Design Doc.md` | Draft | Buff | 系统已实现；Buff Excel/Effect 类型口径需更新 |
| `design/伤害计算公式Design Doc.md` | Draft | 伤害 | 公式管线存在；常量须以 globals_conf 和源码为准 |
| `design/怪物与Boss系统Design Doc.md` | Draft | 敌人/Boss | 表与行为树实现存在；完整 ID 映射待确认 |
| `design/关卡编辑器Design Doc.md` | Draft | 场景生产 | 编辑器、采集器和 Runtime 数据存在 |
| `design/主线关卡系统Design Doc.md` | Draft、逆向待评审 | 主线 | 主线正式，文档细节仍为草案 |
| `design/金币副本Design Doc.md` | Draft | 资源副本 | 金币玩法和 CoinMode 存在，细节待评审 |
| `design/角色经验副本Design Doc.md` | Draft | 资源副本 | 玩法正式，文档细节待评审 |
| `design/专武经验副本Design Doc.md` | Draft | 资源副本 | 实现/配置证据存在；随专武→收容物迁移保持 `CONFLICT / UNKNOWN`，待裁决是否保留 |
| `design/旅券副本Design Doc.md` | Draft | Boss 型副本 | 玩法正式，需逐关回源 |
| `design/无限挑战Design Doc.md` | Draft | 持续挑战 | 玩法正式，Neural 运行模式存在 |
| `design/竞技场Design Doc.md` | Draft | PVPVE | 玩法正式，PVPVEMode 和竞技场配置存在 |
| `design/爬塔Design Doc.md` | Draft | 塔玩法 | 玩法正式，独立运行模式映射待确认 |
| `design/大秘境Design Doc.md` | Draft | 长周期挑战 | 玩法正式，具体版本规则待回源 |
| `design/新手引导系统Design Doc.md` | Draft | 战斗引导 | BattleGuide/UI 实现存在，完整引导覆盖待验收 |
| `design/战力系统Design Doc.md` | Draft | 跨域战力 | 可作为成长到战斗的接口线索，不能替代实战验证 |
| `design/配置表管线Design Doc.md` | Draft | 生产管线 | Luban/CheckRules/导出链真实存在 |
| `design/战斗掉落Icon表现Design Doc.md` | InReview | 局内反馈 | 实现链存在，最终设计/产品验收未关闭 |
| `design/PVPVE怪物伤害数值设计-2026-07-27.md` | 目标已确认、部分工程待同步 | PVPVE 数值 | 目标值可用作同步依据，Prefab/场景与实机验证仍有缺口 |

### PVPVE 数值专项快照

该文档给出的目标怪物伤害包括：

- 50001 碰撞 500；
- 50002 伤害 800；
- 50003 碰撞 200、子弹 5000301 为 300；
- 50004 伤害 200；
- 51001 碰撞 400、子弹 5100101 为 100×9；
- 51002 碰撞 1000。

竞技场怪物乘数源表当前可见：50001 为 100/100，50002 为 180/150，50003 为 5/80，50004 为 120/300，51001 为 8/180，51002 为 80/450（攻击/生命乘数口径以表头为准）。文档明确指出部分 Prefab/SceneData 尚待同步并要求 Unity 刷新与实测，因此状态应保持“目标已确认、工程/验收未完全闭环”。

证据：

- `D:/Vgame_design/design/PVPVE怪物伤害数值设计-2026-07-27.md`
- `D:/Vgame/Config/GameConfig/Datas/Arena/ArenaMonsterMultiplier.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Arena/ArenaMonsterAttribute.xlsx`

## 15. 主要缺口与优先级

### P0：建立当前事实自动同步

- 自动从源码生成 Skill Action、Buff Effect 类型清单；
- 自动从 globals_conf 生成伤害常量快照；
- 自动统计 Skill/Buff/AI/Level 资源覆盖，而不是手工写固定数量；
- 在 `scripts/check.ps1` 或专项检查中拦截文档口径漂移。

### P0：形成完成评审的战斗总纲

当前基础系统实现充分，但多数 Design Doc 为 Draft。需要一份正式总纲统一：战斗定位、属性/伤害、Skill/Buff、敌人/AI、关卡推进、玩法模式、UI 反馈、配置链和验证门禁。子文档保留细节，总纲只管理当前规则与路由。

### P1：玩法到实现映射

建立：

`正式玩法 -> LevelType -> Intent -> GameMode -> 配置表 -> SceneData 模板 -> 胜负/结算 -> 回归用例`

重点补齐爬塔复用模式、大秘境当前版本、Boss 挑战模式、映射装备副本以及各资源本的运行时映射。

### P1：AI 与关卡资源完整性

- MonsterAi/怪物 ID 到行为树资产；
- Boss 阶段配置到技能组；
- level/UIlevel 到 SceneData/LogicData；
- 关卡 Loop 类型、生成目标和胜负计数的一致性。

### P1：关闭实现已落地但设计未关闭的事项

- 战斗掉落 Icon：实现已存在，需明确评审/验收结果；
- PVPVE 怪物伤害：目标已确认，需完成 Prefab/场景同步与实机回归；
- 新手引导：配置和 UI 能力存在，需确认正式覆盖矩阵。

### P2：数值验证资产化

- 固定基准角色集、敌人集、九类标准场景与玩法压力档；
- 保存每版本模型输入、实机日志和偏差解释；
- 把有效 DPS、TTK、生存时长、覆盖率、失败原因纳入共同模板；
- 清理 `Vgame英雄设计.xlsx` 的重复 ID、异常类型和历史 Sheet 混用风险。

## 16. 建议的项目级战斗知识框架

不修改现有 `design/` 的前提下，后续可将战斗域正式知识组织成以下路由：

1. `战斗总纲`：定位、当前正式规则、证据优先级和子域路由；
2. `角色战斗能力`：能力模型、配置链、能量循环和设计验收；
3. `敌人与AI`：单位模板、属性层、行为树和 Boss 阶段；
4. `Skill与Buff`：编辑/序列化/运行时模型和当前类型白名单；
5. `关卡空间与节奏`：入口配置、SceneData、Loop、镜头与节奏指标；
6. `玩法战斗矩阵`：每个正式玩法的模式、胜负、增益、结算和回归；
7. `战斗数值与验证`：公式、基准场景、工具、日志和门禁；
8. `战斗UI与反馈`：HUD、引导、预警、Cut-in、掉落和失败可读性；
9. `配置与生产`：Excel/Luban 与 Skill/Buff/AI/Level 二进制链；
10. `跨域接口`：成长、经济、任务、UI、分析和版本发布责任矩阵。

每份文档应带：Owner、状态、最后回源日期、源表/源码路径、配置导出方式、验证用例和废弃记录。

## 17. 证据路径索引

### 项目入口与规则

- `D:/Vgame_design/AGENTS.md`
- `D:/Vgame_design/skills/vgame-core-understanding/SKILL.md`
- `D:/Vgame_design/skills/vgame-core-understanding/references/current-gameplay.md`
- `D:/Vgame_design/skills/vgame-core-understanding/references/evidence-map.md`
- `D:/Vgame_design/knowledge-graph/KG-AI-RULES.md`
- `D:/Vgame_design/knowledge-graph/.understand-anything/knowledge-graph.json`

### 专项 Skill

- `D:/Vgame_design/skills/vgame-battle-content-map/SKILL.md`
- `D:/Vgame_design/skills/vgame-level-design-map/SKILL.md`
- `D:/Vgame_design/skills/vgame-battle-tuning-helper/SKILL.md`
- `D:/Vgame_design/skills/vgame-hero-skill-config-map/SKILL.md`
- `D:/Vgame_design/skills/vgame-character-kit-design-map/SKILL.md`
- `D:/Vgame_design/skills/vgame-config-schema/SKILL.md`

### 配置源表

- `D:/Vgame/Config/GameConfig/Datas/Hero/Hero.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Skill/Skill.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Skill/Buff.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Monster/Monster.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Monster/Boss.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Monster/MonsterAttribute.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Monster/MonsterAttributeType.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Monster/MonsterAttributeCorrect.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/level/level.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/level/UIlevel.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/globals_conf/globals_conf_cs.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/Guide/BattleGuide.xlsx`
- `D:/Vgame/Config/GameConfig/Datas/__tables__.xlsx`

### 客户端实现

- `D:/Vgame/HorizonFlyProject/Lua/Logic/PlayerData/Systems/Battle/`
- `D:/Vgame/HorizonFlyProject/Lua/UI/Battle/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Calculation/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/SkillSystem/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Entities/Buff/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/BehaviourTree/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Mode/`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/Managers/LLevelMgr.cs`
- `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.GameLogic/Runtime/Combat/BattleUI/UIBattlePanel.cs`

### 工具与数值模型

- `D:/Vgame/Config/GameConfig/luban.conf`
- `D:/Vgame/Config/GameConfig/scripts/export_excel.py`
- `D:/Vgame/Config/GameConfig/scripts/check_rules/CheckRules.py`
- `D:/Vgame_design/skills/vgame-battle-tuning-helper/scripts/battle_tuning.py`
- `D:/Vgame_design/skills/vgame-battle-tuning-helper/scripts/character_fullmax_quant.py`
- `D:/数值文档/数值文档/Vgame基本战斗框架.xlsx`
- `D:/数值文档/数值文档/Vgame英雄设计.xlsx`

## 18. 审查结论

Vgame 的战斗内域不是“缺少实现”，而是“实现、配置和草案文档之间缺少一个持续同步的正式知识层”。当前最值得立即做的不是继续堆叠逆向 Design Doc，而是先固定项目级战斗总纲、玩法到实现矩阵和自动事实抽取，再让角色、敌人、Skill/Buff、关卡、UI 与数值验证各自挂到同一套证据和状态体系上。

本报告未改动 `design/`，也未把 SVN 工程中的真实配置或源码作为写入目标。
