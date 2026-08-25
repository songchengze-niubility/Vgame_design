# 02_AI规则

这里放 AI 如何读取、增加、修改数值框架的规则。正式参数从 `03_沉淀MD/参数基线` 读取，不再从参数工作簿读取。

建议内容：

- `表结构说明.md`：每张源表的 sheet、字段、单位、引用关系。
- `模块读写规则.md`：养成、经济、节奏、战斗四条主链路分别读写哪些资料；奖励、掉落、概率归属到具体玩法/系统模块，经济总账后置汇总。
- `MD参数契约.md`：MD 机器参数块、稳定参数 ID、公式缓存与变更同步规则。
- `sync_global_sources_to_md.py`：校验或同步 `01_源表` 拥有的全局事实与派生字段；默认只检查，只有 `--write` 才修改 MD。
- `check_md_parameters.py`：校验五域 MD 参数块可解析且可被生成器加载。
- `check_final_document_independence.py`：检查最终 Excel 是否含外链、数据连接、参数表引用或明显公式错误。
- `stage_final_documents_from_md.py`：从本次生成物干净组装 44 个终稿到 staging；不得读取或回拷旧 `04`。
- `配置映射与正式落表流程.md`：定义 Schema 镜像、配置草案、人工批准、正式 Datas 写入与导出回执的硬门禁。
- `generate_vgame_config_mapping.py`：只读解析 Vgame Schema，生成 `00_总览/Vgame配置映射总表.xlsx` 及审计报告。
- `generate_mapping_equip_full_package.py`：从映射装备权威 MD 生成 P02 全链路映射配置包；正式 Datas 只读，包含属性、Items/Generate、30 层 Drop/UIlevel、EquipmentLevel 和 Portable 子包。
- `validate_mapping_equip_full_package.py`：不导入生成器，独立复算 P02 行数、属性公式、ID 唯一性、Drop 10000 权重、外键、公式错误和正式 Datas 哈希。
- `schema/`：可选的字段结构、校验规则、枚举定义。

使用规则：

- AI 每次做数值前，先读 `00_总览` 和这里。
- 这里记录读写方法，不记录单系统最终结论。
- 字段所有权顺序为：用户已确认裁决 > `source_owned`（01）> `md_owned`（系统 MD）> `derived`。无所有权的冲突必须阻断，不能静默选值。
- `04_数值文档` 是派生交付物，不是参数维护源；升级时必须重新生成 staging 并通过 `05_验算核算/scripts/validate_rebuild.py`。
- 配置映射总表同样不是参数维护源；批次中的新裁决必须回写 MD，用户批准前禁止修改正式配置。
