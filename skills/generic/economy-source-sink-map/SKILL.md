---
name: economy-source-sink-map
description: Generic game economy source/sink mapping skill. Covers resource ledger modeling, source/sink tracing, cycle tracking, preview vs real reward distinction, and economy risk identification.
---

# Economy Source-Sink Map

## Load Order
1. Load after project-core-adapter (needs gameplay structure).
2. Load before reward-drop-config (economy context informs drop design).

## Scope
- Model the full resource ledger (see references/resource-ledger-model.md)
- Trace every source (where resources enter the economy)
- Trace every sink (where resources leave the economy)
- Distinguish preview/display rewards from real granted rewards
- Track cycle/frequency of each source and sink
- Identify economy risks

## Standard Workflow

### Step 1 — Resource Ledger Construction
Classify all resources into layers:
| Layer | Examples |
|-------|----------|
| Currencies | Gold, gems, stamina, premium currency |
| Growth Resources | EXP items, upgrade materials, skill books |
| Equipment Resources | Gear, fragments, enhancement stones |
| Gacha Resources | Summon tickets, pity counters, guarantee tokens |
| Paid Resources | Direct purchase items, battle pass exclusives |

### Step 2 — Source Tracing
For each resource, identify ALL sources:
- Which system grants it (dungeon clear, quest, mail, shop, event)
- Frequency (one-time, daily cap, weekly reset, seasonal, unlimited)
- Quantity per instance
- Is it a preview/display value or actually granted?

### Step 3 — Sink Tracing
For each resource, identify ALL sinks:
- Which system consumes it (upgrade, craft, shop purchase, entry cost)
- Is consumption mandatory or optional for progression
- Is there a refund/recovery mechanism

### Step 4 — Balance Ledger
| Resource | Daily Source Total | Daily Sink Total | Net Flow | Risk Flag |
|----------|-------------------|------------------|----------|-----------|
| (fill per resource) | | | | |

### Step 5 — Economy Risk Assessment
| Risk Type | Description | Detection Method |
|-----------|-------------|-----------------|
| Hyperinflation | Source far exceeds sink | Net flow consistently positive |
| Uncapped Production | No daily/weekly limit on source | Check frequency constraints |
| Preview ≠ Real | Displayed reward differs from granted | Compare UI table vs drop table |
| Paid Sensitivity | F2P progression blocked without paid resource | Trace critical path sinks |
| Deflation Trap | Sink far exceeds source at some progression point | Model cumulative flow |

## Output Contract
- Complete resource ledger with layer classification
- Source table: resource × system × frequency × quantity
- Sink table: resource × system × frequency × quantity
- Net flow analysis with risk flags
- List of preview ≠ real discrepancies (if any)
