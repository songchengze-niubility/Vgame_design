# MD 参数契约

## 权威关系

```text
01_源表 / 正式配置 / 用户输入
        ↓ 事实与决策证据
03_沉淀MD（唯一参数与公式权威）
        ↓
本次生成物 → 全新 04 staging（派生交付物）
        ↓
05_验算核算 → 发布正式 04 → 复验
```

`_shared/共享参数.xlsx` 与养成、战斗、经济、节奏目录中的 `参数.xlsx` 已在 2026-07-10 完成逐格迁移和 MD-only 回归后删除。

## 参数块

五个参数域分别位于 `03_沉淀MD/参数基线/*.md`，每个文件只允许一个由以下标记包围的 JSON 块：

````text
<!-- VGAME_PARAMETER_JSON_BEGIN -->
```json
{"schema": "vgame-parameter-workbook/v1", "scope": "养成", "sheets": []}
```
<!-- VGAME_PARAMETER_JSON_END -->
````

- 稳定参数 ID：`<参数域>/<Sheet>!<Cell>`。
- 普通单元格直接保存 JSON 标量。
- 旧公式单元格保存为 `{"formula":"=...","value":确定值}`；生成器读取 `value`，公式用于追踪语义。
- 公式变化时，必须同时更新 `formula` 和经确认的 `value`，不得依赖 Excel 缓存或外部工作簿重算。
- 人读说明写在参数块外；不得在块外再维护第二份同名权威值。

## 修改流程

1. 读全局源表、正式配置、用户输入和已有系统沉淀。
2. 记录受影响参数 ID、旧值、新值、公式、来源证据和下游终稿位置。
3. 用户确认后修改唯一 MD 参数块或对应系统沉淀章节。
4. 刷新生成物并组装全新 staging；不得把旧 `04` 当模板或输入。
5. 完成公式重算，运行 `validate_rebuild.py` 与 `check_final_document_independence.py`；通过后发布并对正式 `04` 复验。

## 迁移与兼容

- `02_AI规则/check_md_parameters.py` 校验五域 MD 参数块与内存工作簿读取结果；旧参数表不再参与任何门禁。
- `_shared/md_parameter_reader.py` 把 MD 参数块还原为内存工作簿，使旧生成器只替换读取层即可继续复现。
- 不得从最终 Excel 反向覆盖 MD；若终稿与 MD 冲突，先登记变更并由用户裁决。
- 最终 Excel 不是紧急参数入口；需要变更时先修正所有权对应的源表或 MD，再执行全量重建。
