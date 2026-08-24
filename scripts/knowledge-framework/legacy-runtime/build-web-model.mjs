import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { detailMarkdown, safeFileName, markdownRefFor } from "./render-markdown.mjs";

const root = path.dirname(fileURLToPath(import.meta.url));
const jsonPath = path.join(root, "knowledge-model.json");
const jsPath = path.join(root, "knowledge-model.js");
const searchIndexPath = path.join(root, "knowledge-search-index.js");
const routerManifestPath = path.join(root, "router-manifest.json");
const policyPath = path.join(root, "retrieval-policy.json");
const contractsPath = path.join(root, "shared-contracts", "contract-registry.json");
const detailsDir = path.join(root, "system-details");
const chunksDir = path.join(root, "system-chunks");
const systemsDir = path.join(root, "systems");
const moduleDetailsDir = path.join(root, "module-details");
const moduleChunksDir = path.join(root, "module-chunks");
const decisionCardRegistryPath = path.join(root, "decision-card-registry.json");

const model = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));
const contractRegistry = JSON.parse(fs.readFileSync(contractsPath, "utf8"));
const detailFiles = fs.existsSync(detailsDir)
  ? fs.readdirSync(detailsDir).filter(file => file.endsWith(".json")).sort()
  : [];
const details = detailFiles.map(file => {
  const detail = JSON.parse(fs.readFileSync(path.join(detailsDir, file), "utf8"));
  if (!detail.systemId) throw new Error(`${file}: missing systemId`);
  if (!model.systems.some(system => system.id === detail.systemId)) {
    throw new Error(`${file}: unknown systemId ${detail.systemId}`);
  }
  return detail;
});

// 专业模块正文（M01/M02，vgame-module-detail/v1）
const moduleDetailFiles = fs.existsSync(moduleDetailsDir)
  ? fs.readdirSync(moduleDetailsDir).filter(file => file.endsWith(".json")).sort()
  : [];
const moduleDetails = moduleDetailFiles.map(file => {
  const detail = JSON.parse(fs.readFileSync(path.join(moduleDetailsDir, file), "utf8"));
  if (!detail.moduleId) throw new Error(`${file}: missing moduleId`);
  if (detail.schema !== "vgame-module-detail/v1") throw new Error(`${file}: unsupported schema ${detail.schema}`);
  return detail;
});

// 决策卡注册表（DC-A~DC-P，结构化供网页评审台消费）
const decisionCardRegistry = fs.existsSync(decisionCardRegistryPath)
  ? JSON.parse(fs.readFileSync(decisionCardRegistryPath, "utf8"))
  : { schema: "vgame-decision-card-registry/v1", cards: [] };

const groupById = Object.fromEntries(model.systemGroups.map(group => [group.id, group]));
const systemById = Object.fromEntries(model.systems.map(system => [system.id, system]));
const contractById = Object.fromEntries(contractRegistry.contracts.map(contract => [contract.id, contract]));
const atomKeys = ["rules", "conditions", "rewards", "exceptions", "ui", "configs", "relationships", "evidence", "openQuestions"];
const detailAtoms = detail => atomKeys.flatMap(key => detail[key] || []);
const unique = values => [...new Set(values.filter(Boolean))];

// 从正文语义字段提取 CamelCase/全大写技术符号（供路由技术符号检索）。
const TECH_TOKEN_PATTERN = /\b[A-Z][A-Za-z0-9]{3,}\b|\b[A-Z][A-Z0-9]{2,}\b/g;
const TECH_TOKEN_FIELDS = ["name", "targetRule", "sourceFact", "rule", "description", "acceptance", "question", "impact", "location", "purpose"];
function extractTechTokens(detail, limit = 150) {
  const tokens = new Set();
  const atoms = [...(detail.rules || []), ...(detail.conditions || []), ...(detail.rewards || []),
    ...(detail.exceptions || []), ...(detail.ui || []), ...(detail.configs || []), ...(detail.relationships || []),
    ...(detail.openQuestions || []), ...(detail.evidence || [])];
  const texts = [];
  for (const atom of atoms) for (const field of TECH_TOKEN_FIELDS) if (atom[field]) texts.push(String(atom[field]));
  for (const step of (detail.flows || []).flatMap(flow => flow.steps || [])) if (step.description) texts.push(step.description);
  for (const text of texts) for (const match of text.matchAll(TECH_TOKEN_PATTERN)) {
    const token = match[0];
    if (/^L\d+$/.test(token) || /^\d+$/.test(token)) continue; // 行号/纯数字不是可检索符号
    if (token.length >= 4 && token.length <= 30) tokens.add(token);
    if (tokens.size >= limit) return [...tokens];
  }
  return [...tokens];
}

for (const detail of details) {
  for (const ref of detail.contractRefs || []) {
    if (!contractById[ref.id]) throw new Error(`${detail.systemId}: unknown contract ${ref.id}`);
  }
}

const detailRegistry = Object.fromEntries(details.map(detail => [
  detail.systemId,
  {
    systemId: detail.systemId,
    name: detail.name,
    revision: detail.revision,
    updatedAt: detail.updatedAt,
    detailLevel: detail.detailLevel,
    atomCount: detailAtoms(detail).length + (detail.flows || []).reduce((sum, flow) => sum + 1 + (flow.steps || []).length, 0),
    evidenceCount: (detail.evidence || []).length,
    contractRefs: (detail.contractRefs || []).map(item => item.id),
    chunkRef: `system-chunks/${detail.systemId}.js`,
    jsonRef: `system-details/${detail.systemId}.json`,
    markdownRef: markdownRefFor(detail)
  }
]));

function atomSearchEntries(detail) {
  const system = systemById[detail.systemId];
  const group = groupById[system.group];
  const common = {
    parentId: detail.systemId,
    parentName: detail.name,
    module: "system",
    path: `系统 / ${group?.name || system.group} / ${detail.name}`,
    targetRevision: detail.revision
  };
  const entries = [];
  for (const flow of detail.flows || []) {
    entries.push({
      ...common,
      id: flow.id,
      targetType: "flow",
      name: flow.name,
      summary: flow.summary || (flow.steps || []).map(step => step.name).join(" → "),
      status: flow.status || "KNOWLEDGE_CURRENT",
      evidenceRefs: flow.evidenceRefs || []
    });
    for (const step of flow.steps || []) {
      entries.push({
        ...common,
        id: step.id,
        targetType: "flow-step",
        name: step.name,
        summary: step.description || "",
        status: step.status || flow.status || "KNOWLEDGE_CURRENT",
        evidenceRefs: step.evidenceRefs || flow.evidenceRefs || []
      });
    }
  }
  const typeByKey = {
    rules: "rule",
    conditions: "condition",
    rewards: "reward",
    exceptions: "exception",
    ui: "ui",
    configs: "config",
    relationships: "relation",
    evidence: "evidence",
    openQuestions: "question"
  };
  for (const key of atomKeys) {
    for (const item of detail[key] || []) {
      entries.push({
        ...common,
        id: item.id,
        targetType: typeByKey[key],
        name: item.name || item.label || item.question || item.id,
        summary: item.targetRule || item.rule || item.description || item.role || item.impact || item.location || "",
        status: item.status || item.priority || "UNKNOWN",
        lifecycle: item.lifecycle || (key === "openQuestions" ? "OPEN" : undefined),
        resolutionOwner: item.resolutionOwner,
        answer: item.answer,
        resolvedBy: item.resolvedBy,
        resolvedAt: item.resolvedAt,
        closureEvidenceRefs: item.closureEvidenceRefs || [],
        evidenceRefs: key === "evidence" ? [item.id] : (item.evidenceRefs || [])
      });
    }
  }
  return entries;
}

const searchIndex = details.flatMap(atomSearchEntries);

// 模块 section 进入搜索索引（targetType=module-section，parentId=moduleId）
// module 字段设为 "module" 以便网页搜索结果点击后导航到 #module/<moduleId>/<sectionId>
const moduleSearchEntries = moduleDetails.flatMap(detail =>
  (detail.sections || []).map(section => ({
    id: section.id,
    parentId: detail.moduleId,
    parentName: detail.name,
    module: "module",
    path: `专业模块 / ${detail.name} / ${section.name}`,
    targetRevision: detail.revision,
    targetType: "module-section",
    name: section.name,
    summary: section.summary || "",
    status: section.status || "KNOWLEDGE_CURRENT",
    evidenceRefs: []
  }))
);
const fullSearchIndex = [...searchIndex, ...moduleSearchEntries];
const routerSystems = model.systems.map(system => {
  const detail = details.find(item => item.systemId === system.id);
  const group = groupById[system.group];
  const aliases = unique([system.name, ...(policy.aliasOverrides?.[system.id] || [])]);
  const atomNames = detail ? searchIndex.filter(item => item.parentId === system.id).map(item => item.name) : [];
  // 技术符号 token（ResultHash/CoinMode/GameOverData 等 CamelCase）：让"某符号在哪赋值/是否实装"类问题
  // 能命中对应系统，而不需要在问题里写出系统名。来源限定正文语义字段，控制数量防止 manifest 膨胀。
  const techTokens = detail ? extractTechTokens(detail) : [];
  return {
    id: system.id,
    name: system.name,
    module: "system",
    groupId: system.group,
    groupName: group?.name || system.group,
    path: `系统 / ${group?.name || system.group} / ${system.name}`,
    aliases,
    keywords: unique([...aliases, ...(system.relations || []), ...atomNames, ...techTokens]),
    summary: system.summary,
    status: system.status,
    relations: system.relations || [],
    relatedIds: unique((detail?.relationships || []).map(item => item.targetId)),
    detailLevel: detail?.detailLevel || "summary",
    detailRef: detail ? `system-details/${system.id}.json` : null,
    chunkRef: detail ? `system-chunks/${system.id}.js` : null,
    markdownRef: detail ? markdownRefFor(detail) : null,
    contractRefs: (detail?.contractRefs || []).map(item => item.id),
    revision: detail?.revision || null,
    evidenceCount: (detail?.evidence || []).length
  };
});

const specialistModules = moduleDetails.map(detail => {
  const aliases = unique([detail.name, detail.moduleId, ...(policy.aliasOverrides?.[detail.moduleId] || [])]);
  const sectionNames = (detail.sections || []).map(section => section.name);
  return {
    id: detail.moduleId,
    name: detail.name,
    module: detail.parentModule,
    moduleName: model.modules.find(item => item.id === detail.parentModule)?.name || detail.parentModule,
    path: `专业模块 / ${detail.name}`,
    aliases,
    keywords: unique([...aliases, ...sectionNames, ...(detail.crossRefs || []).map(ref => `${ref.targetType}:${ref.targetId}`)]),
    summary: detail.overview?.purpose || "",
    status: (detail.statusAxes || [])[0]?.status || "KNOWLEDGE_CURRENT",
    revision: detail.revision,
    updatedAt: detail.updatedAt,
    detailLevel: detail.detailLevel,
    sourceDoc: detail.sourceDoc,
    detailRef: `module-details/${detail.moduleId}.json`,
    chunkRef: `module-chunks/${detail.moduleId}.js`,
    sectionIds: (detail.sections || []).map(section => section.id),
    crossRefCount: (detail.crossRefs || []).length,
    aggregatedConflicts: (detail.aggregatedConflicts || []).map(item => item.id)
  };
});

const routerManifest = {
  schema: "vgame-knowledge-router-manifest/v1",
  version: model.meta.version,
  updatedAt: model.meta.updatedAt,
  title: model.meta.title,
  thesis: model.meta.thesis,
  promptlessRouting: policy.promptlessRouting,
  layers: policy.layers,
  profiles: policy.depthProfiles,
  intentSignals: policy.intentSignals,
  provenance: policy.provenance,
  modules: model.modules,
  groups: model.systemGroups,
  systems: routerSystems,
  specialistModules,
  contracts: contractRegistry.contracts
};

const canonicalHash = crypto
  .createHash("sha256")
  .update(JSON.stringify(details.map(d => d.systemId).sort()))
  .update(JSON.stringify(details.map(d => [d.systemId, d.revision, d.updatedAt, d.detailLevel])))
  .update(JSON.stringify(fullSearchIndex.map(e => [e.id, e.parentId, e.targetType, e.name, e.summary, e.status])))
  .update(JSON.stringify(moduleDetails.map(d => [d.moduleId, d.revision, d.updatedAt, d.detailLevel])))
  .digest("hex")
  .substring(0, 16);
routerManifest.buildHash = canonicalHash;

fs.mkdirSync(chunksDir, { recursive: true });
fs.mkdirSync(systemsDir, { recursive: true });
fs.mkdirSync(moduleChunksDir, { recursive: true });
for (const detail of details) {
  fs.writeFileSync(
    path.join(chunksDir, `${detail.systemId}.js`),
    `/* Generated lazy detail chunk. */\nwindow.VGAME_SYSTEM_DETAILS = window.VGAME_SYSTEM_DETAILS || {};\nwindow.VGAME_SYSTEM_DETAILS[${JSON.stringify(detail.systemId)}] = ${JSON.stringify(detail, null, 2)};\n`,
    "utf8"
  );
  const safeName = safeFileName(detail.name);
  fs.writeFileSync(path.join(systemsDir, `${detail.systemId}-${safeName}.md`), detailMarkdown(detail, contractById), "utf8");
}
// 从源 Markdown 提取每个 section 的正文，编译进 module chunk，使 file:// 离线打开时
// "加载本章节完整正文" 不依赖 fetch（浏览器在 file:// 下阻止 fetch 本地文件）。
function extractSectionMarkdown(sourcePath, sections) {
  let mdText = "";
  try {
    mdText = fs.readFileSync(sourcePath, "utf8");
  } catch {
    return sections; // 源文件不存在时返回原样（不阻塞构建）
  }
  const lines = mdText.split("\n");
  return sections.map(section => {
    const anchor = section.anchor;
    const anchorIdx = lines.findIndex(l => l.trim() === anchor);
    if (anchorIdx < 0) return section;
    let endIdx = lines.length;
    for (let i = anchorIdx + 1; i < lines.length; i++) {
      if (/^##\s/.test(lines[i]) && !lines[i].trim().startsWith("###")) { endIdx = i; break; }
    }
    const sectionMd = lines.slice(anchorIdx, endIdx).join("\n").trimEnd();
    return { ...section, sectionContent: sectionMd };
  });
}

for (const detail of moduleDetails) {
  const sourcePath = path.join(root, detail.sourceDoc || "");
  const enrichedSections = extractSectionMarkdown(sourcePath, detail.sections || []);
  const chunkDetail = { ...detail, sections: enrichedSections };
  fs.writeFileSync(
    path.join(moduleChunksDir, `${detail.moduleId}.js`),
    `/* Generated lazy module detail chunk. */\nwindow.VGAME_MODULE_DETAILS = window.VGAME_MODULE_DETAILS || {};\nwindow.VGAME_MODULE_DETAILS[${JSON.stringify(detail.moduleId)}] = ${JSON.stringify(chunkDetail, null, 2)};\n`,
    "utf8"
  );
}

const catalogModel = structuredClone(model);
catalogModel.detailRegistry = detailRegistry;
// 模块注册表：供网页懒加载 module-chunks/ 和渲染模块正文
catalogModel.moduleRegistry = moduleDetails.map(detail => ({
  moduleId: detail.moduleId,
  name: detail.name,
  revision: detail.revision,
  updatedAt: detail.updatedAt,
  detailLevel: detail.detailLevel,
  parentModule: detail.parentModule,
  sourceDoc: detail.sourceDoc,
  chunkRef: `module-chunks/${detail.moduleId}.js`,
  detailRef: `module-details/${detail.moduleId}.json`,
  sectionIds: (detail.sections || []).map(section => section.id),
  sections: (detail.sections || []).map(section => ({ id: section.id, name: section.name, anchor: section.anchor, summary: section.summary, status: section.status })),
  overview: detail.overview,
  statusAxes: detail.statusAxes || []
}));
// 决策卡注册表：供网页评审台渲染 DC-A~DC-P
catalogModel.decisionCardRegistry = decisionCardRegistry;
delete catalogModel.systemDetails;
fs.writeFileSync(
  jsPath,
  `/* Generated lightweight catalog. Full system details load lazily from system-chunks/. */\nwindow.VGAME_KB = ${JSON.stringify(catalogModel, null, 2)};\n`,
  "utf8"
);
fs.writeFileSync(
  searchIndexPath,
  `/* Generated lightweight atom search index; no full rule bodies. */\nwindow.VGAME_KB_SEARCH = ${JSON.stringify(fullSearchIndex, null, 2)};\n`,
  "utf8"
);
fs.writeFileSync(routerManifestPath, `${JSON.stringify(routerManifest, null, 2)}\n`, "utf8");

const output = {
  catalogBytes: fs.statSync(jsPath).size,
  searchIndexBytes: fs.statSync(searchIndexPath).size,
  routerManifestBytes: fs.statSync(routerManifestPath).size,
  detailedSystems: details.length,
  specialistModules: moduleDetails.length,
  detailAtoms: searchIndex.length,
  moduleSectionEntries: moduleSearchEntries.length
};
console.log(JSON.stringify(output, null, 2));
