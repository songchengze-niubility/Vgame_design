---
name: planning-liveops-readiness
description: 为游戏活动或版本功能设计 LiveOps 排期、开放范围、功能开关、灰度、回滚、补偿、跨活动冲突、上线观察和复盘。用户说上线方案、活动排期、灰度、补偿、回滚、运营配置或复盘时使用。
---

# 游戏 LiveOps 与上线准备

1. 读取需求契约、风险档位、规则、数值、配置、实现、UI、验收和指标方案。
2. 使用 [上线准备模板](references/liveops-template.md) 生成 `03-specialist-results/liveops.md`。
3. 明确预热、开启、结算、补领、展示结束和数据清理时间，以及统一时区。
4. 明确区服、人群、版本、渠道、平台和账号资格。
5. HIGH 风险或付费功能必须定义灰度、开关、回滚、补偿和客服口径。
6. 检查与活动、任务、商店、排行、赛季和版本节点的冲突。
7. 关联 `$planning-analytics-instrumentation` 的指标和告警。
8. 上线后使用 [复盘模板](references/live-review-template.md) 生成 `09-live-review.md`。

禁止把“配置可改”当作回滚方案；禁止只写开始时间而遗漏结算、补领和清理。
