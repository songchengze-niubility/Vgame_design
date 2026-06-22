# SystemOpen & Unlock Chain

## 功能开放系统 (SystemOpen)

路径: `D:\Vgame\Config\GameConfig\Datas\system_open\SystemOpen.xlsx`

### Schema (92个系统)

| 列 | 字段 | 说明 |
|---|---|---|
| B | Id | 系统ID |
| C | Name | 系统显示名 |
| D | ParentId | 父系统（子系统归属） |
| E | CloseSys | 是否关闭（版本控制开关） |
| F | SortId | 排序 |
| G | HideInSys | 隐藏开放通知 |
| H | Icon | 图标资源 |
| I | Desc | 描述文本 |
| K | UnlockId | 关联 Unlock 条件ID |
| L | EntranceResident | 入口按钮是否常驻 |
| M | NoPopUp | 不弹开放提示 |
| N | JumpId | 开放后UI跳转目标 |
| O | UIViewName | View脚本名 |
| P | JumpParams | 跳转额外参数 |
| Q | ForceJump | 强制跳转 |
| R | IsValid | 是否有效 |

### 系统分类

| ID 范围 | 类别 | 示例 |
|---|---|---|
| 1-45 | 核心系统 | 邮件、好友、聊天、背包、角色、招募、商店、公会 |
| 201-326 | 挑战/副本子系统 | 爬塔、深渊、肉鸽、Boss、资源副本 |
| 401+ | 活动系统 | 开服挑战 |
| 99901+ | 纯跳转展示 | 不是真实系统开放 |

### CloseSys 用法

`CloseSys=true` 表示该系统当前版本**强制关闭**，无论 Unlock 条件是否满足都不开放。用于：
- 废弃功能（肉鸽 → CloseSys=true）
- 版本控制（某功能下个版本才上）
- 灰度控制（配合服务器开关）

---

## 解锁条件系统 (Unlock)

路径: `D:\Vgame\Config\GameConfig\Datas\unlock\Unlock.xlsx`

### Schema (682条)

| 列 | 字段 | 说明 |
|---|---|---|
| B | Id | 条件ID |
| C | UnLockDesc | 描述 |
| D | UnLockType | 条件类型枚举 |
| E | UnLockParams | 参数列表(;分隔) |

### 解锁类型

| 枚举 | 参数 | 说明 |
|---|---|---|
| `UnLock_UUT_Level` | 关卡ID | 通关指定关卡 |
| `UnLock_UUT_player_Grade` | 等级数 | 达到玩家等级 |
| `UnLock_UUT_Climb_Tower_Max_Layer` | 层数 | 爬塔历史最高层 |
| `UnLock_UUT_Climb_Tower_Current_Layer` | 层数 | 当赛季爬塔层数 |
| `UnLock_UUT_Character_Star` | 角色ID | 拥有指定角色 |
| `UnLock_UUT_Task_InProgress` | 任务ID | 任务进行中 |
| `UnLock_UUT_Task_Complete` | 任务ID | 任务已完成 |

### 关键开放节点一览

| 系统 | UnlockId | 条件 | 估计时间点 |
|---|---|---|---|
| 背包/角色 | 4004/4005 | 等级1 | 立即 |
| 主线 | 4008 | 等级1 | 立即 |
| 任务/商店/招募 | 4006/4012/4017 | 通过1-1 | ~3min |
| 邮件 | 4001 | 通过0-4 | ~8min |
| 挑战(资源本) | 4009 | 通过1-6 | ~20min |
| 好友/聊天 | 4002/4003 | 通过1-10 | ~30min |
| 竞技场 | 4112 | 等级20 | ~Day 3 |
| 爬塔 | 4101 | 等级25 | ~Day 5 |
| 专武 | 4016 | 等级27 | ~Day 6 |
| 首领挑战 | 4104 | 等级32 | ~Day 10 |
| 旅券副本 | — | 等级34 | ~Day 12 |
| 大秘境 | 4102 | 等级37 | ~Day 14 |
| 映射装备 | 4014 | 通过2-15 | ~Day 10 |

### 解锁链路

```
SystemOpen.UnlockId → Unlock.Id → Unlock.UnLockType + UnLockParams
                                         ↓
              UnLock_UUT_Level → 需要通关 level.LevelId (如 100215 = Ch2-15)
              UnLock_UUT_player_Grade → 需要玩家等级达标
```

### 与引导系统的关系

```
Unlock 条件满足
  → ConditionSystem 广播 OnSystemUnlock 事件
    → SystemOpen 标记系统可用 (UI入口显示)
    → NewbieGuideSystem 检查是否有 Sequence.UnlockId 匹配
      → 有: 入队等待执行引导
      → 无: 仅开放入口，不引导
```

### 与 NewbieGuide Sequence 的对应

| Sequence.UnlockId | 对应解锁 | 引导内容 |
|---|---|---|
| 与 SystemOpen.UnlockId 相同 | 功能首次开放时 | 教玩家如何使用该功能 |
| Sequence.ExpireId | 更高进度条件 | 如果玩家已经自己探索过，不再强制引导 |

---

## 新增系统开放的流程

| 步骤 | 操作 | 表 |
|---|---|---|
| 1 | 确定开放条件（通关/等级） | 设计决策 |
| 2 | 在 Unlock.xlsx 新增条件行 | Unlock |
| 3 | 在 SystemOpen.xlsx 新增系统行，填 UnlockId | SystemOpen |
| 4 | 如需引导，在 GuideEditor 创建 Sequence | GuideEditorData.json |
| 5 | 设置 Sequence.UnlockId = 新 Unlock ID | GuideEditor |
| 6 | 设计引导步骤 (TargetUI + TargetNode + MaskType) | GuideEditor |
| 7 | 导出 Lua auto 文件 | GuideEditor 导出按钮 |
| 8 | 测试：满足条件后引导是否正确触发 | 运行时验证 |

---

## 常见问题

| 问题 | 排查 |
|---|---|
| 功能不开放 | CloseSys=true? UnlockId条件未满足? IsValid=false? |
| 引导不触发 | Sequence.UnlockId 和 SystemOpen.UnlockId 对应? ExpireId 已满足? |
| 引导卡住 | TargetNode 不存在? TargetUI 未打开? SubTargetUI 加载延迟? |
| 重复引导 | 服务器同步丢失? IsSequenceEndNode 未标记? |
| 引导和其他弹窗冲突 | ForceJumpUI 时有其他面板挡住? |
