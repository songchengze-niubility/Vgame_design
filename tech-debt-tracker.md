# Vgame Tech Debt Tracker

| 编号 | 日期 | 类型 | 描述 | 影响 | 负责人 | 状态 |
|---|---|---|---|---|---|---|
| DEBT-0001 | 2026-06-18 | Harness | 初版门禁只检查仓库结构，尚未接入真实配置引用审查 | 中 | 待定 | 打开 |
| DEBT-0002 | 2026-06-18 | 数值模型 | 角色强度模型仍需要更多高置信标杆和实战日志校准 | 高 | 待定 | 打开 |
| DEBT-0003 | 2026-06-24 | 策划流程 | `scripts/verify_design_artifacts.py`（第9步交付总校验）缺失；已提交首版草案，待按真实产物校准规则 ID/嵌图/Manifest 校验项并接入门禁 | 高 | 待定 | 进行中 |
| DEBT-0004 | 2026-06-24 | 策划流程 | `scripts/update_planning_workflow_state.py`：已提交首版草案（阶段/结果/人类门禁/返工计数/历史写入，`--accept-delivery` 为唯一验收入口），待按真实使用校准 | 高 | 待定 | 进行中 |
| DEBT-0005 | 2026-06-24 | 策划流程 | `scripts/planning_workflow_status.py`：已提交首版草案（状态文件 + 实际产物双视图对账，输出状态块），待按真实产物命名校准探测项 | 中 | 待定 | 进行中 |
| DEBT-0006 | 2026-06-24 | 策划流程 | `scripts/check_planning_template_cache.py`：已提交首版草案（读取检查 + `--build` 增量构建，只扫模板源目录）。**工作假设**：索引位置默认 `${VGAME_OUTPUT_ROOT}/.template-index.json`、模板源默认 `${VGAME_SOURCE_DOCS_ROOT}/模板`、主模板按文件名「主/main」识别——三项待用户确认真实约定 | 低 | 待定 | 进行中 |

