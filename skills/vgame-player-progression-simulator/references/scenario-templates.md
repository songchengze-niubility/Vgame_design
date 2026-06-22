# Scenario Templates

## 预设模拟场景

### 场景 1: F2P 活跃玩家

```yaml
name: f2p_active
description: 免费玩家，每天打满体力，完成所有每日/每周任务
parameters:
  daily_playtime: 60  # 分钟
  stamina_purchase: 0  # 不买体力
  monthly_spend: 0  # 不付费
  daily_tasks: complete  # 完成全部每日
  weekly_tasks: complete  # 完成全部每周
  stamina_allocation:
    mainline: 0.30  # 前期高，后期降
    resource_dungeon: 0.50
    equipment_dungeon: 0.20
  gacha_strategy: save_for_pity  # 攒满保底再抽
  activity_participation: full  # 活动全参与
  pvp_rank: mid  # 中等排名
```

### 场景 2: F2P 休闲玩家

```yaml
name: f2p_casual
description: 免费玩家，每天只花15-30分钟，不一定打满体力
parameters:
  daily_playtime: 20
  stamina_purchase: 0
  monthly_spend: 0
  daily_tasks: partial  # 完成60-70%
  weekly_tasks: partial
  stamina_allocation:
    mainline: 0.40
    resource_dungeon: 0.40
    equipment_dungeon: 0.20
  stamina_waste: 0.30  # 30%体力浪费（未用完）
  gacha_strategy: random  # 有券就抽
  activity_participation: partial
  pvp_rank: low
```

### 场景 3: 小R（月卡玩家）

```yaml
name: light_spender
description: 购买月卡，每天活跃游玩
parameters:
  daily_playtime: 60
  stamina_purchase: 1  # 每天买1次体力
  monthly_spend: 30  # 月卡价格（元）
  monthly_card: true
  daily_tasks: complete
  weekly_tasks: complete
  stamina_allocation:
    mainline: 0.25
    resource_dungeon: 0.45
    equipment_dungeon: 0.30
  gacha_strategy: save_for_pity
  activity_participation: full
  pvp_rank: mid_high
```

### 场景 4: 中R（月卡+通行证）

```yaml
name: medium_spender
description: 月卡+通行证，额外购买性价比礼包
parameters:
  daily_playtime: 60
  stamina_purchase: 2  # 每天买2次体力
  monthly_spend: 100  # 月卡+通行证+偶尔礼包
  monthly_card: true
  battle_pass: paid
  daily_tasks: complete
  weekly_tasks: complete
  stamina_allocation:
    mainline: 0.20
    resource_dungeon: 0.40
    equipment_dungeon: 0.40
  gacha_strategy: target_banner  # 有目标角色/武器时抽
  activity_participation: full
  pvp_rank: high
```

### 场景 5: 大R（重度付费）

```yaml
name: whale
description: 大量付费，追求快速满配
parameters:
  daily_playtime: 90
  stamina_purchase: max  # 买满每日体力
  monthly_spend: 1000+
  monthly_card: true
  battle_pass: paid
  extra_diamond_purchase: true
  daily_tasks: complete
  weekly_tasks: complete
  stamina_allocation:
    mainline: 0.15
    resource_dungeon: 0.35
    equipment_dungeon: 0.50
  gacha_strategy: every_banner  # 每个池都抽
  activity_participation: full
  pvp_rank: top
```

---

## 对比维度

### 关键里程碑对比

| 里程碑 | F2P休闲 | F2P活跃 | 小R | 中R | 大R |
|---|---|---|---|---|---|
| 主角Lv30 | Day 5 | Day 3 | Day 2 | Day 2 | Day 1 |
| 主角Lv40 | Day 14 | Day 10 | Day 7 | Day 5 | Day 3 |
| 主角Lv50 | Day 35 | Day 25 | Day 18 | Day 14 | Day 7 |
| 主角Lv60 | Day 90+ | Day 60 | Day 45 | Day 35 | Day 14 |
| 首个SSR角色 | Day 20 | Day 14 | Day 10 | Day 7 | Day 1 |
| 5角色队伍成型 | Day 60+ | Day 45 | Day 35 | Day 25 | Day 7 |

（以上为估算值，需用实际参数校准）

### 卡点对比

| 卡点 | F2P | 付费 | 说明 |
|---|---|---|---|
| 经验不足 | Day 7-10 | Day 3-5 | 中期最早出现的瓶颈 |
| 金币不足 | Day 14-20 | Day 10 | 多角色同时升级时 |
| 突破材料不足 | Day 20-30 | Day 14 | 需要专门副本产出 |
| 抽卡资源不足 | 持续 | 缓解 | F2P长期瓶颈 |
| 装备深度不足 | Day 30+ | Day 20 | 后期验证玩法需要 |

---

## 自定义场景指南

### 修改参数优先级

1. `monthly_spend` — 付费等级直接决定资源增速
2. `stamina_allocation` — 体力分配决定哪个模块先满
3. `gacha_strategy` — 抽卡策略决定角色/武器获取速度
4. `activity_participation` — 活动参与度影响额外资源量

### What-If 常见调整

| 问题 | 调整参数 |
|---|---|
| 如果增加主线金币奖励？ | `mainline_gold_multiplier` |
| 如果增加每日任务钻石？ | `daily_task_diamond` |
| 如果降低升级消耗？ | `level_cost_multiplier` |
| 如果增加体力上限？ | `daily_stamina_base` |
| 如果加入新资源副本？ | 新增 `extra_daily_income` |
