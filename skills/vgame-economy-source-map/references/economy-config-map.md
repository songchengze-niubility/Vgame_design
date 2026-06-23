# Economy Config Map

## 已确认根路径

| 类型 | 路径 | 说明 |
|---|---|---|
| 源 Excel | `${VGAME_ROOT}\Config\GameConfig\Datas` | 策划源表。 |
| 逻辑表注册 | `${VGAME_ROOT}\Config\GameConfig\Datas\__tables__.xlsx` | 用于确认逻辑表和输入 Excel。 |
| 服务端 JSON | `${VGAME_ROOT}\Config\GameConfig\server_json` | 生成物，不直接当源表改。 |

精确 schema、导出链路和校验命令交给 `vgame-config-schema`。

## 物品账本

| 源表 | 已观察字段 | 用途 | 注意 |
|---|---|---|---|
| `Datas\items\Items.xlsx` | `Id`, `Name`, `ParaList`, `ItemType`, `ItemSubType`, `ItemQuality`, `Description`, `AccessList`, `NumLimit`, `RelatedId`, `IsValid` | 物品/货币主索引。 | `AccessList` 是显示途径线索，不等于真实产出。 |
| `Datas\items\ItemAccess.xlsx` | `Id`, `Name`, `GotoId`, `SaoDangSupport`, `IsValid` | 获得途径名称和跳转。 | 可辅助定位系统入口。 |
| `Datas\items\TopAssets.xlsx` | `ViewName`, `ShowName`, `ShowItemIds` | UI 顶部资产展示。 | 只表示界面展示，不表示产出或消耗。 |
| `Datas\items\ItemSweep.xlsx` | `LevelId`, `ItemId`, `Sort` | 扫荡相关道具展示/关联。 | 实际掉落仍需查关卡和 Drop。 |
| `Datas\items\ItemChest.xlsx` | `ItemId`, `ChestId` | 宝箱道具关联。 | 宝箱内容需要继续查对应配置。 |

已观察样例：

- `Items.Id=1` 为 `猎鹰金币`，`ItemSubType_Currency`，`AccessList=4`，途径指向 `ItemAccess.Id=4 金币副本`。
- `Items.Id=2` 为 `元晶`，属于高敏感付费/通用资源。
- `Items.Id=3` 为 `储能`，属于体力/行动资源。
- `Items.Id=16/17` 分别观察到日/周任务积分类资源。

## Drop 与奖励包

| 逻辑/源表 | 已观察字段 | 用途 | 注意 |
|---|---|---|---|
| `Drop` 逻辑表 | `__tables__.xlsx` 输入为多个 Drop 文件 | 全局奖励包逻辑表。 | 不要假设单个 Drop 文件就是全部。 |
| `Datas\Drop\Drop_dungeon.xlsx` | `ID`, `DropId`, `DropName`, `DropId2`, `DropType`, `DropMinNum`, `DropMaxNum`, `DropItem_id`, `DropItemNumMin`, `DropItemNumMax`, `DropWeight`, `ShowItemID`, `IsValid` | 副本/关卡类奖励包候选。 | 奖励包内容交给 `vgame-reward-drop-sync`。 |
| `Datas\Drop\Drop_mainlevel.xlsx` | 同 Drop schema | 主线奖励包候选。 | `level.xlsx` 和章节奖励会引用。 |
| `Datas\Drop\Drop_other.xlsx` | 同 Drop schema | 任务、杂项、系统奖励候选。 | 需要按 DropId 反查。 |
| `Datas\Drop\Drop_BattlePass.xlsx` | 同 Drop schema | 通行证奖励包候选。 | `BattlePassReward` 常引用。 |
| `Datas\Drop\Drop_draw.xlsx` | 同 Drop schema | 抽卡池奖励候选。 | 需要与 `DrawCard`/卡池规则共同判断。 |
| `Datas\Drop\Drop_TimeLimitedActivity.xlsx` | 同 Drop schema | 限时活动奖励候选。 | 注意活动周期和补领。 |
| `Datas\Drop\Drop_world.xlsx` | 同 Drop schema | 世界/进度奖励候选。 | 任务触发时再深入。 |
| `Datas\Drop\Drop_GiftBox.xlsx` | 同 Drop schema | 礼包/宝箱奖励候选。 | 与商品/礼包/宝箱关联时再展开。 |

## 关卡与 UIlevel 经济字段

| 源表 | 已观察字段 | 用途 | 注意 |
|---|---|---|---|
| `Datas\level\level.xlsx` | `LevelId`, `Unlock`, `Number`, `FirstReward`, `FallReward`, `MopUp`, `Vitality`, `Grade` | 战斗关卡底表、体力、扫荡、奖励引用。 | 奖励字段多为 DropId 引用。 |
| `Datas\level\UIlevel.xlsx` | `LevelId`, `LevelType`, `Unlock`, `Reward`, `FirstReward`, `FirstRewardDrop`, `FallRewardDrop`, `ThreeStarRewardDrop`, `HighRewardDrop`, `MultiSettlementTimes`, `Vitality` | UI 层奖励预览、奖励包引用、层级解锁、结算次数。 | `Reward/FirstReward` 多为预览；真实奖励看 Drop 字段。 |
| `Datas\level\ChapterStarReward.xlsx` | `ChapterId`, `Star`, `DropId`, `IsDifficult` | 章节星级奖励。 | DropId 内容另查。 |
| `Datas\level\ChapterTasks.xlsx` | `ChapterId`, `DropId`, `TaskIdList` | 章节任务完成奖励。 | 任务链和 DropId 分开查。 |

关卡开放、LevelType、Unlock/SystemOpen 关系交给 `vgame-level-progression-map`。

## 商店与付费

| 源表 | 已观察字段 | 用途 | 注意 |
|---|---|---|---|
| `Datas\Shop\Shop.xlsx` | `Id`, `Name`, `IsTab`, `RelateTab`, `ViewPanel`, `RefreshType`, `CurrencyShow`, `HiddenWhenSoldOut`, `Unlock`, `ShopType` | 商店页签、刷新、解锁、顶部货币展示。 | `Unlock` 关联 `Unlock.xlsx`。 |
| `Datas\Shop\ShopGoods.xlsx` | `Id`, `Name`, `ShopId`, `ItemId`, `Num`, `PayProduct`, `PriceType`, `Price`, `Discount`, `RandLabel`, `RandWeight`, `RandNum`, `LimitType`, `LimitNum`, `Unlock`, `IsValid` | 商品产出和价格消耗。 | `Price` 常见为 `PropType` 格式，如 `1,100`。人民币商品关注 `PayProduct`。 |
| `Datas\MonthCard\MonthCard.xlsx` | `Price`, `PayProductId`, `CostItem`, `firstReward`, `dailyReward`, `FirstRewardShow`, `DailyRewardShow`, `TotalReward`, `PowerLimitUP` | 月卡价格、立得、每日奖励、体力上限。 | 付费和长期供给高风险。 |

## 任务、活跃和通行证

| 源表 | 已观察字段 | 用途 | 注意 |
|---|---|---|---|
| `Datas\task\Task.xlsx` | `Id`, `TaskName`, `TaskType`, `TaskTarget`, `UnlockId`, `DropId`, `NextTaskList`, `AutomaticGetReward` | 任务奖励和任务链。 | `DropId` 内容需展开；不要只看任务名。 |
| `Datas\task\DailyTask.xlsx` | `ID`, `Task`, `Tag`, `TagTaskNum`, `Weight`, `IsValid` | 日常任务池。 | 与 `Task.xlsx` 的任务奖励联动。 |
| `Datas\task\WeeklyTask.xlsx` | `ID`, `TaskID` | 周常任务集合。 | 与 `Task.xlsx` 的任务奖励联动。 |
| `Datas\task\DailyActiveReward.xlsx` | `ID`, `ActivePoint`, `RewardId`, `IsValid` | 日活跃阶段奖励。 | `RewardId` 多为 DropId 类引用，需要查 Drop。 |
| `Datas\task\WeeklyReward.xlsx` | `ID`, `ActivePoint`, `RewardId`, `IsValid` | 周活跃阶段奖励。 | 周期性供给高风险。 |
| `Datas\Battlepass\BattlePass.xlsx` | `OpenTime`, `RewardItemPreview`, `BasicEditionPayProduct`, `BasicEditionReward`, `AdvancedEditionReward`, `PassRewardPreview` | 通行证配置、付费档、预览。 | 预览和真实奖励要分开。 |
| `Datas\Battlepass\BattlePassLevel.xlsx` | `Lv`, `UpgradeCostExp` | 通行证等级经验需求。 | 用于产消曲线，不单独代表奖励。 |
| `Datas\Battlepass\BattlePassReward.xlsx` | `BattlePassID`, `TargetParam`, `CommonReward`, `PassAdditionReward`, `IsSignificanceLevel` | 通行证普通/付费奖励引用。 | 观察到 `CommonReward=40000001`、`PassAdditionReward=40001001` 等 Drop 引用模式。 |

## 签到、活动、邮件

| 源表 | 已观察字段 | 用途 | 注意 |
|---|---|---|---|
| `Datas\SignInReward\DailySign.xlsx` | `month`, `day`, `rewardItems` | 每日签到直接道具奖励。 | `rewardItems` 是 `PropType` 数组。 |
| `Datas\SignInReward\SevenDaySign.xlsx` | `ActivityId`, `OpenDay`, `ItemReward` | 七日/阶段签到奖励。 | 直接奖励，仍需确认活动周期。 |
| `Datas\SignInReward\MonthlyAccumulate.xlsx` | `month`, `AccumulateDay`, `rewardItems` | 月累计签到奖励。 | 周期性供给。 |
| `Datas\SignInReward\TravelAccumulate.xlsx` | `AccumulateDay`, `rewardItems` | 旅程/累计奖励。 | 表最大行可能很大，按有效行读取。 |
| `Datas\Activity\Activity.xlsx` | `Id`, `ActivityName`, `ActivityType`, `UnlockId`, `AvyId`, `SystemIds`, `ActiveItemId`, `JumpId`, `IsValid` | 活动入口、开放、活跃道具。 | 活动奖励要结合子表和时间。 |
| `Datas\Activity\ActiveReward.xlsx` | `ActivityId`, `ActivePoint`, `RewardId`, `IsValid` | 活动活跃奖励。 | `RewardId` 内容查 Drop。 |
| `Datas\Activity\DoubleDropActivity.xlsx` | `DoubleCount`, `ActivityType`, `OpenType`, `SystemIds`, `TypeUnLock1/2`, `JumpId1/2` | 双倍掉落活动。 | 会改变重复产出效率，高风险。 |
| `Datas\Activity\FourteenDayActivity.xlsx` | `ActivityId`, `OpenDay`, `TaskList` | 14 日活动任务列表。 | 任务奖励需回查 `Task.xlsx`。 |
| `Datas\mail\Mail.xlsx` | `Id`, `Title`, `Text`, `ExpirationTime` | 邮件文本和有效期。 | 不含奖励本体。 |
| `Datas\mail\PresendMail.xlsx` | `Unlock`, `MailId`, `Drop`, `IsValid` | 预发邮件奖励引用。 | `Drop` 是奖励包引用；邮件是一次性或条件性供给。 |

## 抽卡与卡池

| 源表 | 已观察字段 | 用途 | 注意 |
|---|---|---|---|
| `Datas\Activity\DrawCard\DrawCard.xlsx` | `Id`, `Name`, `DrawType`, `CurrencyShow`, `DropId`, `OnePrice`, `TenPrice`, `QuickPurchase`, `TenDropId` | 抽卡入口、卡池奖励、单抽/十连消耗。 | `OnePrice/TenPrice` 为 `PropType`；`DropId` 查卡池掉落。 |
| `Datas\Activity\DrawCard\DrawCardPool.xlsx` | `DrawId`, `PoolType`, `UpItemId`, `Pool`, `IsValid` | 卡池角色/奖池内容。 | 概率还需看权重/规则。 |
| `Datas\Activity\DrawCard\DrawCardWeight.xlsx` | `ID`, `DrawWeight` | 抽卡权重序列。 | 概率判断交给数值审计。 |
| `Datas\Activity\DrawCard\DrawSpecialChooseGacha.xlsx` | 待任务触发时读取 | 特殊自选卡池候选。 | 不纳入默认深读。 |

## 其他经济相关候选

| 领域 | 候选表 | 说明 |
|---|---|---|
| 玩家等级 | `Datas\Player\PlayerLv.xlsx` | `UpgradeCostExp`, `UpgradeGetPhy`, `UpgradeGetItem` 会影响体力和升级奖励。 |
| 竞技场 | `Datas\Arena\ArenaWinReward.xlsx`, `ArenaRankReward.xlsx` | 胜利、排行供给。 |
| 爬塔 | `Datas\TowerTrial\TowerReward.xlsx`, `TowerFirstReward.xlsx`, `TowerRankReward.xlsx` | 首通、周期、排行供给。 |
| 大秘境 | `Datas\mythic_dungeon\WeekMaxLayerReward.xlsx`, `WeekScoreReward.xlsx`, `SeasonScoreReward.xlsx`, `SeasonRankReward.xlsx` | 周期和赛季奖励。 |
| 装备/专武 | `Datas\SpecialEquipment\SpecialEquipmentEffectDrop.xlsx`, `Datas\ExclusiveWeapon\WeaponDuplicateReward.xlsx`, `Datas\item_craft\StrategyCraft.xlsx` | 分解、掉落、制作和兑换候选。 |
| 世界/地图 | `Datas\WorldMap\WorldScheduleReward.xlsx` | 世界进度奖励候选。 |

这些表首版只做入口记录，任务触发时再深入。
