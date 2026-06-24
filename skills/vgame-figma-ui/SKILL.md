---
name: vgame-figma-ui
description: 将已评审通过的 Vgame 策划规则和 UI 规格制作成可由 UI/UE、策划与程序继续编辑的 Figma 游戏界面、组件库、交互流和程序交接清单。用户要求正式可编辑 UI、Figma 源文件、游戏 HUD/菜单、组件变体、切图标记、开发交接或从 HTML 原型升级为 Figma 交付时使用；不要用于仅需 HTML 示意图或直接修改 Unity Prefab 的任务。
---

# Vgame 可编辑 Figma UI

把已冻结的策划 UI 转成结构化 Figma 源文件，而不是静态截图或铺满位图的画板。交付目标是让 UI/UE 能继续设计，让程序能读取尺寸、状态、资源与规则映射。

## 强制依赖

1. 先读取 `vgame-core-understanding`，按知识图谱定位项目事实并回源确认正式 UI、字体、素材和术语。
2. `figma_ui_plan_confirmed` 通过后，Figma 写入前必须加载 `figma:figma-use`。
3. 创建或更新完整页面时同时加载 `figma:figma-generate-design`。
4. 创建变量、组件或状态变体时同时加载 `figma:figma-generate-library`。
5. 使用 `game-studio:game-ui-frontend` 约束游戏视野保护、信息层级与动效；只采用其游戏设计原则，不照搬浏览器 DOM 实现。
6. 需要新建 Figma 文件时，调用 `create_new_file` 前必须加载 `figma:figma-create-new-file`。

## 输入与门禁

读取同一功能目录中的：

- `00-design-contract.md`
- `01-project-reference.md`
- `02-core-design.md`
- `03-specialist-results/ui-spec.md`
- `03-specialist-results/figma-ui-plan.md`（若已生成）
- `03-specialist-results/figma-target.json`（若已生成）
- `04-review.md`
- 已存在时读取 `ui/ui-asset-manifest.json` 与 HTML 原型，但只把它们作为流程证据。

只有 `review_approved` 已通过才可提出正式 UI 方案；只有用户明确通过 `figma_ui_plan_confirmed` 与 `figma_target_confirmed` 后才可写入 Figma。三个门禁相互独立，不得用评审通过、笼统的“继续”、历史文件或最近打开的 Figma 页面推断方案或写入目标已批准。缺少页面 ID、组件 ID、既有规则 ID、目标视口或关键状态时，退回契约/UI 规格，不自行补号。

开始前确认：

- 使用已有 Figma 文件还是新建文件；优先使用团队已有设计文件和组件库。
- 文件所属 Figma plan；存在多个 plan 时由用户选择。
- 目标平台、参考分辨率、安全区、输入方式与语言压力测试范围。
- 交付是否只包含设计源文件，还是还要求程序切图包。

## 工作流

### 1. 只读发现与映射

1. 检查现有 Figma 文件、订阅库、组件、变量和页面命名。
2. 通过 Vgame 工程回源确认对应 Prefab、缓存预览、UIAtlas、字体和术语；不得把相似资源说成正式现状。
3. 建立 `规则 ID -> PAGE/COMP ID -> Figma node -> 交互状态 -> 导出资产` 映射。
4. 确定需要复用、包装或新建的组件。禁止在未搜索现有库前重画通用组件。
5. 本阶段只允许 Figma 只读查询与截图。禁止调用 `use_figma`、`create_new_file`、`generate_figma_design`、`upload_assets` 以及任何 Code Connect 写入工具。

### 2. UI 方案确认门禁

1. 复制 `assets/figma-ui-plan.template.md`，生成 `03-specialist-results/figma-ui-plan.md`。
2. 方案必须列出正式风格依据、页面信息架构、关键布局、组件/变体、设计变量、交互流、适配、安全区、输入方式、动效、导出范围和未确定项。
3. 向用户展示方案摘要、主要取舍和证据路径；没有正式 UI 依据时明确标记工作假设，不得声称“沿用 Vgame 正式风格”。
4. 输出 `figma_ui_plan / waiting_human` 状态并停止所有 Figma 写入。
5. 只有用户明确批准当前版本后，才把方案状态改为 `approved`，记录批准证据并设置 `figma_ui_plan_confirmed=true`。方案内容变化后必须重新确认。
6. 方案通过后进入 `figma_target`，仍不得写入 Figma 内容。

等待确认时使用：

```planning-workflow-gate
{"actor":"figma-ui-designer","phase":"figma_ui_plan","outcome":"waiting_human","next_action":"approve_ui_plan","evidence":"03-specialist-results/figma-ui-plan.md"}
```

### 3. Figma 写入目标确认门禁

1. 复制 `assets/figma-target.template.json`，生成 `03-specialist-results/figma-target.json`。
2. 记录并展示准确的 Figma design URL、file key、目标 page/node、文件来源以及访问验证结果。禁止使用“当前文件”“最近文件”或猜测的 file key。
3. 只有用户明确批准展示出的目标地址后，才设置 `figma_target_confirmed=true` 并记录批准证据；目标 URL、file key 或 page/node 变化时立即关闭门禁并重新确认。
4. 若需要新建文件，先确认 Figma plan/project 和文件名；只允许创建空文件。获得 URL 后停止，不得在同一步写入 UI 内容；先填写目标文件并请用户确认准确 URL。
5. 首次内容写入前同时校验 UI 方案和目标地址；返回非零时禁止调用任何 Figma 写工具：

```powershell
python "${VGAME_SKILL_ROOT}\vgame-figma-ui\scripts\check_figma_write_gate.py" `
  --plan "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-ui-plan.md" `
  --target "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-target.json"
```

等待目标确认时使用：

```planning-workflow-gate
{"actor":"figma-ui-designer","phase":"figma_target","outcome":"waiting_human","next_action":"confirm_figma_target","evidence":"03-specialist-results/figma-target.json"}
```

### 4. 建立游戏 UI 基础与组件库

按 `figma-generate-library` 的检查点顺序执行：

1. 创建或复用颜色、文字、间距、圆角、安全区、层级和动效变量。
2. 为组件建立真实变体：默认、聚焦/选中、按下、禁用、锁定、加载、错误、成功等，仅覆盖适用状态。
3. 用 Auto Layout、变量绑定和组件属性保证可编辑；正文文字保持 TEXT，图标保持 VECTOR 或可替换实例。
4. 对游戏界面额外定义手柄焦点、输入提示、长文本/本地化、动态背景可读性和安全区规则。
5. 在每个组件检查点用截图验证，并等待用户确认后继续。

### 5. 搭建正式页面与交互流

1. 页面 Frame 名以契约 ID 开头，例如 `PAGE-001/爬塔主界面`。
2. 组件 Set 名以组件 ID 开头，例如 `COMP-003/开始挑战按钮`。
3. 页面使用组件实例组合，不得复制脱离组件库的散装图层。
4. 逐页实现入口、返回、弹窗、页签、选中、冲突、失败和结算等已冻结流程。
5. 保持玩法中心视野清晰；大段说明、次要信息和低频操作使用分层披露。
6. 每完成一页，检查整页和关键局部截图，修复截字、遮挡、占位文本和错误变体。

### 6. 程序与 UI/UE 交接

在 Figma 文件中建立交接页，并在功能输出目录生成：

```text
figma/
├─ figma-ui-handoff-manifest.json
├─ figma-ui-handoff-report.md
└─ previews/
   ├─ page-*.png
   └─ component-*.png
```

交接页至少包含：

- Figma 文件、页面和组件节点链接。
- 基准分辨率、安全区与适配策略。
- 组件状态、焦点顺序、交互说明和规则 ID。
- 导出格式、倍率、命名、是否允许染色，以及九宫格边界说明。
- 字体、图标、图片来源与授权状态。
- 动效时长、触发与可降级方案。
- 未确定项、需程序实现项及明确非目标。

Figma 交付不等于 Unity Prefab。九宫格、Canvas 锚点、Binder 和 Lua 绑定必须作为程序交接说明记录，不能伪装成已完成的引擎实现。

### 7. 校验

1. 用 Figma metadata 检查页面、组件、实例、变量绑定和节点 ID。
2. 用 Figma screenshot 检查每个正式页面及关键组件状态。
3. 复制 `assets/figma-ui-handoff-manifest.template.json` 和 `assets/figma-ui-handoff-report.template.md`，填写本次节点、规则映射与 UI 方案批准证据。
4. 运行：

```powershell
python "${VGAME_SKILL_ROOT}\vgame-figma-ui\scripts\validate_figma_handoff.py" `
  --manifest "${VGAME_OUTPUT_ROOT}\<功能短名>\figma\figma-ui-handoff-manifest.json" `
  --contract "${VGAME_OUTPUT_ROOT}\<功能短名>\00-design-contract.md" `
  --plan "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-ui-plan.md" `
  --target "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-target.json" `
  --require-previews
```

5. 运行仓库门禁。校验失败时留在 `figma_ui` 阶段。

详细字段和交付质量要求见 [Figma 游戏 UI 交付契约](references/figma-game-ui-handoff-contract.md)。

## 完成条件

- Figma 文件可访问，页面、组件、变量和交互均可继续编辑。
- `figma-ui-plan.md` 已获用户明确批准，且写入发生在批准之后。
- `figma-target.json` 已锁定准确 URL/file key/page 或 node，获用户明确批准，且最终 Manifest 与其一致。
- 所有契约页面与关键状态有 Figma node ID 和预览图。
- 组件实例未无故脱离，存在 token 时不硬编码重复视觉值。
- Manifest 可解析、无重复或断链，并只沿用契约中的规则 ID。
- 程序交接页包含切图、九宫格、适配、状态和未落地边界。
- 用户完成视觉与交互人工确认；Agent 不得代替用户设置最终验收通过。

阶段状态使用：

```planning-workflow-gate
{"actor":"figma-ui-designer","phase":"figma_ui","outcome":"success","next_action":"excel","evidence":"Figma URL + figma/figma-ui-handoff-manifest.json"}
```
