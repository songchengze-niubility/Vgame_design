# 需求变更记录

## CHG-019 无用历史材料与可重建产物清理

- 状态：`implemented_pending_graph_rebuild`
- 日期：2026-08-24
- 原因：用户要求清理无用历史材料；仅处理无引用、空白、可重建或已明确被取代的产物，不删除 Design 源文档、research 回源正文、人工裁决原始证据或终验追踪链。
- 活动库清理：移出两套工作区的旧预览图、`tmpcheck.mjs`、旧 v0.1 评审页、QA 截图/依赖缓存、一次性修补脚本、Understand 旧 trash；另移出执行 worktree 的重复 `.codex-tmp` 与主工作区旧临时目录、冗余依赖、旧候选封装集和无说明章节解锁备份。
- 网页断链：新版知识库移除“旧版评审台”入口；QA 不再要求该历史按钮存在。当前决策卡评审台仍保留在 `knowledge-base/index.html#decisions`。
- 检索隔离：两套 `.understandignore` 新增临时目录、旧候选集、历史 review、QA 和 `design/archive` 排除规则；现有 Understand 图谱尚未重建，因此状态保持 `pending_graph_rebuild`。
- 恢复点：`D:\Vgame_cleanup_quarantine\20260824-knowledge-history-cleanup` 与 `C:\Users\songchengze\AppData\Local\Vgame\cleanup-quarantine\20260824-knowledge-history-cleanup`。
- 边界：保留 `02-project-planning-knowledge-framework.md` 与 `project-planning-framework.json`，因为仍是框架校验输入和历史裁决上下文；保留 `knowledge-base/preview.png`，因为工作流仍引用该证据。

## CHG-018 18 项正式人工裁决同步

- 状态：`verified_by_ai_gates`（等待独立复核；人工批准与交付验收仍为 false）
- 日期：2026-08-24
- 原因：用户正式确认“确认同步这18项裁决”，输入为 18/18 已选择的决策卡导出 JSON。
- 输入门禁：schema、18 张卡 ID、选项 ID、唯一 closeableQuestionIds、targetId/targetType 与 canonical 双向绑定全部精确匹配；原始 JSON 未改写归档，SHA-256 为 `8736877372517ec7a20f4d0996b9b9fb3599d828eb34d83d66d425a433f827f3`。
- 生命周期：只关闭 18 个明确绑定 QID；canonical 更新为 240 问（209 OPEN / 0 ANSWERED / 31 CLOSED），HUMAN_DECISION 为 18 CLOSED / 23 OPEN。
- 状态边界：18 项均为 `APPROVED_TARGET / HUMAN_DECISION_CONFIRMED / IMPLEMENTATION_PENDING`；不把目标确认写成 WORKING_COPY_OBSERVED、已实现、Production 或 LIVE。
- DC-E：原样保存“只有主线、高难需要三星”；其他玩法按已确认规则或 UNKNOWN，不补造。
- 同步范围：decision registry、19 个相关 canonical system details、M01/M02、shared contracts、Design/Skill 口径、待裁决清单、网页/搜索/路由/Markdown、validator/负例/浏览器 QA 与交接报告。
- 边界：未修改 `D:\Vgame`，未合并 `D:\Vgame_design`；`review_approved=false`、`delivery_accepted=false`。

| 影响对象 | 同步状态 |
|---|---|
| 原始证据 / audit metadata | synced，源与归档哈希相同 |
| registry / lifecycle / closure evidence | synced，18 卡只关闭 18 QID |
| canonical / M01 / M02 / contracts | synced，实施状态分离 |
| Design / Skills / simulator | synced，不宣称当前正式线或 LIVE |
| 网页 / Markdown / ARIA / QA | synced，已确认选项只读且键盘可访问 |
| framework / search / router / reports / workflow | synced，等待独立复核 |

## CHG-017 第二轮终验整改：问题生命周期、一卡一问与证据来源门禁

- 状态：`verified_by_ai_gates`（人工门禁仍为 false）
- 日期：2026-08-20
- 原因：独立终验确认哈希漂移、AI_EVIDENCE 未关闭、决策卡批量关闭、provenance 伪回填、Skill 旧事实、网页无障碍与 validator 盲区。
- 新规则：`openQuestions[]` 引入 OPEN/ANSWERED/CLOSED 生命周期与机器可读关闭证据；AI_EVIDENCE 必须 CLOSED；P0 禁止 DEFERRED_DETAIL；每张决策卡仅关闭 1 个真正独立问题；relation provenance 必须与 evidence kind 相容。
- 事实同步：映射装备最新设计源吸收 CHG-015；当前工作副本解锁链与 99 个主线节点同步到 core/progression/tutorial/release/outer-loop/simulator/economy Skill；C-001 保持冲突/未知。
- 网页与 QA：Markdown 粗体/行内代码/引用按语义渲染；390px 保留状态/证据等入口；抽屉补 dialog/aria-modal/焦点约束/Escape/焦点恢复；决策选项使用 radiogroup/radio 与方向键。
- canonical 统计：240 问（36 P0 / 127 P1 / 77 P2）；227 OPEN / 0 ANSWERED / 13 CLOSED；AI_EVIDENCE 13 / HUMAN_DECISION 41 / RUNTIME_OWNER 118 / DEFERRED_DETAIL 68；18 张一问单选卡。
- 边界：本轮未修改 `D:\Vgame` 真实 SVN 工程，不声称 Production/LIVE 或人工批准。

| 影响对象 | 同步状态 |
|---|---|
| canonical system details / decision registry | synced |
| SPEC / builder / validator / negative tests | synced |
| SYS-OUT-GR-07 / M02 / framework hash / search / router | synced |
| core/progression/tutorial/release/outer-loop/economy/simulator Skills | synced |
| 网页 / 390px / dialog focus / radio / Markdown QA | synced |
| HANDOFF / review / workflow | 全门禁后进入 waiting_human，human gates=false |

## CHG-001 将抽象表态卡改为可追溯评审单

- 状态：`verified`
- 日期：2026-08-17
- 提出人：项目负责人
- 目标版本：项目级策划知识框架评审批注台 2026-08-17
- 原因：原页面仅展示条目名称、简述和结论按钮，无法判断具体评审什么，也无法直接找到判断依据。
- 旧规则：对 160 个条目直接选择“认可 / 修改 / 删除 / 待确认”，评论未标注问题维度；页面不呈现证据路径、条目类型或多轴状态。
- 新规则：每个条目提供可展开的评审单，展示当前口径、四个具体评审问题、真实证据入口、条目类型、框架/设计/运行/落地/裁决状态轴和关联条目；评论增加维度，JSON/Markdown 一并保存。
- 明确不变项：战斗内、战斗外、支撑治理的候选分类内容不在本次变更中重写；160 个稳定条目 ID、已有评论结构和 `review-comments.json` 导入兼容性保持不变。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 评审 UI | `review/index.html` | Codex | synced | 评审单、证据入口、状态轴、评论维度已实现 |
| 使用说明 | `review/README.md` | Codex | synced | 已更新评审步骤与对象说明 |
| 评审数据 | `review-comments.json` | 项目负责人 | compatible | 新增 `dimension` 为可选字段，旧文件可继续导入 |
| 框架源文档 | `02-project-planning-knowledge-framework.md` | 主策/系统设计 | unchanged | 等待用户评论后再修订，不提前覆盖 |
| 验收 | 桌面/移动离线页面 | Codex | verified | Chrome 离线验证：28 领域 / 160 条目 / 6 裁决；476 个证据链接实例对应 58 个真实文件，缺失 0；桌面和 390px 移动端无脚本错误、无横向溢出；评论维度、JSON/Markdown 导出、重载恢复和关联跳转通过 |

## 复核结论

- 是否重走契约确认：否；本次仅修正评审媒介，不改变候选策划规则。
- 是否重走一致性评审：评论回收并修订框架时需要。
- 是否重新验收：是；评审页必须通过离线桌面/移动交互、链接及导入导出验证。

## CHG-002 将 160 项逐条审核改为分层审核

- 状态：`verified`
- 日期：2026-08-17
- 提出人：项目负责人
- 目标版本：项目级策划知识框架评审批注台 2026-08-17 分层版
- 原因：知识原子拆分粒度适合专家回源，不适合作为主策人工门禁；原页面使用户误以为必须逐条完成 160 项。
- 旧规则：顶部进度按 160 个条目计算；所有领域和条目构成默认主流程；6 个系统事实被标为本轮必须裁决。
- 新规则：主进度只计算 BI、BO、XS 三个一级结构判断；一级结构可批量认可其 9/10/9 个领域；领域地图按需展开；43 个异常优先进入专家明细，160 项均不计主进度；6 个系统事实移至后续专项问题。
- 明确不变项：候选框架内容、28 个领域、160 个稳定条目 ID、证据路径、已有 `itemReviews` 和 `decisionReviews` 均不删除；整层认可只写领域结构结论，不写原子条目事实结论。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 评审门禁 | `06-review.md` §5 | planning-reviewer | aligned | 页面重新对齐“本轮只裁决项目级分类” |
| 分层审核 UI | `review/index.html` | Codex | synced | 1 个总评、3 个一级结构、28 个按需领域、160 个可选专家明细 |
| 评审数据 | `review-comments.json` | 项目负责人 | compatible | 新增可选 `zoneReviews` 与领域 `decision/inheritedFrom`；原评论无损保留 |
| 使用说明 | `review/README.md` | Codex | synced | 已改为整层认可与按需下钻流程 |
| 验收用例 | `08-acceptance-cases.md` AC-13 | acceptance-designer | synced | 增加结构进度与专家明细解耦用例 |
| 框架源文档 | `02-project-planning-knowledge-framework.md` | 主策/系统设计 | unchanged | 本次只修正审核方法，不修改候选知识内容 |
| 验收 | 桌面/移动离线页面 | Codex | verified | Chrome 离线验证：默认 0/3；BI/BO/XS 批量写入 9/10/9 个领域且 itemReviews 保持 0；人工领域结论不会被批量覆盖；43 异常默认筛选；旧 JSON 无损恢复；桌面与 390px 无脚本错误和横向溢出；JSON/Markdown 分层导出通过 |

## CHG-002 复核结论

- 是否重走契约确认：否；KF-R001～KF-R003 未改变。
- 是否重走一致性评审：否；新页面反而恢复 `06-review.md` 已定义的审核边界。
- 是否重新验收：是；需验证结构进度与专家明细进度完全解耦。

## CHG-003 从领域审计包重构为项目—系统—战斗—数值知识库

- 状态：`verified`
- 日期：2026-08-17
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.2
- 原因：v0.1 虽覆盖 28 个领域、160 个知识原子、状态和证据，但主阅读结构仍以 BI/BO/XS 和审计材料为中心，难以轻松调用或修改；用户明确要求先有项目整体介绍，再按系统、战斗、数值分模块，最后下钻具体内容与关系。
- 旧规则：项目入口是一篇同时承载项目定位、BI/BO 分类、战斗事实、战斗外系统、支撑治理、状态冲突和目录方案的巨型文档；评审台承担主要交互入口。
- 新规则：日常入口改为“项目总览 → 系统 / 战斗 / 数值 → 具体系统和关系”；系统内分战斗内/外，战斗外分玩法/养成/周边；战斗聚焦规则和角色设计；数值对齐框架 v2；治理与旧评审材料降为附录。
- 明确不变项：原 Design 文档、原 v0.1 框架、52 文档矩阵、160 专家原子、状态冲突、回源审查和已有评论均不删除；Vgame SVN 配置与代码保持只读。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 需求契约 | `00-design-contract.md` KF-R001～KF-R006 | feature-scoper | synced | 已同步用户 2026-08-17 的模块结构裁决 |
| 澄清记录 | `00-clarification-log.md` | requirement-clarifier | synced | 已记录“大杂烩”纠偏与三模块要求 |
| 日常知识入口 | `knowledge-base/README.md` | system/combat/numeric designer | synced | 项目总览、系统、战斗、数值、关系、治理附录已建立 |
| 系统分类 | `knowledge-base/10-系统框架.md`、`11-战斗内系统.md`、`12-战斗外系统.md` | system-designer | synced | 已输出具体系统初步分类、摘要与关系 |
| 战斗框架 | `knowledge-base/20-战斗框架.md` | combat-designer | synced | 战斗规则与角色设计双入口已建立 |
| 数值框架 | `knowledge-base/30-数值框架.md` | num-balance | synced | 已回源框架 v2 的 README、沉淀 MD、参数基线及四域收口文档 |
| 关系模型 | `knowledge-base/40-系统关系.md`、`knowledge-model.json` | design-lead | synced | 已定义 11 类关系与稳定系统 ID；JS 为离线生成物 |
| 浏览/评论 UI | `knowledge-base/index.html` | Codex | verified | Chrome 离线 QA：桌面 1440 与移动 390 的五路由均无脚本错误和横向溢出；17 个子导航、45 个系统、搜索、深链、评论恢复与 JSON 导出全部通过 |
| 旧评审台 | `review/index.html` | Codex | synced | 已标为 v0.1 历史评审台并链接新版入口 |
| 验收 | `08-acceptance-cases.md` AC-14～AC-17 | acceptance-designer | synced | 新增专业模块、系统分层、数值 v2 与治理降级用例 |

## CHG-003 复核结论

- 是否重走契约确认：已依据用户当前明确裁决同步新契约；v0.2 阅读结构仍等待用户人工确认。
- 是否重走一致性评审：是；需要核对系统—战斗—数值职责没有重复或断链。
- 是否重新验收：是；已完成桌面/移动、搜索、深链、评论和导出验证，未发现阻断或功能缺陷。

## CHG-004 修复具体系统详情与分类页签不同步

- 状态：`verified`
- 日期：2026-08-17
- 提出人：项目负责人
- 影响范围：`knowledge-base/index.html`
- 原问题：从“战斗外 · 玩法”点击“主线”等具体系统时，详情正确打开，但分类页签错误回落到第一项“战斗内系统”。
- 修复规则：具体系统深链根据稳定系统 ID 自动恢复所属分类；关闭详情后保留当前系统分类，不再回落到第一项。
- 验证：已覆盖战斗内、战斗外玩法、战斗外养成、战斗外周边四类直接深链，以及“玩法 → 主线 → 关闭详情”完整操作；选中态与渲染分组一致，浏览器脚本错误为 0。
- 契约影响：无；仅修复浏览状态同步，不改变知识分类或系统内容。

## CHG-005 从系统摘要升级为可维护的完整系统正文

- 状态：`verified`
- 日期：2026-08-17
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.3
- 原因：v0.2 的“主线”只有章节、节点、评价、首通、扫荡等一段目录摘要，没有具体策划规则、条件、流程、异常和配置权威链，不能作为可直接调用或修改的知识正文。
- 旧规则：45 个系统都只有 `id/group/name/summary/status/relations` 六类摘要字段；点击系统只打开摘要抽屉；自动校验只能证明摘要齐全。
- 新规则：保留系统目录，同时新增 `vgame-system-detail/v1` 结构化正文层。首个样板 `SYS-OUT-GP-01` 包含 4 个状态轴、8 步流程、12 条规则，以及条件、奖励、异常、UI、配置、类型化关系、证据和 8 个待裁决问题；每个知识原子拥有稳定 ID，可独立评论。
- 事实修正：有效普通主线按 99 个节点统计；物理存在的 0-5、1-9、1-10、2-13、2-14、2-15 六行首列均为 `##`，不纳入当前有效配置。目标设计、当前源表、交付镜像和 LIVE 状态分开呈现。
- 明确不变项：真实 SVN 配置和代码保持只读；未裁决冲突不代替主策作结论；其余 44 个系统仍为摘要索引，不虚报完整覆盖。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 需求契约 | `00-design-contract.md` KF-R005/KF-R007 | feature-scoper | synced | 已明确“首页不复制正文”不等于“系统没有正文” |
| 结构化正文 | `knowledge-base/system-details/SYS-OUT-GP-01.json` | system-designer | synced | schema v1；87 个唯一详情原子，证据和关系引用可解析 |
| 人类可读正文 | `knowledge-base/systems/SYS-OUT-GP-01-主线.md` | build pipeline | generated | 由结构化正文生成，不建立第二手工权威源 |
| 浏览与评论 | `knowledge-base/index.html#system/SYS-OUT-GP-01` | Codex | verified | 独立详情页、11 个章节导航、规则级评论、旧评论兼容 |
| 构建链 | `knowledge-base/build-web-model.mjs` | Codex | verified | 自动合并详情并生成离线 JS 与 Markdown |
| 完整度门禁 | `knowledge-base/validate-knowledge-base.mjs` | acceptance-designer | verified | 30/30；45 系统、1 个完整正文、87 个详情原子、证据路径、状态语义与项目入口开放点同步通过 |
| 桌面/移动 QA | Chrome 离线页面 | Codex | verified | 1440px 与 390px 直接深链均显示 12 条规则、4 状态轴、11 个子导航；无 console/pageerror 和根横向溢出；规则评论可保存恢复 |
| 项目入口事实 | `skills/vgame-core-understanding/references/current-gameplay.md` | project-maintainer | synced | 资源本2-4、竞技场2-7、映射装备2-10、无限挑战3-15已按2026-08-17工作副本刷新；旧值不再冒充当前 |
| 状态语义 | `SYS-OUT-GP-01` revision `2026-08-17.2` | planning-reviewer | verified | `TARGET / WORKING_COPY / KNOWLEDGE_CURRENT / CONFLICT / LIVE` 图例已加入；UI需求改为 `TARGET_REQUIRED`，工作副本证据不再使用 `CURRENT_SOURCE` |

## CHG-005 复核结论

- 是否重走契约确认：是；新增 KF-R007，源于用户对具体系统正文深度的明确纠偏。
- 是否重走一致性评审：是；已核对目标设计、当前源表和运行状态未合并成单一“现行”结论。
- 是否重新验收：是；主线样板已通过结构、引用、离线桌面/移动和评论恢复验证。
- 当前门禁：`WaitingHumanReview`。用户确认主线样板的正文深度和组织方式后，按同一 schema 扩展其余 44 个系统。

## CHG-006 建立分层结构化 RAG 与按系统懒加载

- 状态：`verified`
- 日期：2026-08-17
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.4
- 原因：用户希望知识库可以非常大且细致，但每次调用只取当前问题真正需要的内容；现阶段先采用结构化检索，向量检索在正文覆盖充分后再启用。
- 旧规则：网页和 Agent 主要依赖系统目录、页面搜索与人工选择；完整正文若继续增加，会逐步放大首屏数据与单次上下文。
- 新规则：建立 `quick / design / audit` 三档读取深度、共享契约注册表和路由清单；网页目录、搜索原子与系统正文拆开，系统正文仅在进入对应稳定 ID 时加载；项目 Skill 根据问题先生成最小 `readPlan`，不得枚举全部正文。
- 术语策略：canonical 名称、别名、边界词、排除词和来源优先级随正文增量积累；不先造巨型词典。向量检索以后只承担语义候选召回，仍受系统、状态、来源和深度过滤约束。
- 明确不变项：结构化正文仍是权威源；工作副本不等于 LIVE；向量召回不能覆盖稳定 ID、关系与证据边界。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 检索策略 | `knowledge-base/retrieval-policy.json` | knowledge-architect | synced | 三档深度、来源层与最小读取规则已登记 |
| 共享契约 | `knowledge-base/shared-contracts/contract-registry.json` | integrator | synced | 7 个框架契约进入统一注册表 |
| 自动路由 | `skills/vgame-knowledge-router/` | router-maintainer | verified | quick/design/audit 样例均只打开计划内文件；未遍历详情目录 |
| 路由清单 | `knowledge-base/router-manifest.json` | build pipeline | generated | 45 系统目录与详情引用一致 |
| 网页懒加载 | `knowledge-base/system-chunks/` | build pipeline | verified | 首页详情 0，进入主线后仅加载 1 个 chunk |
| 搜索索引 | `knowledge-base/knowledge-search-index.js` | build pipeline | generated | 87 个主线原子可在不加载正文时被发现 |
| 验收 | `knowledge-base/validation-report.json`、离线 Chrome QA | acceptance-designer | verified | v0.4 初始结构验证 40/40；桌面与移动深链、搜索、评论、导出无阻断 |

## CHG-006 复核结论

- 是否重走契约确认：否；这是已确认“大库、小调用”的实现方式，不改变具体系统规则。
- 是否重走一致性评审：是；每个读取计划必须保留状态、来源与未知项，不能只返回最像的文本。
- 是否重新验收：是；已验证首屏轻量、按 ID 懒加载、搜索不触发正文加载及三档路由边界。
- 向量门禁：`deferred`。正文、别名和负向边界覆盖不足前不启用。

## CHG-007 建立跨对话接力与并行正文生产协议

- 状态：`verified`
- 日期：2026-08-17
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.4 authoring handoff
- 原因：剩余 44 个系统若由一个长对话串行回源、编写和集成，会重复加载项目上下文，速度慢且容易让多个作者修改同一共享文件。
- 旧规则：已有 README 说明浏览与维护，但没有新对话唯一入口、批次领取、生产型回源路由、通用正文规范或并行写入所有权。
- 新规则：以 `HANDOFF.md` 作为唯一接力入口；44 个摘要系统拆为 9 个唯一工作包和 3 个生产 Wave，每 Wave 最多 3 个作者并行，保留 1 个集成者；作者只能写本人系统正文，集成者独占共享模型、契约、构建脚本与生成物。
- 质量规则：主线只作为关卡/奖励型实例，通用规范允许合法 `N/A/GAP/UNKNOWN`；不得为了数组非空伪造奖励、配置、UI、流程或异常；系统事实仍需逐项评审，工作包完成不等于用户批准或 LIVE。
- 状态口径：历史 `00-workflow-state.json` 记录早期评审循环；后续批次领取和生产进度以 `knowledge-base/work-packages.json` 为准，阶段变更继续通过官方状态脚本留痕。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 接力入口 | `HANDOFF.md` | integrator | synced | 新对话读取顺序、可复制提示词、边界、命令与完成定义齐全 |
| 并行队列 | `knowledge-base/work-packages.json` | integrator | verified | 44/44 待扩展系统唯一覆盖，无重复或遗漏 |
| 生产回源路由 | `knowledge-base/authoring-source-map.json` | knowledge-researcher | synced | 按系统登记 Skill、文档、知识入口、配置/代码区域与风险 |
| 通用正文规范 | `knowledge-base/SYSTEM-DETAIL-SPEC.md` | knowledge-architect | synced | 定义跨类型字段、稳定 ID、来源/状态、适用性与 G0–G6 门禁 |
| 机械门禁 | `knowledge-base/validate-knowledge-base.mjs` | integrator | verified | 51/51；检查工作包唯一覆盖、生产回源路径与Skill，并允许受适用性约束的合法空章节 |
| 阅读入口 | `README.md`、`knowledge-base/README.md` | integrator | synced | 接力入口与生产资料置于维护说明首部 |

## CHG-007 复核结论

- 是否重走契约确认：否；并行协议不改变知识框架和系统事实。
- 是否重走一致性评审：每个工作包完成后由唯一集成者执行，作者不得自行修改共享契约或关系类型。
- 是否重新验收：是；需持续验证 44 个系统唯一领取、来源路径、引用完整性、构建结果与桌面/移动按需加载。
- 当前进度：1/45 完整正文，44/45 已进入可领取队列；未把摘要系统虚报为完成。

## CHG-008 知识库返工与复审（HIGH 风险，needs_revision）

- 状态：`verified`
- 日期：2026-08-18
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.4 rework
- 原因：Wave1/2/3 全部交付后 45/45 系统拥有完整正文，但机械校验暴露 6 项失败：276 条关系缺少 evidenceRefs 或 provenance、生成物（chunks/markdown/search-index/router-manifest）与 canonical 数据不一致、搜索索引计数漂移。语义层面存在 IN-03/06/08 规则将代码观察写成正式 targetRule、GR-10 专武正文自相矛盾等问题。
- 旧规则：部分规则只有代码/配置观察却被写成正式 targetRule；关系数组无逐条证据绑定；生成物未在每次 canonical 变更后重建；校验器缺少日期、关系证据、targetRule、生成物一致性等检查。
- 新规则：
  1. 日期不得晚于当前环境日期；批量报告中的未来日期已修正。
  2. HANDOFF/workflow-state/change-log/work-packages 对齐实际完成情况，review=needs_revision，review_approved=false，delivery_accepted=false。
  3. IN-03/IN-06/IN-08 观察型规则的 targetRule 改为 GAP/UNKNOWN，观察保留在 sourceFact。
  4. GR-10 专武正文保持 CONFLICT/UNKNOWN，不擅自写成"已承接/替代"；生成用户裁决问题。
  5. 276 条关系逐条绑定 evidenceRefs 或标 CROSS_SOURCE_SYNTHESIS/UNKNOWN，禁止机械填同一伪证据。
  6. validate-knowledge-base.mjs 强化：系统目录与详情集合一致、detailLevel=full、targetRule 必填、日期不晚于今天、关系证据校验、生成物一致性。
  7. SYSTEM-DETAIL-SPEC.md 与校验器对齐。
  8. 45 系统分批（每批≤3）语义复审，区分结构完成/语义复审完成/用户正式批准。
- 明确不变项：Vgame SVN 工程只读；不代用户裁决；review_approved 和 delivery_accepted 保持 false。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 工作流状态 | `00-workflow-state.json` | integrator | synced | current_phase=review, last_outcome=needs_revision |
| 变更记录 | `07-change-log.md` CHG-008 | change-sync-reviewer | synced | 本条 |
| 日期修正 | `research/batches/W2-A.md` ~ `W3-C.md` | integrator | synced | 2026-08-19 → 2026-08-18 |
| 校验器强化 | `knowledge-base/validate-knowledge-base.mjs` | integrator | synced | 67/67 校验通过 |
| 规范对齐 | `knowledge-base/SYSTEM-DETAIL-SPEC.md` | knowledge-architect | synced | 日期门禁、targetRule、关系证据 |
| 规则来源修复 | `system-details/SYS-IN-03.json`、`SYS-IN-06.json`、`SYS-IN-08.json` | integrator | synced | 观察型规则回 sourceFact，targetRule → GAP/UNKNOWN |
| GR-10 矛盾修复 | `system-details/SYS-OUT-GR-10.json` | integrator | synced | CONFLICT/UNKNOWN 保留 + 裁决问题（C-001） |
| 关系证据 | 45 个 system-details relationships | integrator | synced | 逐条绑定 evidenceRefs/provenance；GR-05↔GR-10 双向 supersedes+conflicts-with |
| 证据路径修复 | 20 条 evidence `path`（含 7 条 `href`）| integrator | synced | `Systems\<Folder>\<Name>System.lua` 子目录层级 → `Systems\<Name>System.lua` 扁平路径（SVN Lua 实为扁平），仅当扁平文件存在时替换；复检 0 缺路径 |
| contractRefs 补齐 | 19 个 system-details（15 缺字段 + 4 空数组：IN-02/03/04/05） | integrator | synced | 统一插入顶层 contractRefs（contract-registry 8 个合法 ID，无悬挂 ruleRefs），45 系统 contractRefs 校验 ALL_OK |
| 生成物重建 | `build-web-model.mjs` | integrator | synced | 重建后校验器 67/67 通过 |

## CHG-008 复核结论

- 是否重走契约确认：否；知识框架和系统事实不变。
- 是否重走一致性评审：是；已按 45 系统分批完成语义复审。
- 是否重新验收：是；已通过强化校验器（67/67）、Playwright 桌面/移动验证。
- 当前进度：返工完成（内容修复、数量对齐、生成物重建、校验 67/67、桌面/移动回归通过）；P0/P1 留给用户裁决，未取得用户正式批准前不宣布整体验收完成。

## CHG-009 主线章节补充主角等级双门槛

- 状态：`verified`
- 日期：2026-08-18
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.4 / 主线正文 revision 2026-08-18.2
- 原因：用户明确补充“主线每个章节还有与等级相关的开启条件，具体等级按源表节奏口径”；原主线正文只记录前章末关与 `ChapterLevel.Unlock`，遗漏等级门槛。
- 旧规则：章节内由节点前置串联，跨章只描述为 `ChapterLevel.Unlock` 接续；当前工作副本中的章节 Unlock 也确实只解析到前章末关。
- 新规则：跨章开启采用“前一章末关通关 AND 主角等级（玩家账号等级）达标”。当前数值节奏唯一权威单源门槛为：序章 Lv1、第一章 Lv6、第二章 Lv14、第三章 Lv20、第四章 Lv25、第五章 Lv30、第六章 Lv34、第七章 Lv37。
- 明确不变项：章节内节点仍按前一关推进；高难章节另归 `SYS-OUT-GP-02`；本次不修改 Vgame SVN 配置或代码，不把目标门槛误写为已实装/LIVE。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 项目证据 | `01-project-evidence.md` EV-025 | project-researcher | synced | 用户裁决、节奏单源、ChapterLevel/Unlock 工作副本三层证据已区分 |
| 主线 Design | `design/主线关卡系统Design Doc.md` R-01 | system-designer | synced | 双门槛、8 个等级门槛、锁定提示与配置缺口已写入 |
| 等级 Design | `design/主角等级Design Doc.md` R-04 | num-balance | synced | 章节起始等级与当前唯一权威节奏单源已写入 |
| 结构化正文 | `knowledge-base/system-details/SYS-OUT-GP-01.json` R03/C03/UI01/EV18/Q09 | system-designer | synced | revision 2026-08-18.2；目标规则与工作副本缺口分层 |
| 人类可读正文/检索 | `knowledge-base/systems/SYS-OUT-GP-01-主线.md`、`knowledge-search-index.js`、`router-manifest.json` | build pipeline | generated | `build-web-model.mjs` 已重建，45 个 full 正文、2582 个原子（返工后校验复核值） |
| 验收 | `08-acceptance-cases.md` AC-22 | acceptance-designer | synced | 覆盖两种单条件不足与双条件同时满足场景 |
| 待裁决 | `待裁决清单.md` GP-01-Q09、`HANDOFF.md` | change-sync-reviewer | synced | 明确 `ChapterLevel.Unlock` 为单值且当前只配置关卡条件，需裁决复合条件实现方式 |
| 自动校验 | `knowledge-base/validation-report.json` | integrator | verified | `validate-knowledge-base.mjs` 67/67，通过；45 systems / 2582 detail atoms |

## CHG-009 复核结论

- 是否重走契约确认：否；知识框架范围不变，用户已直接确认主线新增规则。
- 是否重走一致性评审：是；已核对用户口径、数值节奏单源与 SVN 工作副本，确认“目标规则已冻结、配置实现有缺口”，未混写为 LIVE。
- 是否重新验收：是；新增 AC-22，并通过知识库 67/67 自动校验。实际配置/代码落地后仍需执行双门槛运行验收。
- 当前门禁：变更同步已闭环；`review_approved=false` 与 `delivery_accepted=false` 保持不变，复合门槛实现方式列为 P1 待裁决。

## CHG-010 用户截图修正第3～7章开启等级

- 状态：`verified`
- 日期：2026-08-18
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.4 / 主线正文 revision 2026-08-18.3
- 原因：用户提供《章节等级表》截图，明确第3～7章开启等级为24、28、31、33、35，与 CHG-009 引用的生成节奏单源20、25、30、34、37不一致。
- 旧规则：完整门槛为 Lv1/6/14/20/25/30/34/37。
- 新规则：完整门槛为 Lv1/6/14/24/28/31/33/35；第0～2章未出现在截图中，继续沿用既有1/6/14，第3～7章以用户截图为最新权威。
- 明确不变项：章节开启仍为“前章末关通关 AND 主角等级达标”；当前 SVN 只配置前章末关的实现缺口不变；本次不修改 SVN 配置、代码或数值源 Excel。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 用户原始证据 | `evidence/chapter-level-table-user-20260818.png` | project-researcher | synced | SHA256 `9473C7BF92D5DFA71A6CBE9917724B060DFF4620219AF8F73BEDEA8A964493E6` |
| 澄清记录 | `00-clarification-log.md` | requirement-clarifier | synced | 记录第3～7章新旧值与第0～2章沿用边界 |
| 项目证据 | `01-project-evidence.md` EV-026 | project-researcher | synced | EV-025 保留历史结论并标明被部分覆盖 |
| 主线/等级 Design | `design/主线关卡系统Design Doc.md`、`design/主角等级Design Doc.md` | system-designer / num-balance | synced | 目标门槛、证据优先级和旧数值单源待同步已写入 |
| 结构化正文 | `knowledge-base/system-details/SYS-OUT-GP-01.json` R03/C03/EV18/EV19 | system-designer | synced | revision 2026-08-18.3；EV18降为部分过期，EV19为用户最新证据 |
| 验收 | `08-acceptance-cases.md` AC-22 | acceptance-designer | synced | 第3～7章期望值改为24/28/31/33/35 |
| 生成与自动校验 | `build-web-model.mjs`、`validate-knowledge-base.mjs`、`scripts/check.ps1` | integrator | verified | 已重建为 45 个 full 正文、2582 个原子；知识库校验 67/67；仓库门禁 0 FAIL（760 条既有 WARN） |

## CHG-010 复核结论

- 是否重走契约确认：否；只修正已确认双门槛中的数值参数，不改变知识框架范围。
- 是否重走一致性评审：是；已确认 Design、结构化正文、生成物、证据和验收统一使用 Lv1/6/14/24/28/31/33/35；旧值仅保留在明确标注为历史或待同步的上下文中。
- 是否重新验收：是；AC-22 已改按 Lv1/6/14/24/28/31/33/35 检查，知识库自动校验 67/67 通过；实际配置/代码落地后仍需执行运行验收。
- SVN 写入核对：`ChapterLevel.xlsx`、`Unlock.xlsx`、`level.xlsx`、`UIlevel.xlsx`、`MainLevel.xlsx` 目标文件状态均 clean，本次未修改真实配置。
- 当前门禁：变更同步已闭环；`review_approved=false` 与 `delivery_accepted=false` 保持不变，数值单源同步与双门槛实现方式仍待裁决。

## CHG-011 章节0～2取消硬卡并落地第3～7章等级条件

- 状态：`verified`
- 日期：2026-08-18
- 提出人：项目负责人
- 目标版本：Vgame 本机 SVN 工作副本 / 项目级策划知识库 v0.4 主线正文 revision 2026-08-18.4
- 原因：用户进一步明确“0～2章不需要开启条件，不会硬卡”，并授权配置剩余章节；该口径覆盖 CHG-009/CHG-010 的双门槛推断。
- 旧规则（已被覆盖）：0～2章沿用Lv1/6/14；3～7章采用“前章末关通关 AND 等级24/28/31/33/35”。
- 新规则：0～2章不设 `ChapterLevel.Unlock`；3～7章仅按主角/玩家等级24/28/31/33/35开启，不叠加前章末关条件。章节内具体关卡顺序链保持不变。
- 状态边界：工作副本源表已配置、客户端已导出并验证；尚未完成实机冒烟和发布台账核验，不称 Production/LIVE。

| 影响对象 | ID/路径 | 变更 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 章节源表 | `Datas/level/ChapterLevel.xlsx` | 10000～10002 Unlock置空；10003～10007改为201～205 | configured | 与备份逐格比较，仅7个目标单元格变化 |
| 解锁源表 | `Datas/unlock/Unlock.xlsx` | 201～205保持 `UnLock_UUT_player_Grade`，参数改为24/28/31/33/35 | configured | 仅5个目标单元格变化；55个公式及缓存完整 |
| 客户端 Lua | `LuaConfig/chapterlevel.lua`、`LuaConfig/unlock.lua` | 导出章节0～2为0、章节3～7为201～205及等级参数 | generated | `export_client.bat` 退出码0，精确值与SHA256复核通过 |
| 客户端 bytes | `ExcelData/chapterlevel.bytes`、`ExcelData/unlock.bytes` | 与源表同步生成 | generated | SHA256复核通过 |
| 运行语义 | `LevelSystem.lua`、`ConditionSystem.lua` | 未改代码；空/0条件为开放，player_Grade按等级判定 | verified | 源码回源确认 |
| 设计与验收 | 主线/主角等级 Design、AC-22、评审与证据 | 双门槛改为0～2无条件、3～7单等级条件 | synced | 文档交叉核对 |
| 结构化知识 | `SYS-OUT-GP-01`、`SYS-OUT-GR-01`、`SYS-OUT-SU-13` | 规则、条件、配置和证据同步 | synced | 构建与知识校验 |
| 审计报告 | `09-config-quality-audit-chapter-unlock.md` | 记录来源链、差异、公式、引用、导出、哈希与工具限制 | verified | `verify_main_chapter_unlocks.py` PASS |
| 回滚备份 | `backups/chapter-unlock-20260818-171110/` | 保存修改前两张源表 | available | 两文件SHA256已登记 |

## CHG-011 复核结论

- 是否重走契约确认：否；用户已直接给出明确规则并授权配置。
- 是否重走一致性评审：是；用户口径、ChapterLevel、Unlock、运行代码、客户端生成物、Design、验收和结构化知识已同步。
- 是否重新验收：是；目标源表差异、公式缓存、引用完整性、Lua/bytes内容和哈希均通过针对性校验。
- 工具限制：通用配置审计脚本因范围外短行工作簿的 `IndexError` 未完成全库扫描；本次目标审计通过，未把全库扫描误报为成功。
- 当前门禁：配置落地闭环；仍需客户端实机验证锁定、升级刷新与进入行为。整体 `review_approved=false`、`delivery_accepted=false` 保持不变。

## CHG-012 知识库收尾修复：M01/M02 接入、证据/契约修正、validator 加固与统计同步

- 状态：`verified`
- 日期：2026-08-19
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.4 closeout / 正文 revision 2026-08-19.1（涉及 GR-05/GR-10/SU-12/GP-09/GP-03/SU-01/SU-02/IN-06/IN-08/GP-01）
- 原因：45 系统正文虽完成，但项目级知识库未闭环：M01/M02 为孤立文档（work-packages 仍 planned）、L1 目录状态与正文状态轴漂移（GP-09「未开放」vs UNKNOWN_LIVE、GR-05「落地待核」vs 候选方案冲突）、GR-05 REL01 跨正文证据引用可被 provenance 绕过、契约错绑（GR05 UNLOCK→升星规则、GR10 UNLOCK→本体规则、GP09 BATTLE-RESULT 只覆盖重复层）、SU12 EV07 混合两份源码证据、发言 CD/禁言把不可见的服务端执行写成事实、交接统计停留在旧口径（224/2582）、workflow 时间线乱序、QA waitForSystem 忽略系统 ID。
- 新规则：
  1. M01/M02 建立 canonical（`module-details/M01.json`、`M02.json`，schema `vgame-module-detail/v1`），接入构建（module-chunks/搜索索引 18 条/router specialistModules）；M01 修正 CoinMode 胜利 UNKNOWN（GameOverData 仅候选）、通用 CNotifyFightOver 不覆盖 PVPVE、竞技场三层口径（§3.2.1）；M02 新增 §0.5 映射边界（行级/域级深度区分，收窄「视图非完整映射」声明）。work-packages M01/M02 → complete。
  2. GR05 REL01 移除跨正文 evidenceRef（SYS-OUT-GR-10-EV07）；GR05 删除 UNLOCK/REWARD 契约误绑；GR10 UNLOCK 改绑 C02（专武系统开放）；GP09 BATTLE-RESULT 补 R06；SU12 EV07 拆分为 EV07（pb_types_new.lua）+ EV08（ExcelDataDefine.lua 真实路径）；11 条 CROSS_SOURCE_SYNTHESIS 关系补「推导边界」四要素。
  3. SU12 发言 CD/频道解锁/禁言：源码回源确认 `SendChannelMessage`(L308-327) 不调用 `CheckSendCD`（仅 SendGIF L368 调用），普通文本 CD 拦截、频道级解锁拦截、禁言拦截的服务端执行一律改 UNKNOWN，不再写「服务端已执行限制」。
  4. GP09 解锁枚举区分 Excel 原始字段值（数值 1）与代码枚举语义（玩家等级）；GR10 R01 补 RelatedHero 39 行全空事实（schema 存在≠现行绑定，本机只读核对）。
  5. IN-06-Q07（与 IN-08-Q05 近重复）从 canonical 删除并入 SYS-IN-08-Q05，ID 不复用，引用同步清理。
  6. knowledge-model.json：GP-09 状态改「工作副本关闭·运行UNKNOWN（UNKNOWN_LIVE）」、GR-05 改「候选目标方案·P0冲突待裁决（C-001）」、SU-10 改「设计封存候选·运行UNKNOWN（C-006）」；current-gameplay.md/SKILL.md 专武条目加 C-001 中央冲突注记。
  7. validator 51→80 检查：contractRefs 必填+命名空间、evidenceRefs 不因 provenance 绕过、CSS 推导边界、wave gate 覆盖 M01/M02、Markdown 全文深度一致（共享渲染器 render-markdown.mjs）、模块 canonical/router/chunk 一致、workflow 时间线（乱序/未来/updated_at）、交接统计一致性（旧口径 token 禁入）、L1↔详情状态轴一致；13 个负例测试（tests/validate-negative.test.mjs）全部证明坏数据会被拦截。
  8. 路由器：目录型查询强制 quick、具体分组词优先于「战斗外」宽组扩展、技术符号 token 入 keywords（ResultHash/CoinMode 等可检索）、M01/M02 直达路由、quick/design 档输出 L1 状态边界提示；test_route.py 扩至 12 样例全 PASS。
  9. 决策卡 14→16 张（新增 DC-O 社交激励经济与治理、DC-P 竞技场段位与奖励口径），13 个新增问题全部映射（见 决策卡/README.md 映射表）。
- 明确不变项：Vgame SVN 工程只读（本轮仅只读核对 ExclWeapon.xlsx/ChatSystem.lua）；review_approved=false、delivery_accepted=false 保持；不代主策裁决专武迁移、奖励权威源、Production/LIVE 等人工事项。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 正文数据 | GR-05/GR-10/SU-12/GP-09/GP-03/SU-01/SU-02/IN-06/IN-08 | integrator | synced | 17+11 处修正（scripts/fix_evidence_contracts_20260819.py 等）；revision 2026-08-19.1 |
| 模块 canonical | `module-details/M01.json`、`M02.json` | integrator | synced | anchor 全部命中；validator module 检查 5 项 |
| 构建器 | `build-web-model.mjs` + `render-markdown.mjs` | integrator | synced | 45 系统 + 2 模块；2619 原子 + 18 模块条目 |
| 校验器 | `validate-knowledge-base.mjs` | integrator | synced | 80 检查；负例 13/13 拦截 |
| 路由 | `skills/vgame-knowledge-router/scripts/route_query.py` + `test_route.py` | router-maintainer | synced | 12/12 样例 PASS；quick_validate 通过 |
| 决策卡 | `决策卡/DC-O-*.md`、`DC-P-*.md`、README | integrator | synced | 16 张卡；13 问映射表 |
| 交接统计 | HANDOFF/06-review/待裁决清单/最终返工完成报告/00-workflow-state | change-sync-reviewer | synced | 236 问（33 P0 / 126 P1 / 77 P2）、2619 原子、16 卡 |
| workflow | `00-workflow-state.json` | integrator | synced | history 时间序修复；追加 CHG-012 事件 |

## CHG-012 复核结论

- 是否重走契约确认：否；知识框架范围不变。
- 是否重走一致性评审：是；validator 新增 L1↔详情一致性、统计一致性、workflow 时间线检查防止再次漂移。
- 是否重新验收：是；build/validator 80 检查/route 12 样例/负例 13 项/QA（桌面+移动）全部执行。
- GP-01 revision 补记：主线正文 revision `2026-08-18.5` 为 2026-08-18 收尾轮语义修订（战斗语义/ResultHash 条件赋值等，当时未单独立 CHG 条目），本次补记归档；当前无更高 revision。
- 当前门禁：`review_approved=false`、`delivery_accepted=false` 保持；等待主策按 16 张决策卡集中评审。

## CHG-013 最后一轮 AI 返工：M01/M02 网页接入、决策卡评审台、语义修复、漂移文档同步、QA 重写、Validator 加固

- 状态：`verified`
- 日期：2026-08-19
- 提出人：项目负责人
- 目标版本：项目级策划知识库 v0.4 final rework / 正文 revision 2026-08-19.2（涉及 IN-01/06/08、GR-05/10、GP-07/09、M01/M02 等）
- 原因：CHG-012 收尾轮后，底层 canonical 基本完成，但网页、评审入口、QA 和部分语义仍未闭环：M01/M02 无网页模块页面（仅 canonical/chunk/搜索/router 旁路接入）、决策卡只有 Markdown 无网页评审台、ResultHash 口径不一致、IN-06-Q07 残留 questionRef、GR05/GR10 仍用肯定式 supersedes、5 份源文档哈希漂移、QA waitForSystem 未验证真实路由 ID、validator 缺少 P0 归类/原子 questionRefs/源文档哈希检查。
- 新规则：
  1. **M01/M02 网页接入**：build-web-model.mjs 新增 moduleRegistry（含 sections/overview/statusAxes）和 decisionCardRegistry 到 catalog；index.html 新增 `renderModuleDetail`/`renderModuleDetailContent` 渲染模块正文（含状态轴、章节、crossRefs、aggregatedConflicts）；支持 `#module/M01`、`#module/M02`、`#module/M01/M01-S3`、`#module/M02/M02-S2` 稳定深链；兼容旧 `#M01`/`#M02` 重定向；战斗页增加"进入战斗专业正文"、数值页增加"进入数值框架v2专业正文"；搜索结果点击模块原子后导航到 `#module/<parentId>/<sectionId>`。
  2. **决策卡评审台**：新建 `decision-card-registry.json`（schema `vgame-decision-card-registry/v1`，16 张卡 DC-A~DC-P，每卡含 id/theme/confirmedFacts/conflicts/options/affectedSystems/aiRecommendation/singleQuestion/closeableQuestionIds/supplementaryItems）；网页新增 `renderDecisionCards`/`renderDecisionCard` 渲染完整卡片（主题/已确认事实/冲突/选项/影响系统/AI推荐/单问/可关问题ID）；支持选择方案、评论自动暂存、刷新恢复；JSON 导出含完整卡片 ID/选择/评论 + catalog.decisionCards 统计；Markdown 导出含决策卡裁决记录；修复漏掉的 P0 `SYS-OUT-GP-02-Q01`（高难主线缺失 1/5/6/7 章共 20 个地图节点，并入 DC-B）；所有 P0 openQuestion 新增 `decisionCardId` 或 `resolutionOwner` 机器可读归类（33 P0 全部映射到 16 张卡）。
  3. **语义修复**：
     - ResultHash：SYS-IN-01-R05 sourceFact/acceptance、REL01 description、flow step description、overview output 全部修正为"BattleRecord/ResultHash/Version 仅在 NormalMessageProcessor 路径赋值，PVPVEMode 重写后不赋"；M01 Markdown 同步。
     - 大秘境：GP-09 REL02 description 明确"MysteryMode.cs 为空类（仅继承 BaseGameMode，无 override），战斗内词缀 C# 实装为 GAP"。
     - 专武与收容物：GR-05 REL01 和 GR-10 REL01 从 `supersedes` 改为新增关系类型 `migrates-to`（候选迁移），description 明确"不得使用肯定式 supersedes"；knowledge-model.json 新增 `migrates-to` 关系类型。
     - 战斗结算：IN-06-R08 acceptance 删除"断线已有可执行判定"改为"断线重连/判定的可执行性=UNKNOWN"；IN-06 sectionApplicability 删除残留的 IN-06-Q07 questionRef；IN-08-REL04 从"把胜负与评价交主线进度更新"改为 CROSS_SOURCE_SYNTHESIS + "不得无证据肯定已上报主线"；GP-07-REL04 从"DropId 真实入账"改为"配置存在不等于真实入账"；GP-07-REL05 从"知识框架 §2.2 定位"改为引用 Design Doc + 代码证据。
     - GP-09 CONTRACT-BATTLE-RESULT ruleRefs 从 R04/R06 改为 R05/R06（真实结果/消费边界）。
     - GR-10 开放条件 C02/UI02 状态从 WORKING_COPY_OBSERVED_CONFLICT 改为 DESIGN_GAP（Draft 反推，非工作副本观察）。
     - SU-12 友情点 EV08 引用修正（FriendsGiftPoint 来自 ExcelDataDefine.lua）；发言 CD EX10 状态改 UNKNOWN_ENFORCEMENT。
     - M02 §0.5 从"45 系统真实映射"收窄为"41 个显式映射 + 4 个域级占位（SU09/SU10/SU12/SU14）"；M02 crossRefs 补齐 CONTRACT-SWEEP/LEVEL-ENTRY 使契约数量与正文一致。
     - HANDOFF/work-packages "友情点配置和Lua齐全"越界说法修正为"配置与Lua代码存在（工作副本观察），正式服发放状态 UNKNOWN"。
     - knowledge-model.json SU-15 名称从"月卡/礼包/付费商品"统一为"月卡、礼包与付费商品"（与 detail 一致）。
  4. **漂移文档同步**：5 份漂移源文档（公会系统/映射装备数值/章节任务重设计/主角等级/主线关卡）SHA256 重新计算并更新到 project-planning-framework.json，同时更新映射装备/章节任务的 statusAxes 元数据；framework validation 18→19/19，52/52 哈希匹配。
  5. **QA 重写**：ROOT 基于脚本位置计算（不硬编码 D 盘）；waitForSystem 验证真实路由 ID（breadcrumb 含 systemId）、详情标题（H1 含系统名）和 registry 加载；关系表检查目标系统/证据列非空/provenance 可见；新增 M01/M02 正文页和章节深链测试、旧路由重定向测试；决策卡数量/DC-A/DC-P/包含 GP-02-Q01 的卡片测试；评论保存+刷新恢复测试；JSON/Markdown 实际下载内容验证（不只检查按钮）；桌面 1440 + 移动 390；截图路径与报告一致。
  6. **Validator 加固（80→87 检查）**：新增 `atom-question-refs-resolve`（原子 questionRefs 必须指向本系统存在的 openQuestion）、`p0-question-classification`（P0 必须有 decisionCardId 或合法 resolutionOwner）、`decision-card-registry`（注册表存在/数量 14-18/字段完整/cardId 可解析）、`web-module-registry`（生成物含 moduleRegistry/decisionCardRegistry）、`m02-mapping-claim-consistent`（宣称 45 映射时必须覆盖 45 或收窄声明）、`source-document-hashes`（52 份源文档哈希不漂移）、`relation-types-includes-migrates-to`；负例 13→23 个（新增 N13-N22 覆盖 P0 归类/注册表缺失/数量越界/questionRefs 悬挂/哈希漂移/M02 声称/moduleRegistry 缺失/migrates-to 缺失/M01 正文篡改/报告错误统计）。
  7. **状态与文档**：workflow phase=review, outcome=needs_revision（门禁全通过后改 waiting_human）；新增本轮 CHG-013；最终返工完成报告重写为当前自洽版本（旧 14 卡/4/4/67/67/224 移入 change log）。
- 明确不变项：Vgame SVN 工程只读；review_approved=false、delivery_accepted=false 保持；不代主策裁决。

| 影响对象 | ID/路径 | 责任角色 | 同步状态 | 验证证据 |
|---|---|---|---|---|
| 网页正文 | `knowledge-base/index.html` | integrator | synced | moduleRegistry/decisionCardRegistry 接入、模块正文渲染、决策卡评审台、搜索定位、旧路由重定向 |
| 构建器 | `knowledge-base/build-web-model.mjs` | integrator | synced | 45 系统 + 2 模块 + 16 决策卡；moduleRegistry/decisionCardRegistry 写入 catalog |
| 决策卡注册表 | `knowledge-base/decision-card-registry.json` | integrator | synced | 16 张卡 DC-A~DC-P；含 GP-02-Q01 修复 |
| 校验器 | `knowledge-base/validate-knowledge-base.mjs` | integrator | synced | 87 检查；负例 23/23 拦截 |
| 语义修复 | IN-01/06/08、GR-05/10、GP-07/09、M01/M02、SU-12、knowledge-model | integrator | synced | revision 2026-08-19.2 |
| 漂移文档 | `project-planning-framework.json` | integrator | synced | 5 份文档哈希更新；framework validation 19/19 |
| QA | `qa/knowledge-base-qa.mjs` | integrator | verified | 45 系统 + M01/M02 + 决策卡 + 导出 + 评论恢复；0 失败 |
| 负例 | `knowledge-base/tests/validate-negative.test.mjs` | integrator | verified | 23/23 拦截 |
| 交接统计 | HANDOFF/06-review/待裁决清单/最终返工完成报告/00-workflow-state | change-sync-reviewer | synced | 236 问（33 P0 / 126 P1 / 77 P2）、2619 原子、16 卡、87 检查 |

## CHG-013 复核结论

- 是否重走契约确认：否；知识框架范围不变。
- 是否重走一致性评审：是；validator 新增 7 项检查防止 P0 未归类/原子 questionRefs 悬挂/源文档哈希漂移/M02 映射声称/moduleRegistry 缺失等。
- 是否重新验收：是；build/validator 87 检查/route 12 样例/负例 23 项/framework 19/19/check.ps1 FAIL 0/QA（桌面+移动 0 失败）全部执行。
- 当前门禁：`review_approved=false`、`delivery_accepted=false` 保持；M01/M02 可在网页完整浏览、16 张决策卡可在网页评论和导出、所有 P0 完成机器可读归类、语义错误关闭、framework validation 19/19、QA 不再假阳性。

---

## CHG-014 决策卡规范化与路由语义加固（2026-08-20）

**变更人**：integrator  
**变更类型**：AI_FIX（决策卡 ID 规范化 + validator 双向校验 + 路由语义加固 + QA 加固）  
**影响范围**：决策卡注册表、validator、路由脚本、路由测试、负例测试、QA 脚本、决策卡 markdown、系统详情 JSON、workflow/HANDOFF/报告

### 变更内容

1. **决策卡注册表规范化**：16 张卡的 `closeableQuestionIds` 全部从短 ID 转为 canonical ID（`SYS-OUT-*` / `SYS-IN-*` 格式）；DC-G 移除已删除的 `SYS-IN-06-Q07`；`SYS-OUT-GP-02-Q01` 显式列入 DC-B；5 个 P1/P2 问题（SYS-IN-06-Q06/Q08/Q09、SYS-IN-08-Q05/Q06）从 `DEFERRED_DETAIL` 改为 `decisionCardId` 完成双向闭环。
2. **Validator 双向一致性校验**：`decision-card-registry` 检查升级为完整双向校验（canonical 格式 + 跨卡唯一 + 存在性 + closeableQuestionIds↔decisionCardId 双向匹配 + P0 反向覆盖）。
3. **负例测试 23→27**：N23 短 ID 格式、N24 引用不存在问题、N25 双向不一致、N26 P0 不在 closeableQuestionIds 中。
4. **路由语义加固**：quick 档模块正文降为 L1（不加载全文）；消除"未命中具体系统"与模块命中的矛盾；新增 `catalogLayers` 状态分层（confirmed_live/working_copy_observed/candidate_pending/closed_or_deprecated）。
5. **路由测试 12→16**：R9/R10 quick 档模块 L1 + reason 断言；R11 catalogLayers 存在且含 4 键；R12 M01 直达不出现矛盾 unknowns。
6. **QA 加固**：新增 1280px 桌面视口（3 视口 × 45 系统 = 135 页）；canonical ID 验证；模块页评论抽屉未自动打开检查。
7. **源文档哈希同步**：映射装备数值设计文档 SHA256 更新。
8. **决策卡 markdown 同步**：16 张卡 + README 全部更新为 canonical ID。

### 变更后门禁

| 门禁 | 结果 |
|---|---|
| build | ✅ exit 0, 45 系统 + 2 模块, 2619 原子 + 18 模块条目 |
| validator | ✅ 87/87 passed |
| 负例 | ✅ 27/27 拦截 |
| 路由 | ✅ 16/16 PASS |
| framework | ✅ 19/19, 52/52 哈希匹配 |
| check.ps1 | ✅ FAIL 0, WARN 759 |
| QA | ✅ 0 failures, 3 视口 135 页, 0 console/page error |

### 变更后权威统计

| 维度 | 数值 |
|---|---|
| 系统 | 45 |
| 专业模块 | 2 |
| 详情原子 | 2619 |
| 模块条目 | 18 |
| 关系类型 | 12 |
| 共享契约 | 8 |
| openQuestions | 236（33 P0 / 126 P1 / 77 P2） |
| 决策卡 | 16（canonical ID 双向一致） |
| validator 检查 | 87 |
| 负例测试 | 27 |
| 路由样例 | 16 |
| framework 源文档 | 52（哈希全部匹配） |
| QA 视口 | 3（1440 / 1280 / 390） |

### SV N 修改声明

- **本仓库（D:\Vgame_design）**：仅修改 `output/项目级策划知识框架/` 下的知识库文件（JSON/MD/JS/HTML）、`skills/vgame-knowledge-router/scripts/` 下的路由脚本与测试、`project-planning-framework.json` 中的源文档哈希。
- **VGAME_ROOT（SVN 工作副本）**：**未修改**。本轮全部为知识库侧文档/脚本/验证变更，未触碰 SVN 下的真实配置或代码。

---

## CHG-015 独立终审 AI 自修复轮

- 状态：`verified`
- 日期：2026-08-20
- 提出人：项目负责人（独立终审）
- 目标版本：项目级策划知识库 v0.5-review-candidate（CHG-015）
- 原因：独立终审发现 P0/P1 级 AI 可自修问题：DC-Q 缺失、DC-O confirmedFacts 错误、GP-09 状态残留"已开放/未开放"、GP-07 契约错绑、GR-10 证据路径错误+证据缺失、SU-12 proto/ChatSystem 行号漂移、IN-08 DoGameOver 行号错误、M02 映射口径不准确、GP-02 Q01 decisionCardId 未指向 DC-Q、growth skill 缺 C-001 警告、QA false-green（.comment-drawer 选择器错误、waitForSystem 缺 registry ID 验证、无搜索测试、无离线 sectionContent 测试）。

### 变更内容

1. **DC-Q 新增**：从 DC-B 拆分高难主线缺失节点（SYS-OUT-GP-02-Q01）为独立决策卡 DC-Q（3 选项：补齐/收缩/分版本补齐）；DC-B closeableQuestionIds 移除 Q01；GP-02 Q01 decisionCardId 改为 DC-Q。
2. **DC-O confirmedFacts 修正**：CheckSendCD 调用方列表修正为 SendGIF+SendTeamEmote+SendPVPPVERecord；proto 行号 2099-2100→2111-2112。
3. **GP-09 全状态统一**：大秘境 REL02/REL03/REL04 状态从 KNOWLEDGE_CURRENT_CLOSED 改为 WORKING_COPY_OBSERVED_UNKNOWN_LIVE；M01 正文清除"未开放"；90-状态与证据.md 和 05-status-conflict-register.md 同步。
4. **GP-07 契约重绑**：CONTRACT-BATTLE-RESULT ruleRefs R04/R06→R02/R04；CONTRACT-FAILURE-IDEMPOTENCY ruleRefs R06/EX04→EX04/RW02。
5. **GR-10 证据增强+路径修正**：新增 EV14（unlock.lua L467 [4016] UnLockParams={34}）和 EV15（systemopen.lua L18+L44 UnlockId=4016）并绑定 R05/C02/UI02；EV14/EV15 path 从错误路径 `D:\Vgame\Config\GameConfig\Datas\` 修正为正确路径 `D:\Vgame\HorizonFlyProject\LuaConfig\`。4016 是收容物/旧专武入口；专武经验副本 303 的当前条件是主线 2-4，二者不得混写。
6. **SU-12 行号漂移修正**：CRespReceiveFriendGift 2099-2100→2111-2112，CRespFriendSendGift 1194-1195→1205，ReceivedFriendPoint 3653→3677；ChatSystem.lua StartServerChannelCD 1298→1296，GetServerChannelCDRemainTime 1344→1342，total 1461→1459；ReceiveGift 378→377，CRespReceiveFriendGift 386→385。
7. **IN-08 DoGameOver 行号修正**：GameModeBase.cs IsGameOver 守卫 L34-35→L38-39（经源码核实：L38 `if (IsGameOver)` L39 `return;`）；REL04 补 questionRefs/evidenceRefs；revision 更新为 2026-08-20.1。
8. **M02 映射口径修正**："41 个显式映射"→"41 个显式引用映射（其中养成域 GR-01..GR-10 共 10 系统与配置交付域 17 模块为行级映射，战斗/经济/节奏域为域级引用，非行级）+ 4 个域级占位映射"；M02 markdown §0.5 同步。
9. **Growth skill C-001 警告**：growth-module-map.md / verification-mode-map.md / growth-combat-overview.md 三份 reference 文件头部加 C-001 冲突警告。
10. **Validator 87→88**：新增 `p1p2-question-classification` 检查（P1/P2 问题也需 decisionCardId 或合法 resolutionOwner）；反向双向一致性从仅 P0 扩展到 P0/P1/P2 全覆盖。
11. **负例 27→28**：新增 N27 P1 问题缺少 decisionCardId/resolutionOwner。
12. **路由测试 16→19**：新增 R13（大秘境不得进入 confirmed_live）、R14（跑商不得进入 working_copy）、R15（收容物在 candidate_pending）成员级状态断言。
13. **QA false-green 修复**：`.comment-drawer`→`.drawer`（选择器与实际 DOM 一致）；waitForSystem 新增 `registryOk` 验证（`window.VGAME_SYSTEM_DETAILS[id]` 存在）；新增搜索功能验证（"玩法局内模式" 有结果）；新增离线 sectionContent 验证（M01 ≥2 章节有 >50 字内容）。

### 变更后门禁

| 门禁 | 结果 |
|---|---|
| build | ✅ exit 0, 45 系统 + 2 模块, 2621 原子 + 18 模块条目 |
| validator | ✅ 88/88 passed |
| 负例 | ✅ 28/28 拦截 |
| 路由 | ✅ 19/19 PASS |
| framework | ✅ 19/19, 52/52 哈希匹配 |
| QA | ✅ 0 failures, 3 视口 135 页 + 搜索 + 离线 sectionContent, 0 console/page error |

### 变更后权威统计

| 维度 | 数值 |
|---|---|
| 系统 | 45 |
| 专业模块 | 2 |
| 详情原子 | 2621 |
| 模块条目 | 18 |
| 关系类型 | 12 |
| 共享契约 | 8 |
| openQuestions | 236（33 P0 / 126 P1 / 77 P2） |
| 决策卡 | 17（DC-A~DC-Q, canonical ID, P0/P1/P2 全覆盖双向一致） |
| validator 检查 | 88 |
| 负例测试 | 28 |
| 路由样例 | 19 |
| framework 源文档 | 52（哈希全部匹配） |
| QA 视口 | 3（1440 / 1280 / 390） |

### SVN 修改声明

- **本仓库（D:\Vgame_design）**：仅修改 `output/项目级策划知识框架/` 下的知识库文件（JSON/MD/JS/HTML）、`skills/vgame-knowledge-router/scripts/` 下的路由脚本与测试、`skills/vgame-growth-combat-conversion-map/references/` 下的 reference 文件、QA 脚本。
- **VGAME_ROOT（SVN 工作副本）**：**未修改**。本轮全部为知识库侧文档/脚本/验证变更，未触碰 SVN 下的真实配置或代码。

---

## CHG-016 独立交叉终验整改（2026-08-20）

- 状态：`verified`；workflow=`review/waiting_human`
- 变更人：change-sync-reviewer
- 输入：`review/独立交叉终验结论-2026-08-20.md`
- 原始输入：`C:\Users\songchengze\AppData\Local\Temp\zcode-final-review\独立交叉终验结论-2026-08-20.md`
- 边界：`D:\Vgame` 仅回源只读，未修改 SVN 配置或代码。

### 变更内容

1. **GP-02 真实事实修复**：回源 `level.xlsx`，Type=37 共 35 行，全部 `Vitality=0 / FirstReward=1 / FallReward=1 / MopUp=1`；Unlock=9001..9605。DropId=1 在 `Drop_draw.xlsx` 指向 311035..311039 五个 R 卡随机项，因此保留 P0 冲突，不解释为正确高难奖励。
2. **Skill 与参考资料清理**：发布状态注册表中“工作副本存在”不再直接等于 LIVE；4016 明确为玩家等级 34 的收容物/旧专武入口；专武经验副本 303 独立保持主线 2-4；废弃专武成长成本退出模拟器默认输入；8 个 Drop 源确认无具名 `IsValid`，物理第16列空表头不得命名为 IsValid。
3. **共享契约与路由精度**：新增 `CONTRACT-FAILURE-STATE` 承载全员死亡/战斗失败，`CONTRACT-FAILURE-IDEMPOTENCY` 收窄为断线、重试、幂等；SYS-IN-02-R06 仍保留失败状态关系，没有机械删除。R16 验证“全员死亡”只召回失败状态契约。
4. **责任重分流**：236 问逐问分为 `AI_EVIDENCE=43 / RUNTIME_OWNER=98 / HUMAN_DECISION=26 / DEFERRED_DETAIL=69`；只有 HUMAN_DECISION 允许持有 `decisionCardId`。
5. **决策卡重构**：17 张卡 A-Q 全部改为一卡一个互斥单选；DC-A/DC-D/DC-G/DC-O 等旧过度绑定拆开；卡片只关闭 26 个 canonical `closeableQuestionIds`，不得把部分相关问题批量 resolved。
6. **证据与关系**：276 条关系全部要求显式 provenance；补齐缺失来源性质。SU-12、GP-09、GR-05、M01/M02 的行号、行数、镜像文件数与映射口径按当前工作副本修正。
7. **QA 行为断言**：增加搜索结果点击后的 hash/目标 registry/滚动/高亮，同 hash 重导航，章节完整正文按钮，决策选择刷新恢复，决策卡专用 JSON/Markdown 导出内容；卡片范围文案改为按注册表动态生成。
8. **正式追踪与工作流**：TEMP 终验报告复制到 `review/` 并建立整改基线；workflow 已按规定脚本从旧 `waiting_human` 退回 `needs_revision`。

### 当前 canonical 统计

| 维度 | 当前值 |
|---|---:|
| 系统正文 | 45 |
| 专业模块 | 2 |
| 详情原子 | 2622 |
| 模块条目 | 18 |
| openQuestions | 236（33 P0 / 126 P1 / 77 P2） |
| 问题责任 | AI_EVIDENCE 43 / RUNTIME_OWNER 98 / HUMAN_DECISION 26 / DEFERRED_DETAIL 69 |
| 决策卡 | 17（覆盖 26 个 HUMAN_DECISION） |
| 关系 | 276（全部显式 provenance） |
| 共享契约 | 9 |
| validator | 88 |
| 路由样例 | 20 |

### 门禁记录

最终门禁结果见 `review/终验整改完成报告-2026-08-20.md`：build 45+2 / 2622 原子，validator 88/88，负例 30/30，route 20/20，framework 19/19，QA failures 0，check.ps1 FAIL 0 / WARN 766。生成物、36 张 PNG 与 12 个导出文件分别统计。
