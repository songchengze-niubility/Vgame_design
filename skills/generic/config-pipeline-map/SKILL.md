---
name: config-pipeline-map
description: Generic config table pipeline skill. Covers source Excel to export tool to generated output, schema reading, formula safety, table registration, and new table onboarding.
---

# Config Pipeline Map

## Load Order
1. Load after project-core-adapter (needs project identity).
2. Load before any skill that reads or writes config tables.

## Scope
- Map the full pipeline: Source Excel → Export Tool → Generated Output (code/data)
- Understand table registration and logical table mapping
- Read schemas correctly (header rows, column types, enums, bean structures)
- Enforce formula safety rules (see references/formula-safety-protocol.md)
- Onboard new tables with proper registration

## Standard Workflow

### Step 1 — Pipeline Discovery
Identify and document:
1. Where source Excel files live (directory structure)
2. What export tool is used (Luban, custom exporter, etc.)
3. What output format is generated (JSON, binary, scriptable objects)
4. Where the generated output is consumed (client, server, both)

### Step 2 — Schema Reading Methodology
- Identify header row positions (typically row 1-4: field name, type, description, export target)
- Identify column types: primitive, enum, bean/struct, list, map
- Identify which columns are key/ID columns
- Note any columns that contain formulas vs literal values

### Step 3 — Formula Safety Protocol
Before ANY write operation on an Excel file:
1. Scan all columns for formula presence
2. Mark formula columns as READ-ONLY in your working model
3. Never insert or delete rows (shifts formula references)
4. Only write to whitelisted literal-value columns
5. After write, verify formula columns are unchanged

### Step 4 — Config Impact Matrix
| Table | Depends On | Depended By | Export Target |
|-------|-----------|-------------|---------------|
| (fill per project) | | | |

### Step 5 — New Table Onboarding Checklist
- [ ] Table file created in correct directory
- [ ] Header rows follow project schema convention
- [ ] Table registered in export tool configuration
- [ ] ID column uses correct allocation range
- [ ] Cross-references to other tables validated
- [ ] Export tested and output verified

## Output Contract
- Pipeline diagram (source → tool → output)
- Schema summary per table touched
- Formula safety scan report (which columns have formulas)
- Impact matrix for any table modification
