# Vgame 策划 Skill 目录

## 结构

```text
skills/
  config.toml                    — 项目级 Skill 路由配置
  agents/                        — Agent 定义（vgame-design-lead.toml）
  generic/                       — 通用框架模板（16 个，不绑定任何项目）
  vgame-core-understanding/      — [入口] 项目身份、路由、证据纪律
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
```

## 入口顺序

1. `vgame-core-understanding` 先读，确认问题类型和路由。
2. 按路由表进入对应专项 Skill。
3. 涉及配置表时先过 `vgame-config-schema`。
4. 涉及奖励落地时过 `vgame-reward-drop-sync`。

## 通用模板

`generic/` 目录保存 16 个不绑定项目的策划 Agent 框架模板。Vgame 任务直接使用 `vgame-*` 专项 Skill；通用模板仅在以下场景参考：
- 为新项目初始化策划 Agent（以通用模板为骨架，填入项目具体事实）
- 审查某领域方法论完整性（对比通用模板看专项 Skill 是否遗漏关键维度）
- 跨项目迁移（通用模板定义了"需要回答什么问题"，专项 Skill 定义了"项目 X 的具体答案"）
