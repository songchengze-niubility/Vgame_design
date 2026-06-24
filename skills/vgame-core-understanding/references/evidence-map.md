# Vgame 证据地图

## 检索优先级

1. 用户当前明确给出的文件、表名、功能名、ID、页签。
2. `${VGAME_OUTPUT_ROOT}` 中已有任务产物。
3. `vgame-core-understanding` 与 `senior-game-economy` 的 references。
4. `${VGAME_ROOT}\策划` 下的项目策划文档。
5. `${VGAME_ROOT}\Config` 下的源表、导出配置、Luban 工具和规则文档。
6. `${VGAME_ROOT}\HorizonFlyProject` 下的客户端实现、资源和 UI。

## 主要资料入口

| 任务 | 优先读取 |
|---|---|
| Vgame 是什么、正式玩法结构 | `vgame-core-understanding/SKILL.md` 与 `references/current-gameplay.md` |
| 术语、资源名、品质、别名 | `senior-game-economy/references/vgame-terminology.md` |
| 战斗属性与公式 | `senior-game-economy/references/vgame-battle-system.md` |
| 战斗数值母表结构、玩法难度线 | `senior-game-economy/references/vgame-battle-framework-overview.md` |
| 养成结构、旅券、映射装备、专武 | `senior-game-economy/references/vgame-progression-structure.md` |
| 成长系统如何转化为战斗表现和玩法验证 | `vgame-growth-combat-conversion-map` |
| 新手引导、功能开启、主角等级推进 | `senior-game-economy/references/vgame-onboarding-and-unlock-overview.md` |
| 抽卡、商店、任务、签到、战令、活动、邮件、月卡等外循环关系 | `vgame-outer-loop-system-map` |
| 奖励、经济、无限奖励、Excel 落地 | `senior-game-economy` 对应 references |
| 综合数值体验分析 | `game-numerical-analysis` |
| 配置源表、Luban schema、导出链路、校验入口 | `vgame-config-schema` |
| 资源/货币/道具来源与消耗账本 | `vgame-economy-source-map` |
| DropId、Drop/UIlevel、奖励预览、首通和重复奖励同步 | `vgame-reward-drop-sync` |
| LevelId、LevelType、章节、Unlock/SystemOpen、体力、扫荡、玩法开放 | `vgame-level-progression-map` |
| 配置质量、断引用、注册表、ID 完整性和交付前只读审查 | `vgame-config-quality-audit` |
| 可编辑 Figma 游戏 UI、组件变体、设计变量、交互流与程序交接 | `vgame-figma-ui`、目标 Figma 文件及其已订阅组件库、Vgame 正式 UI 源资产 |
| 怪物、Boss、技能、Buff、AI、波次、子弹、召唤物和战斗内容配置链 | `vgame-battle-content-map` |
| 关卡设计、地形编排、Loop 区域、移动平台、刷怪布局、战斗节奏、关卡编辑器、场景序列化和镜头边界 | `vgame-level-design-map` |
| DPS、TTK、怪物属性、玩家战力曲线、难度系数和战斗 What-If | `vgame-battle-tuning-helper` |
| 新手引导、战斗教学、ZoneShowGuide、引导序列/步骤、SystemOpen 功能开放、Unlock 解锁链、引导编辑器和首小时体验 | `vgame-tutorial-onboarding-map` |
| 版本里程碑、功能状态、SystemOpen 运行时开关、AB、灰度、Hotfix 和回滚 | `vgame-version-release-map` |
| 玩家进度模拟、按天资源积累、养成里程碑、卡点、场景对比和体力预算 | `vgame-player-progression-simulator` |

## 文件级证据记录

任务输出中的 `01-project-evidence.md` 使用：

| 证据 ID | 文件 | 位置 | 摘要 | 用途 | 状态 |
|---|---|---|---|---|---|
| EV-001 |  | sheet/字段/行/代码路径 |  | 规则/配置/验证 | 已观察/待确认/冲突 |

## 搜索约束

- 优先用用户提供路径，不做无目标全盘扫描。
- Excel 必须读取 sheet 和字段后再下结论。
- JSON 只作为配置证据或导出物，是否源表必须确认。
- 同名多版本 Excel 存在时，先确认版本再修改。
