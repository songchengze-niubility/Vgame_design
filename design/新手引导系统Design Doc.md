# 新手引导系统 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 新手引导系统（Tutorial / Onboarding） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | MEDIUM |
| 关联 Proposal | — |

## 背景与目标
### 背景
Vgame 采用双系统引导新玩家：战斗内由 BattleGuide（C# 层，锁步机制）驱动关卡内的引导操作；战斗外由 NewbieGuide（Lua 层，UI 引导）通过 GuideEditorWindow 编辑器生成 JSON → GuideSequenceData_Auto.lua + GuideStepData_Auto.lua，控制 UI 界面的遮罩、箭头、气泡和手指动画引导玩家操作。此外 SystemOpen.xlsx 通过 Unlock.xlsx（682 条件）对 92 个系统做渐进式解锁，形成软引导层。

### 目标
- 定义战斗内 BattleGuide 的 16 种引导类型及其触发流程
- 规范 NewbieGuide 的编辑管线与运行时引导序列
- 明确 SystemOpen 渐进式解锁与 Unlock 条件体系
- 梳理新玩家 0-30min 的引导时间线

### 非目标
- 引导具体文案内容（属策划/本地化范畴）
- 引导埋点数据分析
- 服务端引导状态同步细节

## 核心规则

### R-01: BattleGuide 战斗内引导
- **触发条件**：关卡中角色进入 `ZoneShowGuide` 触发区域时
- **前置限制**：BattleGuide.xlsx 已配置该引导的 GuideType 和参数
- **操作流程**：Zone 触发器激活 → 读取 BattleGuide.xlsx 配置 → 根据 GuideType 执行对应行为：
  - `Jump`：指示玩家跳跃
  - `UseSkill`：指示使用指定技能
  - `ShowPic`：显示引导图片
  - `Pause`：暂停战斗等待玩家操作
  - `ForbidOperation`：禁止除引导目标外的所有操作
  - ……（共 16 种）
  - 引导完成后移除 Zone 触发区域（或标记已完成）
- **状态变化**：战斗锁定（ForbidOperation）→ 引导中 → 引导完成/跳过 → 恢复操作
- **资源变化**：加载引导图片/箭头/光圈预制体
- **UI 反馈**：高亮目标按钮、显示操作提示文字、引导手指动画
- **异常边界**：GuideType 未知 → 跳过引导并打 warning；引导资源缺失 → 使用默认提示文字替代图片
- **落地点**：`BattleGuide.xlsx` → `BattleGuideManager.TriggerGuide(guideId)` → C# 锁步执行

### R-02: NewbieGuide 编辑管线
- **触发条件**：策划打开 GuideEditorWindow（Unity 编辑器）编辑 UI 引导
- **前置限制**：编辑器已安装并正确加载 GuideEditorWindow 模块
- **操作流程**：GuideEditorWindow → 策划配置 Sequence（UnlockId 前置解锁条件 → StartType 启动类型）→ 策划配置 Steps（ClickTarget / Drag / Timer 等类型）→ 设置遮罩类型、气泡、箭头、手指动画、FailureLevel（0-3）→ 保存 → 生成 JSON → 自动生成 `GuideSequenceData_Auto.lua` + `GuideStepData_Auto.lua`
- **状态变化**：编辑 → 保存 → 生成 Lua 代码
- **资源变化**：JSON 中间文件 + 两个 .lua 脚本文件生成/更新
- **UI 反馈**：编辑器内实时预览引导遮罩和步骤流程
- **异常边界**：UnlockId 不存在于 Unlock.xlsx 时警告但允许保存；Step 列表为空时阻止保存
- **落地点**：编辑器导出 → `GuideSequenceData_Auto.lua` + `GuideStepData_Auto.lua`

### R-03: NewbieGuide 运行时执行（StartType 与 Steps）
- **触发条件**：UnlockId 条件达成 → 根据 StartType 启动引导
- **前置限制**：GuideSequenceData_Auto.lua 已生成，UnlockId 条件已满足
- **操作流程**：
  1. `StartType = ForceJumpUI`：强制跳转到目标 UI 界面 → 开始引导
  2. `StartType = WaitUIOpen`：等待玩家自然打开目标 UI → 开始引导
  3. 进入 Step 序列：依次执行 ClickTarget（点击指定区域）/ Drag（拖拽）/ Timer（等待）
  4. 每个 Step 显示遮罩（Mask）、气泡提示（Bubble）、箭头指向（Arrow）、手指动画（Finger）
  5. FailureLevel 0-3：0=不可失败，1=允许取消，2=允许跳步，3=允许跳过整个引导
- **状态变化**：未触发 → 等待条件 → 引导中 → Step1 → Step2 → ... → 引导完成/失败 → 服务端同步完成状态
- **资源变化**：Lua 层创建引导 UI 对象
- **UI 反馈**：非目标区域半透明遮罩、目标区域高亮、气泡文字、箭头动画、手指点击动画
- **异常边界**：ForceJumpUI 目标界面加载失败 → 降级为 WaitUIOpen；玩家中途强退 → 服务端记录未完成，下次登录重新触发
- **落地点**：`GuideSequenceData_Auto.lua` → `NewbieGuideManager.StartSequence(sequenceId)`

### R-04: SystemOpen 渐进式系统解锁
- **触发条件**：玩家满足 Unlock 条件时触发系统开放检查
- **前置限制**：SystemOpen.xlsx 和 Unlock.xlsx 已配置
- **操作流程**：
  1. SystemOpen.xlsx 定义 92 个系统（背包、技能、副本、活动等）→ 每个系统绑定 UnlockId
  2. Unlock.xlsx（682 条条件）定义解锁条件类型：`UnLock_UUT_Level`（角色等级）、`UnLock_UUT_player_Grade`（玩家段位）等
  3. 玩家状态变化（升级/通关/段位提升）→ 遍历 Unlock 条件 → 满足则开放对应系统
- **状态变化**：系统 Locked → Unlocked
- **资源变化**：解锁后相关 UI 入口可见、功能激活
- **UI 反馈**：加锁图标变为正常图标；首次解锁弹出系统介绍弹窗
- **异常边界**：Unlock 条件引用不存在的条件类型 → 永久锁定（需修复配置）；升级后多个系统同时解锁 → 按优先级依次弹出介绍弹窗
- **落地点**：`SystemOpen.xlsx` + `Unlock.xlsx` → `SystemOpenManager.CheckUnlock()` → Lua UI 层响应

### R-05: 新玩家时间线
- **触发条件**：新玩家首次进入游戏
- **前置限制**：服务器标记为新手账号（无历史进度）
- **操作流程**：
  - **0-3min**：开场剧情动画 + 强制第一场战斗（教学模式）
  - **3-10min**：强制引导关卡（使用 BattleGuide ZoneShowGuide，不可跳过）
  - **10-21min**：首批 UI 引导触发（NewbieGuide ForceJumpUI → 背包/技能/装备界面）
  - **21min+**：软引导（SystemOpen 逐步解锁系统 → WaitUIOpen 引导仅在玩家自然打开时触发）
- **状态变化**：各阶段引导完成后更新服务器进度
- **资源变化**：按阶段加载对应的引导资源和教学关卡
- **UI 反馈**：0-10min 高强制感引导（遮罩覆盖大、不可跳过），10min+ 逐渐减弱引导感
- **异常边界**：强退/闪退后重进，从当前阶段继续（不回到 0min）；跳过式引导允许加速（提前满足 Unlock 条件直接解锁）
- **落地点**：`NewPlayerTimelineController` 管理阶段推进，服务端 `TutorialProgress` 数据持久化

### R-06: 引导完成度标记与服务器同步
- **触发条件**：每个引导步骤/序列完成时
- **前置限制**：网络连接正常
- **操作流程**：引导完成 → 本地标记完成 → 发送完成协议到服务器 → 服务器更新引导进度 → 回写本地确认
- **状态变化**：InProgress → Completed（服务器/本地双向同步）
- **资源变化**：无
- **UI 反馈**：完成引导后引导 UI 消失
- **异常边界**：网络断开时本地暂存完成标记，重连后批量上报；服务器返回重复完成 → 忽略（幂等）
- **落地点**：`GuideProgressManager.MarkCompleted(guideId)` → `NetMsg.RequestCompleteGuide(guideId)`

### R-07: FailureLevel 容错策略
- **触发条件**：引导步骤中玩家进行非预期操作时
- **前置限制**：Step 已定义 FailureLevel（0-3）
- **操作流程**：
  - `FailureLevel 0`：完全不可失败。玩家非预期操作被拦截，遮罩阻挡所有非目标点击
  - `FailureLevel 1`：允许取消。玩家点击引导遮罩外区域即取消引导，当前步骤重置
  - `FailureLevel 2`：允许跳步。玩家可跳过当前步骤进入下一步
  - `FailureLevel 3`：允许跳过整个引导。玩家可完全关闭该引导序列
- **状态变化**：按级别分别进入 拦截 / 取消-待重试 / 跳步 / 跳过整序列
- **资源变化**：无
- **UI 反馈**：Level 3 显示"跳过"按钮；Level 0 无任何退出方式
- **异常边界**：Level 0 引导卡住（目标 UI 不存在）→ 30s 超时自动降级为 Level 3
- **落地点**：`GuideStep.FailureLevel` → `GuideFailHandler.HandleFailure(level)`
