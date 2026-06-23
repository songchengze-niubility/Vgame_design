# Vgame Design Roadbook

> 本文件是 Vgame 驾驭工程的唯一计划索引。原 `PLANS.md` 已并入此处，`plans/` 目录不再保留。

## 当前阶段

| 阶段 | 目标 | 状态 |
|---|---|---|
| P0 | 建立 Vgame design harness 框架 | 已完成 |
| P1 | 接入 Vgame skill 与项目知识图谱 | 已完成 |
| P2 | 建立核心系统 Design Doc 索引 | 进行中 |
| P3 | 建立配置质量与数值验证常规门禁 | 进行中 |

## 近期路线

| 优先级 | 事项 | 产物 |
|---|---|---|
| P1 | 核心系统地图 | `design/` 下的系统 Design Doc |
| P1 | 配置链审查标准 | `harness/maintenance-gates.md`、`vgame-config-quality-audit` 联动 |
| P2 | 战斗强度标杆与量化流程 | 角色强度评价 Design/Proposal |
| P2 | 资源产销常规追踪流程 | 经济来源去向 Design/Proposal |

## 流转规则

- 新系统先进入 `design/`。
- 已定方向进入 `proposals/`。
- 可执行事项进入 `tasks/`。
- 跨仓信息记录到 `CROSS-REPO-CHANGES.md`。

## 维护节奏

- 每次新增大型设计：补 `design/`。
- 每次跨系统改动：补 `proposals/` 和 `tasks/`。
- 每次发现 skill 判断坑点：回写对应 skill，并在提案或债务记录中标注。
- 每个版本结束：更新 `quality-score.md` 与 `tech-debt-tracker.md`。
