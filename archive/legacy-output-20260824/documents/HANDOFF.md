# Vgame 项目级策划知识库接力入口

> 更新：2026-08-24  
> 状态：`review/waiting_human`（18 项人工目标已确认；实施和独立复核仍待完成，人工门禁保持 false）

## 当前 canonical

- 45/45 系统完整正文，2 个专业模块（M01/M02）。
- 问题记录共 240：36 P0 / 127 P1 / 77 P2。
- 生命周期：209 `OPEN` / 0 `ANSWERED` / 31 `CLOSED`。
- 责任分流总量：13 `AI_EVIDENCE` / 41 `HUMAN_DECISION` / 118 `RUNTIME_OWNER` / 68 `DEFERRED_DETAIL`。
- 机器统计摘要：209 OPEN / 0 ANSWERED / 31 CLOSED；AI_EVIDENCE 13 / HUMAN_DECISION 41 / RUNTIME_OWNER 118 / DEFERRED_DETAIL 68。
- 18 张决策卡（DC-A–DC-R）已全部确认，每张只关闭其唯一绑定 QID；`HUMAN_DECISION` 为 18 CLOSED / 23 OPEN。
- 剩余开放优先级：19 P0 / 122 P1 / 68 P2；其中 P0 为 HUMAN_DECISION 12、RUNTIME_OWNER 7、DEFERRED_DETAIL 0。
- 所有正式选择均为 `APPROVED_TARGET / HUMAN_DECISION_CONFIRMED / IMPLEMENTATION_PENDING`。

## 证据与边界

- 原始人工输入：`review/decisions/vgame-decision-cards-2026-08-24.json`，SHA-256 `8736877372517ec7a20f4d0996b9b9fb3599d828eb34d83d66d425a433f827f3`；审计元数据见同目录 `.audit.json`。
- 最新映射装备设计源 SHA-256：`d82c7764eb5630db88a0221e73abc7c6e39db677b5479cf587dd3acd97d9b25c`。
- DC-E 用户原话保持为“只有主线、高难需要三星”；其他玩法仅按既有已确认规则处理，否则为 UNKNOWN。
- C-001 的产品目标已确认为“专武线废弃并迁移”，但迁移版本、数据方案、兼容期和工作副本实现仍待完成；不得写成当前正式成长线或 LIVE。
- 当前解锁链、配置和源码仅是 SVN 工作副本观察，不是 Production/LIVE；本轮未修改 `D:\Vgame`。
- `review_approved=false`、`delivery_accepted=false`；`waiting_human` 表示等待独立复核和剩余责任人处理，不等于批准或交付验收。

## 最小阅读路径

1. 根目录 `AGENTS.md`。
2. `review/18项人工裁决同步报告-2026-08-24.md`。
3. `knowledge-base/SYSTEM-DETAIL-SPEC.md` 与 `knowledge-base/decision-card-registry.json`。
4. 原始裁决与审计证据：`review/decisions/`。
5. 查询具体事实时先运行 `skills/vgame-knowledge-router/scripts/route_query.py`，再按最小 readPlan 回源。
