# 通用策划 Skill 模板

本目录保存策划 Agent 的**通用框架模板**，不绑定任何具体项目。它们是方法论层：描述"怎么思考"，不含"项目 X 的具体字段"。

| 通用模板 | 对应 Vgame 专项 Skill | 覆盖范围 |
|---|---|---|
| `project-core-adapter` | `vgame-core-understanding` | 项目入口、身份、路由、证据纪律 |
| `config-pipeline-map` | `vgame-config-schema` | 配置管线、Schema、公式安全、注册 |
| `config-quality-audit` | `vgame-config-quality-audit` | 配置质量审查、断引用、闭环 |
| `battle-content-config` | `vgame-battle-content-map` | 怪物/Boss/技能/Buff/AI/波次配置 |
| `battle-tuning-framework` | `vgame-battle-tuning-helper` | DPS/TTK/存活/难度/同行比较 |
| `character-kit-design` | `vgame-character-kit-design-map` | 角色套件设计、定位、天赋、升星 |
| `character-skill-config` | `vgame-hero-skill-config-map` | Hero/Skill/Buff 表、编辑器链路 |
| `economy-source-sink-map` | `vgame-economy-source-map` | 资源产销、道具账本、经济风险 |
| `growth-combat-conversion` | `vgame-growth-combat-conversion-map` | 成长属性→战斗转化、验证 |
| `level-design-map` | `vgame-level-design-map` | 关卡设计、地形、刷怪、编辑器 |
| `outer-loop-system-map` | `vgame-outer-loop-system-map` | 抽卡/商店/任务/签到/战令 |
| `player-progression-simulator` | `vgame-player-progression-simulator` | 进度模拟、日收入、卡点 |
| `progression-unlock-map` | `vgame-level-progression-map` | 关卡/章节/解锁/体力链 |
| `reward-drop-config` | `vgame-reward-drop-sync` | 奖励/掉落/DropId/UI 预览 |
| `tutorial-onboarding-map` | `vgame-tutorial-onboarding-map` | 新手引导/战斗教学/功能开放 |
| `version-feature-map` | `vgame-version-release-map` | 版本/功能状态/灰度/开关/回滚 |

`game-numerical-analysis` 和 `senior-game-economy` 是 Vgame 项目独有，没有通用模板。

**使用场景**：
- 为新项目初始化策划 Agent 时，以这些通用模板为骨架，填入项目具体事实。
- Vgame 已有专项 Skill，日常任务直接读 Vgame 版；通用模板仅在需要跨项目迁移或审查方法论完整性时参考。
