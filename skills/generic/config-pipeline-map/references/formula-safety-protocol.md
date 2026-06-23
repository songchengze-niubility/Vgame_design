# Formula Safety Protocol

## Purpose
Prevent accidental corruption of Excel formula columns when an agent or script writes to config tables.

## Core Rules

### Rule 1 — Scan Before Write
Before modifying any Excel file, scan every column to identify which contain formulas.
Record these as a formula-column whitelist for the file.

### Rule 2 — Never Write to Formula Columns
Formula columns are READ-ONLY. Any value needed from a formula column must be read, not overwritten.
If a task requires changing formula output, modify the formula's input cells instead.

### Rule 3 — Never Insert or Delete Rows
Row insertion/deletion shifts cell references and breaks formulas throughout the sheet.
To add entries: append at the designated append zone (usually bottom of data range).
To remove entries: clear cell contents but preserve the row structure.

### Rule 4 — Never Insert or Delete Columns
Column structural changes break named ranges and cross-sheet references.
New fields must be added at designated extension columns only.

### Rule 5 — Verify After Write
After any write operation:
1. Re-read formula columns and compare to pre-write snapshot
2. If any formula is altered or returns #REF!, rollback immediately
3. Log verification result

## Pre-Write Checklist
- [ ] File opened and all columns scanned for formulas
- [ ] Formula columns recorded and marked read-only
- [ ] Write target columns confirmed as literal-value only
- [ ] No row/column insertion or deletion planned
- [ ] Post-write verification step scheduled

## Recovery Procedure
If formula corruption is detected:
1. Do NOT save the corrupted file
2. Restore from the last known-good backup
3. Re-apply only the literal-value changes
4. Re-verify formula integrity

## Common Formula Patterns to Watch
| Pattern | Risk |
|---------|------|
| `=VLOOKUP(...)` | Cross-table reference; row shift breaks it |
| `=IF(A2="","",...` | Conditional fill; row delete orphans references |
| `=SUM(range)` | Aggregate; row insert may silently extend range |
| `=INDIRECT(...)` | Dynamic reference; any structural change is dangerous |
| Named ranges | Column/row changes invalidate definitions |
