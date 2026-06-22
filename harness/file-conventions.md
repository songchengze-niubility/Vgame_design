# File Conventions

## 目录用途

| 目录 | 用途 |
|---|---|
| `design/` | 系统设计、反推文档、长期设计记录 |
| `proposals/` | 等待评审或已批准的落地方案 |
| `tasks/` | 可执行任务拆解和状态跟踪 |
| `plans/` | 计划索引、里程碑、专题路线 |
| `harness/` | 协作规则、门禁、方法论 |
| `knowledge-graph/` | 知识图谱入口、构建说明、索引 |
| `scripts/` | 门禁和辅助检查脚本 |

## 命名规则

| 类型 | 规则 | 示例 |
|---|---|---|
| Design Doc | `<系统名>-design.md` 或中文系统名 | `角色强度评价-design.md` |
| Proposal | `<主题>-YYYY-MM-DD.md` | `角色强度标杆校准-2026-06-18.md` |
| Task | `<主题>-YYYY-MM-DD.md` | `补全经济产销审查-2026-06-18.md` |
| Harness 文档 | 小写 kebab-case | `maintenance-gates.md` |
| 脚本 | 小写或动词短语 | `check.ps1` |

## 内容边界

- 本仓库可以保存设计文档和分析结论。
- 本仓库不作为真实 Excel 配置源。
- 若必须保存样例表，文件名必须含 `sample`，并在文档中说明不是线上配置。

