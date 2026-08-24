# 共享底座

本域共登记 9 个原子。正文只给出规范化导航；精确上下文按 `sourceLocator` 回源。

| 原子 | 状态 | 标题 | 规范化陈述 | 系统 | Skill |
|---|---|---|---|---|---|
| `NATOM-3262DE1699E3` | ACTIVE | MD 参数契约 | MD 参数契约（源章节未提供可直接摘要的自然语言正文） | SYS-IN-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-9E3F8EFDB5DE` | ACTIVE | 共享参数基线 | 本文件是该参数域的唯一参数权威。旧参数工作簿已在完成逐格迁移与 MD-only 回归后删除。 参数单元格稳定 ID 为 `共享/<Sheet>!<Cell>`。正式数值文档修改必须同步本参数块或对应系统沉淀 MD。 | SYS-OUT-SU-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-3F51495D0227` | ACTIVE | 字段原则 | 所有百分比字段在表头标明单位，例如 `数值(%)` 或 `系数`。 所有 ID 字段使用稳定英文或拼音，不直接依赖显示名。 所有人工待填字段保留空白，不用生成器猜测。 所有备注字段写明来源或设计意图。 | SYS-IN-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-5C710060485A` | ACTIVE | 总体规划 | 总体规划（源章节未提供可直接摘要的自然语言正文） | SYS-OUT-SU-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-7FFD2AEA24FC` | ACTIVE | 数值边界与口径 | 本文件只定义数值职责边界，不记录具体数值。全局事实以 `01_源表` 为证据，单系统参数与公式以 `03_沉淀MD` 为唯一设计权威，`04_数值文档` 为最终交付结果。 | SYS-OUT-SU-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-88A21F09DDAB` | ACTIVE | 模块读写规则 | 模块读写规则（源章节未提供可直接摘要的自然语言正文） | SYS-IN-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-5C281A71F521` | ACTIVE | 禁止事项 | 不把单系统最终展开表当源表。 不把生成结果反写进源表，除非用户明确确认这是新的全局口径。 不在源表中隐藏临时假设。 不从 `_shared/共享参数.xlsx` 或四模块 `参数.xlsx` 直接决定终稿。 不允许最终文档出现无法回到 MD 参数 ID 或系统沉淀章节的关键硬编码。 不用 `run_all.py` 的生成结果无提示覆盖 `04_数值文档`。  | SYS-IN-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-D30E62B97BC2` | ACTIVE | 表结构说明 | 本文件记录 `01_源表` 的推荐字段。后续如源表结构调整，需要同步更新这里。 单系统参数不再使用 Excel 参数表维护，统一遵循 `MD参数契约.md`；本文件只定义全局源表结构。 | SYS-IN-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
| `NATOM-E728517D76AE` | ACTIVE | 输入文档更新流程 | 后续框架更新默认按本文档执行。目标是先把用户给的输入文档拆成可审、可追踪、可生成的框架文档，确认后再落到最终框架产物中。 | SYS-OUT-SU-04 | vgame-knowledge-router、game-numerical-analysis、vgame-config-schema |
