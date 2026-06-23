# Skill System Architecture

## 配置层

### 技能主表: Skill.xlsx

路径: `${VGAME_ROOT}\Config\GameConfig\Datas\Skill\Skill.xlsx` (1356行)

| 字段 | 类型 | 说明 |
|---|---|---|
| SkillId | int | 技能唯一ID |
| Name | lotext | 技能名 |
| Describe | lotext | 描述 |
| DescParam | array;string | 描述参数（用于动态文本） |
| Icon | string | 图标资源路径 |
| Lv | int | 技能等级 |
| SkillType | Skill_type | 技能类型枚举 |
| SP | int | SP消耗 |
| SkillData | string | **编辑器资产路径**（如 "Chips/chipstest"） |
| Introduction | string | 介绍文本 |
| AutoSkillType | AutoSkillType? | 自动释放类型 |

### 技能类型枚举 (Skill_type)

| 枚举 | 说明 |
|---|---|
| SkillsSTMelee | 普攻 |
| SkillsSTPower | 必杀 |
| SkillsSTTalent | 天赋 |
| SkillsSTStrategy | 策略/旅券 |
| SkillsSTEqpt | 装备技能 |
| SkillsSTExcl | 专武技能 |
| SkillsSTEnhancementPassive1-3 | 效率被动 |
| SkillsSTEnhancement1-4 | 效率主动 |
| SkillsChips | 芯片技能 |
| SkillsSpecialEquipment | 映射装备技能 |

### 相关配置表

| 表 | 用途 |
|---|---|
| TargetSkill.xlsx (405行) | SkillId → 目标选择模式 (ModifierTargetType) |
| LevelSkill.xlsx (199行) | 关卡/装备技能配置（回复速率、存储量、消耗） |
| HeroSkillLv.xlsx (40行) | 技能升级消耗（按职业×类型×等级） |
| BuffIcon.xlsx (18行) | Buff图标注册（攻击UP、防御DOWN、流血等） |

---

## 编辑器层

### 技能编辑器

- 工具: `SkillEditorWindow.cs`（Unity EditorWindow，节点图编辑器）
- 资产: `SkillEditorAsset.cs`（ScriptableObject，菜单 "Game Play/Skill Asset"）
- 存储路径: `Assets/GameResources/GameData/SkillData/Editor/{asm}/{name}.asset`

### 编辑流程

```
1. 在 Unity 中创建/打开 SkillEditorAsset
2. 使用节点图编辑器连接 States 和 Events
3. 每个 State 包含多个 SkillActionClip（时间轴片段）
4. 每个 ActionClip 配置具体行为（伤害/Buff/移动/特效等）
5. 保存 → SkillSerializer.Serialize() → .bytes 文件

产出: Assets/GameResources/GameData/SkillData/Runtime/{asm}/{name}.bytes
```

### 引用关系

```
Skill.xlsx.SkillData = "{asm}/{name}"  →  对应 .bytes 文件路径
例: SkillData = "Chips/chipstest"  →  Runtime/Chips/chipstest.bytes
```

---

## 运行时层

### 核心执行流程

```
SkillInstance (技能实例)
  ├── SkillLine (状态机 / 时间轴)
  │     └── ClipState[] (按时间顺序)
  │           └── SkillActionClip (具体行为)
  │                 ├── OnTick() — 每帧执行
  │                 └── OnFinish() — 结束时执行
  ├── SkillEventListener[] (事件监听)
  │     └── 条件满足时触发对应 State
  └── SkillCooldown (冷却管理)
```

### SkillContext（执行上下文）

| 字段 | 说明 |
|---|---|
| Id | 技能ID |
| World | LogicWorld引用 |
| Entity | 施法者实体 |
| Component | LSkillComponent |
| Skill | SkillInstance |
| EntityBlackboard | 共享变量黑板 |
| DeltaTime / PassTime | 帧时间 / 已过时间 |
| Interrupted | 是否被打断 |
| IsDestroyed | 技能是否已销毁 |

### 63种 Action 类型

| 类别 | Action | 说明 |
|---|---|---|
| **伤害/治疗** | CastDamageAction | 造成伤害 |
| | HealAction | 治疗 |
| | ShieldAction | 施加护盾 |
| **Buff** | AddBuffAction | 添加Buff |
| | RmBuffAction | 移除Buff |
| | ModifyBuffStackAction | 修改Buff层数 |
| **移动** | MoveAction | 位移 |
| | DashAction | 冲刺 |
| | ForceMove | 强制移动 |
| **发射** | FireBullet | 发射子弹 |
| | SummonAction | 召唤实体 |
| | SummonTerrainAction | 召唤地形 |
| **能量** | ChangeEnergyAction | 修改能量 |
| | CooldownAction | 修改冷却 |
| **状态** | InvincibleAction | 无敌 |
| | CounterAction | 反击 |
| | ForceSkillAction | 强制释放技能 |
| | CastSkillAction | 释放另一个技能 |
| **表现** | PlaySpineAnimation | 播放Spine动画 |
| | PlayEffect | 播放特效 |
| | CameraShakeAction | 镜头震动 |
| | PlayBulletTimeAction | 子弹时间（慢动作） |
| | CutInAction | 演出插入 |
| **控制** | ForbidOperation | 禁止操作 |
| | AllowOperation | 恢复操作 |

### 打断策略

| 策略 | 行为 |
|---|---|
| StateInterrupt | 暂停当前，打断结束后恢复 |
| ResetInterrupt | 重置，从头开始 |

### 事件系统

技能可以监听 LEventType 事件并条件触发：
- 受击时、击杀时、死亡时、HP阈值、能量满、定时器等
- 通过 `SkillEventListener` + `CompareHandler` 条件判断

---

## 数据流总结

```
策划配表 (Skill.xlsx)
  → SkillId + SkillType + SkillData路径 + SP + Icon

技能编辑器 (Unity)
  → 节点图定义 States/Events/Actions
  → 序列化为 .bytes (MessagePack)

运行时
  → LSkillComponent.Tick()
    → SkillInstance.Tick()
      → SkillLine.Tick() → ActionClip.Execute()
        → CastDamage / AddBuff / FireBullet / ...
```
