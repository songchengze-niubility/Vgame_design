# 通行证系统 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 通行证系统 (Battle Pass) |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | HIGH |
| 关联 Proposal | — |

## 背景与目标
### 背景
通行证系统是游戏长线付费与活跃的双核心驱动之一，采用免费线 + 付费线双轨制设计。玩家通过完成日常/周常任务获取通行证经验（BP EXP），升级解锁各等级奖励。付费线通过 BasicEditionPayProduct 购买后解锁，提供 PassAdditionReward 额外奖励。关键里程碑等级标注为 IsSignificanceLevel。

### 目标
- 免费线 + 付费线双轨奖励
- 等级经验需求表 BattlePassLevel.xlsx 驱动升级
- 每级奖励通过 DropId 引用（CommonReward + PassAdditionReward）
- 关键等级 IsSignificanceLevel 高亮展示
- 购买通行证即时解锁已达成等级的全部付费奖励

### 非目标
- 不设计通行证等级直升/购买等级
- 不处理多期通行证并行
- 不设计通行证经验加速道具

## 核心规则
### R-01: 通行证经验获取与等级提升
- **触发条件**：玩家完成任务/活动产出 BP EXP
- **前置限制**：通行证活动在开放时间内（OpenTime 内）
- **操作流程**：接收 EXP 事件 → 累加当前等级内 EXP → 对比 BattlePassLevel.xlsx 中当前等级 UpgradeCostExp → 达标则升级（多级连升）
- **状态变化**：BP 等级 +1（或多级）；当前等级 EXP 重置或溢出结转
- **资源变化**：无（升级不直接给资源，需领取奖励）
- **UI 反馈**：BP 进度条推进 → 升级动画 → 可领取奖励红点提示
- **异常边界**：EXP 一次性大量涌入（跨期任务批量结算）需支持多级连升
- **落地点**：BattlePass.xlsx, BattlePassLevel.xlsx

### R-02: 免费线奖励领取
- **触发条件**：玩家在通行证界面点击免费线奖励格
- **前置限制**：BP 等级达到该奖励格所需等级；该格未领取；奖励格在 CommonReward 列有配置
- **操作流程**：读取 BattlePassReward.xlsx 对应等级 CommonReward（DropId 如 40000001）→ 发放 Drop → 标记已领取
- **状态变化**：该等级免费奖励标记已领
- **资源变化**：+DropId 对应奖励内容
- **UI 反馈**：奖励格打勾 → 奖励飞入背包
- **异常边界**：DropId 配置无效 → 跳过发放并告警
- **落地点**：BattlePassReward.xlsx

### R-03: 付费线奖励领取
- **触发条件**：玩家在通行证界面点击付费线奖励格
- **前置限制**：已购买通行证（付费线已解锁）；BP 等级达标；该格未领取
- **操作流程**：读取 BattlePassReward.xlsx 对应等级 PassAdditionReward（DropId 如 40001001）→ 发放 Drop → 标记已领取
- **状态变化**：该等级付费奖励标记已领
- **资源变化**：+DropId 对应奖励内容
- **UI 反馈**：奖励格打勾 → 奖励飞入背包
- **异常边界**：未购买时点击付费线格提示"购买通行证解锁"
- **落地点**：BattlePassReward.xlsx

### R-04: 购买通行证解锁付费线
- **触发条件**：玩家点击"购买通行证"按钮
- **前置限制**：未购买当前期通行证；持有对应 PayProduct；通行证在开放时间内
- **操作流程**：拉起支付 → 支付成功 → 标记通行证已购买 → 遍历玩家已达成等级，自动发放全部未领取的 PassAdditionReward
- **状态变化**：通行证购买标记置为 true
- **资源变化**：-RMB（支付）；+当前等级及以下全部付费线奖励
- **UI 反馈**：付费线解锁动画 → 批量奖励飞入 → 界面切换为双轨展示
- **异常边界**：支付回调失败 → 不标记购买也不发奖；断线补发需幂等
- **落地点**：BattlePass.xlsx (BasicEditionPayProduct)

### R-05: 关键等级高亮
- **触发条件**：通行证界面渲染时
- **前置限制**：BattlePassReward.xlsx 中 IsSignificanceLevel = true
- **操作流程**：读取各等级 IsSignificanceLevel 标记 → 渲染时对标记为 true 的等级使用高亮美术资源
- **状态变化**：无
- **资源变化**：无
- **UI 反馈**：关键等级奖励格外框发光 / 图标更大 / 专有特效
- **异常边界**：关键等级数量过多导致视觉疲劳 → 策划控制数量（通常 5-8 个）
- **落地点**：BattlePassReward.xlsx

### R-06: 奖励预览
- **触发条件**：通行证界面打开（未购买前）
- **前置限制**：无
- **操作流程**：读取 BattlePass.xlsx 中 BasicEditionReward（付费线总览物品列表）+ AdvancedEditionReward → 在预览区域展示可获得的全部奖励摘要
- **状态变化**：无
- **资源变化**：无
- **UI 反馈**：预览面板展示"购买后可获得以下全部奖励" + 物品图标列表
- **异常边界**：RewardItemPreview 为空 → 隐藏预览区
- **落地点**：BattlePass.xlsx

### R-07: 通行证赛季结束
- **触发条件**：当前时间超过 BattlePass.xlsx 中 OpenTime 结束时间
- **前置限制**：无
- **操作流程**：关闭经验获取入口 → 保留奖励领取窗口期（通常 +3~7 天）→ 窗口期结束后关闭通行证 → 未领取奖励通过邮件补发
- **状态变化**：通行证状态变为"已结束"
- **资源变化**：补发未领取奖励
- **UI 反馈**：通行证入口变灰/标注"已结束" → 邮件通知补发
- **异常边界**：补发邮件达到上限 → 分批发送
- **落地点**：BattlePass.xlsx

## 技术方案
### 架构影响
- BP 经验单独一条属性存储，与玩家等级经验分轨
- BP 购买状态 + 各等级领取状态存储于玩家存档
- 赛季结束逻辑需定时任务扫描，触发补发

### 数据变更
| 表 | 变更类型 | 说明 |
|----|----------|------|
| BattlePass.xlsx | 配置 | 开放时间、奖励预览、付费产品 ID、双版奖励总览 |
| BattlePassLevel.xlsx | 配置 | 每级升级所需 EXP (UpgradeCostExp) |
| BattlePassReward.xlsx | 配置 | 每级 CommonReward(免费) + PassAdditionReward(付费) + IsSignificanceLevel |

### 接口变更
- `BPGetInfo`：出参 CurrentLevel, CurrentExp, IsPurchased, ClaimedFree[], ClaimedPaid[]
- `BPClaimReward`：入参 Level + Track(1=Free/2=Paid)；出参 RewardItems[]
- `BPPurchase`：入参 PayProductId；出参 AllPaidRewards[]
- `BPAddExp`：事件由任务/活动模块推送，非玩家主动调用

## 风险评估
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 付费线奖励价值不足导致购买率低 | 中 | 高 | 结合数值规划确保付费线性价比 5x 以上 |
| 赛季结束补发遗漏 | 低 | 高 | 赛季结算时全量扫描 + 补发日志 |
| EXP 结算溢出/跨期异常 | 中 | 中 | 赛季边界时间严格校验 |
| 购买后批量发奖性能问题 | 低 | 中 | 分批发放 + 进度提示 |
| IsSignificanceLevel 配置与实际奖励不匹配 | 低 | 低 | 配置审核流程 |

## 工作假设
| 假设 | 状态 | 澄清结论 |
|------|------|----------|
| 通行证首期时长 30 天 | 待确认 | — |
| 付费线奖励领取窗口期 7 天 | 待确认 | — |
| 不设计通行证等级购买 | 已确认 | — |
