---
name: config-quality-audit
description: Generic config quality audit skill. Provides read-only audit methodology, ID/reference integrity checks, cross-table validation, baseline management, and standardized audit reporting.
---

# Config Quality Audit

## Load Order
1. Load after config-pipeline-map (needs schema knowledge).
2. This skill is READ-ONLY — it never modifies source files.

## Scope
- Perform non-destructive audits on config tables
- Check ID uniqueness and reference integrity
- Validate cross-table references (foreign keys)
- Manage known baselines for regression detection
- Classify and report config quality issues

## Standard Workflow

### Step 1 — Baseline Snapshot
- Record current state of tables as the known baseline
- Note any pre-existing issues (grandfather clause)
- Baseline is updated only after human-approved changes

### Step 2 — ID Integrity Check
For each table:
- [ ] ID column has no duplicates
- [ ] ID column has no gaps (if sequential allocation is required)
- [ ] ID values fall within the allocated range for this table
- [ ] No reserved/deprecated IDs are reused

### Step 3 — Cross-Table Reference Validation
For each foreign key column:
- [ ] Every referenced ID exists in the target table
- [ ] Referenced entries are not marked deprecated/disabled
- [ ] Bidirectional references are consistent (if applicable)

### Step 4 — Value Constraint Checks
- [ ] Enum fields contain only valid enum values
- [ ] Numeric fields are within documented min/max bounds
- [ ] Required fields are not empty
- [ ] String fields match expected format patterns

### Step 5 — Regression Detection
- Compare current state against baseline
- Flag any unexpected changes (values changed without associated task)
- Flag any new entries that violate naming conventions

## Common Config Quality Issues Taxonomy
| Category | Example |
|----------|---------|
| Orphan Reference | Drop table references non-existent item ID |
| Duplicate ID | Two rows share the same primary key |
| Range Violation | Stat value exceeds documented maximum |
| Empty Required | Mandatory field left blank |
| Type Mismatch | String in numeric column |
| Stale Reference | Points to deprecated/removed entry |
| Convention Breach | ID outside allocated range for table |

## Audit Report Template
```
## Audit Report — [Table Name] — [Date]
Baseline: [version/date]
Status: PASS / FAIL (N issues)

### Critical (blocks export)
- [list]

### Warning (functional but incorrect)
- [list]

### Info (style/convention)
- [list]
```

## Output Contract
- Audit report per table (using template above)
- Summary: total tables audited, pass/fail counts, issue breakdown by category
- No file modifications (read-only skill)
