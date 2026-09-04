# 全栈数值知识层

本目录是 `knowledge-base/README.md` 下的数值权威子层，不是第二个正式入口。外部数值框架共纳管 **71203** 个文件；其中 **1868** 个权威 Markdown 文件已按章节形成 **20136** 个来源原子，另注入 2 个人工裁决原子；**33** 个源工作簿已登记结构。

## 查询顺序

1. 先由 `vgame-knowledge-router` 选择系统和数值域。
2. 从 `atom-registry.json` 加载最小原子及五类映射。
3. 需要完整上下文、源表值或真实配置时，按 `sourceLocator`、`sourceId` 与配置候选回源。
4. `sourceNature` 为 `SOURCE_EXPLICIT` 只证明源文明确；不能据此推断 Production/LIVE。

## 机器入口

- `source-registry.json`：全部源文件及唯一处置。
- `workbook-registry.json`：权威源工作簿/工作表结构。
- `atom-registry.json`：规范化数值知识原子。
- `formula-registry.json`：公式和计算规则候选。
- `parameter-registry.json`：机器可读参数块。
- `mappings/`：数值原子到系统、Skill、证据、配置、项目框架节点。

## 治理边界

- 旧源文件继续是证据，不是本仓库正式正文。
- 备份、报告、最终配置镜像和 staging 只做可追溯登记。
- 房车 C 与专武 B 以 `knowledge-base/governance/rulings.json` 及本层的裁决原子为准。
- 本目录全部是 Git 跟踪源；网页、索引、切片和图谱必须能在没有外部数值盘的环境中重建。
