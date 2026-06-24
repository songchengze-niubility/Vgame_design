# <功能短名> Figma UI 方案

## 门禁状态

- 状态：`draft`
- 人工门禁：`figma_ui_plan_confirmed=false`
- 方案版本：`v1`
- 批准人：待确认
- 批准时间：待确认
- 批准证据：待确认

```planning-workflow-gate
{"actor":"figma-ui-designer","phase":"figma_ui_plan","outcome":"waiting_human","next_action":"approve_ui_plan","evidence":"等待用户确认本方案"}
```

用户明确批准后，将状态改为 `approved`、门禁改为 `true`，补齐批准证据，并把状态块改为 `outcome: success`、`next_action: figma_ui`。不得提前填写。

## 正式风格依据

| 证据 | 文件/Figma node | 已观察内容 | 本方案如何沿用 | 状态 |
|---|---|---|---|---|
| EV-UI-001 |  |  |  | 已观察/待确认 |

## 页面方案

| PAGE ID | 页面 | 核心目的 | 信息层级与布局 | 入口/出口 | 覆盖规则 |
|---|---|---|---|---|---|
| PAGE-001 |  |  |  |  | R-xx |

## 组件与变量方案

| COMP ID | 组件 | 复用/新建 | 状态与变体 | token/变量 | 覆盖规则 |
|---|---|---|---|---|---|
| COMP-001 |  |  | default / focused / disabled |  | R-xx |

## 交互与游戏专项

- 核心交互流：
- 参考分辨率与安全区：
- 宽屏/窄屏策略：
- 键鼠/手柄/触控范围：
- 手柄焦点顺序：
- 本地化压力测试：
- 动效与降级：

## Figma 落点与交付范围

- 目标文件/Plan：
- 复用组件库：
- 新建页面/组件/变量：
- 需要导出的程序资源：
- 不属于本次交付：Unity Prefab、Binder、Lua 绑定及运行时实现。

## 取舍与待确认

- 主要取舍：
- 工作假设：
- 未确定项：
