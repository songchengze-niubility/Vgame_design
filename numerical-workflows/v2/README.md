# Vgame 数值生产工作流 V2

本目录是项目唯一权威仓库中的数值生产源码、输入与正式数值交付层，不是第二知识入口。

## 目录

- `framework/`：原生产入口、规则、共享代码、源表、参数 MD、专项生成器与动态验算器。
- `framework/04_数值文档/`：44 份 Git 管理的正式数值 Excel；拉取仓库即可使用。
- `legacy-inputs/`：仍被生产链读取的四份历史全局源工作簿。
- `workflow-manifest.json`：全部生产文件、原始哈希、迁入哈希、职责与写入风险。
- `governance-overrides.json`：房车 C、专武 B、公式缓存缺失策略及真实配置默认拒绝策略。
- `MIGRATION.md`：新旧内容迁移、归档、保留与历史断点修复清单。
- `human-confirmations.json`：仍需人工判断的最小问题列表。

## 运行

```powershell
python scripts/numerical-workflows/run_production.py
```

运行器先在 `output/numerical-production-workflow-v2/` 从 Git 管理的输入创建全新 staging，再执行 2 个输入门禁、22 个生成任务、44 份数值终稿组装和独立动态验算。全部门禁通过后，正式终稿整体发布到 Git 管理的 `framework/04_数值文档/`；运行过程、诊断报告、临时工作区和旧发布归档继续保存在 `output/`。

正式 Excel 是可追溯的交付结果，不是参数或模板输入。每次重建都会从隔离工作区排除已有 `04_数值文档/`，继续只以 `01_源表/` 和 `03_沉淀MD/` 作为数值设计依据。

旧外部数值文档盘不参与运行。真实配置源由 `VGAME_CONFIG_DATAS` 指定，只作为只读工程证据；任何直接写真实配置的旧工具都不得由主生产链自动执行，且没有 `VGAME_ALLOW_FORMAL_CONFIG_WRITE=USER_APPROVED` 时会明确拒绝。

源表拥有字段必须先显式同步回 Git 管理的 `03_沉淀MD/参数基线/`，再刷新知识库参数注册表与生产蓝图；正式生产只执行源表与 MD 的零差异检查，不会在 staging 中偷偷覆盖权威参数。后续源表变化时按以下顺序执行：

```powershell
python numerical-workflows/v2/framework/02_AI规则/sync_global_sources_to_md.py --write --report output/numerical-production-workflow-v2/source-md-authority-sync.json
python scripts/numerical-knowledge/sync_parameter_baselines.py --json-report output/numerical-production-workflow-v2/parameter-baseline-sync.json
python scripts/numerical-workflows/refresh_manifest.py
python scripts/numerical-workflows/run_production.py
```

专武源页已被删除，但最新 B 裁决要求一个大版本兼容期，因此兼容终稿继续从现有参数 MD 生成；节奏源表缺失公式缓存时保留已确认的 MD 值，不用空值覆盖历史结论。

正式项目知识入口仍为 `knowledge-base/README.md`，Skill 正文仍只位于 `skills/`。

## 门禁路线图

现有 2 个输入门禁与独立动态验算覆盖"生成正确性"；以下规划补齐"设计正确性"钩子，完整定义见 `harness/maintenance-gates.md` 的"数值生产门禁（规划）"。优先级从高到低：

1. **引用闭环审查**：DropId、LevelId、Unlock、UIlevel 只读闭环校验（原扩展方向存量项，最先落地）。
2. **经济沙盘门禁**：奖励结构变更于方案冻结后、落表前运行确定性 12 周库存/通胀模拟（python 计算）；假设清单随方案冻结显式登记；通胀增速超红线即 FAIL 并禁止进入最终配置。
3. **口径一致性审计**：沉淀 MD、参数基线与配置注册表三方定期对账。
4. **黄金数回归**：44 份终稿每次发布生成基线快照，重建时自动 diff。
5. **设计模板升级**：假设声明必填字段并入 design/proposal 模板。

分工约束与上游规则同见 `harness/maintenance-gates.md`：数值权威属于代码与阈值；AI 承担搭建、审计与解读，不承担计算判定。
