# 数值生产工作流单仓迁移报告

## 结论

数值知识正文、Skill、生产源码、可编辑数值设计输入和 44 份正式数值交付文档现在同属于唯一权威 Git 仓库。正式知识入口仍是 `knowledge-base/README.md`；本目录提供可执行生产能力和交付资产，不构成第二知识入口。

| 对象 | 迁入数量 | 权威位置 | 处置 |
|---|---:|---|---|
| 旧 Python 生产、专项和验算脚本 | 59/59 | `framework/` | 全部迁入；1个正式配置写入工具默认拒绝 |
| 受控输入工作簿 | 37/37 | `framework/01_源表/`、`framework/经济/模块产销表/`、`legacy-inputs/` | Git管理，只作数值设计输入，不是SVN正式配置 |
| 历史全局基础工作簿 | 4/4 | `legacy-inputs/` | 运行时复制到隔离工作区，保持旧脚本相对路径兼容 |
| 生产规则与沉淀 Markdown | 76/76 | `framework/` | 路径已移植；已清理被专武裁决B覆盖的旧结论 |
| 全部迁移生产资产 | 172/172 | `workflow-manifest.json` | 记录源哈希、迁入哈希、职责和真实配置写入风险 |
| 主生成任务 | 22/22 | `framework/run_all.py` | 由仓库隔离运行器调度 |
| 最终数值工作簿 | 44/44 | `framework/04_数值文档/` | 全量重新生成并纳入 Git；不是参数或模板输入 |
| 独立动态验算 | 6/6 | `output/numerical-production-workflow-v2/runs/<run>/reports/` | 全部门禁通过后才允许正式发布 |

## 迁移、归档与保留

- **迁入**：生产入口、59个脚本、共享代码、源表、参数MD、专项系统沉淀、22份经济模块输入、4份历史全局工作簿、规则、动态验算器，以及从新生产链完整重建的44份正式数值文档。
- **不迁入**：旧目录的`.git`、备份、缓存、旧`04_数值文档`原件、旧`05_验算核算`、旧`06_最终配置`和历史staging；它们继续作为原位置历史证据，不被无依据删除。新 `framework/04_数值文档/` 只接收通过门禁的新生成版本。
- **保留**：旧数值目录原始内容、真实SVN Datas、用户已有历史证据，以及项目唯一正式知识入口和33个现有Skill。
- **可追溯归档**：生产失败记录、诊断产物和被新发布替换的历史生成目录，仅保存在可重建的`output/numerical-production-workflow-v2/`。
- **证据链接迁移**：52处已迁入数值沉淀路径改为仓库内相对定位；22处旧最终配置镜像/中间产物改为带源注册表引用的历史证据，不再依赖旧数值盘作为当前正文来源。
- **禁止**：从旧最终数值文档回拷缺失文件；在 `framework/04_数值文档/` 之外的生产源码目录保存生成工作簿；将正式交付 Excel 反向作为参数或模板输入；未经用户明确授权修改真实SVN配置。
- **跨环境哈希**：Python、Markdown 和 JSON 使用 UTF-8/LF 归一化内容哈希，Excel 等二进制资产使用原始字节 SHA-256，避免 Windows Git checkout 的 CRLF 转换破坏重建。

## 已修复的历史断点

1. 专武源工作表已被删除，但人工裁决B要求一个大版本兼容期：以已沉淀参数作为冻结兼容输入，继续生成专武终稿，不把旧消耗自动迁移到收容物。
2. 当前源表与历史参数MD曾存在33处漂移：31个源表拥有字段与2个确定性派生值已同步回 Git 管理的共享、养成、战斗、节奏4份参数基线及知识库机器参数注册表；完整历史差异报告保留在`output/`，后续正式生产强制源表与MD零差异，不再修改staging中的参数。节奏公式缓存缺失时继续保留已确认MD值。
3. 角色星盘旧生成器仍强制二级预算1.2和无基础属性：已改按最新确认的基础系数1.2、二级预算1.8生成，并明确标记源表基础系数0待人工同步。
4. 映射装备旧生成器依赖旧Markdown表头、旧锻造二次公式和旧爬塔装备材料：已适配最新部位主属性、副属性上限、59级合计94500的离散锻造经验，以及爬塔不再产装备材料。

## 运行与状态

```powershell
python scripts/numerical-workflows/run_production.py
python scripts/numerical-workflows/validate_migration.py --production-report output/numerical-production-workflow-v2/latest-production-report.json
pwsh -File scripts/knowledge-framework/rebuild.ps1 -Publish
```

旧数值文档盘在运行时显式不可用。`VGAME_CONFIG_DATAS`仅用作真实工程配置的只读证据。最小人工确认列表见`human-confirmations.json`。独立终验状态始终为`PENDING`，交由独立审核对话验收。
