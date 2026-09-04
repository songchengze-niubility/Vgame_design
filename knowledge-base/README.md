# Vgame 全栈策划知识框架 V2.0

> **唯一正式权威入口。** 正文位于本目录；Skill 正文只位于 `../skills/`；`../output/` 仅含可重新生成的网页、索引、切片和报告。

## 阅读顺序

1. [项目总览与核心循环](framework/00-项目总览与核心循环.md)
2. [系统框架](framework/10-系统框架.md)
3. [战斗规则、角色与内容](framework/20-战斗规则角色与内容.md)
4. [数值框架 V2](framework/30-数值框架V2.md) → [全栈数值知识层](numerical/README.md) → [单仓数值生产工作流](../numerical-workflows/v2/README.md)
5. [系统输入、输出、依赖和循环](framework/40-系统关系.md)
6. [Skill 注册与调用层](framework/50-Skill注册与调用.md)
7. [证据、状态、裁决与治理](framework/90-证据状态裁决与治理.md)

机器入口：`AUTHORITY.json`、`registries/skill-registry.json`、`mappings/*.json`、`numerical/*.json`、`numerical/mappings/*.json`。

任务教训与坑点收口于 `experience/`：写入时机见交付流程第 9 步（`../skills/planning-feature-workflow/SKILL.md`），门禁为 `../scripts/check_experience.py`，查询由 `../skills/vgame-knowledge-router` 在每次路由时自动带出命中条目。

数值知识与生产能力均已纳入本策划框架：原子正文、公式/参数注册及映射位于 `numerical/`；59 个生产脚本、37 份受控输入工作簿、规则、沉淀 MD 和 44 份正式数值交付文档位于 `../numerical-workflows/v2/`。正式 Excel 入口为 `../numerical-workflows/v2/framework/04_数值文档/`，随 Git 仓库交付。旧数值盘仅是迁移证据，不是运行依赖；查询按需加载原子，不复制 Skill 正文。

知识网页与索引重建：`pwsh -File scripts/knowledge-framework/rebuild.ps1`。数值终稿与动态验算重建：`python scripts/numerical-workflows/run_production.py`。网页、索引、staging 与验算报告仅落入 `output/`；44 份正式数值终稿在全部门禁通过后发布到 Git 管理的 `../numerical-workflows/v2/framework/04_数值文档/`。终验必须由独立审核对话执行。
