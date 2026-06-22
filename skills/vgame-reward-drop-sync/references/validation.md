# 奖励同步验证

## 必查项

- `UIlevel` 中写入的 DropId 在逻辑 `Drop` 源文件集合中存在。
- `FirstRewardDrop` 对应 `FirstReward`，`FallRewardDrop` 对应 `Reward`。
- 预览项与真实 Drop 包一致；如果只展示代表项，说明展示规则。
- 固定奖励数量使用 `DropItemNumMin = DropItemNumMax`。
- 随机奖励数量范围、权重、二级掉落符合设计。
- 未修改无关字段，例如 `LevelType`、`Vitality`、剧情、怪物、阵容和解锁条件。
- 源 Excel 保存后可重新打开。

## 当前项目自动检查缺口

已观察 `CheckRules.py` 会校验 Drop 内部数量范围、Drop 二级引用、DropItem 到 item/chest 的引用，以及 DrawCard 到 Drop 的引用。

未观察到 UIlevel 奖励 DropId 到逻辑 Drop 的自动外键规则；因此奖励任务必须手动或用脚本检查：

- `FirstRewardDrop`
- `FallRewardDrop`
- `ThreeStarRewardDrop`
- `HighRewardDrop`

随机奖励权重总和检查当前在代码中注释，不能只依赖导出成功。

## 只读观察基线

2026-06-16 对当前项目只读扫描：

- 逻辑 Drop 源文件合计观察到 2087 个 DropId。
- `UIlevel` 引用了 601 个 DropId。
- 其中 4 个未在逻辑 Drop 源表集合中找到：`60004`、`60005`、`10000001`、`10000002`。
- `UIlevel` 引用来源分布：约 450 个在 `Drop_dungeon.xlsx`，约 147 个在 `Drop_mainlevel.xlsx`。

这些基线缺口应作为历史状态记录。后续任务如果没有触碰这些 ID，不要把它们归因到本次修改。

## 建议交付格式

| LevelId | LevelType | 字段 | 旧 DropId/预览 | 新 DropId/预览 | Drop 源文件 | 验证 |
|---|---|---|---|---|---|---|

验证栏至少写：

- DropId 是否存在
- 预览是否一致
- 导出/校验命令是否已运行
