# Figma 游戏 UI 交付契约

## 目录

- [交付边界](#交付边界)
- [Figma 文件结构](#figma-文件结构)
- [可编辑性要求](#可编辑性要求)
- [游戏专项要求](#游戏专项要求)
- [Manifest 结构](#manifest-结构)
- [程序交接要求](#程序交接要求)

## 交付边界

Figma 交付负责可编辑设计源、组件、状态、交互与程序说明；不宣称已经生成 Unity Prefab、Canvas 锚点、ObjectBinder、`_Auto.lua` 或业务 Lua。

静态 PNG 只用于评审和追踪，不能替代 Figma 源文件。不得把完整页面压成一张图片后称为可编辑 UI。

## 写入前方案门禁

- `review_approved` 只代表规则可以进入正式 UI，不代表视觉和交互方案已获批准。
- 写入 Figma 前必须生成 `03-specialist-results/figma-ui-plan.md`，并由用户明确确认当前方案版本。
- 门禁确认前只允许读取 Figma metadata、design context、variables、libraries、screenshots 和设计系统搜索结果。
- 门禁确认前禁止新建文件、创建/修改/删除节点、上传资产、捕获页面或写入 Code Connect。
- 方案批准后发生页面范围、视觉方向、组件策略或交互路径变化时，退回 `figma_ui_plan` 重新确认。

## 写入目标门禁

- UI 方案批准后仍不得直接写入；必须生成并确认 `03-specialist-results/figma-target.json`。
- 目标记录必须包含准确的 Figma design URL、file key、目标 page/node、来源、访问验证结果和用户批准证据。
- 最近打开的文件、当前浏览器标签、猜测的 file key 和只给文件名都不构成有效地址。
- 新建文件时，只允许先创建空文件。取得 URL 后停止并请用户确认；确认前不得向空文件写入 UI 内容。
- URL、file key 或目标 page/node 改变后，`figma_target_confirmed` 立即失效。

## Figma 文件结构

推荐页面结构；复用已有文件时匹配其既有规范：

```text
00 Cover & Handoff
01 Foundations
02 Components
03 Screens
04 Prototype Flow
05 Export Specs
```

要求：

- 正式页面名以 `PAGE-*` 开头。
- 组件或 Component Set 名以 `COMP-*` 开头。
- 页面和组件描述包含原有规则 ID，不为 Figma 重编号。
- 远程组件保持实例关系；只有明确记录原因时才允许 detach。
- 页面节点、组件节点和可导出资产均使用稳定、可读名称。

## 可编辑性要求

- 结构：相关元素使用 Auto Layout；避免无语义的 Group 堆叠。
- 文字：正文与标签保持 TEXT，加载并保留正确字体，不轮廓化。
- 图标：优先 VECTOR 或 INSTANCE_SWAP，不用字符/emoji 冒充。
- 图片：背景、插画和头像可使用 IMAGE fill，但不能吞掉可编辑文字与控件。
- 变量：颜色、间距、圆角、字号和常用尺寸尽量绑定变量。
- 组件：按钮、页签、弹窗、列表项、奖励项、角色槽等使用组件与变体。
- 状态：交互状态使用组件属性或变体表达，不靠页面旁文字代替。
- 原型：关键路径必须建立 Prototype 连接；不可达页面需注明原因。

## 游戏专项要求

- 视野：普通游戏态中心与下中区域不得被低优先级信息长期占用。
- 安全区：记录标题安全区、动作安全区和可调整策略；不要把关键内容贴屏幕边缘。
- 输入：列出键鼠、手柄、触控的适用范围与焦点顺序。
- 提示：输入图标按 Action 语义设计，不能把某个平台按键写死为唯一方案。
- 可读性：在亮、暗、动态和高特效背景上验证 HUD 文字与关键数值。
- 无障碍：颜色信息需有形状、图标或文字冗余；强动效需有降级方案。
- 本地化：用长文本和数字极值做压力测试，避免只验证短中文。
- 适配：至少记录基准分辨率、宽屏/窄屏策略、缩放与锚点意图。

## Manifest 结构

顶层必填：

| 字段 | 说明 |
|---|---|
| `schema_version` | 固定为 `1.0` |
| `feature` | 功能短名 |
| `rule_id_source` | 相对路径，通常为 `../00-design-contract.md` |
| `figma_file` | `file_key`、`url`、`name` |
| `ui_plan` | 方案文件、确认状态和用户批准证据 |
| `figma_target` | 已确认的写入地址文件及确认状态 |
| `reference_viewport` | `width`、`height`、`safe_area_percent` |
| `pages` | 正式页面记录，至少一条 |
| `components` | 关键组件记录，至少一条 |
| `flows` | 关键交互流记录 |
| `handoff` | 程序/UI-UE 交接检查项 |

页面记录：

```json
{
  "id": "PAGE-001",
  "name": "爬塔主界面",
  "node_id": "123:456",
  "url": "https://www.figma.com/design/FILE/NAME?node-id=123-456",
  "state": "default",
  "preview_file": "previews/page-001.png",
  "rule_ids": ["R-01", "R-04"]
}
```

组件记录：

```json
{
  "id": "COMP-003",
  "name": "开始挑战按钮",
  "page_id": "PAGE-002",
  "node_id": "234:567",
  "component_set_node_id": "234:500",
  "states": ["default", "focused", "pressed", "disabled"],
  "preview_file": "previews/component-003.png",
  "rule_ids": ["R-03", "R-09"],
  "export": {
    "required": false,
    "format": null,
    "scales": []
  }
}
```

交互流记录：

```json
{
  "id": "FLOW-001",
  "name": "进入编队",
  "from_page_id": "PAGE-001",
  "to_page_id": "PAGE-002",
  "trigger": "点击编队挑战",
  "rule_ids": ["R-01"]
}
```

## 程序交接要求

`handoff` 至少包含：

```json
{
  "target_engine": "Unity 2022.3 uGUI",
  "editable_source_confirmed": true,
  "component_instances_confirmed": true,
  "prototype_links_confirmed": true,
  "export_specs_confirmed": true,
  "nine_slice_annotations_confirmed": true,
  "safe_area_confirmed": true,
  "localization_stress_tested": true,
  "unresolved_items": []
}
```

每个需导出的视觉资产应说明：

- Figma node ID 与显示名称。
- 建议 Unity 资源名和目录。
- PNG/SVG 等格式、倍率和透明背景要求。
- 是否允许运行时染色。
- 九宫格不可拉伸区域与边界数值。
- 是否包含字体或需使用 TextEx/TMP 渲染。

Manifest 只证明交接信息存在，不证明 Unity 实现已经完成。
