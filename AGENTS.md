# Vgame 策划 Agent 总入口

> 地图而非手册。本文件是智能体入口页，只负责告诉下一步该看什么。
> 具体规则放在 `harness/`，具体设计放在 `design/`，执行计划放在 `proposals/` 与 `tasks/`。

## Quick Start

```text
Design -> Proposal -> Task -> Config/Code
```

1. 有新系统或大改动：先写 `design/<系统名>.md`。
2. 需要评审落地：写 `proposals/<主题>-YYYY-MM-DD.md`。
3. 已批准要执行：拆成 `tasks/<主题>-YYYY-MM-DD.md`。
4. 要改真实配置或代码：先确认来源链路，再回到 `${VGAME_ROOT}` 执行。
5. 提交前：运行 `scripts/check.ps1`。
6. 涉及项目事实：先按 `knowledge-graph/KG-AI-RULES.md` 查图谱，再回源确认。

## 本机工程连接

本仓库是 Codex 新对话的工作目录。开始 Vgame 项目任务前：

1. 读取 `%LOCALAPPDATA%\Vgame\design-harness.env.bat` 或本仓库忽略的 `local.env.bat`。
2. 确认 `${VGAME_ROOT}` 指向当前电脑上的 Vgame SVN 工作副本。
3. 先读取 `skills/vgame-core-understanding/SKILL.md`，再按路由加载专项 Skill。
4. 通过 `${VGAME_CONFIG_DATAS}` 和 `${VGAME_CODE_ROOT}` 读取真实配置与代码。
5. 除非用户明确授权修改，否则将 SVN 工程视为只读。

首次安装、换电脑或路径变化时，运行 `驾驭工程/配置本机路径.bat` 和 `驾驭工程/一键安装.bat`。不要再从 Vgame SVN 目录启动驾驭工程。

## 项目概览

| 维度 | 当前理解 |
|---|---|
| 项目 | Vgame |
| 本仓库 | Vgame 设计/harness/提案/任务/知识图谱/策划Skill 全包 |
| 游戏工程 | `${VGAME_ROOT}` |
| 配置体系 | Excel 配置表为核心源，真实表不直接放入本仓库 |
| Agent skill | `skills/`（本仓库内，入口 `skills/vgame-core-understanding/SKILL.md`） |
| 协作目标 | 让策划、数值、配置、战斗、外循环问题有可追踪的判断链 |

## 仓库关系

```text
<Vgame_design 仓库>        <- 设计约束、提案、任务、知识图谱、策划Skill（全部自包含）
${VGAME_ROOT}              <- 项目工程与真实配置（SVN）
```

策划 Skill 已全部纳入本仓库 `skills/` 目录，不再依赖外部路径。

## 入口文档

| 场景 | 下一步看 |
|---|---|
| 新人安装、Git/SVN 与完整使用流程 | `新人上手指南.md`、`驾驭工程/README.md` |
| 不知道怎么开始 | `harness/concepts/00-overview.md` |
| 需要新增玩法/系统设计 | `DESIGN.md`、`design/TEMPLATE.md` |
| 需要形成落地方案 | `proposals/TEMPLATE.md` |
| 需要拆任务 | `tasks/TEMPLATE.md` |
| 需要看仓库约束 | `golden-principles.md` |
| 需要跑门禁 | `harness/maintenance-gates.md`、`scripts/check.ps1` |
| 涉及跨仓改动 | `CROSS-REPO-CHANGES.md` |
| 涉及 Vgame skill | `skills/vgame-core-understanding/SKILL.md`（入口） |
| 查询代码/配置/文档关系 | `knowledge-graph/README.md`、`knowledge-graph/KG-AI-RULES.md` |
| 更新或查看知识图谱 | `knowledge-graph/知识图谱自动更新方案.md` |

## Vgame Skill 路由

| 问题类型 | 优先 skill |
|---|---|
| 策划案交付、需求澄清、验收追踪 | `planning-feature-workflow`（每次发起需求必须加载） |
| 项目总览、路由、边界 | `vgame-core-understanding` |
| 配置字段、表结构、注册源表 | `vgame-config-schema` |
| 奖励、Drop、UIlevel 同步 | `vgame-reward-drop-sync` / `vgame-drop-uilevel-sync` |
| 关卡、章节、开放、体力、扫荡 | `vgame-level-progression-map` |
| 道具产销、经济风险 | `vgame-economy-source-map`、`senior-game-economy` |
| 成长到战斗转化 | `vgame-growth-combat-conversion-map` |
| 角色技能、配置链、强度验证 | `vgame-character-kit-design-map`、`vgame-hero-skill-config-map`、`vgame-battle-tuning-helper` |
| 外循环系统 | `vgame-outer-loop-system-map` |
| 配置质量审查 | `vgame-config-quality-audit` |
| 版本、教程、玩法内容 | `vgame-version-release-map`、`vgame-tutorial-onboarding-map`、`vgame-battle-content-map`、`vgame-level-design-map` |

策划案交付流程子 skill（由 `planning-feature-workflow` 按步骤调用）：

| 步骤 | skill |
|---|---|
| 需求逐条澄清 | `planning-requirement-clarification` |
| 验收与追踪矩阵 | `planning-acceptance-traceability` |
| 需求变更同步 | `planning-change-sync` |
| 数据与埋点 | `planning-analytics-instrumentation` |
| LiveOps 与上线准备 | `planning-liveops-readiness` |
| 商业化设计 | `game-monetization` |

## 黄金原则

1. 不在仓库里的决策，对智能体不存在。
2. 不直接修改真实配置，除非任务明确要求。
3. 所有关联判断必须能回到表、字段、skill 或设计文档。
4. 设计先闭环，再拆提案和任务。
5. 门禁脚本不是装饰，提交前必须跑。
