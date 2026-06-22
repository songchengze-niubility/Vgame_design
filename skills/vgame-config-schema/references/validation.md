# Vgame 配置校验

## 自动校验入口

服务端和全量导出会调用 `scripts\check_rules\CheckRules.py`：

```powershell
cd D:\Vgame\Config\GameConfig
.\export_server.bat
.\export_all.bat
```

也可在脚本层运行：

```powershell
python scripts\export_excel.py --bat --mode s --full-check
python scripts\export_excel.py --bat --mode cs --full-check
```

## 已观察 CheckRules 覆盖

`Drop`：

- `DropMinNum <= DropMaxNum`
- `DropItemNumMin <= DropItemNumMax`
- `DropId2` 外键到逻辑 `drop.DropId`
- `DropItem_id` 外键到 `item.Id` 或 `chest.ChestId`
- `WeightSumCheck` 当前被注释，权重总和不会自动强制

`DrawCard`：

- `DropId`
- `TenDropId`
- `XiaoBaoDiId`

这些字段会外键到逻辑 `drop.DropId`。

## 当前未确认或未覆盖

- 未在 `CheckRules.py` 中观察到 `UILevel.FirstRewardDrop`、`UILevel.FallRewardDrop`、`UILevel.ThreeStarRewardDrop`、`UILevel.HighRewardDrop` 到逻辑 `drop.DropId` 的自动外键规则。
- 随机掉落的权重总和检查当前注释，需要人工或任务脚本补查。
- 2026-06-16 只读观察时，`UIlevel` 引用的 601 个 DropId 中有 4 个未在逻辑 Drop 源表集合中找到：`60004`、`60005`、`10000001`、`10000002`。这些可能是历史遗留、待补配置或特殊约定；修改奖励时必须单独说明，不要把它们当作新改动造成的问题。

## 交付前检查

- 源 Excel 能打开并保存。
- `##var`、`##type`、`##group` 未被破坏。
- 关键 ID 唯一，或符合多行共享同一业务 ID 的表约定。
- 引用字段能在目标逻辑表中找到。
- 生成 JSON 可解析，目标 ID 存在，类型与旧结构一致。
- 变更有配置影响矩阵和验证命令。
