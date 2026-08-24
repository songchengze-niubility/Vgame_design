// 负例回归测试：把坏数据注入知识库临时副本，运行 validate-knowledge-base.mjs，
// 断言每个目标检查真正失败（而不是只看整体 exit code）。
// 用法: node tests/validate-negative.test.mjs   （在 knowledge-base/ 下运行）
import fs from "node:fs";
import path from "node:path";
import cp from "node:child_process";
import os from "node:os";
import { fileURLToPath } from "node:url";

const KB = path.dirname(fileURLToPath(import.meta.url)); // .../knowledge-base/tests
const kbRoot = path.dirname(KB);                          // .../knowledge-base
const FRAMEWORK_ROOT = path.dirname(kbRoot);              // .../项目级策划知识框架
const nodeBin = process.execPath;

// 手动递归复制（此环境下 fs.cpSync 递归复制会触发原生崩溃，改用 copyFileSync 循环）
function copyTree(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (entry.isDirectory()) copyTree(path.join(src, entry.name), path.join(dest, entry.name));
    else fs.copyFileSync(path.join(src, entry.name), path.join(dest, entry.name));
  }
}

function copyKB(dest) {
  fs.mkdirSync(path.join(dest, "knowledge-base"), { recursive: true });
  for (const entry of fs.readdirSync(kbRoot, { withFileTypes: true })) {
    if (["node_modules", "tests", "npmcache"].includes(entry.name)) continue;
    const src = path.join(kbRoot, entry.name);
    const target = path.join(dest, "knowledge-base", entry.name);
    if (entry.isDirectory()) copyTree(src, target);
    else fs.copyFileSync(src, target);
  }
  for (const file of ["00-workflow-state.json", "HANDOFF.md", "待裁决清单.md", "06-review.md", "最终返工完成报告.md"]) {
    fs.copyFileSync(path.join(FRAMEWORK_ROOT, file), path.join(dest, file));
  }
  // 复制 framework JSON（用于 source-document-hashes 检查）
  const frameworkJsonPath = path.join(FRAMEWORK_ROOT, "project-planning-framework.json");
  if (fs.existsSync(frameworkJsonPath)) fs.copyFileSync(frameworkJsonPath, path.join(dest, "project-planning-framework.json"));
}

function readJSON(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }
function writeJSON(p, data) { fs.writeFileSync(p, JSON.stringify(data, null, 2) + "\n", "utf8"); }
function readText(p) { return fs.readFileSync(p, "utf8"); }
function writeText(p, s) { fs.writeFileSync(p, s, "utf8"); }

// 每个负例：mutate(tmpRoot) 注入坏数据；expectCheck 为必须失败的检查名；expectDetail 为失败详情需包含的片段
const NEGATIVE_CASES = [
  {
    name: "N01 缺少顶层 contractRefs",
    expectCheck: "system-detail-contract-refs-field",
    expectDetail: "missing-top-level-contractRefs",
    mutate: t => { const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GR-06.json"); const d = readJSON(p); delete d.contractRefs; writeJSON(p, d); }
  },
  {
    name: "N02 contractRefs.ruleRefs 指向其他正文原子",
    expectCheck: "system-detail-contract-refs-namespace",
    expectDetail: "foreign-ruleRef",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GR-05.json");
      const d = readJSON(p);
      d.contractRefs[0].ruleRefs = ["SYS-OUT-GR-10-R02"];
      writeJSON(p, d);
    }
  },
  {
    name: "N03 relationship.evidenceRefs 指向外部正文证据（provenance=UNKNOWN 不得绕过）",
    expectCheck: "system-detail-relationship-evidence",
    expectDetail: "foreign-evidenceRef",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GR-05.json");
      const d = readJSON(p);
      const rel = d.relationships.find(r => r.id === "SYS-OUT-GR-05-REL02");
      rel.evidenceRefs = ["SYS-OUT-GR-10-EV07"];
      writeJSON(p, d);
    }
  },
  {
    name: "N04 CROSS_SOURCE_SYNTHESIS 无推导边界",
    expectCheck: "system-detail-synthesis-boundary",
    expectDetail: "missing-synthesis-boundary",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GR-05.json");
      const d = readJSON(p);
      const rel = d.relationships.find(r => r.id === "SYS-OUT-GR-05-REL03");
      rel.provenance = "CROSS_SOURCE_SYNTHESIS";
      rel.description = "两系统有供给关系。";
      writeJSON(p, d);
    }
  },
  {
    name: "N05 M01 工作包回到 planned",
    expectCheck: "work-package-waves-complete",
    expectDetail: "M01:planned",
    mutate: t => {
      const p = path.join(t, "knowledge-base/work-packages.json");
      const d = readJSON(p);
      d.packages.find(x => x.id === "M01").status = "planned";
      writeJSON(p, d);
    }
  },
  {
    name: "N06 Markdown 与 canonical 内容漂移",
    expectCheck: "generated-markdown-deep-equal",
    expectDetail: "content-drift",
    mutate: t => {
      const p = path.join(t, "knowledge-base/systems/SYS-OUT-GP-01-主线.md");
      writeText(p, readText(p) + "\n<!-- tampered -->\n");
    }
  },
  {
    name: "N07 search index 内容漂移（ID 不变、summary 篡改）",
    expectCheck: "deterministic-build-hash",
    mutate: t => {
      const p = path.join(t, "knowledge-base/knowledge-search-index.js");
      const s = readText(p);
      const marker = "window.VGAME_KB_SEARCH = ";
      const jsonStart = s.indexOf(marker) + marker.length;
      const jsonEnd = s.lastIndexOf(";");
      const entries = JSON.parse(s.slice(jsonStart, jsonEnd).trim());
      entries[0].summary = "被篡改的摘要。"; // ID 不变、内容漂移
      writeText(p, s.slice(0, jsonStart) + JSON.stringify(entries, null, 2) + s.slice(jsonEnd));
    }
  },
  {
    name: "N08 workflow 存在未来事件",
    expectCheck: "workflow-timeline-consistent",
    expectDetail: "future",
    mutate: t => {
      const p = path.join(t, "00-workflow-state.json");
      const d = readJSON(p);
      d.history.push({ at: "2099-01-01T00:00:00.000000+00:00", actor: "test", phase: "review", outcome: "success", next_action: "x", evidence: "x" });
      writeJSON(p, d);
    }
  },
  {
    name: "N08b workflow 事件乱序",
    expectCheck: "workflow-timeline-consistent",
    expectDetail: "out-of-order",
    mutate: t => {
      const p = path.join(t, "00-workflow-state.json");
      const d = readJSON(p);
      const first = d.history[0];
      d.history[0] = { ...d.history[d.history.length - 1] };
      d.history[d.history.length - 1] = first;
      writeJSON(p, d);
    }
  },
  {
    name: "N09 HANDOFF 统计与 canonical 不一致（旧口径回流）",
    expectCheck: "handoff-stats-consistent",
    expectDetail: "stale",
    mutate: t => {
      const p = path.join(t, "HANDOFF.md");
      const s = readText(p);
      writeText(p, s.replace(/36 P0 \/ 127 P1 \/ 77 P2/g, "33 P0 / 122 P1 / 69 P2").replace(/240/g, "224"));
    }
  },
  {
    name: "N10 生成物 chunk 与 canonical deep equality 失败",
    expectCheck: "generated-chunks-match-canonical",
    expectDetail: "content-drift",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-chunks/SYS-OUT-GP-01.js");
      writeText(p, readText(p).replace('"purpose": "', '"purpose": "被篡改 '));
    }
  },
  {
    name: "N11 模块正文 anchor 漂移（M01 与 md 脱钩）",
    expectCheck: "module-details-sections",
    expectDetail: "anchor-missing",
    mutate: t => {
      const p = path.join(t, "knowledge-base/module-details/M01.json");
      const d = readJSON(p);
      d.sections[1].anchor = "## 1. 不存在的章节";
      writeJSON(p, d);
    }
  },
  {
    name: "N12 L1 目录状态与详情运行轴矛盾（GP09 写回「未开放」）",
    expectCheck: "l1-status-consistent-with-details",
    expectDetail: "UNKNOWN_LIVE",
    mutate: t => {
      const p = path.join(t, "knowledge-base/knowledge-model.json");
      const d = readJSON(p);
      d.systems.find(s => s.id === "SYS-OUT-GP-09").status = "未开放";
      writeJSON(p, d);
    }
  },
  // ===== 2026-08-20 新增负例 =====
  {
    name: "N13 P0 问题缺少 decisionCardId 或 resolutionOwner",
    expectCheck: "p0-question-classification",
    expectDetail: "no-decisionCardId-or-resolutionOwner",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GP-01.json");
      const d = readJSON(p);
      // 找到一个 P0 问题并删除其 decisionCardId/resolutionOwner
      const p0 = (d.openQuestions || []).find(q => q.priority === "P0");
      if (p0) { delete p0.decisionCardId; delete p0.resolutionOwner; }
      writeJSON(p, d);
    }
  },
  {
    name: "N14 决策卡注册表缺失",
    expectCheck: "decision-card-registry",
    expectDetail: "registry-missing",
    mutate: t => {
      fs.unlinkSync(path.join(t, "knowledge-base/decision-card-registry.json"));
    }
  },
  {
    name: "N15 决策卡数量超出范围（少于14张）",
    expectCheck: "decision-card-registry",
    expectDetail: "card-count",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      d.cards = d.cards.slice(0, 10); // 只有10张
      writeJSON(p, d);
    }
  },
  {
    name: "N16 原子 questionRefs 指向已删除问题",
    expectCheck: "atom-question-refs-resolve",
    expectDetail: "dangling-questionRef",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GP-01.json");
      const d = readJSON(p);
      // 在某个规则的 questionRefs 中引用不存在的问题 ID
      if (d.rules && d.rules[0]) {
        d.rules[0].questionRefs = ["SYS-OUT-GP-01-FAKE-Q99"];
      }
      writeJSON(p, d);
    }
  },
  {
    name: "N17 源文档哈希漂移（框架门禁）",
    expectCheck: "source-document-hashes",
    expectDetail: "hash-drift",
    mutate: t => {
      // 复制一个 design 文件到临时目录，使文件存在但哈希不匹配
      const frameworkPath = path.join(t, "project-planning-framework.json");
      if (!fs.existsSync(frameworkPath)) return;
      const d = readJSON(frameworkPath);
      if (!d.documents || !d.documents[0]) return;
      const doc = d.documents[0];
      // 创建 design 目录并复制文件
      const designDir = path.join(t, "design");
      fs.mkdirSync(designDir, { recursive: true });
      const srcPath = path.join(FRAMEWORK_ROOT, "..", "design", path.basename(doc.sourcePath));
      if (fs.existsSync(srcPath)) {
        fs.copyFileSync(srcPath, path.join(t, ...doc.sourcePath.split("/")));
      } else {
        // 如果源文件不存在，创建一个空文件
        fs.writeFileSync(path.join(t, ...doc.sourcePath.split("/")), "test content");
      }
      // 修改哈希为错误值
      doc.sourceSha256 = "0000000000000000000000000000000000000000000000000000000000000000";
      writeJSON(frameworkPath, d);
    }
  },
  {
    name: "N18 M02 宣称45映射但结构化映射不足45",
    expectCheck: "m02-mapping-claim-consistent",
    expectDetail: "claims-45-but-mapped",
    mutate: t => {
      const p = path.join(t, "knowledge-base/module-details/M02.json");
      const d = readJSON(p);
      // 恢复旧的"45 系统真实映射"声明
      d.overview.inScope[0] = "45 系统的真实引用映射（行级/域级深度区分，见 §0.5）";
      d.sections.find(s => s.id === "M02-S05").summary = "NUM 域×45 系统真实引用映射，行级与域级深度区分。";
      // 同时删除部分 crossRefs systemIds 使结构化映射不足 45
      for (const ref of (d.crossRefs || [])) {
        if (ref.systemIds && ref.systemIds.length > 10) {
          ref.systemIds = ref.systemIds.slice(0, ref.systemIds.length - 5);
        }
      }
      writeJSON(p, d);
    }
  },
  {
    name: "N19 网页 moduleRegistry 缺失",
    expectCheck: "web-module-registry",
    expectDetail: "count-mismatch",
    mutate: t => {
      // 删除生成的 knowledge-model.js 中的 moduleRegistry
      const p = path.join(t, "knowledge-base/knowledge-model.js");
      const s = readText(p);
      // 破坏 moduleRegistry 字段
      const tampered = s.replace('"moduleRegistry":', '"moduleRegistry_REMOVED":');
      writeText(p, tampered);
    }
  },
  {
    name: "N20 relationTypes 缺少 migrates-to",
    expectCheck: "relation-types-includes-migrates-to",
    expectDetail: "migrates-to-missing",
    mutate: t => {
      const p = path.join(t, "knowledge-base/knowledge-model.json");
      const d = readJSON(p);
      d.relationTypes = d.relationTypes.filter(r => r[0] !== "migrates-to");
      writeJSON(p, d);
    }
  },
  {
    name: "N21 修改 M01 正文但保留 anchor",
    expectCheck: "module-details-sections",
    mutate: t => {
      const p = path.join(t, "knowledge-base/M01-战斗专业正文.md");
      const s = readText(p);
      // 保留所有 anchor（## 0.、## 1. 等），但修改正文内容
      writeText(p, s.replace(/战斗规则/g, "被篡改的内容"));
    }
  },
  {
    name: "N22 最终报告写错误统计",
    expectCheck: "handoff-stats-consistent",
    expectDetail: "stale",
    mutate: t => {
      const p = path.join(t, "最终返工完成报告.md");
      const s = readText(p);
      writeText(p, s.replace(/36 P0 \/ 127 P1 \/ 77 P2/g, "33 P0 / 122 P1 / 69 P2").replace(/240/g, "224"));
    }
  },
  {
    name: "N23 决策卡 closeableQuestionId 使用短ID（非canonical格式）",
    expectCheck: "decision-card-registry",
    expectDetail: "not-canonical-format",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      // 将 DC-A 的第一个 closeableQuestionId 改回短ID
      if (d.cards[0] && d.cards[0].closeableQuestionIds[0]) {
        d.cards[0].closeableQuestionIds[0] = "GR-10-Q01";
      }
      writeJSON(p, d);
    }
  },
  {
    name: "N24 决策卡 closeableQuestionId 引用不存在的问题",
    expectCheck: "decision-card-registry",
    expectDetail: "not-found-in-openQuestions",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      // 将 DC-A 的第一个 closeableQuestionId 改为不存在的 canonical ID
      if (d.cards[0] && d.cards[0].closeableQuestionIds[0]) {
        d.cards[0].closeableQuestionIds[0] = "SYS-OUT-GR-10-Q99";
      }
      writeJSON(p, d);
    }
  },
  {
    name: "N25 决策卡 closeableQuestionId 双向不一致（question未指回卡片）",
    expectCheck: "decision-card-registry",
    expectDetail: "decisionCardId-mismatch",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      // 将 SYS-OUT-GR-10-Q01 从 DC-A 移到 DC-B
      // 该问题 decisionCardId=DC-A，放入 DC-B 会导致 mismatch
      const dcA = d.cards.find(c => c.id === "DC-A");
      const dcB = d.cards.find(c => c.id === "DC-B");
      if (dcA && dcB) {
        dcA.closeableQuestionIds = dcA.closeableQuestionIds.filter(id => id !== "SYS-OUT-GR-10-Q01");
        dcB.closeableQuestionIds.push("SYS-OUT-GR-10-Q01");
      }
      writeJSON(p, d);
    }
  },
  {
    name: "N26 P0问题有decisionCardId但不在对应卡的closeableQuestionIds中",
    expectCheck: "decision-card-registry",
    expectDetail: "not-in-closeableQuestionIds",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      // 从 DC-B 中移除其唯一 canonical 问题。
      const dcB = d.cards.find(c => c.id === "DC-B");
      if (dcB && dcB.closeableQuestionIds) {
        dcB.closeableQuestionIds = dcB.closeableQuestionIds.filter(
          id => id !== "SYS-OUT-SU-05-Q01"
        );
      }
      writeJSON(p, d);
    }
  },
  {
    name: "N27 P1问题缺少 decisionCardId 或 resolutionOwner",
    expectCheck: "p1p2-question-classification",
    expectDetail: "no-decisionCardId-or-resolutionOwner",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GP-01.json");
      const d = readJSON(p);
      // 找到一个 P1 问题并删除其 decisionCardId/resolutionOwner
      const p1 = (d.openQuestions || []).find(q => q.priority === "P1");
      if (p1) { delete p1.decisionCardId; delete p1.resolutionOwner; }
      writeJSON(p, d);
    }
  },
  {
    name: "N28 决策卡问题被错误分给非人工 owner",
    expectCheck: "decision-card-registry",
    expectDetail: "non-human-owner-with-card",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GR-10.json");
      const d = readJSON(p);
      const q = (d.openQuestions || []).find(item => item.id === "SYS-OUT-GR-10-Q01");
      if (q) q.resolutionOwner = "RUNTIME_OWNER";
      writeJSON(p, d);
    }
  },
  {
    name: "N29 关系缺少显式 provenance",
    expectCheck: "system-detail-relationship-provenance-valid",
    expectDetail: "missing-provenance",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-GP-01.json");
      const d = readJSON(p);
      if (d.relationships && d.relationships[0]) delete d.relationships[0].provenance;
      writeJSON(p, d);
    }
  },
  {
    name: "N30 AI_EVIDENCE 问题仍为 OPEN",
    expectCheck: "question-lifecycle-and-closure",
    expectDetail: "ai-evidence-not-closed",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-IN-06.json");
      const d = readJSON(p);
      const q = d.openQuestions.find(item => item.resolutionOwner === "AI_EVIDENCE");
      q.lifecycle = "OPEN";
      writeJSON(p, d);
    }
  },
  {
    name: "N31 P0 被错分为 DEFERRED_DETAIL",
    expectCheck: "question-lifecycle-and-closure",
    expectDetail: "p0-deferred-detail",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-OUT-SU-03.json");
      const d = readJSON(p);
      const q = d.openQuestions.find(item => item.priority === "P0" && !item.decisionCardId);
      q.resolutionOwner = "DEFERRED_DETAIL";
      writeJSON(p, d);
    }
  },
  {
    name: "N32 Design 证据关系伪标 WORKING_COPY",
    expectCheck: "system-detail-relationship-provenance-compatible",
    expectDetail: "working-copy-kind-mismatch",
    mutate: t => {
      const p = path.join(t, "knowledge-base/system-details/SYS-IN-06.json");
      const d = readJSON(p);
      const rel = d.relationships.find(item => item.evidenceRefs?.some(ref => d.evidence.find(ev => ev.id === ref)?.kind === "design-target"));
      rel.provenance = "WORKING_COPY_OBSERVED";
      writeJSON(p, d);
    }
  },
  {
    name: "N33 决策卡错绑多个 QID",
    expectCheck: "decision-card-registry",
    expectDetail: "must-close-exactly-one-question",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      d.cards.find(card => card.id === "DC-A").closeableQuestionIds.push("SYS-OUT-GR-05-Q01");
      writeJSON(p, d);
    }
  },
  {
    name: "N34 人工裁决选择指向不存在选项",
    expectCheck: "human-decision-import",
    expectDetail: "selected-option-mismatch",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      d.cards.find(card => card.id === "DC-A").selectedOptionId = 99;
      writeJSON(p, d);
    }
  },
  {
    name: "N35 人工裁决被误标为已实现/LIVE",
    expectCheck: "human-decision-import",
    expectDetail: "implementation-not-pending",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      d.cards.find(card => card.id === "DC-N").implementationStatus = "LIVE_IMPLEMENTED";
      writeJSON(p, d);
    }
  },
  {
    name: "N36 DC-E 用户评论未原样保留",
    expectCheck: "human-decision-import",
    expectDetail: "comment-not-preserved-verbatim",
    mutate: t => {
      const p = path.join(t, "knowledge-base/decision-card-registry.json");
      const d = readJSON(p);
      d.cards.find(card => card.id === "DC-E").userComment = "主线需要三星";
      writeJSON(p, d);
    }
  }
];

function runValidator(tmpRoot) {
  const script = path.join(tmpRoot, "knowledge-base", "validate-knowledge-base.mjs");
  const result = cp.spawnSync(nodeBin, [script], { encoding: "utf8", cwd: path.join(tmpRoot, "knowledge-base") });
  const reportPath = path.join(tmpRoot, "knowledge-base", "validation-report.json");
  const report = fs.existsSync(reportPath) ? readJSON(reportPath) : null;
  return { exitCode: result.status, report };
}

let failures = 0;
const base = fs.mkdtempSync(path.join(os.tmpdir(), "kb-negative-"));
for (const testCase of NEGATIVE_CASES) {
  const tmp = path.join(base, testCase.name.replace(/[^\w]/g, "_"));
  copyKB(path.join(tmp));
  testCase.mutate(tmp);
  const { exitCode, report } = runValidator(tmp);
  const errors = [];
  if (!report) errors.push("无 validation-report（validator 崩溃）");
  else {
    const target = report.checks.find(c => c.name === testCase.expectCheck);
    if (!target) errors.push(`检查不存在: ${testCase.expectCheck}`);
    else if (target.pass) errors.push(`坏数据未被发现: ${testCase.expectCheck} 仍 pass`);
    else if (testCase.expectDetail && !target.detail.includes(testCase.expectDetail)) {
      errors.push(`失败详情不含「${testCase.expectDetail}」: ${target.detail.slice(0, 120)}`);
    }
    if (exitCode !== 1) errors.push(`exit code = ${exitCode}（应为 1）`);
  }
  const status = errors.length ? "FAIL" : "PASS";
  if (errors.length) failures += 1;
  console.log(`[${status}] ${testCase.name}`);
  for (const e of errors) console.log(`      - ${e}`);
}
fs.rmSync(base, { recursive: true, force: true });
console.log(failures ? `\n${failures} 个负例未按预期失败。` : `\n全部 ${NEGATIVE_CASES.length} 个负例均使目标检查失败（坏数据会被拦截）。`);
process.exit(failures ? 1 : 0);
