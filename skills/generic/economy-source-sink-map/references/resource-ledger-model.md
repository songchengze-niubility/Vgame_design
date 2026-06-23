# Resource Ledger Model

## Purpose
Provide a universal framework for classifying game economy resources into functional layers, enabling systematic source/sink analysis regardless of game genre.

## Layer Definitions

### Layer 1 — Currencies
Resources used as general exchange media. Typically numeric, fungible, and displayed in the HUD.
- **Hard Currency**: Premium/paid (gems, crystals, diamonds)
- **Soft Currency**: Earnable through gameplay (gold, coins)
- **Energy/Stamina**: Time-gated entry resource for content
- **Specialized Currency**: System-specific tokens (PvP coins, guild currency)

### Layer 2 — Growth Resources
Resources consumed to increase character/unit power.
- **EXP Materials**: Level-up items
- **Breakthrough/Ascension Materials**: Rank-up items (often tiered by rarity)
- **Skill Materials**: Ability upgrade items
- **Universal Fragments**: Convertible growth resources

### Layer 3 — Equipment Resources
Resources related to gear systems.
- **Equipment Drops**: Direct gear acquisition
- **Enhancement Materials**: Gear level-up consumables
- **Refinement Materials**: Gear quality improvement
- **Salvage Returns**: Resources recovered from dismantling gear

### Layer 4 — Gacha/Acquisition Resources
Resources that control character/item acquisition RNG.
- **Summon Tickets**: Direct pull currency
- **Pity/Guarantee Counters**: Accumulated pull count (implicit resource)
- **Selection/Choice Tokens**: Guaranteed pick items
- **Duplicate Conversion**: Resources from pulling duplicates

### Layer 5 — Paid/Monetization Resources
Resources exclusively or primarily from real-money purchase.
- **Direct Purchase Items**: Cash shop exclusives
- **Battle Pass Rewards**: Paid track items
- **Monthly Card Yields**: Subscription daily rewards
- **First Purchase Bonuses**: One-time paid bonuses

## Properties Per Resource
| Property | Description |
|----------|-------------|
| Name | In-game display name |
| Internal ID | Config table identifier |
| Layer | Which layer (1-5) |
| Fungibility | Can it be exchanged/converted |
| Cap | Maximum holdable amount (if any) |
| Expiry | Does it expire (event currency, seasonal) |
| Visibility | Shown to player or hidden (pity counter) |

## Flow Notation
```
[Source System] --({quantity} × {frequency})--> [Resource] --({quantity} × {frequency})--> [Sink System]
```

Example:
```
[Daily Dungeon] --(100 × daily)--> [Gold] --(500 × per upgrade)--> [Equipment Enhancement]
```

## Cross-Layer Conversion
Some resources convert between layers. Document these paths:
```
[Layer 4: Duplicate Token] --(exchange shop)--> [Layer 2: Growth Material]
[Layer 1: Soft Currency] --(craft system)--> [Layer 3: Enhancement Material]
```

## Audit Questions Per Resource
1. What are ALL sources? (completeness check)
2. What are ALL sinks? (completeness check)
3. Is daily net flow positive or negative at each progression stage?
4. Is there a hard cap? What happens when cap is reached?
5. Can paid players acquire this faster? By what multiplier?
