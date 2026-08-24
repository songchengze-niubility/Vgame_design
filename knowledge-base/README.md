# Vgame 项目级策划知识框架 V1.0

> **唯一正式权威入口。** 正文位于本目录；Skill 正文只位于 `../skills/`；`../output/` 仅含可重新生成的网页、索引、切片和报告。

## 阅读顺序

1. [项目总览与核心循环](framework/00-项目总览与核心循环.md)
2. [系统框架](framework/10-系统框架.md)
3. [战斗规则、角色与内容](framework/20-战斗规则角色与内容.md)
4. [数值框架 V2](framework/30-数值框架V2.md)
5. [系统输入、输出、依赖和循环](framework/40-系统关系.md)
6. [Skill 注册与调用层](framework/50-Skill注册与调用.md)
7. [证据、状态、裁决与治理](framework/90-证据状态裁决与治理.md)

机器入口：`AUTHORITY.json`、`registries/skill-registry.json`、`mappings/*.json`。

重建：`pwsh -File scripts/knowledge-framework/rebuild.ps1`。终验必须由独立审核对话执行。
