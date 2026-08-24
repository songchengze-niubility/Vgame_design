# Vgame 项目级策划知识框架：战斗外知识域审查

> 审查日期：2026-08-14  
> 审查性质：只读；未修改 `design/`、`${VGAME_ROOT}` 配置或代码  
> 范围：玩法入口、养成、资源经济、任务与留存、商业化、社交、公会、引导与解锁、版本运营、配置与数据  
> 事实口径：先查统一知识图谱，再回源到项目 Skill、`design/`、`proposals/`、`tasks/`、真实源 Excel 存在性与客户端文件。

## 1. 结论摘要

Vgame 的战斗外闭环可以归纳为：

```text
主线/玩家等级推进
  -> Unlock / SystemOpen 开放内容入口
  -> 任务、签到、活动、商店、战令、抽卡、社交等组织留存与供给
  -> 角色、收容物/专武、旅券、映射装备、房车等完成成长
  -> 属性、技能机制、阵容宽度、构筑与玩法专属能力输入战斗
  -> 战斗结算产出通关进度、经验、Drop、排行/赛季结果、任务计数
  -> 外循环消费这些结果并继续开放、发奖、养成、留存和商业化
```

当前项目事实呈现出三个并存层级：

1. **正式系统结构已经较完整。** 主线、稳定成长副本、验证玩法，以及任务、抽卡、商店、签到、战令、邮件、公会、好友/聊天等外循环，在项目总 Skill 和发布状态登记中均有正式口径；客户端和配置图谱也能定位到对应实现或注册表。
2. **大量 Design Doc 仍是反推 Draft。** “系统正式存在”与“文档已 Approved”不是同一件事。多数 2026-06-19 Design Doc 是对已有实现的反推草稿，能作为结构和导航证据，不能单独作为新规则落地授权。
3. **2026-07 至 2026-08 的新设计迭代尚未全部进入 SVN。** 房车、收容物、章节任务、映射装备、公会新数值、碎片回收等已有确认或 ConfigReady 口径，但多处明确写了“SVN 未修改”“Pending Config”或“程序接入待完成”。

最重要的状态冲突是：`vgame-core-understanding` 仍把“专武抽卡/专武系统”列为正式外循环和成长线，但 `design/抽卡系统Design Doc.md` 在 2026-07-27 明确写“专武抽卡线已经废弃”，并转向角色与收容物抽卡；`design/主线关卡奖励重设计-2026-07-30.md` 还要求后续统一使用“收容物”。因此，**专武抽卡的现行状态应标记为“冲突/待统一 canonical”，不能继续无条件当正式现行口径。**

## 2. 状态判定口径

| 标签 | 本报告含义 | 判定依据 |
|---|---|---|
| 正式 | 纳入当前项目正式玩法/外循环结构；并不等于当前 Design Doc 已评审通过 | `skills/vgame-core-understanding/SKILL.md`、`references/current-gameplay.md`、发布状态登记、运行时/配置证据 |
| 已确认设计 | 规则或数值已获确认，但可能仍未进入 Proposal、Task、SVN 或程序 | 文档明确写 `approved`、`Design Confirmed`、`ConfigReady` 等 |
| 草案 | 文档为 `Draft`、反推草稿或讨论稿，不能直接作为实施依据 | `design/*.md` 元信息 |
| 待确认 | 缺少真实源表、开关、版本号、运行时或发布证据；或证据之间冲突 | 项目 Skill 的证据规则与版本边界 |
| 废弃/非正式 | 当前 canonical 明确排除，或较新的专项文档明确宣布废弃 | 核心 Skill 废弃清单、文档顶部历史/废弃声明 |
| 历史追溯 | 仅保留讨论、变更或旧版证据，不再是权威正文 | 文档明确“停止维护/非权威/被替代” |

注意：配置表存在、客户端类存在、图谱有节点，只能证明“有实现/残留/注册”，不能单独证明当前全量上线。当前 `SystemOpen.xlsx` 没有具名 `IsValid` 字段；发布状态应检查 `SystemOpen.CloseSys`、`Unlock`、服务器开关、活动时间、客户端版本门控和实际发布记录，不能把无表头的物理列臆断为有效性字段。

## 3. 统一战斗接口

| 战斗外域 | 向战斗提供的输入 | 如何消费战斗结果 |
|---|---|---|
| 内容入口与解锁 | `LevelId/LevelType`、编队资格、体力、挑战次数、玩法入口 | 通关状态、星级、最高层、排行、赛季分数反向驱动下一关、系统开放和结算 |
| 养成 | 角色属性、技能/天赋、阵容宽度、旅券套装、映射装备词条、账号/职业全局属性 | 战斗掉落和验证结果用于继续升级、突破、升星、装备成型及判断成长是否有效 |
| 资源经济 | 储能作为进入战斗的消耗；金币/经验/材料构成成长预算 | 首通、重复掉落、任务、排行和活动奖励进入物品账本，再流向各养成消耗口 |
| 任务与留存 | 把指定玩法、养成行为和周期目标组织成回流动机 | 通关、击杀、养成、排行等事件更新任务与活跃度，并触发 Drop/直接奖励 |
| 商业化 | 抽卡扩充角色/收容物 box；商店、战令、月卡加速资源获取 | 战斗暴露阵容与资源缺口，转化为抽卡、购买、付费线和快捷购买需求 |
| 社交与公会 | 好友、公会、聊天提供协作、比较、组织目标；公会科技设计可提供全局属性 | 战绩、活动、公会任务和公会战结果形成社交反馈、贡献、货币与排行目标 |
| 引导与解锁 | 在正确时间开放系统并教会战斗内操作/战斗外功能 | 完成关卡、等级、任务等条件触发下一段引导或功能入口；完成记录防止重复教学 |
| 版本运营 | 通过开关、活动时间、灰度和版本门控决定哪些内容可进入 | 使用参与、经济、排行和异常结果决定热修、关闭、回滚、补偿和后续版本调整 |

## 4. 分域审查

### 4.1 玩法与内容入口

| 子域 | 当前状态 | 战斗输入 | 战斗结果的外循环去向 | 主要证据 |
|---|---|---|---|---|
| 主线 | 正式；系统 Design Doc 为反推 Draft | 提供主战斗轴、剧情、早期编队与教学，承载功能开放前置 | 通关、星级、章节推进触发 Unlock/SystemOpen、章节任务、首通/常规奖励 | `design/主线关卡系统Design Doc.md`；`Datas/level/MainLevel.xlsx`、`ChapterLevel.xlsx`、`level.xlsx`、`UIlevel.xlsx` |
| 高难主线 | 正式玩法层存在；2026-07-30 七章/35关新方案已确认但配置边界明确为未落表 | 提供更高体力与次数约束下的进阶战斗入口 | 首通、常规掉落、星级奖励回流到宝石/成长与章节进度 | `design/高难主线关卡奖励重设计-2026-07-30.md` |
| 金币、角色经验、专武经验资源副本 | 正式稳定成长层；各 Design Doc 为 Draft | 消耗储能，检验基础清怪与稳定战斗能力 | 产出金币、角色经验、专武经验；直接喂给基础养成 | `design/金币副本Design Doc.md`、`角色经验副本Design Doc.md`、`专武经验副本Design Doc.md`；`UIlevel.xlsx`、`level.xlsx` |
| 旅券副本 | 正式；Design Doc 为 Draft | 以四个 Boss 型副本验证中期机制、DPS、生存和节奏处理 | 产出旅券及相关成长资源，反哺角色构筑 | `design/旅券副本Design Doc.md`；`LevelType_Strategy_First/Second/Three/Four` |
| 映射装备副本 | 正式；旧系统 Doc 为 Draft，新数值追溯文档非权威 | 提供后期短循环 farm 和终局掉落追求 | 产出映射装备、宝石/相关资源，形成随机深度与分解/打造闭环 | `design/映射装备系统Design Doc.md`；`design/映射装备数值超级爆改-2026-08-14.md` 顶部非权威声明；`UIlevel.xlsx`、映射装备配置族 |
| 无限挑战、PVPVE、爬塔、大秘境、BOSS挑战 | 正式验证层；版本号待确认；各 Design Doc 多为 Draft | 分别验证耐久与账号深度、竞争效率与基地生存、单队纵深、box breadth/环境适配、Boss处理 | 最高层、排名、赛季分数、首通/周期奖励进入任务、货币、排行和长期目标 | `skills/vgame-growth-combat-conversion-map/references/verification-mode-map.md`；相关玩法 Design Doc 与 Arena/Tower/mythic 配置族 |
| 跑商 | 待确认是否纳入当前正式结构；仓库文件仅为索引，SVN `Datas/Trade` 明示为临时测试值 | 可能接收房车储藏架载货量等战斗外成长，不直接提供常规战斗力 | 产出商品筹码/职业便签等，用于房车和商店闭环 | `design/跑商玩法数值设计文档-2026-07-06.md`；权威沉淀 MD 路径由该索引给出 |

关键关系：主线不是一个孤立关卡列表，而是战斗外所有入口的时间轴。配置级默认链为 `LevelType.SystemId -> SystemOpen.Id -> UnlockId -> Unlock.UnLockType/UnLockParams`；具体关卡层级还要单独检查 `UIlevel.Unlock`，不能把“系统入口开放”和“某一层可挑战”混为一谈。

### 4.2 养成

| 养成模块 | 状态与职责 | 向战斗提供的输入 | 如何消费战斗结果 | 证据与缺口 |
|---|---|---|---|---|
| 玩家等级 | 正式横轴；Doc 为反推 Draft | 作为系统开放、角色等级上限和玩法资格的门槛 | 关卡/任务经验推动升级，升级返体力和道具，再投入战斗/成长 | `design/主角等级Design Doc.md`；`Datas/Player/PlayerLv.xlsx` |
| 角色升级/突破 | 正式；Doc 为反推 Draft | 基础生命、攻击、防御与等级上限 | 角色经验、金币、突破材料来自关卡/任务/商店等；成长后回到主线和验证玩法 | `design/角色升级与突破Design Doc.md`；突破是否直接给额外属性等仍有待确认项 |
| 角色星盘/能效 | 正式角色机制成长；Doc 为反推 Draft；“能效本”本身为废弃玩法 | 基础属性、百分比、二级属性、技能/被动节点 | 战斗产出的能效材料和进度激活节点，节点改变角色定位、输出、生存和辅助深度 | `design/角色星盘与能效Design Doc.md`；`HeroEnergyEfficiencyMap/Attr` 配置族 |
| 角色升星 | 正式高敏成长；Doc 为反推 Draft | 天赋、全属性和稀有二级属性，显著影响战斗机制与强度 | 抽卡重复转碎片，碎片作为升星消耗；满星后需要回收/余音等后续出口 | `design/角色升星Design Doc.md`；不同品质与重复转化仍有未确认项 |
| 专武 | **状态冲突**：旧 canonical 仍正式，2026-07-27 抽卡文档宣布专武抽卡线废弃 | 旧口径为基础属性、偏向属性和专属机制 | 旧链使用专武经验与重复专武；现行是否保留本体成长、仅废弃卡池，需统一确认 | `design/专武系统Design Doc.md`、`design/抽卡系统Design Doc.md` 顶部历史草案提示；核心 Skill 待同步 |
| 收容物 | 已确认设计/`ConfigReady`；最终配置镜像已生成，SVN Datas/程序待接入 | 主位、副位和未上阵收集属性，提供全局一级/二级属性；长期 box 深度高 | 收容凭证抽取、重复碎片、经验和金币进入升级升星；结果反哺全队战斗 | `design/收容物养成数值Design Doc.md`；未达到“已在 SVN 正式生效”的证据门槛 |
| 旅券 | 正式稳定装备成长；Doc 为 Draft | 六槽、2/4件套、主副属性和套装机制 | 旅券副本掉落、合成与装备替换形成稳定成型路径 | `design/旅券系统Design Doc.md`、`design/旅券副本Design Doc.md`；`Strategy*` 配置族 |
| 映射装备 | 正式终局随机成长；旧 Doc 为 Draft，最新追溯文档非权威 | 固定主属性、副词条、宝石/效果、洗练/超限等形成终局属性最优解 | 副本掉落、分解、打造和洗练消费战斗产出，继续提高 farm/终局挑战效率 | `design/映射装备系统Design Doc.md`；唯一权威被指向外部沉淀 MD；SVN同步状态需按具体变更复核 |
| 房车整备/出行指南 | 已确认设计，已进“06最终配置镜像”，SVN 未修改 | 全账号固定基础属性；按职业提供百分比与二级属性 | 爬塔挂机、跑商等结果产出房车零件/职业便签，升级后反哺主线、爬塔与挑战 | `design/房车养成系统当前版本设计-2026-07-09.md`、`房车养成系统小分叉重设计-2026-07-14.md` |
| 房车设备 | InReview；规则/数值已确认，待配置和经济验算 | 持续产金币、玩家经验、体力、旅券精力、加工资源；储藏架连接跑商 | 设备升级消费建材，生产物进入各成长/玩法；没有已确认的真实配置表 | `design/房车设备数值设计-2026-07-21.md` |
| 公会个人/公会科技 | 正式公会的新增长期设计；规则多已确认，真实源表待实施 | 个人科技已确认设计为全局生效，包含 PvE、PVPVE、竞技；公会科技提供任务/商店/成员等增益 | 公会任务、派遣、贡献提供个人/集体代币，转为科技和商店成长 | `design/公会系统Design Doc.md`；必须区分“文档已确认数值”和“源表已生效” |

成长到战斗的核心不是单一“战力”值，而是六类输出：基础面板、百分比放大、二级属性、技能/天赋机制、套装/特殊效果、阵容与账号宽度。验证玩法应分别观察 DPS、生存、能量/冷却节奏、Boss窗口、长线耐久和环境适配，不能只用总战力替代。

### 4.3 资源经济

| 账本层 | 主要资源/渠道 | 战斗关系 | 状态与风险 |
|---|---|---|---|
| 基础货币与行动资源 | 猎鹰金币、元晶、储能 | 储能进入关卡；金币支付升级/突破/装备/房车等；元晶连接抽卡、商店和公会创建等 | 正式；元晶、储能、金币均为高敏资源 |
| 战斗直接产出 | 首通/重复 Drop、章节星级、排行/赛季、Boss/副本奖励 | 战斗结果直接写入物品账本 | 必须区分 `UIlevel.Reward/FirstReward` 预览与真实 `DropId`；逻辑 Drop 合并八个源文件 |
| 周期供给 | 日/周任务、签到、战令、活动、月卡、商店刷新 | 为持续挑战和养成提供资源补给 | 周期、领取次数、刷新、限购、活动时间必须明确；不能把一次性邮件算作常态日收入 |
| 抽卡资源 | 角色票、收容凭证、元晶；旧专武票状态冲突 | 扩充阵容和收容物属性输入战斗 | 权重、硬保底、付费转化高风险；旧凭证 112 停用与换算为 107 属新设计口径 |
| 装备/成长材料 | 角色经验、突破/能效材料、旅券、映射装备材料、房车材料 | 将战斗产出转换为属性、机制与构筑 | 旅券偏稳定，映射装备偏随机深度；房车/收容物部分链尚未正式接入 SVN |
| 社交/玩法货币 | 竞技币、公会个人/集体代币、商品筹码、活动积分 | 战斗/任务/社交活动结果转为商店或科技消费 | 具体来源次数和正式表需逐项展开，不能仅凭 `Items.AccessList` 断言真实产出 |

配置证据入口：

- 物品主索引：`D:/Vgame/Config/GameConfig/Datas/items/Items.xlsx`。
- 关卡与奖励引用：`Datas/level/level.xlsx`、`UIlevel.xlsx`。
- 真实奖励包：逻辑 `Drop`，输入 `Drop_draw.xlsx`、`Drop_dungeon.xlsx`、`Drop_mainlevel.xlsx`、`Drop_other.xlsx`、`Drop_GiftBox.xlsx`、`Drop_TimeLimitedActivity.xlsx`、`Drop_world.xlsx`、`Drop_BattlePass.xlsx`。
- 任务/活动/商业化：`Task`、`Daily/Weekly*`、`BattlePass*`、`SignInReward/*`、`Activity/*`、`Mail/PresendMail`、`DrawCard*`、`Shop*`、`MonthCard`。

已知历史基线缺口：2026-06-16 的只读扫描发现 `UIlevel` 引用的 601 个 DropId 中，`60004`、`60005`、`10000001`、`10000002` 未在逻辑 Drop 集合中找到。该基线不能自动归因于后续变更，但后续奖励审查必须重新验证。

### 4.4 任务与留存

| 系统 | 职责/周期 | 战斗输入与结果消费 | 状态 | 证据 |
|---|---|---|---|---|
| 章节任务 | 推进提示与关键养成承接；按章节一次性 | 消费主线进度、养成里程碑；奖励再补充养成 | 基础系统正式；七章重设计已确认，尚未进入 Proposal/Task/Excel/SVN | `design/任务系统Design Doc.md`；`design/章节任务重设计讨论稿-2026-07-22.md` |
| 每日任务/日活跃 | 日常留存和基础供给 | 消费每日战斗/养成行为事件；产出活跃点与奖励 | 正式；通用 Doc 为 Draft | `Task.xlsx`、`DailyTask.xlsx`、`DailyActiveReward.xlsx` |
| 每周任务/周奖励 | 中周期目标和资源节奏 | 累积多日玩法/养成结果，触发阶段奖励 | 正式；周期刷新口径需以运行时和配置复核 | `WeeklyTask.xlsx`、`WeeklyReward.xlsx` |
| 签到 | 日常、七日、月累计、长期累计留存 | 不直接消费战斗结果，但为战斗和成长补充票券/资源 | 正式；Doc 为 Draft；七日签到是否永久开放仍待确认 | `design/签到系统Design Doc.md`；`SignInReward/*.xlsx` |
| 通行证 | 赛季型留存 + 免费/付费双线 | 任务/活动行为产生 BP EXP，等级解锁奖励再投入成长/战斗 | 正式；Doc 为 Draft；首期时长和领取窗口待确认 | `design/通行证系统Design Doc.md`；`BattlePass*.xlsx` |
| 活动/十四日/双倍掉落 | 限时刺激、追赶和版本内容承载 | 消费活动任务与战斗次数；双倍掉落直接改变重复产出效率 | 配置和客户端系统存在；当前活动目录、时间、正式发布状态待确认 | `Activity.xlsx`、`ActiveReward.xlsx`、`DoubleDropActivity.xlsx`、`FourteenDayActivity.xlsx`；客户端 `ActivitySystem.lua`、`FourteenDayTaskSystem.lua` |
| 邮件/补偿 | 消息、运营投放和异常补偿 | 消费运营/活动/回滚结果，不是常态战斗收入 | 正式；Doc 为 Draft | `design/邮件系统Design Doc.md`；`Mail.xlsx`、`PresendMail.xlsx` |
| 扫荡 | 降低重复战斗成本，连接历史通关与日常资源获取 | 以已通关/历史记录为输入，直接结算关卡奖励；可能放大战斗结果的长期效率 | 正式主线外循环；必须核对 `MopUp`、体力和多倍结算 | `level.xlsx`、`UIlevel.xlsx`、`ItemSweep.xlsx`；核心 Skill 正式外循环清单 |

### 4.5 商业化

| 系统 | 商业化职责 | 战斗输入 | 消费战斗结果/反馈 | 状态与风险 |
|---|---|---|---|---|
| 角色/收容物抽卡 | box 扩展、重复转碎片、核心付费消耗 | 新角色/收容物提供阵容宽度、机制与全局属性 | 战斗暴露阵容缺口；重复转化进入升星、余音和碎片回收闭环 | 抽卡系统正式；具体“角色+收容物”新口径需同步 canonical；权重表当前正式源逐抽权重为 0 的文档声明意味着只能确认硬保底 |
| 专武抽卡 | 旧口径为机制深度和第二商业化轴 | 旧专武强化角色技能机制 | 旧重复专武进入升星 | **冲突/待确认**；新文档明确废弃，核心 Skill 尚未同步 |
| 商店 | 多货币消耗、付费直购、资源转换 | 购买角色/装备/成长资源加速战斗准备 | 战斗/任务获得的货币在商品、限购、刷新中消耗 | 正式；Doc 为 Draft；需检查 `RefreshType/LimitType/LimitNum/Unlock/PayProduct` |
| 战令 | 免费与付费线叠加的赛季变现 | 奖励提升成长速度与阵容准备 | 任务/活动结果转 BP EXP，再触发普通/付费奖励 | 正式；周期、预览与真实奖励一致性高风险 |
| 月卡 | 小额 recurring、立即奖励、每日返还、体力上限 | 稳定资源和体力提高可玩时长/养成速度 | 登录领取，不直接依赖战斗结果 | 配置和客户端实现存在，但发布登记仍为“待确认”；不能因表存在判 LIVE |
| 快捷购买/充值商品 | 资源不足时的即时付费转化 | 补足抽卡或成长资源 | 战斗卡点和资源短缺形成购买触发 | 能力存在；具体商品、定价、付费开关和地区状态待确认 |
| 碎片回收/余音回抽 | 满星后碎片消耗和回收体验 | 降低无效重复，间接维持 box 深度 | 满星重复碎片转余音，再可回到旅券/抽卡资源 | 规则评审就绪但未达配置实施门禁；存在高敏感“回抽链”风险，需概率和成熟账号专项测算 |

商业化结论：当前最需要治理的是“旧专武商业化轴”向“收容物抽卡/养成轴”的迁移状态。如果 canonical、Design、真实卡池、票券投放和商店商品不同步，会同时造成玩家预期、经济、任务奖励和版本内容冲突。

### 4.6 社交

| 子系统 | 状态 | 战斗关系 | 证据与缺口 |
|---|---|---|---|
| 好友 | 正式外循环 | 主要提供在线关系、申请/互动、组队或比较入口；默认不承担核心成长供给 | 客户端 `D:/Vgame/HorizonFlyProject/Lua/Logic/PlayerData/Systems/Friend/FriendSystem.lua` 与 `D:/Vgame/HorizonFlyProject/Lua/Logic/EventDefine/FriendEvent.lua` 存在；仓库无独立好友 Design Doc，规则、奖励、上限和版本状态待补 |
| 聊天 | 正式外循环 | 世界/公会/私聊承载交流、招募和战绩反馈，不应默认产生经济资源 | 客户端 `D:/Vgame/HorizonFlyProject/Lua/Logic/PlayerData/Systems/Chat/ChatSystem.lua`、`D:/Vgame/HorizonFlyProject/Lua/Logic/EventDefine/ChatEvent.lua` 与 Chat 配置族存在；仓库无独立聊天 Design Doc，频道治理、屏蔽举报、频率与留存指标待补 |
| 组队/邀请 | 图谱能定位 UI 邀请与队伍聊天组件，但不在核心正式外循环清单中单列 | 可能把社交关系转为协作战斗入口 | 当前只作为实现线索，正式玩法范围、奖励、匹配和版本状态待确认 |

社交域的主要缺口不是“没有代码”，而是**缺少策划层权威文档**。好友/聊天虽然被核心 Skill 列为正式，但规则、经济边界、治理与指标无法从 `design/` 获得完整可追踪判断链。

### 4.7 公会

公会是正式外循环，也是当前设计信息最丰富但“文档确认与真实配置同步”最容易混淆的领域。

| 子模块 | 当前口径 | 向战斗提供输入 | 如何消费战斗/行为结果 | 状态 |
|---|---|---|---|---|
| 创建/成员管理 | 等级20开放、创建消耗、退出冷却等结构 | 提供组织归属和协作入口 | 成员行为进入公会日志、权限和留存关系 | 基础系统正式；Doc 总状态仍为 Draft |
| 公会任务/贡献 | 有效贡献按设计 1:1 产公会经验、集体代币、个人代币 | 资源可投入科技、商店与补给 | 消费成员日常/任务完成结果 | 多项规则已确认；具体任务项仍延后，真实源表待实施 |
| 公会派遣 | 每日派遣角色、按品质产个人代币与额外资源 | 占用角色但不是常规战斗；提供经济补充 | 派遣结果转为个人代币和奖励 | 数值规则已确认；需核对正式配置与服务端 |
| 公会商店 | 使用个人代币购买资源 | 商品补充成长并进入战斗准备 | 消费公会活动所得货币 | 首批商品数值文档已确认；源表同步仍需检查 |
| 个人科技 | 11节点/38级的全局属性树 | 文档已确认全局影响 PvE、PVPVE、竞技 | 消费个人代币 | 新设计已确认，真实实现/配置待核 |
| 公会科技 | 任务、派遣、商店、成员、补给等组织增益 | 间接提高经济效率；非全都直接加战斗属性 | 消费集体代币 | 新设计已确认，真实实现/配置待核 |
| 公会补给 | 周期性集体资源消耗与成员奖励 | 提供金币、角色经验、元晶、旅券等 | 消费公会积累结果 | 规则已确认，发奖与资格需幂等/周期验证 |
| 公会战 | 历史流程草案 | 可能是组织级战斗验证 | 结果进入排行/奖励/组织目标 | 本轮明确范围外；不应纳入当前已确认新设计 |
| 公会拍卖 | 不做 | 无 | 无 | 当前版本明确废弃/排除 |

证据：`design/公会系统Design Doc.md`；配置图谱中的 `GuildLv`、`GuildMission`、`GuildComission`、`GuildBuilding`、`Guild*` 表；客户端 `D:/Vgame/HorizonFlyProject/Lua/Logic/PlayerData/Systems/Guild/GuildSystem.lua`。

### 4.8 引导与解锁

Vgame 使用三层串联：

```text
主线/等级/任务条件
  -> Unlock
  -> SystemOpen 显示并开放功能
  -> NewbieGuide 在战斗外教功能

进入关卡并到达触发区
  -> ZoneShowGuide
  -> BattleGuide 教跳跃、下蹲、技能、必杀等战斗操作
```

| 系统 | 触发与职责 | 持久化/完成 | 状态与证据 |
|---|---|---|---|
| BattleGuide | 关卡内 `ZoneShowGuide` 位置触发；16 种动作类型，可暂停/恢复 | `HistoricalCompletedGuideIds` 防重复 | 正式实现能力；`Datas/Guide/BattleGuide.xlsx`，客户端 `D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.GameLogic/Runtime/Combat/GuideMgr.cs`、`D:/Vgame/HorizonFlyProject/Packages/VGame/VGame.Lockstep/Runtime/Logic/TriggerData/ZoneShowGuide.cs`；Design Doc 为 Draft |
| NewbieGuide | Unlock/系统开放或 UI 打开触发；Sequence + Step 控制遮罩、气泡、箭头、点击/拖拽 | 完成序列同步服务器，断线恢复；ExpireId 防过时引导 | 正式实现能力；`NewbieGuideSystem.lua`、`GuideSequenceData_Auto.lua`、`GuideStepData_Auto.lua`、GuideEditor；Design Doc 为 Draft |
| SystemOpen | 控制入口、父子系统、关闭、隐藏、常驻、弹窗、跳转和有效性 | 根据 Unlock 条件动态可用 | 源表存在；Skill 观察为 92 个系统，但当前源表已更新，精确有效数量需重新扫描 |
| Unlock | 通关、玩家等级、任务、爬塔层数、角色等条件 | 条件满足后广播开放事件 | Skill 观察为 682 条；当前源表已更新，精确有效数量需重新扫描 |

首小时高层口径为约 24 步：0-3 分钟开场/首关，3-10 分钟战斗操作教学，10-15 分钟首轮 UI 功能引导，15-21 分钟强制引导收束，之后转为 SystemOpen 与弱引导。该时间线来自专项 Skill 的项目映射，不应替代实际埋点和当前引导配置验收。

高风险点：`SystemOpen.CloseSys=true`、`BattleGuide.IsValid=false`、Sequence.UnlockId 不匹配、TargetNode 不存在、动态 UI 时序、强制跳转与弹窗冲突、完成节点未上报、系统入口与关卡层级 Unlock 混淆。不要把 `BattleGuide.IsValid` 外推为 `SystemOpen.IsValid`。

### 4.9 版本运营

| 能力 | 当前证据 | 判定 |
|---|---|---|
| 发布生命周期 | 项目 Skill 定义 `PLAN -> DEV -> INTERNAL_TEST -> GRAY -> LIVE -> MAINTAIN -> DEPRECATED -> REMOVED` | 可作为统一状态模型 |
| 配置开关 | `SystemOpen.CloseSys`、Unlock、活动时间；`BattleGuide.IsValid` 仅属于引导表 | 有真实配置入口；不能替代服务器全局/灰度开关；当前 `SystemOpen` 无具名 `IsValid` |
| 服务器开关/AB/灰度 | 仅有框架和模板，无当前实验、流量或人群登记 | 待确认 |
| 客户端版本门控 | 有概念模型，无当前最低版本/资源版本证据 | 待确认 |
| 版本号/节奏 | `version-milestone-overview.md` 全部明确为待确认 | 不能编造当前版本号、发布日期或 Minor 周期 |
| 功能状态登记 | `release-status-registry.md` 将主要玩法和多数外循环标为 LIVE，月卡待确认，废弃项另列 | 可作项目口径索引；首次上线版本与最后修改版本基本未填 |
| Hotfix/回滚日志 | 专项日志仍是空模板 | 项目缺少集中、可审计的真实历史台账 |
| 实际回滚案例 | `tasks/主线前三章删关奖励调整-2026-07-13.md` 明确记录因“先对设计、不修改配置”而撤回 UIlevel、ChapterStarReward 和生成 JSON 变更 | 已观察到一次真实治理/回滚证据 |

版本域的核心问题是：**有模型、有开关、有零散任务记录，但没有持续维护的版本—功能—开关—配置—回滚单一登记表。** 因此，任何“当前已上线”“某版本首次上线”“正在灰度”的精确结论都应继续标 `待确认`。

### 4.10 配置与数据

配置数据链路已确认如下：

```text
Datas 源 Excel
  -> __tables__.xlsx 注册逻辑表/输入文件
  -> __beans__.xlsx 定义 PropType 等复合类型
  -> __enums__.xlsx 定义枚举
  -> export_excel.py 扁平复制到 TempDatas
  -> Luban
  -> server/json + 客户端 bytes/Lua/C# 生成物
  -> CheckRules + 项目专项校验
```

| 数据域 | 核心源表 | 关键引用 | 与战斗闭环的职责 |
|---|---|---|---|
| 关卡/入口 | `level.xlsx`、`UIlevel.xlsx`、`MainLevel.xlsx`、`ChapterLevel.xlsx`、`LevelType.xlsx` | `LevelId`、`LevelType`、`Unlock`、`SystemId`、`MopUp`、`Vitality` | 决定进入什么战斗、何时开放、消耗什么、如何结算 |
| 开放/引导 | `Unlock.xlsx`、`SystemOpen.xlsx`、`BattleGuide.xlsx`、GuideEditor 生成数据 | `UnlockId`、`SystemOpen.CloseSys`、`BattleGuide.IsValid`、Sequence/Step | 把进度条件、入口和教学连接起来；两个表的字段不得混写 |
| 奖励/经济 | `Items.xlsx`、逻辑 `Drop`、`UIlevel.xlsx` | `ItemId`、`DropId/RewardId`、预览字段、`PropType` | 将战斗和外循环结果落入物品账本 |
| 任务/留存 | `Task.xlsx`、`Daily/Weekly*`、`BattlePass*`、`SignInReward/*`、`Activity/*`、`Mail/*` | 任务目标、活跃点、奖励引用、周期/活动条件 | 消费战斗/养成事件并产生回流供给 |
| 商业化 | `DrawCard*`、`Shop/ShopGoods`、`PayProducts`、`MonthCard` | 价格、票券/元晶、池、权重、限购、付费商品 | 把 box 和资源缺口转换为消费，并向成长/战斗供给 |
| 成长 | 角色、星盘、收容物/专武、`Strategy*`、`SpecialEquipment*`、Guild/房车候选表 | 属性、技能、套装、材料消耗、全局增益 | 将资源转换为可验证的战斗表现 |

本次只读存在性核对确认：`__tables__.xlsx`、`__beans__.xlsx`、`__enums__.xlsx`、Items、level、UIlevel、MainLevel、ChapterLevel、Unlock、SystemOpen、Task、DailyTask、WeeklyTask、BattlePass、DailySign、Activity、Mail、PresendMail、DrawCard、Shop、ShopGoods、MonthCard、PlayerLv、BattleGuide 均在 `D:/Vgame/Config/GameConfig/Datas` 下存在；其中多张源表在 2026-08-13/14 有更新。

路径漂移：`vgame-config-schema` 的现有参考文档仍写生成目标为 `Config/GameConfig/server_json`，但本机当前 `scripts/path_config.py` 明确配置为 `SERVER_PATH=Config/GameConfig/server`、`SERVER_JSON_PATH=server/json`，且 `D:/Vgame/Config/GameConfig/server/json` 实际存在。因此当前生成物证据应以 `server/json` 为准，并回补 Skill 文档；两者都不是策划编辑源。

图谱来源与时效风险：

- 当前仓库图谱 `.understand-anything/knowledge-graph.json` 生成于 2026-08-14，包含 3013 节点、2327 边；本项目框架的 52/52 Design 文档匹配只指这份当前仓库图谱。
- 旧跨仓快照 `knowledge-graph/.understand-anything/knowledge-graph.json` 生成于 2026-06-23，包含 1896 节点、1200 边，其中 client 1550、config 281、design 65。
- `knowledge-graph/config-schema.json` 同样生成于 2026-06-23，而真实源 Excel 在 2026-08-13/14 仍有更新。
- 2026-07/08 新增的房车、收容物、章节任务、映射装备、公会与碎片回收文档并未全部进入该旧跨仓图谱。

因此，当前仓库图谱适合做 Design 文档导航；旧跨仓图谱适合定位历史 client/config 线索。两者都不适合直接宣称 2026-08-14 的字段、有效行或功能状态已经同步。正式实施前应重建跨仓图谱/Schema，并对目标 Excel 重新读取 row 1-4 表头与有效数据行。

## 5. Design 文档映射

| 知识域 | 文档 | 文档状态/权威性 | 主要用途 |
|---|---|---|---|
| 玩法入口 | `design/主线关卡系统Design Doc.md` | Draft，反推草稿 | 主线推进、奖励、章节与 SystemOpen 基础链 |
| 玩法入口/经济 | `design/主线关卡奖励重设计-2026-07-30.md` | Draft，但多项口径已确认；未读取/修改真实配置 | 99 关普通主线的新奖励口径；含“收容物”术语迁移 |
| 玩法入口/经济 | `design/高难主线关卡奖励重设计-2026-07-30.md` | 结构与奖励已确认；未落具体配置 | 七章高难、储能、次数、宝石与星级奖励 |
| 账号进度 | `design/主角等级Design Doc.md` | Draft，反推草稿 | 玩家等级、经验、体力返还、功能开放横轴 |
| 养成 | `design/角色升级与突破Design Doc.md` | Draft，反推草稿 | 角色等级、突破与基础属性 |
| 养成 | `design/角色升星Design Doc.md` | Draft，反推草稿 | 碎片、天赋、高价值星级节点 |
| 养成 | `design/角色星盘与能效Design Doc.md` | Draft，反推草稿 | 能效/星盘/技能树与节点成长 |
| 养成/商业化 | `design/专武系统Design Doc.md` | Draft，旧口径；需受 2026-07-27 废弃声明约束 | 旧专武成长和卡池链 |
| 养成/商业化 | `design/收容物养成数值Design Doc.md` | ConfigReady；最终配置镜像完成，SVN/程序待接入 | 收容物位置、等级、星级、碎片和全局属性 |
| 养成 | `design/旅券系统Design Doc.md` | Draft | 旅券装备、套装、合成和稳定成长 |
| 养成/玩法 | `design/旅券副本Design Doc.md` | Draft | 四 Boss 副本和旅券稳定产出 |
| 养成 | `design/映射装备系统Design Doc.md` | Draft | 终局随机装备结构 |
| 养成 | `design/映射装备数值超级爆改-2026-08-14.md` | 已停止维护、非权威；仅变更追溯 | 记录 2026-08-14 approved 变更，不能替代沉淀 MD |
| 养成 | `design/房车养成系统当前版本设计-2026-07-09.md` | Draft/CurrentDecision；部分被后续文档替代 | 房车整备仍有效；旧出行指南需看后续文档 |
| 养成 | `design/房车养成系统小分叉重设计-2026-07-14.md` | 数值/产出已确认，镜像已同步，SVN 未修改 | 出行指南、职业材料、爬塔挂机供给 |
| 养成/经济 | `design/房车设备数值设计-2026-07-21.md` | InReview；规则数值确认，待配置/经济验算 | 生产设备、储藏架、跑商连接 |
| 内容/经济 | `design/跑商玩法数值设计文档-2026-07-06.md` | 索引，正文不在本仓库 | 指向权威沉淀 MD；SVN Trade 为临时测试值 |
| 经济/玩法 | `design/金币副本Design Doc.md`、`角色经验副本Design Doc.md`、`专武经验副本Design Doc.md` | Draft | 日常稳定资源供给与解锁 |
| 任务/留存 | `design/任务系统Design Doc.md` | Draft | 日/周/章节/引导任务结构 |
| 任务/留存 | `design/章节任务重设计讨论稿-2026-07-22.md` | Design Confirmed / Pending Proposal & Config | 七章章节任务新口径 |
| 留存 | `design/签到系统Design Doc.md` | Draft | 日签、七日、月累计、长期累计 |
| 留存/商业化 | `design/通行证系统Design Doc.md` | Draft | 赛季经验、免费/付费奖励线 |
| 商业化 | `design/抽卡系统Design Doc.md` | Draft；顶部 2026-07-27 新声明覆盖旧专武双线 | 角色/收容物现行抽卡索引与旧草案边界 |
| 商业化 | `design/商店系统Design Doc.md` | Draft | 多货币、刷新、限购、付费商品 |
| 商业化 | `design/月卡系统Design Doc.md` | Draft；发布状态待确认 | 立即/每日奖励、体力上限、付费商品 |
| 运营/补偿 | `design/邮件系统Design Doc.md` | Draft | 文本邮件、预发邮件、附件与过期 |
| 商业化/经济 | `design/碎片回收Design Doc.md` | 规则评审就绪；服务端回源未完成，未达配置门禁 | 满星碎片、余音回收、回抽风险 |
| 社交/公会 | `design/公会系统Design Doc.md` | 总状态 Draft；内部多项 2026-07/08 规则已确认 | 公会任务、派遣、商店、科技、补给、范围排除 |
| 引导 | `design/新手引导系统Design Doc.md` | Draft，反推 | BattleGuide、NewbieGuide、SystemOpen/Unlock |
| 配置数据 | `design/配置表管线Design Doc.md` | Draft，反推 | Excel/Luban/JSON/代码生成和校验 |
| 经济新功能 | `design/局内金币带出Design Doc.md` | Draft；规则已确认，无阻塞待确认，但尚属设计 | 手动战斗记录转扫荡额外金币；未证明已实现 |

缺失的 Design 文档：好友、聊天、通用活动、版本发布/灰度/AB/Hotfix 没有对应的长期策划 Design Doc。现有事实主要散落在 Skill、客户端实现、配置表和任务记录中。

## 6. 废弃、草案与冲突清单

### 6.1 Canonical 废弃或非正式

- 世界 Boss。
- 能效本；注意角色“能效/星盘”成长仍正式，废弃的是独立能效副本。
- 主角装备本、独立宝石本、铭文本；`design/archive/宝石与铭文Design Doc.md` 是归档证据。
- 肉鸽。
- BOSS 无限挑战：核心快照列为 Draft/非正式，不应混入正式 BOSS挑战或无限挑战。
- 公会拍卖：`design/公会系统Design Doc.md` 明确当前版本不做。

### 6.2 被后续文档替代或降级为历史证据

- `design/房车养成系统数值设计文档-2026-07-03.md` 的出行指南部分被 2026-07-14/16 口径替代。
- `design/房车养成系统当前版本设计-2026-07-09.md` 中出行指南结构继续被后续小分叉重设计替代；房车整备仍有效。
- `design/映射装备数值超级爆改-2026-08-14.md` 明确停止维护、非权威，只作变更追溯。
- `design/抽卡系统Design Doc.md` 正文中的专武双线、软保底和 112 凭证旧描述受顶部 2026-07-27 新声明约束。

### 6.3 需要尽快统一的冲突

1. **专武抽卡：** 核心 Skill/发布登记仍正式，较新抽卡文档已废弃。
2. **专武术语与收容物迁移：** 新主线奖励文档要求统一“收容物”，但多个正式 Skill、资源副本、设计 Doc 和配置族仍使用专武。
3. **旧跨仓图谱与真实源时效：** 当前仓库图已更新并覆盖 52/52 Design；但承载 client/config 的旧跨仓图谱与 Schema 停留在 2026-06-23，不能覆盖后续源表变更。
4. **文档状态与系统状态：** 许多正式系统的 Design Doc 仍是 Draft，容易被误判为“系统未上线”或相反“文档内新规则已生效”。
5. **版本状态：** 发布登记给出 LIVE，但实际版本号、开关、灰度范围和首次上线证据仍空缺。

## 7. 项目级缺口与优先级

| 优先级 | 缺口 | 影响 | 建议产物 |
|---|---|---|---|
| P0 | 专武 -> 收容物迁移没有统一 canonical 状态 | 抽卡、票券、资源本、任务、商店、养成和术语可能互相冲突 | 一页迁移决议：保留/废弃范围、兼容资源、配置表、系统开关、版本状态、回滚方案 |
| P0 | 旧跨仓图谱/Schema 索引过期 | 最新 Excel 字段和 client/config 关系可能漏检，跨域判断失真 | 重建跨仓知识图谱；保留当前仓库图用于 52 份 Design 映射，并记录两者生成时间与源表 commit/SVN revision |
| P0 | 缺少集中版本/开关/回滚登记 | 无法可靠回答“是否 LIVE/GRAY/何版本上线” | 版本功能注册表：Feature、Version、State、Switch、Config impact、Owner、Rollback、Evidence |
| P1 | 好友/聊天没有策划 Design Doc | 正式社交系统缺少规则、治理、奖励边界和指标 | `design/好友与聊天系统Design Doc.md` 或拆成两篇，明确无经济供给/组队边界/审核治理 |
| P1 | 活动系统只有配置映射，没有当前活动目录与节奏 | 活动供给、双倍、任务、版本内容无法做长期审计 | 活动日历 + ActivityId/AvyId/任务/Drop/商店/版本映射 |
| P1 | 已确认设计与 SVN 落地状态混杂 | 房车、收容物、公会、章节任务、映射装备容易被误当已生效 | 每篇设计附“设计状态 / 配置镜像 / SVN Datas / 客户端 / 服务端 / 验证”五段状态栏 |
| P1 | 经济账本没有持续全量更新 | 无法量化资源供需与商业化压力 | ItemId 级 source/sink/cadence/limit/paid/unlock 账本，Drop 展开与活动周期分层 |
| P2 | 引导首小时口径缺埋点验证 | 时间线可能与当前配置/玩家行为偏离 | 引导序列—系统开放—关卡—完成率—失败原因映射 |
| P2 | `proposals/`、`tasks/` 状态有局部不一致 | 例如“任务待开始”但子任务已完成，影响交付判断 | 状态机校验与 `Design -> Proposal -> Task -> Config` 自动追踪 |

## 8. 证据索引

### 项目规则与图谱

- `D:/Vgame_design/AGENTS.md`
- `D:/Vgame_design/knowledge-graph/KG-AI-RULES.md`
- `D:/Vgame_design/knowledge-graph/.understand-anything/knowledge-graph.json`
- `D:/Vgame_design/knowledge-graph/.understand-anything/meta.json`
- `D:/Vgame_design/.understand-anything/knowledge-graph.json`（2026-08-14 当前仓库图；本框架 52/52 文档映射来源）
- `D:/Vgame_design/knowledge-graph/config-schema.json`
- `D:/Vgame_design/knowledge-graph/design-docs.json`

### 核心与专项 Skill

- `D:/Vgame_design/skills/vgame-core-understanding/`
- `D:/Vgame_design/skills/vgame-outer-loop-system-map/`
- `D:/Vgame_design/skills/vgame-growth-combat-conversion-map/`
- `D:/Vgame_design/skills/vgame-economy-source-map/`
- `D:/Vgame_design/skills/vgame-level-progression-map/`
- `D:/Vgame_design/skills/vgame-tutorial-onboarding-map/`
- `D:/Vgame_design/skills/vgame-version-release-map/`
- `D:/Vgame_design/skills/vgame-config-schema/`
- `D:/Vgame_design/skills/vgame-reward-drop-sync/`

### 真实项目只读入口

- 源 Excel：`D:/Vgame/Config/GameConfig/Datas/`
- 生成 JSON：`D:/Vgame/Config/GameConfig/server/json/`（当前 `path_config.py` 的真实目标；生成物，不是编辑源）
- 客户端：`D:/Vgame/HorizonFlyProject/`
- 本地环境：`D:/Vgame_design/local.env.bat`、`C:/Users/songchengze/AppData/Local/Vgame/design-harness.env.bat`

### 版本/治理案例

- `D:/Vgame_design/tasks/主线前三章删关奖励调整-2026-07-13.md`
- `D:/Vgame_design/proposals/主线首通金币翻倍-2026-06-19.md`
- `D:/Vgame_design/tasks/主线首通金币翻倍-2026-06-19.md`

## 9. 审查边界

- 本报告没有展开每个 DropId、ItemId、RewardId 或真实有效数据行，不能替代配置实施审计。
- 本报告没有将 `Items.AccessList`、奖励预览字段、生成 JSON 或图谱推断边当作真实产出/外键证明。
- 本报告没有把客户端代码存在等同为正式上线，也没有为缺失的版本号、AB、灰度或活动时间编造结论。
- 外部“沉淀 MD”和“06 最终配置镜像”仅按仓库索引记录其权威关系；本次未对外部数值文档做全量数值审计。
- 若进入实施阶段，必须按目标系统重新读取真实 Excel 的 `##var/##type/##group/##` 表头、有效行、公式、逻辑表注册和所有引用，并运行对应导出与专项校验。
