# Peer Comparison Rules (Generic)

## Purpose
Ensure any character strength conclusion is supported by fair, transparent comparison against peers under controlled conditions.

## 基本原则 (Core Principles)

1. **Same Role** — Only compare characters fulfilling the same combat role (DPS vs DPS, Support vs Support).
2. **Same Investment Level** — Normalize progression variables: level, breakthrough/ascension, star/constellation, skill levels, equipment quality.
3. **Same Scenario** — Use identical enemy target(s) with defined DEF, HP, element, and resistance.
4. **Transparent Assumptions** — Document every assumption: rotation, buff sources, team composition, uptime percentages.

## 比较流程 (Comparison Protocol)

### Step 1: Define the Comparison Set
- Select 3–5 peers of the same role and similar release era or rarity tier.
- If fewer than 3 peers exist, note the limited sample.

### Step 2: Normalize Investment
- Lock all characters to the same progression milestone.
- Use a standard equipment template (e.g., "best-in-slot 4-star" or "mid-tier 5-star").
- Skill levels equal across all subjects.

### Step 3: Define Scenario
- Single-target sustained, single-target burst, multi-target (2/3/5 enemies).
- Specify enemy level relative to player, DEF value, elemental resistance.
- State time limit if applicable (e.g., DPS check window).

### Step 4: Calculate Metrics
- Rotation DPS (total damage / rotation time).
- Burst window DPS (damage in first N seconds).
- Effective contribution (for non-DPS roles, convert utility to value).

### Step 5: Present Results
- Table format: Character | Metric | Rank | Delta from median.
- Highlight if any character is >20% above/below median — flag as outlier.
- State confidence level (high if data is formula-derived; medium if estimate-based).

## 禁止事项 (Prohibited Practices)

- Comparing characters at different investment levels.
- Cherry-picking a scenario that uniquely favors one character.
- Omitting team buff context when one character requires specific teammates.
- Making strength claims without showing numeric evidence.
- Using subjective "feel" as sole basis for ranking.

## 输出格式 (Output Format)

```markdown
### Peer Comparison: [Subject] vs [Peer Group]
| Character | Investment | Scenario | Metric | Value | Rank |
|-----------|-----------|----------|--------|-------|------|
| ...       | ...       | ...      | ...    | ...   | ...  |

**Conclusion**: [Factual statement with delta from median]
**Confidence**: [High / Medium / Low]
**Caveats**: [List any limitations]
```
