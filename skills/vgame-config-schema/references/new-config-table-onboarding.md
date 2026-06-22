# New Config Table Onboarding

Use this when Vgame adds, registers, renames, relocates, or classifies a new source config table.

## Required Flow

1. Confirm the new table's player-facing purpose and owning system.
2. Place the source workbook under the correct `D:\Vgame\Config\GameConfig\Datas\<domain>` directory.
3. Ensure the workbook file name is unique under `Datas`; export flattens files into `TempDatas`, so duplicate file names are unsafe even in different folders.
4. Follow the Vgame header convention:
   - row 1: `##var` field names
   - row 2: `##type` field types
   - row 3: `##group` export groups
   - row 4: `##` planning comments
   - row 5+: data
5. If the table introduces a new compound field, update `__beans__.xlsx`.
6. If the table introduces a new enum, update `__enums__.xlsx`.
7. Register the logical table in `__tables__.xlsx`:
   - `full_name`: logical table name
   - `value_type`: DataModel type
   - `read_schema_from_file`: normally true when schema comes from the Excel headers
   - `input`: source workbook file name; multiple files only when one logical table intentionally merges inputs
   - `gen_csharp_class`, `index`, `mode`, `group`, `comment`, `output`: follow nearby table conventions
8. Confirm `__tables__.xlsx input -> Datas actual path` resolves with no missing or duplicate file-name ambiguity.
9. Classify the table's role and key relationships using field names/types:
   - `ItemId`, `PropType`, `Price`, `CostItem` -> `Items`
   - `DropId`, `RewardId`, `CommonReward`, `FirstRewardDrop` -> logical `Drop`
   - `Unlock`, `UnlockId` -> `Unlock`
   - `SystemId`, `JumpId`, `GotoId`, `UIViewName` -> `SystemOpen` or UI jump
   - `LevelId`, `LevelType`, `ChapterId` -> level/progression tables
   - `TaskId`, `ActivityId`, `ShopId`, `DrawId`, `PayProductId` -> their matching system tables
10. Refresh or update:
   - `D:\数值文档\策划agent\项目专属\Vgame\output\config-table-application-summary.md`
   - `D:\数值文档\策划agent\项目专属\Vgame\output\config-table-role-relationship-map.md`
11. Update the relevant project skill if the new table creates a new route:
   - rewards/Drop/UIlevel -> `vgame-reward-drop-sync`
   - resource source/sink -> `vgame-economy-source-map`
   - LevelId/LevelType/Unlock/SystemOpen -> `vgame-level-progression-map`
   - schema/export/validation -> `vgame-config-schema`
12. Validate with the narrowest export/check command the task allows.

## Output Contract

For every new table onboarding task, report:

| Item | Required content |
|---|---|
| Source workbook | Actual `Datas` path and sheet |
| Logical table | `__tables__.xlsx` row fields |
| Schema | Key fields, field types, new beans/enums |
| Role | System category and player-facing purpose |
| Relationships | Item/Drop/Unlock/SystemOpen/Level/Task/Shop/Activity/Pay references |
| Generated output | Expected JSON/code output target |
| Documentation | Whether the application and relationship maps were updated |
| Validation | Export/check command or manual validation gap |

Use `待确认` for any relationship not directly observed.

## Hard Rules

- Do not treat generated `server_json` as the source of truth.
- Do not add a new Excel file without `__tables__.xlsx` registration when it is meant to export through Luban.
- Do not add duplicate workbook file names under `Datas`.
- Do not classify historical or draft gameplay as formal gameplay just because a table is registered.
- Do not skip updating the application/relationship maps; they are the project index for future agents.
