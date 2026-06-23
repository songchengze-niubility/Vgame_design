---
name: vgame-config-schema
description: Use for Vgame configuration-source discovery, Excel schema reading, Luban table mapping, generated JSON/code export tracing, new config table onboarding, and config validation. Trigger when a task mentions Vgame config files, Datas Excel, server_json, Luban, __tables__.xlsx, __beans__.xlsx, __enums__.xlsx, Drop/UIlevel schemas, source-vs-generated decisions, adding/registering a new config table, or asks which table/field/export/check command should be used.
---

# Vgame Config Schema

Use this skill to decide where a Vgame config fact comes from, how an Excel source table becomes runtime config, and how a config change should be verified.

## Load Order

1. Read `vgame-core-understanding` first when the task needs project context.
2. Read `references/config-pipeline.md` for source paths, generated paths, and export commands.
3. Read `references/schema-map.md` when the task involves table names, fields, enum/bean types, or logical table inputs.
4. Read `references/new-config-table-onboarding.md` when adding, registering, relocating, or classifying a new config table.
5. Read `references/validation.md` before declaring a config change ready.
6. If the task is specifically about rewards, DropId, first-clear rewards, repeat drops, or UI preview rewards, use `vgame-reward-drop-sync` after this skill.

## Operating Rules

- Treat `${VGAME_ROOT}\Config\GameConfig\Datas` as the source Excel root.
- Treat `${VGAME_ROOT}\Config\GameConfig\server_json` as generated output, not a source of truth to edit.
- Confirm the logical table in `__tables__.xlsx` before editing a source file. Some logical tables merge multiple Excel files.
- For any new config table, register it through `__tables__.xlsx`, confirm the actual `Datas` path, and update the config table application/relationship maps.
- Read row 1 `##var`, row 2 `##type`, row 3 `##group`, and row 4 comments before changing any Excel table.
- Preserve formulas, row ordering conventions, existing enum strings, and source grouping unless the user explicitly requests a schema migration.
- For every proposed config change, report source workbook, sheet, key field, old value, new value, generated output, and validation method.

## Formula Safety Rules (Critical)

Datas 配表中存在公式列，写入时必须遵守以下规则：

### 已知含公式的配表

| 表 | 公式列 | 公式内容 | 风险 |
|---|---|---|---|
| `Drop_dungeon.xlsx` | Col 2 (ID) | `=ROW()+200000-4` | 插入/删除行会导致所有ID错位 |
| `Drop_dungeon.xlsx` | Col 3 (DropId) | `=C<prev>+1` 等相对引用 | 改前行会影响后续行 |
| `Drop_dungeon.xlsx` | Col 6 (DropId2) | `=F<n>+3` 等偏移引用 | 同上 |
| `MonsterAttribute.xlsx` | Col 7 (MagicAttack) | `=F<row>` (=PhysicsAttack) | 直接写值会断开联动 |
| `Monster.xlsx` | Col 6 (##注释) | VLOOKUP 到 @Desc1 | 注释列不导出，风险低 |

### 写入安全协议

1. **写入前必须用 `data_only=False` 打开目标文件，扫描目标单元格是否为公式**
2. **如果目标单元格是公式 → 绝不覆写，改为输出手动修改指令给用户**
3. **如果目标单元格是纯值 → 可以安全写入**
4. **绝不执行 insert_rows / delete_rows / insert_cols / delete_cols** — 会导致 ROW() 等公式错位
5. **绝不修改公式列的值** — 即使想写入"正确结果"也不行，公式关系比当前值更重要
6. **写入时使用 `data_only=False` 模式**（保留其他单元格的公式原样）
7. **只修改明确安全的列**（已确认为纯数据的列）

### 需要新增行时的处理

如果配置变更需要新增行（如新增 Drop 条目），不能自动操作，必须输出手动指令：

```
[需要手动操作]
文件: Datas\Drop\Drop_dungeon.xlsx
操作: 在第 N 行后新增 M 行（使用 Excel/WPS 的"插入行"功能）
原因: ID 列使用 ROW() 公式，插入行后公式会自动更新为正确值
插入后需填入的数据:
  Row X, Col G: "首通金币"
  Row X, Col K: 1
  Row X, Col L: 10000
  ...
```

### 安全写入的列（已验证）

| 表 | 可安全写入的列 | 说明 |
|---|---|---|
| `Drop_dungeon.xlsx` | Col 7+(DropType, DropMinNum, DropMaxNum, DropItem_id, DropItemNumMin, DropItemNumMax, DropWeight, ShowItemID, IsValid) | 第7列起全部是纯数据 |
| `UIlevel.xlsx` | 全部列 | 无公式 |
| `level.xlsx` | 全部列 | 无公式 |
| `MonsterAttribute.xlsx` | 除 Col 7 (MagicAttack) 外 | Col 7 是 =PhysicsAttack 公式 |
| `Monster.xlsx` | 除 Col 6 (注释) 外 | Col 6 是 VLOOKUP 但不导出 |

## Default Workflow

1. Identify the target behavior, player-facing system, and candidate config names.
2. Use `__tables__.xlsx` to map the logical table to source workbook names.
3. Locate the actual workbook under `Datas`; do not assume the path from the file name alone.
4. Inspect headers and nearby rows before making claims about fields or formats.
5. Check `__beans__.xlsx` for compound field formats and `__enums__.xlsx` for enum values.
6. If editing, back up the source workbook first.
7. Export with the narrowest appropriate command, then run validation.
8. Put the result into a config impact matrix.

## Output Contract

When answering a config question, include:

- `Source`: exact source workbook and sheet.
- `Schema`: relevant fields and types.
- `Generated`: expected JSON/code output target.
- `Risk`: references, economy impact, UI preview impact, or validation gaps.
- `Verify`: command or manual check needed.

Use `待确认` for any field, source, or reference path that was not directly observed.
