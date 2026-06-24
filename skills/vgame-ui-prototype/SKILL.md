---
name: vgame-ui-prototype
description: 将 Vgame 策划需求契约、核心规则和 UI 规格转成可交互 HTML 原型、真实渲染的页面/组件 PNG 与可追踪的 ui-asset-manifest.json。策划交付档位为 UI_ONLY 或 DOC_UI，或用户要求搭建 UI 原型图、页面流程、组件状态、交互演示、策划案嵌图时使用。
---

# Vgame UI 原型

把已冻结的策划规则变成可操作、可截图、可追踪的 UI 资产。不要用静态概念图代替真实渲染原型。

## 输入

1. 先读取 `00-design-contract.md`、`01-project-reference.md`、`02-core-design.md`、`03-specialist-results/ui-spec.md` 和 `04-review.md`。
2. 仅在 `review_approved` 已满足后制作正式 UI；若尚未满足，只补 UI 规格或标记阻塞。
3. 从契约提取页面 ID、组件 ID、规则 ID、玩家路径、正常/空/失败/加载/禁用状态、目标平台和视口。
4. 若已安装 `$frontend-design`，加载它作为视觉设计与前端工艺基线；Vgame 的规则、目录和追踪契约始终以本技能为准。

缺少页面 ID、规则 ID、关键状态或目标视口时，不要臆造正式资产；将缺口写入 `03-specialist-results/ui-spec.md` 并退回需求契约或核心设计。

## 工作流

### 1. 冻结 UI 规格

在 `03-specialist-results/ui-spec.md` 中列出：

- 每个页面：`PAGE-*`、用途、入口、出口、关联既有规则 ID、关键状态。
- 每个组件：`COMP-*`、所属页面、状态、操作、反馈、关联既有规则 ID。
- 视觉方向：题材语汇、色彩、字体、密度、动效语气及一项可辨识特征。
- 目标视口、适配策略、安全区、键鼠/触控/手柄约束。

优先复用项目已有 UI、图标、字体和术语。引用真实项目资源前按 `vgame-core-understanding` 回源确认。

### 2. 构建真实 HTML 原型

在功能输出目录的 `ui/` 下生成 `index.html`。默认使用自包含 HTML/CSS/JS；只有现有工程明确要求时才引入框架。

- 页面根节点标记 `data-ui-kind="page"`、`data-ui-id="PAGE-*"`、`data-rule-ids="R-01 R-02"`。
- 组件根节点标记 `data-ui-kind="component"`、`data-ui-id="COMP-*"`、`data-page-id="PAGE-*"`、`data-rule-ids="R-01"`。
- 用真实交互切换页面和状态；按钮、页签、弹窗、错误、空态与加载态不可只写在说明文字里。
- 保持中心玩法画面、安全区和信息层级；菜单不能伪装成通用 SaaS 仪表盘。
- 使用 CSS 变量组织颜色、字号、间距和层级；提供键盘焦点、可读对比度和 reduced-motion 处理。
- 未确认的数据明确标记为示例或待定，不伪装成项目事实。

### 3. 浏览器校验与截图

通过可用的浏览器控制或 Playwright 打开实际页面，不从源代码直接推断渲染结果。

1. 在目标视口加载 `ui/index.html`。
2. 逐条执行主流程，检查控制台、文本溢出、遮挡、焦点、状态反馈和返回路径。
3. 对每个页面根节点截图为 `page-<页面ID序号小写>.png`，例如 `PAGE-001` 对应 `page-001.png`。
4. 对关键组件根节点截图为 `component-<组件ID序号小写>-<状态>.png`，例如 `COMP-001` 的默认态对应 `component-001-default.png`。
5. 截图必须来自本次 HTML 的实际渲染；不得用图像生成结果冒充页面截图。

若使用本地服务器，结束后停止临时服务。页面包含外部资源时，确认离线或交付环境是否仍可显示。

### 4. 生成 Manifest

复制 `assets/ui-asset-manifest.template.json` 为 `ui/ui-asset-manifest.json`，按 [UI 资产契约](references/ui-asset-contract.md) 填写。

- 每张 PNG 恰好对应一条 Manifest 记录。
- PAGE 记录必须关联页面 ID 和至少一个规则 ID。
- COMPONENT 记录必须关联组件 ID、所属页面 ID、状态和至少一个规则 ID。
- `selector` 必须能在 `index.html` 中唯一定位截图节点。
- Manifest 不保留已删除或已替换资产。

### 5. 校验

运行：

```powershell
python "${VGAME_SKILL_ROOT}\vgame-ui-prototype\scripts\validate_ui_assets.py" --ui-dir "${VGAME_OUTPUT_ROOT}\<功能短名>\ui" --require-components
```

随后执行策划总校验与仓库门禁。校验失败时留在 UI 阶段，不进入正式 Excel。

## 完成条件

- `ui/index.html` 可实际加载并完成核心路径。
- 所有契约页面都有 `page-*.png`；关键组件和状态都有 `component-*.png`。
- `ui-asset-manifest.json` 可解析、无重复 ID/文件、无断链，规则映射完整。
- PNG 来自当前 HTML 的实际渲染，文件非空且尺寸有效。
- 正常、空、加载、失败、禁用和返回路径按适用范围覆盖。
- UI 结果与冻结规则一致；视觉选择不掩盖玩法信息。

输出阶段状态时仍使用工作流角色名 `ui-prototype`：

```planning-workflow-gate
{"actor":"ui-prototype","phase":"ui","outcome":"success","next_action":"excel","evidence":"ui/index.html + ui/ui-asset-manifest.json"}
```

自动校验只证明结构和引用通过；最终视觉、交互与策划表达仍由用户人工验收。
