#!/usr/bin/env python3
"""Report a feature's planning-workflow progress.

读取 ``${VGAME_OUTPUT_ROOT}/<功能短名>/00-workflow-state.json`` 并扫描实际产物，
按门禁契约的优先级（用户声明 > 状态文件 > 实际文件）给出可对账的进度视图。

用法::

    python scripts/planning_workflow_status.py --feature "<功能名>"
    python scripts/planning_workflow_status.py --feature "<功能名>" --json

实现依据：skills/planning-feature-workflow/SKILL.md「启动」与「状态回复」，
references/planning-workflow-gate-contract.md。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vgame_paths  # noqa: E402

STATE_FILE = "00-workflow-state.json"

# (phase, 步骤标签, 证据探测函数)。顺序即推进顺序，用于推断已达阶段。
def _has_file(rel: str) -> Callable[[Path], bool]:
    return lambda d: (d / rel).is_file()


def _has_glob(pattern: str) -> Callable[[Path], bool]:
    return lambda d: any(d.glob(pattern))


def _has_dir_with_files(rel: str) -> Callable[[Path], bool]:
    return lambda d: (d / rel).is_dir() and any((d / rel).iterdir())


PHASE_EVIDENCE: list[tuple[str, str, Callable[[Path], bool]]] = [
    ("reference", "步骤1 任务登记与参考选择", _has_file("01-project-reference.md")),
    ("contract", "步骤2 需求契约与范围确认", _has_file("00-design-contract.md")),
    ("clarification", "步骤3 逐条澄清与决策冻结", _has_file("00-clarification-log.md")),
    ("core_design", "步骤4 核心设计", _has_file("02-core-design.md")),
    ("specialists", "步骤5 专项设计", _has_dir_with_files("03-specialist-results")),
    ("review", "步骤6 一致性评审与规则冻结", _has_file("04-review.md")),
    ("ui", "步骤7A HTML UI 原型资产", _has_file("ui/ui-asset-manifest.json")),
    ("figma_ui", "步骤7B 可编辑 Figma 交付", _has_file("figma/figma-ui-handoff-manifest.json")),
    ("excel", "步骤8 正式 Excel", _has_glob("*.xlsx")),
    ("acceptance", "步骤9 验收追踪", _has_file("06-acceptance-cases.md")),
    ("delivery", "步骤9 成品校验", _has_file("08-delivery-report.json")),
    ("change_sync", "变更循环", _has_file("07-change-log.md")),
]

HUMAN_GATES = [
    "contract_confirmed", "clarification_resolved", "review_approved",
    "figma_ui_plan_confirmed", "figma_target_confirmed",
    "acceptance_approved", "delivery_accepted",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--feature", required=True, help="功能短名")
    parser.add_argument("--output-root", type=Path, default=None, help="覆盖 VGAME_OUTPUT_ROOT")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    return parser.parse_args()


def load_state(feature_dir: Path) -> dict[str, Any] | None:
    path = feature_dir / STATE_FILE
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def detect_artifacts(feature_dir: Path) -> tuple[list[dict[str, str]], str, str]:
    detected: list[dict[str, str]] = []
    reached_phase = ""
    reached_label = "（无产物，疑似未开始）"
    for phase, label, probe in PHASE_EVIDENCE:
        if probe(feature_dir):
            detected.append({"phase": phase, "label": label})
            reached_phase = phase
            reached_label = label
    return detected, reached_phase, reached_label


def open_gates(state: dict[str, Any] | None) -> list[str]:
    if not state:
        return []
    gates = state.get("human_gates", {})
    return [g for g in HUMAN_GATES if not gates.get(g, False)]


def main() -> int:
    args = parse_args()
    out_root = args.output_root.resolve() if args.output_root else vgame_paths.output_root()
    feature_dir = out_root / args.feature

    if not feature_dir.is_dir():
        msg = f"功能目录不存在: {feature_dir}（尚未开始或 VGAME_OUTPUT_ROOT 配置不一致）"
        if args.json:
            print(json.dumps({"feature": args.feature, "exists": False, "message": msg},
                             ensure_ascii=False, indent=2))
        else:
            print(f"[WARN] {msg}")
        return 0

    state = load_state(feature_dir)
    detected, reached_phase, reached_label = detect_artifacts(feature_dir)
    gaps = open_gates(state)

    state_phase = state.get("current_phase", "") if state else ""
    mismatch = bool(state) and state_phase and reached_phase and state_phase != reached_phase

    if args.json:
        print(json.dumps({
            "feature": args.feature,
            "exists": True,
            "state_phase": state_phase,
            "artifact_phase": reached_phase,
            "phase_mismatch": mismatch,
            "detected": detected,
            "open_human_gates": gaps,
            "state": state,
        }, ensure_ascii=False, indent=2))
        return 0

    mode = state.get("execution_mode", "?") if state else "?"
    profile = state.get("artifact_profile", "?") if state else "?"
    risk = state.get("risk_tier", "?") if state else "?"

    print(f"**当前推断阶段**：{reached_label}")
    if not state:
        print("  （未找到 00-workflow-state.json，仅凭实际产物推断）")
    elif mismatch:
        print(f"  ⚠ 状态文件声称 `{state_phase}`，实际产物只到 `{reached_phase}`，请对账")
    print()
    print(f"**执行档位**：{mode} / {profile} / {risk}")
    print()
    print("**已检测到**：")
    if detected:
        for item in detected:
            print(f"- {item['label']}")
    else:
        print("- （无）")
    print()
    print("**下一步**：")
    if gaps and "delivery_accepted" in gaps and reached_phase == "delivery":
        print("1. 交付物已就绪，等待用户最终人工验收")
        print("2. 用户验收后运行：update_planning_workflow_state.py --accept-delivery")
    else:
        print("1. 推进至下一未完成阶段，或修复上面的对账差异")
        print("2. 阶段收尾后运行：update_planning_workflow_state.py 记录状态")
    print()
    print("**需您确认（未通过的人类门禁）**：")
    if gaps:
        for gate in gaps:
            print(f"- {gate}")
    else:
        print("- （无未决门禁）" if state else "- 状态文件缺失，门禁未知")
    return 0


if __name__ == "__main__":
    sys.exit(main())
