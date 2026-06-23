---
name: growth-combat-conversion
description: Generic growth to combat conversion skill. Covers growth module classification, attribute output categories, combat conversion chains, verification gameplay mapping, and standard analysis workflow.
---

# Growth → Combat Conversion

## Load Order
1. Load after progression-unlock-map (needs to know what content tests growth).
2. Load after economy-source-sink-map (growth consumes resources).

## Scope
- Classify all growth modules in the game
- Map each module's attribute output
- Trace the conversion chain from growth investment to combat outcome
- Identify which gameplay content verifies which growth line
- Route to tuning skills when numbers need adjustment

## Standard Workflow

### Step 1 — Growth Module Classification
| Category | Examples |
|----------|----------|
| Character/Unit | Level, ascension, star rank, awakening |
| Weapon | Weapon level, refinement, passive unlock |
| Equipment/Gear | Gear level, set bonus, substats, enhancement |
| Passive/Talent | Skill tree, talent board, constellation |
| External Buff | Title, achievement bonus, guild buff, artifact |

### Step 2 — Attribute Output Categories
Each growth module outputs one or more attribute types:
| Type | Description |
|------|-------------|
| Base Flat | Additive base stat (ATK +100) |
| Base Percentage | Multiplicative scaling (ATK +10%) |
| Secondary Stat | Crit rate, crit damage, speed, resistance |
| Skill/Mechanic | New ability, mechanic change, cooldown reduction |
| Conditional | Buff active only under certain conditions |

### Step 3 — Conversion Chain
Map the full chain for each growth module:
```
[Growth Investment] → [Attribute Output] → [Combat Effect]
```
Example pattern:
```
Weapon Refinement → Skill DMG +15% → Higher burst damage in boss fights
Equipment Set → Crit Rate +12% → More consistent DPS across all content
```

### Step 4 — Verification Gameplay Mapping
| Growth Line | Primary Verification Content | What It Tests |
|-------------|------------------------------|---------------|
| Character Level | Main story progression | Base survival |
| Equipment | Daily resource dungeon | Sustained DPS |
| Skill/Talent | Weekly boss | Burst window optimization |
| Full Build | Endgame challenge | Everything combined |

### Step 5 — Gap Analysis
- Identify growth modules with unclear combat impact
- Identify content with no dedicated growth verification
- Flag modules where investment cost is disproportionate to combat gain
- Route findings to economy skill (cost) or tuning (values)

## Output Contract
- Growth module inventory with category classification
- Attribute output map per module
- Conversion chain diagram (growth → attribute → combat effect)
- Verification mapping (growth line × content type)
- Gap analysis with routing recommendations
