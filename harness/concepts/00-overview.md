# Harness Engineering 概览

Vgame 的 harness 目标是把策划、数值、配置、战斗、外循环协作中的隐性规则变成显性约束。

## Harness 是什么

传统文档回答“我们知道什么”。Harness 进一步回答：

- 智能体应该从哪里开始读。
- 哪些规则不能被随手绕过。
- 哪些检查可以机械化。
- 设计、提案、任务如何流转。
- 经验、坑点和债务如何回收。

## 核心理念索引

| 文档 | 作用 |
|---|---|
| `01-repo-as-source-of-truth.md` | 仓库即记录系统 |
| `02-mechanical-enforcement.md` | 用脚本守护不变量 |
| `03-throughput-changes-merge.md` | 高吞吐协作下的小步合并 |
| `04-entropy-management.md` | 定期回收设计和配置熵 |
| `05-design-proposal-task.md` | Design -> Proposal -> Task 流程 |

## Vgame 初版结构

```text
<Vgame_design 仓库>/
  AGENTS.md
  CLAUDE.md
  ARCHITECTURE.md
  DESIGN.md
  golden-principles.md
  harness/
  design/
  proposals/
  tasks/
  plans/
  knowledge-graph/
  scripts/check.ps1
```
