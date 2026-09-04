# ARENA-RANK-DESC-CHG011

日期：2026-08-31。对应沉淀变更 `CHG-011`（`03_沉淀MD/经济/11_外循环_任务_03_开服挑战经济沉淀-2026-07-09.md`）。

用户要求：查竞技场段位对应分数，把七日活动竞技场历史最高分任务的描述由分数改为段位名称。

## 段位依据

`${VGAME_CONFIG_DATAS}/Arena/ArenaRank.xlsx` 有效段位（Id 1~12；13~22 行首列为 `##`，按废弃候选不采用）。CHG-010 后的 7 个参数分恰为各段位最低分，因此描述改段位名与判分参数完全一致，无描述/进度错位。

## 变更矩阵（06_最终配置 相对路径，21 格）

| 文件 | ID | 字段旧值 → 新值 | ParamList（不变） |
|---|---|---|---|
| 任务/Task.xlsx | 5105 | …1100分 → 竞技场历史最高达到**黄金Ⅱ** | 0,1100 |
| 任务/Task.xlsx | 5205 | …1200分 → **黄金Ⅰ** | 0,1200 |
| 任务/Task.xlsx | 5305 | …1300分 → **铂金Ⅲ** | 0,1300 |
| 任务/Task.xlsx | 5405 | …1400分 → **铂金Ⅱ** | 0,1400 |
| 任务/Task.xlsx | 5505 | …1500分 → **铂金Ⅰ** | 0,1500 |
| 任务/Task.xlsx | 5605 | …1600分 → **钻石Ⅲ** | 0,1600 |
| 任务/Task.xlsx | 5705 | …1700分 → **钻石Ⅱ** | 0,1700 |
| 任务/TaskTarget.xlsx | 5105~5705 | TargetDesc 同步上述 7 条 | 不变 |

TaskName 与 TaskDesc 保持同文；段位名照抄 ArenaRank 原文（全角罗马数字Ⅰ/Ⅱ/Ⅲ）。奖励、DropId、UnlockId=4112 均不变。

## 执行与验收

- `python apply_arena_rank_desc_chg011.py`：备份 → 改 21 格 → `plan.json` → 逐格对比（计划外差异为空）→ 业务校验（段位描述、ParamList=段位最低分、奖励与解锁）→ `validation.json`，status=PASS。
- 产物：`05_验算核算/七日竞技场段位描述CHG011_20260831/`。
- 范围：已同步 06 最终配置与沉淀MD。

## SVN 落表（2026-08-31，用户确认后执行）

`python land_svn_chg011.py` 已执行：21 格落入 `${VGAME_CONFIG_DATAS}/task/Task.xlsx`、`TaskTarget.xlsx`，列位置按表头名定位。业务校验 PASS（段位描述、ParamList=段位最低分、UnlockId=4112 与 DropId 不变），逐格对比计划外差异为空。产物：同目录 `backup-svn/`、`plan-svn.json`、`validation-svn.json`。落表后 `svn status` 仅这两个文件 M（与 CHG-010 分数改动叠加），**未执行 `svn commit`，由用户复核后一并提交**。
