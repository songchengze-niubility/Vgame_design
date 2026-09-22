---
id: EXP-20260914-01
date: 2026-09-14
title: openpyxl 重序列化会丢公式缓存值，Luban 导出报"字段不能为空"
category: process
tags: 配置表, xlsx, openpyxl, Luban, 公式, 候选文件
triggerTerms: 用openpyxl改配置表后Luban导出失败; 字段不能为空 DropDataModel.ID; excel候选文件导出报错; openpyxl 保存后公式变空; Drop_dungeon B5 空
status: active
source: 映射装备开箱品质调整（向下开方案）落 SVN，2026-09-14
refs: output/映射装备开箱品质调整/05-验证核算/scripts/patch_xml_v5.py; skills/vgame-reward-drop-sync/SKILL.md
---

## 现象

用 openpyxl（`load_workbook(data_only=False)` → 改单元格 → `save`）生成配置候选并写入 SVN 后，
Luban 导出直接失败：

```
[LUBAN] 文件: Drop@...\TempDatas\Drop_dungeon.xlsx
[LUBAN] 位置: Sheet:Drop 字段:ID 位置:[B:5]
[LUBAN] Err:  字段不能为空  字段: {DropDataModel}.ID
```

B5 是公式列 `=ROW()+200000-4`，导出器读的是公式的**缓存计算值**，而 openpyxl 保存时不写缓存值，
导致所有公式单元格在读缓存的一方看来全是空。

## 根因

openpyxl 不计算公式，保存时会剥离 `<c>` 里的 `<v>` 缓存值，只保留 `<f>`。
"逐格对比公式字符串一致"的验证掩盖了这一点——公式确实没变，变的是它的缓存值。
任何"读缓存值"的下游（Luban/ExcelDataReader/部分服务器导表脚本）都会踩空。

## 处理

1. 从备份回滚 SVN 工作副本。
2. 改用**外科手术式 XML 补丁**：zipfile 直接改 xlsx 内的 sheet XML，只替换目标单元格
   （数值格换 `<v>`；字符串格复用/追加 sharedStrings 并改索引），公式格与其缓存值原样保留。
3. 验证三件套：`data_only=True` 读公式格必须返回数字（缓存还在）；
   值级全表 diff 必须恰好等于目标格集合；公式格仍以 `=` 开头。
4. 重跑 Luban 导出并在生成 json 里抽查新值。

## 规则化建议

- **任何含公式列的 Vgame 配置表，禁止用 openpyxl 整簿重序列化生成候选/落表**；
  逐格值验证必须额外包含"公式缓存值仍在"这一项（只验公式字符串不够）。
- 信号：候选文件比源文件 zip 条目数变少、或 Luban/导表报"字段不能为空"且定位在公式列 → 立即怀疑本坑。
- 参考实现：`output/映射装备开箱品质调整/05-验证核算/scripts/patch_xml_v5.py`（补丁）
  与 `verify_patch_v5.py`（三件套验证）。
