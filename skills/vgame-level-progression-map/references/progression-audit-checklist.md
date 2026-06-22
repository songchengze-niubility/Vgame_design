# Vgame 关卡进度只读审查清单

## 使用场景

在回答以下问题前使用：

- 某玩法什么时候开。
- 某 LevelId 属于哪个玩法。
- 某章节、主线、高难或副本链是否配置闭环。
- 某玩法涉及哪些表。
- 某配置变更会影响哪些进度、入口、体力、扫荡和奖励引用。

## 基础识别

| 检查 | 结果 |
|---|---|
| 是否属于首版正式玩法范围 |  |
| 玩法名、LevelId、LevelType 或 SystemOpen.Id 是否明确 |  |
| 是否涉及奖励实际内容 | 如涉及，转 `vgame-reward-drop-sync` |
| 是否涉及战斗难度/公式 | 如涉及，转数值/战斗相关 skill |

## LevelId 链路

| 检查 | 表/字段 |
|---|---|
| LevelId 是否存在于战斗底表 | `level.xlsx / LevelId` |
| 是否有关卡前置 | `level.xlsx / Unlock` |
| 是否有关卡类型和难度 | `level.xlsx / Type`、`Difficulty` |
| 是否可扫荡 | `level.xlsx / MopUp` |
| 体力或消耗是否配置 | `level.xlsx / Vitality`，或 `UIlevel.xlsx / Vitality` |
| 战斗数据路径是否存在 | `level.xlsx / LevelDataPath` |
| 等级和系数是否存在 | `level.xlsx / Grade`、`HpCoefficient`、`AttackCoefficient` |

## 主线/章节链路

| 检查 | 表/字段 |
|---|---|
| 主线节点是否存在 | `MainLevel.xlsx / LevelId` |
| 章节归属是否存在 | `MainLevel.xlsx / ChapterId` |
| 下一关是否配置 | `MainLevel.xlsx / NextLevel` |
| 是否 Boss 关 | `MainLevel.xlsx / IsBoss` |
| 章节是否存在 | `ChapterLevel.xlsx / ChapterId` |
| 章节解锁是否存在 | `ChapterLevel.xlsx / Unlock` |
| 高难解锁是否存在 | `ChapterLevel.xlsx / DifficultUnlock` |

## UIlevel 链路

| 检查 | 表/字段 |
|---|---|
| UIlevel 是否存在目标 LevelId | `UIlevel.xlsx / LevelId` |
| LevelType 是否符合玩法 | `UIlevel.xlsx / LevelType` |
| 是否有出现/解锁条件 | `AppearIdParamList`、`Unlock` |
| 是否有层数或刷新 | `TierNum`、`LevelRefreshType`、`RefreshNum` |
| 是否有推荐等级 | `RecommendLevel` |
| 是否有 UI 预览 | `Reward`、`FirstReward` |
| 是否引用奖励 DropId | `FirstRewardDrop`、`FallRewardDrop`、`ThreeStarRewardDrop`、`HighRewardDrop` |

奖励 DropId 是否存在和奖励内容是否正确，由 `vgame-reward-drop-sync` 继续检查。

## LevelType/SystemOpen 链路

| 检查 | 表/字段 |
|---|---|
| LevelType 是否存在 | `LevelType.xlsx / Id` |
| LevelType 分组是否正确 | `LevelType.xlsx / Group` |
| 是否有关联系统入口 | `LevelType.xlsx / SystemId` |
| 系统入口是否存在 | `SystemOpen.xlsx / Id` |
| 系统是否有效 | `SystemOpen.xlsx / IsValid` |
| 系统是否关闭 | `SystemOpen.xlsx / CloseSys` |
| 系统是否隐藏 | `SystemOpen.xlsx / HideInSys` |
| 解锁条件是否存在 | `SystemOpen.xlsx / UnlockId` -> `Unlock.xlsx / Id` |

## 常见坑

| 坑 | 处理 |
|---|---|
| 系统入口开放和关卡层级开放混淆 | `SystemOpen.UnlockId` 回答“玩法入口何时开”；`UIlevel.Unlock` 回答“具体层级何时可进”。 |
| 高层口径写“主线1-6” | 追 `Unlock.UnLockParams` 到 `level.xlsx.LevelId`，再用 `level.xlsx.Number` 确认。 |
| `UIlevel.Vitality` 与 `level.xlsx.Vitality` 不一致 | 同时报告两边值，并标记真实消耗读取逻辑待客户端/服务端确认。 |
| 奖励预览和真实 Drop 包混淆 | `Reward/FirstReward` 是展示；`FirstRewardDrop/FallRewardDrop` 是 DropId 引用；真实奖励交给 `vgame-reward-drop-sync`。 |

## 玩法专表

| 玩法 | 至少检查 |
|---|---|
| 大秘境 | `Dungeon.xlsx / DungeonId, MaxLayer`；`Layers.xlsx / DungeonId, Layer, LevelId` |
| 爬塔 | `TowerReward.xlsx / LayerLimit, SeasonDropId`；`TowerFirstReward.xlsx / Layer, DropId` |
| BOSS挑战 | `Boss_Dungeon.xlsx`，任务触发时读取字段 |
| 无限挑战 | 任务触发时从 LevelType/UIlevel 和对应玩法表深入 |
| 竞技场（PVPVE） | 任务触发时从 LevelType/UIlevel 和 Arena 表深入 |

## 输出矩阵

| 对象 | 源表 | 主键/字段 | 已观察结论 | 风险 | 下一步 |
|---|---|---|---|---|---|

风险常见值：

- `待确认源表`
- `缺解锁链`
- `缺 UIlevel`
- `缺 SystemOpen`
- `奖励引用需另查`
- `战斗难度需另查`
- `生成物非源表`

## 完成判定

可以声明“只读审查完成”的最低条件：

- 已确认目标属于正式玩法或明确标记为首版排除项。
- 已列出至少一个源表路径和关键字段。
- 若涉及开放条件，已检查 `Unlock` 或说明未找到。
- 若涉及系统入口，已检查 `SystemOpen` 或说明未找到。
- 若涉及奖励，只记录引用并转交奖励 skill。
- 所有未直接观察的信息标记为 `待确认`。
