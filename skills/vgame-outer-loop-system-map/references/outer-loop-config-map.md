# 外循环配置地图

## 根路径

| 类型 | 路径 |
|---|---|
| 源 Excel | `D:\Vgame\Config\GameConfig\Datas` |
| 逻辑表注册 | `D:\Vgame\Config\GameConfig\Datas\__tables__.xlsx` |
| 生成 JSON | `D:\Vgame\Config\GameConfig\server_json` |

生成 JSON 默认不是修改源。精确 schema 和导出链路使用 `vgame-config-schema`。

## 抽卡与卡池

| 源表 | 关键字段 | 用途 |
|---|---|---|
| `Datas\Activity\DrawCard\DrawCard.xlsx` | `Id`, `Name`, `DrawType`, `CurrencyShow`, `DropId`, `OnePrice`, `TenPrice`, `QuickPurchase`, `TenDropId` | 抽卡入口、卡池奖励、单抽/十连消耗、快捷购买。 |
| `Datas\Activity\DrawCard\DrawCardPool.xlsx` | `DrawId`, `PoolType`, `UpItemId`, `Pool`, `IsValid` | 卡池内容、UP 信息、奖池池组。 |
| `Datas\Activity\DrawCard\DrawCardWeight.xlsx` | `ID`, `DrawWeight` | 抽卡权重序列。 |
| `Datas\Drop\Drop_draw.xlsx` | Drop schema | 抽卡池奖励包候选。 |

## 商店、付费和月卡

| 源表 | 关键字段 | 用途 |
|---|---|---|
| `Datas\Shop\Shop.xlsx` | `Id`, `Name`, `IsTab`, `RelateTab`, `ViewPanel`, `RefreshType`, `CurrencyShow`, `HiddenWhenSoldOut`, `Unlock`, `ShopType` | 商店页签、刷新、解锁、展示货币。 |
| `Datas\Shop\ShopGoods.xlsx` | `Id`, `Name`, `ShopId`, `ItemId`, `Num`, `PayProduct`, `PriceType`, `Price`, `Discount`, `LimitType`, `LimitNum`, `Unlock`, `IsValid` | 商品产出、价格消耗、限购、付费商品。 |
| `Datas\Pay\PayProducts.xlsx` | `Price`, `ProductType`, `RelateId` 等 | 付费商品候选，任务触发时读 schema。 |
| `Datas\MonthCard\MonthCard.xlsx` | `Price`, `PayProductId`, `CostItem`, `firstReward`, `dailyReward`, `FirstRewardShow`, `DailyRewardShow`, `TotalReward`, `PowerLimitUP` | 月卡价格、立得/每日奖励、展示奖励和体力上限。 |

## 任务、活跃和战令

| 源表 | 关键字段 | 用途 |
|---|---|---|
| `Datas\task\Task.xlsx` | `Id`, `TaskName`, `TaskType`, `TaskTarget`, `UnlockId`, `DropId`, `NextTaskList`, `AutomaticGetReward` | 任务奖励、任务链、自动领取。 |
| `Datas\task\DailyTask.xlsx` | `Task`, `Tag`, `TagTaskNum`, `Weight` | 日常任务池。 |
| `Datas\task\WeeklyTask.xlsx` | `TaskID` | 周常任务集合。 |
| `Datas\task\DailyActiveReward.xlsx` | `ActivePoint`, `RewardId` | 日活跃阶段奖励。 |
| `Datas\task\WeeklyReward.xlsx` | `ActivePoint`, `RewardId` | 周活跃阶段奖励。 |
| `Datas\Battlepass\BattlePass.xlsx` | `OpenTime`, `RewardItemPreview`, `BasicEditionPayProduct`, `BasicEditionReward`, `AdvancedEditionReward`, `PassRewardPreview` | 通行证周期、付费档和奖励预览。 |
| `Datas\Battlepass\BattlePassReward.xlsx` | `BattlePassID`, `TargetParam`, `CommonReward`, `PassAdditionReward`, `IsSignificanceLevel` | 通行证免费/付费奖励引用。 |
| `Datas\Battlepass\BattlePassLevel.xlsx` | `Lv`, `UpgradeCostExp` | 通行证等级经验需求。 |

## 签到、活动和邮件

| 源表 | 关键字段 | 用途 |
|---|---|---|
| `Datas\SignInReward\DailySign.xlsx` | `month`, `day`, `rewardItems` | 每日签到直接奖励。 |
| `Datas\SignInReward\SevenDaySign.xlsx` | `ActivityId`, `OpenDay`, `ItemReward` | 七日/阶段签到奖励。 |
| `Datas\SignInReward\MonthlyAccumulate.xlsx` | `month`, `AccumulateDay`, `rewardItems` | 月累计签到奖励。 |
| `Datas\SignInReward\TravelAccumulate.xlsx` | `AccumulateDay`, `rewardItems` | 旅程/累计奖励。 |
| `Datas\Activity\Activity.xlsx` | `Id`, `ActivityName`, `ActivityType`, `UnlockId`, `AvyId`, `SystemIds`, `ActiveItemId`, `JumpId`, `IsValid` | 活动入口、开放、活跃道具、跳转。 |
| `Datas\Activity\ActiveReward.xlsx` | `ActivityId`, `ActivePoint`, `RewardId` | 活动活跃奖励。 |
| `Datas\Activity\DoubleDropActivity.xlsx` | `DoubleCount`, `ActivityType`, `OpenType`, `SystemIds`, `TypeUnLock1`, `TypeUnLock2`, `JumpId1`, `JumpId2` | 双倍掉落活动。 |
| `Datas\Activity\FourteenDayActivity.xlsx` | `ActivityId`, `OpenDay`, `TaskList` | 14 日活动任务列表。 |
| `Datas\mail\Mail.xlsx` | `Id`, `Title`, `Text`, `ExpirationTime` | 邮件文本和期限。 |
| `Datas\mail\PresendMail.xlsx` | `Unlock`, `MailId`, `Drop`, `IsValid` | 预发邮件奖励引用。 |

## 补充入口

| 源表 | 用途 |
|---|---|
| `Datas\Player\PlayerLv.xlsx` | 玩家等级经验、升级体力和升级奖励。 |
| `Datas\items\ItemAccess.xlsx` | 获取途径展示和跳转线索，不等于真实产出。 |
| `Datas\items\TopAssets.xlsx` | UI 顶部资产展示，不等于产销。 |
| `Datas\items\ItemSweep.xlsx` | 扫荡相关道具展示/关联，实际掉落仍查关卡和 Drop。 |

## 字段判断

- `Reward/FirstReward/RewardItemPreview/PassRewardPreview` 常是展示或预览。
- `DropId/RewardId/CommonReward/PassAdditionReward/Drop` 需要展开到逻辑 Drop。
- `Price/OnePrice/TenPrice/CostItem/rewardItems/ItemReward` 多为 `PropType` 或其数组。
- `Unlock/UnlockId/SystemIds/JumpId/GotoId` 需要结合 `vgame-level-progression-map`。
