# Vgame Agent Skill Integration Guide

## 目标

把本仓库的设计流程与 Vgame 项目专项 skill 接起来，让智能体在回答策划问题时有稳定路线。

## Skill 根目录

```text
${VGAME_SKILL_ROOT}
```

关键文件：

- `config.toml` — 项目 Skill 路由配置
- `agents/` — Agent 定义
- `vgame-core-understanding/` — 入口 Skill
- `vgame-*` — 18 个 Vgame 专项 Skill
- `generic/` — 16 个通用框架模板（不绑定项目，供新项目初始化或方法论参考）

## 使用顺序

1. 先读 `vgame-core-understanding`，确认问题属于哪个设计域。
2. 涉及配置字段时读 `vgame-config-schema`。
3. 根据问题进入专项 skill。
4. 如果分析过程中发现新经验或坑点，补回对应 skill 的 references。
5. 如果会影响长期设计或流程，补到本仓库的 `design/`、`proposals/` 或 `tech-debt-tracker.md`。

## 常见路由

| 用户问题 | 读取路线 |
|---|---|
| 某玩法什么时候开放 | `vgame-core-understanding` -> `vgame-level-progression-map` -> `vgame-config-schema` |
| 奖励要怎么改 | `vgame-core-understanding` -> `vgame-reward-drop-sync` -> `vgame-config-schema` |
| 道具从哪来花到哪去 | `vgame-economy-source-map` -> `senior-game-economy` |
| 角色强弱怎么判断 | `vgame-battle-tuning-helper` -> `vgame-character-kit-design-map` -> `vgame-hero-skill-config-map` |
| 外循环是否闭环 | `vgame-outer-loop-system-map` -> `vgame-economy-source-map` -> `vgame-growth-combat-conversion-map` |
| 配置是否有错 | `vgame-config-quality-audit` -> `vgame-config-schema` |

## 回写规则

| 发现内容 | 回写位置 |
|---|---|
| 字段含义、表关联 | 对应 skill reference |
| 只读审查流程 | `vgame-config-quality-audit` 或本仓库 `harness/` |
| 系统级设计 | 本仓库 `design/` |
| 落地改造方案 | 本仓库 `proposals/` |
| 待确认坑点 | `tech-debt-tracker.md` |

## 只读优先

默认不修改真实配置表。用户明确要求写表时，必须先输出：

- 将修改哪些表。
- 影响哪些字段和引用。
- 如何验证。
- 如何回滚。
