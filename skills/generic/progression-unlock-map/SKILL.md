---
name: progression-unlock-map
description: Generic progression and unlock chain skill. Covers level/stage ID conventions, unlock condition types, feature gating, progression chain tracing, stamina models, sweep rules, and audit methodology.
---

# Progression & Unlock Map

## Load Order
1. Load after project-core-adapter (needs gameplay structure).
2. Load before growth-combat-conversion (progression defines what growth is tested against).

## Scope
- Map level/stage/dungeon ID conventions and allocation
- Classify unlock condition types
- Model system open / feature gating
- Trace full progression chains (what unlocks what)
- Document stamina/entry cost models
- Define sweep/auto-clear eligibility rules

## Standard Workflow

### Step 1 — Stage ID Convention
Document the project's stage identification scheme:
- ID range allocation per content type (main story, daily dungeon, event, etc.)
- Difficulty tier encoding (normal/hard/hell within same content)
- Chapter/act grouping logic

### Step 2 — Unlock Condition Classification
| Condition Type | Description |
|----------------|-------------|
| Level Clear | Must clear a specific prior stage |
| Player Grade/Rank | Account level or rank threshold |
| Task/Quest Complete | Specific quest must be finished |
| Item Possession | Must own a specific item or character |
| Time Gate | Unlocks after calendar date or days since registration |
| Manual GM Open | Requires server-side activation |

### Step 3 — Feature Gating Model
Map when each game system becomes available:
| System | Unlock Condition | Typical Player Day |
|--------|-----------------|-------------------|
| (fill per project) | | |

### Step 4 — Progression Chain Tracing
For any target content, trace backwards:
1. What is the immediate unlock condition?
2. What unlocks THAT condition?
3. Continue until reaching a condition met at game start
4. Output: full dependency chain from new player → target

### Step 5 — Stamina/Entry Cost Model
- What resource is consumed to enter content
- Refill mechanics (time regen, paid refill, items)
- Daily cap on attempts (soft cap via stamina vs hard cap via attempt count)

### Step 6 — Sweep/Auto-Clear Rules
- Eligibility: typically requires prior manual clear with specific rating
- Reward equivalence: does sweep give same reward as manual clear?
- Restrictions: any content that cannot be swept

## Progression Audit Checklist
- [ ] No orphan stages (every stage reachable via some unlock chain)
- [ ] No circular unlock dependencies
- [ ] Unlock conditions reference valid stage/quest IDs
- [ ] Difficulty progression is monotonically increasing
- [ ] Stamina costs scale appropriately with progression
- [ ] Sweep eligibility correctly references clear records

## Output Contract
- Stage ID allocation map
- Unlock condition matrix (stage × condition)
- Feature gating timeline
- Full progression chain for any queried target
- Stamina economy summary
