#!/usr/bin/env python3
"""Verify planning-workflow delivery artifacts by delivery profile.

第9步交付总校验。按交付档位检查一个功能输出目录是否结构完整，并生成
``08-delivery-report.json``。

用法::

    python scripts/verify_design_artifacts.py "<功能输出目录>" --profile DOC_UI

自动校验只证明结构通过；最终 Excel 排版、规则正确性和 UI 表达仍须用户人工确认。
本脚本不会、也不得把 ``delivery_accepted`` 设为 true。

实现依据：
- skills/planning-feature-workflow/references/planning-workflow-gate-contract.md 的「完成判定」表
- skills/planning-feature-workflow/SKILL.md 第9步
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"

# 各档位的交付物要求，对应门禁契约「完成判定」表。
PROFILES = {
    "ADVICE",
    "DOC_ONLY",
    "UI_ONLY",
    "DOC_UI",
    "FIGMA_UI",
    "DOC_FIGMA",
    "IMPLEMENTATION",
}

RULE_ID_RE = re.compile(r"\b(?:R|RULE)-[A-Z0-9][A-Z0-9-]*\b")

CONTRACT_DOC = "00-design-contract.md"
TRACE_DOC = "05-traceability-matrix.md"
ACCEPT_DOC = "06-acceptance-cases.md"
STATE_FILE = "00-workflow-state.json"
REPORT_FILE = "08-delivery-report.json"


class Report:
    """收集分级检查结果。"""

    def __init__(self) -> None:
        self.checks: list[dict[str, str]] = []

    def add(self, level: str, check_id: str, message: str) -> None:
        self.checks.append({"level": level, "id": check_id, "message": message})

    def passed(self, check_id: str, message: str) -> None:
        self.add("PASS", check_id, message)

    def warn(self, check_id: str, message: str) -> None:
        self.add("WARN", check_id, message)

    def fail(self, check_id: str, message: str) -> None:
        self.add("FAIL", check_id, message)

    @property
    def errors(self) -> int:
        return sum(1 for c in self.checks if c["level"] == "FAIL")

    @property
    def warnings(self) -> int:
        return sum(1 for c in self.checks if c["level"] == "WARN")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("feature_dir", type=Path, help="功能输出目录，如 ${VGAME_OUTPUT_ROOT}/<功能短名>")
    parser.add_argument("--profile", help="交付档位；省略时从 00-workflow-state.json 读取")
    parser.add_argument("--skill-root", type=Path, default=None,
                        help="Skill 根目录，用于定位 UI/Figma 子校验器；默认 VGAME_SKILL_ROOT 或 <repo>/skills")
    parser.add_argument("--no-subvalidators", action="store_true",
                        help="跳过对 validate_ui_assets.py / validate_figma_handoff.py 的委派调用")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return None


def resolve_profile(feature_dir: Path, requested: str | None, report: Report) -> str | None:
    profile = requested
    if not profile:
        state = read_json(feature_dir / STATE_FILE)
        if state:
            profile = state.get("artifact_profile") or state.get("delivery_profile") or state.get("profile")
        if not profile:
            report.fail("profile.missing",
                        "未提供 --profile 且 00-workflow-state.json 无 delivery_profile")
            return None
    profile = str(profile).upper()
    if profile not in PROFILES:
        report.fail("profile.invalid", f"未知交付档位: {profile}（合法: {sorted(PROFILES)}）")
        return None
    report.passed("profile", f"交付档位: {profile}")
    return profile


def require_file(feature_dir: Path, rel: str, report: Report, check_id: str) -> Path | None:
    path = feature_dir / rel
    if path.is_file():
        report.passed(check_id, f"存在: {rel}")
        return path
    report.fail(check_id, f"缺失: {rel}")
    return None


def find_xlsx(feature_dir: Path) -> Path | None:
    preferred = sorted(feature_dir.glob("*策划案.xlsx"))
    if preferred:
        return preferred[0]
    others = sorted(feature_dir.glob("*.xlsx"))
    return others[0] if others else None


def check_excel(feature_dir: Path, report: Report, require_embedded_image: bool) -> None:
    xlsx = find_xlsx(feature_dir)
    if xlsx is None:
        report.fail("excel.missing", "缺失正式 Excel 策划案 (*.xlsx)")
        return
    report.passed("excel", f"存在 Excel: {xlsx.name}")
    try:
        with zipfile.ZipFile(xlsx) as zf:
            names = zf.namelist()
            has_media = any(n.startswith("xl/media/") for n in names)
            sheet_xml = b"".join(
                zf.read(n) for n in names if n.startswith("xl/worksheets/") and n.endswith(".xml")
            )
    except (OSError, zipfile.BadZipFile) as exc:
        report.fail("excel.corrupt", f"Excel 无法作为 xlsx 打开: {exc}")
        return

    if require_embedded_image:
        if has_media:
            report.passed("excel.embedded_image", "Excel 含嵌入图片 (xl/media/)")
        else:
            report.fail("excel.embedded_image",
                        "Excel 未嵌入任何图片；DOC_UI/DOC_FIGMA 要求页面主图与组件详图嵌入正文")
    elif has_media:
        report.passed("excel.embedded_image", "Excel 含嵌入图片 (xl/media/)")

    if b"<f>" in sheet_xml or b"<f " in sheet_xml:
        report.passed("excel.formula", "Excel 含公式单元格")
    else:
        report.warn("excel.formula", "Excel 未检出任何公式单元格，请确认数值是否应由公式驱动")


def check_ui(feature_dir: Path, report: Report) -> None:
    ui_dir = feature_dir / "ui"
    if not ui_dir.is_dir():
        report.fail("ui.dir", "缺失 ui/ 目录")
        return
    require_file(feature_dir, "ui/index.html", report, "ui.index")
    require_file(feature_dir, "ui/ui-asset-manifest.json", report, "ui.manifest")
    pngs = [p for p in ui_dir.rglob("*.png") if "assets" not in p.relative_to(ui_dir).parts]
    if pngs:
        report.passed("ui.png", f"页面/组件 PNG 数量: {len(pngs)}")
    else:
        report.fail("ui.png", "ui/ 下没有导出的页面/组件 PNG")


def check_figma(feature_dir: Path, report: Report) -> None:
    require_file(feature_dir, "03-specialist-results/figma-ui-plan.md", report, "figma.plan")
    require_file(feature_dir, "03-specialist-results/figma-target.json", report, "figma.target")
    require_file(feature_dir, "figma/figma-ui-handoff-manifest.json", report, "figma.manifest")
    previews = list((feature_dir / "figma" / "previews").glob("*.png")) if (feature_dir / "figma" / "previews").is_dir() else []
    if previews:
        report.passed("figma.previews", f"预览 PNG 数量: {len(previews)}")
    else:
        report.fail("figma.previews", "figma/previews/ 下没有页面/组件预览 PNG")

    state = read_json(feature_dir / STATE_FILE) or {}
    for field in ("figma_ui_plan_confirmed", "figma_target_confirmed"):
        if state.get(field) is True:
            report.passed(f"figma.{field}", f"人类门禁已确认: {field}")
        else:
            report.fail(f"figma.{field}",
                        f"人类门禁未确认: {field}=true（未确认前 Figma 交付不算完成）")


def extract_rule_ids(path: Path | None) -> set[str]:
    if path is None:
        return set()
    text = read_text(path)
    if text is None:
        return set()
    return set(RULE_ID_RE.findall(text))


def check_traceability(feature_dir: Path, report: Report) -> None:
    trace = require_file(feature_dir, TRACE_DOC, report, "trace.matrix")
    accept = require_file(feature_dir, ACCEPT_DOC, report, "accept.cases")
    contract = feature_dir / CONTRACT_DOC

    contract_rules = extract_rule_ids(contract if contract.is_file() else None)
    trace_rules = extract_rule_ids(trace)
    accept_rules = extract_rule_ids(accept)

    if not contract_rules:
        report.warn("rules.none",
                    f"{CONTRACT_DOC} 中未检出稳定规则 ID (R-* / RULE-*)，无法做规则对应校验")
        return

    # 核心规则不得缺验收用例 / 不得缺追踪映射。
    missing_in_trace = sorted(contract_rules - trace_rules)
    missing_in_accept = sorted(contract_rules - accept_rules)
    if missing_in_trace:
        report.fail("rules.trace_gap",
                    f"以下契约规则缺少追踪映射: {', '.join(missing_in_trace)}")
    else:
        report.passed("rules.trace_gap", "全部契约规则已出现在追踪矩阵")
    if missing_in_accept:
        report.fail("rules.accept_gap",
                    f"以下契约规则缺少验收用例: {', '.join(missing_in_accept)}")
    else:
        report.passed("rules.accept_gap", "全部契约规则已出现在验收用例")

    # 验收用例不得缺规则来源。
    orphan_accept = sorted(accept_rules - contract_rules)
    if orphan_accept:
        report.fail("rules.accept_orphan",
                    f"以下验收用例引用了契约外规则: {', '.join(orphan_accept)}")
    else:
        report.passed("rules.accept_orphan", "验收用例引用的规则均可回到契约")


def default_skill_root(repo_root: Path, override: Path | None) -> Path:
    if override:
        return override
    env = os.environ.get("VGAME_SKILL_ROOT")
    if env:
        return Path(env)
    return repo_root / "skills"


def run_subvalidator(label: str, script: Path, args: list[str], report: Report, check_id: str) -> None:
    if not script.is_file():
        report.warn(check_id, f"{label} 子校验器缺失，已跳过深度校验: {script.name}")
        return
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        report.warn(check_id, f"{label} 子校验器无法运行: {exc}")
        return
    if proc.returncode == 0:
        report.passed(check_id, f"{label} 深度校验通过")
    else:
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-3:]
        report.fail(check_id, f"{label} 深度校验失败: {' | '.join(tail) or '见脚本输出'}")


def verify(feature_dir: Path, profile: str, skill_root: Path, use_sub: bool, report: Report) -> None:
    doc_profiles = {"DOC_ONLY", "DOC_UI", "DOC_FIGMA"}
    ui_profiles = {"UI_ONLY", "DOC_UI"}
    figma_profiles = {"FIGMA_UI", "DOC_FIGMA"}
    embed_profiles = {"DOC_UI", "DOC_FIGMA"}

    if profile == "ADVICE":
        report.passed("advice", "ADVICE 档位只给建议，不要求交付文件")
        return

    # 所有交付档位都要求追踪矩阵与验收用例。
    check_traceability(feature_dir, report)

    if profile in doc_profiles:
        check_excel(feature_dir, report, require_embedded_image=profile in embed_profiles)

    if profile in ui_profiles:
        check_ui(feature_dir, report)
        if use_sub:
            run_subvalidator(
                "UI", skill_root / "vgame-ui-prototype" / "scripts" / "validate_ui_assets.py",
                ["--ui-dir", str(feature_dir / "ui"), "--require-components"],
                report, "ui.subvalidator",
            )

    if profile in figma_profiles:
        check_figma(feature_dir, report)
        if use_sub:
            run_subvalidator(
                "Figma",
                skill_root / "vgame-figma-ui" / "scripts" / "validate_figma_handoff.py",
                [
                    "--manifest", str(feature_dir / "figma" / "figma-ui-handoff-manifest.json"),
                    "--contract", str(feature_dir / CONTRACT_DOC),
                    "--plan", str(feature_dir / "03-specialist-results" / "figma-ui-plan.md"),
                    "--target", str(feature_dir / "03-specialist-results" / "figma-target.json"),
                    "--require-previews",
                ],
                report, "figma.subvalidator",
            )

    if profile == "IMPLEMENTATION":
        report.warn("impl.evidence",
                    "IMPLEMENTATION 档位的实际改动与验证证据无法自动确认，须人工核对")


def write_report(feature_dir: Path, profile: str, report: Report) -> dict[str, Any]:
    status = "fail" if report.errors else "pass"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "feature": feature_dir.name,
        "profile": profile,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {"errors": report.errors, "warnings": report.warnings},
        "checks": report.checks,
        "note": "自动校验只证明结构通过；最终排版、规则正确性、UI 表达需用户人工确认。"
                "本脚本不设置 delivery_accepted。",
    }
    out = feature_dir / REPORT_FILE
    try:
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"[WARN] 无法写入 {REPORT_FILE}: {exc}")
    return payload


def main() -> int:
    args = parse_args()
    feature_dir = args.feature_dir.resolve()
    report = Report()

    if not feature_dir.is_dir():
        print(f"[FAIL] 功能目录不存在: {feature_dir}")
        return 2

    repo_root = Path(__file__).resolve().parent.parent
    skill_root = default_skill_root(repo_root, args.skill_root)
    if (skill_root / "skills").is_dir():
        skill_root = skill_root / "skills"

    profile = resolve_profile(feature_dir, args.profile, report)
    if profile is not None:
        verify(feature_dir, profile, skill_root, not args.no_subvalidators, report)

    payload = write_report(feature_dir, profile or "UNKNOWN", report)

    for check in report.checks:
        if check["level"] != "PASS":
            print(f"[{check['level']}] {check['id']}: {check['message']}")
    print(f"=== {payload['status'].upper()} "
          f"(FAIL: {report.errors}, WARN: {report.warnings}) -> {REPORT_FILE} ===")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
