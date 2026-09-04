# Maintenance Gates

## 运行方式

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```

## 初版检查项

| 检查 | 级别 | 说明 |
|---|---|---|
| 入口文件存在 | FAIL | `AGENTS.md`、`CLAUDE.md`、`ARCHITECTURE.md` 等不能缺 |
| 核心目录存在 | FAIL | `harness/`、`design/`、`proposals/`、`tasks/` 等不能缺 |
| 模板存在 | FAIL | Design、Proposal、Task 模板不能缺 |
| 待办标记扫描 | WARN | 新待办需要登记到 `tech-debt-tracker.md` |
| 大文档扫描 | WARN | 超大文档需要拆分或索引化 |
| 真实配置误提交 | WARN | `.xlsx`、`.xlsm`、`.csv` 需要确认是否只是样例 |
| 经验条目校验 | FAIL | `scripts/check_experience.py`（check.ps1 内自动调用）：`knowledge-base/experience/` 条目字段齐全、id 唯一且与文件名日期一致、refs 路径存在；正文过短或缺现象/根因为 WARN |
| 环境能力缺失 | WARN | python/git 缺失时不再静默跳过：显式 WARN 并在结果前汇总全部未执行检查，新人据此对齐维护者基线 |
| Skill 根目录检查 | WARN | 缺失时提示，不阻断本仓库维护 |

## 扩展方向

- 校验 Vgame skill 的 `SKILL.md` 与 references 完整性。
- 校验 `config.toml` skill 路由是否存在。
- 接入 `__tables__.xlsx` 注册源表扫描。
- 对 DropId、LevelId、Unlock、UIlevel 引用做只读闭环审查。
- 对角色强度产物做表头、字体、标杆偏差校验。

## 数值生产门禁（规划，2026-08-27 评审补入）

现状结论：上表检查项均为仓库卫生类；数值实质类门禁为零。按规则"某步出错的发现延迟越长、影响越大，钩子放在越上游"，沿数值生产流程补齐以下钩子：

| 流程阶段 | 钩子 | 内容 | 状态 |
|---|---|---|---|
| 设计阶段 | 假设声明模板 | 玩家画像分档、周存活率、各系统回收速率进入 design/proposal 模板必填字段，方案冻结前显式登记 | 未开始 |
| 沉淀阶段 | 口径一致性审计 | 沉淀MD ↔ 参数基线 ↔ 配置注册表三方定期对账；AI 负责审计与报告，不承担数值判定 | 未开始 |
| 落表前 | 经济沙盘门禁 | 奖励结构变更在方案冻结后、落表前运行确定性 12 周库存/通胀模拟（python 计算），通胀增速超红线即 FAIL，禁止进入最终配置 | 未开始 |
| 落表后 | 黄金数回归 | 44 份终稿发布时生成哈希与指标基线快照，下次重建自动 diff，漂移需人工裁决 | 半自动（有哈希文化，无自动比对） |
| 配置层 | 引用闭环审查 | DropId、LevelId、Unlock、UIlevel 引用只读闭环校验 | 已列入扩展方向，未实施 |

分工约束：人负责提需求、定假设、定红线阈值；脚本负责计算与卡门禁；AI 负责搭建维护工具、审计一致性、解读归档结果。中间数值环节不允许人工心算与口头裁决充当验证。
