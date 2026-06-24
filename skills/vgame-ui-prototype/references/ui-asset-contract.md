# UI 资产契约

## 目录

- [目录结构](#目录结构)
- [HTML 标记](#html-标记)
- [Manifest 结构](#manifest-结构)
- [命名规则](#命名规则)
- [状态覆盖](#状态覆盖)

## 目录结构

```text
ui/
├─ index.html
├─ page-001.png
├─ component-001-default.png
├─ component-001-disabled.png
└─ ui-asset-manifest.json
```

允许 `ui/assets/` 保存本地字体、图片或脚本，但 `index.html` 必须使用相对路径引用。

## HTML 标记

页面：

```html
<main
  data-ui-kind="page"
  data-ui-id="PAGE-001"
  data-rule-ids="R-01 R-04">
</main>
```

组件：

```html
<section
  data-ui-kind="component"
  data-ui-id="COMP-003"
  data-page-id="PAGE-001"
  data-rule-ids="R-04">
</section>
```

同一截图目标的 `data-ui-id` 在 DOM 中必须唯一。不同交互状态可以复用组件 ID，但截图时应通过 `state` 和文件名区分。

## Manifest 结构

顶层字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `schema_version` | 是 | 当前固定为 `1.0` |
| `source_html` | 是 | 固定为 `index.html` |
| `viewport` | 是 | 截图视口 `width`、`height`、`device_scale_factor` |
| `pages` | 是 | 页面截图记录数组，至少一条 |
| `components` | 是 | 组件截图记录数组 |

页面记录：

```json
{
  "id": "PAGE-001",
  "name": "活动主页面",
  "file": "page-001.png",
  "selector": "[data-ui-kind='page'][data-ui-id='PAGE-001']",
  "state": "default",
  "rule_ids": ["R-01", "R-04"]
}
```

组件记录：

```json
{
  "id": "COMP-003",
  "name": "领取按钮",
  "page_id": "PAGE-001",
  "file": "component-003-disabled.png",
  "selector": "[data-ui-kind='component'][data-ui-id='COMP-003']",
  "state": "disabled",
  "rule_ids": ["R-04"]
}
```

同一组件可以有多条不同 `state` 的记录。记录唯一键是 `id + state`，文件路径必须全局唯一。

## 命名规则

- 页面 ID：`PAGE-001` 起，契约内稳定不复用。
- 组件 ID：`COMP-001` 起，契约内稳定不复用。
- 规则 ID：原样沿用 `00-design-contract.md` 中已有格式（例如 `R-01` 或 `RULE-001`），不得为 UI 重新编号。
- 页面图片：`page-<页面ID序号小写>.png`，类型前缀不重复。
- 组件图片：`component-<组件ID序号小写>-<状态>.png`，类型前缀不重复。
- 状态使用英文小写短名：`default`、`empty`、`loading`、`error`、`disabled`、`selected`、`success`。

## 状态覆盖

按组件与流程适用性覆盖，而不是机械生成全部状态：

| 状态 | 最低可观察结果 |
|---|---|
| `default` | 信息层级、主要入口和默认数据可读 |
| `empty` | 说明为何为空并给出下一步 |
| `loading` | 防止重复操作并提供明确反馈 |
| `error` | 说明失败对象并提供恢复操作 |
| `disabled` | 视觉与交互均不可触发，原因可理解 |
| `selected` | 当前选择清晰，切换结果一致 |
| `success` | 操作结果与资源/状态变化可见 |

策划案嵌图优先使用能解释规则的页面主图和关键组件状态，不要只嵌入装饰性局部图。
