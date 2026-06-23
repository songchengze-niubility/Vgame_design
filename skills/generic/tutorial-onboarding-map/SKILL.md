---
name: tutorial-onboarding-map
description: Generic methodology for designing tutorial and onboarding systems — covering dual tutorial patterns, trigger types, guide data models, feature unlock gating, new player timelines, and guide editor workflows applicable to any game.
---

# Tutorial & Onboarding Mapping Skill

## Load Order
1. Read this SKILL.md for patterns and methodology.
2. Identify the project's guide system implementation and unlock conditions.
3. Apply the dual-system model when designing or reviewing onboarding flow.

## Scope
- Dual tutorial system (in-gameplay vs out-of-gameplay).
- Guide trigger types and sequence data model.
- Feature unlock gating patterns.
- New player timeline design.
- Guide intensity levels. Editor workflows.
- Persistence and server sync.

## 双轨教程模式 (Dual Tutorial System Pattern)

| System | Description | Examples |
|--------|-------------|----------|
| In-gameplay tutorial | Embedded in the game world; player learns by doing | Forced movement, contextual prompts during combat, gated progression |
| Out-of-gameplay guide | UI overlay or separate screen explaining mechanics | Pop-up tips, help pages, video tutorials, codex entries |

Design principle: Teach through action first; provide reference material second.

## 引导触发类型 (Guide Trigger Types)

| Trigger Type | Fires When | Use Case |
|--------------|-----------|----------|
| Zone-based | Player enters a spatial region | Exploration tutorials, area introductions |
| Condition-based | Game state meets criteria (level, quest, item) | System unlock tutorials |
| UI-event-based | Player opens a UI panel for the first time | Feature explanation overlays |
| Time-based | Elapsed time since account creation or last login | Re-engagement reminders |
| Failure-based | Player fails N times | Adaptive difficulty hints |

## 引导序列数据模型 (Guide Sequence Data Model)

```
Guide {
  guideId, guideName, priority, triggerCondition,
  prerequisiteGuides[],
  steps[]: Step {
    stepIndex, type (dialogue/highlight/action/wait),
    targetUI or targetWorldObject,
    text/locKey, voiceover (optional),
    completionCondition, timeoutBehavior
  },
  onComplete: { markFlag, grantReward (optional), unlockNext }
}
```

## 功能解锁门控模式 (Feature Unlock Gating Pattern)

```
System Exists (code deployed)
  → Unlock Condition Met (player level, quest complete, tutorial done)
    → Feature Visible (UI element appears)
      → Tutorial Triggered (guide plays on first access)
        → Feature Fully Available (player can use freely)
```

Gating prevents information overload; each system revealed progressively.

## 新手时间线设计 (New Player Timeline Methodology)

1. **Minutes 0–5**: Core loop introduced (move, attack, loot).
2. **Minutes 5–15**: First system layers (skills, equipment).
3. **Day 1 session**: Primary progression loop complete (quest→fight→reward→upgrade).
4. **Day 2–3**: Social features, secondary systems unlocked.
5. **Week 1**: All core systems accessible; player self-directed.

Map each unlock to specific player actions, not just elapsed time.

## 引导强度等级 (Guide Intensity Levels)

| Level | Behavior | Player Agency |
|-------|----------|--------------|
| Forced | Screen locked; only guided action allowed | None |
| Soft | Highlighted target; other actions possible but discouraged | Low |
| Hint | Subtle indicator (pulse, arrow); easily dismissed | High |
| Passive | Entry in help/codex; player must seek it | Full |

Principle: Use forced only for critical first-time actions; escalate to softer modes quickly.

## 引导编辑器工作流 (Guide Editor Workflow)

1. Author guide sequence in visual editor (node graph or timeline).
2. Assign trigger conditions and prerequisites.
3. Preview in-editor with mock player state.
4. Export to config format (JSON/table).
5. Validate: no circular prerequisites, all target refs exist.
6. Test in-game with fresh account.

## 引导持久化与服务器同步 (Persistence & Server Sync)

- Completed guide flags stored server-side (prevent re-triggering on reinstall).
- Progress within a multi-step guide stored locally (resume on disconnect).
- Server authoritative for unlock conditions; client requests guide state on login.
- Analytics event fired on guide start, each step completion, and guide skip.

## Standard Workflow
1. Map feature unlock order to player timeline.
2. For each unlock, design guide sequence (trigger + steps + completion).
3. Assign intensity level appropriate to feature importance.
4. Author in guide editor; validate prerequisites.
5. Test with fresh account through full Day 1 flow.
6. Analyze skip/completion rates post-launch; iterate.

## Output Contract
- Complete guide sequence definitions with triggers and steps.
- Feature unlock dependency graph (DAG, no cycles).
- New player timeline document (minute-by-minute for Day 1).
- Intensity level justified per guide.
- Validation report: no broken refs or circular dependencies.
