---
name: vgame-config-quality-audit
description: Use for read-only Vgame configuration QA and delivery-gate audits across Datas Excel source tables, __tables__.xlsx registration, logical Drop references, UIlevel reward references, PropType formats, ItemId/DropId/RewardId integrity, shop price/item checks, DrawCard reward and price references, task/battle-pass/activity/mail reward references, and common source-vs-generated mistakes. Trigger when asked to check config quality, validate a change before delivery, audit broken references, inspect whether tables are registered, verify reward/config chains after edits, or run a read-only config QA script.
---

# Vgame Config Quality Audit

Use this skill as the Vgame config QA layer. It checks whether configuration chains are structurally safe before a result is considered ready.

This skill is read-only by default. It does not design rewards, decide economic value, tune combat, or edit real config tables.

## Load Order

1. Read `vgame-core-understanding` first for project entry, evidence rules, and delivery gates.
2. Read `references/audit-overview.md` for the QA role and boundary.
3. Read `references/audit-checklist.md` before doing a manual review.
4. Read `references/automated-checks.md` before running or interpreting `scripts/audit_config_quality.py`.
5. Read `references/known-baselines.md` before treating historical missing references as newly introduced issues.
6. Use `vgame-config-schema` for source table discovery, schema, `__tables__`, export, and generated JSON tracing.
7. Use `vgame-reward-drop-sync` for Drop/UIlevel reward implementation and reward-package content.
8. Use `vgame-economy-source-map` for item/resource source and sink meaning.
9. Use `vgame-level-progression-map` for LevelId, LevelType, Unlock, SystemOpen, stamina, and sweep chains.
10. Use `senior-game-economy` or `game-numerical-analysis` for value, pacing, and balance judgment.

## Scope

Covered in v1:

- source table registration and missing input Excel detection
- duplicate input filename ambiguity under `Datas`
- logical `Drop` source aggregation from `__tables__.xlsx`
- Drop internal reference checks: quantity ranges, `DropId2`, `DropItem_id`
- UIlevel reward DropId reference checks
- DrawCard DropId and price PropType checks
- ShopGoods item and price PropType checks
- Task, daily/weekly active reward, battle pass reward, activity reward, and presend mail Drop reference checks
- basic PropType format and ItemId existence checks

Not covered in v1:

- final reward value or economy balance
- exact gacha probability and pity expectation
- combat difficulty correctness
- client/server runtime behavior not visible in source Excel
- automatic modification of any workbook

## Script

Use the bundled script for broad read-only checks:

```powershell
python "${VGAME_SKILL_ROOT}\vgame-config-quality-audit\scripts\audit_config_quality.py" --datas-root "${VGAME_ROOT}\Config\GameConfig\Datas" --output "${VGAME_OUTPUT_ROOT}\config-quality-audit.md"
```

The script prints a summary and writes a Markdown report when `--output` is provided.

## Output Contract

For config QA work, include:

- `Audit scope`: tables, systems, or changed areas covered.
- `Checked tables`: source workbooks and key fields.
- `Critical issues`: broken references, missing files, malformed required formats.
- `Warnings`: historical baselines, preview-vs-real ambiguity, missing optional chains, high-risk references.
- `Reference integrity`: ItemId, DropId, RewardId, LevelId, Unlock/SystemOpen where applicable.
- `Schema/export risk`: source-vs-generated risk, unregistered tables, missing schema evidence.
- `Needs specialist review`: economy, reward, progression, combat, or numerical follow-up.
- `Conclusion`: ready, blocked, or ready with known baseline exceptions.

Never hide known issues. If a broken reference is an existing baseline, label it as `known baseline` instead of calling it clean.
