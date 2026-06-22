# Vgame Design Architecture

## 仓库定位

本仓库是 Vgame 的设计约束仓库，不是游戏工程仓库，也不是配置导出仓库。

它负责保存：

- 设计决策与系统说明。
- Proposal 与 Task 流程。
- Harness 规则与维护门禁。
- 跨仓变更记录。
- 知识图谱与 agent skill 的接入说明。

它不负责保存：

- 真实配置表源文件。
- Unity/客户端/服务器代码。
- 本地导出缓存、临时分析产物。

## 分层

```text
需求/问题
  -> design/                 高层设计与反推文档
  -> proposals/              已准备评审的落地方案
  -> tasks/                  可执行任务拆解
  -> ${VGAME_ROOT}          真实配置或工程变更
  -> knowledge-graph/        长期知识索引与图谱入口
```

## Vgame 设计域

| 领域 | 关注点 | 主要 skill |
|---|---|---|
| 角色与技能 | 技能机制、配置链、强度横评 | `vgame-character-kit-design-map`、`vgame-hero-skill-config-map`、`vgame-battle-tuning-helper` |
| 成长与战斗转化 | 属性、等级、升星、装备、战力口径 | `vgame-growth-combat-conversion-map` |
| 关卡与开放 | 主线、章节、LevelId、LevelType、Unlock、SystemOpen | `vgame-level-progression-map` |
| 奖励与经济 | Drop、UIlevel、道具来源去向、经济风险 | `vgame-reward-drop-sync`、`vgame-economy-source-map` |
| 外循环 | 目标、留存、养成、玩法消耗和产出 | `vgame-outer-loop-system-map` |
| 质量审查 | 配置闭环、字段引用、缺失与异常 | `vgame-config-quality-audit` |

## 数据来源优先级

1. 真实配置表和项目工程。
2. 项目专项 skill 的已整理知识。
3. 设计文档、提案、任务记录。
4. 口头信息或临时判断。

低优先级信息不能覆盖高优先级信息。若发现冲突，需要记录在 `tech-debt-tracker.md` 或新的 proposal 中。
