# 关卡编辑器 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 关卡编辑器（Level Editor） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | LOW |
| 关联 Proposal | — |

## 背景与目标
### 背景
Vgame 的关卡编辑器是 Unity 编辑器工具（TerrainInfoEditor），通过菜单 `局内工具/Scene/关卡编辑 &M` 进入。策划通过放置地形块、标记循环区域、放置实体（怪物/道具/触发器）、配置移动平台和摄像机边界来构建关卡。最终通过 TerrainDataCollector 序列化为 3 个 .bytes 文件（LogicData.bytes + VisualData.bytes + StringTable.bytes），运行时由 LevelUtility 加载。

### 目标
- 定义关卡编辑器的完整工作流程（地形 → 实体 → 序列化）
- 规范循环区域（LoopTerrain）配置和战斗目标绑定
- 明确编辑器的子窗口体系和职责
- 梳理运行时关卡加载的序列化文件结构

### 非目标
- Unity 场景编辑的基础操作教程
- 具体关卡的美术/视觉设计规范
- 网络同步下的关卡流式加载

## 核心规则

### R-01: 编辑器入口与子窗口体系
- **触发条件**：策划在 Unity 菜单栏点击 `局内工具 → Scene → 关卡编辑 &M`
- **前置限制**：已安装关卡编辑器插件，Unity 项目中已加载目标场景
- **操作流程**：
  1. 点击菜单项 → 打开 TerrainInfoEditor 主窗口
  2. 主窗口内可开启以下子窗口：
     - `TerrainOperationWindow`：放置/移动/删除地形块
     - `TerrainListWindow`：管理地形块列表，查看/选择/批量编辑
     - `DrawMovePathWindow`：绘制移动平台的移动路径
  3. 各子窗口可同时打开，互操作实时反映到场景视图中
- **状态变化**：编辑器 UI 加载 → 等待策划操作
- **资源变化**：无（仅编辑阶段）
- **UI 反馈**：场景视图中实时高亮选中的地形块或实体；Inspector 显示选中对象属性
- **异常边界**：编辑器初始化时找不到场景 → 提示选择或新建场景；子窗口重复打开时聚焦已有窗口而非新建
- **落地点**：Unity Editor 工具，代码位于 `Editor/TerrainInfoEditor/` 目录

### R-02: 地形块放置与循环区域标记
- **触发条件**：策划通过 TerrainOperationWindow 选取并放置地形块
- **前置限制**：地形块预制体资源已准备（材质、碰撞体等）
- **操作流程**：
  1. TerrainOperationWindow 中选择地形块类型（平台、斜坡、墙壁等）
  2. 在场景视图中点击放置 → 生成地形块 GameObject
  3. 调整位置、旋转、缩放
  4. 使用 `LoopTerrainSetUp` 功能将多个地形块标记为一个循环区域组
  5. 循环区域可绑定战斗目标类型（BossKill / EliteKill / OrdinaryKill / None）
- **状态变化**：场景中地形块对象新增/修改/删除
- **资源变化**：场景中增加地形块 GameObject
- **UI 反馈**：循环区域以不同颜色线框高亮，标注战斗目标类型
- **异常边界**：地形块放置在摄像机边界外 → 警告但允许（支持超宽关卡）；同一地形块属于多个循环区域 → 警告并阻止重复隶属
- **落地点**：`TerrainDataCollector` 收集所有地形信息 → 序列化为 `TerrainLogicData[]`

### R-03: 实体放置（怪物/道具/触发器）
- **触发条件**：策划需要向场景中放置交互实体
- **前置限制**：实体的配置表数据已准备（MonsterId / ItemId / TriggerType 等有效）
- **操作流程**：
  1. 在编辑器中选取实体类型（怪物 / 道具 / Zone 触发器）
  2. 在场景视图中 X 坐标位置点击放置
  3. 配置实体属性：
     - 怪物：MonsterId、等级、所属循环区域组
     - 道具：ItemId、数量、刷新规则
     - 触发器：TriggerType（如 ZoneShowGuide）、关联引导 ID
  4. 所有实体数据收集到 `IEntityData[]` 列表中
- **状态变化**：实体数据写入 TerrainDataCollector
- **资源变化**：编辑器内创建实体数据对象（非运行时 GameObject）
- **UI 反馈**：场景中以图标+Gizmo 形式预览实体位置
- **异常边界**：MonsterId 不存在于 Monster.xlsx → 编辑时警告，放置后图标显示红色！标记；实体与循环区域不关联 → 允许但不参与战斗目标判定
- **落地点**：`IEntityData[]` 包含 MonsterEntityData / ItemEntityData / TriggerEntityData 等派生类

### R-04: 移动平台路径编辑
- **触发条件**：策划需要在关卡中添加移动平台时
- **前置限制**：已放置了可移动的地形块
- **操作流程**：
  1. 选择目标地形块 → 打开 `DrawMovePathWindow`
  2. 在场景视图中点击添加路径点 → 形成路径线段
  3. 配置路径属性：移动速度、暂停时间（每个路径点）、循环模式（往返/单向/循环）
  4. 预览路径动画 → 确认保存 → 路径数据写入 TerrainDataCollector
- **状态变化**：地形块路径数据新增/修改
- **资源变化**：路径点列表（Vector3 坐标数组）写入数据
- **UI 反馈**：场景中以彩色虚线显示路径，箭头指示移动方向；预览时地形块沿路径运动
- **异常边界**：路径点少于 2 个时无法保存；路径穿出摄像机边界 → 警告但允许
- **落地点**：`MovingPlatformData[]` 包含在 `TerrainLogicData` 中

### R-05: 摄像机边界设置
- **触发条件**：关卡编辑器进入最终调整阶段
- **前置限制**：地形块已基本摆放完毕
- **操作流程**：
  1. 在编辑器中拖拽或输入数值设置摄像机边界框（左/右/上/下）
  2. 摄像机边界定义了玩家可视范围，角色和战斗在此范围内进行
  3. 边界框外的地形块和实体不会被摄像机渲染但可能存在（用于关卡逻辑）
- **状态变化**：摄像机边界数据更新
- **资源变化**：边界框四个坐标值写入 SceneLogicData
- **UI 反馈**：场景视图中以黄色半透明矩形显示摄像机边界
- **异常边界**：边界框面积过小（无法容纳一个角色）→ 警告；循环区域完全超出边界 → 警告
- **落地点**：`CameraBoundData` 包含在 `SceneLogicData` 头部元信息中

### R-06: 序列化与文件生成
- **触发条件**：策划完成关卡编辑后点击保存/导出
- **前置限制**：所有地形块、实体、路径数据已配置完毕
- **操作流程**：
  1. `TerrainDataCollector` 从场景收集所有编辑数据
  2. 按数据类型组织：
     - `LogicData.bytes`：TerrainLogicData[]（地形数据）+ TerrainLoopLogicData[]（循环区域数据）+ IEntityData[]（实体数据）+ CameraBoundData + MovingPlatformData[]
     - `VisualData.bytes`：SceneVisualData（视觉层数据，贴图引用、装饰物等）
     - `StringTable.bytes`：关卡内用到的文本字符串表（NPC 对话、提示文字等）
  3. 使用 MessagePack 序列化为 .bytes 文件 → 保存到关卡资源目录
- **状态变化**：编辑器数据 → 序列化 → .bytes 文件
- **资源变化**：3 个 .bytes 文件生成/更新
- **UI 反馈**：保存进度条 → 完成提示 + 文件大小显示
- **异常边界**：序列化过程中引用资源缺失 → 用默认值替代并在日志中记录；.bytes 文件写入权限不足 → 报错并提示检查文件占用
- **落地点**：关卡资源目录下 `LogicData.bytes` / `VisualData.bytes` / `StringTable.bytes`

### R-07: 运行时关卡加载
- **触发条件**：玩家进入关卡/切换场景时
- **前置限制**：level.xlsx 中 LevelDataPath 已配置为对应 Unity 场景名称
- **操作流程**：
  1. `LevelUtility.LoadSceneLogicData(levelName)` → 读取 `LogicData.bytes`
  2. 反序列化 → 获取 TerrainLogicData[]（地形）→ LLevelMgr 加载地形 block
  3. 获取 IEntityData[] → 逐项实例化怪物/道具/触发器
  4. 获取 TerrainLoopLogicData[] → 初始化循环区域组和战斗目标
  5. 获取 CameraBoundData → 设置摄像机移动范围
  6. 加载 `VisualData.bytes` 和 `StringTable.bytes` → 应用视觉层和本地化文本
- **状态变化**：数据加载 → 场景实例化 → 关卡就绪
- **资源变化**：Unity 场景中动态创建所有关卡对象
- **UI 反馈**：加载界面显示关卡名称→ 完成后淡入进入战斗
- **异常边界**：.bytes 文件版本与当前代码不兼容 → 报错并使用空白关卡 fallback；循环区域无激活的战斗目标（全部 None）→ 警告，关卡正常运行但不触发战斗结束条件
- **落地点**：`LevelUtility.LoadSceneLogicData()` → `LLevelMgr.Initialize()` → 关卡运行时
