# Vgame Design Roadbook

## 近期路线

| 优先级 | 事项 | 产物 |
|---|---|---|
| P0 | Harness 基础框架 | `harness/`、入口文档、门禁脚本 |
| P0 | Skill 接入说明 | `harness/integration-guide.md` |
| P1 | 核心系统地图 | `design/` 下的系统 Design Doc |
| P1 | 配置链审查标准 | `harness/maintenance-gates.md`、`vgame-config-quality-audit` 联动 |
| P2 | 战斗强度标杆与量化流程 | 角色强度评价 Design/Proposal |
| P2 | 资源产销常规追踪流程 | 经济来源去向 Design/Proposal |

## 维护节奏

- 每次新增大型设计：补 `design/`。
- 每次跨系统改动：补 `proposals/` 和 `tasks/`。
- 每次发现 skill 判断坑点：回写对应 skill，并在提案或债务记录中标注。
- 每个版本结束：更新 `quality-score.md` 与 `tech-debt-tracker.md`。

