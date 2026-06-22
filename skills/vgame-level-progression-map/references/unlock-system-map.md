# Vgame 解锁与系统开放地图

## 核心表

| 逻辑表/源表 | 路径 | 职责 |
|---|---|---|
| `Unlock` / `Unlock.xlsx` | `D:\Vgame\Config\GameConfig\Datas\unlock\Unlock.xlsx` | 解锁条件定义。 |
| `UnlockDesc` / `UnlockDesc.xlsx` | `D:\Vgame\Config\GameConfig\Datas\unlock\UnlockDesc.xlsx` | 解锁条件文案模板。 |
| `SystemOpen` / `SystemOpen.xlsx` | `D:\Vgame\Config\GameConfig\Datas\system_open\SystemOpen.xlsx` | 功能/系统开放入口、显示、跳转和可用状态。 |

## `Unlock.xlsx`

Sheet: `Unlock`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `Id` | `int` | 解锁 ID，被其他表引用。 |
| `UnLockDesc` | `string?` | 解锁描述。 |
| `UnLockType` | `UnlockType` | 解锁类型。 |
| `UnLockParams` | `(array#sep=;),long` | 解锁参数，例如关卡、等级、任务等。 |

已观察样例：

- `UnLock_UUT_Level` 可用关卡作为参数，例如主线前置。
- `UnLock_UUT_player_Grade` 可用于玩家等级解锁。

## `UnlockDesc.xlsx`

Sheet: `UnlockDesc`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `UnlockType` | `UnlockType` | 解锁类型。 |
| `UnlockDesc` | `lotext?` | 展示文案模板。 |

用途：

- 当需要解释解锁条件给玩家看时，查看该类型文案。
- 不用于直接判断功能是否开放，开放条件仍以 `Unlock.xlsx` 和引用方为准。

## `SystemOpen.xlsx`

Sheet: `SystemOpen`

关键字段：

| 字段 | 类型 | 用法 |
|---|---|---|
| `Id` | `int` | 系统 ID。 |
| `Name` | `lotext?` | 系统名称。 |
| `ParentId` | `int?` | 父系统。 |
| `CloseSys` | `bool` | 是否关闭系统。 |
| `SortId` | `int` | 排序。 |
| `HideInSys` | `bool` | 是否不显示在系统开放。 |
| `Desc` | `lotext?` | 系统描述。 |
| `UnlockId` | `int?` | 解锁条件 ID，引用 `Unlock.Id`。 |
| `EntranceResident` | `bool` | 功能按钮是否常驻。 |
| `NoPopUp` | `bool` | 是否关闭开启弹窗。 |
| `JumpId` | `int?` | 开启后跳转界面。 |
| `UIViewName` | `string` | 界面脚本名，通常与 prefab 同名。 |
| `JumpParams` | `(array#sep=;),ViewParam` | 额外跳转参数。 |
| `ForceJump` | `bool` | 是否强制跳转。 |
| `IsValid` | `bool` | 当前行是否有效。 |

## 常见引用路径

```text
LevelType.SystemId
-> SystemOpen.Id
-> SystemOpen.UnlockId
-> Unlock.Id
-> Unlock.UnLockType + Unlock.UnLockParams
```

```text
UIlevel.Unlock / UIlevel.AppearIdParamList
-> Unlock.Id 或项目约定条件
-> Unlock.UnLockType + Unlock.UnLockParams
```

```text
ChapterLevel.Unlock / ChapterLevel.DifficultUnlock
-> Unlock.Id 或关卡条件
```

具体字段是否引用 `Unlock.Id` 必须以源表注释和实际数据为准；不能只凭字段名猜。

## 已观察样例：金币副本

2026-06-16 只读观察：

```text
LevelType_Gold
-> LevelType.SystemId = 302
-> SystemOpen.Id = 302
-> SystemOpen.Name = 金币副本
-> SystemOpen.UnlockId = 4302
-> Unlock.Id = 4302
-> Unlock.UnLockType = UnLock_UUT_Level
-> Unlock.UnLockParams = 100106
-> level.xlsx.LevelId = 100106
-> level.xlsx.Number = 1-6
```

因此“金币副本主线 1-6 开放”的配置级证据链是成立的。

金币副本的层级开放另在 `UIlevel.Unlock` 中配置：

- 第 1 层 `Unlock = 1100`，对应玩家等级 10。
- 第 2 层起形如 `1101;5101`，通常是玩家等级条件 + 前一层通关条件。

不要把 `SystemOpen.UnlockId` 的系统入口开放，与 `UIlevel.Unlock` 的层级开放混成同一个条件。

## 审查规则

- 查“什么时候开”时，先确认是“系统入口开放”、 “关卡出现条件”、还是“章节/难度解锁”。
- 系统入口开放优先查 `SystemOpen.UnlockId`。
- 关卡展示/出现优先查 `UIlevel.Unlock` 和 `UIlevel.AppearIdParamList`。
- 主线章节开放优先查 `ChapterLevel.Unlock` 和 `DifficultUnlock`。
- 若 LevelType 表存在 `SystemId`，要追到 `SystemOpen`。
- 若 `SystemOpen.IsValid` 为 false 或 `CloseSys` 为 true，不能只因存在 Unlock 条件就认为系统正式开放。
- 解锁文案来自 `UnlockDesc`，但文案不等于真实条件。
- 高层口径如 `主线1-6` 必须追到实际 LevelId 和 `level.xlsx.Number`，不要用字符串相似度猜。

## 输出要求

解锁/开放问题至少输出：

| 项 | 内容 |
|---|---|
| 系统或玩法 | 玩法名、LevelType 或 SystemOpen.Id |
| 引用链 | LevelType/UIlevel/ChapterLevel -> SystemOpen/Unlock |
| 条件 | UnlockType 和参数 |
| 显示 | 是否常驻、是否弹窗、是否隐藏、是否有效 |
| 待确认 | 未查到或字段语义不确定的部分 |
