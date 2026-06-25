---
name: vgame-figma-ui
description: 将已评审通过的 Vgame 策划规则和 UI 规格制作成可由 UI/UE、策划与程序继续编辑的 Figma 游戏界面、组件库、Prototype 交互流和程序/UE/UMG 交接清单。用户要求正式可编辑 UI、Figma 源文件、游戏 HUD/菜单、组件变体、切图标记、UE/UMG 或 Unity/uGUI 开发交接，或从 HTML 原型升级为 Figma 交付时使用；不要用于仅需 HTML 示意图或直接修改引擎 Prefab/Widget Blueprint 的任务。
---

# Vgame 可编辑 Figma UI

把已冻结的策划 UI 转成结构化 Figma 源文件，而不是静态截图或铺满位图的画板。交付目标是让 UI/UE 能继续设计，让程序能读取尺寸、状态、资源、原型跳转与规则映射。

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

### 6. 从可编辑样稿升级为程序/UE 交接

当用户追问“这是不是原型图”“能否交付给程序/UE”“做成可编辑 UI”时，先澄清交付档位：

- UI 示意图：HTML/PNG 或 Figma 静态画面，只用于评审视觉与布局。
- 可编辑 Figma 源：页面、组件、变量、TEXT、状态变体和实例关系可继续编辑。
- Prototype 交接稿：关键按钮、页签或流程节点已建立 Figma Prototype 连接。
- 程序/UE 交接稿：额外包含 UMG/Widget 命名建议、锚点、安全区、焦点顺序、九宫格、导出边界、运行时绑定和非目标说明。
- 引擎实现：真正的 Widget Blueprint/Prefab、Lua/业务绑定、运行时状态机；本 skill 不直接声明已完成。

升级流程：

1. 保留已批准页面和组件实例，不把页面压成 PNG；不得 detach 已批准组件，除非记录原因。
2. 若关键路径需要跳转但目标正式页面不在当前批准范围内，可创建 `PAGE-xxx/.../Prototype Target Placeholder` 占位帧；必须写明“非最终 UI”，并只使用契约已有 PAGE ID 和规则 ID。`FLOW-*` 仅作为 Manifest 本地交互记录，不是规则 ID。
3. 给真实入口节点建立 Figma Prototype reaction，例如主 CTA `ON_CLICK -> PAGE-xxx Prototype Target Placeholder`，并在 Manifest `flows` 中记录 from/to/trigger/rule_ids。
4. 在 Figma 文件中创建 `UE-HANDOFF/<PAGE-ID>/程序交接说明` 或同等交接板，包含：
   - UE/UMG Widget 命名建议（如 `WBP_*`）、关键 Button/List/Panel 实例名。
   - Canvas/Overlay 锚点、安全区、横竖屏或宽窄屏策略。
   - 键鼠、手柄、触控适用范围与焦点顺序。
   - 九宫格/可拉伸区域；当前为 shape 时说明无需切图，若替换 UIAtlas 贴图再切。
   - 运行时绑定字段、点击回调、状态枚举和非目标。
5. 导出正式页面、关键组件、Prototype 目标占位和交接板 PNG；PNG 只作为评审/追踪，不作为运行时 UI 替代品。
6. 生成或更新 `figma-ui-handoff-manifest.json`、`figma-ui-handoff-report.md`；若目标是 UE/UMG，再生成 `ue-ui-asset-manifest.json`。
7. 明确边界：Figma 交接稿不等于 UE Widget Blueprint、Unity Prefab、Binder、Lua 或运行时实现。

### 7. 程序与 UI/UE 交接

在 Figma 文件中建立交接页，并在功能输出目录生成：

```text
figma/
├─ figma-ui-handoff-manifest.json
├─ figma-ui-handoff-report.md
├─ ue-ui-asset-manifest.json（UE/UMG 交付时）
└─ previews/
   ├─ page-*.png
   ├─ component-*.png
   └─ ue-handoff-*.png
```

交接页至少包含：

- Figma 文件、页面和组件节点链接。
- 基准分辨率、安全区与适配策略。
- 组件状态、焦点顺序、交互说明和规则 ID。
- 导出格式、倍率、命名、是否允许染色，以及九宫格边界说明。
- 字体、图标、图片来源与授权状态。
- 动效时长、触发与可降级方案。
- 未确定项、需程序实现项及明确非目标。

Figma 交付不等于 UE Widget Blueprint 或 Unity Prefab。九宫格、Canvas/Overlay 锚点、UMG/Prefab 层级、Binder 和 Lua/业务绑定必须作为程序交接说明记录，不能伪装成已完成的引擎实现。

### 8. 校验

1. 用 Figma metadata 检查页面、组件、实例、变量绑定和节点 ID。
2. 用 Figma screenshot 检查每个正式页面及关键组件状态。
3. 读取 Prototype 入口节点，确认关键 reaction 的 trigger、destinationId 和 navigation 已写入。
4. 复制 `assets/figma-ui-handoff-manifest.template.json` 和 `assets/figma-ui-handoff-report.template.md`，填写本次节点、规则映射与 UI 方案批准证据。UE/UMG 交付时同时复制 `assets/ue-ui-asset-manifest.template.json`。
5. 运行：

```powershell
python "${VGAME_SKILL_ROOT}\vgame-figma-ui\scripts\validate_figma_handoff.py" `
  --manifest "${VGAME_OUTPUT_ROOT}\<功能短名>\figma\figma-ui-handoff-manifest.json" `
  --contract "${VGAME_OUTPUT_ROOT}\<功能短名>\00-design-contract.md" `
  --plan "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-ui-plan.md" `
  --target "${VGAME_OUTPUT_ROOT}\<功能短名>\03-specialist-results\figma-target.json" `
  --require-previews
```

6. 对 `ue-ui-asset-manifest.json`、构建状态账本等新增 JSON 运行可解析检查；预览 PNG 应存在且可读。
7. 运行仓库门禁。校验失败时留在 `figma_ui` 阶段。

详细字段和交付质量要求见 [Figma 游戏 UI 交付契约](references/figma-game-ui-handoff-contract.md)。

## 完成条件

- Figma 文件可访问，页面、组件、变量和交互均可继续编辑。
- `figma-ui-plan.md` 已获用户明确批准，且写入发生在批准之后。
- `figma-target.json` 已锁定准确 URL/file key/page 或 node，获用户明确批准，且最终 Manifest 与其一致。
- 所有契约页面与关键状态有 Figma node ID 和预览图。
- 组件实例未无故脱离，存在 token 时不硬编码重复视觉值。
- Manifest 可解析、无重复或断链，并只沿用契约中的规则 ID。
- 程序交接页包含切图/不切图边界、九宫格、适配、状态、Prototype flow、UE/UMG 或 Unity/uGUI 命名建议和未落地边界。
- 用户完成视觉与交互人工确认；Agent 不得代替用户设置最终验收通过。

阶段状态使用：

```planning-workflow-gate
{"actor":"figma-ui-designer","phase":"figma_ui","outcome":"success","next_action":"excel","evidence":"Figma URL + figma/figma-ui-handoff-manifest.json"}
```
