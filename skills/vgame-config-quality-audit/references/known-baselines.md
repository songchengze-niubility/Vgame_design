# 已知只读基线

本文件记录已经观察到的历史问题或项目约定。审查时必须说明它们存在，但不要把它们误判为本次修改造成。

## UIlevel 奖励 DropId 缺失基线

2026-06-16 只读观察：

- 逻辑 Drop 源文件合计观察到约 2087 个 DropId。
- `UIlevel` 引用了约 601 个 DropId。
- 其中 4 个 DropId 未在逻辑 Drop 源表集合中找到：
  - `60004`
  - `60005`
  - `10000001`
  - `10000002`

处理规则：

- 若本次任务没有触碰这些 ID，标记为 `known baseline`。
- 若本次任务新增引用或修改这些 ID，必须重新确认用途。

## Drop.IsValid

用户已确认：

- Drop 行中的 `IsValid` 是无效/占位字段。
- 产销扫描、奖励展开和质量审查不要按 `Drop.IsValid` 过滤。

## CheckRules.py 覆盖缺口

已观察：

- `CheckRules.py` 覆盖部分 Drop 内部规则和 DrawCard 到 Drop 的引用。
- 未观察到它自动覆盖 `UIlevel.FirstRewardDrop/FallRewardDrop/ThreeStarRewardDrop/HighRewardDrop` 到逻辑 Drop 的外键。
- 随机掉落权重总和检查存在注释，不应只依赖导出成功。

## 2026-06-16 自动审查补充基线

首版 `audit_config_quality.py` 对当前全量 `Datas` 只读扫描时，另观察到以下奖励引用未在逻辑 Drop 中找到：

- `Task.DropId`: `10000004`, `10000005`, `1040101`, `1040102`, `1040103`
- `ChapterTasks.DropId`: `50000006`

处理规则：

- 这些 ID 在全量审查中按 `known baseline` 输出为 `WARN`。
- 若本次任务触碰任务奖励、章节任务奖励或这些 DropId，必须重新确认，不得直接忽略。

## 非 Items 奖励对象

首版扫描观察到：

- `Drop.DropItem_id` 中存在宝石、装备等非 `Items.xlsx` 对象，例如 `810xx` 宝石。
- `ShopGoods.ItemId` 中存在装备等非 `Items.xlsx` 商品，例如 `52016` 等。

处理规则：

- 自动脚本按 `WARN` 输出，提示结合对应系统表复核。
- 不把这类情况直接列为阻断错误。
