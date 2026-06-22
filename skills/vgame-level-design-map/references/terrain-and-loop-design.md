# Terrain & Loop Design

## 地形类型

### 静态地形 (LTerrain)

| 属性 | 说明 |
|---|---|
| RacetrackTypeEnum | 地形类型分类 |
| BoundaryCfgId | 镜头边界配置ID |
| IsDestructible | 是否可破坏（被打3次后碎裂） |
| RunwayLogic | 物理形状生成器（碰撞体） |
| StartPos / EndPos | 地形段的起止坐标 |
| AngleZ | 旋转角度（斜坡等） |

**地形是玩家跑酷的物理基础**——角色在上面跑/跳/落地，怪物也站在上面。

### 移动平台 (LTerrainMoveEntity)

| 属性 | 说明 |
|---|---|
| 动态物理体 | 会移动的地形 |
| 携带实体 | 站在上面的角色/怪物跟着动 |
| TerrainMove策略 | 路径点+速度+加速度定义运动轨迹 |
| 召唤方式 | 通过 SummonTerrainAction（技能系统） |

**移动平台用于跑酷关卡增加空间变化**——玩家需要跳上移动平台才能到达下一段。

### 可破坏地形

- 有HP概念（默认3次命中后破坏）
- 破坏后物理碰撞消失，角色/怪物会掉落
- 可用于设计"打碎地板让怪物掉下去"的机制

## Loop 地形（波次战斗核心）

### 机制

Loop 是 Vgame 关卡中**最核心的战斗结构**：

```
玩家跑到 Loop 起点
  → 镜头停止前进
  → 地形段循环重复（无限跑道感）
  → 怪物持续刷出
  → 玩家击杀满足条件
  → Loop 结束，镜头继续前进
```

### 数据结构

```
TerrainLoopLogicData:
  LoopChilds[]        // 循环内的地形子块（可以有多段拼接）
  LoopTypeEnum Type   // 结束条件类型
  LoopLength          // 总循环长度
  ParamTemp           // 条件参数（击杀数）
  Position            // 世界坐标位置
```

### 结束条件 (LoopTypeEnum)

| 类型 | 说明 | 典型场景 |
|---|---|---|
| `BossKill` | 击杀N个Boss | Boss战 |
| `EliteKill` | 击杀N个精英 | 精英遭遇战 |
| `OrdinaryKill` | 击杀N个普通怪 | 清怪段 |
| `None` | 立即通过（不循环） | 纯跑酷段 |

### Loop 运行时逻辑

```csharp
// LLevelMgr.cs 核心流程
OnEntityDestroy(entity):
  if (!looping) return
  if (entity.EntityData.ignoreLoop) return  // 标记忽略的不计数
  entityDestroyDic[entity.EntityType].Add(entity.ID)
  TryStopLoop()

TryStopLoop():
  if (ShouldStopLoop()):  // 检查击杀计数是否满足条件
    CleanUpLoop()
    if (lastLoop): ShowBattleWin()  // 最后一个Loop→胜利
    else: PreNextLoop()             // 进入下一个Loop
```

### Loop 设计要点

| 要点 | 说明 |
|---|---|
| Loop 数量 | 一个关卡可以有多个 Loop（多波次） |
| 最后一个 Loop | 结束后触发战斗胜利 |
| ignoreLoop 标记 | 某些实体（道具、环境怪）不参与计数 |
| Loop 子块 | 一个 Loop 内可以有多段地形拼接 |
| ExtraOffset | Loop 结束后计算下一段地形的偏移量 |

### 常见 Loop 模式

| 模式 | 结构 | 典型玩法 |
|---|---|---|
| 单Boss Loop | 1个Loop，BossKill×1 | 旅券副本、主线Boss战 |
| 多波清怪 | 3个Loop，OrdinaryKill×5/8/10 | 资源副本 |
| 渐进式 | Loop1普通→Loop2精英→Loop3Boss | 无限挑战每轮 |
| 无Loop | 纯跑酷，到终点即胜利 | 教学关/演出关 |

## 地形编排节奏

### 关卡结构模板

```
[开头平台] → [跑酷段1] → [Loop1: 清怪] → [跑酷段2] → [Loop2: Boss] → [结算]
```

### 跑酷段 vs 战斗段的交替

| 段落类型 | 特点 | 设计目标 |
|---|---|---|
| 跑酷段 | 无怪/少怪，有平台跳跃/障碍 | 节奏调节、空间转换、喘息 |
| 战斗段(Loop) | 大量怪物，地形平坦 | 战斗验证、DPS输出 |
| 混合段 | 边跑边打，有环境机关 | 紧张感、操作考验 |

### 难度层次（通过地形控制）

| 难度手段 | 实现方式 |
|---|---|
| 增加坑位 | 地形间留空，掉落即受伤 |
| 增加高低差 | 需要跳跃才能到达的平台 |
| 移动平台 | 增加时机判断（跳上移动平台） |
| 可破坏地形 | 站太久会碎，逼玩家前进 |
| 窄平台 | 减少闪避空间 |
| 斜坡 | 影响移动速度和弹道 |

## 镜头边界 (CameraParameter)

| 字段 | 说明 |
|---|---|
| RoleCameraY | 角色在镜头中的Y位置 |
| TerrainY | 地形在镜头中的Y位置 |
| Duration | 过渡时间 |

不同地形段可以配不同的镜头参数，实现"抬镜头看高台""压镜头看地下"等效果。
