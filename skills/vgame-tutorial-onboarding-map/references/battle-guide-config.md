# Battle Guide Config

## 配置表: BattleGuide.xlsx

路径: `${VGAME_ROOT}\Config\GameConfig\Datas\Guide\BattleGuide.xlsx`

### Schema

| 列 | 字段 | 类型 | 说明 |
|---|---|---|---|
| B | Id | int | 引导ID |
| C | Type | BattleGuideEnum | 动作类型 |
| D | IsValid | bool | 是否启用 |
| E | SkillPos | int | 技能槽位(UseSkill时) |
| F | NeedPause | bool | 是否暂停游戏 |
| G | Text | lotext? | 提示文本 |
| H | IntroductionId | int | 关联Introduction图片序列 |
| I | CircleScale | float? | 高亮圈大小 |
| J | CirclePos | int? | 手指位置(0=上,1=下,2=隐藏) |
| K | Text2 | lotext? | 备选文本 |

### 16种引导类型 (BattleGuideEnum)

| 枚举 | 值 | 说明 |
|---|---|---|
| HideUI | 0 | 隐藏战斗UI |
| ShowUI | 1 | 显示战斗UI |
| ChooseOperationType | 2 | 选择操作模式 |
| JumpUp | 3 | 教向上跳 |
| JumpDown | 4 | 教向下跳 |
| UseSkill | 5 | 教使用技能(指定槽位) |
| ShowPic | 6 | 展示图片 |
| ShowTips | 7 | 显示文字提示 |
| DoubleJump | 8 | 教二段跳 |
| HideSkill | 9 | 隐藏技能按钮 |
| JumpDown2 | 10 | 另一种下跳教学 |
| Pause | 11 | 暂停等待 |
| ForbidOperation | 12 | 禁止玩家操作 |
| AllowOperation | 13 | 恢复玩家操作 |
| UseLevelSkill | 14 | 教使用关卡技能 |
| HideLevelSkill | 15 | 隐藏关卡技能 |

### 触发方式

在 Unity 关卡编辑器中摆放 `ZoneShowGuide` 触发器：
- 指定触发器的 X 坐标位置
- 指定 guideId（对应 BattleGuide.xlsx 的 Id）
- 玩家角色到达该 X 坐标时自动触发

### 执行流程

```
ZoneShowGuide 触发
  → GuideMgr.RegisterGuide(guideId)
    → 查表获取配置
    → if NeedPause: 暂停游戏时间
    → VMsg_ShowGuide → UI显示提示
    → 等待玩家操作（或自动超时）
  → CompleteGuide()
    → VMsg_HideGuide → UI隐藏
    → if NeedPause: 恢复游戏时间
    → 记录到 HistoricalCompletedGuideIds（跨战斗持久化）
```

### 完成判定

| Type | 完成条件 |
|---|---|
| JumpUp/JumpDown/DoubleJump | 玩家执行了对应跳跃操作 |
| UseSkill/UseLevelSkill | 玩家使用了指定技能 |
| ShowPic/ShowTips | 玩家点击关闭 |
| Pause | 定时结束 |
| ChooseOperationType | 玩家选择完成 |

### Introduction.xlsx（图片序列）

| 列 | 字段 | 说明 |
|---|---|---|
| B | Id | 序列ID（BattleGuide.IntroductionId 引用） |
| C | ImageRes | 图片资源路径列表(;分隔) |
| D | Desc | 每页描述文本(;分隔) |
| F | IsValid | 是否启用 |

当前仅3条（1001-1003），用于多页图文教学。

### 设计注意事项

| 注意 | 说明 |
|---|---|
| 触发位置 | ZoneShowGuide 的 X 坐标要在玩家能到达的地方 |
| 不要重复触发 | HistoricalCompletedGuideIds 防止重复，但要确保ID唯一 |
| 暂停时机 | NeedPause=true 时要确保不在高空/掉落中暂停 |
| 技能槽位 | UseSkill 的 SkillPos 必须对应当前已解锁的槽位 |
| 顺序 | 多个 ZoneShowGuide 按X坐标排列，确保不会跳过 |
