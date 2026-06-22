# Vgame 配置 Schema 地图

## 核心 schema 文件

| 文件 | 作用 |
|---|---|
| `Datas/__tables__.xlsx` | 逻辑表定义、数据模型、是否生成、输入 Excel 文件名。 |
| `Datas/__beans__.xlsx` | 复合字段结构，例如 `PropType`。 |
| `Datas/__enums__.xlsx` | 枚举定义，例如 `droptype`、`LevelTypeEnum`。 |

## Excel 表头约定

| 行 | 含义 |
|---|---|
| row 1 `##var` | 字段名。 |
| row 2 `##type` | 字段类型。 |
| row 3 `##group` | 导出分组，例如客户端 `c`、服务端 `s`。 |
| row 4 `##` | 策划注释。 |
| row 5+ | 数据。 |

## 已确认逻辑表

| 逻辑表 | DataModel | 输入文件 | 说明 |
|---|---|---|---|
| `Drop` | `DropDataModel` | `Drop_draw.xlsx`, `Drop_dungeon.xlsx`, `Drop_mainlevel.xlsx`, `Drop_other.xlsx`, `Drop_GiftBox.xlsx`, `Drop_TimeLimitedActivity.xlsx`, `Drop_world.xlsx`, `Drop_BattlePass.xlsx` | 逻辑掉落表，由多个源文件合并。 |
| `UILevel` | `UILevelDataModel` | `UILevel.xlsx` | 关卡 UI、奖励预览、DropId 引用。实际路径为 `Datas\level\UIlevel.xlsx`。 |

## 常用 bean

`PropType` in `__beans__.xlsx`：

| 字段 | 类型 | 说明 |
|---|---|---|
| `PropId` | `int` | 道具 ID。 |
| `PropNum` | `long` | 数量。 |

在 Excel 数组字段中常见格式：`itemId,qty;itemId,qty`。例如 `1,30000`、`101,-1;100,-1;4,-1`。

## 常用 enum

`droptype`：

| 名称 | 值 | 说明 |
|---|---:|---|
| `drop_Invalid` | 0 | 无效类型 |
| `random` | 1 | 随机掉落 |
| `fixed_` | 2 | 固定掉落 |
| `fixed__random` | 3 | 固定+随机掉落 |

`LevelTypeEnum` 已观察关键项：

| 名称 | 值 | 说明 |
|---|---:|---|
| `LevelType_Main` | 1 | 主线 |
| `LevelType_Exp` | 2 | 角色经验本 |
| `LevelType_Gold` | 3 | 金币本 |
| `LevelType_Strategy_First` | 10 | 旅券副本 1 |
| `LevelType_Strategy_Second` | 11 | 旅券副本 2 |
| `LevelType_Strategy_Three` | 12 | 旅券副本 3 |
| `LevelType_Strategy_Four` | 13 | 旅券副本 4 |
| `LevelType_WeaponExp` | 24 | 专武经验副本 |
| `LevelType_SpecialEquipment` | 31 | 映射装备本 |
| `LevelType_SpecialEquipmentGem` | 32 | 映射装备宝石本 |
| `LevelType_SpecialEquipmentChip` | 33 | 映射装备铭文本 |
| `LevelType_PVPVE` | 36 | PVPVE 关卡 |
| `LevelType_Main_Difficult` | 37 | 主线高难 |
| `LevelType_RougeLike` | 39 | 肉鸽关卡 |

## Drop 字段快照

源文件：`Datas\Drop\Drop_dungeon.xlsx`，sheet `Drop`。

关键字段：

- `ID`: 表 ID，常见公式 `=ROW()+200000-4`
- `DropId`: 掉落包 ID
- `DropName`: 掉落名
- `DropId2`: 二级掉落 ID
- `DropType`: `droptype`
- `DropMinNum` / `DropMaxNum`: 掉落次数范围
- `DropItem_id`: 道具 ID
- `DropItemNumMin` / `DropItemNumMax`: 道具数量范围
- `DropWeight`: 权重
- `ShowItemID`: 掉落预览道具 ID 数组
- `IsValid`: Drop 中为无效/占位字段；不要用于判断 Drop 行是否有效

## UIlevel 字段快照

源文件：`Datas\level\UIlevel.xlsx`，sheet `level`。

关键字段：

- `LevelId`: 关卡 ID
- `Name`: 名称
- `LevelType`: `LevelTypeEnum`
- `Reward`: 其他关卡掉落展示，类型 `(array#sep=;),PropType`
- `FirstReward`: 其他关卡首通展示，类型 `(array#sep=;),PropType`
- `FirstRewardDrop`: 首通奖励读取掉落表 ID
- `FallRewardDrop`: 通关奖励读取掉落表 ID
- `ThreeStarRewardDrop`: 三星奖励读取掉落表 ID
- `HighRewardDrop`: 高额奖励掉落
- `Vitality`: 挑战消耗道具，类型 `PropType?`
