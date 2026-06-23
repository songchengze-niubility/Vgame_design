---
name: planning-analytics-instrumentation
description: 为游戏功能设计指标体系、埋点事件与属性、漏斗、留存、经济护栏和实验观测方案。用户说埋点、数据指标、漏斗、留存、上线后看什么、A/B 测试或数据复盘时使用。
---

# 游戏策划数据指标与埋点

1. 读取需求契约、核心规则、UI、配置和验收用例。
2. 读取项目已有埋点命名与上报方式；没有证据时标记待技术确认。
3. 按需加载 `$product-analytics-setup`：
   - 使用其事件分类、属性、Schema 版本和漏斗方法。
   - 将 SaaS/Web 示例改写为游戏业务语义，不照搬 GA4。
4. 涉及实验结果时加载 `$experimentation-analytics`。
5. 涉及付费和经济系统时加载 `$game-monetization`，但最终投放规则以项目数值与合规要求为准。
6. 使用 [模板](references/analytics-template.md) 生成 `03-specialist-results/analytics.md`。
7. 将事件和指标关联到规则 ID、页面 ID 和验收用例 ID。

禁止用“按钮点击量”代替核心业务事件；禁止定义没有分母、窗口和去重口径的指标。
