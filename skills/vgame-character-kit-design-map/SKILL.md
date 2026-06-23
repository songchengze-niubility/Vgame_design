---
name: vgame-character-kit-design-map
description: Use for Vgame character and hero kit design analysis, including role positioning, normal attacks, auto skills, ultimates, talents, energy/passive effects, star-up nodes, signature weapons, travel-ticket set skills, mapping-equipment affixes, common passives, team synergy, combat mechanism feasibility, and character-design source workbooks. Trigger when asked about a character's kit, skill logic, hero identity, role archetype, passive/talent design, weapon or equipment synergy, skill implementation risk, or how character design should route into battle, growth, config, and tuning skills.
---

# Vgame Character Kit Design Map

Use this skill to answer: a Vgame character is meant to do what, how the kit works, which growth or equipment layer reinforces it, and what evidence must be read before treating a design as formal.

This is a project mapping and audit skill. It is read-only by default and does not edit design workbooks, config tables, generated JSON, or battle scripts.

## Load Order

1. Read `vgame-core-understanding` first for project identity and routing rules.
2. Read `references/character-kit-overview.md` for the role of character kits in Vgame's full-stack design.
3. Read `references/hero-design-workbook-map.md` when the task names `Vgame英雄设计.xlsx`, a hero design sheet, or a design-document export.
4. Read `references/kit-composition-map.md` when the task involves role positioning, skill slots, passives, star-up, signature weapon, travel-ticket skills, mapping-equipment affixes, or synergy.
5. Read `references/character-kit-audit-checklist.md` when asked to review, QA, compare, or find risks in a character kit.
6. Use `vgame-hero-skill-config-map` for exact hero definition config, Hero/Skill/Buff tables, hero attributes, ascension, star-up, exclusive weapon config, skill editor workflow, and runtime skill serialization.
7. Use `vgame-battle-content-map` for exact monster/boss battle content, shared skill/buff mechanics outside hero ownership, bullet, summon, damage, AI, or runtime battle-content config.
8. Use `vgame-growth-combat-conversion-map` for how star-up, signature weapon, travel-ticket equipment, mapping equipment, or attributes convert into combat performance.
9. Use `vgame-battle-tuning-helper` for DPS, TTK, coefficient, survival, peer comparison, full-max all-character visual quantification, role contribution benchmarks, standard validation scenarios, mechanic value conversion, and character strength reports.
10. Use `game-numerical-analysis` for long-term numerical experience, progression curves, economy pressure, and cross-system balance audits.
11. Use `vgame-config-schema` before claiming exact source table names, fields, Luban schema, or generated JSON links.
12. Use `vgame-reward-drop-sync`, `vgame-economy-source-map`, or `vgame-level-progression-map` only when rewards, item source/sink, or unlock/progression chains enter the question.

## Scope

Covered in v1:

- character identity: name, rarity, faction, role type, design intent, keyword tags
- combat kit: normal attack, auto skill/passive blocks, ultimate, talent, energy and trigger logic
- growth-facing kit extensions: star-up nodes, signature weapon, common passive, travel-ticket set skills, mapping-equipment affixes
- design-document evidence: `${VGAME_SOURCE_DOCS_ROOT}\Vgame英雄设计.xlsx`
- implementation-risk notes from hero-design memo rows
- read-only kit audit and routing to specialist skills

Not covered directly:

- final numerical balance or combat coefficient approval
- exact runtime implementation of skills, buffs, bullets, summons, or damage effects
- exact config table writes or generated JSON edits
- reward drops, item production/consumption, unlock timing, or monetization cadence
- treating archived or memo sheets as formal design without user confirmation

## Standard Workflow

1. Identify whether the user is asking about a character, a skill mechanic, an equipment/passive extension, or a full kit review.
2. Classify the evidence source: formal design sheet, archive, memo, generated config, or runtime implementation.
3. Map the kit from identity -> role -> skill loop -> growth extensions -> expected gameplay verification.
4. Separate confirmed workbook facts from config/runtime facts that still need source reading.
5. Route exact battle mechanics, growth conversion, config schema, tuning, reward, economy, or unlock questions to downstream skills.
6. When reviewing, produce concrete risks and missing evidence rather than inventing final balance conclusions.

## Output Contract

For character kit analysis, include:

- `Character or system`: target hero, passive pool, signature weapon, travel-ticket set, or mapping equipment group.
- `Observed evidence`: workbook, sheet, row/field, or config/source file read.
- `Kit intent`: role, combat loop, keywords, team or equipment synergy.
- `Mechanic chain`: normal attack, skill, ultimate, talent, passive, star-up, weapon, and equipment links.
- `Downstream routes`: battle content, growth conversion, tuning, config schema, reward/economy/progression as needed.
- `Risks and unknowns`: duplicate IDs, archive-only content, formula references, implementation feasibility, balance pressure, or missing config proof.

Use `待确认` for any link not directly observed from project docs, source workbooks, config files, or code.

When the user asks whether a character is strong or weak, do not give a final strength conclusion from single-character evidence. Route to `vgame-battle-tuning-helper` and require same-role, same-investment, same-scenario peer comparison, or label the result as a single-character risk assessment. When the user asks for all-character rankings, full-max comparisons, visual quantification, or concrete tuning priorities, route to `vgame-battle-tuning-helper` and run its full-max quantification script.

## References

- [references/character-kit-overview.md](references/character-kit-overview.md)
- [references/hero-design-workbook-map.md](references/hero-design-workbook-map.md)
- [references/kit-composition-map.md](references/kit-composition-map.md)
- [references/character-kit-audit-checklist.md](references/character-kit-audit-checklist.md)
