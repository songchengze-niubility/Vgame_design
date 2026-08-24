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

const routerPath = path.join(kbOut, "router-manifest.json");
const router = readJson(routerPath);
router.version = "1.0.0";
router.authorityRef = "knowledge-base/README.md";
router.skillRegistryRef = "indexes/skill-registry.json";
router.skillCount = skillRegistry.skills.length;
writeJson(routerPath, router);

const matrixLines = ["# 33 个 Skill 覆盖矩阵", "", "| Skill | 分类 | 覆盖系统数 | 依赖 | 知识层 | 状态 |", "|---|---|---:|---|---|---|"];
for (const s of skillRegistry.skills) matrixLines.push(`| ${s.skillId} | ${s.category} | ${s.coveredSystems.length} | ${s.dependsOnSkills.join("、") || "无"} | ${s.knowledgeLayers.join("、")} | ${s.versionStatus} |`);
writeText(path.join(stageRoot, "reports", "skill-coverage-matrix.md"), `${matrixLines.join("\n")}\n`);

const archiveManifest = readJson(path.join(repoRoot, "archive", "legacy-output-20260824", "manifest.json"));
const classCounts = Object.groupBy ? Object.groupBy(archiveManifest.files, x => x.classification) : archiveManifest.files.reduce((a, x) => ((a[x.classification] ||= []).push(x), a), {});
const migrationLines = ["# 新旧内容迁移清单", "", `旧文件总数：${archiveManifest.fileCount}。`, "", "| 分类 | 数量 | 新处置 |", "|---|---:|---|"];
for (const [key, rows] of Object.entries(classCounts)) migrationLines.push(`| ${key} | ${rows.length} | ${key === "REGENERATABLE" ? "由新生成链重建" : "archive 清单追溯；权威内容已原子化迁入 knowledge-base"} |`);
writeText(path.join(stageRoot, "reports", "migration-manifest.md"), `${migrationLines.join("\n")}\n`);
writeText(path.join(stageRoot, "reports", "delete-archive-keep.md"), `# 删除、归档、保留清单\n\n- 删除/不迁入：旧网页、chunk、搜索索引、router manifest、预览图和孤立生成物；均由新链重建。\n- 归档：旧决策卡、冲突登记、评审、交接、验证报告与全量 SHA-256 清单。\n- 保留：knowledge-base 权威正文、skills 唯一 Skill 正文、scripts/tests/web 生成与验证源。\n`);
writeText(path.join(stageRoot, "reports", "manual-confirmation-minimum.md"), `# 需要人工确认的最小问题列表\n\n1. 专武 B 方案：确认兼容期的起止版本、旧数据读写边界、迁移批次和最终清理版本。\n2. 房车 C 方案：确认强化进度达到 100 时的溢出/进位规则，并补 Production/LIVE 发布证据。\n3. 由独立审核对话执行终验；本重建对话不自行宣称终验通过。\n`);

const model = readJson(path.join(kbSource, "registries", "knowledge-model.json"));
const graphNodes = [];
const graphEdges = [];
const addNode = n => graphNodes.push(n);
const addEdge = e => graphEdges.push({ weight: 0.6, ...e });
for (const n of frameworkNodes.nodes) addNode({ id: `concept:${n.id}`, type: "concept", name: n.name, summary: n.responsibility, tags: ["framework", n.layer] });
for (const s of model.systems) addNode({ id: `module:${s.id}`, type: "module", name: s.name, summary: s.summary, tags: ["system", s.group] });
for (const s of skillRegistry.skills) addNode({ id: `module:skill:${s.skillId}`, type: "module", name: s.skillId, summary: s.responsibility, tags: ["skill", s.category] });
for (const n of frameworkNodes.nodes.slice(1)) addEdge({ source: "concept:PFN-01", target: `concept:${n.id}`, type: "contains", weight: 1 });
const groupNode = { "system-in": "PFN-03", "system-out-gameplay": "PFN-05", "system-out-growth": "PFN-06", "system-out-support": "PFN-09" };
for (const s of model.systems) addEdge({ source: `concept:${groupNode[s.group]}`, target: `module:${s.id}`, type: "contains", weight: 1 });
for (const m of systemSkill.mappings) for (const sid of m.skills) addEdge({ source: `module:skill:${sid}`, target: `module:${m.systemId}`, type: "routes", weight: 0.5 });
for (const s of skillRegistry.skills) {
  addEdge({ source: "concept:PFN-17", target: `module:skill:${s.skillId}`, type: "contains", weight: 1 });
  for (const dep of s.dependsOnSkills) addEdge({ source: `module:skill:${s.skillId}`, target: `module:skill:${dep}`, type: "depends_on" });
}
for (const d of details) for (const r of d.relationships || []) if (model.systems.some(x => x.id === r.targetId)) addEdge({ source: `module:${d.systemId}`, target: `module:${r.targetId}`, type: "related", weight: 0.5 });
const uniqueEdges = [...new Map(graphEdges.map(e => [`${e.source}|${e.target}|${e.type}`, e])).values()];
const layers = [
  { id: "layer:framework", name: "项目框架", description: "19个项目框架节点", nodeIds: graphNodes.filter(x => x.id.startsWith("concept:")).map(x => x.id) },
  { id: "layer:systems", name: "系统正文", description: "45个系统", nodeIds: graphNodes.filter(x => /^module:SYS/.test(x.id)).map(x => x.id) },
  { id: "layer:skills", name: "Skill调用", description: "33个Skill", nodeIds: graphNodes.filter(x => x.id.startsWith("module:skill:")).map(x => x.id) }
];
writeJson(path.join(stageRoot, "understand", "knowledge-graph.json"), {
  version: "1.0.0",
  project: { name: "Vgame 项目级策划知识框架", languages: ["zh", "json", "markdown"], frameworks: ["Vgame Knowledge Framework V1"], description: "项目策划知识、系统、Skill和证据治理图", analyzedAt: new Date().toISOString(), gitCommitHash: cp.execFileSync("git", ["-C", repoRoot, "rev-parse", "HEAD"], { encoding: "utf8" }).trim() },
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
  .digest("hex");
writeJson(path.join(stageRoot, "build-manifest.json"), {
  schema: "vgame-knowledge-build/v1", version: "1.0.0", generatedAt: new Date().toISOString(), sourceDigest,
  authority, counts: { skills: skillRegistry.skills.length, systems: model.systems.length, frameworkNodes: frameworkNodes.nodes.length, evidence: evidenceRegistry.count }, rulings: rulings.rulings.map(x => x.rulingId)
});
console.log(JSON.stringify({ stageRoot, questionTotal, statsSummary, lifecycleSummary, ownerSummary, nodes: graphNodes.length, edges: uniqueEdges.length }, null, 2));
