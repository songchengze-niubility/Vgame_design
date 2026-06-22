# 签到系统 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 签到系统 (Sign-in) |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | MEDIUM |
| 关联 Proposal | — |

## 背景与目标
### 背景
签到系统是游戏上线初期留存与资源投放的核心管道，包含每日签到、七日签到、月度累计、长期旅行累计四套机制。通过首周密集投放 150 钻石 + 物品 + 票券为新玩家建立正向体验。

### 目标
- 每日签到月循环，支持灵活配置 rewardItems（PropType 数组）
- 七日签到配置 OpenDay + ItemReward，与 ActivityId 绑定
- 月度累计：AccumulateDay 阈值触发奖励
- 长期累计 TravelAccumulate 覆盖大天数区间
- 首 7 天总投放：150 钻石 + 物品 + 票券

### 非目标
- 不处理签到补签功能（首版不做）
- 不设计 VIP 双倍签到
- 不与限时活动签到合并

## 核心规则
### R-01: 每日签到
- **触发条件**：玩家每日首次打开签到面板（或自动弹窗）
- **前置限制**：当日尚未签到
- **操作流程**：读取 DailySign.xlsx 当月循环签到表 → 匹配玩家当月已签到天数 → 发放对应 rewardItems
- **状态变化**：签到标记为已签；当月连续签到天数 +1
- **资源变化**：+rewardItems（PropType 数组中的物品）
- **UI 反馈**：签到日历上当天格高亮 → 奖励飞入 → 已签到日期标注 ✓
- **异常边界**：当月天数超过签到表条目 → 循环复用；重复签到拒绝
- **落地点**：DailySign.xlsx

### R-02: 七日签到
- **触发条件**：玩家首次创建角色后第 N 天登录（N = OpenDay）
- **前置限制**：ActivityId 对应的七日签到活动在有效期内
- **操作流程**：读取 SevenDaySign.xlsx 中 ActivityId + OpenDay 对应的 ItemReward → 自动发放或弹窗领取
- **状态变化**：该日签到标记完成
- **资源变化**：+ItemReward 配置物品
- **UI 反馈**：七日签到面板展示 7 格 → 已到达天数亮起可领 → 领取后打勾
- **异常边界**：ActivityId 过期 → 对应奖励不可领但已领保留；OpenDay 跳跃（玩家跨天未登录）→ 逐格补发或仅当日可领（按配置）
- **落地点**：SevenDaySign.xlsx

### R-03: 月度累计签到奖励
- **触发条件**：当月累计签到天数达到 MonthlyAccumulate.xlsx 中 AccumulateDay 阈值
- **前置限制**：无
- **操作流程**：每日签到后遍历月度累计表 → 命中阈值且未领取 → 发放 rewardItems
- **状态变化**：该累计档位标记已领取
- **资源变化**：+rewardItems 配置物品
- **UI 反馈**：月度累计进度条推进 → 达到阈值节点可领 → 领取后节点点亮
- **异常边界**：跨月时重置累计天数与新月份阈值
- **落地点**：MonthlyAccumulate.xlsx

### R-04: 长期旅行累计签到
- **触发条件**：总签到天数（跨月累计）达到 TravelAccumulate.xlsx 中配置的天数阈值
- **前置限制**：无
- **操作流程**：每日签到后遍历长期累计表 → 命中阈值 → 发放对应 rewardItems
- **状态变化**：该长期累计档位标记已领取
- **资源变化**：+rewardItems
- **UI 反馈**：旅行路线图推进 → 到达节点可领
- **异常边界**：长期累计天数上限 > 策划实际能配置的天数 → 最后一行后不再触发
- **落地点**：TravelAccumulate.xlsx

### R-05: 首周总计投放校验
- **触发条件**：运营/数值规划设计周期检查（非运行时）
- **前置限制**：无
- **操作流程**：汇总 DailySign(前7) + SevenDaySign(全7) + MonthlyAccumulate(首月累7) 的首周 rewardItems → 计算钻石总量 + 限时角色票 + 限时专武票 → 核对 ≥ 70 角色票 / ≥ 20 专武票 / ≥ 150 钻石
- **状态变化**：仅设计态校验
- **资源变化**：无
- **UI 反馈**：校验脚本输出差距报告
- **异常边界**：配置不达标 → 调整对应奖励行
- **落地点**：全部签到配置表

## 技术方案
### 架构影响
- 签到状态（每日是否已签）存储于玩家存档，服务端每日 5:00 刷新签到状态
- 七日签到与角色创建时间绑定, 用 `(now - create_time).days + 1` 计算 OpenDay
- 月度累计与长期累计独立计数器

### 数据变更
| 表 | 变更类型 | 说明 |
|----|----------|------|
| DailySign.xlsx | 配置 | 每月签到循环 rewardItems（PropType 数组） |
| SevenDaySign.xlsx | 配置 | 7 日签到 ActivityId + OpenDay + ItemReward |
| MonthlyAccumulate.xlsx | 配置 | 月度累计 AccumulateDay + rewardItems |
| TravelAccumulate.xlsx | 配置 | 长期累计天数 + rewardItems |

### 接口变更
- `SignInDaily`：入参 DayIndex；出参 RewardItems[]
- `SignInSevenDay`：入参 ActivityId + OpenDay；出参 RewardItems[]
- `MonthlyAccumulateClaim`：入参 ThresholdDay；出参 RewardItems[]
- `TravelAccumulateClaim`：入参 ThresholdDay；出参 RewardItems[]
- `GetSignInStatus`：出参 DailySigned[], SevenDaySigned[], MonthlyClaimed[], TravelClaimed[]

## 风险评估
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 跨月签到天数计算偏移 | 低 | 中 | 以服务端 UTC+0 统一计时 |
| 七日签到期后玩家未领无法补领 | 中 | 中 | 明确产品规则：活动过期不补 |
| 长期签到天数极大时性能问题 | 低 | 低 | 已领取阈值标记，不每次全表遍历 |
| rewardItems 配置错误（物品 ID 不存在） | 低 | 中 | 配置校验脚本 |
| 首周投放量不达标影响留存 | 中 | 中 | 上线前专项核查首周总产出 |

## 工作假设
| 假设 | 状态 | 澄清结论 |
|------|------|----------|
| 签到重置时间统一为每日 5:00 | 已确认 | — |
| 七日签到为基础活动，永久开放 | 待确认 | — |
| 补签功能首版不做 | 已确认 | — |
