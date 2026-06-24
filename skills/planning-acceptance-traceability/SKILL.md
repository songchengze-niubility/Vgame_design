---
name: planning-acceptance-traceability
description: 把冻结后的游戏策划规则转成 Given-When-Then 验收用例，并建立规则、UI、配置、实现、Excel 和测试证据的追踪矩阵。用户说验收标准、测试用例、规则对账、追踪矩阵、如何证明完成时使用。
---

# 策划验收与追踪矩阵

1. 读取契约、核心设计、专项结果、评审、当前档位对应的 UI/Figma Manifest 和正式 Excel 证据。
2. 使用 [追踪矩阵模板](references/traceability-matrix-template.md) 生成 `05-traceability-matrix.md`。
3. 使用 [验收用例模板](references/acceptance-cases-template.md) 生成 `06-acceptance-cases.md`。
4. 每个核心规则 ID 至少关联一个验收用例；每个验收用例必须反向关联规则 ID。
5. 场景覆盖成功、失败、边界、刷新、过期、重复操作、断线重连和适用的奖励异常。
6. Then 必须是玩家、日志、状态、资源、页面或数据可以观察到的结果。
7. 发现无法验收的规则时，不自行补规则，退回原责任角色。
8. 运行：

   `python scripts/update_planning_workflow_state.py --feature "<功能名>" --phase acceptance --outcome success --actor acceptance-designer --approve-acceptance`
