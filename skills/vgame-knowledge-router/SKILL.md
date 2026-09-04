---
name: vgame-knowledge-router
description: 自动为 Vgame 项目事实、系统盘点、规则流程、系统关系、设计影响、当前状态、配置字段、源码与证据核验问题选择最小知识包。用于任何需要从项目级策划知识库定位系统、共享契约或原始证据的请求；会自动区分 quick、design、audit 深度，并明确 Design、工作副本、镜像与 Production/LIVE 的来源边界。
---

# Vgame 项目级自动知识路由

## 目标

先路由，再阅读。权威正文来自受 Git 管理的 `knowledge-base/`；路由器使用由这些权威源重建的 `output/knowledge-framework/knowledge-base/router-manifest.json` 选择最小相关模块、系统、共享契约和证据，避免把整个知识库塞进上下文。生成清单不是权威正文。

本 Skill 只负责知识检索与来源边界。需要修改策划案、配置或代码时，在完成路由和回源确认后，再按 `vgame-core-understanding` 进入对应专项 Skill。

## 全栈数值层

当问题命中数值、公式、参数、概率、成长、经济、节奏、难度、奖励或验算语义时，路由脚本从 `knowledge-base/numerical/atom-registry.json` 选择最小 `numericAtoms`，并返回对应系统、Skill、配置候选和 `sourceLocator`。普通系统查询不加载全部数值原子；需要完整源上下文或源表当前值时才沿 `sourceLocator` 回到外部数值框架。生成物、配置镜像和验算结果不得被当作 Production/LIVE 证明。

## 历史经验层

路由脚本在每次检索时同步扫描 `knowledge-base/experience/exp-*.md` 的条目头部（triggerTerms/tags/标题），把命中的 active 教训作为 `experienceHints` 返回，并放入 readPlan 最前（L1，先于任何系统正文）。命中即必读：条目记录的是同类问题已踩过的坑与规避动作；它与当前结论冲突时按来源性质标注冲突，不得静默忽略。`incorporated` / `obsolete` 条目不参与召回。新教训的写入时机见 `planning-feature-workflow` 第 9 步。

## 必须先运行路由器

从仓库根目录运行：

```powershell
python skills/vgame-knowledge-router/scripts/route_query.py "<用户问题>"
```

需要机器可读结果时：

```powershell
python skills/vgame-knowledge-router/scripts/route_query.py "<用户问题>" --format json
```

通常让脚本自动判断档位。只有用户明确要求速览、设计推演或审计核验时，才使用 `--profile quick|design|audit` 覆盖自动判断。

不要在运行路由器之前猜测文件路径。不要遍历或全量读取 `system-details/`。

## 三档路由

| 档位 | 适用问题 | 允许层级 | 硬上限 |
|---|---|---|---|
| `quick` | 是什么、有哪些、概览、分类 | L0/L1 | 0 个系统详情、0 个契约、0 个证据 |
| `design` | 规则、流程、关系、影响、策划设计 | L1/L2 | 最多 3 个系统、5 个契约、0 个原始证据 |
| `audit` | 数值、字段、配置、代码、当前状态、LIVE、证据核验 | L1/L2/L3 | 最多 3 个系统、5 个契约、5 个证据 |

脚本给出的上限与 manifest 取更严格值，不可自行放宽。

## 阅读流程

1. 运行 `route_query.py`，确认 `profile`、命中系统、共享契约、证据和 `readPlan`。
2. 严格按 `readPlan` 顺序读取；同一层内只读取被选中的文件。
3. 对 `detailLevel: full` 的系统，仅在路由结果明确给出 `detailRef` 时读取对应单个详情文件。
4. 对 `detailLevel: summary` 的系统，只能复述 manifest 中的名称、摘要、状态、关系和标识。不得补造流程、字段、异常、UI 或具体数值。
5. 需要跨系统判断时，优先读取命中的共享契约；保留契约自己的 `provenance`，不要把综合规则写成原文明确规则。
6. `audit` 仅可读取路由结果列出的最多 5 个证据路径。路由器只读取已选详情文件中的证据元数据，不读取证据正文，也不扫描整个详情目录。
7. 证据不足、冲突或不存在时输出 `UNKNOWN`，并说明缺少哪一种权威来源或确认动作。

## 来源性质不可混写

回答每个关键结论时，使用 manifest 定义的来源性质：

- `SOURCE_EXPLICIT`：Design、数值文档或其他权威文本直接明确。
- `WORKING_COPY_OBSERVED`：本机 SVN 工作副本观察；只能说明当前工作副本，不能证明 Production/LIVE。
- `CROSS_SOURCE_SYNTHESIS`：多源整理出的关系、流程或边界；需要项目负责人确认。
- `DESIGN_PROPOSAL`：补缺方案，不是既成事实。
- `UNKNOWN`：证据不足、冲突或无法确认。

始终保留以下边界：

- 工作副本 ≠ Production/LIVE。
- 配置镜像 ≠ `Datas` 真实配置 ≠ Production/LIVE。
- “当前”“上线”“LIVE”问题必须有明确环境、版本、发布记录或运行时证据；否则结论为 `UNKNOWN`。
- 路由结果是检索计划，不是项目事实本身。

## 回答契约

最终回答至少包含：

1. 使用的档位以及为何使用。
2. 实际读取的系统，并标注 `full` 或 `summary`。
3. 实际读取的共享契约与原始证据。
4. 每个关键结论的来源性质。
5. 冲突、缺口和 `UNKNOWN`。
6. 若要求落地，指出下一步应进入的专项 Skill 或权威配置/代码源。

不要把“未命中详情”写成“系统不存在”。这只表示当前知识包没有足够的系统级详情。

## 资源

- 路由脚本：`scripts/route_query.py`
- 提问与输出示例：`references/prompt-patterns.md`
- 权威入口：`knowledge-base/README.md`
- 经验沉淀规范：`knowledge-base/experience/README.md`
- 可重建路由清单：`output/knowledge-framework/knowledge-base/router-manifest.json`
