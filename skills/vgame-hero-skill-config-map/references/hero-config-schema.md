# Hero Config Schema

## 角色定义主表: Hero.xlsx

路径: `${VGAME_ROOT}\Config\GameConfig\Datas\Hero\Hero.xlsx`

### 核心字段

| 字段 | 类型 | 说明 |
|---|---|---|
| HeroId | int | 角色ID (1001, 1002...) |
| Name | lotext | 角色名 |
| FirstName | lotext | 称号/头衔 |
| Quality | Quality | 品质: 4=SSR(橙), 3=SR(紫) |
| HeroClass | Class | 职业: DPS(攻手), Tank(坦克), Support(辅助) |
| Sex | HeroSex | 性别 |
| HeroCamp | HeroCamp | 阵营: One(魏), Two(蜀), Three(吴), Four(群) |
| HeroTag | array;lotext | 标签 (如"群攻;控制") |
| HeroItem | int | 角色道具ID（用于背包展示） |
| HeroShards | int | 碎片道具ID |
| SkillMelee | array;int | 普攻技能ID列表(按等级) |
| SkillsPower | array;int | 必杀技能ID列表(按等级) |
| SkillsSTEnhancementPassive1-3 | array;int | 效率被动技能 |
| SkillsSTEnhancement1-4 | array;int | 效率主动技能 |
| EnergyEfficiencyAttrList | array;int | 效率属性点映射ID |
| BoxX / BoxY | int | 碰撞盒尺寸(*1000) |
| Hp / Attack | int | 基础HP / ATK |
| Energy / EnergyPreAdd | int | 能量上限 / 能量回复 |
| IsSpine | bool | 是否使用Spine动画 |

### ID 规范

- 角色ID: 1001起
- 专武ID: 51001起
- 皮肤ID: 按角色分配

---

## 角色属性表: HeroAttribute.xlsx

路径: `Datas\Hero\HeroAttribute.xlsx`

**ID格式**: `HeroId × 1000 + Level`（如 1001001 = 角色1001的1级属性）

| 字段 | 说明 |
|---|---|
| AttributeID | 复合键 |
| Hp | 生命 |
| PhysicsAttack | 物理攻击 |
| MagicAttack | 魔法攻击 |
| Armor | 防御 |
| Energy | 能量上限 |
| EnergyPreAdd | 能量回复速率 |
| Crit / CritDmgBonus | 暴击率 / 暴击伤害 |
| Miss / Hit | 闪避 / 命中 |
| AttackSpeed | 攻击速度 |
| DmgBonus / DmgImmune | 增伤 / 减伤 |

---

## 角色升级: HeroLv.xlsx

| 字段 | 说明 |
|---|---|
| Lv | 等级 |
| UpgradeCost | 升级金币消耗 |
| GetAttributePoint | 获得属性点 |

---

## 角色突破/升阶: HeroAscendLv.xlsx + HeroAscendMaterial.xlsx

### 等级门控 (HeroAscendLv)

| 字段 | 说明 |
|---|---|
| AscendId | 突破阶段 (0-4) |
| LvLimit | 突破前等级上限 |
| LvUpperLimit | 突破后等级上限 |
| PlayerLv | 要求玩家等级 |

### 材料消耗 (HeroAscendMaterial)

| 字段 | 说明 |
|---|---|
| AscendId | 突破阶段 |
| Quality | 品质 (SSR/SR) |
| ItemClass | 材料列表 (typeId,itemId,count) |
| MoneyCost | 金币消耗 (currencyId,amount) |

---

## 角色升星: HeroStarAttrUp.xlsx

| 字段 | 说明 |
|---|---|
| HeroId | 角色ID |
| Star | 星级 (0-6) |
| CostItem | 碎片消耗 (array;PropType) |
| TalentSkill | 解锁的天赋技能ID |
| StarDesc | 属性加成描述 |
| HpCoef / PhysicsAttackCoef / MagicAttackCoef / ArmorCoef | 属性倍率 |
| 30+详细加成字段 | CritLevel, 各种DmgBonus等 |

---

## 效率图/星盘: HeroEnergyEfficiencyMap.xlsx

**节点图结构**——按职业定义不同的星盘树：

| 字段 | 说明 |
|---|---|
| HeroClass | 职业 |
| Name | 节点名 |
| Type | 节点类型: NodeAttr(属性), NodeAddPassive(加被动), NodePassiveUp(升被动), SkillsMelee/Power/Evo |
| Node | 节点位置ID |
| PreId | 前置节点列表 |
| CostCalibrationPoint | 消耗校准点 |
| HeroLv | 要求角色等级 |
| Lv / MaxLv | 升级等级/最高等级 |
| SkillKey | 升级哪个技能 |
| AttrKey | 属性引用ID |

### 节点属性: HeroEnergyEfficiencyAttr.xlsx

每行一个属性加成（38个属性字段中只填一个）。

### 校准点: CalibrationPoints.xlsx + CalibrationPointsAttr.xlsx

校准点 = 星盘的"额外点数"系统，按职业×节点×角色等级定义制作消耗。

---

## 专武: ExclWeapon.xlsx

路径: `Datas\ExclusiveWeapon\ExclWeapon.xlsx`

| 字段 | 说明 |
|---|---|
| Id | 专武ID (51001起) |
| Name | 名称 |
| Star | 初始星级 |
| Quailty | 品质 (SSR/SR) |
| HeroClass | 职业类型 |
| RelatedHero | 关联角色ID |
| Hp / HpGrow | 基础HP + 每级成长 |
| PhysicsAttack / PhysicsAttackGrow | 物攻 + 成长 |
| MagicAttack / MagicAttackGrow | 魔攻 + 成长 |
| Armor / ArmorGrow | 防御 + 成长 |
| SkillList | 每星解锁技能列表 (array;int, 6个) |
| AttrNameList | 每阶突破属性加成 (array;AttrList) |

相关表: ExclWeaponLv(升级消耗), ExclWeaponAscendLv(突破门控), ExclWeaponAscendMaterial(突破材料), ExclWeaponStar(升星消耗)

---

## 全局关系图

```
Hero.xlsx (HeroId)
  ├── HeroAttribute.xlsx (HeroId*1000+Lv → 全属性)
  ├── HeroStarAttrUp.xlsx (HeroId+Star → 倍率+天赋技能)
  ├── HeroAscendLv/Material.xlsx (Quality+AscendId → 等级上限+消耗)
  ├── HeroSkillLv.xlsx (Class+SkillType → 升级消耗)
  ├── HeroEnergyEfficiencyMap.xlsx (Class → 星盘节点图)
  │     └── HeroEnergyEfficiencyAttr.xlsx (节点 → 属性加成)
  ├── CalibrationPoints.xlsx (Class+Node → 校准点制作消耗)
  │     └── CalibrationPointsAttr.xlsx (HeroId*1000+tier → 固定属性)
  ├── Skin.xlsx (Hero → 视觉资源)
  └── ExclWeapon.xlsx (RelatedHero → 专武)
        ├── ExclWeaponLv/AscendLv/AscendMaterial.xlsx
        └── ExclWeaponStar.xlsx

Hero.SkillMelee/SkillsPower → Skill.xlsx.SkillId
Hero.SkillsSTEnhancement* → Skill.xlsx.SkillId
ExclWeapon.SkillList → Skill.xlsx.SkillId
HeroStarAttrUp.TalentSkill → Skill.xlsx.SkillId
```
