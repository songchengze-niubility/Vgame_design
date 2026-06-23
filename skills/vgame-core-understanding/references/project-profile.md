# Vgame 项目画像

## 已确认/已观察事实

| 项 | 内容 | 证据 |
|---|---|---|
| 项目名 | Vgame | 用户指定与 `${VGAME_ROOT}` 工作区 |
| 项目根目录 | `${VGAME_ROOT}` | 当前工作区 |
| Unity 工程候选 | `${VGAME_ROOT}\HorizonFlyProject` | 文件树观察 |
| 配置目录 | `${VGAME_ROOT}\Config` | 文件树观察 |
| 游戏 JSON 配置候选 | `${VGAME_ROOT}\Config\GameConfig\server_json` | 文件树观察 |
| Luban 工具候选 | `${VGAME_ROOT}\Config\Tools\Luban` | 文件树观察 |
| 策划文档目录 | `${VGAME_ROOT}\策划` | 文件树观察 |
| 数值组目录 | `${VGAME_ROOT}\策划\数值组` | 文件树观察 |
| 战斗内容组目录 | `${VGAME_ROOT}\策划\战斗内容组` | 文件树观察 |
| 核心项目理解 | `Vgame 是 5 人小队养成驱动的跑酷战斗射击游戏` | `vgame-core-understanding` |

## 当前核心口径

- 不按传统站桩卡牌理解 Vgame。
- `主线` 是主成长与教学轴。
- `资源副本 / 旅券副本 / 映射装备副本` 是稳定成长供给层。
- `无限挑战 / 竞技场（PVPVE） / 爬塔 / 大秘境 / BOSS挑战` 是验证玩法层。
- `任务 / 抽卡 / 商店 / 通行证 / 签到 / 公会 / 好友聊天` 是外循环系统。
- `世界boss / 能效本 / 主角装备本 / 宝石本 / 铭文本 / 肉鸽` 当前按废弃或非正式内容处理，除非用户明确说明恢复。

## 待确认

| 问题 | 推荐处理 | 状态 |
|---|---|---|
| 当前权威数值版本目录 | 不按日期猜，任务开始时根据用户或文件证据确认 | 待确认 |
| Excel 源表与 JSON 生成关系 | 不直接修改 `server_json`，先确认源表和导表流程 | 待确认 |
| DropId、RewardId、UIlevel 的源表和字段 | 需要结合具体任务读取表结构 | 待确认 |
| 术语表 Excel 原文件 | 当前未在 `${VGAME_ROOT}` 搜到 `Vgame术语表.xlsx`，先使用迁移后的 `vgame-terminology.md` | 待确认 |

## 禁止假设

- 不假设 `server_json` 是源表。
- 不假设最新日期目录就是当前工作版本。
- 不猜奖励、掉落、UIlevel、活动、任务、商店字段语义。
- 不把旧玩法或废弃玩法重新纳入正式设计，除非用户明确要求。
