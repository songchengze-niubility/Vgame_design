# 06候选 → SVN工作副本落表差异清单

核对日期：2026-08-27。基线：本机 `D:/Vgame/Config/GameConfig/Datas`，目录修订r40473；未查询远端HEAD。受控配置没有本地未提交修改；仅有一个未纳入版本控制的Items副本，本次未读取或处理。

## 结论与范围

用户确认的章节任务06数值与当前沉淀MD一致。按本次对话范围落SVN，需要修改7张真实配置表；若只落章节任务，则只需前4张。不能把整个06目录直接覆盖SVN：它含分模块候选、说明页、不同的列布局和行ID。

| SVN相对路径 | 需要同步的内容 |
|---|---|
| task/Jottings.xlsx | 第1、2章挂载列表，共2行 |
| task/Task.xlsx | 11条章节任务文案；其中1315/1327/1328另补DropId |
| task/TaskTarget.xlsx | 11条目标记录：文案、6条参数、2条目标类型及2条跳转入口 |
| Drop/Drop_other.xlsx | 8个章节单项奖励包：新增1包，改7包；清掉旧副材的有效发放 |
| Drop/Drop_dungeon.xlsx | 19个映射首通包的箱子ID/数量，外加无限之旅23000004钥匙1→2 |
| Drop/Drop_mainlevel.xlsx | 11000012的钥匙行ShowItemID 101→25，实际5把已正确 |
| items/Items.xlsx | 仅4375.Description改成固定1件10级金装；开箱规则已正确 |

本次只生成核对清单，未写任何06或SVN工作簿，未提交SVN，未执行Luban或客户端/服务端验收。

## 一、章节挂载

| 章节ID | 字段 | SVN当前 | 06目标 | SVN单元格 |
|---|---|---|---|---|
| 1 | JottingsTasks | 21;22;23;25 | 21;22;23;24;25 | D5 |
| 2 | JottingsTasks | 31;32;33;34 | 31;32;33;34;35;36 | D6 |

JottingsTask的56个组与TaskID列表已一致，不新增或重编号。第1章补组24，第2章补组35、36。

## 二、Task本体与TaskTarget目标

TaskId和TargetId均复用现有记录；不要新增重复任务。下表只列有差异的字段，未列出的字段保持SVN原值。日周任务及那9条曾被否决的UnlockId不在修改范围。

### task/Task.xlsx

| ID | 字段 | SVN当前 | 06目标 | SVN单元格 |
|---|---|---|---|---|
| 1315 | TaskName | 房车达到2级 | 1个舱室达到2级 | C192 |
| 1315 | TaskDesc | 房车达到2级 | 1个舱室达到2级 | D192 |
| 1315 | DropId | 空 | 1030205 | P192 |
| 1327 | TaskName | 房车达到3级 | 收集4件5级的映射装备 | C201 |
| 1327 | TaskDesc | 房车达到3级 | 收集4件5级的映射装备 | D201 |
| 1327 | DropId | 空 | 1030307 | P201 |
| 1328 | TaskName | 2个设备达到2级 | 2个舱室达到2级 | C202 |
| 1328 | TaskDesc | 2个设备达到2级 | 2个舱室达到2级 | D202 |
| 1328 | DropId | 空 | 1030304 | P202 |
| 1338 | TaskName | 1个设备达到2级 | 1个舱室达到3级 | C210 |
| 1338 | TaskDesc | 1个设备达到2级 | 1个舱室达到3级 | D210 |
| 1339 | TaskName | 收集4件10级的装备 | 收集4件10级的映射装备 | C211 |
| 1339 | TaskDesc | 收集4件10级的装备 | 收集4件10级的映射装备 | D211 |
| 1348 | TaskName | 2个设备达到2级 | 2个舱室达到3级 | C219 |
| 1348 | TaskDesc | 2个设备达到2级 | 2个舱室达到3级 | D219 |
| 1349 | TaskName | 收集8件15级的装备 | 收集8件15级的映射装备 | C220 |
| 1349 | TaskDesc | 收集8件15级的装备 | 收集8件15级的映射装备 | D220 |
| 1381 | TaskName | 收集8件25级的装备 | 收集8件25级的映射装备 | C230 |
| 1381 | TaskDesc | 收集8件25级的装备 | 收集8件25级的映射装备 | D230 |
| 1401 | TaskName | 1个设备达到3级 | 1个舱室达到4级 | C194 |
| 1401 | TaskDesc | 1个设备达到3级 | 1个舱室达到4级 | D194 |
| 1384 | TaskName | 收集8件35级的装备 | 收集8件35级的映射装备 | C241 |
| 1384 | TaskDesc | 收集8件35级的装备 | 收集8件35级的映射装备 | D241 |
| 1388 | TaskName | 收集8件40级的装备 | 收集8件45级的映射装备 | C253 |
| 1388 | TaskDesc | 收集8件40级的装备 | 收集8件45级的映射装备 | D253 |

### task/TaskTarget.xlsx

| ID | 字段 | SVN当前 | 06目标 | SVN单元格 |
|---|---|---|---|---|
| 1315 | TargetDesc | 房车达到2级 | 1个舱室达到2级 | C175 |
| 1315 | TargetType | Target_TTT_Rv_Level | Target_TTT_RvCabin_LevelUp_Num | D175 |
| 1315 | ParamList | 0,2 | 2,1 | E175 |
| 1315 | TaskAccessList | 48 | 51 | I175 |
| 1327 | TargetDesc | 房车达到3级 | 收集4件5级的映射装备 | C184 |
| 1327 | TargetType | Target_TTT_Rv_Level | Target_TTT_SpecialEquipmentLevelUp_Num | D184 |
| 1327 | ParamList | 0,3 | 5,4 | E184 |
| 1327 | TaskAccessList | 48 | 14 | I184 |
| 1328 | TargetDesc | 2个设备达到2级 | 2个舱室达到2级 | C185 |
| 1338 | TargetDesc | 1个设备达到2级 | 1个舱室达到3级 | C193 |
| 1338 | ParamList | 2,1 | 3,1 | E193 |
| 1339 | TargetDesc | 收集4件10级的装备 | 收集4件10级的映射装备 | C194 |
| 1348 | TargetDesc | 2个设备达到2级 | 2个舱室达到3级 | C202 |
| 1348 | ParamList | 2,2 | 3,2 | E202 |
| 1349 | TargetDesc | 收集8件15级的装备 | 收集8件15级的映射装备 | C203 |
| 1381 | TargetDesc | 收集8件25级的装备 | 收集8件25级的映射装备 | C213 |
| 1384 | TargetDesc | 收集8件35级的装备 | 收集8件35级的映射装备 | C224 |
| 1388 | TargetDesc | 收集8件40级的装备 | 收集8件45级的映射装备 | C236 |
| 1388 | ParamList | 40,8 | 45,8 | E236 |
| 1401 | TargetDesc | 1个设备达到3级 | 1个舱室达到4级 | C177 |
| 1401 | ParamList | 3,1 | 4,1 | E177 |

## 三、Drop_other章节奖励

| DropId | SVN当前奖励 | 06目标奖励 | 处理 |
|---|---|---|---|
| 1030205 | 无 | 3028×2 | 新增1行 |
| 1030304 | 1×30000 | 3028×3 | 修改现有行 |
| 1030307 | 13×20000 | 25×3 | 修改现有行 |
| 1030407 | 1152×1；1153×1；1154×1；1155×1 | 25×3 | 替换奖励，停用多余旧行 |
| 1030507 | 1152×1；1153×1；1154×1；1155×1 | 25×3 | 替换奖励，停用多余旧行 |
| 1030607 | 1152×2；1153×2；1154×2；1155×2 | 25×3 | 替换奖励，停用多余旧行 |
| 1030707 | 1152×2；1153×2；1154×2；1155×2 | 25×3 | 替换奖励，停用多余旧行 |
| 1030807 | 1152×3；1153×3；1154×3；1155×3 | 25×3 | 替换奖励，停用多余旧行 |

所有新目标行均为fixed_，DropId2=0，包次数1/1，物品Min/Max一致，权重10000。六条映射任务奖励均为25×3，不保留副材；仅追加钥匙而不处理旧行，会同时发放副材。章节完成奖7个包及日周活跃钥匙3个包已经一致，不重复改。

多余15条副材行可在首列标记`##`停用，避免删除行导致ID公式移位：

| DropId | SVN行 | 原道具 | 首列目标 |
|---|---|---|---|
| 1030407 | 503 | 1153 | ## |
| 1030407 | 504 | 1154 | ## |
| 1030407 | 505 | 1155 | ## |
| 1030507 | 507 | 1153 | ## |
| 1030507 | 508 | 1154 | ## |
| 1030507 | 509 | 1155 | ## |
| 1030607 | 511 | 1153 | ## |
| 1030607 | 512 | 1154 | ## |
| 1030607 | 513 | 1155 | ## |
| 1030707 | 515 | 1153 | ## |
| 1030707 | 516 | 1154 | ## |
| 1030707 | 517 | 1155 | ## |
| 1030807 | 519 | 1153 | ## |
| 1030807 | 520 | 1154 | ## |
| 1030807 | 521 | 1155 | ## |

## 四、Drop_dungeon映射首通与无限之旅

以下19个映射首通包只调整箱子；各包钥匙及材料保持现有值。第一、二层与后续层箱子按06逐包同步；第3层20000012已正确发25×1和4375×1，不再改。

| 层数 | DropId | SVN有差异的箱子 | 06目标箱子 | SVN行/操作 |
|---|---|---|---|---|
| 1 | 20000010 | 4202×1 | 4201×1 | 731 |
| 2 | 20000011 | 4207×1 | 4206×1 | 733 |
| 7 | 20000016 | 无 | 4232×1 | 新增箱子行 |
| 8 | 20000017 | 4237×2 | 4237×1 | 746 |
| 9 | 20000018 | 4242×2 | 4242×1 | 748 |
| 10 | 20000019 | 4247×1 | 4248×1 | 750 |
| 11 | 20000020 | 无 | 4253×1 | 新增箱子行 |
| 12 | 20000021 | 4257×2 | 4258×1 | 755 |
| 13 | 20000022 | 4262×1 | 4263×1 | 757 |
| 16 | 20000025 | 无 | 4278×1 | 新增箱子行 |
| 19 | 20000028 | 4293×2 | 4293×1 | 772 |
| 20 | 20000029 | 4298×1 | 4299×1 | 774 |
| 21 | 20000030 | 无 | 4304×1 | 新增箱子行 |
| 22 | 20000031 | 4308×2 | 4309×1 | 779 |
| 23 | 20000032 | 4313×1 | 4314×1 | 781 |
| 24 | 20000033 | 4318×2 | 4319×1 | 784 |
| 25 | 20000034 | 4323×1 | 4325×1 | 786 |
| 26 | 20000035 | 无 | 4329×1 | 新增箱子行 |
| 28 | 20000037 | 4338×2 | 4339×1 | 793 |

无限之旅：普通难度4000分对应DropId23000004，Item25在SVN第2735行的L/M列均由1改2；其余19个钥匙节点已各2把，不动。四难度每档5个钥匙节点，因此补齐后每难度10把/周，日周任务31把/周，共41把/周；实际领取仍以四难度互斥规则为前提。

## 五、主线36星与4375说明

Drop_mainlevel：11000012（第二章36星）已经固定发25×5，不要再追加钥匙。仅把该钥匙行O976（ShowItemID）从101改25。

Items：4375的K484（Description）改为“开启后固定获得1件10级金色映射装备。”。当前旧描述还写5级或10级随机；实际Generate4375已是10级、Orange、固定1件，生成表无需再改。

## 六、所有修改单元格

下面是现有纯数据格的精确新旧值，已独立复读其SVN地址；未发现目标单元格为公式。行号只适用于本次r40473核对快照，操作前先按ID重新定位。

| SVN文件 | 业务ID | 字段 | 单元格 | 当前值 | 目标值 |
|---|---|---|---|---|---|
| task/Jottings.xlsx | 1 | JottingsTasks | D5 | 21;22;23;25 | 21;22;23;24;25 |
| task/Jottings.xlsx | 2 | JottingsTasks | D6 | 31;32;33;34 | 31;32;33;34;35;36 |
| task/Task.xlsx | 1315 | TaskName | C192 | 房车达到2级 | 1个舱室达到2级 |
| task/Task.xlsx | 1315 | TaskDesc | D192 | 房车达到2级 | 1个舱室达到2级 |
| task/Task.xlsx | 1315 | DropId | P192 | 空 | 1030205 |
| task/Task.xlsx | 1327 | TaskName | C201 | 房车达到3级 | 收集4件5级的映射装备 |
| task/Task.xlsx | 1327 | TaskDesc | D201 | 房车达到3级 | 收集4件5级的映射装备 |
| task/Task.xlsx | 1327 | DropId | P201 | 空 | 1030307 |
| task/Task.xlsx | 1328 | TaskName | C202 | 2个设备达到2级 | 2个舱室达到2级 |
| task/Task.xlsx | 1328 | TaskDesc | D202 | 2个设备达到2级 | 2个舱室达到2级 |
| task/Task.xlsx | 1328 | DropId | P202 | 空 | 1030304 |
| task/Task.xlsx | 1338 | TaskName | C210 | 1个设备达到2级 | 1个舱室达到3级 |
| task/Task.xlsx | 1338 | TaskDesc | D210 | 1个设备达到2级 | 1个舱室达到3级 |
| task/Task.xlsx | 1339 | TaskName | C211 | 收集4件10级的装备 | 收集4件10级的映射装备 |
| task/Task.xlsx | 1339 | TaskDesc | D211 | 收集4件10级的装备 | 收集4件10级的映射装备 |
| task/Task.xlsx | 1348 | TaskName | C219 | 2个设备达到2级 | 2个舱室达到3级 |
| task/Task.xlsx | 1348 | TaskDesc | D219 | 2个设备达到2级 | 2个舱室达到3级 |
| task/Task.xlsx | 1349 | TaskName | C220 | 收集8件15级的装备 | 收集8件15级的映射装备 |
| task/Task.xlsx | 1349 | TaskDesc | D220 | 收集8件15级的装备 | 收集8件15级的映射装备 |
| task/Task.xlsx | 1381 | TaskName | C230 | 收集8件25级的装备 | 收集8件25级的映射装备 |
| task/Task.xlsx | 1381 | TaskDesc | D230 | 收集8件25级的装备 | 收集8件25级的映射装备 |
| task/Task.xlsx | 1401 | TaskName | C194 | 1个设备达到3级 | 1个舱室达到4级 |
| task/Task.xlsx | 1401 | TaskDesc | D194 | 1个设备达到3级 | 1个舱室达到4级 |
| task/Task.xlsx | 1384 | TaskName | C241 | 收集8件35级的装备 | 收集8件35级的映射装备 |
| task/Task.xlsx | 1384 | TaskDesc | D241 | 收集8件35级的装备 | 收集8件35级的映射装备 |
| task/Task.xlsx | 1388 | TaskName | C253 | 收集8件40级的装备 | 收集8件45级的映射装备 |
| task/Task.xlsx | 1388 | TaskDesc | D253 | 收集8件40级的装备 | 收集8件45级的映射装备 |
| task/TaskTarget.xlsx | 1315 | TargetDesc | C175 | 房车达到2级 | 1个舱室达到2级 |
| task/TaskTarget.xlsx | 1315 | TargetType | D175 | Target_TTT_Rv_Level | Target_TTT_RvCabin_LevelUp_Num |
| task/TaskTarget.xlsx | 1315 | ParamList | E175 | 0,2 | 2,1 |
| task/TaskTarget.xlsx | 1315 | TaskAccessList | I175 | 48 | 51 |
| task/TaskTarget.xlsx | 1327 | TargetDesc | C184 | 房车达到3级 | 收集4件5级的映射装备 |
| task/TaskTarget.xlsx | 1327 | TargetType | D184 | Target_TTT_Rv_Level | Target_TTT_SpecialEquipmentLevelUp_Num |
| task/TaskTarget.xlsx | 1327 | ParamList | E184 | 0,3 | 5,4 |
| task/TaskTarget.xlsx | 1327 | TaskAccessList | I184 | 48 | 14 |
| task/TaskTarget.xlsx | 1328 | TargetDesc | C185 | 2个设备达到2级 | 2个舱室达到2级 |
| task/TaskTarget.xlsx | 1338 | TargetDesc | C193 | 1个设备达到2级 | 1个舱室达到3级 |
| task/TaskTarget.xlsx | 1338 | ParamList | E193 | 2,1 | 3,1 |
| task/TaskTarget.xlsx | 1339 | TargetDesc | C194 | 收集4件10级的装备 | 收集4件10级的映射装备 |
| task/TaskTarget.xlsx | 1348 | TargetDesc | C202 | 2个设备达到2级 | 2个舱室达到3级 |
| task/TaskTarget.xlsx | 1348 | ParamList | E202 | 2,2 | 3,2 |
| task/TaskTarget.xlsx | 1349 | TargetDesc | C203 | 收集8件15级的装备 | 收集8件15级的映射装备 |
| task/TaskTarget.xlsx | 1381 | TargetDesc | C213 | 收集8件25级的装备 | 收集8件25级的映射装备 |
| task/TaskTarget.xlsx | 1384 | TargetDesc | C224 | 收集8件35级的装备 | 收集8件35级的映射装备 |
| task/TaskTarget.xlsx | 1388 | TargetDesc | C236 | 收集8件40级的装备 | 收集8件45级的映射装备 |
| task/TaskTarget.xlsx | 1388 | ParamList | E236 | 40,8 | 45,8 |
| task/TaskTarget.xlsx | 1401 | TargetDesc | C177 | 1个设备达到3级 | 1个舱室达到4级 |
| task/TaskTarget.xlsx | 1401 | ParamList | E177 | 3,1 | 4,1 |
| Drop/Drop_other.xlsx | 1030304 | DropItem_id | K142 | 1 | 3028 |
| Drop/Drop_other.xlsx | 1030304 | DropItemNumMin | L142 | 30000 | 3 |
| Drop/Drop_other.xlsx | 1030304 | DropItemNumMax | M142 | 30000 | 3 |
| Drop/Drop_other.xlsx | 1030307 | DropItem_id | K145 | 13 | 25 |
| Drop/Drop_other.xlsx | 1030307 | DropItemNumMin | L145 | 20000 | 3 |
| Drop/Drop_other.xlsx | 1030307 | DropItemNumMax | M145 | 20000 | 3 |
| Drop/Drop_other.xlsx | 1030407 | DropItem_id | K502 | 1152 | 25 |
| Drop/Drop_other.xlsx | 1030407 | DropItemNumMin | L502 | 1 | 3 |
| Drop/Drop_other.xlsx | 1030407 | DropItemNumMax | M502 | 1 | 3 |
| Drop/Drop_other.xlsx | 1030507 | DropItem_id | K506 | 1152 | 25 |
| Drop/Drop_other.xlsx | 1030507 | DropItemNumMin | L506 | 1 | 3 |
| Drop/Drop_other.xlsx | 1030507 | DropItemNumMax | M506 | 1 | 3 |
| Drop/Drop_other.xlsx | 1030607 | DropItem_id | K510 | 1152 | 25 |
| Drop/Drop_other.xlsx | 1030607 | DropItemNumMin | L510 | 2 | 3 |
| Drop/Drop_other.xlsx | 1030607 | DropItemNumMax | M510 | 2 | 3 |
| Drop/Drop_other.xlsx | 1030707 | DropItem_id | K514 | 1152 | 25 |
| Drop/Drop_other.xlsx | 1030707 | DropItemNumMin | L514 | 2 | 3 |
| Drop/Drop_other.xlsx | 1030707 | DropItemNumMax | M514 | 2 | 3 |
| Drop/Drop_other.xlsx | 1030807 | DropItem_id | K518 | 1152 | 25 |
| Drop/Drop_dungeon.xlsx | 23000004 | DropItemNumMin | L2735 | 1 | 2 |
| Drop/Drop_dungeon.xlsx | 23000004 | DropItemNumMax | M2735 | 1 | 2 |
| Drop/Drop_mainlevel.xlsx | 11000012 | ShowItemID | O976 | 101 | 25 |
| Drop/Drop_dungeon.xlsx | 20000010 | DropItem_id | K731 | 4202 | 4201 |
| Drop/Drop_dungeon.xlsx | 20000011 | DropItem_id | K733 | 4207 | 4206 |
| Drop/Drop_dungeon.xlsx | 20000017 | DropItemNumMin | L746 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000017 | DropItemNumMax | M746 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000018 | DropItemNumMin | L748 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000018 | DropItemNumMax | M748 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000019 | DropItem_id | K750 | 4247 | 4248 |
| Drop/Drop_dungeon.xlsx | 20000021 | DropItem_id | K755 | 4257 | 4258 |
| Drop/Drop_dungeon.xlsx | 20000021 | DropItemNumMin | L755 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000021 | DropItemNumMax | M755 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000022 | DropItem_id | K757 | 4262 | 4263 |
| Drop/Drop_dungeon.xlsx | 20000028 | DropItemNumMin | L772 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000028 | DropItemNumMax | M772 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000029 | DropItem_id | K774 | 4298 | 4299 |
| Drop/Drop_dungeon.xlsx | 20000031 | DropItem_id | K779 | 4308 | 4309 |
| Drop/Drop_dungeon.xlsx | 20000031 | DropItemNumMin | L779 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000031 | DropItemNumMax | M779 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000032 | DropItem_id | K781 | 4313 | 4314 |
| Drop/Drop_dungeon.xlsx | 20000033 | DropItem_id | K784 | 4318 | 4319 |
| Drop/Drop_dungeon.xlsx | 20000033 | DropItemNumMin | L784 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000033 | DropItemNumMax | M784 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000034 | DropItem_id | K786 | 4323 | 4325 |
| Drop/Drop_dungeon.xlsx | 20000037 | DropItem_id | K793 | 4338 | 4339 |
| Drop/Drop_dungeon.xlsx | 20000037 | DropItemNumMin | L793 | 2 | 1 |
| Drop/Drop_dungeon.xlsx | 20000037 | DropItemNumMax | M793 | 2 | 1 |
| items/Items.xlsx | 4375 | Description | K484 | 本层首通可获得1个标准装备补给箱，开启后随机获得1件5级或10级金色映射装备。 | 开启后固定获得1件10级金色映射装备。 |

## 七、需要手工新增的6行

5行补缺失首通箱，1行新增第一章舱室奖励包。不要直接复制候选B列行ID，不要自动插入或删除公式所在行；在正式表尾部准备新行后，按正式表规则维护ID及DropId公式。

| SVN文件 | DropId | 道具 | 数量Min/Max | DropId2 | DropType | 包次数Min/Max | 权重 | ShowItemID |
|---|---|---|---|---|---|---|---|---|
| Drop/Drop_other.xlsx | 1030205 | 3028 | 2/2 | 0 | fixed_ | 1/1 | 10000 | 空 |
| Drop/Drop_dungeon.xlsx | 20000016 | 4232 | 1/1 | 0 | fixed_ | 1/1 | 10000 | 空 |
| Drop/Drop_dungeon.xlsx | 20000020 | 4253 | 1/1 | 0 | fixed_ | 1/1 | 10000 | 空 |
| Drop/Drop_dungeon.xlsx | 20000025 | 4278 | 1/1 | 0 | fixed_ | 1/1 | 10000 | 空 |
| Drop/Drop_dungeon.xlsx | 20000030 | 4304 | 1/1 | 0 | fixed_ | 1/1 | 10000 | 空 |
| Drop/Drop_dungeon.xlsx | 20000035 | 4329 | 1/1 | 0 | fixed_ | 1/1 | 10000 | 空 |

## 八、不需要同步或不能整表覆盖的内容

- 玩家等级10/20/25/30/33/36/38已在SVN，其他未列出的章节目标不改。JottingsTask共56组已一致。
- 每日80活跃3把、每周20/40活跃4/6把、月签5/12/19/26日各2把已正确；DailyActiveReward、WeeklyReward、DailySign无需再改。
- 映射UIlevel的150行FirstReward/Reward/FirstRewardDrop/FallRewardDrop已一致；116个常规及子掉落包、151条开箱规则也一致，不重刷这些表。
- NR_HighestScoreReward按“难度+分数”对齐后40个节点均一致。SVN采用1～10、101～110、201～210、301～310；06采用1～40，不能为了追求表面一致改正式ID。
- Items候选的品质名Green/Blue/Purple/Orange/Red与SVN数值1～5是编码表示差异。候选还有通用素材名称/图标/描述、空ItemSubType等范围外差异，保留SVN现有正式字段；本次Items只列4375.Description。
- 06中的00_配置清单、中文说明、校验JSON是交付辅助内容，不复制到Datas业务表；Task的候选和SVN列位置并不完全相同，应按字段名贴值。

## 九、落表顺序与验收

1. 备份这7张SVN源表，先按ID准备6条新增Drop行；更新奖励并停用15条旧副材行。
2. 同步TaskTarget、Task和Jottings，最后改4375说明与主线钥匙预览。
3. 复查实际挂载7章/56组/69条，第二至七章映射任务各25×3且无副材；第一、二章舱室各3028×2/×3。
4. 复查30层首通匙1/箱1，第三层4375固定10级金装；普通难度4000分钥匙2把；36星只发5把。
5. 使用正式工程Luban导出并检查引用；联调任务持有量初始化、进度、章节奖励领取与周奖励互斥。静态相等不能替代这些运行验收。

## 复核证据

原始字段对比见同目录raw-comparison.json；精确修改与新增/停用计划见landing-plan.json；独立单元格核对与只读保护见validation.json。没有执行落表。
