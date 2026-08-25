# 全栈数值知识层

本目录是 `knowledge-base/README.md` 下的数值权威子层，不是第二个正式入口。外部数值框架共纳管 **1329** 个文件；其中 **74** 个权威 Markdown 文件已按章节形成 **997** 个来源原子，另注入 2 个人工裁决原子；**33** 个源工作簿已登记结构。

## 查询顺序

1. 先由 `vgame-knowledge-router` 选择系统和数值域。
2. 从 `atom-registry.json` 加载最小原子及五类映射。
3. 需要完整上下文或受控数值源表时，优先回源仓库内 `../../numerical-workflows/v2/framework/`；需要真实配置时再按配置候选回源 SVN Datas。
4. `sourceNature` 为 `SOURCE_EXPLICIT` 只证明源文明确；不能据此推断 Production/LIVE。

## 机器入口

- `source-registry.json`：全部源文件及唯一处置。
- `workbook-registry.json`：权威源工作簿/工作表结构。
- `atom-registry.json`：规范化数值知识原子。
- `formula-registry.json`：公式和计算规则候选。
- `parameter-registry.json`：机器可读参数块。
- `mappings/`：数值原子到系统、Skill、证据、配置、项目框架节点。
- `../../numerical-workflows/v2/workflow-manifest.json`：59 个生产脚本、37 份受控输入表、原始哈希、迁移哈希和真实配置写入风险。

## 完整数值生产

运行 `python scripts/numerical-workflows/run_production.py`，即可从仓库内源码、源表、参数 MD 与只读 Datas 证据生成 44 份最终数值文档，并执行独立动态验算。运行时会显式禁用旧数值文档根目录；所有 staging、报告及正式生成目录均位于 `output/numerical-production-workflow-v2/`。

## 治理边界

- 旧外部源文件继续是迁移证据；受控生产源码、参数 MD 与数值设计输入工作簿已进入本仓库 Git。
- 备份、报告、最终配置镜像和 staging 只做可追溯登记。
- 房车 C 与专武 B 以 `knowledge-base/governance/rulings.json` 及本层的裁决原子为准。
- 本目录全部是 Git 跟踪源；网页、索引、切片和图谱必须能在没有外部数值盘的环境中重建。
