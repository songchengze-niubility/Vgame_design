import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..", "..");
const kbRoot = path.join(repoRoot, "knowledge-base");
const authorityPath = path.join(kbRoot, "AUTHORITY.json");
if (fs.existsSync(authorityPath)) {
  const authority = JSON.parse(fs.readFileSync(authorityPath, "utf8"));
  if (authority.schema === "vgame-knowledge-authority/v2" && !process.argv.includes("--force-v1-destructive")) {
    throw new Error("V2 authority detected. author-v1.mjs is frozen to prevent rollback; use scripts/numerical-knowledge/import-framework.py plus rebuild.ps1.");
  }
}
const legacyRoot = process.argv[2] || "C:/Users/songchengze/.codex/worktrees/3f62/Vgame_design/output/项目级策划知识框架";
const today = "2026-08-24";

const readJson = p => JSON.parse(fs.readFileSync(p, "utf8"));
const sha256 = data => crypto.createHash("sha256").update(data).digest("hex");
const writeJson = (p, data) => {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, `${JSON.stringify(data, null, 2)}\n`, "utf8");
};
const writeText = (p, data) => {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, data.replace(/\r\n/g, "\n"), "utf8");
};
const rel = p => path.relative(repoRoot, p).replace(/\\/g, "/");

const modelPath = path.join(kbRoot, "registries", "knowledge-model.json");
const model = readJson(modelPath);
model.meta = {
  ...model.meta,
  schema: "vgame-planning-knowledge/v1.0",
  version: "1.0.0",
  updatedAt: today,
  title: "Vgame 项目级策划知识框架 V1.0",
  thesis: "knowledge-base 是权威正文；skills 是 Skill 正文唯一来源；output 仅含可重建生成物。"
};

const frameworkNodes = [
  ["PFN-01", "项目总览与核心循环", "project", "Vgame 身份、玩家长期目标与核心循环。"],
  ["PFN-02", "系统框架", "system", "全系统目录、边界与共同契约。"],
  ["PFN-03", "战斗内系统", "system-in", "战斗实例、单位、技能、关卡空间、胜负与反馈。"],
  ["PFN-04", "战斗外系统", "system-out", "战斗外玩法、养成、资源、商业化和辅助域总入口。"],
  ["PFN-05", "战斗外·玩法", "system-out-gameplay", "挑战入口、层级、周期与玩法结算壳。"],
  ["PFN-06", "战斗外·养成", "system-out-growth", "资源向属性、机制、构筑与阵容宽度的转化。"],
  ["PFN-07", "经济资源", "economy", "物品、货币、来源、消耗、掉落与奖励账本。"],
  ["PFN-08", "商业化", "monetization", "抽卡、月卡、礼包、付费商品与经济敏感边界。"],
  ["PFN-09", "周边、运营与辅助系统", "support", "任务、签到、邮件、通行证、社交、引导与 LiveOps。"],
  ["PFN-10", "战斗规则", "combat-rules", "战斗状态、单位、技能 Buff、胜负与结算规则。"],
  ["PFN-11", "角色设计", "character-design", "角色定位、技能循环、成长挂接与配置链。"],
  ["PFN-12", "战斗内容", "battle-content", "敌人、Boss、AI、波次、地形与关卡遭遇。"],
  ["PFN-13", "数值框架 V2", "numeric-v2", "共享底座、养成、战斗、经济、节奏和配置交付。"],
  ["PFN-14", "系统输入与输出", "relations-io", "每个系统消费什么并向下游提供什么。"],
  ["PFN-15", "系统依赖", "relations-dependency", "前置、共享契约、配置和运行依赖。"],
  ["PFN-16", "系统循环", "relations-loop", "核心、成长、经济、留存与 LiveOps 循环。"],
  ["PFN-17", "Skill 注册与调用层", "skill-routing", "33 个 Skill 的注册、依赖与最小按需调用。"],
  ["PFN-18", "证据、状态与来源边界", "evidence-status", "来源性质、工作副本/LIVE 边界与证据账本。"],
  ["PFN-19", "人工裁决与治理", "governance", "裁决、冲突、归档、发布与门禁治理。"]
].map(([id, name, layer, responsibility], index) => ({ id, order: index + 1, name, layer, responsibility, status: "ACTIVE" }));
writeJson(path.join(kbRoot, "registries", "framework-nodes.json"), {
  schema: "vgame-framework-nodes/v1",
  version: "1.0.0",
  formalEntry: "knowledge-base/README.md",
  expectedCount: 19,
  nodes: frameworkNodes
});
model.frameworkNodeIds = frameworkNodes.map(x => x.id);

const allSystemIds = model.systems.map(x => x.id);
const groupSystems = group => model.systems.filter(x => x.group === group).map(x => x.id);
const coverage = {
  "vgame-core-understanding": allSystemIds,
  "vgame-knowledge-router": allSystemIds,
  "planning-feature-workflow": ["FRAMEWORK:*"],
  "vgame-battle-content-map": groupSystems("system-in").concat(groupSystems("system-out-gameplay")),
  "vgame-battle-tuning-helper": groupSystems("system-in").concat(groupSystems("system-out-gameplay")),
  "vgame-character-kit-design-map": ["SYS-IN-02", "SYS-IN-03", "SYS-OUT-GR-02", "SYS-OUT-GR-03", "SYS-OUT-GR-04", "SYS-OUT-GR-05", "SYS-OUT-GR-06", "SYS-OUT-GR-07", "SYS-OUT-GR-10"],
  "vgame-hero-skill-config-map": ["SYS-IN-02", "SYS-IN-03", "SYS-OUT-GR-02", "SYS-OUT-GR-03", "SYS-OUT-GR-04", "SYS-OUT-GR-10"],
  "vgame-config-schema": allSystemIds,
  "vgame-config-quality-audit": allSystemIds,
  "vgame-economy-source-map": groupSystems("system-out-growth").concat(groupSystems("system-out-support")),
  "vgame-reward-drop-sync": groupSystems("system-out-gameplay").concat(["SYS-OUT-SU-04", "SYS-OUT-SU-05", "SYS-OUT-SU-06", "SYS-OUT-SU-07", "SYS-OUT-SU-08", "SYS-OUT-SU-09", "SYS-OUT-SU-10", "SYS-OUT-SU-14", "SYS-OUT-SU-15"]),
  "vgame-level-progression-map": groupSystems("system-out-gameplay").concat(["SYS-OUT-SU-13"]),
  "vgame-growth-combat-conversion-map": groupSystems("system-out-growth").concat(groupSystems("system-out-gameplay")),
  "vgame-level-design-map": ["SYS-IN-05", "SYS-IN-06"].concat(groupSystems("system-out-gameplay")),
  "vgame-outer-loop-system-map": groupSystems("system-out-support"),
  "vgame-player-progression-simulator": groupSystems("system-out-gameplay").concat(groupSystems("system-out-growth"), ["SYS-OUT-SU-04", "SYS-OUT-SU-05", "SYS-OUT-SU-06", "SYS-OUT-SU-07", "SYS-OUT-SU-08", "SYS-OUT-SU-10"]),
  "vgame-tutorial-onboarding-map": ["SYS-IN-07", "SYS-OUT-GP-01", "SYS-OUT-SU-13"],
  "vgame-version-release-map": allSystemIds,
  "senior-game-economy": groupSystems("system-out-gameplay").concat(groupSystems("system-out-growth"), groupSystems("system-out-support")),
  "game-numerical-analysis": allSystemIds,
  "outer-loop-progression-pacing": groupSystems("system-out-gameplay").concat(groupSystems("system-out-growth"), groupSystems("system-out-support")),
  "game-monetization": ["SYS-OUT-SU-01", "SYS-OUT-SU-02", "SYS-OUT-SU-06", "SYS-OUT-SU-10", "SYS-OUT-SU-14", "SYS-OUT-SU-15"],
  "planning-liveops-readiness": ["SYS-OUT-SU-14"],
  "planning-analytics-instrumentation": ["FRAMEWORK:*"],
  "planning-acceptance-traceability": ["FRAMEWORK:*"],
  "planning-change-sync": ["FRAMEWORK:*"],
  "planning-requirement-clarification": ["FRAMEWORK:*"],
  "experimentation-analytics": ["FRAMEWORK:*"],
  "product-analytics-setup": ["FRAMEWORK:*"],
  "accessibility-compliance": ["SYS-IN-07", "SYS-OUT-SU-13"],
  "localize": ["FRAMEWORK:*"],
  "vgame-ui-prototype": ["FRAMEWORK:*"],
  "vgame-figma-ui": ["FRAMEWORK:*"]
};

const categoryMap = {
  "vgame-core-understanding": "项目总控", "vgame-knowledge-router": "知识路由",
  "planning-feature-workflow": "策划流程", "planning-requirement-clarification": "策划流程",
  "planning-acceptance-traceability": "策划流程", "planning-change-sync": "策划流程",
  "planning-analytics-instrumentation": "数据与验收", "planning-liveops-readiness": "运营治理",
  "vgame-config-schema": "配置与质量", "vgame-config-quality-audit": "配置与质量",
  "vgame-reward-drop-sync": "经济与奖励", "vgame-economy-source-map": "经济与奖励",
  "senior-game-economy": "经济与奖励", "game-numerical-analysis": "数值",
  "outer-loop-progression-pacing": "数值", "vgame-player-progression-simulator": "数值",
  "vgame-battle-tuning-helper": "战斗数值", "vgame-battle-content-map": "战斗内容",
  "vgame-level-design-map": "关卡与玩法", "vgame-level-progression-map": "关卡与玩法",
  "vgame-character-kit-design-map": "角色与成长", "vgame-hero-skill-config-map": "角色与成长",
  "vgame-growth-combat-conversion-map": "角色与成长", "vgame-outer-loop-system-map": "外循环",
  "vgame-tutorial-onboarding-map": "引导", "vgame-version-release-map": "版本治理",
  "vgame-ui-prototype": "UI交付", "vgame-figma-ui": "UI交付",
  "game-monetization": "商业化", "experimentation-analytics": "数据分析",
  "product-analytics-setup": "数据分析", "accessibility-compliance": "交付质量",
  "localize": "本地化"
};
const dependencies = {
  "vgame-knowledge-router": ["vgame-core-understanding"],
  "vgame-config-quality-audit": ["vgame-core-understanding", "vgame-config-schema"],
  "vgame-reward-drop-sync": ["vgame-core-understanding", "vgame-config-schema", "vgame-economy-source-map"],
  "vgame-level-progression-map": ["vgame-core-understanding", "vgame-config-schema"],
  "vgame-battle-content-map": ["vgame-core-understanding", "vgame-config-schema"],
  "vgame-level-design-map": ["vgame-core-understanding", "vgame-config-schema", "vgame-battle-content-map"],
  "vgame-growth-combat-conversion-map": ["vgame-core-understanding", "vgame-character-kit-design-map"],
  "vgame-player-progression-simulator": ["vgame-core-understanding", "senior-game-economy"],
  "vgame-ui-prototype": ["planning-feature-workflow"],
  "vgame-figma-ui": ["planning-feature-workflow"],
  "planning-acceptance-traceability": ["planning-feature-workflow"],
  "planning-change-sync": ["planning-feature-workflow", "planning-acceptance-traceability"],
  "planning-analytics-instrumentation": ["planning-feature-workflow"],
  "planning-liveops-readiness": ["planning-feature-workflow", "vgame-version-release-map"]
};
const layerForCategory = category => {
  if (["项目总控", "知识路由", "策划流程"].includes(category)) return ["PFN-17", "PFN-19"];
  if (["配置与质量", "版本治理", "运营治理", "交付质量"].includes(category)) return ["PFN-18", "PFN-19"];
  if (["数值", "战斗数值", "经济与奖励"].includes(category)) return ["PFN-07", "PFN-13", "PFN-14"];
  if (["战斗内容", "关卡与玩法"].includes(category)) return ["PFN-03", "PFN-10", "PFN-12"];
  if (["角色与成长"].includes(category)) return ["PFN-06", "PFN-11", "PFN-13"];
  if (["外循环", "商业化", "引导"].includes(category)) return ["PFN-04", "PFN-08", "PFN-09"];
  return ["PFN-17", "PFN-19"];
};
const gateForCategory = category => {
  if (category === "UI交付") return ["ui_mockup_approved", "asset_manifest_valid", "human_acceptance_required"];
  if (category === "配置与质量") return ["source_schema_confirmed", "read_only_audit_passed", "reference_integrity_passed"];
  if (["经济与奖励", "数值", "战斗数值", "商业化"].includes(category)) return ["evidence_confirmed", "numeric_validation_passed", "human_acceptance_required"];
  return ["evidence_traceable", "required_outputs_exist", "human_acceptance_required"];
};

const skillFiles = fs.readdirSync(path.join(repoRoot, "skills"), { withFileTypes: true })
  .filter(x => x.isDirectory() && fs.existsSync(path.join(repoRoot, "skills", x.name, "SKILL.md")))
  .map(x => x.name).sort();
const skills = skillFiles.map(skillId => {
  const sourcePath = path.join(repoRoot, "skills", skillId, "SKILL.md");
  const source = fs.readFileSync(sourcePath, "utf8");
  const frontmatter = source.match(/^---\s*\n([\s\S]*?)\n---/m)?.[1] || "";
  const description = frontmatter.match(/^description:\s*(.*)$/m)?.[1]?.trim() || source.match(/^#\s+(.+)$/m)?.[1] || skillId;
  const category = categoryMap[skillId] || "通用能力";
  const refDir = path.join(repoRoot, "skills", skillId, "references");
  const refs = fs.existsSync(refDir)
    ? fs.readdirSync(refDir, { withFileTypes: true }).filter(x => x.isFile()).slice(0, 12).map(x => rel(path.join(refDir, x.name)))
    : [];
  return {
    skillId,
    category,
    responsibility: description,
    triggers: [description, `问题明确涉及 ${skillId} 的职责边界`],
    inputs: ["用户问题或已确认需求契约", "按路由选中的最小知识包", "必要的源配置/代码/设计证据"],
    outputs: ["带来源性质的结论或专项产物", "风险、缺口与 UNKNOWN", "对应门禁和可追踪证据"],
    coveredSystems: coverage[skillId] || ["FRAMEWORK:*"],
    dependsOnSkills: dependencies[skillId] || [],
    evidenceSources: [rel(sourcePath), ...refs],
    deliveryGates: gateForCategory(category),
    knowledgeLayers: layerForCategory(category),
    versionStatus: "ACTIVE_V1",
    sourcePath: rel(sourcePath),
    sourceSha256: sha256(source)
  };
});
writeJson(path.join(kbRoot, "registries", "skill-registry.json"), {
  schema: "vgame-skill-registry/v1",
  version: "1.0.0",
  generatedFrom: "skills/*/SKILL.md + registry metadata",
  expectedCount: 33,
  skills
});

const systemSkillMappings = model.systems.map(system => {
  const mapped = new Set(["vgame-core-understanding", "vgame-knowledge-router"]);
  for (const skill of skills) if (skill.coveredSystems.includes(system.id)) mapped.add(skill.skillId);
  if (system.group === "system-in") ["vgame-battle-content-map", "vgame-battle-tuning-helper"].forEach(x => mapped.add(x));
  if (system.group === "system-out-gameplay") ["vgame-level-progression-map", "vgame-reward-drop-sync"].forEach(x => mapped.add(x));
  if (system.group === "system-out-growth") ["vgame-growth-combat-conversion-map", "outer-loop-progression-pacing"].forEach(x => mapped.add(x));
  if (system.group === "system-out-support") ["vgame-outer-loop-system-map", "vgame-economy-source-map"].forEach(x => mapped.add(x));
  return { systemId: system.id, systemName: system.name, primarySkill: [...mapped][2] || "vgame-core-understanding", skills: [...mapped] };
});
writeJson(path.join(kbRoot, "mappings", "system-to-skill.json"), {
  schema: "vgame-system-to-skill/v1", expectedSystemCount: model.systems.length, coverage: "100%", mappings: systemSkillMappings
});
writeJson(path.join(kbRoot, "mappings", "question-to-skill.json"), {
  schema: "vgame-question-to-skill/v1",
  rules: skills.map((skill, index) => ({ id: `QSK-${String(index + 1).padStart(2, "0")}`, signals: skill.triggers, primarySkill: skill.skillId, dependsOnSkills: skill.dependsOnSkills }))
});
writeJson(path.join(kbRoot, "mappings", "skill-to-knowledge-layer.json"), {
  schema: "vgame-skill-to-layer/v1", mappings: skills.map(x => ({ skillId: x.skillId, frameworkNodeIds: x.knowledgeLayers }))
});
writeJson(path.join(kbRoot, "mappings", "skill-to-evidence.json"), {
  schema: "vgame-skill-to-evidence/v1", mappings: skills.map(x => ({ skillId: x.skillId, evidenceSources: x.evidenceSources }))
});

const workPackages = readJson(path.join(kbRoot, "registries", "work-packages.json"));
const packageBySystem = new Map(workPackages.packages.flatMap(item => (item.systemIds || []).map(systemId => [systemId, item.id])));
writeJson(path.join(kbRoot, "registries", "authoring-source-map.json"), {
  schema: "vgame-knowledge-authoring-source-map/v1",
  version: "1.0.0",
  systems: systemSkillMappings
    .filter(item => item.systemId !== "SYS-OUT-GP-01")
    .map(item => ({
      systemId: item.systemId,
      packageId: packageBySystem.get(item.systemId),
      recommendedSkills: item.skills.filter(skillId => fs.existsSync(path.join(repoRoot, "skills", skillId, "SKILL.md"))),
      seedDesignDocs: [],
      seedKnowledgeRefs: [`knowledge-base/system-details/${item.systemId}.json`],
      configAreas: [],
      codeAreas: [],
      risks: ["工作副本观察不得冒充 LIVE 状态", "跨来源推导必须标注 provenance"],
      sourceStatus: "DIRECT"
    }))
});

const detailsDir = path.join(kbRoot, "system-details");
const detailFiles = fs.readdirSync(detailsDir).filter(x => x.endsWith(".json")).sort();
const details = detailFiles.map(file => readJson(path.join(detailsDir, file)));
const deepReplace = value => {
  if (Array.isArray(value)) return value.map(deepReplace);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, deepReplace(v)]));
  if (typeof value !== "string") return value;
  return value
    .replaceAll("D:\\Vgame_design\\output\\项目级策划知识框架", "archive/legacy-output-20260824")
    .replaceAll("D:\\Vgame_design\\design\\", "design/")
    .replaceAll("output/项目级策划知识框架/review/decisions/vgame-decision-cards-2026-08-24.json", "archive/legacy-output-20260824/registries/decision-card-registry.json")
    .replaceAll("已确认专武线废弃并迁移到收容物", "已确认专武向收容物迁移，并保留一个大版本的兼容迁移期")
    .replaceAll("已确认“专武线废弃并迁移到收容物”", "已确认专武向收容物迁移，并保留一个大版本的兼容迁移期")
    .replaceAll("专武线废弃并迁移", "专武向收容物迁移并保留一个大版本兼容期")
    .replaceAll("迁移版本、兼容期、数据方案", "兼容期起止版本、数据方案")
    .replaceAll("C-001 未裁决", "C-001 兼容迁移期已裁决")
    .replaceAll("迁移冲突未裁决", "兼容迁移期已裁决、实施待完成")
    .replaceAll("C-001 记录专武→收容物迁移冲突（未裁决）。", "C-001 的历史冲突已归档；2026-08-24 B 裁决关闭方向问题，实施边界待完成。")
    .replaceAll("不得视为长期双轨", "不得超出获批兼容期")
    .replaceAll("专武→收容物迁移未裁决本体与经验本是否保留；局内不选边，交对应外循环系统裁决。", "专武→收容物采用一个大版本兼容期；经验本在兼容期内的维护与下线点由实施方案确定，局内规则服从发布台账。")
    .replaceAll("决定专武经验本局内规则是否继续维护，未裁决前局内不选边。", "决定专武经验本在一个大版本兼容期内的维护范围与最终下线点；局内规则服从发布台账。");
};

for (let i = 0; i < details.length; i++) details[i] = deepReplace(details[i]);
const byId = Object.fromEntries(details.map(x => [x.systemId, x]));

const rv = byId["SYS-OUT-GR-09"];
rv.revision = "2026-08-24.2";
rv.updatedAt = today;
const rvRule = rv.rules.find(x => x.id === "SYS-OUT-GR-09-R02");
rvRule.status = "HUMAN_DECISION_CONFIRMED_WORKING_COPY_ALIGNED";
rvRule.targetRule = "房车整备采用随机强化：每次结果增加 +30/+60/+100 进度，权重依次为 50/30/20；进度达到100时升级，消耗仍按 RvLvUp 与物品账本结算。";
rvRule.sourceFact = "2026-08-24 用户最新裁决选择 C；本机工作副本 RvStrengthenResult.xlsx 与 RVSystem.lua 已观察到 AddProgress/Weight 与 ResultId 消费链。工作副本一致不等于 Production/LIVE。";
rvRule.acceptance = "仅允许 +30/+60/+100 三档，权重严格为 50/30/20；单次与一键强化均走同一结果表；达到100的溢出/进位规则须由实现验收；被替代口径仅按归档证据 ID 追溯。";
const rvQ = rv.openQuestions.find(x => x.id === "SYS-OUT-GR-09-Q01");
Object.assign(rvQ, {
  lifecycle: "CLOSED",
  answer: "2026-08-24 用户最新裁决 C：随机强化 +30/+60/+100，权重 50/30/20。",
  resolvedBy: "用户当前对话明确裁决",
  resolvedAt: "2026-08-24T00:00:00+08:00",
  closureEvidenceRefs: ["SYS-OUT-GR-09-EV27"],
  approvalStatus: "APPROVED_TARGET",
  decisionStatus: "HUMAN_DECISION_CONFIRMED",
  implementationStatus: "WORKING_COPY_ALIGNED_UNKNOWN_LIVE"
});
const rvEx = rv.exceptions.find(x => x.id === "SYS-OUT-GR-09-EX01");
rvEx.name = "强化结果档裁决已关闭";
rvEx.status = "RESOLVED_BY_HUMAN_DECISION";
rvEx.rule = "最新权威规则为 +30/+60/+100，权重50/30/20；被替代口径仅见 archive/legacy-output-20260824。";
rv.evidence = rv.evidence.filter(item => item.id !== "SYS-OUT-GR-09-EV27");
rv.evidence.push({
  id: "SYS-OUT-GR-09-EV27", kind: "human-decision", label: "2026-08-24 房车随机强化 C 裁决",
  path: "knowledge-base/governance/rulings.json", location: "RULING-RV-C", status: "HUMAN_DECISION_CONFIRMED"
});
rv.statusAxes = rv.statusAxes.filter(item => item.axis !== "最新规则裁决");
rv.statusAxes.push({ axis: "最新规则裁决", value: "C：随机强化 +30/+60/+100；权重50/30/20", status: "HUMAN_DECISION_CONFIRMED", note: "工作副本配置/代码观察与目标规则一致；LIVE仍需发布证据。" });

const ew = byId["SYS-OUT-GR-10"];
ew.revision = "2026-08-24.2";
ew.updatedAt = today;
ew.statusAxes[0] = { axis: "系统身份", value: "迁移兼容系统", status: "APPROVED_COMPATIBILITY_MIGRATION", note: "专武向收容物迁移，保留一个大版本兼容迁移期；兼容期起止版本和运行状态仍需发布台账。" };
ew.statusAxes[1] = { axis: "目标设计", value: "B：一个大版本兼容迁移期", status: "HUMAN_DECISION_CONFIRMED_IMPLEMENTATION_PENDING", note: "旧专武表、入口和数据在兼容期内的读写边界需实施方案；被替代方案只保留于归档。" };
ew.statusAxes[3].value = "兼容迁移期已裁决；生效版本与LIVE状态待发布证据";
ew.statusAxes[3].note = "人工裁决确定兼容期长度，不证明工作副本或Production/LIVE已切换。";
ew.statusAxes[4] = { axis: "人工裁决", value: "B=保留一个大版本的兼容迁移期", status: "HUMAN_DECISION_CONFIRMED_IMPLEMENTATION_PENDING", note: "权威证据：knowledge-base/governance/rulings.json#RULING-EW-B。" };
const ewQ = ew.openQuestions.find(x => x.id === "SYS-OUT-GR-10-Q01");
ewQ.question = "专武向收容物迁移采用哪种兼容策略？";
ewQ.answer = "2026-08-24 用户最新裁决 B：保留一个大版本的兼容迁移期。";
ewQ.resolvedBy = "用户当前对话明确裁决";
ewQ.resolvedAt = "2026-08-24T00:00:00+08:00";
ewQ.closureEvidenceRefs = ["SYS-OUT-GR-10-EV17"];
ewQ.approvalStatus = "APPROVED_TARGET";
ewQ.decisionStatus = "HUMAN_DECISION_CONFIRMED";
ewQ.implementationStatus = "IMPLEMENTATION_PENDING";
const ewDecision = ew.humanDecisions.find(x => x.cardId === "DC-A");
Object.assign(ewDecision, {
  selectedOptionId: 2,
  selectedOptionName: "B：一个大版本兼容期",
  approvedTarget: "专武向收容物迁移，并保留一个大版本的兼容迁移期。",
  confirmedAt: "2026-08-24T00:00:00+08:00",
  implementationNote: "兼容期起止版本、读写边界、数据迁移、旧表/入口/投放清理尚未实施。",
  evidenceRef: "SYS-OUT-GR-10-EV17",
  evidencePath: "knowledge-base/governance/rulings.json"
});
const ewR3 = ew.rules.find(x => x.id === "SYS-OUT-GR-10-R03");
ewR3.name = "专武→收容物兼容迁移策略";
ewR3.status = "HUMAN_DECISION_CONFIRMED_IMPLEMENTATION_PENDING";
ewR3.targetRule = "采用 B：专武向收容物迁移，并保留一个大版本的兼容迁移期。兼容期起止版本、旧数据读写、入口展示与最终清理点由实施方案和发布台账补齐。";
const ewR5 = ew.rules.find(x => x.id === "SYS-OUT-GR-10-R05");
ewR5.status = "APPROVED_COMPATIBILITY_MIGRATION_PENDING";
ewR5.targetRule = "专武抽卡、经验副本、材料、商店与任务在一个大版本兼容迁移期内保持兼容；具体读写和投放边界待实施方案，不得推导为长期并存或已立即下线。";
const ewEx = ew.exceptions.find(x => x.id === "SYS-OUT-GR-10-EX01");
ewEx.name = "专武→收容物兼容迁移策略已裁决";
ewEx.status = "HUMAN_DECISION_CONFIRMED_IMPLEMENTATION_PENDING";
ewEx.rule = "最新裁决 B：保留一个大版本的兼容迁移期；剩余缺口是实施边界与发布证据，不再是方向未裁决。";
ew.evidence = ew.evidence.filter(item => item.id !== "SYS-OUT-GR-10-EV17");
ew.evidence.push({ id: "SYS-OUT-GR-10-EV17", kind: "human-decision", label: "2026-08-24 专武兼容迁移 B 裁决", path: "knowledge-base/governance/rulings.json", location: "RULING-EW-B", status: "HUMAN_DECISION_CONFIRMED" });

const containment = byId["SYS-OUT-GR-05"];
containment.statusAxes[0] = { axis: "系统身份", value: "专武迁移目标系统", status: "APPROVED_TARGET_WITH_COMPATIBILITY_PERIOD", note: "迁移方向已确认，并保留一个大版本兼容迁移期；具体实施与LIVE待证据。" };
const cRule = containment.rules.find(x => x.id === "SYS-OUT-GR-05-R01");
cRule.status = "APPROVED_TARGET_IMPLEMENTATION_PENDING";
cRule.targetRule = "收容物是专武迁移目标；迁移采用一个大版本兼容期。兼容期内旧专武与收容物的表/入口/数据读写边界必须由实施方案明确，不能写成长线双轨，也不能写成迁移已完成。";
const cQ = containment.openQuestions.find(x => x.id === "SYS-OUT-GR-05-Q01");
cQ.question = "一个大版本兼容迁移期的起止版本、数据迁移和读写边界是什么？";
cQ.impact = "迁移方向与期限已裁决；剩余问题影响ExclWeapon表、ItemSubType、抽卡/养成/商店/任务的具体实施。";
cQ.resolutionOwner = "RUNTIME_OWNER";
cQ.lifecycle = "OPEN";
const cEx = containment.exceptions.find(x => x.id === "SYS-OUT-GR-05-EX04");
cEx.name = "专武→收容物兼容迁移实施缺口";
cEx.status = "IMPLEMENTATION_PENDING";
cEx.rule = "迁移策略已裁决为一个大版本兼容期；当前表/类型复用是兼容期实施证据与风险，只表示实施边界与 LIVE 状态待补证。";

for (const detail of details) {
  for (const ev of detail.evidence || []) {
    if (typeof ev.path === "string" && ev.path.startsWith("D:\\Vgame_design\\output")) ev.path = "archive/legacy-output-20260824/manifest.json";
    if (typeof ev.path === "string" && ev.path.startsWith("D:\\Vgame_design\\design\\")) ev.path = ev.path.replace("D:\\Vgame_design\\", "").replaceAll("\\", "/");
    if (typeof ev.path === "string") ev.path = ev.path.replaceAll("\\", "/");
    if (typeof ev.path === "string" && ev.path.startsWith("archive/legacy-output-20260824/")) {
      const legacyRelative = ev.path.slice("archive/legacy-output-20260824/".length);
      const source = path.join(legacyRoot, ...legacyRelative.split("/"));
      const target = path.join(repoRoot, ...ev.path.split("/"));
      if (fs.existsSync(source) && !fs.existsSync(target)) {
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.copyFileSync(source, target);
      }
    }
    if (typeof ev.path === "string" && ev.path.startsWith("design/")) {
      const target = path.join(repoRoot, ...ev.path.split("/"));
      const source = path.join(path.resolve(legacyRoot, "..", ".."), ...ev.path.split("/"));
      if (fs.existsSync(source) && !fs.existsSync(target)) {
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.copyFileSync(source, target);
      }
    }
  }
  writeJson(path.join(detailsDir, `${detail.systemId}.json`), detail);
}

model.systems.find(x => x.id === "SYS-OUT-GR-09").status = "规则已裁决 / UNKNOWN_LIVE";
model.systems.find(x => x.id === "SYS-OUT-GR-09").summary = "账号级养成底盘；随机强化采用+30/+60/+100，权重50/30/20。";
model.systems.find(x => x.id === "SYS-OUT-GR-10").status = "兼容迁移已裁决 / IMPLEMENTATION_PENDING";
model.systems.find(x => x.id === "SYS-OUT-GR-10").summary = "专武向收容物迁移，保留一个大版本兼容迁移期；实施和LIVE状态待证据。";
model.systems.find(x => x.id === "SYS-OUT-GR-05").status = "迁移目标已裁决 / IMPLEMENTATION_PENDING";
writeJson(modelPath, model);

const legacyDecision = readJson(path.join(repoRoot, "archive", "legacy-output-20260824", "registries", "decision-card-registry.json"));
const dcA = legacyDecision.cards.find(x => x.id === "DC-A");
dcA.theme = "专武→收容物兼容迁移策略";
dcA.options = [
  { id: 1, name: "A：立即迁移", description: "不保留跨版本兼容期，实施风险最高。" },
  { id: 2, name: "B：一个大版本兼容期", description: "保留一个大版本兼容迁移期。" },
  { id: 3, name: "C：长期并存（未采用）", description: "未采用方案，原始措辞见归档决策证据。" }
];
dcA.selectedOptionId = 2;
dcA.selectedOptionName = "B：一个大版本兼容期";
dcA.aiRecommendation = "已按用户裁决选择 B：保留一个大版本兼容迁移期；实施时冻结起止版本、读写边界和数据迁移方案。";
dcA.approvedTarget = "专武向收容物迁移，并保留一个大版本的兼容迁移期。";
dcA.confirmedAt = "2026-08-24T00:00:00+08:00";
dcA.implementationNote = "兼容期起止版本、读写边界、数据迁移与最终清理仍待实施。";
dcA.decisionEvidence = { path: "knowledge-base/governance/rulings.json", rulingId: "RULING-EW-B" };
legacyDecision.decisionImport.confirmedAt = "2026-08-24T00:00:00+08:00";
legacyDecision.decisionImport.sourcePath = "knowledge-base/governance/rulings.json";
writeJson(path.join(kbRoot, "registries", "decision-card-registry.json"), legacyDecision);

writeJson(path.join(kbRoot, "governance", "rulings.json"), {
  schema: "vgame-human-rulings/v1",
  version: "1.0.0",
  rulings: [
    {
      rulingId: "RULING-RV-C", systemIds: ["SYS-OUT-GR-09"], decisionLabel: "C",
      decision: "房车采用随机强化 +30/+60/+100，权重 50/30/20。",
      status: "HUMAN_DECISION_CONFIRMED", implementationStatus: "WORKING_COPY_ALIGNED_UNKNOWN_LIVE", decidedAt: today,
      supersedesEvidenceRefs: ["ARCHIVE-RV-PRE-C-01", "ARCHIVE-RV-PRE-C-02"]
    },
    {
      rulingId: "RULING-EW-B", systemIds: ["SYS-OUT-GR-10", "SYS-OUT-GR-05"], decisionLabel: "B",
      decision: "专武向收容物迁移，并保留一个大版本的兼容迁移期。",
      status: "HUMAN_DECISION_CONFIRMED", implementationStatus: "IMPLEMENTATION_PENDING", decidedAt: today,
      unknowns: ["兼容期起止版本", "旧数据读写边界", "入口与投放切换点", "最终清理版本"],
      supersedesEvidenceRefs: ["ARCHIVE-EW-PRE-B-01", "ARCHIVE-EW-PRE-B-02", "ARCHIVE-EW-PRE-B-03"]
    }
  ]
});

const evidence = [];
for (const detail of details) for (const ev of detail.evidence || []) evidence.push({ ...ev, systemId: detail.systemId });
writeJson(path.join(kbRoot, "evidence", "evidence-registry.json"), {
  schema: "vgame-evidence-registry/v1", count: evidence.length, evidence
});
const ioSystems = details.map(d => ({
  systemId: d.systemId,
  name: d.name,
  inputs: d.overview?.inputs || [],
  outputs: d.overview?.outputs || [],
  dependencies: (d.relationships || []).map(r => ({ type: r.type, targetId: r.targetId, status: r.status, provenance: r.provenance }))
}));
writeJson(path.join(kbRoot, "registries", "system-io-dependency-map.json"), {
  schema: "vgame-system-io-dependency/v1",
  systems: ioSystems,
  loops: [
    { id: "LOOP-CORE", name: "核心战斗循环", path: ["进入玩法", "战斗推进", "胜负结算", "奖励入账", "再次挑战"] },
    { id: "LOOP-GROWTH", name: "成长验证循环", path: ["玩法产出", "资源入账", "养成消耗", "战力转化", "验证玩法"] },
    { id: "LOOP-ECONOMY", name: "经济循环", path: ["来源", "库存", "消耗", "成长/兑换", "新需求"] },
    { id: "LOOP-RETENTION", name: "留存运营循环", path: ["日周赛季目标", "参与", "奖励", "进度推进", "下一周期"] }
  ]
});

writeJson(path.join(kbRoot, "AUTHORITY.json"), {
  schema: "vgame-knowledge-authority/v1",
  repository: repoRoot.replace(/\\/g, "/"),
  formalEntry: "knowledge-base/README.md",
  canonicalContentRoot: "knowledge-base/",
  skillSourceRoot: "skills/",
  generatedOutputRoot: "output/knowledge-framework/",
  archiveRoot: "archive/",
  rule: "只有 formalEntry 是正式权威入口；output 不得作为正文源。"
});

const docs = {
  "README.md": `# Vgame 项目级策划知识框架 V1.0\n\n> **唯一正式权威入口。** 正文位于本目录；Skill 正文只位于 \`../skills/\`；\`../output/\` 仅含可重新生成的网页、索引、切片和报告。\n\n## 阅读顺序\n\n1. [项目总览与核心循环](framework/00-项目总览与核心循环.md)\n2. [系统框架](framework/10-系统框架.md)\n3. [战斗规则、角色与内容](framework/20-战斗规则角色与内容.md)\n4. [数值框架 V2](framework/30-数值框架V2.md)\n5. [系统输入、输出、依赖和循环](framework/40-系统关系.md)\n6. [Skill 注册与调用层](framework/50-Skill注册与调用.md)\n7. [证据、状态、裁决与治理](framework/90-证据状态裁决与治理.md)\n\n机器入口：\`AUTHORITY.json\`、\`registries/skill-registry.json\`、\`mappings/*.json\`。\n\n重建：\`pwsh -File scripts/knowledge-framework/rebuild.ps1\`。终验必须由独立审核对话执行。\n`,
  "framework/00-项目总览与核心循环.md": `# 项目总览与核心循环\n\nVgame 是 5 人小队养成驱动的跑酷战斗射击游戏：普通攻击与技能自动释放，玩家把握必杀时机；地形、遭遇节奏、有效输出时间和环境适配共同决定战斗表现。\n\n核心循环：\`进入玩法 → 战斗推进 → 胜负结算 → 奖励入账 → 养成转化 → 更高难度验证\`。主线承担推进、教学和开放；稳定供给玩法提供资源；养成系统把资源转成属性、机制和阵容宽度；验证玩法检查真实战斗转化。\n`,
  "framework/10-系统框架.md": `# 系统框架\n\n系统分为战斗内与战斗外。战斗内覆盖实例、单位、技能/Buff、敌人/AI/Boss、空间遭遇、玩法局内规则、UI反馈与胜负结算。战斗外分为玩法、养成、经济资源、商业化、周边运营与辅助系统。\n\n45 个系统的原子正文位于 \`system-details/\`，目录与状态位于 \`registries/knowledge-model.json\`。系统级结论必须同时保留目标设计、工作副本观察、LIVE状态与证据来源。\n`,
  "framework/20-战斗规则角色与内容.md": `# 战斗规则、角色设计与战斗内容\n\n战斗规则负责状态机、单位阵营、技能/Buff/效果、胜负和结算触发；角色设计负责定位、普通/自动/必杀/天赋循环与成长挂接；战斗内容负责怪物、Boss、AI、波次、子弹、召唤物、机关、地形与遭遇节奏。\n\n专业正文：\`domains/M01-战斗专业正文.md\`。精确配置与运行时结论必须按需调用对应 Skill 并回源。\n`,
  "framework/30-数值框架V2.md": `# 数值框架 V2\n\n数值框架分为共享底座、养成、战斗、经济、节奏和配置交付六域。任何数值结论必须写明目标体验、公式/参数、输入来源、输出消费者、风险边界和验证方法。\n\n专业正文：\`domains/M02-数值框架v2专业正文.md\`。房车最新规则为 +30/+60/+100、权重50/30/20；专武迁移保留一个大版本兼容期，具体版本边界仍待实施。\n`,
  "framework/40-系统关系.md": `# 系统输入、输出、依赖和循环\n\n机器可读关系位于 \`registries/system-io-dependency-map.json\`。每个系统登记 inputs、outputs、typed dependencies 与 provenance。四条核心循环为：核心战斗、成长验证、经济、留存运营。跨系统推导必须标 \`CROSS_SOURCE_SYNTHESIS\`，不得冒充原文明确。\n`,
  "framework/50-Skill注册与调用.md": `# Skill 注册与调用层\n\n33 个 Skill 的唯一正文位于 \`../skills/<skillId>/SKILL.md\`；知识库只登记元数据和映射，不复制全文。查询先走 \`vgame-knowledge-router\`，再按 \`mappings/question-to-skill.json\` 与 \`mappings/system-to-skill.json\` 加载最小 Skill 和知识包。\n\n注册字段覆盖 skillId、分类、职责、触发条件、输入、输出、覆盖系统、依赖 Skill、证据来源、交付门禁和版本状态。\n`,
  "framework/90-证据状态裁决与治理.md": `# 证据、状态、人工裁决与治理\n\n来源性质：SOURCE_EXPLICIT、WORKING_COPY_OBSERVED、CROSS_SOURCE_SYNTHESIS、DESIGN_PROPOSAL、UNKNOWN。工作副本、配置镜像和 Production/LIVE 不可混写。\n\n最新人工裁决以 \`governance/rulings.json\` 为权威：房车 C（+30/+60/+100，50/30/20）；专武 B（一个大版本兼容迁移期）。旧结论只允许出现在 \`archive/\` 且必须标 SUPERSEDED。\n\n发布规则：先在隔离输出重建并运行全部门禁；自动门禁通过只代表结构就绪，最终验收由独立审核对话完成。\n`
};
for (const [name, text] of Object.entries(docs)) writeText(path.join(kbRoot, name), text);

const designFiles = fs.readdirSync(path.join(repoRoot, "design"), { withFileTypes: true })
  .filter(x => x.isFile() && x.name.endsWith(".md"))
  .slice(0, 40)
  .map(x => {
    const p = path.join(repoRoot, "design", x.name);
    return { sourcePath: rel(p), sourceSha256: sha256(fs.readFileSync(p, "utf8").replace(/\r\n/g, "\n")) };
  });
const legacyFramework = readJson(path.join(repoRoot, "archive", "legacy-output-20260824", "registries", "project-planning-framework-legacy.json"));
writeJson(path.join(kbRoot, "registries", "project-planning-framework.json"), {
  ...legacyFramework,
  schema: "vgame-project-planning-framework/v1.0",
  updatedAt: today,
  frameworkNodes,
  documents: designFiles
});

const walk = root => {
  const rows = [];
  const visit = current => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const p = path.join(current, entry.name);
      if (entry.isDirectory()) visit(p);
      else {
        const data = fs.readFileSync(p);
        const relative = path.relative(root, p).replaceAll("\\", "/");
        const generated = /(^|\/)(system-chunks|module-chunks|system-details|systems)(\/|$)|knowledge-model\.js$|knowledge-search-index\.js$|router-manifest\.json$|index\.html$|preview\.png$|validation-report\.json$/.test(relative);
        const evidenceLike = /^(review|决策卡|evidence)\//.test(relative) || /(^|\/)(HANDOFF|最终返工|待裁决|status-conflict|project-evidence)/.test(relative);
        rows.push({ path: relative, size: data.length, sha256: sha256(data), classification: generated ? "REGENERATABLE" : evidenceLike ? "ARCHIVE_EVIDENCE" : "LEGACY_SOURCE", disposition: generated ? "REBUILD_NOT_COPY" : "TRACE_IN_ARCHIVE" });
      }
    }
  };
  if (fs.existsSync(root)) visit(root);
  return rows;
};
const legacyFiles = walk(legacyRoot);
writeJson(path.join(repoRoot, "archive", "legacy-output-20260824", "manifest.json"), {
  schema: "vgame-legacy-archive-manifest/v1", sourceRoot: legacyRoot.replaceAll("\\", "/"), capturedAt: today,
  rule: "旧 output 仅作证据；REGENERATABLE 不复制，ARCHIVE_EVIDENCE/LEGACY_SOURCE 通过本清单与已复制文档追溯。",
  fileCount: legacyFiles.length, files: legacyFiles
});

console.log(JSON.stringify({ skills: skills.length, systems: model.systems.length, frameworkNodes: frameworkNodes.length, evidence: evidence.length, legacyFiles: legacyFiles.length }, null, 2));
