---
name: project-core-adapter
description: Generic project entry point skill template. Establishes project identity, routes tasks to specialist skills, manages evidence rules, and protects against unverified assumptions.
---

# Project Core Adapter

## Load Order
1. Load this skill FIRST for any new project onboarding.
2. Fill in the templates below with project-specific facts.
3. Specialist skills reference this adapter for routing and evidence rules.

## Scope
- Establish project identity (game type, core loop, progression model)
- Route incoming tasks to the correct specialist skill
- Enforce evidence discipline: every claim needs a source of truth or pending-confirmation tag
- Prevent hallucinated assumptions from propagating into deliverables

## Standard Workflow

### Step 1 — Project Identity
Fill the Gameplay Structure Template:
| Layer | Description |
|-------|-------------|
| Main Axis | Core combat/gameplay loop |
| Growth | Character/unit power progression systems |
| Verification | Content that tests player growth (dungeons, PvP, boss) |
| Outer Loop | Retention/monetization systems (gacha, shop, pass, events) |
| Deprecated | Legacy systems scheduled for removal |

### Step 2 — Evidence Rules
- **Confirmed**: Value read directly from config table or official design doc
- **Pending**: Value stated by human but not yet verified against source
- **Assumed**: Value inferred by agent; must be flagged and never used in final output without confirmation
- Rule: Never promote Assumed → Confirmed without reading the source file

### Step 3 — Specialist Routing
| Task Pattern | Route To |
|---|---|
| Config table read/write/audit | config-pipeline-map, config-quality-audit |
| Economy balance, resource flow | economy-source-sink-map |
| Drop/reward table editing | reward-drop-config |
| Progression/unlock chain | progression-unlock-map |
| Growth→combat conversion | growth-combat-conversion |
| Outer loop systems | outer-loop-system-map |

### Step 4 — Delivery Gates
Before any deliverable is finalized:
- [ ] All values are Confirmed (no Assumed tags remain)
- [ ] Cross-references validated against live config
- [ ] Specialist skill output contract satisfied
- [ ] Human sign-off obtained for any irreversible change

## Output Contract
- A filled project identity document
- A routing table mapping task keywords → specialist skills
- An evidence log tracking Confirmed / Pending / Assumed status per fact
