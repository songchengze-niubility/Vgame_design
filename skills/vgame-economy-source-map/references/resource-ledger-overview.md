# Resource Ledger Overview

## 定位

`vgame-economy-source-map` 负责建立 Vgame 的资源账本视角：

- 资源是谁：`ItemId`、名称、类型、子类型、是否有效。
- 从哪里来：关卡、Drop、任务、活跃、签到、活动、邮件、通行证、月卡、商店、抽卡、玩家升级等。
- 去哪里花：商店价格、抽卡价格、体力消耗、养成消耗、制作/分解、礼包/宝箱、付费购买等。
- 是否闭环：来源、消耗、开放时间、次数限制、预览字段和真实奖励是否能互相追踪。

## 资源分层

| 层级 | 常见资源 | 默认关注点 |
|---|---|---|
| 基础货币 | 猎鹰金币、元晶、储能 | 产出稳定性、消耗口、付费敏感度、体力上限/恢复 |
| 抽卡资源 | 招募券、专武抽卡资源、卡池货币 | 获取入口、价格、保底/卡池引用、付费购买 |
| 成长资源 | 玩家 EXP、角色 EXP、装备 EXP、专武/策略卡资源 | 主线/副本/任务供应、等级门槛、消耗曲线 |
| 装备资源 | 映射装备材料、宝石、芯片、装备商店货币 | 副本掉落、分解、商店、随机深度 |
| 外循环资源 | 日/周活跃点、通行证经验、活动积分、竞技场币、公会币 | 周期、刷新、重复领取、排行榜和赛季结算 |
| 付费资源 | 月卡、充值商品、付费礼包、混合价格商品 | 价格字段、付费商品 ID、立即奖励、每日奖励 |

## 默认追踪顺序

1. 从 `Datas\items\Items.xlsx` 确认 `ItemId`、`Name`、`ItemType`、`ItemSubType`、`AccessList`。
2. 用 `ItemAccess.xlsx` 解释 `AccessList` 对应的展示途径和跳转，但不要把它当真实产出。
3. 搜索 `DropItem_id`、`PropType`、`RewardId`、`DropId`、`Price`、`ItemId` 等字段。
4. 区分直接道具字段和奖励包引用字段：
   - 直接道具：常见为 `PropType` 或 `(array#sep=;),PropType`。
   - 奖励包引用：常见为 `DropId`、`RewardId`、`CommonReward`、`PassAdditionReward`、`FirstRewardDrop`、`FallRewardDrop`。
5. 对奖励包内容使用 `vgame-reward-drop-sync` 展开。
6. 对系统开放或玩法入口使用 `vgame-level-progression-map` 追踪 Unlock/SystemOpen/LevelType。
7. 对产消是否合理使用 `senior-game-economy` 或 `game-numerical-analysis` 判断。

## 输出时的口径

- 先说“已观察到什么”，再说“还要确认什么”。
- 对多来源资源，按稳定日常、周期奖励、一次性奖励、付费/商店、活动限时分类。
- 对多消耗资源，按刚性消耗、可选消耗、付费转化、随机系统消耗分类。
- 不要用“所有来源”这类结论，除非做过全表搜索并列出搜索范围。
