---
name: reward-drop-config
description: Generic reward and drop configuration skill. Covers drop package structures, first-clear vs repeat rewards, ID allocation, UI preview vs real reward fields, formula protection, and cross-table validation.
---

# Reward / Drop Config

## Load Order
1. Load after economy-source-sink-map (needs resource classification).
2. Load after config-pipeline-map (needs schema and formula safety).

## Scope
- Design and edit drop packages (fixed, random weighted, nested)
- Distinguish first-clear, repeat, and special condition rewards
- Allocate Drop IDs following project conventions
- Ensure UI preview fields match real granted rewards
- Protect formulas in drop tables
- Validate cross-table references (drop → level, level → UI)

## Standard Workflow

### Step 1 — Drop Package Structure
Understand the project's drop model:
| Type | Description |
|------|-------------|
| Fixed | Guaranteed items, always granted |
| Random Weighted | Pool of items with weight/probability |
| Nested/Group | Drop package that references other drop packages |
| Conditional | Granted only when condition is met (first clear, VIP, etc.) |

### Step 2 — Reward Context Classification
| Context | Typical Use |
|---------|-------------|
| First Clear | One-time reward for initial completion |
| Normal/Repeat | Granted every time content is completed |
| Star/Rating Bonus | Extra reward for performance threshold |
| Sweep/Auto | Reward for skip/auto-complete (may differ from manual) |
| Event Override | Temporary reward modification during events |

### Step 3 — Drop ID Allocation
- Check the project's ID allocation ranges for drop tables
- Never reuse a deprecated Drop ID
- Group related drops in contiguous ID blocks
- Document the mapping: Content ID → Drop ID(s)

### Step 4 — Preview vs Real Validation
- Identify the UI preview table/fields (what player sees before entering)
- Identify the real drop table/fields (what is actually granted)
- Cross-check: every item shown in preview MUST exist in real drops
- Flag any real drops NOT shown in preview (hidden rewards are intentional?)

### Step 5 — Formula & Write Safety
- Scan drop table for formula columns before any edit
- Typically formula columns: probability normalization, total weight calc
- Write only to literal-value columns (item ID, count, weight)
- Verify formulas unchanged after edit

### Step 6 — Cross-Table Reference Check
- [ ] All item IDs in drop table exist in item master table
- [ ] All Drop IDs referenced by level/stage table exist in drop table
- [ ] UI preview table references valid Drop IDs or item IDs
- [ ] No circular references in nested drop packages

## Output Contract
- Drop package definition (structure, items, weights)
- ID allocation record
- Preview ↔ Real consistency report
- Formula safety verification log
- Cross-reference validation result
