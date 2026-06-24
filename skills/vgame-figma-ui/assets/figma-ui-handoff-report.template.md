# <功能短名> Figma UI 交接报告

## 交付入口

- Figma 文件：<URL>
- 文件 Key：<file_key>
- 参考分辨率：<width>x<height>
- 目标引擎：Unity 2022.3 uGUI
- 规则来源：`../00-design-contract.md`
- UI 方案：`../03-specialist-results/figma-ui-plan.md`
- 方案批准证据：<用户明确批准记录>
- Figma 目标：`../03-specialist-results/figma-target.json`
- 目标地址批准证据：<用户明确批准准确 URL 的记录>

## 页面与流程

| PAGE ID | 页面 | Figma node | 覆盖规则 | 关键入口/出口 | 预览 |
|---|---|---|---|---|---|
| PAGE-001 |  |  | R-xx |  | `previews/page-001.png` |

## 组件与状态

| COMP ID | 组件 | Component Set node | 状态/变体 | 覆盖规则 | 是否导出 |
|---|---|---|---|---|---|
| COMP-001 |  |  | default / focused / disabled | R-xx | 否 |

## 适配与输入

- 安全区：
- 宽屏/窄屏策略：
- 键鼠：
- 手柄焦点顺序：
- 触控：
- 本地化压力测试：

## 程序资源交接

| Figma node | Unity 建议名称/目录 | 格式与倍率 | 染色 | 九宫格 | 备注 |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 动效与降级

| 对象 | 触发 | 时长/曲线 | 降级方案 |
|---|---|---|---|
|  |  |  |  |

## 未解决项与边界

- 未解决项：无 / <逐条列出>
- 需程序实现：Canvas 锚点、Prefab、Binder、Lua 绑定及运行时状态。
- 非目标：本报告不证明 Unity 实现已经完成。

## 人工确认

- [ ] UI/UE 已确认可编辑性与视觉
- [ ] 程序已确认资源、状态和交互说明可实现
- [ ] 策划已确认规则 ID 与页面/组件映射
- [ ] 用户已完成最终视觉与交互验收
