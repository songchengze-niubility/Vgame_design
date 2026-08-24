# SYS-OUT-GR-01 玩家等级

> 本文由 `system-details/SYS-OUT-GR-01.json` 生成；结构化 JSON 是本知识库中该系统正文的维护源。

- 详情版本：2026-08-18.5
- 更新时间：2026-08-20
- 完整度：full
- 证据环境：本机 SVN 工作副本
- 核对时间：2026-08-18
- SVN Revision：未建立集中记录
- LIVE 说明：仅证明核对时工作副本中存在配置或实现线索，不证明 Production/LIVE；升级经验曲线与体力口径的权威选择仍待裁决。

## 系统概览

玩家等级是 Vgame 的账号级进度横轴：消费玩家经验驱动升级，升级返还储能并锚定体力上限/恢复，同时作为系统开放与玩法资格的主要条件，把主线、任务等玩法产出统一为账号进度。

### 包含范围

- 玩家经验（行旅帧片 4）的来源口径与升级门槛（PlayerLv.UpgradeCostExp）
- 升级效果（返还储能 UpgradeGetPhy 与升级道具 UpgradeGetItem）
- 体力/储能的上限、恢复间隔与初始值（Power.xlsx）
- 玩家等级作为 Unlock/SystemOpen 条件（UnLock_UUT_player_Grade）的角色
- 经验溢出连升与升级事件的开放触发

### 不包含范围

- 具体经验曲线逐级数值与毕业天数验算；该内容归 NUM-05 节奏数值与 NUM-02 养成数值
- 储能作为道具的身份与堆叠；该内容归 SYS-OUT-SU-04
- 体力补充商店的定价与商品；该内容归 SYS-OUT-SU-06 与 NUM-04 经济数值
- 角色/英雄等级与角色经验；该内容归 SYS-OUT-GR-02
- 主线/任务具体产出多少玩家经验；该内容归各玩法正文

### 输入

- 玩家经验增量（主线通关、任务、每日活跃等产出行旅帧片 4）
- PlayerLv 经验门槛、储能返还与升级道具配置
- Power 体力配置（上限、恢复间隔、初始值）
- Unlock 中 UnLock_UUT_player_Grade 的条件参数

### 输出

- 玩家等级提升与经验溢出结转
- 升级返还储能与升级道具入账
- 体力槽状态（当前值/上限/恢复时间）
- 玩家等级满足 Unlock 条件后触发的系统开放事件

## 状态分层

| 轴 | 当前值 | 状态 | 说明 |
|---|---|---|---|
| 系统身份 | 正式账号进度横轴 | CURRENT_DESIGN_IDENTITY | 玩家等级作为系统开放、体力与整体进度的锚点没有争议，与角色等级是两条独立资源线。 |
| 目标设计 | 经验曲线与升级返还已有沉淀，但 v2 单源与正式表不一致 | CONFIRMED_TARGET_WITH_CONFLICT | 沉淀已确认「玩家经验=行旅帧片4、升级返还储能」口径，但正式 PlayerLv 与 v2 节奏单源经验合计不一致。 |
| 当前工作副本 | PlayerLv 1-60、储能 6 分钟/180 上限、升级道具仅 2 级非空 | WORKING_COPY_OBSERVED | 本机 SVN 工作副本核对于 2026-08-18；升级道具 UpgradeGetItem 几乎全空，与反推 Design 的分层奖励描述不符。 |
| 运行状态 | 等级/体力链路存在；玩家可用版本待发布台账确认 | UNKNOWN_LIVE | 存在源表与客户端实现证据，但没有集中版本—开关—发布时间台账，不能盖为 LIVE。 |

### 状态词图例

| 前缀 | 含义 |
|---|---|
| TARGET / CONFIRMED | 目标设计或已确认策划口径，不代表已配置或已上线。 |
| WORKING_COPY / OBSERVED / CONFIGURED | 本机 SVN 工作副本观察（表或客户端 Lua），不代表 Production/LIVE。 |
| CROSS_SOURCE / SYNTHESIS | 由多份证据组织出的流程、边界或关系，需要项目负责人确认。 |
| CONFLICT / GAP / UNKNOWN | 仍需裁决、补规则或补运行证据。 |
| LIVE | 只有集中版本、开关和发布时间证据齐全时才能使用；本页运行状态尚未确认。 |

## 核心流程

### SYS-OUT-GR-01-F01 玩家升级与开放触发流程

1. **获得玩家经验**：主线通关、任务、每日活跃等产出行旅帧片（4），作为玩家经验增量累加到当前经验。
2. **判定升级门槛**：比对 PlayerLv.UpgradeCostExp；经验溢出可连续升级，溢出部分结转到下一级。
3. **结算升级效果**：每次升级按 UpgradeGetPhy 返还储能，按 UpgradeGetItem 发放升级道具（当前工作副本仅 Lv26/Lv29 非空）。
4. **触发开放检查**：升级事件驱动 ConditionSystem.OnConditionChanged(UnLock_UUT_player_Grade, 等级)，重新评估受玩家等级约束的系统开放与关卡。
5. **刷新进度与体力**：更新主界面等级进度条、升级弹窗与体力槽；连升多级时逐个播放返还展示。

## 系统规则

### SYS-OUT-GR-01-R01 玩家等级身份与责任边界

- 状态：CURRENT_DESIGN_IDENTITY
- 目标规则：玩家等级是账号级横轴，消费玩家经验（行旅帧片 4）；与角色等级（角色经验道具）是两条独立资源线，不得混列。
- 当前工作副本事实：主角升级经济沉淀明确「主角升级是玩家等级线，不是角色/英雄等级线，使用行旅帧片(4)」；Items.xlsx 中行旅帧片(4) ItemSubType=ItemSubType_Exp，角色经验记录盘(100/101/102) ItemSubType=ItemSubType_HeroExp。
- 验收口径：玩家经验与角色经验在产销账中拆列；玩家等级不得误用角色经验曲线。
- 依赖：SYS-OUT-GR-02、SYS-OUT-SU-04
- 证据：SYS-OUT-GR-01-EV03、SYS-OUT-GR-01-EV05

### SYS-OUT-GR-01-R02 账号经验与升级门槛

- 状态：CONFIRMED_TARGET_WORKING_COPY_OBSERVED
- 目标规则：玩家经验累加到当前经验，达到 PlayerLv.UpgradeCostExp 时自动升级，溢出结转；正式表覆盖 Lv1-Lv60。
- 当前工作副本事实：PlayerLv.xlsx 有效行 Lv1-Lv60；Lv1→60 可发生升级经验合计 278,180，储能返还合计 1,195（沉淀口径，不含 Lv60 无下一级消耗）。
- 验收口径：升级门槛只读 PlayerLv.UpgradeCostExp；经验溢出可连升，逐级触发返还。
- 依赖：NUM-05、SYS-OUT-SU-04
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03

### SYS-OUT-GR-01-R03 升级返还储能

- 状态：CONFIRMED_TARGET_WORKING_COPY_OBSERVED
- 目标规则：每次升级按 PlayerLv.UpgradeGetPhy 返还储能（ItemId=3）；返还是一次性补给，不并入自然恢复。
- 当前工作副本事实：PlayerLv.UpgradeGetPhy 分段为 5（Lv1-9）、10（Lv10-19）、15（Lv20-29）、20（Lv30-39）、30（Lv40-49）、40（Lv50-59）；Lv60 UpgradeGetPhy=40 但无下一级消耗。
- 验收口径：升级返还储能写入体力槽；Lv60 的 UpgradeGetPhy=40 是否生效需裁决。
- 依赖：SYS-OUT-SU-04、NUM-04
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03

### SYS-OUT-GR-01-R04 升级道具奖励

- 状态：WORKING_COPY_OBSERVED_DESIGN_GAP
- 目标规则：GAP：缺「升级道具奖励」的正式分档口径；反推 Design 描述前期/中期/后期分层奖励，但工作副本几乎全空。
- 当前工作副本事实：PlayerLv.UpgradeGetItem 仅 Lv26→27 收容凭证(107)x1、Lv29→30 终焉裁判之刃(60055)x1+(60056)x1 非空，其余等级为空。
- 验收口径：策划冻结升级道具奖励口径并同步表；不得把反推 Design 的分层描述当正式规则。
- 依赖：SYS-OUT-SU-04、SYS-OUT-SU-05
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03、SYS-OUT-GR-01-EV10

### SYS-OUT-GR-01-R05 体力/储能上限与恢复

- 状态：WORKING_COPY_OBSERVED
- 目标规则：GAP：体力自然恢复速率、上限与开放等级的正式策划口径未冻结；工作副本观察值见sourceFact。
- 当前工作副本事实：Power.xlsx：体力(1)=储能3 Power_Normal 6分钟/180/180；后备体力(2)=41 Power_Reserve 18分钟/1800/开放等级20；邮票精力(3)=33 Power_strategy 15分钟/160；跑商精力(4)=38 Power_Trade 6分钟/20。
- 验收口径：体力上限/恢复只读 Power.xlsx；邮票精力当前工作副本为 15 分钟/160（已同步最新口径）。
- 依赖：SYS-OUT-SU-04、NUM-04
- 证据：SYS-OUT-GR-01-EV02、SYS-OUT-GR-01-EV04

### SYS-OUT-GR-01-R06 体力消耗转玩家经验

- 状态：WORKING_COPY_OBSERVED
- 目标规则：GAP：体力购买消耗比率由globals_conf维护，正式策划口径未冻结；工作副本观察值见sourceFact。
- 当前工作副本事实：globals_conf.StaminaCostDropRatio=10（消耗一点体力给多少经验）、PlayerExpItem=4（玩家经验道具）、StaminaPotionItemId=105（体力补充道具）。
- 验收口径：体力消耗与玩家经验的折算只读 StaminaCostDropRatio；具体换算由程序结算，不进入 Drop/预览。
- 依赖：SYS-OUT-SU-04、NUM-04
- 证据：SYS-OUT-GR-01-EV06

### SYS-OUT-GR-01-R07 玩家等级作为开放条件

- 状态：WORKING_COPY_OBSERVED_MAINLINE_CONFIGURED
- 目标规则：玩家等级达到 Unlock 的 UnLock_UUT_player_Grade 参数时满足对应解锁；升级事件驱动系统开放与关卡重新评估。主线章节3～7使用该条件直接控制章节入口，门槛为24/28/31/33/35；章节0～2无章节级条件。
- 当前工作副本事实：ConditionSystem.GetIsUnLock 对 UnLock_UUT_player_Grade 判定 Level >= UnLockParams[1]；PlayerSystem 升级后 OnConditionChanged(UnLock_UUT_player_Grade, Level)。工作副本 Unlock 201～205 已配置24/28/31/33/35，并由 ChapterLevel 10003～10007引用；10000～10002的ChapterLevel.Unlock为空。
- 验收口径：受玩家等级约束的系统开放能追到对应 Unlock 参数；主线章节3～7在24/28/31/33/35级达到后开放，0～2章不被章节条件硬卡；升级事件能触发开放刷新。
- 依赖：SYS-OUT-SU-13、SYS-OUT-GP-01
- 证据：SYS-OUT-GR-01-EV07、SYS-OUT-GR-01-EV08、SYS-OUT-GR-01-EV09

### SYS-OUT-GR-01-R08 经验曲线权威冲突

- 状态：P1_CONFLICT
- 目标规则：GAP：需裁决玩家等级经验曲线以正式 PlayerLv.xlsx 还是 v2 节奏单源为新权威。
- 当前工作副本事实：主角升级沉淀记录 v2 节奏单源总经验 302,950，正式 PlayerLv.xlsx 可发生升级经验合计 278,180；未同步前不能混用两套曲线。
- 验收口径：确定单一权威后同步正式表或重算沉淀；毕业天数验算前补齐真实玩家经验来源链。
- 依赖：NUM-05、NUM-02
- 证据：SYS-OUT-GR-01-EV03

## 条件

### SYS-OUT-GR-01-C01 升级门槛

- 状态：WORKING_COPY_OBSERVED
- 规则：currentExp >= UpgradeCostExp 时升级；经验溢出结转，支持一次获得大量经验连升多级。
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03

### SYS-OUT-GR-01-C02 玩家等级开放条件

- 状态：WORKING_COPY_OBSERVED_MAINLINE_CONFIGURED
- 规则：UnLock_UUT_player_Grade 以 UnLockParams[1] 为等级门槛，等级达到即满足。当前主线章节3～7的ChapterLevel.Unlock直接引用该类型条件201～205，不与前章通关条件组合；章节0～2的ChapterLevel.Unlock为空。
- 证据：SYS-OUT-GR-01-EV07、SYS-OUT-GR-01-EV09

### SYS-OUT-GR-01-C03 体力恢复与上限

- 状态：WORKING_COPY_OBSERVED
- 规则：Power_Normal 每 6 分钟恢复 1 点，上限 180；恢复时间由服务端下发 StaminaUpdateTime 与恢复间隔计算。
- 证据：SYS-OUT-GR-01-EV02、SYS-OUT-GR-01-EV04


## 奖励与结算

### SYS-OUT-GR-01-RW01 升级储能返还

- 状态：CONFIRMED_TARGET_WORKING_COPY_OBSERVED
- 规则：升级返还储能（ItemId=3），数量由 PlayerLv.UpgradeGetPhy 维护；是升级奖励而非升级成本。
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03

### SYS-OUT-GR-01-RW02 升级道具奖励

- 状态：WORKING_COPY_OBSERVED_DESIGN_GAP
- 规则：升级道具由 PlayerLv.UpgradeGetItem 维护；当前仅 Lv26/Lv29 发放，其余等级为空。
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03


## 异常与边界

### SYS-OUT-GR-01-EX01 经验曲线权威冲突

- 状态：P1_CONFLICT
- 规则：正式 PlayerLv（278,180）与 v2 节奏单源（302,950）不一致；未裁决前不得混用两套曲线做毕业天数验算。
- 证据：SYS-OUT-GR-01-EV03

### SYS-OUT-GR-01-EX02 Lv60 返还体力悬置

- 状态：P2_GAP
- 规则：PlayerLv Lv60 的 UpgradeGetPhy=40 但 UpgradeCostExp 为空；是否产生返还需裁决。
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03

### SYS-OUT-GR-01-EX03 升级道具与反推 Design 不符

- 状态：P2_GAP
- 规则：反推 Design 描述前期/中期/后期分层升级道具，工作副本 UpgradeGetItem 几乎全空；需澄清是设计未落表还是表被清空。
- 证据：SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV10

### SYS-OUT-GR-01-EX04 玩家经验与角色经验混用风险

- 状态：P2_GAP
- 规则：玩家经验（行旅帧片 4）与角色经验道具（记录盘 100/101/102）可能同时出现在玩法奖励，产销账需拆列。
- 证据：SYS-OUT-GR-01-EV03、SYS-OUT-GR-01-EV05


## UI 与信息表达

### SYS-OUT-GR-01-UI01 等级进度条

- 状态：WORKING_COPY_OBSERVED
- 规则：主界面与个人档案展示玩家等级、当前经验进度与满级状态；满级不显示下一级消耗。
- 证据：SYS-OUT-GR-01-EV08

### SYS-OUT-GR-01-UI02 升级弹窗

- 状态：TARGET_REQUIRED
- 规则：升级时展示返还储能与道具；连升多级时逐个串联播放返还。
- 证据：SYS-OUT-GR-01-EV10


## 共享契约引用

| 契约 ID | 契约 | 本系统规则 |
|---|---|---|
| CONTRACT-UNLOCK-SYSTEMOPEN | 解锁、系统开放与引导 | SYS-OUT-GR-01-R07、SYS-OUT-GR-01-C02 |
| CONTRACT-LEVEL-ENTRY | 玩法进入与资格校验 | SYS-OUT-GR-01-R05、SYS-OUT-GR-01-C03 |

> 共享契约用于跨系统去重和路由，不替代本系统规则，也不代表规则已经冻结。

## 配置契约

| ID | 配置 | 路径 | 职责 | 状态 |
|---|---|---|---|---|
| SYS-OUT-GR-01-CFG01 | PlayerLv | `D:\Vgame\Config\GameConfig\Datas\Player\PlayerLv.xlsx` | 升级经验门槛 UpgradeCostExp、返还储能 UpgradeGetPhy、升级道具 UpgradeGetItem | WORKING_COPY_SOURCE_WITH_CONFLICTS |
| SYS-OUT-GR-01-CFG02 | Power | `D:\Vgame\Config\GameConfig\Datas\Player\Power.xlsx` | 体力/储能上限、恢复间隔、初始值与开放等级（ItemId、RecoverTime、MaxLimit、InitialValue、OpenLv） | WORKING_COPY_SOURCE |
| SYS-OUT-GR-01-CFG03 | globals_conf | `D:\Vgame\Config\GameConfig\Datas\globals_conf\globals_conf.xlsx` | PlayerExpItem=4、StaminaCostDropRatio=10、StaminaPotionItemId=105 等全局参数 | WORKING_COPY_SOURCE |
| SYS-OUT-GR-01-CFG04 | Unlock | `D:\Vgame\Config\GameConfig\Datas\unlock\Unlock.xlsx` | UnLock_UUT_player_Grade 玩家等级开放条件参数 | WORKING_COPY_SOURCE |

## 系统关系

| ID | 类型 | 目标 | 说明 | 状态 | 证据 | 来源/推导边界 |
|---|---|---|---|---|---|---|
| SYS-OUT-GR-01-REL01 | supplies / incoming | SYS-OUT-GP-01 主线 | 来源：主角升级经济消耗沉淀(EV03)确认主线通关为玩家经验主要来源，PlayerLv.xlsx(EV01)定义升级经验门槛，PlayerSystem.lua(EV08)处理升级。推导：主线通关(GP-01)产出玩家经验，经验达到PlayerLv门槛后推动玩家等级升级，构成 supplies/incoming 关系。推导边界：经验产出与升级门槛已由沉淀与配置确认，但主线经验产出的具体数值在GP-01/Drop权威源维护，本正文不复制。UNKNOWN：主线各关卡经验产出量与升级曲线的精确匹配仍待经济域核算。 | KNOWLEDGE_CURRENT | — | UNKNOWN |
| SYS-OUT-GR-01-REL02 | supplies / incoming | SYS-OUT-SU-07 任务与章节任务 | 来源：主角升级经济消耗沉淀(EV03)确认任务奖励为玩家经验来源之一，SYS-OUT-SU-07任务正文定义任务奖励产出。推导：任务与每日/每周奖励(SU-07)产出玩家经验，作为玩家等级升级的补充来源，构成 supplies/incoming 关系。推导边界：经验产出口径已由沉淀确认，但任务经验产出数量在SU-07侧维护，本正文未直接核到任务到升级的完整链路。UNKNOWN：任务经验在总升级经验中的占比与日周节奏仍待经济域核算。 | KNOWLEDGE_CURRENT | — | UNKNOWN |
| SYS-OUT-GR-01-REL03 | unlocks / outgoing | SYS-OUT-SU-13 新手引导与系统开放 | 玩家等级达到 UnLock_UUT_player_Grade 条件时驱动 SystemOpen 开放。 | KNOWLEDGE_CURRENT | SYS-OUT-GR-01-EV09 | WORKING_COPY_OBSERVED |
| SYS-OUT-GR-01-REL04 | balances / incoming | NUM-05 节奏数值 | 来源：主角等级Design Doc(EV10)与知识目录定义节奏数值域职责，PlayerLv.xlsx(EV01)定义等级曲线，体力补充经济沉淀(EV04)定义体力节奏。推导：玩家等级、天数、系统开放与体力恢复节奏由节奏数值域(NUM-05)约束与平衡，构成 balances/incoming 关系。推导边界：等级曲线与体力配置已由工作副本确认，但整体节奏模型(等级-天数-开放-体力的联合约束)属节奏数值域维护。UNKNOWN：玩家等级曲线与开放节奏的精确天数映射仍待节奏数值域确认。 | KNOWLEDGE_CURRENT_WITH_CONFLICT | — | UNKNOWN |
| SYS-OUT-GR-01-REL05 | consumes / incoming | SYS-OUT-GP-11 扫荡 | 来源：Power.xlsx(EV02)定义体力/储能上限与恢复，体力补充经济沉淀(EV04)定义恢复节奏，SYS-OUT-GP-11扫荡正文定义储能消耗。推导：扫荡(GP-11)消耗储能(体力)，消耗量受玩家等级侧体力上限与恢复节奏约束，构成 consumes/incoming 关系。推导边界：体力配置与恢复节奏已由沉淀确认，但扫荡消耗的具体数值在GP-11侧维护，玩家等级对体力上限的影响属推断。UNKNOWN：玩家等级对体力上限的具体影响公式与扫荡消耗在日体力预算中的占比仍待确认。 | KNOWLEDGE_CURRENT | — | UNKNOWN |

## 证据

| ID | 类型 | 证据 | 路径 | 位置 | 状态 |
|---|---|---|---|---|---|
| SYS-OUT-GR-01-EV01 | source-excel | PlayerLv.xlsx | `D:\Vgame\Config\GameConfig\Datas\Player\PlayerLv.xlsx` | 本机SVN工作副本；sheet PlayerLv；Lv1-60、UpgradeCostExp/UpgradeGetPhy/UpgradeGetItem；核对 2026-08-18 | WORKING_COPY_SOURCE_WITH_CONFLICTS |
| SYS-OUT-GR-01-EV02 | source-excel | Power.xlsx | `D:\Vgame\Config\GameConfig\Datas\Player\Power.xlsx` | 本机SVN工作副本；sheet PlayerLv；体力/后备体力/邮票精力/跑商精力的 ItemId/RecoverTime/MaxLimit/InitialValue/OpenLv；核对 2026-08-18 | WORKING_COPY_SOURCE |
| SYS-OUT-GR-01-EV03 | numeric-deposit | 主角升级经济消耗沉淀 | `D:\数值文档\数值文档\框架v2\03_沉淀MD\经济\14_外循环_主角升级经济消耗沉淀-2026-07-08.md` | 结论、与角色升级边界、分段汇总、逐级资源表、风险与待确认 | CONFIRMED_TARGET_WITH_CONFLICT |
| SYS-OUT-GR-01-EV04 | numeric-deposit | 体力补充经济沉淀 | `D:\数值文档\数值文档\框架v2\03_沉淀MD\经济\25_外循环_体力补充经济沉淀-2026-07-09.md` | Power 配置、储能来源观察、邮票精力口径差异 | CONFIRMED_TARGET_WITH_CONFLICT |
| SYS-OUT-GR-01-EV05 | source-excel | Items.xlsx | `D:\Vgame\Config\GameConfig\Datas\items\Items.xlsx` | 本机SVN工作副本；sheet items；行旅帧片(4)=ItemSubType_Exp、储能(3)=ItemSubType_Power、记录盘(100/101/102)=ItemSubType_HeroExp；核对 2026-08-18 | WORKING_COPY_SOURCE |
| SYS-OUT-GR-01-EV06 | source-excel | globals_conf.xlsx | `D:\Vgame\Config\GameConfig\Datas\globals_conf\globals_conf.xlsx` | 本机SVN工作副本；PlayerExpItem=4、StaminaCostDropRatio=10、StaminaPotionItemId=105、StrategyStaminaPotionItemId=113；核对 2026-08-18 | WORKING_COPY_SOURCE |
| SYS-OUT-GR-01-EV07 | source-code | ConditionSystem.lua | `D:\Vgame\HorizonFlyProject\Lua\Logic\PlayerData\Systems\ConditionSystem.lua` | GetIsUnLock 中 UnLock_UUT_player_Grade 分支（127-128 行）与 OnConditionChanged（280-288 行） | WORKING_COPY_SOURCE |
| SYS-OUT-GR-01-EV08 | source-code | PlayerSystem.lua | `D:\Vgame\HorizonFlyProject\Lua\Logic\PlayerData\Systems\Player\PlayerSystem.lua` | GetPlayerMaxLevel（47-54 行）、CRespNotifyPlayerLvUp（435-443 行）与 OnConditionChanged 触发（259 行） | WORKING_COPY_SOURCE |
| SYS-OUT-GR-01-EV09 | source-excel | Unlock.xlsx | `D:\Vgame\Config\GameConfig\Datas\unlock\Unlock.xlsx` | 本机SVN工作副本；sheet Unlock；201～205为UnLock_UUT_player_Grade，参数24/28/31/33/35，并由ChapterLevel 10003～10007引用；核对 2026-08-18 | WORKING_COPY_SOURCE_CONFIGURED |
| SYS-OUT-GR-01-EV10 | reverse-design | 主角等级 Design Doc | `D:\Vgame_design\design\主角等级Design Doc.md` | R-02 升级体力返还、R-03 升级道具奖励、R-05 系统功能开放、工作假设 | DRAFT_REVERSE_ENGINEERED |

## 正式人工裁决

| 卡片 | 选择 | 已关闭 QID | 目标/裁决状态 | 实施状态 | 用户评论 | 证据 |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

## 问题与闭环记录

| ID | 优先级 | 生命周期 | 责任 | 问题 | 答案 | 关闭证据 |
|---|---|---|---|---|---|---|
| SYS-OUT-GR-01-Q01 | P1 | OPEN | DEFERRED_DETAIL | 玩家等级经验曲线以正式 PlayerLv.xlsx 还是 v2 节奏单源为权威？ | — | SYS-OUT-GR-01-EV03 |
| SYS-OUT-GR-01-Q02 | P1 | OPEN | DEFERRED_DETAIL | 升级道具奖励（UpgradeGetItem）为何几乎全空，正式分档口径是什么？ | — | SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV10 |
| SYS-OUT-GR-01-Q03 | P2 | OPEN | DEFERRED_DETAIL | Lv60 的 UpgradeGetPhy=40 是否在满级后仍返还？ | — | SYS-OUT-GR-01-EV01、SYS-OUT-GR-01-EV03 |
| SYS-OUT-GR-01-Q04 | P2 | OPEN | DEFERRED_DETAIL | 体力购买与自然恢复是否允许突破上限？ | — | SYS-OUT-GR-01-EV04 |
