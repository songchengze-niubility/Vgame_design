# 自动检查脚本说明

脚本路径：

```text
scripts/audit_config_quality.py
```

## 推荐命令

```powershell
python "D:\数值文档\策划agent\项目专属\Vgame\skills\vgame-config-quality-audit\scripts\audit_config_quality.py" --datas-root "D:\Vgame\Config\GameConfig\Datas" --output "D:\数值文档\策划agent\项目专属\Vgame\output\config-quality-audit.md"
```

## 检查内容

v1 覆盖：

- `__tables__.xlsx` 注册输入文件是否存在。
- 注册输入文件名是否在 `Datas` 下重名。
- 逻辑 `Drop` 聚合源是否能读取。
- Drop 数量范围、二级 Drop、掉落物品/宝箱引用；非 `Items` 奖励对象会按 `WARN` 输出，需结合对应系统表复核。
- UIlevel 奖励 DropId 引用。
- DrawCard DropId、TenDropId、OnePrice、TenPrice。
- ShopGoods ItemId 和 Price；非 `Items` 商品会按 `WARN` 输出，需结合对应商品系统表复核。
- Task、DailyActiveReward、WeeklyReward、BattlePassReward、ActiveReward、PresendMail 的奖励引用。
- PropType 基础格式和 ItemId 存在性。

## 不覆盖

- 不判断奖励数值合理性。
- 不判断活动时间最终生效逻辑。
- 不判断客户端表现和运行时特殊逻辑。
- 不修复任何问题。

## 报告等级

| 等级 | 含义 |
|---|---|
| `ERROR` | 阻断问题，通常是缺文件、断引用、格式错误。 |
| `WARN` | 需要人工确认，可能是历史基线、预览/真实字段歧义或高风险引用。 |
| `INFO` | 统计和上下文。 |

## 解释注意

- `UIlevel` 中已知历史缺失 DropId 见 `known-baselines.md`。
- `Drop.IsValid` 不参与 Drop 行过滤。
- 如果脚本输出很多历史问题，需要结合本次变更范围区分“已有问题”和“新增问题”。
