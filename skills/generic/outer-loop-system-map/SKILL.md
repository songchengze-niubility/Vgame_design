---
name: outer-loop-system-map
description: Generic outer loop system mapping skill. Covers system classification by purpose, cadence modeling, gacha/shop/pass/event template mapping, display vs real rewards, monetization sensitivity, and audit methodology.
---

# Outer Loop System Map

## Load Order
1. Load after economy-source-sink-map (outer loop systems are major sources).
2. Load after progression-unlock-map (some systems gate behind progression).

## Scope
- Classify all outer loop systems by purpose
- Model system cadence (reset frequency, availability windows)
- Map standard system templates (gacha, shop, task, sign-in, battle pass, etc.)
- Distinguish display rewards from real granted rewards
- Flag monetization-sensitive configurations
- Audit outer loop health

## Standard Workflow

### Step 1 — System Classification by Purpose
| Purpose | Description | Examples |
|---------|-------------|----------|
| Retention | Encourages daily/regular return | Sign-in, daily quest, streak bonus |
| Monetization | Converts spending into value | Gacha, direct shop, monthly card |
| Resource Supplement | Provides resources beyond core loop | Mail, compensation, codes |
| Social | Multiplayer engagement incentives | Guild rewards, friend gifts, co-op bonus |
| Compensation | Makes up for downtime/issues | Maintenance mail, bug compensation |
| Seasonal/Event | Time-limited engagement driver | Limited event, seasonal pass, collab |

### Step 2 — Cadence Model
| Cadence | Reset Behavior | Examples |
|---------|---------------|----------|
| One-time | Never resets | First purchase bonus, achievement |
| Daily | Resets every day | Daily quest, stamina refill, sign-in |
| Weekly | Resets every week | Weekly boss, weekly shop refresh |
| Seasonal/Periodic | Resets per season/patch | Battle pass, ranked season |
| Event | Available during event window only | Limited banner, event shop |
| Paid Refresh | Resets on purchase | Shop manual refresh, extra attempts |

### Step 3 — System Template Mapping
For each outer loop system, document:
| Field | Description |
|-------|-------------|
| System Name | Identifier |
| Purpose | From classification above |
| Cadence | From cadence model above |
| Entry Condition | Unlock requirement |
| Display Rewards | What player sees (UI preview) |
| Real Rewards | What is actually granted (config) |
| Cost | Free, currency cost, or real money |
| Monetization Flag | Does spending accelerate or gate this? |

### Step 4 — Display vs Real Audit
- Compare UI display table entries with actual drop/reward config
- Flag mismatches (shown but not granted, granted but not shown)
- Verify that "premium" labels match actual paid-only status

### Step 5 — Monetization Sensitivity Markers
Flag any system where:
- [ ] F2P players are hard-blocked from rewards without paying
- [ ] Paid refresh gives unlimited resource access (no cap)
- [ ] Probability display may not match actual rates
- [ ] Pity/guarantee system has undocumented resets

## Outer Loop Audit Checklist
- [ ] Every outer loop system classified by purpose and cadence
- [ ] Display rewards match real rewards for all systems
- [ ] No orphan reward references (all IDs valid)
- [ ] Monetization-sensitive items clearly flagged
- [ ] Seasonal/event systems have proper start/end date configs
- [ ] Expired events are properly disabled (not just hidden)

## Output Contract
- Complete system inventory with classification and cadence
- Template mapping per system (using Step 3 format)
- Display vs Real discrepancy report
- Monetization sensitivity flag list
- Audit pass/fail summary
