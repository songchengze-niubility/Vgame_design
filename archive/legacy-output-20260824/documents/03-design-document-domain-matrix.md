# Design 文档—项目领域映射矩阵

> 主领域表示文档的主要策划职责；次领域表示其实际跨域影响。文档声明状态来自原文，不再使用文件名启发式替代真实状态。规范化生命周期只是机器索引；运行与落地状态必须另查系统状态登记。

- 文档总数：52
- 当前仓库 Understand 图谱（`.understand-anything/knowledge-graph.json`）节点匹配：52/52
- 旧跨仓图谱 `knowledge-graph/.understand-anything/knowledge-graph.json` 仅作历史 client/config 快照，不参与本表 52/52 计算。

| 源文档 | 系统/主题 | 主领域 | 次领域 | 原文声明状态 | 规范化设计生命周期 | 当前仓库图谱匹配 | 证据角色 |
|---|---|---|---|---|---|---:|---|
| `design/抽卡系统Design Doc.md` | 抽卡系统 | `BO-03` 获取与阵容扩展 | `BO-06`、`BO-04`、`BO-05` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/大秘境Design Doc.md` | 大秘境 | `BO-01` 玩法与内容编排 | `BI-06`、`BI-07`、`BO-05`、`BO-04` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/房车设备数值设计-2026-07-21.md` | 房车设备数值 | `BO-02` 养成与战力构建 | `BO-04`、`BO-09`、`XS-01` | `Confirmed`（设备规则与数值已确认；舱室单材料升级方案已同步06评审镜像） | `APPROVED` | 是 | design-input-requires-source-validation |
| `design/房车养成系统当前版本设计-2026-07-09.md` | 房车养成当前版本 | `BO-02` 养成与战力构建 | `BO-04`、`BI-02`、`XS-01` | `Draft / CurrentDecision` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/房车养成系统数值设计文档-2026-07-03.md` | 房车养成数值 | `BO-02` 养成与战力构建 | `BO-04`、`XS-01` | `InReview` | `IN_REVIEW` | 是 | design-input-requires-source-validation |
| `design/房车养成系统小分叉重设计-2026-07-14.md` | 房车养成小分叉重设计 | `BO-02` 养成与战力构建 | `BO-04`、`XS-01`、`XS-02` | 数值与产出方案已确认，已合入框架V2的06最终配置镜像；SVN未修改 | `APPROVED` | 是 | design-input-requires-source-validation |
| `design/高难主线关卡奖励重设计-2026-07-30.md` | 高难主线奖励重设计 | `BO-04` 资源、经济与奖励 | `BO-01`、`BI-06`、`XS-01` | 关卡结构、首通奖励、常规掉落与星级奖励均已确认 | `APPROVED` | 是 | design-input-requires-source-validation |
| `design/公会系统Design Doc.md` | 公会系统 | `BO-07` 社交与组织 | `BO-05`、`BO-04`、`BI-06`、`BO-02` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/怪物与Boss系统Design Doc.md` | 怪物与 Boss | `BI-03` 敌人与 AI | `BI-04`、`BI-05`、`BI-07`、`XS-02` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/关卡编辑器Design Doc.md` | 关卡编辑器 | `XS-03` 内容生产工具 | `BI-05`、`XS-02`、`BI-08` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/技能系统Design Doc.md` | 技能系统 | `BI-04` 技能、Buff 与效果 | `BI-02`、`BI-03`、`XS-03`、`XS-02` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/角色经验副本Design Doc.md` | 角色经验副本 | `BO-01` 玩法与内容编排 | `BI-06`、`BO-04`、`BO-08` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/角色升级与突破Design Doc.md` | 角色升级与突破 | `BO-02` 养成与战力构建 | `BI-02`、`BO-04`、`BO-08` | `Draft`（反推草稿，待评审） | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/角色升星Design Doc.md` | 角色升星 | `BO-02` 养成与战力构建 | `BI-02`、`BO-03`、`BO-06` | `Draft`（反推草稿，待评审） | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/角色星盘与能效Design Doc.md` | 角色星盘与能效 | `BO-02` 养成与战力构建 | `BI-02`、`XS-01` | `Draft`（反推草稿，待评审） | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/金币副本Design Doc.md` | 金币副本 | `BO-01` 玩法与内容编排 | `BI-06`、`BO-04`、`BO-08` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/竞技场Design Doc.md` | 竞技场（PVPVE） | `BO-01` 玩法与内容编排 | `BI-06`、`BI-07`、`BO-05`、`BO-04`、`BO-07` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/局内金币带出Design Doc.md` | 局内金币带出 | `BI-09` 战斗结果与结算触发 | `BO-04`、`BI-06`、`XS-02` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/旅券副本Design Doc.md` | 旅券副本 | `BO-01` 玩法与内容编排 | `BI-06`、`BO-04`、`BO-08`、`BI-07` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/旅券系统Design Doc.md` | 旅券系统 | `BO-02` 养成与战力构建 | `BO-04`、`BI-02`、`BO-03` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/爬塔Design Doc.md` | 爬塔 | `BO-01` 玩法与内容编排 | `BI-06`、`BI-07`、`BO-05`、`BO-04` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/跑商玩法数值设计文档-2026-07-06.md` | 跑商玩法 | `BO-01` 玩法与内容编排 | `BO-04`、`BO-09`、`BO-02` | Unstated | `UNKNOWN` | 是 | design-input-requires-source-validation |
| `design/配置表管线Design Doc.md` | 配置表管线 | `XS-02` 配置与数据管线 | `XS-06`、`XS-07` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/签到系统Design Doc.md` | 签到系统 | `BO-05` 任务与留存 | `BO-04`、`BO-09` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/任务系统Design Doc.md` | 任务系统 | `BO-05` 任务与留存 | `BO-04`、`BO-08`、`BO-09` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/伤害计算公式Design Doc.md` | 伤害计算公式 | `BI-01` 战斗规则底座 | `BI-04`、`BI-07`、`XS-01` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/商店系统Design Doc.md` | 商店系统 | `BO-04` 资源、经济与奖励 | `BO-06`、`BO-05`、`BO-10` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/收容物养成数值Design Doc.md` | 收容物养成 | `BO-02` 养成与战力构建 | `BO-03`、`BI-02`、`XS-01`、`XS-02` | `ConfigReady`（属性与养成数值已生成 06 最终配置镜像；SVN Datas/程序接入待完成） | `APPROVED` | 是 | design-input-requires-source-validation |
| `design/碎片回收Design Doc.md` | 碎片回收 | `BO-03` 获取与阵容扩展 | `BO-04`、`BO-06`、`XS-02` | 规则评审就绪；角色“单次重复转化碎片量”尚待服务端回源，未达到配置实施门禁 | `IN_REVIEW` | 是 | design-input-requires-source-validation |
| `design/通行证系统Design Doc.md` | 通行证系统 | `BO-05` 任务与留存 | `BO-06`、`BO-04`、`BO-09` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/无限挑战Design Doc.md` | 无限挑战 | `BO-01` 玩法与内容编排 | `BI-06`、`BI-07`、`BO-05`、`BO-04` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/新手引导系统Design Doc.md` | 新手引导 | `BO-08` 引导、解锁与节奏 | `BI-08`、`BO-10`、`XS-03` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/映射装备数值超级爆改-2026-08-14.md` | 映射装备数值变更追溯 | `BO-02` 养成与战力构建 | `BO-04`、`XS-01`、`XS-07` | 已停止维护，非权威，仅保留为 2026-08-14 讨论与变更追溯记录。 | `DEPRECATED` | 是 | design-input-requires-source-validation |
| `design/映射装备系统数值调整草案-2026-07-02.md` | 映射装备数值调整草案 | `BO-02` 养成与战力构建 | `BO-04`、`XS-01`、`XS-07` | Draft | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/映射装备系统数值设计文档-2026-07-03.md` | 映射装备数值设计 | `BO-02` 养成与战力构建 | `BO-04`、`XS-01`、`XS-02` | Draft，已追加 2026-07-06 合成/制作 8 档变更、2026-07-09 红宝箱外显变更、2026-08-17 映射之匙任务投放调整、2026-08-20 CHG-014/CHG-015 首通展示职责拆分，待策划评审 | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/映射装备系统Design Doc.md` | 映射装备系统 | `BO-02` 养成与战力构建 | `BO-04`、`BO-01`、`BI-02` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/邮件系统Design Doc.md` | 邮件系统 | `BO-05` 任务与留存 | `BO-04`、`BO-09`、`BO-10` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/月卡系统Design Doc.md` | 月卡系统 | `BO-06` 商业化 | `BO-05`、`BO-04`、`BO-09` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/战斗掉落Icon表现Design Doc.md` | 战斗掉落 Icon 表现 | `BI-08` 战斗引导、UI 与反馈 | `BI-09`、`XS-04`、`XS-02` | InReview | `IN_REVIEW` | 是 | design-input-requires-source-validation |
| `design/战力系统Design Doc.md` | 战力系统 | `BI-07` 战斗数值与难度验证 | `BO-02`、`XS-01`、`BO-10` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/章节任务重设计讨论稿-2026-07-22.md` | 章节任务重设计 | `BO-05` 任务与留存 | `BO-01`、`BO-04`、`BO-08` | `Design Confirmed / Config Applied` | `APPROVED` | 是 | design-input-requires-source-validation |
| `design/主角等级Design Doc.md` | 主角等级 | `BO-08` 引导、解锁与节奏 | `BO-02`、`BO-01`、`XS-01` | `Draft`（反推草稿，待评审） | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/主线关卡奖励重设计-2026-07-30.md` | 主线关卡奖励重设计 | `BO-04` 资源、经济与奖励 | `BO-01`、`BO-08`、`XS-01` | `Draft / 已确认基础首通、角色材料、章底舱室建材与章节星级奖励口径` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/主线关卡系统Design Doc.md` | 主线关卡系统 | `BO-01` 玩法与内容编排 | `BI-06`、`BO-08`、`BO-04`、`BI-09` | `Draft`（反推草稿，待评审） | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/专武经验副本Design Doc.md` | 专武经验副本 | `BO-01` 玩法与内容编排 | `BI-06`、`BO-04`、`BO-08` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/专武系统Design Doc.md` | 专武系统 | `BO-02` 养成与战力构建 | `BO-03`、`BI-02`、`BO-04` | `Draft`（反推草稿，待评审） | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/archive/宝石与铭文Design Doc.md` | 宝石与铭文（归档） | `BO-02` 养成与战力构建 | `BI-02`、`BO-04`、`XS-07` | Archived | `ARCHIVED` | 是 | historical-only |
| `design/Buff系统Design Doc.md` | Buff 系统 | `BI-04` 技能、Buff 与效果 | `BI-02`、`BI-03`、`BI-01`、`XS-02` | `Draft` | `DRAFT` | 是 | design-input-requires-source-validation |
| `design/PVPVE怪物伤害数值设计-2026-07-27.md` | PVPVE 怪物伤害数值 | `BI-07` 战斗数值与难度验证 | `BI-06`、`BO-01`、`XS-01` | 数值目标已确认，部分工程配置仍待同步 | `APPROVED` | 是 | design-input-requires-source-validation |
| `design/README.md` | Design 目录入口 | `XS-07` 知识、证据与生命周期治理 | — | Reference | `REFERENCE` | 是 | governance-reference |
| `design/REVERSE-ENGINEERING-TEMPLATE.md` | 系统反推模板 | `XS-07` 知识、证据与生命周期治理 | `XS-02`、`XS-06` | Reference | `REFERENCE` | 是 | governance-reference |
| `design/TEMPLATE.md` | Design Doc 模板 | `XS-07` 知识、证据与生命周期治理 | `XS-06` | Reference | `REFERENCE` | 是 | governance-reference |
