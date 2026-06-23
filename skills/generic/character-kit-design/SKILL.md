---
name: character-kit-design
description: Generic methodology for analyzing and designing character kits — covering identity positioning, kit composition, growth extensions, audit methodology, peer comparison requirements, and feasibility checklists applicable to any RPG or action game character design.
---

# Character Kit Design & Analysis Skill

## Load Order
1. Read this SKILL.md for design frameworks and audit methodology.
2. Identify the project's role taxonomy and progression systems.
3. Apply kit audit checklist when reviewing or proposing a character design.

## Scope
- Character identity and role positioning.
- Kit composition model. Growth extension layer.
- Kit audit methodology. Peer comparison requirements.
- Mechanic feasibility checklist.
- Evidence hierarchy (design doc vs config vs runtime).
- Standard validation scenarios by role.

## 角色身份与定位 (Character Identity & Role Positioning)

Every character must answer:
1. **Who are they?** — Narrative identity, faction, personality.
2. **What role do they fill?** — Combat function (DPS, Tank, Support, Hybrid).
3. **What makes them unique?** — Signature mechanic or playstyle differentiator.
4. **Where do they excel?** — Scenario niches (single-target, AOE, sustain, burst, utility).

## Kit 组成模型 (Kit Composition Model)

```
Normal Attack Chain (resource generation, basic output)
  → Active Skill(s) (cooldown-gated, core mechanic expression)
    → Ultimate / Burst (high-cost payoff, kit climax)
      → Talent / Passive (conditional modifiers, synergy glue)
        → Growth Extensions (star-up, signature weapon, equipment set, passive pool)
```

Each layer should reinforce the character's identity and create a coherent gameplay loop.

## 成长扩展层 (Growth Extension Layer)

| Extension | Design Purpose |
|-----------|---------------|
| Star-up / Constellation | Deepen existing mechanics; add new conditional effects |
| Signature Weapon | Amplify core loop; provide stat foundation |
| Equipment Set | Enable build diversity; synergize with playstyle |
| Passive Pool / Talent Tree | Customization within role boundaries |

Principle: Extensions should amplify identity, not replace it.

## Kit 审计方法论 (Kit Audit Methodology)

### 1. Identity Check
- Is the role clear from the kit alone (without reading lore)?
- Does every skill serve the stated role?
- Is there a clear signature mechanic?

### 2. Loop Check
- Does the kit have a natural rotation (setup → payoff → cooldown)?
- Is resource generation and consumption balanced?
- Are there dead states (nothing meaningful to do)?

### 3. Growth Check
- Do extensions deepen the loop without breaking it?
- Is there meaningful power gain at each growth milestone?
- Are any extensions mandatory (feels incomplete without)?

### 4. Implementation Feasibility
- Does every mechanic have runtime system support?
- Are there new systems required? (Flag for engineering review)
- Are edge cases handled (stacking, interaction with other characters)?

### 5. Verification Readiness
- Can numeric claims be validated with existing formulas?
- Are standard scenarios defined for testing?

## 同行比较要求 (Peer Comparison Requirements)

Before making any strength claim about a character:
- Must compare against 3+ peers of same role and rarity.
- Must normalize investment (level, skills, gear, constellations).
- Must use identical test scenarios.
- Must show numeric evidence (DPS, EHP, utility value).
- Subjective impressions are supplementary, never primary evidence.

## 机制可行性清单 (Mechanic Feasibility Checklist)

- [ ] Does the mechanic use existing buff/skill system capabilities?
- [ ] If new system required: engineering effort estimated and approved?
- [ ] Interaction with existing characters tested (no gamebreaking combos)?
- [ ] Performance impact acceptable (particle count, entity count)?
- [ ] AI behavior for mechanic defined (how AI uses it; how AI counters it)?
- [ ] Edge cases documented (what happens on death, disconnect, phase transition)?

## 证据层级 (Evidence Hierarchy)

| Level | Source | Reliability |
|-------|--------|-------------|
| 1 (Highest) | Runtime test data (actual gameplay recording) | Definitive |
| 2 | Config table values + formula calculation | High |
| 3 | Design document description | Medium (intent, not proof) |
| 4 | Verbal/chat claims without data | Low (requires verification) |

Rule: Never make balance conclusions from Level 3–4 evidence alone.

## 角色验证场景 (Standard Validation Scenarios by Role)

| Role | Scenario | Primary Metric |
|------|----------|---------------|
| DPS | Single-target sustained (60s) | Total damage / time |
| DPS | Burst window (10–15s) | Peak damage in window |
| DPS | Multi-target (3–5 enemies) | Total damage / time |
| Tank | Survival under standard DPS pressure | Time to death |
| Tank | Aggro maintenance | Aggro uptime % |
| Support | Buff/heal contribution | Effective value per rotation |
| Support | Team DPS increase | % DPS gain for team |

## Standard Workflow
1. Review character identity and role statement.
2. Map kit composition (normal → skill → ult → passive → extensions).
3. Run 5-point audit (identity, loop, growth, feasibility, verification).
4. Flag any mechanic requiring feasibility confirmation.
5. If strength claim needed: execute peer comparison protocol.
6. Document findings with evidence level cited.

## Output Contract
- Kit composition diagram with loop flow annotated.
- Audit results: pass/flag/fail per category with notes.
- Feasibility flags with owner assignment (design vs engineering).
- Peer comparison table (if strength claims made).
- Evidence level cited for every conclusion.
