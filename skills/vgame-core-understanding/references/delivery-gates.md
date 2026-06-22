# Vgame 交付门禁

## 人工门禁

| 门禁 | 通过条件 |
|---|---|
| 项目口径确认 | 当前任务已按 Vgame 跑酷战斗射击和正式玩法结构理解 |
| 版本确认 | 明确使用哪个策划 Excel 或配置版本 |
| 源表确认 | 修改对象是源表，或用户明确要求修改目标文件 |
| 配置影响确认 | 表、字段、ID、引用、玩家表现和验证方式已列出 |
| 配置 schema 确认 | 已确认源 Excel、逻辑表、字段类型、生成物和导出命令 |
| 新增配置表接入确认 | 新表已注册到 `__tables__.xlsx`，实际 `Datas` 路径无缺失/重名歧义，作用与关联已更新到配置表地图 |
| 经济来源/消耗确认 | 已确认 ItemId、来源表、消耗表、展示字段、真实奖励引用和周期/次数限制 |
| 成长战斗转化确认 | 已确认成长模块职责、属性/机制输出、战斗表现影响和正式玩法验证点 |
| 外循环关系确认 | 已确认外循环系统职责、周期、真实奖励/展示字段、商业化敏感点和下游引用 |
| Drop/UIlevel 确认 | 已确认 DropId 来源、UIlevel 引用字段、预览字段和逻辑 Drop 引用 |
| 关卡进度确认 | 已确认 LevelId、LevelType、章节、Unlock/SystemOpen、体力、扫荡和玩法入口链 |
| 经济风险确认 | 奖励、货币、抽卡、商店、通行证、无限玩法供给已检查 |
| 配置质量审查确认 | 已运行或手动完成只读配置质检，断引用、PropType 格式、注册源文件和已知基线均已说明 |
| 战斗内容确认 | 已确认怪物、Boss、技能、Buff、AI、波次、子弹、召唤物、地形或战斗事件配置影响、引用链和运行时消费方 |
| 关卡设计确认 | 已确认 Excel 配置层与 Unity 场景层的边界、地形/Loop/刷怪/镜头/序列化影响、可调项和需要关卡编辑器处理的内容 |
| 战斗调参确认 | 已确认玩家模型、怪物模型、DPS/TTK/存活时间、难度系数、目标体验区间和调参风险 |
| 新手引导确认 | 已确认 BattleGuide/NewbieGuide/SystemOpen/Unlock 触发链、引导步骤、完成记录、跳过/失败逻辑和首小时体验影响 |
| 版本发布确认 | 已确认功能状态、目标版本、SystemOpen/功能开关/活动时间/灰度范围、依赖和回滚方案 |
| 玩家进度模拟确认 | 已确认玩家画像、收入/消耗假设、体力分配、养成里程碑、卡点和模拟局限 |
| 最终验收 | 用户明确确认结果通过 |

## 自动检查建议

| 类型 | 检查 |
|---|---|
| Excel | sheet 存在、列存在、ID 唯一、公式未破坏、保存后可重新打开 |
| JSON | 可解析、目标 ID 存在、字段类型与旧结构一致 |
| 引用 | ItemId/DropId/RewardId/UIlevel/SystemOpen 是否可追踪 |
| 奖励 | 首通、重复、补领、过期、权重、长尾、荣誉层是否区分 |
| 质量审查 | 可用 `vgame-config-quality-audit/scripts/audit_config_quality.py` 做只读全量或局部审查 |
| 战斗内容 | 按 `vgame-battle-content-map` 检查战斗元素、引用链、运行时消费方和影响范围 |
| 关卡设计 | 按 `vgame-level-design-map` 检查 Excel 配置层、Unity 场景层、地形/Loop/刷怪/镜头和序列化链路 |
| 战斗调参 | 可用 `vgame-battle-tuning-helper/scripts/battle_tuning.py` 做 DPS、TTK、存活时间和系数 What-If |
| 新手引导 | 按 `vgame-tutorial-onboarding-map` 检查 BattleGuide、NewbieGuide、SystemOpen、Unlock、引导编辑器和首小时体验链路 |
| 版本发布 | 按 `vgame-version-release-map` 检查功能状态、开关层、灰度/AB、活动时间和回滚方案 |
| 进度模拟 | 可用 `vgame-player-progression-simulator/scripts/simulate_progression.py` 做玩家画像、资源、体力和卡点模拟 |
| 文档 | 规则、配置、验收项、证据路径是否一一对应 |

## 阶段状态块

```planning-workflow-gate
{"actor":"vgame-design-lead","phase":"project_adapter","outcome":"waiting_human","next_action":"review","evidence":"列出实际文件路径"}
```

状态块只做记录，不代替人工验收。
