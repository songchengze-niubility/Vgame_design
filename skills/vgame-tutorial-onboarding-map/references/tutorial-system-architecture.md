# Tutorial System Architecture

## 双系统总览

```
┌─────────────────────────────────────────────┐
│  战斗内引导 (BattleGuide) — C# Lockstep     │
│  教操作: 跳跃/下蹲/技能/必杀                  │
│  触发: ZoneShowGuide 区域触发器               │
│  配置: BattleGuide.xlsx → Luban              │
│  管理: GuideMgr.cs                           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  战斗外引导 (NewbieGuide) — Lua UI层         │
│  教功能: 点击按钮/拖拽/功能介绍               │
│  触发: ConditionSystem 解锁事件              │
│  配置: GuideEditor → JSON → Lua auto文件     │
│  管理: NewbieGuideSystem.lua (2092行)        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  功能开放 (SystemOpen) — 进度门控            │
│  控制: 功能入口可见性/可用性                  │
│  触发: Unlock条件满足                        │
│  配置: SystemOpen.xlsx + Unlock.xlsx         │
└─────────────────────────────────────────────┘
```

## 三者关系

```
玩家推进主线/升级
  → Unlock 条件满足
    → SystemOpen 开放功能入口 (UI 按钮出现)
      → NewbieGuideSystem 检测到新功能开放
        → 触发引导序列 (强制打开UI → 遮罩高亮 → 引导操作)

玩家进入关卡
  → 跑到 ZoneShowGuide 位置
    → GuideMgr 注册并执行战斗引导
      → 暂停/提示 → 玩家操作 → 恢复
```

## 核心文件清单

### 战斗内引导

| 文件 | 路径 | 职责 |
|---|---|---|
| GuideMgr.cs | `VGame.GameLogic\Runtime\Combat\GuideMgr.cs` | 战斗引导管理器 |
| ZoneShowGuide.cs | `VGame.Lockstep\Runtime\Logic\TriggerData\ZoneShowGuide.cs` | 区域触发器 |
| BattleGuideModel.cs | `VGame.Common\Runtime\Config\Generated\BattleGuideModel.cs` | 数据模型(自动生成) |
| BattleGuide.xlsx | `Datas\Guide\BattleGuide.xlsx` | 配置表(32条) |
| Introduction.xlsx | `Datas\Guide\Introduction.xlsx` | 图片序列(3条) |

### 战斗外引导

| 文件 | 路径 | 职责 |
|---|---|---|
| NewbieGuideSystem.lua | `Lua\Logic\PlayerData\Systems\Guide\NewbieGuideSystem.lua` | 主管理器 |
| GuideConst.lua | 同目录 | 常量/枚举 |
| GuideSequenceData_Auto.lua | 同目录 | 序列配置(自动导出) |
| GuideStepData_Auto.lua | 同目录 | 步骤配置(自动导出) |
| UIGuideView.lua | `Lua\UI\Guide\UIGuideView.lua` | 引导UI(遮罩/气泡/箭头) |
| GuideEditorWindow.cs | `VGame.GameLogic\Editor\Guide\GuideEditorWindow.cs` | 编辑器窗口 |
| GuideEditorData.json | 同目录 | 编辑器持久化JSON |
| GuideTransparentMaskController.cs | `VGame.GameLogic\Runtime\UI\Guide\` | 透明遮罩(高亮穿透) |
| GuideTargetRelay.cs | 同目录 | 点击中继(检测目标点击) |
| GuideDragRelay.cs | 同目录 | 拖拽中继(验证拖拽目标) |

### 功能开放

| 文件 | 路径 | 职责 |
|---|---|---|
| SystemOpen.xlsx | `Datas\system_open\SystemOpen.xlsx` | 92个系统开放配置 |
| Unlock.xlsx | `Datas\unlock\Unlock.xlsx` | 682个解锁条件 |
| SystemGuideTask.xlsx | `Datas\task\SystemGuideTask.xlsx` | 系统引导任务(3条) |

### 策划规划

| 文件 | 路径 | 职责 |
|---|---|---|
| Vgame新手引导以及开启节奏.xlsx | `D:\数值文档\数值文档\` | 开启节奏/新手流程/主角等级/养成预估 |

## 新手体验时间线

| 阶段 | 时长 | 内容 | 系统 |
|---|---|---|---|
| 0-3min | 开场CG+第一关 | 剧情+基础跑酷 | Plot + BattleGuide |
| 3-10min | 序章1-5关 | 跳跃/下蹲/技能/必杀教学 | BattleGuide |
| 10-15min | 首次UI引导 | 角色/装备/升级/抽卡 | NewbieGuide |
| 15-21min | Ch1前4关 | 强制引导结束 | Mixed |
| 21min+ | 自由推进 | 按解锁节奏弱引导 | SystemOpen + 软引导 |

## 引导类型分级

| 级别 | 特点 | 适用场景 |
|---|---|---|
| 强制引导 | 不可跳过、遮罩锁定、必须按步操作 | 核心操作教学(前21min) |
| 弱引导 | 可跳过、只提示不强制 | 新功能开放时 |
| 提示引导 | 仅UI标记/红点 | 日常功能提醒 |
| 图片引导 | Introduction表展示多页图 | 复杂机制说明 |
