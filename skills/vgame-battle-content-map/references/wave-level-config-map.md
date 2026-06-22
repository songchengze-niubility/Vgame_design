# Wave & Level Config Map

## 关卡-波次配置模型

Vgame 是跑酷战斗射击游戏，关卡结构与传统回合制/塔防不同：

```
Level（关卡）
├─ Terrain（地形分段）
│  ├─ TerrainChild（地形子块）
│  │  ├─ 平台/障碍/机关
│  │  └─ SpawnPoint（刷怪点）
│  └─ LoopTerrain（循环地形）
│     ├─ LoopChild（循环子块）
│     └─ LoopStopCondition（停止条件）
└─ Wave/SpawnGroup（波次/刷怪组）
   ├─ SpawnCondition（触发条件）
   ├─ MonsterList（怪物列表+数量）
   ├─ SpawnPosition（出生位置/相对偏移）
   ├─ SpawnInterval（间隔时间）
   └─ EliteRatio/BossFlag（精英比例/Boss标记）
```

## Loop 机制（Vgame 特色）

从代码 `LLevelMgr.cs` 可知 Vgame 有 Loop 地形机制：

- `data.LoopTerrains` 定义多段循环地形
- `loopIndex` 跟踪当前循环段
- 每段循环结束后判断：已是最后一段 → `ShowBattleWin()`；否则 → `PreNextLoop()`
- 循环停止条件由 `ShouldStopLoop()` 判断（可能基于击杀数/时间/到达位置）
- `OnEntityDestroy` 监听怪物死亡，每次死亡检查 `TryStopLoop()`
- `entityDestroyDic` 按 EntityType 分类记录已击杀实体
- `ignoreLoop` 标记的实体不参与循环计数

### Loop 关键字段（待确认精确表名）

| 字段 | 说明 |
|---|---|
| LoopTerrains | 循环地形配置数组 |
| LoopChilds | 每段循环的子地形块 |
| LoopLength | 循环段总长度 |
| LoopStopCondition | 停止条件（击杀数/类型） |
| ignoreLoop | 实体是否忽略循环计数 |

## 关卡配置

### Level 表关键字段（部分已确认）

| 字段 | 说明 | 确认状态 |
|---|---|---|
| LevelId | 6位关卡ID | 已确认 |
| LevelType | 关卡类型枚举 | 已确认 |
| WorldId | 地图ID | 已确认 |
| ChapterId | 章节ID | 已确认 |
| Terrain/WorldData | 地形配置引用 | 待确认精确字段 |
| WaveConfig | 波次配置引用 | 待确认 |
| MonsterLevel | 怪物等级/推荐等级 | 待确认 |
| Vitality | 体力消耗 | 已确认（格式: ItemId,Count） |

### 已知 LevelType 枚举

| LevelType | 说明 |
|---|---|
| LevelType_Main | 主线普通 |
| LevelType_Main_Difficult | 主线困难 |
| LevelType_Exp | 经验资源本 |
| LevelType_Gold | 金币资源本 |
| LevelType_Weapon | 专武经验本 |
| LevelType_Equip_* | 装备副本 |
| LevelType_Strategy_* | 旅券副本（First/Second/Three/Four） |
| LevelType_SpecialEquipment | 映射装备副本 |
| LevelType_InfiniteChallenge | 无限挑战 |
| LevelType_Arena | 竞技场 |
| LevelType_Tower | 爬塔 |
| LevelType_MythicDungeon | 大秘境 |

## 波次配置

### Wave/SpawnGroup 关键字段（待确认）

| 字段 | 说明 |
|---|---|
| WaveId | 波次ID |
| TriggerType | 触发方式（进入区域/时间/前波清完/手动） |
| TriggerParam | 触发参数 |
| MonsterIds | 怪物ID列表 |
| MonsterCounts | 对应数量 |
| SpawnPositions | 出生位置 |
| SpawnDelay | 出生延迟 |
| SpawnInterval | 分批间隔 |
| EliteChance | 精英概率 |
| IsBossWave | 是否Boss波次 |

## 不同玩法的波次特点

| 玩法 | 波次特点 |
|---|---|
| 主线 | 线性推进，固定波次，Boss在最后 |
| 旅券副本 | 单Boss战，节奏快 |
| 资源本 | 大量小怪，效率型 |
| 无限挑战 | 3段循环（普通→精英→Boss），无限递增 |
| 竞技场 | 双方共享刷怪，未清怪攻击基地 |
| 爬塔 | 逐层递增难度 |
| 大秘境 | 环境词缀 + 递增难度 |

## 环境配置

### 环境机关类型（待确认精确配置）

| 类型 | 说明 |
|---|---|
| 地面陷阱 | 踩到触发伤害/减速 |
| 移动平台 | 周期性移动，影响站位 |
| 伤害区域 | 持续伤害范围 |
| 障碍物 | 阻挡移动/子弹 |
| 弹射装置 | 强制位移 |
| 坠落区域 | 掉落判定 |

### 已知地面检测

从代码 `LLevelMgr.IsGroundBelow` 可知：
- 使用物理射线检测地面
- 与 `LPlayerMoveController` 共享逻辑

## 配置修改影响评估

| 修改内容 | 影响范围 |
|---|---|
| 改Wave怪物数量 | 该关卡难度 + Loop停止条件 |
| 改Monster属性 | 所有引用该Monster的关卡 |
| 改地形结构 | 战斗节奏 + 跑酷体验 |
| 改Loop条件 | 关卡是否能正常结束 |
| 改Boss阶段阈值 | Boss体验节奏 |
