# Level Architecture Overview

## 双层架构

Vgame 关卡采用 **Excel 配表 + Unity 场景** 双层分离的设计：

```
┌─────────────────────────────────────────────────────┐
│  Excel 配表层（策划可直接改）                         │
│  level.xlsx / UIlevel.xlsx / Monster.xlsx            │
│  → 控制：ID、类型、解锁、体力、奖励、属性系数、推荐等级  │
└─────────────────────────────────────────────────────┘
        ↓  level.LevelDataPath 引用场景名
┌─────────────────────────────────────────────────────┐
│  Unity 场景层（需要关卡编辑器）                       │
│  地形布局 / 刷怪点 / Loop区域 / 移动平台 / 触发器     │
│  → 序列化为 LogicData.bytes + VisualData.bytes      │
└─────────────────────────────────────────────────────┘
        ↓  Runtime 加载
┌─────────────────────────────────────────────────────┐
│  Runtime 流式加载                                    │
│  LLevelMgr 根据镜头位置流式加载地形和实体             │
│  GameMode 控制胜负条件                              │
└─────────────────────────────────────────────────────┘
```

## Excel 层控制什么

| 表 | 路径 | 控制内容 |
|---|---|---|
| `level.xlsx` | `Datas\level\level.xlsx` | LevelId, 场景路径(LevelDataPath), HP/ATK/DEF系数, 解锁, 体力, 首通/通关奖励, 阵型, 扫荡, 出生位置, 难度, BossId |
| `UIlevel.xlsx` | `Datas\level\UIlevel.xlsx` | LevelType, 章节ID, 奖励预览, DropId引用, 推荐等级, 怪物列表(UI展示), 三星任务, 多倍结算 |
| `Monster.xlsx` | `Datas\Monster\Monster.xlsx` | 怪物ID, 属性ID, 类型(普通/精英/Boss), 技能组, AI, 模型 |
| `MonsterAttribute.xlsx` | `Datas\Monster\MonsterAttribute.xlsx` | 1000行×多套，怪物属性按等级缩放 |
| `CameraParameter.xlsx` | `Datas\level\CameraParameter.xlsx` | 镜头边界参数 |
| `BossBattleTime.xlsx` | `Datas\level\BossBattleTime.xlsx` | Boss战时间限制、狂暴 |

## 场景层控制什么

| 元素 | 编辑方式 | 存储位置 |
|---|---|---|
| 地形块（静态） | 关卡编辑器摆放 | LogicData.bytes → TerrainLogicData[] |
| Loop区域（波次战斗） | 关卡编辑器标记 | LogicData.bytes → TerrainLoopLogicData[] |
| 刷怪点/实体 | 关卡编辑器按X坐标摆放 | LogicData.bytes → IEntityData[] |
| 移动平台 | 技能系统召唤(SummonTerrainAction) | terrainmove_{id}.bytes |
| 触发器/区域事件 | 编辑器摆放 | LogicData.bytes |
| 视觉背景/前景 | 美术编辑 | VisualData.bytes |

## Runtime 流程

```
1. LLevelMgr.Initialize(levelId, levelName)
   → 从 Tables.Level.Data 读取配表
   → 从 Tables.UILevel.Data 读取UI配表
   → LevelUtility.LoadSceneLogicData(levelName) 反序列化场景数据

2. LLevelMgr.Update() 每帧：
   → 更新 Follower（镜头位置）
   → 计算视口范围
   → 流式加载/卸载地形（进入视口加载，离开卸载）
   → 流式加载/卸载实体（怪物/道具/触发器）

3. Loop 区域：
   → 镜头到达 Loop 起点 → 进入循环模式
   → 地形段重复播放
   → 监听 OnEntityDestroy 事件，计数击杀
   → 满足条件 → CleanUpLoop → 下一段或 ShowBattleWin
```

## Level ID 规范

6位数：`ABCCDD`

| 位 | 含义 | 示例 |
|---|---|---|
| A | 系统类型 | 1=主线, 2=资源本, 3=旅券, 4=映射装备, 5=爬塔, 6=竞技场 |
| B | 难度 | 0=普通, 1=困难 |
| CC | 章节 | 00-99 |
| DD | 关卡序号 | 01-99 |

示例：`100115` = 主线(1) + 普通(0) + 第01章 + 第15关

## 游戏模式与关卡结构的关系

| LevelType | Mode类 | 特殊逻辑 |
|---|---|---|
| 主线/副本/大部分 | NormalMode | 标准：滚屏→Loop战→Boss→胜利 |
| 金币本 | CoinMode | 捡金币+打怪+时间限制，特殊结算 |
| 爬塔 | TowerMode | 逐层递增，每层独立结算 |
| 竞技场 | PVPVEMode | 双方同屏，未清怪攻击基地 |
| 大秘境 | MysteryMode | 环境词缀修改规则 |
| 神经漫游 | NeuralMode | 特殊UI（不显示胜利界面） |

## 策划日常工作分类

| 工作类型 | 改什么 | 在哪改 |
|---|---|---|
| 调数值（怪物血量/攻击） | HP/ATK/DEF系数 | Excel: level.xlsx |
| 调难度曲线 | 怪物等级映射 | Excel: 战斗框架玩法难度线 |
| 新增关卡 | 1.Excel注册 2.场景编辑 | 两层都要 |
| 调地形节奏 | 地形块排列/间距 | Unity 关卡编辑器 |
| 调战斗节奏 | Loop条件/刷怪密度 | Unity 关卡编辑器 |
| 加新Boss | 1.Monster表 2.技能 3.场景 | 三处 |
| 调奖励 | Drop/UIlevel | Excel |
| 调镜头 | CameraParameter | Excel |
