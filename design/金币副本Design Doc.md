# 金币副本 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 金币副本（Coin Dungeon） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | `MEDIUM` |
| 关联 Proposal | — |

## 背景与目标
### 背景
金币副本是玩家日常金币产出的核心管道。当前金币消耗项包括角色升级、装备强化、技能升级等，消耗曲线随等级指数增长。需要一条稳定、可控的每日金币供给线，避免玩家因金币瓶颈卡进度、或因过量产出导致经济膨胀。

### 目标
1. 提供每日稳定金币产出管道，填充 F2P 日常金币缺口
2. 通过 9 档难度阶梯控制产出与练度挂钩，防止低练度账号快速膨胀
3. 以 CoinMode 特殊游玩模式实现"清怪 + 拾取"双核心体验，区别于普通 PvE 战斗
4. 控制单局时长在 60-90 秒内，保证日常效率

### 非目标
- 不替代主线/支线的首通一次性金币奖励（首通是一次性，副本是重复性）
- 不引入 PvP 金币抢夺等竞争机制
- 不设计金币抽奖/赌博消耗入口

## 核心规则
### R-01: 副本开放与解锁
- **触发条件**：通关主线 1-6（关隘：1-6）
- **前置限制**：SystemOpen 表中金币副本条目开启；玩家账号未被封禁
- **操作流程**：
  1. 玩家通关主线 1-6 后，SystemOpen 触发金币副本入口可见
  2. 玩家在主界面/副本界面点击金币副本入口
  3. 进入 UIlevel 难度选择界面，展示 9 档难度（根据玩家等级/主线进度逐步解锁）
- **状态变化**：系统开关 `LevelType_Gold` → Opened
- **资源变化**：无
- **UI 反馈**：主界面解锁金币副本入口图标；未解锁难度灰态显示解锁条件
- **异常边界**：若 SystemOpen 表未配置或配置错误，副本入口不可见（不出错弹窗，仅不显示）
- **落地点**：SystemOpen 表、UIlevel.xlsx

### R-02: 关卡进入与体力消耗
- **触发条件**：玩家点击难度选择面板中的"进入"按钮
- **前置限制**：
  - 玩家体力 ≥ 该难度配置的体力消耗（Vitality: item ID=3, cost=15）
  - 当日已挑战次数 < 每日上限（3-5 次，具体依配置）
  - 玩家等级满足该难度最低等级要求
- **操作流程**：
  1. 客户端校验体力、次数、等级
  2. 客户端请求服务器 `EnterCoinDungeon(difficulty_id)`
  3. 服务器扣减体力 15（item_id=3），增量当日挑战计数
  4. 服务器加载 CoinLevel 配置（OnceCoinDrop, PerCoinDrop, DeathCoinDrop, MaxCoin, TimeLimit）
  5. 客户端切换到 CoinMode 战斗场景
- **状态变化**：体力-15；当日挑战次数+1；进入战斗态
- **资源变化**：`PlayerVitality(item_id=3) -= 15`
- **UI 反馈**：体力条即时更新；剩余次数减 1；加载战斗场景过渡动画
- **异常边界**：
  - 体力不足：弹窗提示"体力不足，是否使用体力药/钻石购买？"
  - 次数不足：弹窗提示"今日挑战次数已用完，明日再来"
  - 网络超时：体力已扣但未进入战斗 → 服务器补偿体力、重置次数（通过结算校验补偿）
- **落地点**：UIlevel.xlsx（Vitality 字段）、CoinLevel.xlsx、每日计数 Redis/DB

### R-03: CoinMode 战斗 — 金币收集
- **触发条件**：成功进入金币副本关卡
- **前置限制**：CoinMode 已激活（与 NormalMode 分离的 GameMode 状态机）
- **操作流程**：
  1. 场景加载：依 CoinLevel 配置加载地图、小怪波次（MonsterId）、Boss（BossId）、金币刷新点
  2. 战斗循环：小怪波 → 击杀掉落金币 → 玩家拾取 → 波次清空 → 下一波 → 最后 Boss
  3. 金币拾取时客户端即时累加已拾取数量，显示顶部 HUD 金币计数器
  4. 计时器倒计时（TimeLimit 秒，典型值 60-90s）
- **状态变化**：GameMode=CoinMode；计时器运行中；金币计数器递增
- **资源变化**：战斗中金币计数为临时变量，不写入持久层
- **UI 反馈**：
  - HUD：剩余时间倒计时、已拾取金币数、怪物剩余波次
  - 金币拾取飘字动画（+GoldValue）
  - 倒计时 <10s 时闪烁警示
- **异常边界**：
  - 玩家战斗中掉线：服务器保留已拾取金币快照，重连后恢复倒计时
  - 玩家未拾取满地金币：时间结束后未拾取金币不计入结算（仅已拾取的有效）
  - 玩家死亡：触发 DeathCoinDrop 惩罚，死亡时角色身上金币按比例扣除
- **落地点**：CoinLevel.xlsx、CoinMode 状态机、CameraParameter.xlsx（币副本专用镜头）

### R-04: 金币结算计算
- **触发条件**：计时器归零 或 玩家手动退出 或 Boss 被击杀后自动结算
- **前置限制**：战斗结束时服务器校验结算数据完整性
- **操作流程**：
  1. 战斗结束，客户端上报：累计拾取金币数、死亡次数、是否击败 Boss
  2. 服务器计算公式：
     - `BaseCoin = OnceCoinDrop（首次通关固定奖励，仅首通有效） + 本次拾取金币 × PerCoinDrop（系数）`
     - `DeathPenalty = 死亡次数 × DeathCoinDrop（单次死亡惩罚）`
     - `FinalCoin = min(BaseCoin - DeathPenalty, MaxCoin)`
     - 若 `FinalCoin < 0` 则取 0
  3. 若为首通，额外加 OnceCoinDrop
  4. 服务器写入金币增量到 PlayerCurrency(Gold)
- **状态变化**：战斗态 → 结算态 → 副本关闭
- **资源变化**：`PlayerGold += FinalCoin`（若首通则 `+= OnceCoinDrop`）
- **UI 反馈**：结算面板展示详细构成（拾取数、系数加成、死亡惩罚、最终获得）；首通标记；与 MaxCoin 上限对比
- **异常边界**：
  - MaxCoin 上限触发：结算面板显示"已达本关金币上限"，溢出部分不发放
  - 服务器计算与客户端预览不一致：以服务器为准，客户端做误差容忍（±5% 不弹窗）
  - 掉线未重连：按掉线时刻快照结算
- **落地点**：CoinLevel.xlsx（OnceCoinDrop, PerCoinDrop, DeathCoinDrop, MaxCoin）、PlayerCurrency 表

### R-05: 难度阶梯与产出曲线
- **触发条件**：玩家选择不同难度进入
- **前置限制**：难度 1-9 逐级解锁，高难度需要更高主线进度/玩家等级
- **操作流程**：
  1. 难度从 1 到 9，怪物等级从 10 到 130，金币产出递增
  2. 策划在 CoinLevel.xlsx 每行配置一组参数（OnceCoinDrop / PerCoinDrop / MaxCoin / TimeLimit / MonsterId / BossId）
  3. 产出曲线设计原则：难度 N+1 产出 ≈ 难度 N × 1.2 ~ 1.5 倍，保持成长感但不过快
- **状态变化**：无持久状态变化（仅数值不同）
- **资源变化**：高难度产出更多金币，消耗相同体力（性价比更高，鼓励练度提升）
- **UI 反馈**：难度选择面板展示每档难度的预览产出范围（概率区间）、推荐战力、怪物等级
- **异常边界**：若高难度产出低于低难度（配置错误），走数据校验 CI 拦截（不得发版）
- **落地点**：CoinLevel.xlsx、UIlevel.xlsx（LevelType=LevelType_Gold, LevelId 关联）

### R-06: 每日挑战次数重置
- **触发条件**：服务器每日 5:00 AM 重置
- **前置限制**：无
- **操作流程**：
  1. 每日 5:00 AM，服务器调度任务批量重置所有玩家金币副本挑战计数为 0
  2. 若玩家正在进行战斗中跨越 5:00，当次战斗计入前一日次数，不占用新一日配额
- **状态变化**：挑战计数器归零
- **资源变化**：无
- **UI 反馈**：主界面副本入口恢复为满次数显示；倒计时提示"次日 5:00 重置"
- **异常边界**：服务器维护导致重置延迟 → 维护结束后补偿所有玩家当日全额次数
- **落地点**：服务器定时任务调度、Redis 计数器

## 技术方案
### 架构影响
- 新增 CoinMode 作为独立 GameMode 枚举值，需要在战斗状态机中注册
- 金币收集逻辑与 NormalMode 正交，需新增 CoinCollectComponent（ECS 组件）
- 结算公式在服务端闭环，客户端仅做预览（防作弊）
- 每日计数需引入 Redis 计数器（高并发读+写），支持 atomic increment

### 数据变更
| 表 | 变更类型 | 说明 |
|----|----------|------|
| CoinLevel.xlsx | 已有 | OnceCoinDrop, PerCoinDrop, DeathCoinDrop, MaxCoin, TimeLimit, BossId, MonsterId |
| level.xlsx | 已有 | LevelType=LevelType_Gold, LevelId 关联 CoinLevel |
| UIlevel.xlsx | 已有 | LevelType 筛选为 Gold, Vitality=15(item_id=3), 每日上限 |
| SystemOpen.xlsx | 已有 | 金币副本解锁条件（主线 1-6 通关） |
| PlayerCurrency | 已有 | Gold 字段增量写入 |
| PlayerDailyCounter | 新增/已有 | 每日副本挑战计数（gold_daily_count） |
| CameraParameter.xlsx | 已有 | 金币副本专用镜头参数 |

### 接口变更
- `EnterCoinDungeon(difficulty_id: int) -> EnterResult { scene_id, time_limit, monster_waves }`
- `SettleCoinDungeon(session_id, picked_coin, death_count, boss_killed) -> SettleResult { final_gold, breakdown }`
- `GetCoinDungeonDailyStatus() -> { remaining, total, next_reset_time }`

## 风险评估
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 经济膨胀（产出过高） | 中 | 高 — 金币贬值，F2P 前期失去付费动力 | 上线前跑 90 天经济模拟；上线后 7 天观察期，产出曲线可热更下调 |
| 外挂刷金（加速/自动拾取） | 高 | 高 — 破坏经济平衡 | 服务端结算强校验；拾取数 vs 时间 vs 地图覆盖率异常检测；MaxCoin 硬上限 |
| 每日次数重置 BUG | 低 | 中 — 部分玩家多打或少打 | 重置逻辑加幂等校验；加监控告警 |
| 掉线补偿漏洞（刷补偿金） | 中 | 中 — 恶意断线刷补偿 | 补偿校验同 session 只发一次，补偿量不超过该难度产出中位数的 50% |
| 高难度解锁卡玩家（体验差） | 低 | 低 — 仅影响高练度玩家 | 解锁条件合理（主线进度自然解锁），不与氪金强绑定 |

## 工作假设
| 假设 | 状态 | 澄清结论 |
|------|------|----------|
| 每日挑战次数范围为 3-5 次 | 待确认 | 需策划确认最终数值 |
| 体力消耗统一为 15（item_id=3） | 待确认 | 部分高难度是否差异化体力消耗待定 |
| OnceCoinDrop 仅首通有效 | 当前规则 | 已确认 |
| 死后金币惩罚按 DeathCoinDrop 绝对值扣减 | 待确认 | 是否需要死亡保护（最低保留比例）待定 |
