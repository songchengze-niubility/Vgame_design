// 共享 Markdown 渲染：build-web-model.mjs（生成）与 validate-knowledge-base.mjs（深度一致校验）共用。
// 从 build-web-model.mjs 原样抽出，保持输出逐字节一致；修改本文件必须同时重建生成物。

export const safeFileName = name => name.replace(/[\\/:*?"<>|]/g, "-");
export const markdownRefFor = detail => `systems/${detail.systemId}-${safeFileName(detail.name)}.md`;

function bullets(items = []) {
  return items.length ? items.map(item => `- ${item}`).join("\n") : "- 暂无。";
}

export function detailMarkdown(detail, contractById) {
  const axes = (detail.statusAxes || []).map(item => `| ${item.axis} | ${item.value} | ${item.status} | ${item.note || ""} |`).join("\n");
  const guide = (detail.statusGuide || []).map(item => `| ${item.prefix} | ${item.meaning} |`).join("\n");
  const contracts = (detail.contractRefs || []).map(item => {
    const contract = contractById[item.id];
    return `| ${item.id} | ${contract?.name || "未知契约"} | ${(item.ruleRefs || []).join("、") || "待补"} |`;
  }).join("\n");
  const rules = (detail.rules || []).map(rule => [
    `### ${rule.id} ${rule.name}`,
    "",
    `- 状态：${rule.status}`,
    `- 目标规则：${rule.targetRule}`,
    `- 当前工作副本事实：${rule.sourceFact}`,
    `- 验收口径：${rule.acceptance}`,
    `- 依赖：${(rule.relatedIds || []).join("、") || "无"}`,
    `- 证据：${(rule.evidenceRefs || []).join("、") || "待补"}`,
    ""
  ].join("\n")).join("\n");
  const flow = (detail.flows || []).map(item => [
    `### ${item.id} ${item.name}`,
    "",
    (item.steps || []).map((step, index) => `${index + 1}. **${step.name}**：${step.description}`).join("\n"),
    ""
  ].join("\n")).join("\n");
  const compactSection = (title, items = []) => [
    `## ${title}`,
    "",
    ...items.flatMap(item => [
      `### ${item.id} ${item.name || item.label || item.question || ""}`,
      "",
      `- 状态：${item.status || item.priority || "UNKNOWN"}`,
      `- 规则：${item.rule || item.description || item.impact || ""}`,
      `- 证据：${(item.evidenceRefs || []).join("、") || "待补"}`,
      ""
    ])
  ].join("\n");
  const configs = (detail.configs || []).map(item => `| ${item.id} | ${item.name} | \`${item.path}\` | ${item.role} | ${item.status} |`).join("\n");
  const relations = (detail.relationships || []).map(item => `| ${item.id} | ${item.type} / ${item.direction || "outgoing"} | ${item.targetId} ${item.targetName} | ${item.description} | ${item.status} | ${(item.evidenceRefs || []).join("、") || "—"} | ${item.provenance || "—"} |`).join("\n");
  const evidence = (detail.evidence || []).map(item => `| ${item.id} | ${item.kind} | ${item.label} | \`${item.path}\` | ${item.location || ""} | ${item.status} |`).join("\n");
  const humanDecisions = (detail.humanDecisions || []).map(item => `| ${item.cardId} | ${item.selectedOptionId} · ${item.selectedOptionName} | ${item.closeableQuestionId} | ${item.approvalStatus} / ${item.decisionStatus} | ${item.implementationStatus} | ${item.userComment || "（空评论）"} | ${item.evidenceRef} |`).join("\n");
  const questions = (detail.openQuestions || []).map(item => `| ${item.id} | ${item.priority} | ${item.lifecycle || "OPEN"} | ${item.resolutionOwner || "待分流"} | ${item.question} | ${item.answer || "—"} | ${(item.closureEvidenceRefs || item.evidenceRefs || []).join("、") || "—"} |`).join("\n");
  const snapshot = detail.sourceSnapshot || {};

  return `# ${detail.systemId} ${detail.name}

> 本文由 \`system-details/${detail.systemId}.json\` 生成；结构化 JSON 是本知识库中该系统正文的维护源。

- 详情版本：${detail.revision}
- 更新时间：${detail.updatedAt}
- 完整度：${detail.detailLevel}
- 证据环境：${snapshot.environment || "未记录"}
- 核对时间：${snapshot.checkedAt || "未记录"}
- SVN Revision：${snapshot.svnRevision || "未记录"}
- LIVE 说明：${snapshot.liveMeaning || "工作副本观察不等于 Production/LIVE。"}

## 系统概览

${detail.overview.purpose}

### 包含范围

${bullets(detail.overview.inScope)}

### 不包含范围

${bullets(detail.overview.outOfScope)}

### 输入

${bullets(detail.overview.inputs)}

### 输出

${bullets(detail.overview.outputs)}

## 状态分层

| 轴 | 当前值 | 状态 | 说明 |
|---|---|---|---|
${axes}

### 状态词图例

| 前缀 | 含义 |
|---|---|
${guide || "| 暂无 | 待补 |"}

## 核心流程

${flow}
## 系统规则

${rules}
${compactSection("条件", detail.conditions)}

${compactSection("奖励与结算", detail.rewards)}

${compactSection("异常与边界", detail.exceptions)}

${compactSection("UI 与信息表达", detail.ui)}

## 共享契约引用

| 契约 ID | 契约 | 本系统规则 |
|---|---|---|
${contracts || "| 暂无 | 暂无 | 暂无 |"}

> 共享契约用于跨系统去重和路由，不替代本系统规则，也不代表规则已经冻结。

## 配置契约

| ID | 配置 | 路径 | 职责 | 状态 |
|---|---|---|---|---|
${configs}

## 系统关系

| ID | 类型 | 目标 | 说明 | 状态 | 证据 | 来源/推导边界 |
|---|---|---|---|---|---|---|
${relations}

## 证据

| ID | 类型 | 证据 | 路径 | 位置 | 状态 |
|---|---|---|---|---|---|
${evidence}

## 正式人工裁决

| 卡片 | 选择 | 已关闭 QID | 目标/裁决状态 | 实施状态 | 用户评论 | 证据 |
|---|---|---|---|---|---|---|
${humanDecisions || "| — | — | — | — | — | — | — |"}

## 问题与闭环记录

| ID | 优先级 | 生命周期 | 责任 | 问题 | 答案 | 关闭证据 |
|---|---|---|---|---|---|---|
${questions}
`;
}
