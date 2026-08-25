# Vgame 数值生产工作流 V2

本目录是项目唯一权威仓库中的数值生产源码与输入层，不是第二知识入口。

## 目录

- `framework/`：原生产入口、规则、共享代码、源表、参数 MD、专项生成器与动态验算器。
- `legacy-inputs/`：仍被生产链读取的四份历史全局源工作簿。
- `workflow-manifest.json`：全部生产文件、原始哈希、迁入哈希、职责与写入风险。
- `governance-overrides.json`：房车 C、专武 B、公式缓存缺失策略及真实配置默认拒绝策略。
- `MIGRATION.md`：新旧内容迁移、归档、保留与历史断点修复清单。
- `human-confirmations.json`：仍需人工判断的最小问题列表。

## 运行

```powershell
python scripts/numerical-workflows/run_production.py
```

运行器先从 Git 管理的输入创建全新 staging，再执行 2 个输入门禁、22 个生成任务、44 份数值终稿组装和独立动态验算。全部生成物只写入 `output/numerical-production-workflow-v2/`。

旧外部数值文档盘不参与运行。真实配置源由 `VGAME_CONFIG_DATAS` 指定，只作为只读工程证据；任何直接写真实配置的旧工具都不得由主生产链自动执行，且没有 `VGAME_ALLOW_FORMAL_CONFIG_WRITE=USER_APPROVED` 时会明确拒绝。

源表与旧参数 MD 的差异只在运行 staging 内按字段归属同步。专武源页已被删除，但最新 B 裁决要求一个大版本兼容期，因此兼容终稿继续从现有参数 MD 生成；节奏源表缺失公式缓存时保留已确认的 MD 值，不用空值覆盖历史结论。

正式项目知识入口仍为 `knowledge-base/README.md`，Skill 正文仍只位于 `skills/`。
