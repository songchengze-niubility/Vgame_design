# Vgame 总体 Skill 工作流

本文件定义 `vgame-core-understanding` 作为 Vgame 项目总控时的任务分类、读取顺序和交付边界。

## 总控职责

`vgame-core-understanding` 负责：

- 统一 Vgame 项目身份、正式玩法结构和废弃/草稿玩法边界。
- 决定当前任务是否需要读取真实项目文件。
- 决定读取哪些专项 skill，而不是让每个问题直接落到专项 skill。
- 保护源表优先、证据优先和不臆造结论的规则。
- 在输出前检查交付门禁。

它不负责：

- 直接替代 `vgame-config-schema` 判断 schema。
- 直接替代 `vgame-reward-drop-sync` 落地 Drop/UIlevel 奖励。
- 直接替代 `vgame-economy-source-map` 做完整产销追踪。
- 直接替代 `senior-game-economy` 或 `game-numerical-analysis` 做价值和数值合理性判断。

## 任务分类

| 类型 | 用户常见说法 | 总控动作 |
|---|---|---|
| 项目理解 | “Vgame 是什么”、“这个玩法算正式吗” | 读取当前 skill 和 `current-gameplay.md`，通常不读 Excel。 |
| 设计讨论 | “这个系统怎么设计”、“下一步做什么” | 先按项目结构回答，再说明需要哪些证据才能落地。 |
| 只读分析 | “查一下”、“追踪一下”、“不要修改配置” | 明确只读，读取相关专项 skill 和源表，输出证据路径与待确认项。 |
| 配置实施 | “帮我改表”、“落到配置” | 先确认源表和字段，再按专项 skill 执行，不能直接改生成 JSON。 |
| 新表接入 | “新增配置表”、“后续新表怎么加” | 读取 `vgame-config-schema/references/new-config-table-onboarding.md`。 |
| 验证审查 | “检查一下”、“有没有风险” | 按证据地图、交付门禁和必要的 `vgame-config-quality-audit` 输出发现、风险和验证方式。 |
| 总结沉淀 | “总结进 skill”、“以后记住” | 更新对应 reference，避免把临时结论散落在对话里。 |

## 读取顺序

默认读取顺序：

1. `vgame-core-understanding/SKILL.md`
2. `references/project-profile.md`
3. `references/project-control-workflow.md`
4. `references/evidence-map.md`
5. 按任务读取专项 skill
6. `references/delivery-gates.md`

当用户只问项目高层结构时，可以只读：

1. `SKILL.md`
2. `references/current-gameplay.md`

当用户要求只读配置分析时，必须读：

1. `references/evidence-map.md`
2. `references/config-index.md`
3. 对应专项 skill
4. 真实源表或已有 output 证据

## 专项 Skill 边界

| 专项 skill | 只在这些问题上介入 |
|---|---|
| `vgame-config-schema` | 源表、逻辑表、字段类型、Luban、导表、校验、新配置表接入。 |
| `vgame-level-progression-map` | LevelId、LevelType、章节、Unlock、SystemOpen、体力、扫荡、玩法开放链。 |
| `vgame-reward-drop-sync` | DropId、Drop 多源表、UIlevel 奖励预览、首通/重复奖励、随机权重奖励。 |
| `vgame-economy-source-map` | ItemId、货币/道具产销、商店、任务、活动、邮件、通行证、签到、抽卡消耗引用。 |
| `vgame-growth-combat-conversion-map` | 角色、专武、旅券、映射装备等成长系统如何转化为战斗表现和正式玩法验证。 |
| `vgame-outer-loop-system-map` | 抽卡、商店、任务、签到、战令、活动、邮件、月卡等外循环职责、周期和商业化支撑关系。 |
| `vgame-config-quality-audit` | 配置交付前只读质检、注册源文件、ID/引用完整性、PropType 格式和常见断链。 |
| `vgame-battle-content-map` | 怪物、Boss、精英、技能、Buff、AI、波次、子弹、召唤物、地形机关和战斗内容配置链。 |
| `vgame-level-design-map` | 关卡设计、地形编排、Loop 区域、移动平台、刷怪布局、战斗节奏、关卡编辑器、场景序列化和镜头边界。 |
| `vgame-battle-tuning-helper` | DPS、TTK、怪物属性、玩家战力曲线、难度系数、存活时间和战斗 What-If 调参。 |
| `vgame-tutorial-onboarding-map` | 新手引导、战斗教学、ZoneShowGuide、引导序列/步骤、SystemOpen 功能开放、Unlock 解锁链、引导编辑器和首小时体验。 |
| `vgame-version-release-map` | 版本里程碑、功能状态、SystemOpen 运行时可用性、功能开关、AB、灰度、Hotfix、回滚和废弃生命周期。 |
| `vgame-player-progression-simulator` | 玩家按天资源积累、养成里程碑、卡点、经济验证、场景对比和体力预算模拟。 |
| `senior-game-economy` | 奖励价值、长线经济、付费敏感性、Excel 奖励方案。 |
| `game-numerical-analysis` | 数值体验、成长曲线、资源收支、战斗平衡、概率期望。 |

## 证据规则

- 用户明确给出的文件、ID、玩法名优先。
- 已有 output 可以作为历史分析线索，但不能替代源表事实。
- Excel 必须确认 sheet、字段和数据行后再下结论。
- JSON 默认是生成物，不作为修改源，除非用户明确要求。
- 同名多版本文件必须先确认版本。
- 旧玩法、草稿玩法、废弃玩法不要自动纳入正式结构。

## 输出规则

高层问题输出：

```text
结论：
依据：
边界：
下一步：
```

只读配置分析输出：

```text
结论：
读取范围：
涉及表和字段：
引用链：
风险/待确认：
未修改配置：
```

配置实施输出：

```text
修改内容：
影响矩阵：
验证结果：
风险和回滚点：
```

## 当前总控建设重点

优先补强 `vgame-core-understanding` 的总体路由和项目事实沉淀。除非出现稳定、重复、跨表且高风险的任务类型，否则不要急着新增专项 skill。
