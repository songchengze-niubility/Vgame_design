# 策划工作流门禁契约

## 状态文件

每个功能独立保存：

`${VGAME_OUTPUT_ROOT}/<功能短名>/00-workflow-state.json`

初始结构参考同目录的 `workflow-state.example.json`。

状态文件是进度辅助；用户明确声明和实际文件证据优先级更高。

## Phase

| phase | 含义 | 主要责任 |
|---|---|---|
| `reference` | 项目参考与模板选择 | project-researcher |
| `contract` | 需求契约 | feature-scoper |
| `clarification` | 逐条澄清与决策冻结 | requirement-clarifier |
| `core_design` | 核心系统/战斗设计 | system/combat designer |
| `specialists` | 数值、配置、实现、UI 规格 | specialists |
| `review` | 一致性评审与规则冻结 | design-reviewer |
| `ui` | HTML、页面主图、组件详图与 Manifest | ui-prototype（使用 `vgame-ui-prototype`） |
| `figma_ui_plan` | Figma 写入前的 UI 方案与人工确认 | figma-ui-designer + 用户 |
| `figma_target` | 精确 Figma 写入地址与人工确认 | figma-ui-designer + 用户 |
| `figma_ui` | 可编辑 Figma 页面、组件、变量、交互与程序交接 | figma-ui-designer（使用 `vgame-figma-ui`） |
| `excel` | 正式 Excel 策划案 | doc-writer |
| `acceptance` | 验收用例与追踪矩阵 | acceptance-designer |
| `delivery` | 自动检查与人工验收 | design-lead + 用户 |
| `change_sync` | 需求变化影响与同步闭环 | change-sync-reviewer |
| `complete` | 用户已验收 | 人工确认 |

Outcome：`success`、`failure`、`needs_revision`、`blocked`、`waiting_human`。

## 状态块

阶段收尾时输出：

````markdown
```planning-workflow-gate
{"actor":"ui-prototype","phase":"ui","outcome":"success","next_action":"excel","evidence":"ui/index.html + manifest"}
```
````

状态块用于记录，不代替实际文件检查。随后运行：

```powershell
python scripts/update_planning_workflow_state.py --feature "<功能名>" --phase ui --outcome success --actor ui-prototype --next-action excel --evidence "ui/index.html"
```

## 人类门禁

| 门禁 | 字段 | 通过条件 |
|---|---|---|
| 需求契约 | `contract_confirmed` | 用户确认契约或明确接受工作假设 |
| 澄清闭环 | `clarification_resolved` | 阻塞澄清已逐条确认并同步回契约 |
| 规则冻结 | `review_approved` | MEDIUM/HIGH 的 P0/P1 已关闭；LOW 自检通过 |
| Figma UI 方案 | `figma_ui_plan_confirmed` | 用户明确批准当前 `figma-ui-plan.md` 版本；未批准时禁止 Figma 写入 |
| Figma 写入目标 | `figma_target_confirmed` | 用户明确批准 `figma-target.json` 中的准确 design URL、file key 和目标 page/node |
| UI 示意图评审 | `ui_mockup_approved` | 用户确认 Codex 产出的 UI 示意图方向；未通过前不得把页面图并入 Excel 策划案 |
| 验收就绪 | `acceptance_approved` | 追踪矩阵和验收用例完整且可执行 |
| 最终验收 | `delivery_accepted` | 用户确认 Excel、规则和 UI 符合预期 |

Agent 不得自动通过最终验收。用户明确验收后才可运行：

```powershell
python scripts/update_planning_workflow_state.py --feature "<功能名>" --accept-delivery
```

Figma 首次内容写入前必须运行：

```powershell
python "${VGAME_SKILL_ROOT}\vgame-figma-ui\scripts\check_figma_write_gate.py" `
  --plan "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-ui-plan.md" `
  --target "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-target.json"
```

命令返回非零时不得调用任何 Figma 写入工具。

## 回退

| phase | failure / needs_revision 回退 |
|---|---|
| `reference` | 保持本阶段，缩小或修正检索 |
| `contract` | 保持本阶段，更新同一契约 |
| `clarification` | 保持本阶段，继续当前问题，不批量跳过 |
| `core_design` | 若范围变化回 contract，否则留在本阶段 |
| `specialists` | 回对应专项；核心规则变化则回 core_design |
| `review` | 回被点名的设计或专项角色 |
| `ui` | 规则问题回 core_design；视觉布局问题留在 ui |
| `figma_ui_plan` | 留在本阶段修订方案；规则问题回 core_design；方案变化后必须重新确认 |
| `figma_target` | 留在本阶段修正 URL/file key/page/node；目标变化后必须重新确认 |
| `figma_ui` | 规则问题回 core_design；视觉、组件或交接问题留在 figma_ui |
| `excel` | 内容问题回设计；排版问题留在 excel |
| `acceptance` | 规则不可验收则回设计；映射缺失则回对应产物阶段 |
| `delivery` | UI/Excel 问题回对应阶段；规则问题回 review |
| `change_sync` | 回受影响阶段；重大变化回 contract |

同一 phase 最多自动返工两次。超过后设置 `blocked`，列出分歧、已尝试方案和需要用户决策的问题。

## 完成判定

| 档位 | 必须存在 |
|---|---|
| `DOC_ONLY` | xlsx、追踪矩阵、验收用例 |
| `UI_ONLY` | html、png、ui-asset-manifest.json、追踪矩阵、验收用例 |
| `DOC_UI` | xlsx、html、png、ui-asset-manifest.json、追踪矩阵、验收用例，且 Excel 有嵌图 |
| `FIGMA_UI` | 已批准的 figma-ui-plan.md 与 figma-target.json、可访问且可编辑的 Figma 源文件、页面/组件 node ID、预览 PNG、figma-ui-handoff-manifest.json、追踪矩阵、验收用例 |
| `DOC_FIGMA` | xlsx、已批准的 figma-ui-plan.md 与 figma-target.json、可访问且可编辑的 Figma 源文件、页面/组件 node ID、预览 PNG、figma-ui-handoff-manifest.json、追踪矩阵、验收用例，且 Excel 有嵌图 |
| `IMPLEMENTATION` | 实际修改、追踪矩阵、验收用例和验证证据 |

UI 阶段完成前先运行：

```powershell
python "${VGAME_SKILL_ROOT}\vgame-ui-prototype\scripts\validate_ui_assets.py" --ui-dir "${VGAME_OUTPUT_ROOT}\<功能短名>\ui" --require-components
```

Figma UI 阶段完成前先运行：

```powershell
python "${VGAME_SKILL_ROOT}\vgame-figma-ui\scripts\validate_figma_handoff.py" `
  --manifest "${VGAME_OUTPUT_ROOT}\<功能短名>\figma\figma-ui-handoff-manifest.json" `
  --contract "${VGAME_OUTPUT_ROOT}\<功能短名>\00-design-contract.md" `
  --plan "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-ui-plan.md" `
  --target "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-target.json" `
  --require-previews
```

```powershell
python scripts/verify_design_artifacts.py "${VGAME_OUTPUT_ROOT}/<功能短名>" --profile <档位>
```
