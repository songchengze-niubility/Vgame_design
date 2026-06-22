# Level Editor Pipeline

## 关卡编辑器入口

- Unity 菜单: `局内工具/Scene/关卡编辑 &M`
- 窗口标题: "地形编辑"
- 子窗口: "编辑"(TerrainOperationWindow) / "地块"(TerrainListWindow) / "绘制路径"(DrawMovePathWindow)
- 文档: `D:\Vgame\策划\战斗内容组\关卡编辑器\《关卡编辑器功能文档》.docx`

## 编辑流程

```
1. 打开 Unity 场景（Battle Scenes 目录下）
2. 打开关卡编辑器窗口
3. 在场景中摆放地形块（从地块列表拖入）
4. 设置 Loop 区域（标记 LoopTerrainSetUp 组件）
5. 摆放实体（怪物、道具、触发器）按 X 坐标定位
6. 配置移动平台路径（绘制路径子窗口）
7. 设置镜头边界（BoundaryCfgId）
8. 保存 → 自动序列化
```

## 数据序列化

保存时，`TerrainDataCollector` 收集场景数据：

```
CollectNonLoopTerrainsLogic()  → 收集普通地形块
CollectLoopTerrainLogic()      → 收集 Loop 区域及其子实体
CollectNonLoopTerrainsVisual() → 收集视觉层地形
CollectLoopTerrainsVisual()    → 收集 Loop 视觉层
```

输出到：

```
Assets/GameResources/GameData/SceneData/Runtime/{levelName}/
├── LogicData.bytes      ← 逻辑层（MessagePack 序列化）
├── VisualData.bytes     ← 表现层
└── StringTable.bytes    ← 资源路径查找表
```

## 数据结构

### SceneLogicData（逻辑层核心）

```
SceneLogicData:
├── TerrainLogicData[]          // 普通地形段列表
│   ├── RacetrackTypeEnum Type  // 地形类型
│   ├── BoundaryCfgId           // 镜头边界
│   ├── IsDestructible          // 可破坏
│   ├── LogicID                 // 逻辑ID
│   ├── RunwayLogic             // 物理碰撞形状
│   ├── StartPos / EndPos       // 起止坐标
│   └── AngleZ                  // 旋转角
│
├── TerrainLoopLogicData[]      // Loop 区域列表
│   ├── LoopChilds[]            // 循环子块
│   ├── LoopTypeEnum Type       // 结束条件
│   ├── LoopLength              // 循环长度
│   ├── ParamTemp               // 击杀数参数
│   └── Position                // 世界坐标
│
└── IEntityData[]               // 全部实体（怪物/道具/触发器）
    ├── 位置(X坐标)             // 决定何时加载
    ├── EntityType              // 实体类型
    ├── ignoreLoop              // 是否忽略Loop计数
    └── 具体数据...             // 怪物ID/属性/AI等
```

### SceneVisualData（表现层）

```
SceneVisualData:
├── 地形 Prefab 引用
├── 背景层（多层视差滚动）
├── 前景装饰
└── 特效/粒子放置
```

## 关卡命名规范

场景文件路径格式:
```
Assets/Scenes/BattleScenes/{系统类型}/{章节名}/{关卡名}.unity
```

示例：
- `Main_Simple/Main_Chapter_01/Main_Simple_01_01.unity` → 主线Ch1第1关
- `Resource/Gold_Dungeon/Gold_01.unity` → 金币本第1层

## 新建关卡完整流程

| 步骤 | 操作 | 产物 |
|---|---|---|
| 1 | 确定玩法类型和关卡定位 | 设计文档 |
| 2 | 在 `level.xlsx` 注册新 LevelId | Excel行 |
| 3 | 在 `UIlevel.xlsx` 注册（UI/奖励/入口） | Excel行 |
| 4 | 创建 Unity 场景文件 | .unity 文件 |
| 5 | 关卡编辑器摆放地形 | 地形布局 |
| 6 | 关卡编辑器摆放怪物/Loop | 战斗结构 |
| 7 | 配置镜头边界 | CameraParameter |
| 8 | 保存序列化 | .bytes 文件 |
| 9 | 测试运行 | 验证流程 |
| 10 | 调整数值系数（HP/ATK） | level.xlsx |
| 11 | 配置奖励 | Drop/UIlevel |
| 12 | 配置解锁条件 | Unlock/SystemOpen |

## ITerrainDataSource 接口

地形数据提供者需要实现：

| 方法 | 返回 | 说明 |
|---|---|---|
| GetRunwayResources() | 物理碰撞段 | 用于生成碰撞体 |
| GetTerrainType() | RacetrackTypeEnum | 地形分类 |
| GetBoundaryCfgId() | int | 镜头边界配置 |
| GetIsDestructible() | bool | 是否可破坏 |
| GetAngleZ() | float | 旋转角 |

实现类：`RacetrackAttributesComponent`、`CurvedTrackGenerator`

## 关键注意事项

| 注意 | 说明 |
|---|---|
| 地形间不能有缝隙 | 否则角色会掉进去（除非故意设计坑位） |
| Loop 内实体必须有正确的 EntityType | 否则击杀计数不生效 |
| ignoreLoop 标记 | 道具/环境实体要标记，否则拾取道具也算"击杀" |
| 移动平台通过技能召唤 | 不是直接摆放，是通过 SummonTerrainAction |
| 镜头边界切换需要 Duration | 否则会突然跳变，体验差 |
| LevelDataPath 必须和场景名一致 | level.xlsx 引用的路径要和实际文件对应 |
