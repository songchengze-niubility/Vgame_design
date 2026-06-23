# Vgame 策划 Skill 目录

## 结构

```text
skills/
  config.toml                    — 项目级 Skill 路由配置
  agents/                        — Agent 定义（vgame-design-lead.toml）

  [项目入口]
  vgame-core-understanding/      — 项目身份、路由、证据纪律

  [策划案交付流程 — 每次发起需求必须加载]
  planning-feature-workflow/     — 九步策划交付编排（需求契约→澄清→核心设计→专项→评审→UI→Excel→验收）
  planning-requirement-clarification/ — 需求逐条澄清
  planning-acceptance-traceability/   — 验收用例与追踪矩阵
  planning-change-sync/          — 需求变更同步
  planning-analytics-instrumentation/ — 数据与埋点专项
  planning-liveops-readiness/    — LiveOps 与上线准备

  [Vgame 专项]
  vgame-config-schema/           — 配置表 Schema、Luban 管线、公式安全
  vgame-config-quality-audit/    — 配置质量审查、断引用、闭环
  vgame-reward-drop-sync/        — 奖励/掉落/DropId/UIlevel 同步
  vgame-level-progression-map/   — 关卡/章节/解锁/体力/扫荡链
  vgame-economy-source-map/      — 资源产销、道具账本、经济风险
  vgame-battle-content-map/      — 怪物/Boss/技能/Buff/AI/波次配置
  vgame-battle-tuning-helper/    — DPS/TTK/存活/难度/同行比较
  vgame-character-kit-design-map/ — 角色套件设计、定位、天赋、升星
  vgame-hero-skill-config-map/   — Hero/Skill/Buff 表、编辑器链路
  vgame-growth-combat-conversion-map/ — 成长→战斗转化、验证
  vgame-outer-loop-system-map/   — 抽卡/商店/任务/签到/战令
  vgame-level-design-map/        — 关卡设计、地形、刷怪、编辑器
  vgame-tutorial-onboarding-map/ — 新手引导/战斗教学/功能开放
  vgame-version-release-map/     — 版本/功能状态/灰度/开关/回滚
  vgame-player-progression-simulator/ — 进度模拟、日收入、卡点
  game-numerical-analysis/       — 综合数值分析、成长曲线、概率
  senior-game-economy/           — 长线经济、奖励价值、落地规范

  [跨领域专项]
  game-monetization/             — F2P 商业化设计、定价、LTV
  localize/                      — 国际化、本地化、文化适配
  accessibility-compliance/      — WCAG 无障碍合规
  experimentation-analytics/     — A/B 测试、统计方法
  product-analytics-setup/       — 产品分析、事件体系、漏斗设计
```

## 入口顺序

1. 每次发起需求或策划案任务：先加载 `planning-feature-workflow`，按九步流程执行。
2. `vgame-core-understanding` 先读，确认问题类型和项目路由。
3. 按路由表进入对应专项 Skill。
4. 涉及配置表时先过 `vgame-config-schema`。
5. 涉及奖励落地时过 `vgame-reward-drop-sync`。
