---
name: planning-feature-workflow
description: 游戏策划功能从需求想法、逐条澄清、专业设计到正式 Excel、UI、验收追踪、变更同步和人工验收的完整流程。用户问策划流程、下一步、当前进度、继续上次任务、完整策划交付、需求变化、design-lead 或 planning-workflow 时使用。
---

# 游戏策划功能交付流程

## 启动

1. 解析功能短名、目标、执行模式、交付档位、风险档位和输出目录。
2. 功能名明确时先运行：

   `python scripts/planning_workflow_status.py --feature "<功能名>"`

3. 按以下优先级判断真实进度：
   - 用户在当前对话中的明确声明。
   - `00-workflow-state.json`。
   - 实际产物是否存在且通过检查。
4. 读取本技能的 [门禁契约](references/planning-workflow-gate-contract.md)。
5. 进入某个角色前，读取 `${VGAME_SKILL_ROOT}` 下对应角色的 agent toml（若存在）。
6. 本技能引用的 `planning_workflow_status.py`、`update_planning_workflow_state.py`、`verify_design_artifacts.py`、`check_planning_template_cache.py` 均已随仓库入库于 `scripts/`，并由 `scripts/check.ps1` 做存在性与可导入性校验；路径依赖见 `scripts/vgame_paths.py`。

## 执行方式

- 用户明确要求 agents、委派、并行或"完整 managed workflow"时，由 `design-lead` 统一编排。
- 用户未明确要求 subagents 时，由主线程按相同角色顺序执行；不得因为未生成子线程而降低任何角色标准。
- specialist 只完成本职工作并返回缺口，不自行调用下游角色。
- 所有下游角色读取同一份 `00-design-contract.md` 和 `01-project-reference.md`。
- 阶段完成后运行 `scripts/update_planning_workflow_state.py`；口头说明不能代替状态和产物。

## 交付档位

| 档位 | 交付物 |
|---|---|
| `ADVICE` | 只给建议，不生成文件 |
| `DOC_ONLY` | Excel 策划案 |
| `UI_ONLY` | HTML + 页面/组件 PNG + UI Manifest |
| `DOC_UI` | Excel + HTML + 页面/组件 PNG + UI Manifest |
| `FIGMA_UI` | 可编辑 Figma 源文件 + 页面/组件预览 PNG + Figma Handoff Manifest |
| `DOC_FIGMA` | Excel + 可编辑 Figma 源文件 + 页面/组件预览 PNG + Figma Handoff Manifest |
| `IMPLEMENTATION` | 代码或配置落地；文档按用户要求补充 |

完整策划功能默认 `DOC_UI`。用户明确要求可由 UI/UE 与程序继续编辑的 Figma 源文件时，切换到 `FIGMA_UI` 或 `DOC_FIGMA`；不要把 HTML 原型冒充 Figma 交付。

## 风险档位

| 风险 | 判断 | 评审要求 |
|---|---|---|
| `LOW` | 单模块、小改动、无复杂数值或跨系统影响 | specialist 和总控自检 |
| `MEDIUM` | 多页面、周期/奖励/配置、复用现有系统 | 一次一致性评审 |
| `HIGH` | 跨系统、多人、经济投放、复杂战斗、版本核心 | 一致性评审 + 成品复核 |

## 输出目录

每个功能使用独立目录：

`${VGAME_OUTPUT_ROOT}/<功能短名>/`

```text
<功能短名>/
├─ 00-workflow-state.json
├─ 00-design-contract.md
├─ 00-clarification-log.md
├─ 01-project-reference.md
├─ 02-core-design.md
├─ 03-specialist-results/
│  ├─ figma-ui-plan.md
│  └─ figma-target.json
├─ 04-review.md
├─ 05-traceability-matrix.md
├─ 06-acceptance-cases.md
├─ 07-change-log.md
├─ ui/
│  ├─ index.html
│  ├─ page-*.png
│  ├─ component-*.png
│  └─ ui-asset-manifest.json
├─ figma/
│  ├─ figma-ui-handoff-manifest.json
│  ├─ figma-ui-handoff-report.md
│  └─ previews/
│     ├─ page-*.png
│     └─ component-*.png
├─ <功能短名>策划案.xlsx
└─ 08-delivery-report.json
```

## 九步流程与变更循环

### 1. 任务登记与参考选择

- 责任：`project-researcher`。
- 判断 `FAST / STANDARD / REFRESH`、交付档位和风险档位。
- 运行 `python scripts/check_planning_template_cache.py`。
- 从模板索引选一个主模板，必要时最多一个辅助模板。
- 使用最多 5 个关键词局部检索相似功能、配置、代码、Prefab 和 UI。
- 产出 `01-project-reference.md`。
- 禁止每次重建全部模板缓存或全量扫描项目。

### 2. 需求契约与范围确认

- 责任：`feature-scoper`。
- 创建唯一的 `00-design-contract.md`。
- 写清目标体验、本期范围、非目标、玩家路径、规则模块、页面和组件清单。
- 区分已确认事实、工作假设、待确认和已否决方案。
- 给核心规则分配稳定规则 ID。
- 记录档位、风险和验收标准。
- 用户必须确认契约或明确接受工作假设；未确认时不得进入步骤 3。

### 3. 逐条澄清与决策冻结

- 责任：`requirement-clarifier`。
- 维护 `00-clarification-log.md`。
- 只记录会改变方向、范围、规则或验收的阻塞问题。
- 每次只向用户确认一个问题，提供 2 至 4 个选项及影响。
- 用户结论同步回需求契约。
- 阻塞项未清空时不得进入核心设计。

### 4. 核心设计

- 活动、任务、商城、成长、奖励、排行、红点：`system-designer`。
- 战斗、Boss、技能、Buff、关卡、怪物机制：`combat-designer`。
- 混合玩法分别产出，但读取同一需求契约。
- 必须覆盖触发、条件、流程、状态、资源、周期、刷新、失败、异常、UI、配置、实现和 QA。
- 产出 `02-core-design.md`。

### 5. 专项设计

按需求执行，不默认全跑：

| 专项 | 责任 | 产出 |
|---|---|---|
| 数值 | `num-balance` | `03-specialist-results/numeric.md` |
| 配置 | `config-table` | `03-specialist-results/config.md` |
| 实现 | `lua-scripter` | `03-specialist-results/implementation.md` 或代码与验证证据 |
| UI 规格 | `ui-prototype`，使用 `vgame-ui-prototype` | `03-specialist-results/ui-spec.md` |
| 可编辑 Figma UI | `figma-ui-designer`，使用 `vgame-figma-ui` | `figma-ui-plan.md` + `figma-target.json`；两者批准后写入目标 Figma 并生成 Handoff Manifest |
| Bug 定位/修复 | `lua-scripter` | 根因、证据、最小验证；IMPLEMENTATION 档位可修复 |
| 数据与埋点 | `analytics-designer` | `03-specialist-results/analytics.md` |
| LiveOps | `liveops-planner` | `03-specialist-results/liveops.md` |

长期系统、限时活动、付费、排行、奖励投放和版本核心功能必须评估数据与上线专项。限时活动至少说明活动结束、补领和清理；高风险功能至少说明开关、灰度、回滚、补偿和监控。

### 6. 一致性评审与规则冻结

- 责任：`design-reviewer`。
- LOW 可由总控按同一清单自检；MEDIUM/HIGH 必须独立评审。
- 检查所有产物是否使用同一契约，规则/数值/配置/实现/UI 是否一致，页面与组件是否覆盖正常和异常路径。
- 禁止把工作假设伪装成项目现状。
- 产出 `04-review.md`。
- MEDIUM/HIGH 必须关闭 P0/P1 后才进入正式 UI/Excel。
- 自动返工最多两轮，之后交用户决策。

### 7A. HTML UI 原型资产制作

- 适用档位：`UI_ONLY`、`DOC_UI`。
- 责任：`ui-prototype`，必须加载 `vgame-ui-prototype`；已安装时同时加载 `$frontend-design` 作为视觉工艺基线。
- 产出 `ui/index.html`、`page-*.png`、`component-*.png` 和 `ui-asset-manifest.json`。
- PAGE 对应页面 ID 和规则 ID；COMPONENT 对应组件 ID、页面 ID 和规则 ID。
- HTML 必须实际渲染并完成核心交互后导出 PNG，不得用图像生成结果冒充页面截图。
- Manifest 遵循 `vgame-ui-prototype/references/ui-asset-contract.md`。
- 进入正式 Excel 前运行 `vgame-ui-prototype/scripts/validate_ui_assets.py`；失败时留在 UI 阶段。

### 7B. 可编辑 Figma UI 交付

- 适用档位：`FIGMA_UI`、`DOC_FIGMA`；除非档位另有约定，不强制重复制作 HTML 原型。
- 责任：`figma-ui-designer`，必须加载 `vgame-figma-ui`；该 skill 会调用官方 Figma 写入、页面搭建和组件库能力，并应用游戏 UI 约束。
- 先以只读方式检查团队已有 Figma 文件、订阅库、组件、变量和正式 UI 证据，生成 `03-specialist-results/figma-ui-plan.md`。
- 用户必须明确批准 UI 方案并设置 `figma_ui_plan_confirmed=true`；批准前禁止新建 Figma 文件、修改节点、上传资产、捕获页面或写入 Code Connect。
- UI 方案批准后还要锁定准确的 Figma design URL、file key 和目标 page/node，并由用户设置 `figma_target_confirmed=true`。
- 新建文件时只能先创建空文件；取得 URL 后必须停下确认，不得在同一步写入 UI 内容。
- 首次内容写入前必须通过 `vgame-figma-ui/scripts/check_figma_write_gate.py`；方案失败停在 `figma_ui_plan`，地址失败停在 `figma_target`。
- UI 方案需说明页面布局、组件/变体、变量、交互、适配、安全区、输入、动效、风格证据、导出范围和关键取舍；方案范围或视觉方向变化时重新确认。
- 批准后优先复用团队已有 Figma 文件、订阅库、组件和变量；新建文件前仍须确认 Figma plan。
- 产出可继续编辑的 Figma 页面、组件/变体、变量、交互流、交接页，以及 `figma/figma-ui-handoff-manifest.json`、报告和预览 PNG。
- PAGE/COMP/FLOW 与规则 ID 必须来自同一契约；不得把完整页面位图铺进画板冒充可编辑源文件。
- Figma 交付是程序/UI-UE 的设计源和规格交接，不等于 Unity Prefab、Binder 或 Lua 已实现。
- 进入正式 Excel 前运行 `vgame-figma-ui/scripts/validate_figma_handoff.py`；失败时留在 `figma_ui` 阶段。

### 8. 正式 Excel

- 责任：`doc-writer`。
- 读取契约、核心设计、专项结果、当前档位对应的 UI/Figma Manifest、真实图片、模板索引和写作规范。
- 页面主图和组件详图必须放在对应规则正文附近。
- 不压窄正文，不创建脱离正文的纯图片 Sheet，不复制空 Sheet。
- 产出 `<功能短名>策划案.xlsx`。

### 9. 验收追踪、成品校验与用户验收

- 责任：`acceptance-designer` + `design-lead`。
- 生成 `05-traceability-matrix.md`，关联规则、HTML/Figma UI、配置、实现、Excel、验收和证据。
- 生成 `06-acceptance-cases.md`，使用 Given-When-Then。
- 核心规则不得缺少验收用例，验收用例不得缺少规则来源。

运行：

`python scripts/verify_design_artifacts.py "${VGAME_OUTPUT_ROOT}/<功能短名>" --profile <交付档位>`

- 按交付档位检查 Excel、HTML 或 Figma 节点、PNG、Manifest、公式、规则 ID 对应、图片嵌入和可读性。
- 生成 `08-delivery-report.json`。
- 自动校验只证明结构通过。
- 最终 Excel 排版、规则正确性和 UI 表达必须由用户人工确认。
- 不得替用户把 `delivery_accepted` 设为 true。

## 需求变更循环

- 责任：`change-sync-reviewer`。
- 任何需求、规则、数值、配置、UI 或实现变化都记录到 `07-change-log.md`。
- 每条变更分配 `CHG-xxx`，列明旧规则、新规则、不变项和影响矩阵。
- 范围、核心体验或经济模型变化时回到契约与评审。
- 局部变化只回到受影响阶段，但必须同步追踪矩阵和验收用例。
- 没有实际文件或验证证据时不得关闭变更。

## 状态回复

```markdown
**当前推断阶段**：步骤 N - {名称}

**执行档位**：{模式} / {交付档位} / {风险档位}

**已检测到**：
- {实际文件路径}

**下一步**：
1. {仅一条主动作}
2. 使用：{角色 / 命令 / 脚本}

**需您确认**：
- {仅在人类门禁时填写}
```

## 禁止

- 跳过需求契约让 specialist 各自理解需求。
- 没有检查实际文件就声称阶段完成。
- MEDIUM/HIGH 未关闭 P0/P1 就制作正式交付。
- 未取得 `figma_ui_plan_confirmed` 就对 Figma 执行任何写入。
- 未取得 `figma_target_confirmed`，或写入地址与已批准的 URL/file key/page/node 不一致，就向 Figma 写入内容。
- UI Manifest 不完整时声称 `DOC_UI` 完成。
- 没有可编辑 Figma 源文件、节点映射和 Handoff Manifest 时声称 `FIGMA_UI` 或 `DOC_FIGMA` 完成。
- 把铺满页面的单张位图或只读截图当作可编辑 Figma 交付。
- Excel 没有实际嵌图时声称 `DOC_UI` 完成。
- Excel 没有嵌入 Figma 实际预览图时声称 `DOC_FIGMA` 完成。
- 替用户宣称最终验收通过。
- 需求变化后只改 Excel 或只改实现，不同步其它受影响产物。
- 功能准备上线却没有指标、监控、回滚或适用的补偿方案。
