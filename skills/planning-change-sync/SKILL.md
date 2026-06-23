---
name: planning-change-sync
description: 在游戏策划需求、规则、数值、配置、UI 或实现发生变化后，分析影响并同步契约、设计、UI、Excel、验收用例和追踪矩阵。用户说需求改了、版本调整、同步改动、配置变化、补变更记录时使用。
---

# 策划需求变更同步

1. 读取需求契约、澄清日志、全部设计产物、追踪矩阵和已有 `07-change-log.md`。
2. 为变更分配 `CHG-xxx`，记录旧规则、新规则、不变项、原因、提出人和版本。
3. 使用 [变更记录模板](references/change-log-template.md) 列出影响：
   - 规则 ID。
   - 页面/组件与 UI 资产。
   - 数值、配置表和字段。
   - 实现模块。
   - Excel 章节和图片。
   - 验收用例和追踪矩阵。
4. 范围、核心体验或经济模型变化时，退回契约确认和一致性评审。
5. 仅局部表现或文案变化时，只回到受影响阶段。
6. 所有同步项必须有实际文件路径或验证证据；禁止仅勾选“已同步”。
7. 完成后更新状态：

   `python scripts/update_planning_workflow_state.py --feature "<功能名>" --phase change_sync --outcome success --actor change-sync-reviewer --close-change`
