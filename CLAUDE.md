# Vgame Design Agent Instructions

本文件给智能体提供工作约束。`AGENTS.md` 是入口地图，`CLAUDE.md` 是执行规则。

## 读取顺序

1. 先读 `AGENTS.md`，确认任务类型。
2. 再读 `golden-principles.md`，确认不可越界的规则。
3. 涉及流程时读 `harness/concepts/05-design-proposal-task.md`。
4. 涉及 Vgame 项目知识时读 `harness/integration-guide.md`，再进入项目 skill。
5. 涉及跨仓改动时读 `CROSS-REPO-CHANGES.md`。
6. 涉及代码、配置字段或跨系统关系时读 `knowledge-graph/KG-AI-RULES.md`。

## 工作边界

- 本仓库只保存设计、提案、任务、harness、知识图谱入口和审查记录。
- 不把真实配置表复制进本仓库作为长期源。
- 不在未确认影响范围时修改 `${VGAME_ROOT}` 下的真实配置或代码。
- 分析类任务默认只读；改动类任务必须说明目标、影响范围、验证方式。
- 如果 skill 与真实配置表冲突，以真实配置表为准，并把经验补回 skill 或提案。

## 输出要求

- 用中文写设计结论。
- 结论要标明置信度：高 / 中 / 低。
- 关键判断要给出来源：文件、表、字段、skill、设计文档或脚本输出。
- 对配置链问题，要至少覆盖：源表、引用字段、下游表、风险、待确认项。
- 对战斗/数值问题，要区分公式事实、模型假设、经验权重。

## 提交前检查

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```

检查失败先修复；检查警告要在提交说明或 `tech-debt-tracker.md` 中说明。
