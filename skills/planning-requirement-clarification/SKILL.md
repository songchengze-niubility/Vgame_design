---
name: planning-requirement-clarification
description: 将游戏策划需求契约中的歧义、缺口和方向分歧整理为澄清队列，并与用户每次只确认一个带选项的问题。用户说需求澄清、逐条确认、边界怎么定、还有哪些问题、需求没想清楚时使用。
---

# 策划需求逐条澄清

1. 读取 `00-design-contract.md`、`01-project-reference.md` 和已有 `00-clarification-log.md`。
2. 区分：
   - 可从项目证据核验的事实。
   - 可显式记录的低风险工作假设。
   - 必须由用户决定的方向性问题。
3. 仅将第三类加入队列，编号 `Q-001` 起。
4. 对用户每次只展示一个问题，提供 2 至 4 个互斥选项、影响和推荐。
5. 用户回答后立即更新澄清日志和需求契约，再进入下一题。
6. 队列为空后运行：

   `python scripts/update_planning_workflow_state.py --feature "<功能名>" --phase clarification --outcome success --actor requirement-clarifier --resolve-clarifications`

使用 [澄清日志模板](references/clarification-log-template.md)。关键体验、范围、经济投放和版本目标不得由 Agent 静默决定。
