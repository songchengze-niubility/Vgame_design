# Vgame 关卡配置地图

## 核心关卡链路表

| 逻辑表/源表 | 路径 | 职责 |
|---|---|---|
| `level` / `level.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\level.xlsx` | 战斗关卡底表。 |
| `MainLevel` / `MainLevel.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\MainLevel.xlsx` | 主线/高难关卡在章节地图上的节点。 |
| `ChapterLevel` / `ChapterLevel.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\ChapterLevel.xlsx` | 章节信息、章节解锁和高难章节解锁。 |
| `UILevel` / `UIlevel.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\UIlevel.xlsx` | 玩法 UI 层级、关卡展示、奖励预览和 DropId 引用。 |
| `LevelType` / `LevelType.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\LevelType.xlsx` | LevelType 分组、系统入口、结算 UI、默认展示奖励。 |
| `LevelCondition` / `LevelCondition.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\LevelCondition.xlsx` | 三星/关卡条件。 |
| `ChapterStarReward` / `ChapterStarReward.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\ChapterStarReward.xlsx` | 章节星级奖励 DropId。 |
| `ChapterTasks` / `ChapterTasks.xlsx` | `${VGAME_ROOT}\Config\GameConfig\Datas\level\ChapterTasks.xlsx` | 章节任务链和章节任务奖励。 |

## `level.xlsx`

Sheet: `level`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `LevelId` | `long` | 关卡 ID。 |
| `Type` | `int` | 关卡类型，注释中已观察 `1=主线关卡`。 |
| `Unlock` | `(array#sep=;),int` | 解锁需通关的前置关卡。 |
| `LevelTask` | `(array#sep=;),int` | 三星任务 ID。 |
| `FirstReward` | `int` | 首通奖励 DropId。 |
| `FallReward` | `int` | 通关奖励 DropId。 |
| `Formation` | `int` | 是否自由编队。 |
| `MopUp` | `int` | 是否可扫荡。 |
| `Vitality` | `int` | 挑战消耗体力。 |
| `LevelDataPath` | `string` | 关卡场景/战斗数据路径索引。 |
| `Grade` | `int` | 关卡等级。 |
| `HpCoefficient` / `AttackCoefficient` | `float` | 生命/攻击系数；难度平衡只记录引用，不在本 skill 定论。 |

用途：

- 查某个 LevelId 的底层战斗配置。
- 查前置关卡、体力、扫荡、首通/通关奖励引用。
- 查是否需要转入战斗配置或数值平衡任务。

## `MainLevel.xlsx`

Sheet: `MainLevel`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `LevelId` | `long` | 主线或高难关卡 ID。 |
| `ChapterId` | `int` | 所属章节。 |
| `PosX` / `PosY` | `float` | 章节地图位置。 |
| `NextLevel` | `(array#sep=;),int` | 下一关。 |
| `IsBoss` | `bool` | 是否 Boss 关卡。 |
| `LevelType` | `LevelTypeEnum` | 主线、高难等类型。 |

用途：

- 查主线关卡排序、地图节点和章节归属。
- 查普通/高难关卡在 UI 地图上的关系。

## `ChapterLevel.xlsx`

Sheet: `ChapterLevel`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `ChapterId` | `int` | 章节 ID。 |
| `ChapterName` | `string` | 章节名。 |
| `Description` | `lotext?` | 章节描述。 |
| `Unlock` | `int` | 章节解锁条件。 |
| `DifficultUnlock` | `int?` | 高难章节解锁条件。 |
| `ChapterBg` / `DifficultChapterBg` | `string` | 普通/高难背景。 |

用途：

- 查章节开放和高难开放。
- 查章节 UI 展示资源。

## `UIlevel.xlsx`

Sheet: `level`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `LevelId` | `long` | UI 关卡 ID。 |
| `Name` | `lotext?` | UI 名称。 |
| `LevelType` | `LevelTypeEnum` | 玩法/关卡类型。 |
| `LevelRefreshType` | `LevelRefreshEnum` | 刷新类型。 |
| `RefreshNum` | `int?` | 刷新次数。 |
| `TierNum` | `int?` | 层数。 |
| `WorldId` / `ChapterId` | `int` | 世界/章节归属。 |
| `AppearIdParamList` | `(array#sep=;),int` | 出现条件。 |
| `Unlock` | `(array#sep=;),int` | 关卡解锁条件。 |
| `Reward` / `FirstReward` | `(array#sep=;),PropType` | UI 预览。 |
| `FirstRewardDrop` / `FallRewardDrop` | `int` | 首通/通关奖励 DropId。 |
| `ThreeStarRewardDrop` / `HighRewardDrop` | `int` / `int?` | 三星/高额奖励 DropId。 |
| `MultiSettlementTimes` | `int` | 多倍结算次数。 |
| `Vitality` | `PropType?` | 挑战消耗。 |
| `RecommendLevel` | `int?` | 推荐等级。 |
| `LevelTask` | `(array#sep=;),int` | 三星任务。 |

用途：

- 查玩法 UI 入口中的关卡列表。
- 查 LevelType 分布、层数、体力、推荐等级、UI 奖励预览。
- 奖励实际落地转给 `vgame-reward-drop-sync`。

注意：

- 对资源副本等玩法，`UIlevel.Vitality` 可能与 `level.xlsx.Vitality` 不一致。2026-06-16 只读观察中，金币本 `UIlevel.Vitality = 3,15`，但同一批 LevelId 在 `level.xlsx` 中 `Vitality = 0`。不要只看其中一张表就断言真实消耗；需要区分 UI/入口展示、战斗底表和运行时读取逻辑。
- `UIlevel.Unlock` 可表达单个关卡层级的解锁条件，不等同于系统入口开放条件。系统入口开放优先查 `LevelType.SystemId -> SystemOpen.UnlockId -> Unlock`。

## `LevelType.xlsx`

Sheet: `LevelType`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `Id` | `LevelTypeEnum` | 对应 UILevel 的 LevelType。 |
| `Name` | `lotext?` | 类型名称。 |
| `Reward` | `(array#sep=;),PropType` | 默认展示奖励。 |
| `Group` | `LevelTypeGroup` | 类型分组。 |
| `SystemId` | `int` | 系统开放/入口 ID。 |
| `WinSettlementUI` / `LoseSettlementUI` | `string?` | 结算 UI。 |
| `BattlePauseType` | `int` | 暂停界面结算按钮规则。 |

用途：

- 从 LevelType 追踪玩法分组和系统入口。
- 查该玩法结算 UI 与入口系统。

已观察样例：

- `LevelType_Gold`：名称 `金币副本`，分组 `LevelTypeGroup_Resource`，`SystemId = 302`，`WinSettlementUI = UICoinSettlementView`，`JumpParams` 需继续追 `SystemOpen.Id = 302`。

## `LevelCondition.xlsx`

Sheet: `LevelCondition`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `Id` | `int` | 条件 ID。 |
| `ConditionType` | `LevelCondType` | 条件类型。 |
| `Condition` | `(array#sep=;),int` | 条件参数。 |
| `ConditionName` | `lotext` | 条件名称。 |

用途：

- 查关卡三星任务或任务条件含义。

## 章节奖励与任务

`ChapterStarReward.xlsx`：

| 字段 | 用法 |
|---|---|
| `Id` | 行 ID。 |
| `ChapterId` | 章节 ID。 |
| `Star` | 要求星数。 |
| `DropId` | 奖励 DropId。 |
| `IsDifficult` | 是否高难。 |

`ChapterTasks.xlsx`：

| 字段 | 用法 |
|---|---|
| `ChapterId` | 章节 ID。 |
| `DropId` | 挑战任务完成奖励。 |
| `TaskIdList` | 任务链。 |

奖励内容仍由 `vgame-reward-drop-sync` 负责查 Drop 包。

## 正式玩法入口表

| 玩法 | 入口表 | 已观察关键字段 |
|---|---|---|
| 主线/高难 | `level\MainLevel.xlsx`、`level\ChapterLevel.xlsx`、`level\level.xlsx`、`level\UIlevel.xlsx` | `LevelId`、`ChapterId`、`NextLevel`、`LevelType`、`Unlock`。 |
| 资源副本 | `level\UIlevel.xlsx`、`level\LevelType.xlsx`、`level\level.xlsx` | `LevelType_Gold`、`LevelType_Exp`、`LevelType_WeaponExp`、`Vitality`、`Reward`。 |
| 旅券副本 | `level\UIlevel.xlsx`、`level\LevelType.xlsx`、`level\level.xlsx` | `LevelType_Strategy_First/Second/Three/Four`。 |
| 映射装备副本 | `level\UIlevel.xlsx`、`level\LevelType.xlsx`、`level\level.xlsx`、`level\EquipmentLevel.xlsx`、`level\SpecialLevel.xlsx` | `LevelType_SpecialEquipment`、`LevelType_SpecialEquipmentGem`、`LevelType_SpecialEquipmentChip`。 |
| 大秘境 | `mythic_dungeon\Dungeon.xlsx`、`mythic_dungeon\Layers.xlsx` | `DungeonId`、`MaxLayer`、`LevelId`、`Layer`、`WeeklyRewardDropId`。 |
| 爬塔 | `TowerTrial\TowerReward.xlsx`、`TowerTrial\TowerFirstReward.xlsx`、其他 `TowerTrial` 表 | `LayerLimit`、`SeasonDropId`、`Layer`、`DropId`。 |
| BOSS挑战 | `BossDungeon\Boss_Dungeon.xlsx` | 需任务触发时深入字段。 |
| 无限挑战 | 需从 `LevelType`、UIlevel 和项目表继续确认 | 首版只标记入口链，任务触发时深入。 |
| 竞技场（PVPVE） | 需从 `LevelType_PVPVE`、UIlevel 和 Arena 表继续确认 | 首版只标记入口链，任务触发时深入。 |

## 使用规则

- 同时存在 `level.xlsx` 与 `UIlevel.xlsx` 时，区分“战斗底表”和“UI/玩法展示表”。
- 同时存在 `FirstReward/FallReward` 与 `FirstRewardDrop/FallRewardDrop` 时，区分“真实奖励引用”和“UI 预览”。
- 查询玩法开放时，不只看当前表；必须联动 `Unlock` 和 `SystemOpen`。
- 查询“第几关开放”这类口径时，必须把 `Unlock.UnLockParams` 追到 `level.xlsx.LevelId`，再用 `level.xlsx.Number` 确认，例如 `100106 -> Number = 1-6`。
- 查询奖励内容时，只记录 DropId 引用，并转交奖励同步 skill。
