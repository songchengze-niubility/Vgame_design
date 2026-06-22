# 配置质量审查清单

## 1. 源表和注册

- 是否明确使用 `D:\Vgame\Config\GameConfig\Datas` 源 Excel。
- 是否避免直接修改 `server_json`。
- 目标逻辑表是否在 `__tables__.xlsx` 注册。
- `input` 指向的 Excel 文件是否真实存在。
- 同名输入文件是否在 `Datas` 下存在多个路径导致歧义。
- 新增配置表是否按 `vgame-config-schema/references/new-config-table-onboarding.md` 处理。

## 2. 表头和字段

- row 1 `##var` 是否仍是字段名行。
- row 2 `##type`、row 3 `##group`、row 4 注释是否保留。
- 必要字段是否存在，例如 `Id`, `ItemId`, `DropId`, `LevelId`, `Unlock` 等。
- 复合字段是否符合 `PropType` 或数组格式。

## 3. 奖励和 Drop

- 逻辑 `Drop` 是否聚合了所有 `Drop_*.xlsx` 源。
- `DropMinNum <= DropMaxNum`。
- `DropItemNumMin <= DropItemNumMax`。
- `DropItem_id` 是否存在于 `Items` 或宝箱配置；若是宝石、装备、旅券等非 `Items` 奖励对象，标记为复核项而不是直接阻断。
- `DropId2` 是否能回到逻辑 Drop。
- `UIlevel.FirstRewardDrop/FallRewardDrop/ThreeStarRewardDrop/HighRewardDrop` 是否能找到。
- `Reward/FirstReward` 是否只是 UI 预览，不当作真实奖励包。

## 4. 道具、价格和商店

- `ShopGoods.ItemId` 是否存在于 `Items.xlsx`；若售卖对象是装备、卡牌或其他非 `Items` 商品，标记为复核项而不是直接阻断。
- `ShopGoods.Price` 是否符合 `PropType` 格式。
- `DrawCard.OnePrice/TenPrice` 是否符合 `PropType` 格式。
- 高风险资源如元晶、抽卡券、付费商品、月卡、战令是否标记。

## 5. 外循环奖励引用

- `Task.DropId` 是否能找到 Drop。
- `DailyActiveReward.RewardId`、`WeeklyReward.RewardId` 是否能找到 Drop。
- `BattlePassReward.CommonReward/PassAdditionReward` 是否能找到 Drop。
- `ActiveReward.RewardId` 是否能找到 Drop。
- `PresendMail.Drop` 是否能找到 Drop。

## 6. 进度和入口

- 涉及 LevelId 时，是否由 `vgame-level-progression-map` 查关卡链。
- 涉及 SystemOpen/Unlock 时，是否区分系统入口和层级解锁。
- 涉及体力/扫荡时，是否同时关注 `level.xlsx` 与 `UIlevel.xlsx`。

## 7. 输出判定

| 判定 | 条件 |
|---|---|
| `blocked` | 存在新增断引用、缺源表、关键格式错误、无法确认源表。 |
| `ready with known baselines` | 只剩已记录历史问题，且本次未触碰。 |
| `ready for specialist review` | 结构无阻断，但需要经济/数值/奖励/进度判断。 |
| `ready` | 结构检查通过，风险和下游复核项已说明。 |
