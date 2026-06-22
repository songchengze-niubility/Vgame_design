# Source Sink Audit Checklist

Use this checklist for read-only resource audits.

## 1. 明确资源

- 确认用户说的是资源名、ItemId、DropId、RewardId、关卡奖励、商店商品，还是 UI 预览。
- 在 `Items.xlsx` 定位 `Id`, `Name`, `ItemType`, `ItemSubType`, `AccessList`, `IsValid`。
- 如果只有中文俗称，先用 `Items.Name` 和项目术语找候选，输出候选列表，不直接唯一化。

## 2. 查展示途径

- 用 `Items.AccessList` 读取 `ItemAccess.xlsx`。
- 记录 `ItemAccess.Name`, `GotoId`, `SaoDangSupport`。
- 标记：这是展示和跳转线索，不是实际产出证明。

## 3. 查真实来源

按资源类型搜索：

| 类型 | 查找字段 |
|---|---|
| Drop 奖励 | `DropItem_id`, `DropId`, `DropId2`, `DropWeight`, `ShowItemID` |
| 直接奖励 | `rewardItems`, `ItemReward`, `UpgradeGetItem`, `FirstRewardShow`, `DailyRewardShow`, `TotalReward` |
| UIlevel/关卡 | `Reward`, `FirstReward`, `FirstRewardDrop`, `FallRewardDrop`, `ThreeStarRewardDrop`, `HighRewardDrop`, `FirstReward`, `FallReward` |
| 任务 | `Task.DropId`, `DailyActiveReward.RewardId`, `WeeklyReward.RewardId` |
| 通行证 | `BattlePassReward.CommonReward`, `PassAdditionReward`, `BattlePass.*Reward*` |
| 活动 | `ActiveReward.RewardId`, `Activity.ActiveItemId`, `DoubleDropActivity.*` |
| 邮件 | `PresendMail.Drop` |
| 抽卡 | `DrawCard.DropId`, `TenDropId`, `OnePrice`, `TenPrice`, `DrawCardPool.Pool` |
| 商店 | `ShopGoods.ItemId`, `ShopGoods.Price`, `PayProduct` |

Drop 产出扫描不要按 `IsValid` 过滤；该字段在 Drop 行中为无效/占位字段。

## 4. 查消耗口

- 商店：`ShopGoods.Price` 中是否引用该资源，确认 `LimitType`, `LimitNum`, `RefreshType`, `Unlock`。
- 抽卡：`DrawCard.OnePrice`、`TenPrice` 是否消耗该资源。
- 关卡：`level.Vitality` 与 `UIlevel.Vitality` 是否涉及体力类资源；不要混用两个字段。
- 月卡/付费：`MonthCard.CostItem`, `Price`, `PayProductId`。
- 养成/制作：任务触发时查对应系统表，首版不要臆造完整消耗链。

## 5. 展开奖励引用

- 如果字段是 DropId/RewardId/CommonReward/PassAdditionReward/FirstRewardDrop/FallRewardDrop，转给 `vgame-reward-drop-sync` 展开。
- 如果字段是 `PropType` 或 `(array#sep=;),PropType`，通常可直接读成 `ItemId,Num`；仍需用 `vgame-config-schema` 确认 bean 格式。

## 6. 查开放和次数

- 系统入口开放用 `vgame-level-progression-map` 查 `LevelType -> SystemOpen -> Unlock -> level.Number`。
- 层级/关卡开放用 `UIlevel.Unlock` 或 `level.Unlock`，不要和系统入口 Unlock 混为一谈。
- 周期性来源必须确认刷新或活动周期：`Shop.RefreshType`, `BattlePass.OpenTime`, `Activity.AvyId`, `DoubleDropActivity.DoubleCount`, `Daily/Weekly` 表名和字段。

## 7. 输出风险

至少检查：

- 一次性还是重复性来源。
- 日常/周常/赛季/活动周期是否明确。
- 是否涉及付费、抽卡、元晶、体力、排行榜。
- UI 预览和真实奖励是否一致。
- 是否存在同名资源、旧玩法资源、废弃玩法资源。
- 是否需要数值模型才能判断供需是否合理。

## 8. 只读结论格式

```text
Resource:
Sources:
Sinks:
Reward references to expand:
Unlock/progression references:
Risks:
Next skill:
```

没有直接观察的部分写 `待确认`。
