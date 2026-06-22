# Drop/UIlevel 奖励规则

## 真实奖励与 UI 展示

| 表 | 作用 |
|---|---|
| 逻辑 `Drop` | 真实奖励包。控制物品、数量、掉落类型、权重、二级掉落和 DropId。 |
| `UIlevel` | 关卡引用和 UI 展示。控制关卡引用哪个 DropId，以及奖励预览显示什么。 |

`UIlevel` 引用的是逻辑 `Drop`，而不是单个 `Drop_dungeon.xlsx`。逻辑 `Drop` 由多个 Drop 源文件合并。

## Drop 字段

| 字段 | 用法 |
|---|---|
| `ID` | 行 ID。常见公式 `=ROW()+200000-4`，追加行时保持公式约定。 |
| `DropId` | 奖励包 ID。多行可以共享同一个 `DropId`，表示一个奖励包里多个掉落项。 |
| `DropName` | 策划可读名称。 |
| `DropId2` | 二级掉落 ID。 |
| `DropType` | `random`、`fixed_`、`fixed__random` 等。 |
| `DropMinNum` / `DropMaxNum` | 奖励包掉落次数范围。固定奖励常为 `1/1`。 |
| `DropItem_id` | 掉落道具 ID。 |
| `DropItemNumMin` / `DropItemNumMax` | 单项道具数量范围。固定数量时二者相等。 |
| `DropWeight` | 权重。固定奖励常见 `10000`。 |
| `ShowItemID` | 掉落预览道具 ID 数组。 |
| `IsValid` | 无效/占位字段；Drop 行有效性不要按该字段过滤或判断。 |

## UIlevel 字段

| 字段 | 用法 |
|---|---|
| `LevelId` | 关卡 ID。 |
| `LevelType` | 关卡类型。 |
| `Reward` | 普通或重复奖励 UI 预览，格式为 `itemId,qty;itemId,qty`。`-1` 常用于只显示不显示数量。 |
| `FirstReward` | 首通奖励 UI 预览。 |
| `FirstRewardDrop` | 首通奖励 DropId。 |
| `FallRewardDrop` | 通关或重复奖励 DropId。 |
| `ThreeStarRewardDrop` | 三星奖励 DropId。 |
| `HighRewardDrop` | 高额奖励 DropId。 |
| `Vitality` | 关卡消耗，`PropType?`。奖励同步时不要顺手改。 |

## 常见联动

| 需求 | Drop | UIlevel |
|---|---|---|
| 首通奖励 | 配置真实 Drop 包 | 写 `FirstRewardDrop`，同步 `FirstReward` 预览 |
| 重复奖励 | 配置真实 Drop 包 | 写 `FallRewardDrop`，同步 `Reward` 预览 |
| 预览展示调整 | 不改，除非真实奖励也变 | 只改 `Reward` 或 `FirstReward` |
| 随机奖励 | 同 DropId 多行，配置权重和数量范围 | 预览显示代表项，按项目约定确认 |

## 已观察样例

资源本：

- `LevelType_Gold`: 9 层；首通 DropId `21001001` 起；`FirstReward` 如 `1,30000`；`Reward` 如 `1,-1;4,-1`。
- `LevelType_Exp`: 9 层；首通 DropId `21001011` 起；重复 DropId `21000011` 起。
- `LevelType_WeaponExp`: 9 层；首通 DropId `21001021` 起；重复 DropId `21000021` 起。

旅券副本：

- `LevelType_Strategy_First`: 已观察 10 层；首通 DropId `20001001` 起；重复 DropId `20001101` 起。
- `LevelType_Strategy_Three`: 已观察 10 层；首通 DropId `20003001` 起；重复 DropId `20003101` 起。
- `LevelType_Strategy_Four`: 已观察 10 层；首通 DropId `20004001` 起；重复 DropId `20004101` 起。
- 枚举中存在 `LevelType_Strategy_Second`，表内样例需按实际行确认。

映射装备：

- `LevelType_SpecialEquipment`: 已观察 150 行，部分行有首通和重复 DropId，部分行仅有预览。
- `LevelType_SpecialEquipmentGem` 和 `LevelType_SpecialEquipmentChip`: 已观察有 `FirstRewardDrop = 20000000`、`FallRewardDrop = 20005101` 的共享引用。

## 固定奖励行约定

固定奖励通常使用：

- `DropType = fixed_`
- `DropMinNum = 1`
- `DropMaxNum = 1`
- `DropItemNumMin = DropItemNumMax`
- `DropWeight = 10000`

多物品固定奖励可用多行同一个 `DropId`。
