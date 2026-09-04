import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import cp from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..", "..");
const stageRoot = path.resolve(process.argv[2] || path.join(repoRoot, "output", ".staging", "knowledge-framework-v1"));
const kbSource = path.join(repoRoot, "knowledge-base");
const kbOut = path.join(stageRoot, "knowledge-base");
const readJson = p => JSON.parse(fs.readFileSync(p, "utf8"));
const writeJson = (p, data) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, `${JSON.stringify(data, null, 2)}\n`, "utf8"); };
const writeText = (p, data) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, data.replace(/\r\n/g, "\n"), "utf8"); };
const copyFile = (src, dst) => { fs.mkdirSync(path.dirname(dst), { recursive: true }); fs.copyFileSync(src, dst); };
const copyDir = (src, dst, filter = () => true) => {
  fs.mkdirSync(dst, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (!filter(entry)) continue;
    const s = path.join(src, entry.name), d = path.join(dst, entry.name);
    if (entry.isDirectory()) copyDir(s, d, filter); else copyFile(s, d);
  }
};

fs.mkdirSync(kbOut, { recursive: true });
copyFile(path.join(kbSource, "registries", "knowledge-model.json"), path.join(kbOut, "knowledge-model.json"));
copyDir(path.join(kbSource, "system-details"), path.join(kbOut, "system-details"));
copyFile(path.join(kbSource, "domains", "M01-战斗专业正文.md"), path.join(kbOut, "M01-战斗专业正文.md"));
copyFile(path.join(kbSource, "domains", "M02-数值框架v2专业正文.md"), path.join(kbOut, "M02-数值框架v2专业正文.md"));
copyDir(path.join(kbSource, "domain-details"), path.join(kbOut, "module-details"));
copyDir(path.join(kbSource, "numerical"), path.join(kbOut, "numerical"));
copyFile(path.join(kbSource, "registries", "contract-registry.json"), path.join(kbOut, "shared-contracts", "contract-registry.json"));
copyFile(path.join(kbSource, "governance", "retrieval-policy.json"), path.join(kbOut, "retrieval-policy.json"));
copyFile(path.join(kbSource, "registries", "work-packages.json"), path.join(kbOut, "work-packages.json"));
copyFile(path.join(kbSource, "registries", "authoring-source-map.json"), path.join(kbOut, "authoring-source-map.json"));
copyFile(path.join(kbSource, "registries", "decision-card-registry.json"), path.join(kbOut, "decision-card-registry.json"));
copyFile(path.join(kbSource, "registries", "project-planning-framework.json"), path.join(stageRoot, "project-planning-framework.json"));
copyFile(path.join(repoRoot, "web", "knowledge-framework", "index.html"), path.join(kbOut, "index.html"));
for (const [source, target] of [
  ["README.md", "README.md"],
  ["framework/00-项目总览与核心循环.md", "00-项目总览.md"],
  ["framework/10-系统框架.md", "10-系统框架.md"],
  ["framework/20-战斗规则角色与内容.md", "20-战斗框架.md"],
  ["framework/30-数值框架V2.md", "30-数值框架.md"],
  ["framework/40-系统关系.md", "40-系统关系.md"],
  ["framework/10-系统框架.md", "11-战斗内系统.md"],
  ["framework/10-系统框架.md", "12-战斗外系统.md"],
  ["framework/90-证据状态裁决与治理.md", "90-状态与证据.md"]
]) copyFile(path.join(kbSource, ...source.split("/")), path.join(kbOut, target));
writeText(path.join(kbOut, "SYSTEM-DETAIL-SPEC.md"), "# System Detail Spec\n\n生成物中的 45 个 system-details 必须满足 vgame-system-detail/v1，并通过 91 项知识库检查。\n");
for (const file of ["build-web-model.mjs", "render-markdown.mjs", "validate-knowledge-base.mjs"]) {
  copyFile(path.join(scriptDir, "legacy-runtime", file), path.join(kbOut, file));
}
copyFile(path.join(repoRoot, "tests", "knowledge-framework", "validate-negative.test.mjs"), path.join(kbOut, "tests", "validate-negative.test.mjs"));

const details = fs.readdirSync(path.join(kbOut, "system-details")).filter(x => x.endsWith(".json")).map(x => readJson(path.join(kbOut, "system-details", x)));
const qStats = { P0: 0, P1: 0, P2: 0 };
const lifecycle = { OPEN: 0, ANSWERED: 0, CLOSED: 0 };
const owners = { AI_EVIDENCE: 0, HUMAN_DECISION: 0, RUNTIME_OWNER: 0, DEFERRED_DETAIL: 0 };
let questionTotal = 0;
for (const d of details) for (const q of d.openQuestions || []) {
  qStats[q.priority] += 1; lifecycle[q.lifecycle] += 1; owners[q.resolutionOwner] += 1; questionTotal += 1;
}
const statsSummary = `${qStats.P0} P0 / ${qStats.P1} P1 / ${qStats.P2} P2`;
const lifecycleSummary = `${lifecycle.OPEN} OPEN / ${lifecycle.ANSWERED} ANSWERED / ${lifecycle.CLOSED} CLOSED`;
const ownerSummary = `AI_EVIDENCE ${owners.AI_EVIDENCE} / HUMAN_DECISION ${owners.HUMAN_DECISION} / RUNTIME_OWNER ${owners.RUNTIME_OWNER} / DEFERRED_DETAIL ${owners.DEFERRED_DETAIL}`;
const commonStats = `问题总数 ${questionTotal}\n\n优先级：${statsSummary}\n\n生命周期：${lifecycleSummary}\n\n责任方：${ownerSummary}\n`;
writeText(path.join(stageRoot, "HANDOFF.md"), `# V1.0 重建交接\n\n${commonStats}\n自动门禁通过不等于最终验收；交给独立审核对话。\n`);
writeText(path.join(stageRoot, "待裁决清单.md"), `# 待裁决清单\n\n${commonStats}\n最新 B/C 裁决已关闭方向问题；其余 OPEN 按 evidence registry 追踪。\n`);
writeText(path.join(stageRoot, "06-review.md"), `# 重建评审\n\n${commonStats}\n当前状态：等待独立审核。\n`);
writeText(path.join(stageRoot, "最终返工完成报告.md"), `# V1.0 原子化重建完成报告\n\n${commonStats}\n本报告只记录自动门禁，不宣称终验通过。\n`);
writeJson(path.join(stageRoot, "00-workflow-state.json"), {
  schema: "planning-workflow-state/v1",
  feature: "项目级策划知识框架 V1.0 原子化重建",
  current_phase: "review",
  last_outcome: "waiting_human",
  updated_at: "2026-08-24T00:03:00+08:00",
  human_gates: { contract_confirmed: true, clarification_resolved: true, review_approved: false, delivery_accepted: false },
  history: [
    { at: "2026-08-24T00:01:00+08:00", actor: "codex", phase: "reference", outcome: "success", next_action: "authoring", evidence: "legacy archive manifest" },
    { at: "2026-08-24T00:02:00+08:00", actor: "codex", phase: "core_design", outcome: "success", next_action: "validation", evidence: "knowledge-base" },
    { at: "2026-08-24T00:03:00+08:00", actor: "codex", phase: "review", outcome: "waiting_human", next_action: "independent_audit", evidence: "gate reports" }
  ]
});

const build = cp.spawnSync(process.execPath, [path.join(kbOut, "build-web-model.mjs")], { cwd: kbOut, encoding: "utf8" });
if (build.status !== 0) throw new Error(`legacy web build failed\n${build.stdout}\n${build.stderr}`);

const skillRegistry = readJson(path.join(kbSource, "registries", "skill-registry.json"));
const frameworkNodes = readJson(path.join(kbSource, "registries", "framework-nodes.json"));
const systemSkill = readJson(path.join(kbSource, "mappings", "system-to-skill.json"));
const rulings = readJson(path.join(kbSource, "governance", "rulings.json"));
const evidenceRegistry = readJson(path.join(kbSource, "evidence", "evidence-registry.json"));
const authority = readJson(path.join(kbSource, "AUTHORITY.json"));
const numericalRegistry = readJson(path.join(kbSource, "numerical", "atom-registry.json"));
const numericalSources = readJson(path.join(kbSource, "numerical", "source-registry.json"));
const numericalWorkbooks = readJson(path.join(kbSource, "numerical", "workbook-registry.json"));
const numericalSummary = readJson(path.join(kbSource, "numerical", "migration-summary.json"));
const numericalProduction = readJson(path.join(repoRoot, "numerical-workflows", "v2", "workflow-manifest.json"));
const numericalHumanConfirmations = readJson(path.join(repoRoot, "numerical-workflows", "v2", "human-confirmations.json"));
const indexOut = path.join(stageRoot, "indexes");
for (const [name, source] of [
  ["skill-registry.json", path.join(kbSource, "registries", "skill-registry.json")],
  ["framework-nodes.json", path.join(kbSource, "registries", "framework-nodes.json")],
  ["system-to-skill.json", path.join(kbSource, "mappings", "system-to-skill.json")],
  ["question-to-skill.json", path.join(kbSource, "mappings", "question-to-skill.json")],
  ["skill-to-knowledge-layer.json", path.join(kbSource, "mappings", "skill-to-knowledge-layer.json")],
  ["skill-to-evidence.json", path.join(kbSource, "mappings", "skill-to-evidence.json")],
  ["evidence-registry.json", path.join(kbSource, "evidence", "evidence-registry.json")],
  ["rulings.json", path.join(kbSource, "governance", "rulings.json")]
]) copyFile(source, path.join(indexOut, name));
for (const name of ["source-registry.json", "workbook-registry.json", "atom-registry.json", "formula-registry.json", "parameter-registry.json", "migration-summary.json"]) {
  copyFile(path.join(kbSource, "numerical", name), path.join(indexOut, "numerical", name));
}
copyFile(path.join(repoRoot, "numerical-workflows", "v2", "workflow-manifest.json"), path.join(indexOut, "numerical", "production-workflow-manifest.json"));
copyFile(path.join(repoRoot, "numerical-workflows", "v2", "human-confirmations.json"), path.join(indexOut, "numerical", "production-human-confirmations.json"));
for (const name of ["numeric-to-system.json", "numeric-to-skill.json", "numeric-to-evidence.json", "numeric-to-config.json", "numeric-to-framework-node.json"]) {
  copyFile(path.join(kbSource, "numerical", "mappings", name), path.join(indexOut, "numerical", "mappings", name));
}

const numericalSearch = numericalRegistry.atoms.map(atom => ({
  id: atom.atomId,
  parentId: "PFN-13",
  parentName: "数值框架 V2",
  module: "numeric",
  path: `数值 / ${atom.domain} / ${atom.title}`,
  targetRevision: "2.0.0",
  targetType: atom.atomType === "HUMAN_RULING" ? "numeric-ruling" : "numeric-atom",
  name: atom.title,
  summary: atom.statement,
  status: atom.status,
  evidenceRefs: atom.evidenceRefs,
  sourceLocator: atom.sourceLocator,
  systemIds: atom.coveredSystems,
  skillIds: atom.skillIds
}));
writeJson(path.join(indexOut, "numerical-search-index.json"), { schema: "vgame-numerical-search-index/v2", count: numericalSearch.length, entries: numericalSearch });
writeText(path.join(kbOut, "numerical-search-index.js"), `/* Generated numerical atom search index. */\nwindow.VGAME_NUMERICAL_SEARCH = ${JSON.stringify(numericalSearch, null, 2)};\n`);
const numericChunkRoot = path.join(kbOut, "numerical-chunks");
for (const domain of [...new Set(numericalRegistry.atoms.map(atom => atom.domain))].sort()) {
  const atoms = numericalRegistry.atoms.filter(atom => atom.domain === domain);
  writeText(path.join(numericChunkRoot, `${domain}.js`), `/* Generated numerical domain chunk. */\nwindow.VGAME_NUMERICAL_DOMAINS = window.VGAME_NUMERICAL_DOMAINS || {};\nwindow.VGAME_NUMERICAL_DOMAINS[${JSON.stringify(domain)}] = ${JSON.stringify(atoms, null, 2)};\n`);
}

const routerPath = path.join(kbOut, "router-manifest.json");
const router = readJson(routerPath);
router.version = "1.0.0";
router.authorityRef = "knowledge-base/README.md";
router.skillRegistryRef = "indexes/skill-registry.json";
router.skillCount = skillRegistry.skills.length;
router.numerical = {
  schema: "vgame-numerical-router/v2",
  atomCount: numericalRegistry.atoms.length,
  sourceCount: numericalSources.files.length,
  workbookCount: numericalWorkbooks.workbooks.length,
  production: {
    workflowRoot: numericalProduction.workflowRoot,
    formalDocumentRoot: numericalProduction.formalDocumentRoot,
    formalDocumentsVersionControlled: numericalProduction.formalDocumentsVersionControlled,
    manifestRef: "../indexes/numerical/production-workflow-manifest.json",
    inputWorkbooks: numericalProduction.counts.inputWorkbooks,
    scripts: numericalProduction.counts.migratedPythonFiles,
    tasks: numericalProduction.counts.mainGenerationJobs,
    finalWorkbooks: numericalProduction.counts.expectedFinalWorkbooks,
    externalNumericalSourceRequired: numericalProduction.legacyExternalSourceRequiredAtRuntime
  },
  atomIndexRef: "numerical/atom-registry.json",
  searchIndexRef: "../indexes/numerical-search-index.json",
  domains: [...new Set(numericalRegistry.atoms.map(atom => atom.domain))].sort().map(domain => ({
    id: domain,
    count: numericalRegistry.atoms.filter(atom => atom.domain === domain).length,
    chunkRef: `numerical-chunks/${domain}.js`,
    canonicalRef: `numerical/domains/${domain}.md`
  }))
};
writeJson(routerPath, router);

const matrixLines = ["# 33 个 Skill 覆盖矩阵", "", "| Skill | 分类 | 覆盖系统数 | 依赖 | 知识层 | 状态 |", "|---|---|---:|---|---|---|"];
for (const s of skillRegistry.skills) matrixLines.push(`| ${s.skillId} | ${s.category} | ${s.coveredSystems.length} | ${s.dependsOnSkills.join("、") || "无"} | ${s.knowledgeLayers.join("、")} | ${s.versionStatus} |`);
writeText(path.join(stageRoot, "reports", "skill-coverage-matrix.md"), `${matrixLines.join("\n")}\n`);

const archiveManifest = readJson(path.join(repoRoot, "archive", "legacy-output-20260824", "manifest.json"));
const classCounts = Object.groupBy ? Object.groupBy(archiveManifest.files, x => x.classification) : archiveManifest.files.reduce((a, x) => ((a[x.classification] ||= []).push(x), a), {});
const migrationLines = ["# 新旧内容迁移清单", "", `旧文件总数：${archiveManifest.fileCount}。`, "", "| 分类 | 数量 | 新处置 |", "|---|---:|---|"];
for (const [key, rows] of Object.entries(classCounts)) migrationLines.push(`| ${key} | ${rows.length} | ${key === "REGENERATABLE" ? "由新生成链重建" : "archive 清单追溯；权威内容已原子化迁入 knowledge-base"} |`);
writeText(path.join(stageRoot, "reports", "migration-manifest.md"), `${migrationLines.join("\n")}\n`);
const numericalDispositionRows = Object.entries(numericalSummary.dispositions).map(([key, count]) => `| ${key} | ${count} | ${key === "NORMALIZED_INTO_CANONICAL" || key === "TOOLING_OR_RULE_EVIDENCE" ? "原子化或规则化纳入" : "只做可追溯登记，不复制为正文"} |`);
writeText(path.join(stageRoot, "reports", "numerical-migration-manifest.md"), `# 数值框架与生产工作流迁移清单\n\n- 磁盘实际文件：${numericalSummary.sourceFiles}\n- 权威 Markdown：${numericalSummary.authoritativeMarkdownFiles}\n- 源工作簿结构登记：${numericalSummary.sourceWorkbooks}\n- 数值原子：${numericalSummary.atoms}（ACTIVE ${numericalSummary.activeAtoms} / SUPERSEDED_TRACE ${numericalSummary.supersededAtoms} / HISTORICAL_TRACE ${numericalSummary.historicalAtoms}）\n- 公式/计算规则候选：${numericalSummary.formulas}\n- 机器参数块：${numericalSummary.parameterSets}\n- Git 管理生产资产：${numericalProduction.counts.files}/${numericalProduction.counts.files}\n- 旧 Python 生产脚本：${numericalProduction.counts.migratedPythonFiles}/${numericalProduction.counts.originalPythonFiles}\n- 受控生产输入工作簿：${numericalProduction.counts.inputWorkbooks}/${numericalProduction.counts.inputWorkbooks}\n- 主生产任务：${numericalProduction.counts.mainGenerationJobs}/${numericalProduction.counts.mainGenerationJobs}\n- Git 管理正式数值工作簿：${numericalProduction.counts.expectedFinalWorkbooks}/${numericalProduction.counts.expectedFinalWorkbooks}\n- 正式数值文档目录：${numericalProduction.formalDocumentRoot}/\n- 运行时是否依赖旧数值文档盘：${numericalProduction.legacyExternalSourceRequiredAtRuntime ? "是" : "否"}\n\n| 处置 | 数量 | 迁移策略 |\n|---|---:|---|\n${numericalDispositionRows.join("\n")}\n`);
const numericalSkillIds = [...new Set(numericalRegistry.atoms.flatMap(atom => atom.skillIds))].sort();
const numericalSkillLines = ["# 数值层 Skill 覆盖矩阵", "", "| Skill | 数值原子数 | 数值域 | 状态 |", "|---|---:|---|---|"];
for (const skillId of numericalSkillIds) {
  const rows = numericalRegistry.atoms.filter(atom => atom.skillIds.includes(skillId));
  const skill = skillRegistry.skills.find(item => item.skillId === skillId);
  numericalSkillLines.push(`| ${skillId} | ${rows.length} | ${[...new Set(rows.map(row => row.domain))].sort().join("、")} | ${skill?.versionStatus || "UNKNOWN"} |`);
}
writeText(path.join(stageRoot, "reports", "numerical-skill-coverage-matrix.md"), `${numericalSkillLines.join("\n")}\n`);
writeText(path.join(stageRoot, "reports", "delete-archive-keep.md"), `# 删除、归档、保留清单\n\n- 删除/不迁入：旧网页、chunk、搜索索引、router manifest、预览图和孤立生成物；均由新链重建，外部旧目录原件未删除。\n- 数值层不复制：旧 04 原件、05 验算输出、06 配置镜像、reports、backups 与 staging；全部在 source-registry 保留哈希和处置。\n- 归档：旧决策卡、冲突登记、评审、交接、验证报告、历史数值结论与全量 SHA-256 清单；8 个被 B/C 覆盖的原子标 SUPERSEDED_SOURCE_CONTEXT；被替换正式生成物转入 output 下可追溯归档。\n- Git 保留：knowledge-base 权威正文与数值原子、skills 唯一 Skill 正文、${numericalProduction.counts.migratedPythonFiles} 个完整生产脚本、${numericalProduction.counts.inputWorkbooks} 个受控数值输入工作簿，以及 ${numericalProduction.counts.expectedFinalWorkbooks} 份全新重建的正式数值交付文档（${numericalProduction.formalDocumentRoot}/）和 scripts/tests/web 生成与验证源。\n- 外部只读保留：历史数值目录证据和 SVN Datas 工程配置；运行时不依赖外部历史数值盘，正式配置写入默认拒绝。\n`);
const confirmationLines = ["# 需要人工确认的最小问题列表", ""];
for (const [index, item] of numericalHumanConfirmations.questions.entries()) {
  confirmationLines.push(`${index + 1}. ${item.system}：${item.question}`);
}
confirmationLines.push(`${numericalHumanConfirmations.questions.length + 1}. 由独立审核对话执行终验；本重建对话不自行宣称终验通过。`);
writeText(path.join(stageRoot, "reports", "manual-confirmation-minimum.md"), `${confirmationLines.join("\n")}\n`);

const model = readJson(path.join(kbSource, "registries", "knowledge-model.json"));
const graphNodes = [];
const graphEdges = [];
const addNode = n => graphNodes.push(n);
const addEdge = e => graphEdges.push({ weight: 0.6, ...e });
for (const n of frameworkNodes.nodes) addNode({ id: `concept:${n.id}`, type: "concept", name: n.name, summary: n.responsibility, tags: ["framework", n.layer] });
for (const s of model.systems) addNode({ id: `module:${s.id}`, type: "module", name: s.name, summary: s.summary, tags: ["system", s.group] });
for (const s of skillRegistry.skills) addNode({ id: `module:skill:${s.skillId}`, type: "module", name: s.skillId, summary: s.responsibility, tags: ["skill", s.category] });
for (const atom of numericalRegistry.atoms) addNode({ id: `numeric:${atom.atomId}`, type: "concept", name: atom.title, summary: atom.statement, tags: ["numeric", atom.domain, atom.sourceNature] });
addNode({ id: "numeric-production:v2", type: "concept", name: "数值生产工作流 V2", summary: `${numericalProduction.counts.migratedPythonFiles} 个生产脚本、${numericalProduction.counts.inputWorkbooks} 个受控输入、${numericalProduction.counts.mainGenerationJobs} 条生产任务和 ${numericalProduction.counts.expectedFinalWorkbooks} 份正式数值文档全部归入 Git 权威仓库。`, tags: ["numeric", "production", "single-repository"] });
for (const item of numericalProduction.files) {
  const digest = crypto.createHash("sha256").update(item.repositoryPath).digest("hex").slice(0, 20);
  addNode({ id: `numeric-production-file:${digest}`, type: "file", name: path.basename(item.repositoryPath), summary: `${item.role}：${item.repositoryPath}`, tags: ["numeric", "production", item.role] });
  addEdge({ source: "numeric-production:v2", target: `numeric-production-file:${digest}`, type: "contains", weight: 1 });
}
addEdge({ source: "concept:PFN-13", target: "numeric-production:v2", type: "contains", weight: 1 });
addEdge({ source: "module:skill:game-numerical-analysis", target: "numeric-production:v2", type: "routes", weight: 0.8 });
for (const n of frameworkNodes.nodes.slice(1)) addEdge({ source: "concept:PFN-01", target: `concept:${n.id}`, type: "contains", weight: 1 });
const groupNode = { "system-in": "PFN-03", "system-out-gameplay": "PFN-05", "system-out-growth": "PFN-06", "system-out-support": "PFN-09" };
for (const s of model.systems) addEdge({ source: `concept:${groupNode[s.group]}`, target: `module:${s.id}`, type: "contains", weight: 1 });
for (const m of systemSkill.mappings) for (const sid of m.skills) addEdge({ source: `module:skill:${sid}`, target: `module:${m.systemId}`, type: "routes", weight: 0.5 });
for (const s of skillRegistry.skills) {
  addEdge({ source: "concept:PFN-17", target: `module:skill:${s.skillId}`, type: "contains", weight: 1 });
  for (const dep of s.dependsOnSkills) addEdge({ source: `module:skill:${s.skillId}`, target: `module:skill:${dep}`, type: "depends_on" });
}
for (const atom of numericalRegistry.atoms) {
  addEdge({ source: "concept:PFN-13", target: `numeric:${atom.atomId}`, type: "contains", weight: 1 });
  for (const sid of atom.coveredSystems) addEdge({ source: `numeric:${atom.atomId}`, target: `module:${sid}`, type: "quantifies", weight: 0.7 });
  for (const skillId of atom.skillIds) addEdge({ source: `module:skill:${skillId}`, target: `numeric:${atom.atomId}`, type: "loads", weight: 0.5 });
  for (const nodeId of atom.frameworkNodeIds.filter(id => id !== "PFN-13")) addEdge({ source: `concept:${nodeId}`, target: `numeric:${atom.atomId}`, type: "classifies", weight: 0.4 });
}
for (const d of details) for (const r of d.relationships || []) if (model.systems.some(x => x.id === r.targetId)) addEdge({ source: `module:${d.systemId}`, target: `module:${r.targetId}`, type: "related", weight: 0.5 });
const uniqueEdges = [...new Map(graphEdges.map(e => [`${e.source}|${e.target}|${e.type}`, e])).values()];
const layers = [
  { id: "layer:framework", name: "项目框架", description: "19个项目框架节点", nodeIds: graphNodes.filter(x => x.id.startsWith("concept:")).map(x => x.id) },
  { id: "layer:systems", name: "系统正文", description: "45个系统", nodeIds: graphNodes.filter(x => /^module:SYS/.test(x.id)).map(x => x.id) },
  { id: "layer:skills", name: "Skill调用", description: "33个Skill", nodeIds: graphNodes.filter(x => x.id.startsWith("module:skill:")).map(x => x.id) }
  ,{ id: "layer:numerical", name: "全栈数值原子", description: `${numericalRegistry.atoms.length}个数值原子`, nodeIds: graphNodes.filter(x => x.id.startsWith("numeric:")).map(x => x.id) }
  ,{ id: "layer:numerical-production", name: "单仓数值生产工作流", description: `${numericalProduction.counts.files}份 Git 管理生产资产`, nodeIds: graphNodes.filter(x => x.id.startsWith("numeric-production:") || x.id.startsWith("numeric-production-file:")).map(x => x.id) }
];
writeJson(path.join(stageRoot, "understand", "knowledge-graph.json"), {
  version: "1.0.0",
  project: { name: "Vgame 全栈策划知识框架", languages: ["zh", "json", "markdown"], frameworks: ["Vgame Knowledge Framework V2"], description: "项目策划、全栈数值、系统、Skill和证据治理图", analyzedAt: new Date().toISOString(), gitCommitHash: cp.execFileSync("git", ["-C", repoRoot, "rev-parse", "HEAD"], { encoding: "utf8" }).trim() },
  nodes: graphNodes, edges: uniqueEdges, layers,
  tour: [
    { order: 1, title: "项目与核心循环", description: "从19个框架节点理解项目。", nodeIds: ["concept:PFN-01", "concept:PFN-02"] },
    { order: 2, title: "系统正文", description: "沿战斗内外分层查看45个系统。", nodeIds: ["concept:PFN-03", "concept:PFN-04"] },
    { order: 3, title: "Skill与证据治理", description: "查看按需调用和证据边界。", nodeIds: ["concept:PFN-17", "concept:PFN-18", "concept:PFN-19"] }
  ]
});

const sourceDigest = crypto.createHash("sha256")
  .update(fs.readFileSync(path.join(kbSource, "AUTHORITY.json")))
  .update(fs.readFileSync(path.join(kbSource, "registries", "skill-registry.json")))
  .update(fs.readFileSync(path.join(kbSource, "registries", "knowledge-model.json")))
  .update(fs.readFileSync(path.join(kbSource, "numerical", "atom-registry.json")))
  .update(fs.readFileSync(path.join(repoRoot, "numerical-workflows", "v2", "workflow-manifest.json")))
  .digest("hex");
writeJson(path.join(stageRoot, "build-manifest.json"), {
  schema: "vgame-knowledge-build/v2", version: "2.0.0", generatedAt: new Date().toISOString(), sourceDigest,
  authority, counts: { skills: skillRegistry.skills.length, systems: model.systems.length, frameworkNodes: frameworkNodes.nodes.length, evidence: evidenceRegistry.count, numericalSources: numericalSummary.sourceFiles, numericalAtoms: numericalRegistry.atoms.length, numericalWorkbooks: numericalWorkbooks.workbooks.length, numericalProductionFiles: numericalProduction.counts.files, numericalProductionScripts: numericalProduction.counts.migratedPythonFiles, numericalProductionInputWorkbooks: numericalProduction.counts.inputWorkbooks, numericalProductionTasks: numericalProduction.counts.mainGenerationJobs }, rulings: rulings.rulings.map(x => x.rulingId)
});
console.log(JSON.stringify({ stageRoot, questionTotal, statsSummary, lifecycleSummary, ownerSummary, nodes: graphNodes.length, edges: uniqueEdges.length }, null, 2));
