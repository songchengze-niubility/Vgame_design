# 战斗掉落 Icon 表现 — Design Doc

## 元信息

| 项 | 内容 |
|---|---|
| 功能名称 | 战斗掉落 Icon 表现 |
| 状态 | InReview |
| 风险档位 | MEDIUM |
| 更新日期 | 2026-07-10 |
| 关联 Proposal | 待创建 |

## 1. 目标与边界

关卡战斗中，普通小怪死亡时可按配置概率掉出道具 Icon；关底怪死亡且正式触发胜利时，掉出关底配置的 Icon 和关中未掉完的余量。所有 Icon 从怪物位置弹出，飞入左上角战利品宝箱 Icon。

本期为纯客户端视觉表现：

- 关中掉落池、概率、关底掉落全部配置在 `UIlevel`。
- 不接入后端、不新增协议、不预摇真实奖励、不读取 `Drop`、`FirstRewardDrop` 或 `FallRewardDrop`。
- 不改变背包、真实奖励、货币、结算、任务或成就。
- `IconCount` 是实际飞出的视觉 Icon 数量，不是道具真实数量。
- 不展示品质框、品质色、道具名称、数量文字或 `xN`。
- 不生成可拾取地面物、碰撞体、Zone 或其他逻辑实体。
- 不在 MonsterData、Monster.xlsx 或关卡场景实体上新增掉落配置字段。

## 2. 配置方案

### 2.1 UIlevel 新增字段

源表为 `${VGAME_CONFIG_DATAS}/level/UIlevel.xlsx`，sheet `level`，逻辑表 `UILevel`。

| 字段 | 类型 | 配置格式 | 用途 |
|---|---|---|---|
| `MidVisualDropItems` | `(array#sep=;),PropType` | `itemId,iconCount;itemId,iconCount` | 关中普通小怪按概率掉落的视觉 Icon 总池。 |
| `MidVisualDropChance` | `int` | `0–10000` | 每只非关底普通小怪死亡时的掉落概率，万分比。 |
| `LevelEndVisualDropItems` | `(array#sep=;),PropType` | `itemId,iconCount;itemId,iconCount` | 关底怪死亡并正式胜利时固定播放的视觉 Icon。 |

`PropType.PropId` 对应 `Items.Id`，`PropType.PropNum` 对应 `IconCount`。

示例：

```text
MidVisualDropItems = 1001,3;2001,1
MidVisualDropChance = 5000
LevelEndVisualDropItems = 3001,2
```

含义：关中视觉池共 4 个 Icon；每只普通小怪死亡有 50% 概率掉 1 个。关底固定再播放 2 个 `3001` Icon；关中未掉完的余量同时在关底飞出。

### 2.2 数据约束

- `ItemId` 必须在 `Items` 中存在且有可用 Icon。
- `IconCount` 必须为正整数。
- 每个数组内的 `ItemId` 不得重复；运行时可防御性合并并记录告警。
- 空数组表示该部分不播放。
- `MidVisualDropChance=0` 表示关中永不掉落；`10000` 表示每次有剩余池的小怪死亡都掉落。
- 不新增 `GlobalsConf` 字段。

## 3. 客户端运行规则

### R-01：战斗初始化

进入战斗后，客户端读取当前 `UIlevel`：

1. 将 `MidVisualDropItems` 克隆为本局 `RemainingMidVisualPool`。
2. 保留 `MidVisualDropChance` 与 `LevelEndVisualDropItems` 作为本局配置快照。
3. 本局状态只存在于客户端战斗生命周期内，不写入存档，不影响真实奖励。

### R-02：关中普通小怪掉落

非关底普通小怪真实死亡时：

1. 若 `RemainingMidVisualPool` 为空，不播放。
2. 使用 `MidVisualDropChance` 做一次万分比概率判定；未命中不播放且不扣减池。
3. 命中后，按各 `ItemId` 的剩余 `IconCount` 作为权重，随机抽取 1 个 Icon。
4. 被抽中项剩余数量减 1；从当前小怪胸口位置播放该 Icon 并飞入战利品宝箱。
5. 每只小怪死亡最多播放 1 个关中 Icon。

此随机仅是纯表现随机，不得占用战斗随机流、真实掉落随机流或任何后端奖励随机。

### R-03：关底合并播放

某次怪物死亡正式触发关卡胜利时：

1. 此次死亡怪物为关底表现起点；不再执行 R-02。
2. 将全部 `RemainingMidVisualPool` 与 `LevelEndVisualDropItems` 按 `ItemId` 合并，`IconCount` 累加。
3. 从关底怪物位置依次飞出合并后的全部 Icon。
4. 清空本局关中余量。

因此，若剩余掉落数量大于后续可击杀小怪数量，或者中间概率多次未命中，全部余量都会在关底一并飞出。

### R-04：Icon 动画与目标

1. Icon 从怪物胸口锚点弹出；无锚点时使用模型中心加固定高度偏移。
2. Icon 短暂散开后，按队列飞向左上角战利品宝箱 Icon 的实际 HUD 锚点。
3. 到达目标后回收到对象池。
4. 终点必须使用 HUD 的实际 `RectTransform`，不得写死屏幕坐标。

### R-05：异常处理

- 失败、退出、断线、超时、跳关、场景卸载：清理本局视觉池，不补播，不发奖。
- 重连不恢复或重播之前的 Icon；本功能没有任何服务器侧状态。
- HUD 目标不存在、隐藏或已销毁时，跳过当次飞行表现并记录错误，不阻塞战斗和结算。
- Icon 表现失败不得阻塞怪物死亡、胜利、场景切换或原有结算。

## 4. 配置示例

### 示例 A：仅关底

```text
MidVisualDropItems = 空
LevelEndVisualDropItems = 1001,3;2001,1
```

关底怪死亡并正式胜利时，飞出 `1001` Icon ×3 与 `2001` Icon ×1。

### 示例 B：关中概率池

```text
MidVisualDropItems = 3001,2;4001,1
MidVisualDropChance = 5000
LevelEndVisualDropItems = 空
```

每只普通小怪死亡有 50% 概率掉 1 个 Icon。命中时按当前余量随机抽取；共 3 个 Icon 都未掉完的部分留到关底。

### 示例 C：关中余量与关底合并

```text
MidVisualDropItems = 1001,3;3001,1
MidVisualDropChance = 10000
LevelEndVisualDropItems = 2001,1
```

若关中只杀死两只普通小怪，且依次掉出 `1001`、`3001`，则关底剩余 `1001` Icon ×2，与固定 `2001` Icon ×1 一起飞出。

### 4.1 主线与高难奖励同步口径

- 主线 `MidVisualDropItems` 对应当关常规材料；固定数量取实际数量，随机区间取上限作为视觉池数量。
- 主线 `LevelEndVisualDropItems` 对应当关首通奖励，不重复计入常规材料；首次通关时由客户端将关中余量与关底池合并播放。
- 高难 `MidVisualDropItems` 对应当关同色宝石的4次普通判定或2次稀有判定；1级、2级宝石Icon数按章节概率折算为整数代表池，总Icon数保持4或2。
- 高难 `LevelEndVisualDropItems` 对应当关首通元晶与首通宝石。
- `MidVisualDropChance` 主线与高难统一使用 `2000`，只控制关中出现时机；未出现的余量仍在关底补播。
- 玩家经验由程序默认结算，不进入视觉池。
- 元晶无论实际数量统一展示1个Icon；猎鹰金币每5,000折算1个Icon；记录盘、材料和宝石按实际数量或上述区间/概率规则配置。
- 奖励同步时保留既有的小寒、旅券、初级隔热头盔特殊关底表现，避免覆盖教程或剧情表现。

## 5. 实现影响

| 模块 | 改动 |
|---|---|
| UIlevel | 新增 `MidVisualDropItems`、`MidVisualDropChance`、`LevelEndVisualDropItems` 三个客户端可读字段。 |
| Items | 复用 `Items.Id` 到 Icon 的映射。 |
| 客户端战斗 | 初始化关中池；监听普通小怪死亡与权威胜利事件；概率抽取、关底合并、对象池与飞行队列。 |
| HUD | 暴露左上角战利品宝箱 Icon 锚点。 |
| 后端 / 协议 / Drop | 无改动。 |
| Monster / 场景 | 无新增字段，无需重存 LogicData。 |

## 6. 验收标准

| 验收 ID | 场景 | 预期 |
|---|---|---|
| AC-01 | `MidVisualDropItems` 为空、关底字段有值 | 只在正式胜利的关底飞出关底配置 Icon。 |
| AC-02 | `MidVisualDropChance=0` | 关中永不掉落；全量关中池在关底与关底配置合并。 |
| AC-03 | `MidVisualDropChance=10000` | 每只有剩余池的普通小怪死亡均随机飞出 1 个 Icon，直至池空。 |
| AC-04 | `MidVisualDropChance=5000` | 未命中时不播放、不扣池；命中后才随机抽 1 个并扣减。 |
| AC-05 | 剩余数量大于后续小怪数 | 未播放的全部 Icon 在关底一并飞出。 |
| AC-06 | 关底怪死亡触发胜利 | 不执行关中抽取；仅播放关中余量与关底配置的合并结果。 |
| AC-07 | 空池、无效 ItemId、缺 Icon 或负数量 | 给出配置错误/告警，跳过无效项，战斗不被中断。 |
| AC-08 | 失败、退出、断线、重连 | 不发奖、不补播、不重播。 |
| AC-09 | UI | 只显示道具 Icon；无品质框、名称和数量文字；终点为左上角战利品宝箱。 |
| AC-10 | 真实奖励链 | 不调用后端、协议、Drop、背包或结算奖励接口。 |

## 7. 变更记录

| 变更 ID | 旧规则 | 新规则 | 不变项 |
|---|---|---|---|
| CHG-001 | 个别小怪在 MonsterData 配置掉落。 | 关中与关底表现统一配置在 UIlevel。 | 关底以权威胜利事件为准；Icon 飞入战利品宝箱。 |
| CHG-002 | 关中有池即必掉。 | 每只普通小怪先按 `MidVisualDropChance` 判定，命中后才随机抽 1 个。 | 关中余量在关底合并。 |
| CHG-007 | 后端预摇真实首通/常规奖励，并向客户端下发计划。 | 回退为 UIlevel 的纯客户端关中池、概率和关底配置。 | 不展示品质、名称、数量；失败/断线不补播。 |
| CHG-008 | 06交付包仅抽取99个主线与35个高难行，连续粘贴时会因正式表保留旧关卡而错位。 | UIlevel交付包保留正式表完整行序；视觉字段按LevelId与正式Drop引用逐关生成和校验。 | 现行主线99关、高难35关的奖励内容与Icon折算规则不变。 |
