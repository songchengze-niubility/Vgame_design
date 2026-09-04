# 任务经验沉淀层（Experience）

> 本目录是驾驭工程自进化回路的收口位置：交付过程中踩过的坑、找到的根因和可复用的规避动作，
> 以受控条目形式沉淀在这里，供后续所有对话通过 `vgame-knowledge-router` 自动召回。
> 正文即权威；没有生成清单，也没有需要单独维护的索引文件。

## 自进化回路

```text
写：planning-feature-workflow 第 9 步验收后必检 -> 新增/修订 exp-*.md
     planning-change-sync 关闭变更时 -> 若坑点源于旧条目覆盖不足则更新旧条目
查：skills/vgame-knowledge-router/scripts/route_query.py -> experienceHints + readPlan 提前带出
守：scripts/check_experience.py -> 门禁校验字段完整性与 refs 存在性（check.ps1 内自动运行）
```

## 什么时候必须写

1. 交付流程第 9 步（验收）结束时发现"本次踩了坑且下次可能再踩"，无论坑多小。
2. 同一个坑第二次出现时，即使已有条目也要回头修订该条目（补触发词、根因或新证据）。
3. 没有可写的教训时，应在当次对话明确声明"本次无经验沉淀"；跳过判断本身就是禁止项。

## 条目格式

文件名：`exp-<YYYY-MM-DD>-<英文短题>.md`。正文头部使用简单键值块（不依赖 YAML 库）：

```text
---
id: EXP-YYYYMMDD-NN          # 仓库内唯一，日期段须与文件名一致
date: YYYY-MM-DD             # 首次入库日期
title: 一句话标题（含场景关键词）
category: harness|config|numerical|workflow|ui|economy|combat|process
tags: 词1, 词2               # 至少 1 个；给人工浏览看
triggerTerms: 词组A; 词组B    # 至少 1 个；给路由召回看，写成用户真实会问的措辞
status: active               # active | incorporated | obsolete
source: 来源功能/对话/变更号
refs: 相对路径1, 相对路径2   # 可选；指向受影响脚本/文档，门禁会校验存在
---
现象：...
根因：...
处理：...
规则化建议：...（何时应该想起这条经验）
```

## 生命周期

- `active`：仍然可能复发，路由持续召回。
- `incorporated`：教训已固化进 skill 正文、脚本或模板，不再需要路由提示；保留原文作证据。
- `obsolete`：条件已消失（如工具链更换），标注原因，不再召回。
- 状态改动的触发时机：某条 active 被反复命中 ≥3 次，应评估把规避动作写进对应 skill 并转 incorporated。

## 边界

- 只放"可行动的教训"；纯知识整理去 `framework/`，数值事实去 `numerical/`，一次性的方案讨论留在功能输出目录。
- 不放真实密钥、机器私有路径；涉及外部绝对路径用角色描述替代。
- 中文书写为主，但 id 与文件名保持 ASCII。
