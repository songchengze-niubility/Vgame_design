import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { isDeepStrictEqual } from "node:util";
import { fileURLToPath } from "node:url";
import { detailMarkdown, safeFileName, markdownRefFor } from "./render-markdown.mjs";

const root = path.dirname(fileURLToPath(import.meta.url));
function findRepositoryRoot(start) {
  if (process.env.VGAME_REPO_ROOT) return path.resolve(process.env.VGAME_REPO_ROOT);
  let cursor = path.resolve(start);
  while (true) {
    if (fs.existsSync(path.join(cursor, ".git")) && fs.existsSync(path.join(cursor, "knowledge-base", "AUTHORITY.json"))) return cursor;
    const parent = path.dirname(cursor);
    if (parent === cursor) return path.resolve(root, "../../..");
    cursor = parent;
  }
}
const repositoryRoot = findRepositoryRoot(root);
const model = JSON.parse(fs.readFileSync(path.join(root, "knowledge-model.json"), "utf8"));
const policy = JSON.parse(fs.readFileSync(path.join(root, "retrieval-policy.json"), "utf8"));
const contracts = JSON.parse(fs.readFileSync(path.join(root, "shared-contracts", "contract-registry.json"), "utf8"));
const router = JSON.parse(fs.readFileSync(path.join(root, "router-manifest.json"), "utf8"));
const workPackages = JSON.parse(fs.readFileSync(path.join(root, "work-packages.json"), "utf8"));
const authoringSourceMap = JSON.parse(fs.readFileSync(path.join(root, "authoring-source-map.json"), "utf8"));
const generatedCatalogText = fs.readFileSync(path.join(root, "knowledge-model.js"), "utf8");
const generatedSearchText = fs.readFileSync(path.join(root, "knowledge-search-index.js"), "utf8");
const contractById = Object.fromEntries(contracts.contracts.map(contract => [contract.id, contract]));
function generatedValue(text, marker) {
  const start = text.indexOf(marker);
  if (start < 0) throw new Error(`missing generated marker ${marker}`);
  const jsonStart = start + marker.length;
  return JSON.parse(text.slice(jsonStart, text.lastIndexOf(";")).trim());
}
const generatedCatalog = generatedValue(generatedCatalogText, "window.VGAME_KB = ");
const generatedSearch = generatedValue(generatedSearchText, "window.VGAME_KB_SEARCH = ");
const detailsDir = path.join(root, "system-details");
const detailFiles = fs.existsSync(detailsDir)
  ? fs.readdirSync(detailsDir).filter(file => file.endsWith(".json")).sort()
  : [];
const details = detailFiles.map(file => ({
  file,
  data: JSON.parse(fs.readFileSync(path.join(detailsDir, file), "utf8"))
}));
const moduleDetailsDir = path.join(root, "module-details");
const moduleDetailFiles = fs.existsSync(moduleDetailsDir)
  ? fs.readdirSync(moduleDetailsDir).filter(file => file.endsWith(".json")).sort()
  : [];
const moduleDetails = moduleDetailFiles.map(file => ({
  file,
  data: JSON.parse(fs.readFileSync(path.join(moduleDetailsDir, file), "utf8"))
}));
const moduleSectionIds = moduleDetails.flatMap(({ data }) => (data.sections || []).map(section => section.id));
const checks = [];

function check(name, condition, detail = "") {
  checks.push({ name, pass: Boolean(condition), detail });
}

const expectedModules = ["project", "system", "combat", "numeric", "relations"];
const moduleIds = model.modules.map(item => item.id);
const groupIds = new Set(model.systemGroups.map(item => item.id));
const entityIds = [
  ...model.projectPillars,
  ...model.systems,
  ...model.combat.rules,
  ...model.combat.character,
  ...model.numeric
].map(item => item.id);

check("schema", ["vgame-planning-knowledge/v0.4", "vgame-planning-knowledge/v1.0"].includes(model.meta.schema), model.meta.schema);
check("detail-schema", model.meta.detailSchema === "vgame-system-detail/v1", model.meta.detailSchema);
check("five-main-modules", JSON.stringify(moduleIds) === JSON.stringify(expectedModules), moduleIds.join(", "));
check("system-groups", model.systemGroups.length === 4, String(model.systemGroups.length));
check("all-systems-have-valid-group", model.systems.every(item => groupIds.has(item.group)));
check("system-count", model.systems.length === 45, String(model.systems.length));
check("battle-in-count", model.systems.filter(item => item.group === "system-in").length === 8);
check("outer-gameplay-count", model.systems.filter(item => item.group === "system-out-gameplay").length === 12);
check("outer-growth-count", model.systems.filter(item => item.group === "system-out-growth").length === 10);
check("outer-support-count", model.systems.filter(item => item.group === "system-out-support").length === 15);
check("combat-two-entries", model.combat.rules.length >= 8 && model.combat.character.length >= 7, `${model.combat.rules.length}/${model.combat.character.length}`);
check("numeric-v2-domains", ["NUM-01","NUM-02","NUM-03","NUM-04","NUM-05","NUM-06"].every(id => model.numeric.some(item => item.id === id)));
check("typed-relations", model.relationTypes.length === 12, String(model.relationTypes.length));
check("unique-entity-ids", new Set(entityIds).size === entityIds.length, `${new Set(entityIds).size}/${entityIds.length}`);
check("system-summaries", model.systems.every(item => item.name && item.summary && item.status && Array.isArray(item.relations)));

const systemIds = new Set(model.systems.map(item => item.id));
const detailIds = details.map(item => item.data.systemId);
const requiredDetailArrays = ["statusAxes", "rules", "flows", "conditions", "rewards", "exceptions", "ui", "configs", "relationships", "evidence", "openQuestions"];
const substantiveDetailArrays = ["statusAxes", "rules", "evidence"];
const applicableSectionKeys = ["flows", "conditions", "rewards", "exceptions", "ui", "configs"];
const detailAtoms = details.flatMap(({ data }) => [
  ...(data.rules || []),
  ...(data.flows || []),
  ...(data.flows || []).flatMap(flow => flow.steps || []),
  ...(data.conditions || []),
  ...(data.rewards || []),
  ...(data.exceptions || []),
  ...(data.ui || []),
  ...(data.configs || []),
  ...(data.relationships || []),
  ...(data.evidence || []),
  ...(data.openQuestions || [])
]);
const detailAtomIds = detailAtoms.map(item => item.id);
const ambiguousStatusValues = new Set(["CURRENT", "OBSERVED", "CONFIGURED", "SOURCE", "REQUIRED", "UNKNOWN", "CONFLICT"]);
const ambiguousDetailStatuses = details.flatMap(({ data }) => [
  ...(data.statusAxes || []),
  ...detailAtoms.filter(item => String(item.id || "").startsWith(`${data.systemId}-`))
].filter(item => ambiguousStatusValues.has(item.status)).map(item => `${item.id || item.axis}:${item.status}`));
const evidenceIds = new Set(details.flatMap(({ data }) => (data.evidence || []).map(item => item.id)));
const referencedEvidenceIds = details.flatMap(({ data }) => [
  ...(data.rules || []),
  ...(data.conditions || []),
  ...(data.rewards || []),
  ...(data.exceptions || []),
  ...(data.ui || []),
  ...(data.openQuestions || [])
].flatMap(item => item.evidenceRefs || []));
const relationTypeIds = new Set(model.relationTypes.map(item => item[0]));
const navigableIds = new Set(entityIds);

check("system-detail-files", details.length === model.systems.length, String(details.length));
check("system-detail-exact-coverage", new Set(detailIds).size === detailIds.length && detailIds.length === systemIds.size && detailIds.every(id => systemIds.has(id)) && [...systemIds].every(id => detailIds.includes(id)), `catalog=${systemIds.size} details=${detailIds.length}`);
check("system-detail-schema-and-level", details.every(({ data }) => data.schema === "vgame-system-detail/v1" && data.detailLevel === "full"), details.filter(({ data }) => data.schema !== "vgame-system-detail/v1" || data.detailLevel !== "full").map(({ data }) => data.systemId).join(", "));
check("system-detail-ids", details.every(({ file, data }) => data.systemId && systemIds.has(data.systemId) && file === `${data.systemId}.json`), detailIds.join(", "));
check("system-detail-unique", new Set(detailIds).size === detailIds.length, `${new Set(detailIds).size}/${detailIds.length}`);
check("system-detail-sections", details.every(({ data }) => data.overview && requiredDetailArrays.every(key => Array.isArray(data[key]))));
check("system-detail-substantive-sections", details.every(({ data }) => substantiveDetailArrays.every(key => data[key].length > 0)), substantiveDetailArrays.join(", "));
const applicabilityErrors = details.flatMap(({ data }) => {
  const questionIds = new Set((data.openQuestions || []).map(item => item.id));
  return applicableSectionKeys.flatMap(key => {
    const entry = data.sectionApplicability?.[key];
    if (!entry || !["APPLICABLE", "N/A", "GAP", "UNKNOWN"].includes(entry.state)) return [`${data.systemId}:${key}:missing-or-invalid-state`];
    if (entry.state === "APPLICABLE" && data[key].length === 0) return [`${data.systemId}:${key}:applicable-but-empty`];
    if (entry.state === "N/A" && (data[key].length > 0 || !entry.reason)) return [`${data.systemId}:${key}:invalid-na`];
    if (["GAP", "UNKNOWN"].includes(entry.state)) {
      if (!entry.reason || !Array.isArray(entry.questionRefs) || entry.questionRefs.length === 0 || entry.questionRefs.some(id => !questionIds.has(id))) {
        return [`${data.systemId}:${key}:untracked-${entry.state.toLowerCase()}`];
      }
    }
    return [];
  });
});
check("system-detail-section-applicability", applicabilityErrors.length === 0, applicabilityErrors.join(", "));
check("system-detail-source-snapshot", details.every(({ data }) => data.sourceSnapshot?.environment && data.sourceSnapshot?.checkedAt && data.sourceSnapshot?.liveMeaning && Array.isArray(data.statusGuide) && data.statusGuide.length >= 4));
check("system-detail-unambiguous-status", ambiguousDetailStatuses.length === 0, ambiguousDetailStatuses.join(", "));
check("system-detail-atom-ids", detailAtomIds.every(Boolean) && new Set(detailAtomIds).size === detailAtomIds.length, `${new Set(detailAtomIds).size}/${detailAtomIds.length}`);
check("system-detail-evidence-refs", referencedEvidenceIds.every(id => evidenceIds.has(id)), referencedEvidenceIds.filter(id => !evidenceIds.has(id)).join(", "));
const ruleFieldErrors = details.flatMap(({ data }) => (data.rules || []).flatMap(rule => {
  const errors = [];
  if (!rule.id) errors.push(`${rule.id || "MISSING"}:id`);
  if (!rule.name) errors.push(`${rule.id}:name`);
  if (!rule.status) errors.push(`${rule.id}:status`);
  if (!rule.targetRule || !String(rule.targetRule).trim()) errors.push(`${rule.id}:targetRule-empty`);
  if ("rule" in rule) errors.push(`${rule.id}:legacy-rule-field`);
  if (!rule.sourceFact || !String(rule.sourceFact).trim()) errors.push(`${rule.id}:sourceFact-empty`);
  if (!rule.acceptance || !String(rule.acceptance).trim()) errors.push(`${rule.id}:acceptance-empty`);
  return errors;
}));
check("system-detail-rule-required-fields", ruleFieldErrors.length === 0, ruleFieldErrors.join(", "));
check("system-detail-rule-links", details.every(({ data }) => data.rules.every(rule => (rule.relatedIds || []).every(id => navigableIds.has(id)))), details.flatMap(({ data }) => data.rules.flatMap(rule => (rule.relatedIds || []).filter(id => !navigableIds.has(id)))).join(", "));
check("system-detail-typed-relations", details.every(({ data }) => data.relationships.every(item => relationTypeIds.has(item.type) && ["incoming", "outgoing"].includes(item.direction) && navigableIds.has(item.targetId))));
const historicalNumericalRegistry = JSON.parse(fs.readFileSync(path.join(repositoryRoot, "knowledge-base", "numerical", "source-registry.json"), "utf8"));
const historicalNumericalPaths = historicalNumericalRegistry.files.map(item => item.relativePath);
const evidencePathExists = item => {
  const value = item.path;
  if (!value) return false;
  if (String(value).startsWith("vgame-numeric-source://框架v2/")) {
    if (item.historicalEvidenceOnly !== true || item.sourceRegistryRef !== "knowledge-base/numerical/source-registry.json") return false;
    const historicalPath = String(value).slice("vgame-numeric-source://框架v2/".length).replace(/\/+$/, "");
    return historicalNumericalPaths.some(sourcePath => sourcePath === historicalPath || sourcePath.startsWith(`${historicalPath}/`));
  }
  if (fs.existsSync(value)) return true;
  const candidate = path.resolve(repositoryRoot, ...String(value).replace(/\\/g, "/").split("/"));
  return fs.existsSync(candidate);
};
const missingEvidencePaths = details.flatMap(({ data }) => data.evidence.filter(item => !evidencePathExists(item)).map(item => item.path));
check("system-detail-evidence-paths", missingEvidencePaths.length === 0, missingEvidencePaths.join(", "));
const missingDetailMarkdown = details.filter(({ data }) => !fs.existsSync(path.join(root, "systems", `${data.systemId}-${data.name.replace(/[\\/:*?"<>|]/g, "-")}.md`))).map(({ data }) => data.systemId);
check("system-detail-markdown", missingDetailMarkdown.length === 0, missingDetailMarkdown.join(", "));
const contractIds = new Set(contracts.contracts.map(item => item.id));
const contractRefs = details.flatMap(({ data }) => data.contractRefs || []);
// 2026-08-19 加固：contractRefs 顶层字段必填（数组可为空但必须显式存在）；ruleRefs 必须指向本系统命名空间内的原子，禁止跨正文凑数。
const contractRefsFieldErrors = details
  .filter(({ data }) => !Array.isArray(data.contractRefs))
  .map(({ data }) => `${data.systemId}:missing-top-level-contractRefs`);
check("system-detail-contract-refs-field", contractRefsFieldErrors.length === 0, contractRefsFieldErrors.join(", "));
const contractRefsNamespaceErrors = details.flatMap(({ data }) =>
  (data.contractRefs || []).flatMap(ref =>
    (ref.ruleRefs || [])
      .filter(id => !id.startsWith(`${data.systemId}-`))
      .map(id => `${data.systemId}:foreign-ruleRef(${ref.id}:${id})`)
  )
);
check("system-detail-contract-refs-namespace", contractRefsNamespaceErrors.length === 0, contractRefsNamespaceErrors.join(", "));
check("shared-contract-registry", contracts.schema === "vgame-shared-contract-registry/v1" && contractIds.size >= 7, String(contractIds.size));
check("system-detail-contract-refs", contractRefs.every(ref => contractIds.has(ref.id) && (ref.ruleRefs || []).every(id => detailAtomIds.includes(id))), contractRefs.filter(ref => !contractIds.has(ref.id) || (ref.ruleRefs || []).some(id => !detailAtomIds.includes(id))).map(ref => ref.id).join(", "));
check("retrieval-policy", policy.schema === "vgame-knowledge-retrieval-policy/v1" && policy.promptlessRouting === true && ["quick","design","audit"].every(id => policy.depthProfiles?.[id]), policy.schema);
check("router-manifest", router.schema === "vgame-knowledge-router-manifest/v1" && router.version === model.meta.version && router.systems.length === model.systems.length, `${router.version}/${router.systems.length}`);
check("router-detail-refs", router.systems.every(item => !item.detailRef || fs.existsSync(path.join(root, item.detailRef))), router.systems.filter(item => item.detailRef && !fs.existsSync(path.join(root, item.detailRef))).map(item => item.id).join(", "));
check("lightweight-catalog", !generatedCatalog.systemDetails && Object.keys(generatedCatalog.detailRegistry || {}).length === details.length && Buffer.byteLength(generatedCatalogText, "utf8") < 100000, `${Buffer.byteLength(generatedCatalogText, "utf8")} bytes`);
check("lightweight-search-index", generatedSearch.length === detailAtomIds.length + moduleSectionIds.length && generatedSearch.every(item => item.id && item.parentId && item.targetType), String(generatedSearch.length));
const missingChunks = details.filter(({ data }) => !fs.existsSync(path.join(root, "system-chunks", `${data.systemId}.js`))).map(({ data }) => data.systemId);
check("lazy-detail-chunks", missingChunks.length === 0, missingChunks.join(", "));

const localToday = (() => {
  const now = new Date();
  const pad = value => String(value).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
})();
const isoDatePattern = /\d{4}-\d{2}-\d{2}/;
const futureDateErrors = [];
function rejectFutureDate(label, value) {
  const match = String(value || "").match(isoDatePattern);
  if (match && match[0] > localToday) futureDateErrors.push(`${label}:${match[0]}`);
}
rejectFutureDate("knowledge-model.meta.updatedAt", model.meta.updatedAt);
rejectFutureDate("work-packages.updatedAt", workPackages.updatedAt);
for (const { data } of details) {
  rejectFutureDate(`${data.systemId}.updatedAt`, data.updatedAt);
  rejectFutureDate(`${data.systemId}.revision`, data.revision);
  rejectFutureDate(`${data.systemId}.sourceSnapshot.checkedAt`, data.sourceSnapshot?.checkedAt);
}
check("knowledge-dates-not-future", futureDateErrors.length === 0, `${futureDateErrors.join(", ")} > today ${localToday}`);

const relationshipEvidenceErrors = details.flatMap(({ data }) => {
  const localEvidence = new Set((data.evidence || []).map(item => item.id));
  return (data.relationships || []).flatMap(item => {
    const refs = item.evidenceRefs || [];
    // evidenceRefs 一旦提供，必须逐个解析到本正文证据；provenance 只能作为补充说明，不得让非法引用绕过（2026-08-19 加固）。
    const invalidRefs = refs.filter(id => !localEvidence.has(id));
    const noEvidenceAtAll = refs.length === 0 && !["CROSS_SOURCE_SYNTHESIS", "UNKNOWN"].includes(item.provenance);
    const errors = [];
    if (invalidRefs.length) errors.push(`${item.id}:foreign-evidenceRef(${invalidRefs.join(",")})`);
    if (noEvidenceAtAll) errors.push(`${item.id}:no-evidence-or-provenance`);
    return errors;
  });
});
check("system-detail-relationship-evidence", relationshipEvidenceErrors.length === 0, relationshipEvidenceErrors.join(", "));

const validProvenanceValues = new Set(["SOURCE_EXPLICIT", "WORKING_COPY_OBSERVED", "CROSS_SOURCE_SYNTHESIS", "DESIGN_PROPOSAL", "UNKNOWN"]);
const relationshipProvenanceErrors = details.flatMap(({ data }) =>
  (data.relationships || [])
    .filter(item => !item.provenance || !validProvenanceValues.has(item.provenance))
    .map(item => `${item.id}:${item.provenance ? `invalid-provenance(${item.provenance})` : "missing-provenance"}`)
);
check("system-detail-relationship-provenance-valid", relationshipProvenanceErrors.length === 0, relationshipProvenanceErrors.join(", "));

// provenance 必须与本地 evidence kind 一致，不得只要枚举非空就通过。
const provenanceDesignKinds = new Set(["design-target", "design-index", "numeric-deposit", "decision-record", "user-supplied-image"]);
const provenanceWorkingKinds = new Set(["source-code", "source-excel", "numeric-source-excel", "generated-config", "runtime-observation", "working-copy-config-and-export"]);
const provenanceCompatibilityErrors = details.flatMap(({ data }) => {
  const evidenceById = new Map((data.evidence || []).map(ev => [ev.id, ev]));
  return (data.relationships || []).flatMap(rel => {
    const refs = (rel.evidenceRefs || []).map(id => evidenceById.get(id)).filter(Boolean);
    const kinds = refs.map(ev => ev.kind);
    const hasDesign = kinds.some(kind => provenanceDesignKinds.has(kind));
    const hasWorking = kinds.some(kind => provenanceWorkingKinds.has(kind));
    const hasReverse = kinds.includes("reverse-design");
    const hasIndirect = kinds.some(kind => ["knowledge-ref", "knowledge-model", "delivery-mirror"].includes(kind));
    const errors = [];
    if (rel.provenance === "SOURCE_EXPLICIT" && (!refs.length || !hasDesign || hasWorking || hasReverse || hasIndirect)) errors.push(`${rel.id}:source-explicit-kind-mismatch(${kinds.join("+")})`);
    if (rel.provenance === "WORKING_COPY_OBSERVED" && (!refs.length || !hasWorking || hasDesign || hasReverse || hasIndirect)) errors.push(`${rel.id}:working-copy-kind-mismatch(${kinds.join("+")})`);
    if (rel.provenance === "DESIGN_PROPOSAL" && (!refs.length || !hasReverse || hasWorking || hasDesign || hasIndirect)) errors.push(`${rel.id}:design-proposal-kind-mismatch(${kinds.join("+")})`);
    if (rel.provenance === "CROSS_SOURCE_SYNTHESIS" && !(hasIndirect || [hasDesign, hasWorking, hasReverse].filter(Boolean).length >= 2)) errors.push(`${rel.id}:cross-source-without-mixed-or-indirect-evidence(${kinds.join("+")})`);
    if (rel.provenance === "UNKNOWN" && refs.length) errors.push(`${rel.id}:unknown-with-resolvable-evidence(${kinds.join("+")})`);
    return errors;
  });
});
check("system-detail-relationship-provenance-compatible", provenanceCompatibilityErrors.length === 0, provenanceCompatibilityErrors.join(", "));

// CROSS_SOURCE_SYNTHESIS 关系必须说明推导边界（来源→推导→边界→UNKNOWN），不得伪装成原文直接结论。
const synthesisBoundaryErrors = details.flatMap(({ data }) =>
  (data.relationships || [])
    .filter(item => item.provenance === "CROSS_SOURCE_SYNTHESIS")
    .filter(item => !/推导|边界|来源/.test(item.description || ""))
    .map(item => `${item.id}:missing-synthesis-boundary`)
);
check("system-detail-synthesis-boundary", synthesisBoundaryErrors.length === 0, synthesisBoundaryErrors.join(", "));

const openQuestionFieldErrors = details.flatMap(({ data }) =>
  (data.openQuestions || []).flatMap(q => {
    const errors = [];
    if (!q.id) errors.push(`${q.id || "MISSING"}:id`);
    if (!q.priority || !["P0", "P1", "P2"].includes(q.priority)) errors.push(`${q.id}:priority`);
    if (!q.question || !String(q.question).trim()) errors.push(`${q.id}:question-empty`);
    if (!q.impact || !String(q.impact).trim()) errors.push(`${q.id}:impact-empty`);
    return errors;
  })
);
check("system-detail-open-questions-fields", openQuestionFieldErrors.length === 0, openQuestionFieldErrors.join(", "));

const questionLifecycleErrors = details.flatMap(({ data }) => {
  const evidenceIds = new Set((data.evidence || []).map(ev => ev.id));
  return (data.openQuestions || []).flatMap(q => {
    const errors = [];
    if (!["OPEN", "ANSWERED", "CLOSED"].includes(q.lifecycle)) errors.push(`${q.id}:invalid-lifecycle(${q.lifecycle || "missing"})`);
    if (q.lifecycle === "OPEN" && (q.answer || q.resolvedBy || q.resolvedAt || q.closureEvidenceRefs?.length)) errors.push(`${q.id}:open-has-resolution-fields`);
    if (["ANSWERED", "CLOSED"].includes(q.lifecycle) && (!q.answer || !q.resolvedBy || !q.resolvedAt)) errors.push(`${q.id}:answered-missing-answer-metadata`);
    if (q.lifecycle === "CLOSED") {
      if (!Array.isArray(q.closureEvidenceRefs) || !q.closureEvidenceRefs.length) errors.push(`${q.id}:closed-without-evidence`);
      for (const ref of q.closureEvidenceRefs || []) if (!evidenceIds.has(ref)) errors.push(`${q.id}:unresolvable-closure-evidence(${ref})`);
    }
    if (q.resolutionOwner === "AI_EVIDENCE" && q.lifecycle !== "CLOSED") errors.push(`${q.id}:ai-evidence-not-closed`);
    if (q.priority === "P0" && q.resolutionOwner === "DEFERRED_DETAIL") errors.push(`${q.id}:p0-deferred-detail`);
    return errors;
  });
});
check("question-lifecycle-and-closure", questionLifecycleErrors.length === 0, questionLifecycleErrors.join(", "));

const evidenceFieldErrors = details.flatMap(({ data }) =>
  (data.evidence || []).flatMap(ev => {
    const errors = [];
    if (!ev.id) errors.push(`${ev.id || "MISSING"}:id`);
    if (!ev.kind) errors.push(`${ev.id}:kind`);
    if (!ev.label) errors.push(`${ev.id}:label`);
    if (!ev.path) errors.push(`${ev.id}:path`);
    if (!ev.status) errors.push(`${ev.id}:status`);
    return errors;
  })
);
check("system-detail-evidence-fields", evidenceFieldErrors.length === 0, evidenceFieldErrors.join(", "));

const markdownRefErrors = details.flatMap(({ data }) => {
  const expectedRef = `systems/${data.systemId}-${safeFileName(data.name)}.md`;
  const errors = [];
  if (!fs.existsSync(path.join(root, expectedRef))) errors.push(`${data.systemId}:file-missing(${expectedRef})`);
  const routerEntry = router.systems.find(item => item.id === data.systemId);
  if (!routerEntry || routerEntry.markdownRef !== expectedRef) errors.push(`${data.systemId}:router-markdownRef-mismatch`);
  const registryEntry = generatedCatalog.detailRegistry?.[data.systemId];
  if (!registryEntry || registryEntry.markdownRef !== expectedRef) errors.push(`${data.systemId}:catalog-markdownRef-mismatch`);
  return errors;
});
check("markdown-refs-exist-and-consistent", markdownRefErrors.length === 0, markdownRefErrors.join(", "));

const chunkMismatch = details.flatMap(({ data }) => {
  const chunkPath = path.join(root, "system-chunks", `${data.systemId}.js`);
  if (!fs.existsSync(chunkPath)) return [`${data.systemId}:missing`];
  const text = fs.readFileSync(chunkPath, "utf8");
  const marker = `window.VGAME_SYSTEM_DETAILS[${JSON.stringify(data.systemId)}] = `;
  const start = text.indexOf(marker);
  if (start < 0) return [`${data.systemId}:marker-missing`];
  try {
    const parsed = JSON.parse(text.slice(start + marker.length, text.lastIndexOf(";")).trim());
    return isDeepStrictEqual(parsed, data) ? [] : [`${data.systemId}:content-drift`];
  } catch (error) {
    return [`${data.systemId}:parse-error`];
  }
});
check("generated-chunks-match-canonical", chunkMismatch.length === 0, chunkMismatch.join(", "));

const expectedAtomCount = detail => {
  const atomKeysForCount = ["rules", "conditions", "rewards", "exceptions", "ui", "configs", "relationships", "evidence", "openQuestions"];
  return atomKeysForCount.reduce((sum, key) => sum + (detail[key] || []).length, 0) + (detail.flows || []).reduce((sum, flow) => sum + 1 + (flow.steps || []).length, 0);
};
const routerConsistencyErrors = details.flatMap(({ data }) => {
  const entry = router.systems.find(item => item.id === data.systemId);
  if (!entry) return [`${data.systemId}:not-in-router`];
  const errors = [];
  if (entry.revision !== data.revision) errors.push(`${data.systemId}:revision`);
  if (entry.detailLevel !== data.detailLevel) errors.push(`${data.systemId}:detailLevel`);
  if (entry.detailRef !== `system-details/${data.systemId}.json`) errors.push(`${data.systemId}:detailRef`);
  if (entry.chunkRef !== `system-chunks/${data.systemId}.js`) errors.push(`${data.systemId}:chunkRef`);
  if (entry.detailLevel === "full" && entry.markdownRef !== `systems/${data.systemId}-${safeFileName(data.name)}.md`) errors.push(`${data.systemId}:markdownRef`);
  if (JSON.stringify(entry.contractRefs) !== JSON.stringify((data.contractRefs || []).map(item => item.id))) errors.push(`${data.systemId}:contractRefs`);
  if (JSON.stringify(entry.relatedIds) !== JSON.stringify([...new Set((data.relationships || []).map(item => item.targetId))])) errors.push(`${data.systemId}:relatedIds`);
  if (entry.evidenceCount !== (data.evidence || []).length) errors.push(`${data.systemId}:evidenceCount`);
  return errors;
});
check("router-manifest-consistent-with-canonical", routerConsistencyErrors.length === 0, routerConsistencyErrors.join(", "));

const catalogRegistryErrors = details.flatMap(({ data }) => {
  const entry = generatedCatalog.detailRegistry?.[data.systemId];
  if (!entry) return [`${data.systemId}:missing`];
  const errors = [];
  if (entry.name !== data.name) errors.push(`${data.systemId}:name`);
  if (entry.revision !== data.revision) errors.push(`${data.systemId}:revision`);
  if (entry.updatedAt !== data.updatedAt) errors.push(`${data.systemId}:updatedAt`);
  if (entry.detailLevel !== data.detailLevel) errors.push(`${data.systemId}:detailLevel`);
  if (entry.atomCount !== expectedAtomCount(data)) errors.push(`${data.systemId}:atomCount`);
  if (entry.evidenceCount !== (data.evidence || []).length) errors.push(`${data.systemId}:evidenceCount`);
  if (JSON.stringify(entry.contractRefs) !== JSON.stringify((data.contractRefs || []).map(item => item.id))) errors.push(`${data.systemId}:contractRefs`);
  return errors;
});
check("generated-catalog-registry-consistent", catalogRegistryErrors.length === 0, catalogRegistryErrors.join(", "));

const canonicalAtomIdSet = new Set(detailAtomIds);
const expectedSearchIds = new Set([...canonicalAtomIdSet, ...moduleSectionIds]);
const searchIndexIdErrors = [
  ...[...new Set(generatedSearch.map(item => item.id))].filter(id => !expectedSearchIds.has(id)).map(id => `unexpected:${id}`),
  ...[...expectedSearchIds].filter(id => !generatedSearch.some(item => item.id === id)).map(id => `missing:${id}`)
];
check("generated-search-index-consistent", searchIndexIdErrors.length === 0 && generatedSearch.length === detailAtomIds.length + moduleSectionIds.length, searchIndexIdErrors.slice(0, 10).join(", "));

const markdownHeaderErrors = details.flatMap(({ data }) => {
  const mdPath = path.join(root, "systems", `${data.systemId}-${safeFileName(data.name)}.md`);
  if (!fs.existsSync(mdPath)) return [`${data.systemId}:missing`];
  const text = fs.readFileSync(mdPath, "utf8");
  const errors = [];
  if (!text.startsWith(`# ${data.systemId} ${data.name}\n`)) errors.push(`${data.systemId}:header`);
  if (!text.includes(`- 详情版本：${data.revision}`)) errors.push(`${data.systemId}:revision-line`);
  if (!text.includes(`- 更新时间：${data.updatedAt}`)) errors.push(`${data.systemId}:updatedAt-line`);
  return errors;
});
check("generated-markdown-matches-canonical", markdownHeaderErrors.length === 0, markdownHeaderErrors.join(", "));

// 2026-08-19 加固：Markdown 与 canonical 全文深度一致（按共享渲染器重渲染逐字节对比，拦截任何内容漂移）。
const markdownDeepErrors = details.flatMap(({ data }) => {
  const mdPath = path.join(root, markdownRefFor(data));
  if (!fs.existsSync(mdPath)) return [`${data.systemId}:missing`];
  const expected = detailMarkdown(data, contractById);
  const actual = fs.readFileSync(mdPath, "utf8");
  return actual === expected ? [] : [`${data.systemId}:content-drift`];
});
check("generated-markdown-deep-equal", markdownDeepErrors.length === 0, markdownDeepErrors.join(", "));

const expectedBuildHash = crypto
  .createHash("sha256")
  .update(JSON.stringify(details.map(d => d.data.systemId).sort()))
  .update(JSON.stringify(details.map(d => [d.data.systemId, d.data.revision, d.data.updatedAt, d.data.detailLevel])))
  .update(JSON.stringify(generatedSearch.map(e => [e.id, e.parentId, e.targetType, e.name, e.summary, e.status])))
  .update(JSON.stringify(moduleDetails.map(d => [d.data.moduleId, d.data.revision, d.data.updatedAt, d.data.detailLevel])))
  .digest("hex")
  .substring(0, 16);
check("deterministic-build-hash", router.buildHash === expectedBuildHash, `expected=${expectedBuildHash} actual=${router.buildHash || "missing"}`);

// 2026-08-19：wave gate 覆盖 M01/M02（专业模块不得停留在 planned/未接入）。
const incompleteWavePackages = workPackages.packages
  .filter(item => (/^W\d+-/.test(item.id) || /^M0[12]$/.test(item.id)) && item.status !== "complete")
  .map(item => `${item.id}:${item.status}`);
check("work-package-waves-complete", incompleteWavePackages.length === 0, incompleteWavePackages.join(", "));
const mainline = details.find(({ data }) => data.systemId === "SYS-OUT-GP-01")?.data;
check("mainline-full-detail", Boolean(mainline && mainline.detailLevel === "full" && mainline.rules.length >= 10 && mainline.openQuestions.length >= 5), mainline ? `${mainline.rules.length}/${mainline.openQuestions.length}` : "missing");
const currentGameplayPath = path.resolve(repositoryRoot, "skills/vgame-core-understanding/references/current-gameplay.md");
const currentGameplay = fs.existsSync(currentGameplayPath) ? fs.readFileSync(currentGameplayPath, "utf8") : "";
check("project-entry-unlocks-synced", ["主线2-4", "主线2-7", "主线2-10", "主线3-15"].every(value => currentGameplay.includes(value)) && !currentGameplay.includes("unlock: `主线1-6`") && !currentGameplay.includes("unlock: `主线2-15`"));
const repoRoot = repositoryRoot;
const routerSkillPath = path.join(repoRoot, "skills", "vgame-knowledge-router", "SKILL.md");
const routerScriptPath = path.join(repoRoot, "skills", "vgame-knowledge-router", "scripts", "route_query.py");
const promptPatternsPath = path.join(repoRoot, "skills", "vgame-knowledge-router", "references", "prompt-patterns.md");
check("knowledge-router-skill", [routerSkillPath, routerScriptPath, promptPatternsPath].every(file => fs.existsSync(file)));
const projectEntryFiles = [
  path.join(repoRoot, "AGENTS.md"),
  path.join(repoRoot, "skills", "config.toml"),
  path.join(repoRoot, "skills", "README.md"),
  path.join(repoRoot, "skills", "vgame-core-understanding", "SKILL.md"),
  path.join(repoRoot, "skills", "agents", "vgame-design-lead.toml")
];
check("knowledge-router-project-wiring", projectEntryFiles.every(file => fs.existsSync(file) && fs.readFileSync(file, "utf8").includes("vgame-knowledge-router")), projectEntryFiles.filter(file => !fs.existsSync(file) || !fs.readFileSync(file, "utf8").includes("vgame-knowledge-router")).map(file => path.basename(file)).join(", "));

const packageIds = workPackages.packages.map(item => item.id);
const queuedPackageSystems = workPackages.packages
  .filter(item => /^W\d+-/.test(item.id))
  .flatMap(item => item.systemIds || []);
const expectedQueuedSystems = model.systems.map(item => item.id).filter(id => id !== "SYS-OUT-GP-01");
const queuedSet = new Set(queuedPackageSystems);
check("work-package-schema", workPackages.schema === "vgame-knowledge-work-packages/v1" && workPackages.coordination?.maxConcurrentAuthors === 3, workPackages.schema);
check("work-package-unique-ids", new Set(packageIds).size === packageIds.length, `${new Set(packageIds).size}/${packageIds.length}`);
check("work-package-exact-system-coverage", queuedPackageSystems.length === expectedQueuedSystems.length && queuedSet.size === expectedQueuedSystems.length && expectedQueuedSystems.every(id => queuedSet.has(id)), `${queuedPackageSystems.length}/${queuedSet.size}/${expectedQueuedSystems.length}`);
check("work-package-valid-system-ids", queuedPackageSystems.every(id => systemIds.has(id) && id !== "SYS-OUT-GP-01"), queuedPackageSystems.filter(id => !systemIds.has(id) || id === "SYS-OUT-GP-01").join(", "));
const packageBySystem = new Map(workPackages.packages.flatMap(item => (item.systemIds || []).map(systemId => [systemId, item.id])));
const sourceMapSystems = authoringSourceMap.systems || [];
const sourceMapIds = sourceMapSystems.map(item => item.systemId);
const missingAuthoringPaths = sourceMapSystems.flatMap(item => [...(item.seedDesignDocs || []), ...(item.seedKnowledgeRefs || [])]
  .filter(file => !fs.existsSync(path.resolve(repoRoot, file)))
  .map(file => `${item.systemId}:${file}`));
const missingAuthoringSkills = sourceMapSystems.flatMap(item => (item.recommendedSkills || [])
  .filter(skill => !fs.existsSync(path.join(repoRoot, "skills", skill, "SKILL.md")))
  .map(skill => `${item.systemId}:${skill}`));
check("authoring-source-map-schema", authoringSourceMap.schema === "vgame-knowledge-authoring-source-map/v1", authoringSourceMap.schema);
check("authoring-source-map-coverage", sourceMapIds.length === expectedQueuedSystems.length && new Set(sourceMapIds).size === expectedQueuedSystems.length && expectedQueuedSystems.every(id => sourceMapIds.includes(id)), `${sourceMapIds.length}/${new Set(sourceMapIds).size}/${expectedQueuedSystems.length}`);
check("authoring-source-map-fields", sourceMapSystems.every(item => item.packageId === packageBySystem.get(item.systemId) && Array.isArray(item.recommendedSkills) && item.recommendedSkills.length > 0 && Array.isArray(item.seedDesignDocs) && Array.isArray(item.seedKnowledgeRefs) && item.seedKnowledgeRefs.length > 0 && Array.isArray(item.configAreas) && Array.isArray(item.codeAreas) && Array.isArray(item.risks) && ["DIRECT", "PARTIAL", "GAP", "CONFLICT"].includes(item.sourceStatus)));
check("authoring-source-map-paths", missingAuthoringPaths.length === 0, missingAuthoringPaths.join(", "));
check("authoring-source-map-skills", missingAuthoringSkills.length === 0, missingAuthoringSkills.join(", "));

const sourceFiles = new Set([
  ...model.modules.map(item => item.source),
  ...model.systemGroups.map(item => item.source),
  "README.md",
  "90-状态与证据.md",
  "index.html",
  "knowledge-model.js",
  "knowledge-search-index.js",
  "router-manifest.json",
  "retrieval-policy.json",
  "shared-contracts/contract-registry.json",
  "work-packages.json",
  "authoring-source-map.json",
  "SYSTEM-DETAIL-SPEC.md",
  "render-markdown.mjs",
  "module-details/M01.json",
  "module-details/M02.json",
  "M01-战斗专业正文.md",
  "M02-数值框架v2专业正文.md",
  "../HANDOFF.md",
  "../待裁决清单.md",
  "../06-review.md",
  "../最终返工完成报告.md",
  "../00-workflow-state.json"
]);
const missingSources = [...sourceFiles].filter(file => !fs.existsSync(path.join(root, file)));
check("local-source-files", missingSources.length === 0, missingSources.join(", "));

// ===== 2026-08-19 加固：专业模块（M01/M02）canonical 接入 =====
const moduleFileIds = moduleDetails.map(({ data }) => data.moduleId).sort();
const moduleExpectedIds = ["M01", "M02"];
const moduleSchemaErrors = moduleDetails.flatMap(({ file, data }) => {
  const errors = [];
  if (data.schema !== "vgame-module-detail/v1") errors.push(`${file}:schema(${data.schema})`);
  if (!data.moduleId || !data.name || !data.revision || !data.updatedAt || data.detailLevel !== "full") errors.push(`${file}:required-fields`);
  if (!data.sourceDoc || !fs.existsSync(path.join(root, data.sourceDoc))) errors.push(`${file}:sourceDoc-missing`);
  return errors;
});
check("module-details-schema", JSON.stringify(moduleFileIds) === JSON.stringify(moduleExpectedIds) && moduleSchemaErrors.length === 0, [...moduleFileIds, ...moduleSchemaErrors].join(", "));
const moduleAnchorErrors = moduleDetails.flatMap(({ data }) => {
  const md = fs.readFileSync(path.join(root, data.sourceDoc), "utf8");
  return (data.sections || []).filter(section => !md.includes(section.anchor)).map(section => `${data.moduleId}:${section.id}:anchor-missing`);
});
const moduleSectionIdErrors = moduleDetails.filter(({ data }) => {
  const ids = (data.sections || []).map(section => section.id);
  return ids.length === 0 || new Set(ids).size !== ids.length || !ids.every(id => id.startsWith(`${data.moduleId}-`));
}).map(({ data }) => `${data.moduleId}:section-ids`);
check("module-details-sections", moduleAnchorErrors.length === 0 && moduleSectionIdErrors.length === 0, [...moduleAnchorErrors, ...moduleSectionIdErrors].join(", "));
const numericIds = new Set(model.numeric.map(item => item.id));
const combatRuleIds = new Set(model.combat.rules.map(item => item.id));
const characterRuleIds = new Set(model.combat.character.map(item => item.id));
const moduleCrossRefErrors = moduleDetails.flatMap(({ data }) =>
  (data.crossRefs || []).flatMap(ref => {
    const errors = [];
    const pool = ref.targetType === "combat-rule" ? combatRuleIds
      : ref.targetType === "character-rule" ? characterRuleIds
      : ref.targetType === "system" ? systemIds
      : ref.targetType === "contract" ? contractIds
      : ref.targetType === "numeric" ? numericIds : null;
    if (!pool) errors.push(`${data.moduleId}:unknown-targetType(${ref.targetType})`);
    else if (!pool.has(ref.targetId)) errors.push(`${data.moduleId}:unresolved(${ref.targetType}:${ref.targetId})`);
    for (const sid of ref.systemIds || []) if (!systemIds.has(sid)) errors.push(`${data.moduleId}:unresolved-systemId(${sid})`);
    return errors;
  })
);
check("module-details-cross-refs", moduleCrossRefErrors.length === 0, moduleCrossRefErrors.join(", "));
const questionIdPool = new Set(details.flatMap(({ data }) => (data.openQuestions || []).map(q => q.id)));
const moduleConflictRefErrors = moduleDetails.flatMap(({ data }) =>
  (data.aggregatedConflicts || []).flatMap(conflict =>
    (conflict.externalQuestionRefs || []).filter(id => !questionIdPool.has(id)).map(id => `${data.moduleId}:${conflict.id}:unresolved-question(${id})`)
  )
);
check("module-details-conflict-refs", moduleConflictRefErrors.length === 0, moduleConflictRefErrors.join(", "));
const moduleChunkErrors = moduleDetails.flatMap(({ data }) => {
  const chunkPath = path.join(root, "module-chunks", `${data.moduleId}.js`);
  if (!fs.existsSync(chunkPath)) return [`${data.moduleId}:chunk-missing`];
  const text = fs.readFileSync(chunkPath, "utf8");
  const marker = `window.VGAME_MODULE_DETAILS[${JSON.stringify(data.moduleId)}] = `;
  const start = text.indexOf(marker);
  if (start < 0) return [`${data.moduleId}:marker-missing`];
  try {
    const parsed = JSON.parse(text.slice(start + marker.length, text.lastIndexOf(";")).trim());
    // 构建阶段会向 chunk 的 sections 注入 sectionContent（编译进 JS，使 file:// 离线可用），
    // canonical JSON 不含此字段；比较时移除 sectionContent 再做 deep-equal。
    const stripContent = obj => {
      const clone = structuredClone(obj);
      if (clone.sections) clone.sections = clone.sections.map(s => { const { sectionContent, ...rest } = s; return rest; });
      return clone;
    };
    return isDeepStrictEqual(stripContent(parsed), data) ? [] : [`${data.moduleId}:content-drift`];
  } catch {
    return [`${data.moduleId}:parse-error`];
  }
});
check("module-chunks-match-canonical", moduleChunkErrors.length === 0, moduleChunkErrors.join(", "));
const routerModuleErrors = moduleDetails.flatMap(({ data }) => {
  const entry = (router.specialistModules || []).find(item => item.id === data.moduleId);
  if (!entry) return [`${data.moduleId}:not-in-router`];
  const errors = [];
  if (entry.name !== data.name) errors.push(`${data.moduleId}:name`);
  if (entry.revision !== data.revision) errors.push(`${data.moduleId}:revision`);
  if (entry.detailRef !== `module-details/${data.moduleId}.json`) errors.push(`${data.moduleId}:detailRef`);
  if (entry.chunkRef !== `module-chunks/${data.moduleId}.js`) errors.push(`${data.moduleId}:chunkRef`);
  if (JSON.stringify(entry.sectionIds) !== JSON.stringify((data.sections || []).map(section => section.id))) errors.push(`${data.moduleId}:sectionIds`);
  if (entry.crossRefCount !== (data.crossRefs || []).length) errors.push(`${data.moduleId}:crossRefCount`);
  return errors;
});
check("router-manifest-modules-consistent", routerModuleErrors.length === 0, routerModuleErrors.join(", "));

// ===== 2026-08-19 加固：workflow 时间线（无未来/乱序事件） =====
const workflowPath = path.join(root, "..", "00-workflow-state.json");
const workflow = JSON.parse(fs.readFileSync(workflowPath, "utf8"));
const workflowTimeErrors = [];
{
  const nowMs = Date.now() + 5 * 60 * 1000; // 5 分钟时钟容差
  let prev = 0;
  for (const event of workflow.history || []) {
    const at = Date.parse(event.at);
    if (Number.isNaN(at)) workflowTimeErrors.push(`invalid-time(${event.at})`);
    else {
      if (at < prev) workflowTimeErrors.push(`out-of-order(${event.at})`);
      if (at > nowMs) workflowTimeErrors.push(`future(${event.at})`);
      prev = at;
    }
  }
  const maxAt = Math.max(...(workflow.history || []).map(event => Date.parse(event.at)));
  if (Date.parse(workflow.updated_at || "1970-01-01") < maxAt) workflowTimeErrors.push(`updated_at(${workflow.updated_at}) < max-history`);
  if (workflow.human_gates && (workflow.human_gates.review_approved !== false || workflow.human_gates.delivery_accepted !== false)) {
    workflowTimeErrors.push("human-gates-must-stay-false-before-human-review");
  }
  const lastHistory = (workflow.history || []).at(-1);
  if (workflow.current_phase !== "review") workflowTimeErrors.push(`current-phase-must-be-review(${workflow.current_phase})`);
  if (!lastHistory || lastHistory.outcome !== workflow.last_outcome) workflowTimeErrors.push(`last-outcome-mismatch(state=${workflow.last_outcome},history=${lastHistory?.outcome})`);
  if (!["needs_revision", "waiting_human"].includes(workflow.last_outcome)) workflowTimeErrors.push(`invalid-review-outcome(${workflow.last_outcome})`);
}
check("workflow-timeline-consistent", workflowTimeErrors.length === 0, workflowTimeErrors.join(", "));

// ===== 2026-08-19 加固：交接统计与 canonical 一致（禁止旧口径残留） =====
const questionStats = { P0: 0, P1: 0, P2: 0 };
const questionLifecycleStats = { OPEN: 0, ANSWERED: 0, CLOSED: 0 };
const questionOwnerStats = { AI_EVIDENCE: 0, HUMAN_DECISION: 0, RUNTIME_OWNER: 0, DEFERRED_DETAIL: 0 };
let questionTotal = 0;
for (const { data } of details) for (const q of data.openQuestions || []) {
  questionStats[q.priority] += 1;
  questionLifecycleStats[q.lifecycle] += 1;
  questionOwnerStats[q.resolutionOwner] += 1;
  questionTotal += 1;
}
const statsSummary = `${questionStats.P0} P0 / ${questionStats.P1} P1 / ${questionStats.P2} P2`;
const statsDocFiles = ["../HANDOFF.md", "../待裁决清单.md", "../06-review.md", "../最终返工完成报告.md"];
const staleStatTokens = ["共 224", "224 问", "224 个 openQuestions", "33 P0 / 122 P1 / 69 P2", "122 P1 / 69 P2", "2582 个详情原子", "2619 atoms", "237 个 openQuestions", "237 问"];
const statsDocErrors = statsDocFiles.flatMap(file => {
  if (!fs.existsSync(path.join(root, file))) return [`${file}:missing`];
  const text = fs.readFileSync(path.join(root, file), "utf8");
  const stale = staleStatTokens.filter(token => text.includes(token));
  return stale.length ? [`${path.basename(file)}:stale(${stale.join(",")})`] : [];
});
const handoffText = fs.readFileSync(path.join(root, "..", "HANDOFF.md"), "utf8");
if (!handoffText.includes(statsSummary)) statsDocErrors.push(`HANDOFF.md:missing-current-stats(${statsSummary})`);
if (!handoffText.includes(String(questionTotal))) statsDocErrors.push(`HANDOFF.md:missing-total(${questionTotal})`);
const lifecycleSummary = `${questionLifecycleStats.OPEN} OPEN / ${questionLifecycleStats.ANSWERED} ANSWERED / ${questionLifecycleStats.CLOSED} CLOSED`;
const ownerSummary = `AI_EVIDENCE ${questionOwnerStats.AI_EVIDENCE} / HUMAN_DECISION ${questionOwnerStats.HUMAN_DECISION} / RUNTIME_OWNER ${questionOwnerStats.RUNTIME_OWNER} / DEFERRED_DETAIL ${questionOwnerStats.DEFERRED_DETAIL}`;
if (!handoffText.includes(lifecycleSummary)) statsDocErrors.push(`HANDOFF.md:missing-lifecycle-stats(${lifecycleSummary})`);
if (!handoffText.includes(ownerSummary)) statsDocErrors.push(`HANDOFF.md:missing-owner-stats(${ownerSummary})`);
const rulingText = fs.readFileSync(path.join(root, "..", "待裁决清单.md"), "utf8");
if (!rulingText.includes(statsSummary)) statsDocErrors.push(`待裁决清单.md:missing-current-stats(${statsSummary})`);
check("handoff-stats-consistent", statsDocErrors.length === 0, statsDocErrors.join(", "));

// ===== 2026-08-19 加固：L1 目录状态与详情状态轴一致（防再次漂移） =====
const l1StatusErrors = details.flatMap(({ data }) => {
  const runtimeAxis = (data.statusAxes || []).find(axis => axis.axis === "运行状态");
  const l1 = model.systems.find(item => item.id === data.systemId);
  if (!l1 || !runtimeAxis) return [];
  const errors = [];
  const runtimeStatus = String(runtimeAxis.status || "");
  if (runtimeStatus.includes("UNKNOWN_LIVE")) {
    if (/未开放|已上线|LIVE_CONFIRMED/.test(l1.status)) errors.push(`${data.systemId}:L1「${l1.status}」与详情运行轴 UNKNOWN_LIVE 矛盾`);
  }
  if (runtimeStatus === "LIVE_CONFIRMED" && !/LIVE/.test(l1.status)) errors.push(`${data.systemId}:L1 缺少 LIVE 标注但详情为 LIVE_CONFIRMED`);
  return errors;
});
check("l1-status-consistent-with-details", l1StatusErrors.length === 0, l1StatusErrors.join(", "));

// ===== 2026-08-20 加固：原子级 questionRefs 解析检查 =====
// 所有 sectionApplicability 的 questionRefs 和 rule 的 questionRefs 必须指向本系统存在的 openQuestion ID
const allQuestionIdsBySystem = new Map(details.map(({ data }) => [data.systemId, new Set((data.openQuestions || []).map(q => q.id))]));
const atomQuestionRefErrors = details.flatMap(({ data }) => {
  const localQIds = allQuestionIdsBySystem.get(data.systemId);
  const errors = [];
  // sectionApplicability questionRefs
  for (const [key, entry] of Object.entries(data.sectionApplicability || {})) {
    if (Array.isArray(entry.questionRefs)) {
      for (const qid of entry.questionRefs) {
        if (!localQIds.has(qid)) errors.push(`${data.systemId}:${key}:dangling-questionRef(${qid})`);
      }
    }
  }
  // rule-level questionRefs
  for (const rule of (data.rules || [])) {
    if (Array.isArray(rule.questionRefs)) {
      for (const qid of rule.questionRefs) {
        if (!localQIds.has(qid)) errors.push(`${data.systemId}:${rule.id}:dangling-questionRef(${qid})`);
      }
    }
  }
  return errors;
});
check("atom-question-refs-resolve", atomQuestionRefErrors.length === 0, atomQuestionRefErrors.join(", "));

// ===== 2026-08-20 加固：P0 openQuestion 机器可读归类（decisionCardId 或合法 resolutionOwner） =====
const validResolutionOwners = new Set(["AI_EVIDENCE", "RUNTIME_OWNER", "HUMAN_DECISION", "DEFERRED_DETAIL"]);
const p0ClassificationErrors = details.flatMap(({ data }) =>
  (data.openQuestions || [])
    .filter(q => q.priority === "P0")
    .filter(q => {
      const hasOwner = q.resolutionOwner && validResolutionOwners.has(q.resolutionOwner);
      const cardOwnerConsistent = q.resolutionOwner === "HUMAN_DECISION" || !q.decisionCardId;
      return !hasOwner || !cardOwnerConsistent;
    })
    .map(q => `${data.systemId}:${q.id}:no-decisionCardId-or-resolutionOwner`)
);
check("p0-question-classification", p0ClassificationErrors.length === 0, p0ClassificationErrors.join(", "));

// ===== 2026-08-20 加固：P1/P2 openQuestion 也需机器可读归类 =====
const p1p2ClassificationErrors = details.flatMap(({ data }) =>
  (data.openQuestions || [])
    .filter(q => q.priority === "P1" || q.priority === "P2")
    .filter(q => {
      const hasOwner = q.resolutionOwner && validResolutionOwners.has(q.resolutionOwner);
      const cardOwnerConsistent = q.resolutionOwner === "HUMAN_DECISION" || !q.decisionCardId;
      return !hasOwner || !cardOwnerConsistent;
    })
    .map(q => `${data.systemId}:${q.id}:no-decisionCardId-or-resolutionOwner`)
);
check("p1p2-question-classification", p1p2ClassificationErrors.length === 0, p1p2ClassificationErrors.join(", "));

// ===== 2026-08-20 加固：决策卡注册表存在且结构合法 =====
const decisionCardRegistryPath = path.join(root, "decision-card-registry.json");
const decisionCardRegistry = fs.existsSync(decisionCardRegistryPath)
  ? JSON.parse(fs.readFileSync(decisionCardRegistryPath, "utf8"))
  : null;
const decisionCardErrors = [];
if (!decisionCardRegistry) decisionCardErrors.push("registry-missing");
else {
  if (decisionCardRegistry.schema !== "vgame-decision-card-registry/v1") decisionCardErrors.push("schema-mismatch");
  const cards = decisionCardRegistry.cards || [];
  if (cards.length < 14 || cards.length > 18) decisionCardErrors.push(`card-count(${cards.length})-out-of-range`);
  const cardIds = cards.map(c => c.id);
  if (new Set(cardIds).size !== cardIds.length) decisionCardErrors.push("duplicate-card-ids");
  for (const card of cards) {
    if (!card.id || !card.theme || !card.singleQuestion || !Array.isArray(card.closeableQuestionIds)) {
      decisionCardErrors.push(`${card.id || "MISSING"}:missing-required-fields`);
    }
    if (!Array.isArray(card.options) || card.options.length < 2 || card.options.length > 4) {
      decisionCardErrors.push(`${card.id || "MISSING"}:options-not-2-to-4`);
    } else if (new Set(card.options.map(option => option.id)).size !== card.options.length) {
      decisionCardErrors.push(`${card.id}:duplicate-option-ids`);
    }
    if (card.closeableQuestionIds?.length !== 1) decisionCardErrors.push(`${card.id}:must-close-exactly-one-question`);
    if (!card.options?.every(option => option.name && option.description)) decisionCardErrors.push(`${card.id}:option-missing-name-or-description`);
  }
  // 检查所有 P0 question 都有对应决策卡（或合法 resolutionOwner）
  // 同时做双向一致性校验：closeableQuestionIds ↔ openQuestions.decisionCardId
  // 1. 收集所有 openQuestion 的全量索引
  const allOpenQuestionMap = new Map(); // qid -> { systemId, priority, decisionCardId }
  for (const { data } of details) {
    for (const q of (data.openQuestions || [])) {
      allOpenQuestionMap.set(q.id, { systemId: data.systemId, priority: q.priority, decisionCardId: q.decisionCardId || null, resolutionOwner: q.resolutionOwner || null });
    }
  }
  // 2. 校验 closeableQuestionIds：canonical 格式、存在性、唯一性、双向一致
  const allCloseableIds = new Set();
  const idToCardMap = new Map(); // qid -> cardId（用于检测跨卡重复）
  for (const card of cards) {
    for (const qid of (card.closeableQuestionIds || [])) {
      // 2a. canonical 格式检查：必须以 SYS- 开头
      if (!qid.startsWith("SYS-")) {
        decisionCardErrors.push(`${card.id}:closeableQuestionId(${qid})-not-canonical-format`);
        continue;
      }
      // 2b. 跨卡重复检查
      if (idToCardMap.has(qid)) {
        decisionCardErrors.push(`${card.id}:closeableQuestionId(${qid})-duplicate-in-${idToCardMap.get(qid)}`);
        continue;
      }
      idToCardMap.set(qid, card.id);
      allCloseableIds.add(qid);
      // 2c. 存在性：必须在 system-details 的 openQuestions 中存在
      if (!allOpenQuestionMap.has(qid)) {
        decisionCardErrors.push(`${card.id}:closeableQuestionId(${qid})-not-found-in-openQuestions`);
        continue;
      }
      // 2d. 双向一致：该 question 的 decisionCardId 必须指向本卡
      const qInfo = allOpenQuestionMap.get(qid);
      if (qInfo.decisionCardId !== card.id) {
        decisionCardErrors.push(`${card.id}:closeableQuestionId(${qid})-decisionCardId-mismatch(expected=${card.id},actual=${qInfo.decisionCardId})`);
      }
      if (qInfo.resolutionOwner !== "HUMAN_DECISION") {
        decisionCardErrors.push(`${card.id}:closeableQuestionId(${qid})-owner-mismatch(expected=HUMAN_DECISION,actual=${qInfo.resolutionOwner})`);
      }
    }
  }
  // 3. 反向检查：所有 priority 的 openQuestion 有 decisionCardId 的，必须出现在对应卡的 closeableQuestionIds 中（P0/P1/P2 全覆盖）
  for (const { data } of details) {
    for (const q of (data.openQuestions || [])) {
      if (!validResolutionOwners.has(q.resolutionOwner)) {
        decisionCardErrors.push(`${data.systemId}:${q.id}:invalid-resolutionOwner(${q.resolutionOwner || "missing"})`);
      }
      if (q.resolutionOwner !== "HUMAN_DECISION" && q.decisionCardId) {
        decisionCardErrors.push(`${data.systemId}:${q.id}:non-human-owner-with-card`);
      }
      if (q.decisionCardId) {
        if (!cardIds.includes(q.decisionCardId)) {
          decisionCardErrors.push(`${data.systemId}:${q.id}:decisionCardId(${q.decisionCardId})-not-found`);
        }
        // 反向：该 question.id 应在对应卡的 closeableQuestionIds 中
        if (!allCloseableIds.has(q.id)) {
          decisionCardErrors.push(`${data.systemId}:${q.id}:not-in-closeableQuestionIds-of(${q.decisionCardId})`);
        }
      }
    }
  }
}
check("decision-card-registry", decisionCardErrors.length === 0, decisionCardErrors.join(", "));

// ===== 2026-08-24：正式人工裁决导入、原始证据与实施状态分离 =====
const humanDecisionErrors = [];
if (decisionCardRegistry) {
  const imported = decisionCardRegistry.decisionImport;
  if (!imported) humanDecisionErrors.push("decisionImport-missing");
  else {
    if (imported.status !== "HUMAN_DECISION_CONFIRMED") humanDecisionErrors.push(`decisionImport-status(${imported.status})`);
    if (imported.approvalStatus !== "APPROVED_TARGET") humanDecisionErrors.push(`decisionImport-approval(${imported.approvalStatus})`);
    if (imported.implementationStatus !== "IMPLEMENTATION_PENDING") humanDecisionErrors.push(`decisionImport-implementation(${imported.implementationStatus})`);
    if (imported.totalCards !== 18 || imported.confirmedCards !== 18) humanDecisionErrors.push("decisionImport-count-mismatch");
    const archiveManifestPath = path.join(repositoryRoot, "archive", "legacy-output-20260824", "manifest.json");
    const rulingsPath = path.join(repositoryRoot, "knowledge-base", "governance", "rulings.json");
    if (!fs.existsSync(archiveManifestPath)) humanDecisionErrors.push("decision-archive-missing");
    else {
      const archiveManifest = JSON.parse(fs.readFileSync(archiveManifestPath, "utf8"));
      if (!archiveManifest.fileCount || !Array.isArray(archiveManifest.files)) humanDecisionErrors.push("decision-archive-schema-or-count");
    }
    if (!fs.existsSync(rulingsPath)) humanDecisionErrors.push("rulings-registry-missing");
    else {
      const rulings = JSON.parse(fs.readFileSync(rulingsPath, "utf8"));
      if (!(rulings.rulings || []).some(item => item.rulingId === "RULING-EW-B" && item.status === "HUMAN_DECISION_CONFIRMED")) humanDecisionErrors.push("exclusive-weapon-ruling-missing");
    }
  }

  const questionMap = new Map();
  const detailMap = new Map(details.map(({ data }) => [data.systemId, data]));
  for (const { data } of details) for (const q of data.openQuestions || []) questionMap.set(q.id, { q, data });
  for (const card of decisionCardRegistry.cards || []) {
    if (card.approvalStatus !== "APPROVED_TARGET") humanDecisionErrors.push(`${card.id}:approval-not-approved-target`);
    if (card.decisionStatus !== "HUMAN_DECISION_CONFIRMED") humanDecisionErrors.push(`${card.id}:decision-not-confirmed`);
    if (card.implementationStatus !== "IMPLEMENTATION_PENDING") humanDecisionErrors.push(`${card.id}:implementation-not-pending(${card.implementationStatus})`);
    if (/LIVE|WORKING_COPY_OBSERVED|IMPLEMENTED/.test(card.implementationStatus || "")) humanDecisionErrors.push(`${card.id}:implementation-status-overclaim`);
    const option = (card.options || []).find(item => item.id === card.selectedOptionId);
    if (!option || option.name !== card.selectedOptionName) humanDecisionErrors.push(`${card.id}:selected-option-mismatch`);
    if (!card.confirmedAt || !card.decisionEvidence?.path) humanDecisionErrors.push(`${card.id}:decision-evidence-missing`);
    const qid = card.closeableQuestionIds?.[0];
    const holder = questionMap.get(qid);
    if (!holder) continue;
    const { q, data } = holder;
    if (q.lifecycle !== "CLOSED") humanDecisionErrors.push(`${card.id}:${qid}:not-closed`);
    if (q.resolutionOwner !== "HUMAN_DECISION") humanDecisionErrors.push(`${card.id}:${qid}:owner-mismatch`);
    if (q.approvalStatus !== "APPROVED_TARGET" || q.decisionStatus !== "HUMAN_DECISION_CONFIRMED" || q.implementationStatus !== "IMPLEMENTATION_PENDING") humanDecisionErrors.push(`${card.id}:${qid}:closure-status-mismatch`);
    const decision = (data.humanDecisions || []).find(item => item.cardId === card.id);
    if (!decision) humanDecisionErrors.push(`${card.id}:${qid}:system-humanDecision-missing`);
    else {
      if (decision.closeableQuestionId !== qid || decision.selectedOptionId !== card.selectedOptionId || decision.selectedOptionName !== card.selectedOptionName) humanDecisionErrors.push(`${card.id}:${qid}:system-humanDecision-mismatch`);
      if (decision.approvalStatus !== "APPROVED_TARGET" || decision.decisionStatus !== "HUMAN_DECISION_CONFIRMED" || decision.implementationStatus !== "IMPLEMENTATION_PENDING") humanDecisionErrors.push(`${card.id}:${qid}:system-humanDecision-status`);
      if (!q.closureEvidenceRefs?.includes(decision.evidenceRef)) humanDecisionErrors.push(`${card.id}:${qid}:closure-evidence-mismatch`);
      const evidence = (data.evidence || []).find(item => item.id === decision.evidenceRef);
      if (!evidence || evidence.kind !== "human-decision" || evidence.status !== "HUMAN_DECISION_CONFIRMED") humanDecisionErrors.push(`${card.id}:${qid}:human-evidence-invalid`);
    }
  }
  const dcE = decisionCardRegistry.cards?.find(card => card.id === "DC-E");
  if (dcE?.userComment !== "只有主线、高难需要三星") humanDecisionErrors.push("DC-E:comment-not-preserved-verbatim");
}
check("human-decision-import", humanDecisionErrors.length === 0, humanDecisionErrors.join(", "));

// ===== 2026-08-20 加固：网页 moduleRegistry 和决策卡注册表在生成物中 =====
const catalogModuleRegistry = generatedCatalog.moduleRegistry;
const moduleRegistryErrors = [];
if (!Array.isArray(catalogModuleRegistry) || catalogModuleRegistry.length !== 2) moduleRegistryErrors.push("count-mismatch");
else {
  for (const entry of catalogModuleRegistry) {
    if (!entry.moduleId || !entry.chunkRef || !entry.detailRef || !Array.isArray(entry.sectionIds)) {
      moduleRegistryErrors.push(`${entry.moduleId || "MISSING"}:missing-fields`);
    }
    if (entry.chunkRef && !fs.existsSync(path.join(root, entry.chunkRef))) moduleRegistryErrors.push(`${entry.moduleId}:chunk-missing`);
  }
}
if (!generatedCatalog.decisionCardRegistry || !Array.isArray(generatedCatalog.decisionCardRegistry.cards)) {
  moduleRegistryErrors.push("decisionCardRegistry-missing-in-catalog");
}
check("web-module-registry", moduleRegistryErrors.length === 0, moduleRegistryErrors.join(", "));

// ===== 2026-08-20 加固：M02 宣称 45 映射时结构化映射必须覆盖 45 系统 =====
const m02Detail = moduleDetails.find(({ data }) => data.moduleId === "M02");
const m02MappingErrors = [];
if (m02Detail) {
  // 只检查 overview.inScope 和 sections 的 summary，不跨字段拼接
  const m02InScope = (m02Detail.data.overview?.inScope || []).join(" ");
  const m02SectionSummaries = (m02Detail.data.sections || []).map(s => s.summary || "").join(" ");
  const m02CheckedText = m02InScope + " " + m02SectionSummaries;
  const claims45 = /45\s*个?系统.*映射|45.*真实映射/.test(m02CheckedText);
  // 检查 crossRefs 或 sections 中是否覆盖全部 45 系统
  const mappedSystemIds = new Set();
  for (const ref of (m02Detail.data.crossRefs || [])) {
    for (const sid of (ref.systemIds || [])) mappedSystemIds.add(sid);
  }
  if (claims45 && mappedSystemIds.size < 45) {
    m02MappingErrors.push(`claims-45-but-mapped-${mappedSystemIds.size}`);
  }
  // 如果映射不足 45，检查是否收窄声明
  if (mappedSystemIds.size < 45) {
    if (!/41.*显式映射|41.*explicit|域级占位|domain-level/.test(m02CheckedText)) {
      m02MappingErrors.push("should-narrow-claim-to-41-explicit-plus-4-domain-level");
    }
  }
}
check("m02-mapping-claim-consistent", m02MappingErrors.length === 0, m02MappingErrors.join(", "));

// ===== 2026-08-20 加固：源文档哈希漂移（项目门禁） =====
const frameworkJsonPath = path.join(root, "..", "project-planning-framework.json");
const sourceDocHashErrors = [];
if (fs.existsSync(frameworkJsonPath)) {
  const framework = JSON.parse(fs.readFileSync(frameworkJsonPath, "utf8"));
  // projectRoot: 优先从 framework JSON 同级目录推断（兼容临时目录测试），否则用标准路径
  const projectRoot = repositoryRoot;
  for (const doc of (framework.documents || [])) {
    const sourcePath = path.join(projectRoot, ...doc.sourcePath.split("/"));
    if (!fs.existsSync(sourcePath)) { sourceDocHashErrors.push(`${doc.sourcePath}:missing`); continue; }
    const normalizedSource = fs.readFileSync(sourcePath, "utf8").replace(/\r\n/g, "\n");
    const actualHash = crypto.createHash("sha256").update(normalizedSource, "utf8").digest("hex");
    if (actualHash !== doc.sourceSha256) sourceDocHashErrors.push(`${doc.sourcePath}:hash-drift`);
  }
}
check("source-document-hashes", sourceDocHashErrors.length === 0, sourceDocHashErrors.join(", "));

// ===== 2026-08-20 加固：relationTypes 包含新类型 migrates-to =====
check("relation-types-includes-migrates-to", model.relationTypes.some(item => item[0] === "migrates-to"), "migrates-to-missing");

const report = {
  schema: "vgame-planning-knowledge-validation/v1",
  generatedAt: new Date().toISOString(),
  passed: checks.every(item => item.pass),
  summary: {
    checks: checks.length,
    modules: model.modules.length,
    systems: model.systems.length,
    detailedSystems: details.length,
    specialistModules: moduleDetails.length,
    detailAtoms: detailAtomIds.length,
    moduleSections: moduleSectionIds.length,
    questionRecords: questionTotal,
    openQuestions: questionLifecycleStats.OPEN,
    questionStats,
    questionLifecycleStats,
    questionOwnerStats,
    decisionCards: decisionCardRegistry?.cards?.length || 0,
    combatEntries: model.combat.rules.length + model.combat.character.length,
    numericEntries: model.numeric.length,
    relationTypes: model.relationTypes.length
  },
  checks
};

fs.writeFileSync(path.join(root, "validation-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report.summary));
if (!report.passed) process.exitCode = 1;
