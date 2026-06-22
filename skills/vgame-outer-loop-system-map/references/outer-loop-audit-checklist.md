# 外循环审查清单

## 1. 明确系统

- 确认用户说的是抽卡、商店、任务、签到、战令、活动、邮件、月卡、扫荡，还是泛外循环。
- 确认是高层关系分析、只读配置分析，还是要落地改表。

## 2. 判断职责

标记系统职责：

- 留存
- 资源补充
- box 扩展
- 商业化支撑
- 社交留存
- 运营补偿
- 活动刺激

## 3. 定位配置

- 用 `outer-loop-config-map.md` 找候选源表。
- 涉及 schema、逻辑表、导出或新表时转 `vgame-config-schema`。
- 涉及 Unlock/SystemOpen/LevelType/扫荡时转 `vgame-level-progression-map`。

## 4. 区分真实字段与展示字段

- 展示字段：`RewardItemPreview`, `PassRewardPreview`, `FirstRewardShow`, `DailyRewardShow`, `TotalReward`, UI 预览类字段。
- 真实奖励：直接 `PropType` 字段或 DropId/RewardId 引用。
- DropId 内容必须用 `vgame-reward-drop-sync` 展开。

## 5. 判断周期和次数

- 一次性：首通、主线、章节、邮件、玩家等级奖励。
- 日常：每日任务、每日活跃、签到、月卡每日、资源副本。
- 周常：周任务、周活跃、周奖励。
- 赛季：战令、竞技场、爬塔、大秘境。
- 活动：Activity/AvyTime/DoubleDrop/14 日活动。
- 刷新：Shop.RefreshType、LimitType、LimitNum。

## 6. 标记风险

至少检查：

- 是否涉及付费或元晶。
- 是否涉及抽卡券或专武抽卡券。
- 是否是可重复供给。
- 是否和常驻供给叠加。
- 是否有活动时间或赛季边界。
- 是否有展示与真实发奖不一致。
- 是否可能绕过主线、关卡或成长节奏。

## 7. 输出格式

```text
System:
Responsibility:
Cadence:
Source tables:
Reward/cost references:
Unlock/activity references:
Risks:
Next skill:
```

没有直接观察的部分写 `待确认`。
