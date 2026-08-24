# 主线章节开启条件配置审计

- 审计日期：2026-08-18
- 审计范围：本机 Vgame SVN 工作副本中的 `ChapterLevel.xlsx`、`Unlock.xlsx` 及客户端导出物
- 状态边界：`WORKING_COPY_CONFIGURED_EXPORT_VERIFIED`，不代表 Production/LIVE
- 目标规则：0～2章不设章节开启条件；3～7章仅按玩家/主角等级 24/28/31/33/35 开启，不叠加前章末关条件

## 配置结果

| 章节 | ChapterId | ChapterLevel.Unlock | Unlock 类型 | 参数 | 结论 |
|---|---:|---:|---|---:|---|
| 0 | 10000 | 空（导出0） | — | — | 无章节开启条件 |
| 1 | 10001 | 空（导出0） | — | — | 无章节开启条件 |
| 2 | 10002 | 空（导出0） | — | — | 无章节开启条件 |
| 3 | 10003 | 201 | UnLock_UUT_player_Grade | 24 | 仅等级条件 |
| 4 | 10004 | 202 | UnLock_UUT_player_Grade | 28 | 仅等级条件 |
| 5 | 10005 | 203 | UnLock_UUT_player_Grade | 31 | 仅等级条件 |
| 6 | 10006 | 204 | UnLock_UUT_player_Grade | 33 | 仅等级条件 |
| 7 | 10007 | 205 | UnLock_UUT_player_Grade | 35 | 仅等级条件 |

## 来源链与运行语义

- `ChapterLevel.xlsx` 与 `Unlock.xlsx` 均已在 Luban `__tables__.xlsx` 注册，字段类型分别为章节 `Unlock:int` 与解锁条件 `UnLockType/UnLockParams`。
- `LevelSystem.GetChapterIsUnlock` 将 `ChapterLevel.Unlock` 交给 `ConditionSystem.GetIsUnLock`。
- 空值导出为0；`Tables.Unlock.Row(0)` 无记录时 `GetIsUnLock` 返回 true，因此0～2章不会被章节条件硬卡。
- `UnLock_UUT_player_Grade` 按 `PlayerSystem.Level >= UnLockParams[1]` 判定；升级事件会触发条件刷新。
- 章节内具体关卡的 NextLevel/Unlock 链未改，本次只改变章节入口条件。

## 改动范围与安全检查

- 与备份逐单元格比较：`ChapterLevel.xlsx` 仅7个单元格变化，`Unlock.xlsx` 仅5个单元格变化，均为目标字段。
- 未新增表行；复用原有且类型已为 `UnLock_UUT_player_Grade` 的201～205，避免改写旧的104/113/127/145/160/175/275关卡条件及高难引用。
- `Unlock.xlsx` 的55个公式文本全部保留；经隐藏 Excel 完整重算后，55个公式缓存均非空，未发现 `#REF!/#DIV/0!/#VALUE!/#N/A/#NAME?/#NUM!/#NULL!`。
- 所有非0 `ChapterLevel.Unlock` 均能解析到现有 Unlock ID。
- 可复核脚本：`scripts/configure_main_chapter_unlocks.py`、`scripts/verify_main_chapter_unlocks.py`。

## 导出验证

- `export_client.bat`：退出码0，Luban 校验与客户端导出成功。
- `chapterlevel.lua`：10000～10002导出 `Unlock=0`；10003～10007导出201～205。
- `unlock.lua`：201～205导出类型1，参数24/28/31/33/35。
- 对应 `chapterlevel.bytes`、`unlock.bytes` 已同步生成并通过哈希复核。

| 文件 | SHA256 |
|---|---|
| chapterlevel.lua | `1C6C217C253AE02273F2B40E330CFEC1FC6F391338487152CA7CA0F2330FA3F6` |
| unlock.lua | `2493163D2C3C568BB156F841173CD247AA1DF3511A04CB2F935208EF22086304` |
| chapterlevel.bytes | `62A9168D7CB0629AD27BB269B3608445D0A809B12A25CE61621D9BE4A4B03E92` |
| unlock.bytes | `CCA57473BA5FCF7E2FBAE6DDA3A5CE3FF8C8F16111C73B7EFD8301B8867AC1FC` |

## 回滚备份

备份目录：`backups/chapter-unlock-20260818-171110/`

| 文件 | SHA256 |
|---|---|
| ChapterLevel.xlsx | `7BCD385191D2465DE8484CD0DA3DF015A4AEEB9A314BFA57B61E9D549B2CE44D` |
| Unlock.xlsx | `D1EF9C1D0987F0FDA8AE566D68C19E4056F9FB441A734A6B539D9DD0CE4A0112` |

## 工具限制与结论

通用 `vgame-config-quality-audit` 扫描器在遍历本次范围外的另一本短行工作簿时触发 `IndexError`，因此未把该全量扫描标记为通过。本报告改用目标源表、备份差异、运行代码、公式缓存、引用完整性和生成物的组合审计；这些检查全部通过。

结论：配置与客户端导出已就绪，可进入实机冒烟验证；在未完成实机与发布台账核验前，不标记为 LIVE。
