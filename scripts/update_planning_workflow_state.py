#!/usr/bin/env python3
"""Update a feature's planning-workflow state file.

维护 ``${VGAME_OUTPUT_ROOT}/<功能短名>/00-workflow-state.json``。

状态文件是进度辅助；用户明确声明和实际文件证据优先级更高（见门禁契约）。
本脚本是阶段状态与人类门禁的唯一机器写入入口；口头说明不能代替它。

用法::

    # 记录某阶段产出
    python scripts/update_planning_workflow_state.py --feature "<功能名>" \
        --phase ui --outcome success --actor ui-prototype \
        --next-action excel --evidence "ui/index.html"

    # 翻转人类门禁（例如契约已确认）
    python scripts/update_planning_workflow_state.py --feature "<功能名>" \
        --set-gate contract_confirmed=true

    # 最终验收（仅用户明确验收后运行；这是设置 delivery_accepted 的唯一入口）
    python scripts/update_planning_workflow_state.py --feature "<功能名>" --accept-delivery

实现依据：skills/planning-feature-workflow/references/planning-workflow-gate-contract.md
与 workflow-state.example.json。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vgame_paths  # noqa: E402

PHASES = [
    "reference", "contract", "clarification", "core_design", "specialists",
    "review", "ui", "figma_ui_plan", "figma_target", "figma_ui",
    "excel", "acceptance", "delivery", "change_sync", "complete",
]
OUTCOMES = ["success", "failure", "needs_revision", "blocked", "waiting_human"]
REWORK_OUTCOMES = {"failure", "needs_revision"}
HUMAN_GATES = [
    "contract_confirmed", "clarification_resolved", "review_approved",
    "figma_ui_plan_confirmed", "figma_target_confirmed", "ui_mockup_approved",
    "acceptance_approved", "delivery_accepted",
]
# attempts_by_phase 跟踪自动返工次数，键与 example 一致（不含 complete）。
ATTEMPT_PHASES = [p for p in PHASES if p != "complete"]

STATE_FILE = "00-workflow-state.json"
MAX_AUTO_ATTEMPTS = 2


def default_state(feature: str) -> dict[str, Any]:
    return {
        "feature": feature,
        "current_phase": "reference",
        "execution_mode": "STANDARD",
        "artifact_profile": "DOC_UI",
        "risk_tier": "MEDIUM",
        "last_actor": "",
        "last_outcome": "",
        "human_gates": {gate: False for gate in HUMAN_GATES},
        "attempts_by_phase": {phase: 0 for phase in ATTEMPT_PHASES},
        "block_reason": "",
        "history": [],
        "updated_at": "",
    }


def parse_gate(raw: str) -> tuple[str, bool]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError(f"--set-gate 需要 NAME=true/false，得到 {raw!r}")
    name, _, value = raw.partition("=")
    name = name.strip()
    value = value.strip().lower()
    if name not in HUMAN_GATES:
        raise argparse.ArgumentTypeError(f"未知人类门禁: {name}（合法: {HUMAN_GATES}）")
    if value not in ("true", "false"):
        raise argparse.ArgumentTypeError(f"门禁值必须是 true/false，得到 {value!r}")
    return name, value == "true"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--feature", required=True, help="功能短名")
    parser.add_argument("--phase", choices=PHASES, help="本次推进到的阶段")
    parser.add_argument("--outcome", choices=OUTCOMES, help="阶段结果")
    parser.add_argument("--actor", default="", help="执行角色")
    parser.add_argument("--next-action", default="", help="下一步动作")
    parser.add_argument("--evidence", default="", help="证据（文件路径或说明）")
    parser.add_argument("--set-gate", action="append", default=[], type=parse_gate,
                        metavar="NAME=BOOL", help="设置人类门禁，可重复")
    parser.add_argument("--accept-delivery", action="store_true",
                        help="设置 delivery_accepted=true 并进入 complete（仅用户明确验收后运行）")
    parser.add_argument("--resolve-clarifications", action="store_true",
                        help="设置 clarification_resolved=true（阻塞澄清已逐条确认并同步回契约）")
    parser.add_argument("--approve-acceptance", action="store_true",
                        help="设置 acceptance_approved=true（追踪矩阵与验收用例完整且可执行）")
    parser.add_argument("--approve-ui-mockup", action="store_true",
                        help="设置 ui_mockup_approved=true（Codex 的 UI 示意图已经用户评审，可并入 Excel）")
    parser.add_argument("--close-change", action="store_true",
                        help="标记当前变更已闭环并记入 history（须配合 --phase change_sync）")
    parser.add_argument("--mode", help="执行模式 FAST/STANDARD/REFRESH")
    parser.add_argument("--profile", help="交付档位")
    parser.add_argument("--risk", help="风险档位 LOW/MEDIUM/HIGH")
    parser.add_argument("--block-reason", default="", help="outcome=blocked 时的阻塞原因")
    parser.add_argument("--output-root", type=Path, default=None,
                        help="覆盖 VGAME_OUTPUT_ROOT")
    return parser.parse_args()


def load_state(path: Path, feature: str) -> dict[str, Any]:
    if not path.is_file():
        return default_state(feature)
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[WARN] 现有状态文件无法解析，将重建: {exc}")
        return default_state(feature)
    if not isinstance(data, dict):
        return default_state(feature)
    # 用默认结构补齐缺失键，保持向后兼容。
    base = default_state(feature)
    base.update(data)
    base["human_gates"] = {**{g: False for g in HUMAN_GATES}, **data.get("human_gates", {})}
    base["attempts_by_phase"] = {**{p: 0 for p in ATTEMPT_PHASES},
                                 **data.get("attempts_by_phase", {})}
    if not isinstance(base.get("history"), list):
        base["history"] = []
    return base


def main() -> int:
    args = parse_args()
    out_root = args.output_root.resolve() if args.output_root else vgame_paths.output_root()
    feature_dir = out_root / args.feature
    feature_dir.mkdir(parents=True, exist_ok=True)
    state_path = feature_dir / STATE_FILE

    state = load_state(state_path, args.feature)
    now = datetime.now(timezone.utc).isoformat()
    notes: list[str] = []

    if args.mode:
        state["execution_mode"] = args.mode
    if args.profile:
        state["artifact_profile"] = args.profile
    if args.risk:
        state["risk_tier"] = args.risk

    if args.phase:
        state["current_phase"] = args.phase
    if args.actor:
        state["last_actor"] = args.actor
    if args.outcome:
        state["last_outcome"] = args.outcome
        if args.outcome in REWORK_OUTCOMES and args.phase in state["attempts_by_phase"]:
            state["attempts_by_phase"][args.phase] += 1
            attempts = state["attempts_by_phase"][args.phase]
            if attempts > MAX_AUTO_ATTEMPTS:
                notes.append(
                    f"阶段 {args.phase} 自动返工已达 {attempts} 次，超过上限 "
                    f"{MAX_AUTO_ATTEMPTS}，应置 blocked 交用户决策")
        if args.outcome == "blocked":
            state["block_reason"] = args.block_reason or state.get("block_reason", "")
        elif args.outcome == "success":
            state["block_reason"] = ""

    for name, value in args.set_gate:
        state["human_gates"][name] = value
        notes.append(f"门禁 {name} -> {value}")

    # 便捷门禁别名，与子 skill 的收尾命令保持一致（见各 planning-* SKILL.md）。
    if args.resolve_clarifications:
        state["human_gates"]["clarification_resolved"] = True
        notes.append("门禁 clarification_resolved -> True（--resolve-clarifications）")
    if args.approve_acceptance:
        state["human_gates"]["acceptance_approved"] = True
        notes.append("门禁 acceptance_approved -> True（--approve-acceptance）")
    if args.approve_ui_mockup:
        state["human_gates"]["ui_mockup_approved"] = True
        notes.append("门禁 ui_mockup_approved -> True（--approve-ui-mockup）")
    if args.close_change:
        notes.append("变更已闭环（--close-change）")

    if args.accept_delivery:
        state["human_gates"]["delivery_accepted"] = True
        state["current_phase"] = "complete"
        state["last_outcome"] = "success"
        notes.append("delivery_accepted=true，进入 complete（用户验收）")

    if args.phase or args.outcome or args.evidence or args.actor:
        state["history"].append({
            "at": now,
            "actor": args.actor,
            "phase": args.phase or state.get("current_phase", ""),
            "outcome": args.outcome or "",
            "next_action": args.next_action,
            "evidence": args.evidence,
        })

    state["updated_at"] = now

    try:
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    except OSError as exc:
        print(f"[FAIL] 无法写入状态文件: {exc}")
        return 1

    print(f"[OK] {STATE_FILE} 已更新: {state_path}")
    print(f"     current_phase={state['current_phase']} last_outcome={state['last_outcome']}")
    for note in notes:
        print(f"     - {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
