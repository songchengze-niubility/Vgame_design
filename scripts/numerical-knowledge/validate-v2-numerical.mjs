import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import cp from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..", "..");
const stageRoot = path.resolve(process.argv[2]);
const kb = path.join(repoRoot, "knowledge-base");
const numeric = path.join(kb, "numerical");
const read = p => JSON.parse(fs.readFileSync(p, "utf8"));
const gates = [];
const gate = (name, pass, detail = "") => gates.push({ name, pass: Boolean(pass), detail: String(detail) });

const source = read(path.join(numeric, "source-registry.json"));
const workbooks = read(path.join(numeric, "workbook-registry.json"));
const atoms = read(path.join(numeric, "atom-registry.json"));
const formulas = read(path.join(numeric, "formula-registry.json"));
const parameters = read(path.join(numeric, "parameter-registry.json"));
const summary = read(path.join(numeric, "migration-summary.json"));
const skills = read(path.join(kb, "registries", "skill-registry.json"));
const model = read(path.join(kb, "registries", "knowledge-model.json"));
const framework = read(path.join(kb, "registries", "framework-nodes.json"));
const rulings = read(path.join(kb, "governance", "rulings.json"));
const mappingNames = ["numeric-to-system", "numeric-to-skill", "numeric-to-evidence", "numeric-to-config", "numeric-to-framework-node"];
const mappings = Object.fromEntries(mappingNames.map(name => [name, read(path.join(numeric, "mappings", `${name}.json`))]));

const unique = values => new Set(values).size === values.length;
const portableTextHash = p => crypto.createHash("sha256").update(fs.readFileSync(p, "utf8").replace(/\r\n/g, "\n").replace(/\r/g, "\n")).digest("hex");
const sourceIds = new Set(source.files.map(x => x.sourceId));
const atomIds = new Set(atoms.atoms.map(x => x.atomId));
const skillIds = new Set(skills.skills.map(x => x.skillId));
const systemIds = new Set(model.systems.map(x => x.id));
const frameworkIds = new Set(framework.nodes.map(x => x.id));
const allowedDispositions = new Set(["ARCHIVE_TRACE_ONLY", "MIRROR_OR_STAGING_TRACE_ONLY", "NORMALIZED_INTO_CANONICAL", "REGENERATABLE_OR_READING_OUTPUT", "REGISTERED_EVIDENCE", "SOURCE_WORKBOOK_EVIDENCE", "TOOLING_OR_RULE_EVIDENCE", "VALIDATION_EVIDENCE"]);

gate("source-registry-schema", source.schema === "vgame-numerical-source-registry/v2");
gate("source-files-covered", source.files.length === source.count && source.count === summary.sourceFiles && source.count >= 1000, `${source.count}`);
gate("source-files-unique", unique(source.files.map(x => x.relativePath)) && unique(source.files.map(x => x.sourceId)));
gate("source-hashes-complete", source.files.every(x => /^[0-9a-f]{64}$/.test(x.sha256)));
gate("source-dispositions-complete", source.files.every(x => allowedDispositions.has(x.disposition) && x.reason));
gate("source-paths-relative", source.files.every(x => !path.isAbsolute(x.relativePath) && !x.relativePath.includes("..")));
gate("authoritative-markdown-covered", new Set(atoms.atoms.filter(x => x.sourceId.startsWith("NSRC-")).map(x => x.sourceId)).size === summary.authoritativeMarkdownFiles, `${summary.authoritativeMarkdownFiles}`);

gate("workbook-registry-count", workbooks.workbooks.length === workbooks.count && workbooks.count === summary.sourceWorkbooks, `${workbooks.count}`);
gate("workbook-structures-readable", workbooks.workbooks.every(x => !x.inspectionError && x.sheets.length > 0));
gate("workbook-sheets-unique", workbooks.workbooks.every(x => unique(x.sheets.map(s => s.sheetId)) && unique(x.sheets.map(s => s.name))));

gate("atom-registry-count", atoms.atoms.length === atoms.count && atoms.count === summary.atoms, `${atoms.count}`);
gate("atom-ids-unique", unique(atoms.atoms.map(x => x.atomId)));
gate("atom-required-fields", atoms.atoms.every(x => ["atomId", "atomType", "domain", "title", "statement", "sourceId", "sourceLocator", "sourceNature", "status"].every(k => x[k])));
gate("atom-system-mapping-valid", atoms.atoms.every(x => x.coveredSystems.length > 0 && x.coveredSystems.every(id => systemIds.has(id))));
gate("atom-skill-mapping-valid", atoms.atoms.every(x => x.skillIds.length > 0 && x.skillIds.every(id => skillIds.has(id))));
gate("atom-evidence-valid", atoms.atoms.every(x => x.evidenceRefs.length > 0 && x.evidenceRefs.every(id => sourceIds.has(id) || ["RULING-RV-C", "RULING-EW-B"].includes(id))));
gate("atom-framework-valid", atoms.atoms.every(x => x.frameworkNodeIds.includes("PFN-13") && x.frameworkNodeIds.every(id => frameworkIds.has(id))));
gate("atom-config-boundary", atoms.atoms.every(x => x.configCandidates.length > 0));
gate("mapping-five-complete", mappingNames.every(name => mappings[name].mappings.length === atoms.count && mappings[name].mappings.every(x => atomIds.has(x.atomId))));

const superseded = atoms.atoms.filter(x => x.status === "SUPERSEDED_SOURCE_CONTEXT");
const historical = atoms.atoms.filter(x => x.status === "HISTORICAL_SOURCE_CONTEXT");
gate("superseded-history-preserved", superseded.length === summary.supersededAtoms && superseded.length > 0, `${superseded.length}`);
gate("superseded-history-governed", superseded.every(x => ["RULING-EW-B", "RULING-RV-C"].includes(x.supersededBy) && x.validation.includes("DO_NOT_ROUTE_AS_CURRENT")));
gate("historical-source-context-governed", historical.length === summary.historicalAtoms && historical.length > 0 && historical.every(x => x.validation.includes("DO_NOT_ROUTE_AS_CURRENT")), `${historical.length}`);
const activeText = atoms.atoms.filter(x => x.status === "ACTIVE").map(x => `${x.title} ${x.statement} ${(x.numericStatements || []).join(" ")}`).join("\n");
gate("no-active-old-ew-ruling", !/专武（已废弃）|专武(?:系统|抽卡)?已废弃|当前版本已移除专武|旧消耗不得迁移到收容物|不接入当前验算/.test(activeText));
gate("no-active-old-rv-ruling", !/固定\s*\+?100|不参与随机强化|不参与随机结果/.test(activeText));
gate("latest-rv-ruling-atom", atoms.atoms.some(x => x.atomId === "NATOM-RULING-RV-C" && x.statement.includes("+30/+60/+100") && x.statement.includes("50/30/20")) && rulings.rulings.some(x => x.rulingId === "RULING-RV-C"));
gate("latest-ew-ruling-atom", atoms.atoms.some(x => x.atomId === "NATOM-RULING-EW-B" && x.statement.includes("一个大版本")) && rulings.rulings.some(x => x.rulingId === "RULING-EW-B"));
gate("formula-and-parameter-traceable", formulas.formulas.every(x => atomIds.has(x.atomId) && sourceIds.has(x.sourceId)) && parameters.parameterSets.every(x => atomIds.has(x.atomId) && sourceIds.has(x.sourceId)), `${formulas.count}/${parameters.count}`);

gate("skill-registry-still-33", skills.count === 33 && skills.skills.length === 33 && unique(skills.skills.map(x => x.skillId)), `${skills.skills.length}/33`);
gate("skill-source-hashes-current", skills.skills.every(x => portableTextHash(path.join(repoRoot, x.sourcePath)) === x.sourceSha256));
gate("canonical-not-ignored", cp.spawnSync("git", ["-C", repoRoot, "check-ignore", "knowledge-base/numerical/atom-registry.json"]).status !== 0);

const stageKb = path.join(stageRoot, "knowledge-base");
const stageAtoms = read(path.join(stageKb, "numerical", "atom-registry.json"));
const router = read(path.join(stageKb, "router-manifest.json"));
const numericSearch = read(path.join(stageRoot, "indexes", "numerical-search-index.json"));
const graph = read(path.join(stageRoot, "understand", "knowledge-graph.json"));
gate("generated-canonical-deep-equal", JSON.stringify(stageAtoms) === JSON.stringify(atoms));
gate("generated-numerical-search", numericSearch.count === atoms.count && numericSearch.entries.length === atoms.count, `${numericSearch.count}`);
gate("generated-numerical-chunks", router.numerical.domains.every(x => fs.existsSync(path.join(stageKb, x.chunkRef))) && router.numerical.domains.length === 9, `${router.numerical.domains.length}`);
gate("generated-router-manifest", router.numerical.atomCount === atoms.count && router.numerical.sourceCount === source.count && router.numerical.workbookCount === workbooks.count);
gate("generated-web-loads-numerical-index", fs.readFileSync(path.join(stageKb, "index.html"), "utf8").includes("numerical-search-index.js"));
gate("understand-numerical-layer", graph.nodes.filter(x => x.id.startsWith("numeric:")).length === atoms.count && graph.layers.some(x => x.id === "layer:numerical"));

function route(query, profile = "design") {
  const env = { ...process.env, VGAME_KNOWLEDGE_OUTPUT: stageKb, PYTHONIOENCODING: "utf-8" };
  const run = cp.spawnSync("python", [path.join(repoRoot, "skills", "vgame-knowledge-router", "scripts", "route_query.py"), query, "--profile", profile, "--format", "json"], { encoding: "utf8", env });
  if (run.status !== 0) return { error: run.stderr || run.stdout };
  return JSON.parse(run.stdout);
}
const rvRoute = route("房车随机强化数值权重是多少");
const ewRoute = route("专武兼容迁移期数值规则");
const costRoute = route("角色升级成本数值怎么计算");
gate("route-rv-current", !rvRoute.error && rvRoute.numericAtoms.some(x => x.atomId === "NATOM-RULING-RV-C") && rvRoute.numericAtoms.every(x => x.sourceNature !== "SOURCE_EXPLICIT_SUPERSEDED"));
gate("route-ew-current", !ewRoute.error && ewRoute.numericAtoms.some(x => x.atomId === "NATOM-RULING-EW-B") && ewRoute.numericAtoms.every(x => x.sourceNature !== "SOURCE_EXPLICIT_SUPERSEDED"));
gate("route-numerical-general", !costRoute.error && costRoute.numericAtoms.length > 0 && costRoute.readPlan.some(x => x.ref === "ROUTER_OUTPUT.numericAtoms"));

const report = { schema: "vgame-numerical-gates/v2", generatedAt: new Date().toISOString(), passed: gates.every(x => x.pass), summary: { passed: gates.filter(x => x.pass).length, total: gates.length }, counts: { sources: source.count, workbooks: workbooks.count, atoms: atoms.count, activeAtoms: summary.activeAtoms, supersededAtoms: summary.supersededAtoms, historicalAtoms: summary.historicalAtoms, formulas: formulas.count, parameterSets: parameters.count }, gates };
fs.mkdirSync(path.join(stageRoot, "reports"), { recursive: true });
fs.writeFileSync(path.join(stageRoot, "reports", "numerical-v2-gates.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ passed: report.summary.passed, total: report.summary.total, counts: report.counts }));
if (!report.passed) {
  for (const item of gates.filter(x => !x.pass)) console.error(`[FAIL] ${item.name}: ${item.detail}`);
  process.exitCode = 1;
}
