# ARENA-SCORE-CHG010

日期：2026-08-31。对应沉淀变更 `CHG-010`（`03_沉淀MD/经济/11_外循环_任务_03_开服挑战经济沉淀-2026-07-09.md`）。

用户要求：七日活动竞技场历史最高分目标改为第1~7天分别 1100/1200/1300/1400/1500/1600/1700 分。

## 变更矩阵

| 文件 | ID | 字段 | 旧值 | 新值 |
|---|---|---|---|---|
| 任务/Task.xlsx | 5105 | TaskName/TaskDesc | 竞技场历史最高达到1200分 | 竞技场历史最高达到1100分 |
| 任务/Task.xlsx | 5205 | TaskName/TaskDesc | 竞技场历史最高达到1250分 | 竞技场历史最高达到1200分 |
| 任务/Task.xlsx | 5605 | TaskName/TaskDesc | 竞技场历史最高达到1550分 | 竞技场历史最高达到1600分 |
| 任务/Task.xlsx | 5705 | TaskName/TaskDesc | 竞技场历史最高达到1600分 | 竞技场历史最高达到1700分 |
| 任务/TaskTarget.xlsx | 5105 | TargetDesc/ParamList | …1200分 / 0,1200 | …1100分 / 0,1100 |
| 任务/TaskTarget.xlsx | 5205 | TargetDesc/ParamList | …1250分 / 0,1250 | …1200分 / 0,1200 |
| 任务/TaskTarget.xlsx | 5605 | TargetDesc/ParamList | …1550分 / 0,1550 | …1600分 / 0,1600 |
| 任务/TaskTarget.xlsx | 5705 | TargetDesc/ParamList | …1600分 / 0,1600 | …1700分 / 0,1700 |

5305/5405/5505（1300/1400/1500）本就符合新曲线，不改。奖励、DropId、UnlockId=4112 均不变。

## 执行与验收

- `python apply_arena_score_chg010.py`：备份 → 改 16 格 → `plan.json` → 逐格对比（计划外差异为空）→ 业务校验（7 天分数线、奖励与解锁）→ `validation.json`，status=PASS。
- 产物：`05_验算核算/七日竞技场分数CHG010_20260831/`（backup/、plan.json、validation.json）。
- `scripts/check.ps1`：FAIL 0（仅 2 条与本批次无关的旧文档长度 WARN）。
- 范围：仅 `06_最终配置` 候选与沉淀MD。

## SVN 落表（2026-08-31，用户授权）

`python land_svn_chg010.py`：把同样 16 格落入 `${VGAME_CONFIG_DATAS}/task/Task.xlsx`、`TaskTarget.xlsx`。SVN Task.xlsx 比 06 多 `Target` 列，列位置按表头名定位。产物：同目录 `backup-svn/`、`plan-svn.json`、`validation-svn.json`（PASS）。落表后 `svn status` 仅这两个文件 M；**未执行 `svn commit`，由用户复核后提交**。

首次执行曾因 TaskDesc 赋值逻辑错误把 SVN Task.xlsx 4 行 TaskDesc 清空，已从 `backup-svn/` 恢复（`svn status` 验证干净）后修正重跑；以 `plan-svn.json`/`validation-svn.json` 的最终结果为准。
