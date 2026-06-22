# Vgame 角色套件路由补充

## 使用入口

涉及以下问题时，优先读取 `vgame-character-kit-design-map`：

- 角色定位、英雄身份、品级、阵营、类型。
- 普攻、自动技能、能效被动、能效额外、必杀、天赋。
- 升星节点、角色专武、通用被动。
- 旅券/邮票套装技能、映射装备词条。
- 角色技能设计源文档，例如 `D:\数值文档\数值文档\Vgame英雄设计.xlsx`。
- 角色设计审查、技能实现风险、角色机制和玩法验证关系。

## 边界

`vgame-character-kit-design-map` 只负责角色设计关系、证据判断和审查路由：

- 技能、Buff、子弹、召唤、伤害效果、AI 或 runtime battle content：转 `vgame-battle-content-map`。
- 角色定义、Hero/Skill/Buff 表、角色属性、突破、升星、专武配置、技能编辑器和 runtime 序列化链：转 `vgame-hero-skill-config-map`。
- 升星、专武、旅券、映射装备如何转化为战斗表现：转 `vgame-growth-combat-conversion-map`。
- DPS、TTK、系数、生存和战斗数值平衡：转 `vgame-battle-tuning-helper` 或 `game-numerical-analysis`。
- 真实配置表、字段、Luban schema、生成 JSON：转 `vgame-config-schema`。
- 奖励、DropId、道具来源/消耗、开放节奏：转对应奖励、经济或关卡进度 skill。

## 证据规则

- `角色技能设计` 可作为当前角色设计主证据。
- `角色（留档）` 只作历史对照。
- `角色技能备忘录（后期删除）` 只作实现风险记录。
- 发现重复 ID、合并单元格、公式引用、空值或异常品质/类型时，必须标记 `待确认`。
- 不把设计文档内容直接等同于真实配置事实。
