# Vgame 配置索引

## 已确认配置链路

| 类型 | 路径 | 说明 |
|---|---|---|
| 源 Excel | `D:\Vgame\Config\GameConfig\Datas` | 策划配置源。 |
| 临时 Excel | `D:\Vgame\Config\GameConfig\TempDatas` | 导出脚本扁平复制生成。 |
| 服务端 JSON | `D:\Vgame\Config\GameConfig\server_json` | 生成物，不直接作为源表修改。 |
| Luban 配置 | `D:\Vgame\Config\GameConfig\luban.conf` | schema、dataDir、target 定义。 |
| 导出脚本 | `D:\Vgame\Config\GameConfig\scripts\export_excel.py` | 复制 Excel、调用 Luban、生成客户端/服务端配置。 |
| 校验脚本 | `D:\Vgame\Config\GameConfig\scripts\check_rules\CheckRules.py` | 服务端导出后的规则检查入口。 |

详细规则见 `vgame-config-schema`。资源、货币、道具的来源/消耗账本见 `vgame-economy-source-map`。战斗内容配置链见 `vgame-battle-content-map`，关卡设计和场景层链路见 `vgame-level-design-map`，新手引导与功能开放触发见 `vgame-tutorial-onboarding-map`，战斗数值测算见 `vgame-battle-tuning-helper`。

## 已观察配置候选

| 领域 | 候选配置 | 说明 | 状态 |
|---|---|---|---|
| 活动 | `activity.json`, `activereward.json` | 活动与奖励候选 | 待确认源表 |
| 战令 | `battlepass.json`, `battlepasslevel.json`, `battlepassreward.json` | 战令周期、等级、奖励 | 待确认源表 |
| 商店 | `shop.json`, `shopgoods.json` | 商店与商品 | 待确认源表 |
| 任务 | `task.json`, `tasktarget.json`, `weeklytask.json`, `weeklyreward.json` | 任务、目标、周常奖励 | 待确认源表 |
| 系统开放 | `systemopen.json`, `unlock.json`, `unlockdesc.json` | 功能开启与解锁说明 | 待确认源表 |
| UI | `uilevel.json`, `uirule.json`, `uipoppriority.json` | UI 预览、规则和弹窗优先级 | 待确认源表 |
| 竞技/排行 | `arenarank.json`, `arenarankreward.json`, `arenawinreward.json` | 排名与胜利奖励 | 待确认源表 |
| 爬塔/世界 | `towerreward.json`, `towerfirstreward.json`, `worldschedulereward.json` | 关卡、首通、进度奖励 | 待确认源表 |
| 装备/养成 | `specialequipment*.json`, `strategy*.json`, `battery*.json` | 装备、策略卡、电池养成 | 待确认源表 |
| 战斗内容 | monster、skill、buff、wave、AI、bullet、summon、hazard 相关配置 | 怪物、Boss、技能、Buff、波次、AI、地形机关和战斗反馈 | 待按 `vgame-battle-content-map` 深入 |
| 关卡设计/场景 | level、UIlevel、CameraParameter、LevelDataPath、LogicData.bytes、VisualData.bytes、StringTable.bytes | Excel 配置层、Unity 场景层、地形、Loop、刷怪点、镜头边界和场景序列化 | 待按 `vgame-level-design-map` 深入 |
| 新手引导/功能开放 | `BattleGuide.xlsx`, `SystemOpen.xlsx`, `Unlock.xlsx`, GuideEditor JSON/Lua 自动导出文件 | 战斗教学、战斗外引导序列/步骤、功能开放、解锁条件和首小时体验 | 待按 `vgame-tutorial-onboarding-map` 深入 |
| 版本/开关 | `systemopen.json`, activity 时间、服务器开关、AB/灰度记录 | 功能可用性、版本状态、活动开放和回滚风险 | 待按 `vgame-version-release-map` 深入 |

## 已确认重点源表

| 逻辑表 | 源表 | 说明 |
|---|---|---|
| `Drop` | `Datas\Drop\Drop_draw.xlsx`, `Drop_dungeon.xlsx`, `Drop_mainlevel.xlsx`, `Drop_other.xlsx`, `Drop_GiftBox.xlsx`, `Drop_TimeLimitedActivity.xlsx`, `Drop_world.xlsx`, `Drop_BattlePass.xlsx` | 逻辑掉落表，多文件合并。 |
| `UILevel` | `Datas\level\UIlevel.xlsx` | 关卡 UI、奖励预览、DropId 引用。 |
| `level` | `Datas\level\level.xlsx` | 战斗关卡底表，含前置、体力、扫荡、首通/通关奖励引用、场景和系数。 |
| `MainLevel` | `Datas\level\MainLevel.xlsx` | 主线/高难关卡章节地图节点。 |
| `ChapterLevel` | `Datas\level\ChapterLevel.xlsx` | 章节信息、章节解锁和高难解锁。 |
| `Unlock` / `SystemOpen` | `Datas\unlock\Unlock.xlsx`, `Datas\system_open\SystemOpen.xlsx` | 解锁条件和系统入口开放。 |
| `BattleGuide` | `Datas\Guide\BattleGuide.xlsx` | 战斗内引导配置，通常由关卡内 `ZoneShowGuide` 触发。 |

奖励落地与 DropId 规则见 `vgame-reward-drop-sync`。
关卡进度、章节、解锁、体力和扫荡规则见 `vgame-level-progression-map`。
新手引导、战斗教学、功能开放和首小时体验链路见 `vgame-tutorial-onboarding-map`。

## 已确认经济源表

| 领域 | 源表 | 说明 |
|---|---|---|
| 物品账本 | `Datas\items\Items.xlsx`, `ItemAccess.xlsx`, `TopAssets.xlsx`, `ItemSweep.xlsx`, `ItemChest.xlsx` | ItemId、名称、类型、展示途径、顶部资产、扫荡/宝箱关联。 |
| 商店 | `Datas\Shop\Shop.xlsx`, `ShopGoods.xlsx` | 商店页签、刷新、解锁、商品产出、价格消耗、限购和付费商品。 |
| 任务/活跃 | `Datas\task\Task.xlsx`, `DailyTask.xlsx`, `WeeklyTask.xlsx`, `DailyActiveReward.xlsx`, `WeeklyReward.xlsx` | 任务奖励、日/周任务池、活跃奖励引用。 |
| 通行证 | `Datas\Battlepass\BattlePass.xlsx`, `BattlePassLevel.xlsx`, `BattlePassReward.xlsx` | 通行证付费档、等级经验、普通/付费奖励引用。 |
| 签到 | `Datas\SignInReward\DailySign.xlsx`, `SevenDaySign.xlsx`, `MonthlyAccumulate.xlsx`, `TravelAccumulate.xlsx` | 签到、累计签到和旅程累计直接奖励。 |
| 活动/邮件 | `Datas\Activity\Activity.xlsx`, `ActiveReward.xlsx`, `DoubleDropActivity.xlsx`, `FourteenDayActivity.xlsx`, `Datas\mail\Mail.xlsx`, `PresendMail.xlsx` | 活动入口、活动奖励、双倍掉落、活动任务、邮件奖励引用。 |
| 抽卡/月卡 | `Datas\Activity\DrawCard\*.xlsx`, `Datas\MonthCard\MonthCard.xlsx` | 抽卡价格、卡池、权重、月卡价格和长期奖励。 |
| 玩家等级 | `Datas\Player\PlayerLv.xlsx` | 玩家等级经验、升级体力和升级道具。 |

## 高风险配置

- 奖励、掉落、权重、首通、重复奖励、补领、活动周期、系统开放、付费货币、抽卡资源。
- 涉及上述内容时，必须使用配置影响矩阵，不直接口头确认完成。

## 配置影响矩阵

| 表/文件 | 源或生成物 | ID/字段 | 旧值 | 新值 | 引用方 | 风险 | 验证方式 |
|---|---|---|---|---|---|---|---|

## 默认规则

- 未确认源表前，不直接改 `D:\Vgame\Config\GameConfig\server_json`。
- 修改 Excel 前先读取目标 sheet 周边结构、公式和引用。
- 涉及奖励落地时优先读取 `senior-game-economy/references/excel-delivery.md`。
- 涉及配置源表、Luban schema、导出和校验时优先使用 `vgame-config-schema`。
- 新增配置表时必须读取 `vgame-config-schema/references/new-config-table-onboarding.md`，并更新配置表应用归纳与作用关联地图。
- 涉及 DropId/UIlevel 奖励同步时优先使用 `vgame-reward-drop-sync`。
- 涉及 LevelId/LevelType、章节、Unlock/SystemOpen、体力、扫荡和玩法开放时优先使用 `vgame-level-progression-map`。
- 涉及怪物、Boss、技能、Buff、AI、波次、子弹、召唤物、地形机关和战斗内容配置链时优先使用 `vgame-battle-content-map`。
- 涉及关卡设计、地形编排、Loop 区域、移动平台、刷怪布局、战斗节奏、关卡编辑器、场景序列化、镜头边界或 Excel 到 Unity 场景关系时优先使用 `vgame-level-design-map`。
- 涉及 DPS、TTK、怪物属性、玩家战力曲线、难度系数、存活时间和战斗 What-If 时优先使用 `vgame-battle-tuning-helper`。
- 涉及新手引导、战斗教学、ZoneShowGuide、引导序列/步骤、SystemOpen 功能开放、Unlock 解锁条件、引导编辑器或首小时体验时优先使用 `vgame-tutorial-onboarding-map`。
- 涉及版本里程碑、功能发布状态、SystemOpen 运行时开关、AB、灰度、Hotfix、回滚和废弃生命周期时优先使用 `vgame-version-release-map`。
- 涉及玩家进度模拟、按天资源积累、养成里程碑、卡点、场景对比和体力预算时优先使用 `vgame-player-progression-simulator`。
