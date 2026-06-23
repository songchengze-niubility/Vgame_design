---
name: version-feature-map
description: Generic methodology for managing game versions and feature lifecycles — covering versioning models, feature switches, AB testing, gray releases, hotfix procedures, and release checklists applicable to any live-service game.
---

# Version & Feature Management Skill

## Load Order
1. Read this SKILL.md for frameworks and templates.
2. Identify the project's release cadence and deployment infrastructure.
3. Apply lifecycle model to each feature being tracked.

## Scope
- Version numbering model.
- Feature lifecycle stages.
- Feature switch layers.
- AB test registry. Gray release tracking.
- Hotfix/rollback procedures.
- Release checklist. Deprecation management.

## 版本模型 (Version Model)

```
Major.Minor.Patch.Hotfix
  │      │     │      └─ Emergency fix (no new content)
  │      │     └─ Bug fixes, balance adjustments
  │      └─ Feature update (new content, systems)
  └─ Milestone release (season, expansion, major overhaul)
```

Naming convention: `v{Major}.{Minor}.{Patch}[.{Hotfix}]` — e.g., v2.3.1, v2.3.1.1

## 功能生命周期 (Feature Lifecycle)

```
Plan → Develop → Test → Gray Release → Live → Maintain → Deprecate → Remove
```

| Stage | Exit Criteria |
|-------|--------------|
| Plan | Design doc approved, resources allocated |
| Develop | Implementation complete, unit tests pass |
| Test | QA sign-off, performance benchmarks met |
| Gray | Metrics nominal for target cohort, no critical bugs |
| Live | Rolled out to 100% of players |
| Maintain | Ongoing balance/bug fixes as needed |
| Deprecate | Announced removal timeline, migration path provided |
| Remove | All references cleaned, data archived |

## 功能开关层 (Feature Switch Layers)

| Layer | Mechanism | Use Case |
|-------|-----------|----------|
| Config Gate | Server-side JSON/DB flag | Kill switch, gradual rollout |
| Server Flag | Per-player or per-cohort flag | AB test, beta access |
| Client Version | Min client version check | Ensure compatible client |
| Activity Time | Start/end timestamp | Seasonal events, limited modes |

Principle: Every new feature should have at least one kill-switch layer.

## AB 测试注册模板 (AB Test Registry Template)

```markdown
| Test ID | Feature | Cohort Split | Start Date | End Date | Primary Metric | Result |
|---------|---------|-------------|-----------|---------|---------------|--------|
| AB-001  | ...     | 50/50       | ...       | ...     | ...           | ...    |
```

## 灰度发布追踪 (Gray Release Tracking)

- Define cohort criteria (region, account age, device tier).
- Rollout stages: 1% → 5% → 20% → 50% → 100%.
- At each stage: monitor crash rate, error logs, key metrics.
- Go/no-go decision documented before expanding.

## 热修复与回滚日志 (Hotfix & Rollback Log Template)

```markdown
| Hotfix ID | Date | Issue | Root Cause | Fix Applied | Rollback? | Post-fix Verification |
|-----------|------|-------|-----------|------------|-----------|----------------------|
| HF-001   | ...  | ...   | ...       | ...        | No        | ...                  |
```

## 发布检查清单 (Release Checklist Template)

- [ ] All feature flags configured correctly
- [ ] Config tables validated (no broken refs, schema pass)
- [ ] Client/server version compatibility confirmed
- [ ] Rollback plan documented and tested
- [ ] Monitoring dashboards updated for new features
- [ ] Patch notes drafted and reviewed
- [ ] Reward/economy changes sanity-checked
- [ ] Localization complete for target regions
- [ ] Legal/compliance review (if applicable)
- [ ] Post-release observation window scheduled

## 废弃功能管理 (Deprecated Feature Management)

1. Announce deprecation with timeline (minimum 1 version in advance).
2. Provide migration path or compensation for affected players.
3. Remove client UI references; keep server-side data for grace period.
4. Archive data after grace period; clean config tables.

## Standard Workflow
1. Assign version number per release cadence rules.
2. Register each feature's lifecycle stage in tracking system.
3. Configure feature switches before deploy.
4. Execute release checklist.
5. Monitor gray release metrics; escalate anomalies.
6. Log any hotfixes; update version accordingly.

## Output Contract
- Version changelog with categorized entries.
- Feature status registry (current lifecycle stage per feature).
- Release checklist: all items checked or exceptions documented.
- Hotfix log updated within 1 hour of any emergency patch.
