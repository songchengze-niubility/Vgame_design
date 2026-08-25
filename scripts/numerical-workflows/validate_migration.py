#!/usr/bin/env python3
"""验证单仓数值生产蓝图、裁决一致性以及正式配置写入默认拒绝。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ROOT = REPO_ROOT / "numerical-workflows" / "v2"
BEGIN = "<!-- VGAME_PARAMETER_JSON_BEGIN -->"
END = "<!-- VGAME_PARAMETER_JSON_END -->"


def digest(path: Path) -> str:
    if path.suffix.lower() in {".py", ".md", ".json"}:
        normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rv_rows(parameter_path: Path) -> list[tuple[int, int]]:
    text = parameter_path.read_text(encoding="utf-8")
    block = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    if block.startswith("```json"):
        block = block[len("```json") :].lstrip("\r\n")
    if block.endswith("```"):
        block = block[:-3].rstrip("\r\n")
    payload = json.loads(block)
    sheet = next(item for item in payload["sheets"] if item["name"] == "房车参数")
    rows = sheet["rows"]
    title = next(index for index, row in enumerate(rows) if row and row[0] == "房车强化结果")
    results = []
    for row in rows[title + 2 :]:
        if not row or not row[0]:
            break
        results.append((int(row[1]), int(row[2])))
    return results


def run_checks(report_path: Path | None = None) -> tuple[list[dict], dict]:
    manifest = load_json(WORKFLOW_ROOT / "workflow-manifest.json")
    overrides = load_json(WORKFLOW_ROOT / "governance-overrides.json")
    rulings = {item["rulingId"]: item for item in load_json(REPO_ROOT / overrides["canonicalRulings"])["rulings"]}
    rows = manifest["files"]
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"gate": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    missing = []
    changed = []
    portability = []
    outdated_ew_conclusions = []
    for row in rows:
        path = REPO_ROOT / row["repositoryPath"]
        if not path.is_file():
            missing.append(row["repositoryPath"])
            continue
        if digest(path) != row["migratedSha256"]:
            changed.append(row["repositoryPath"])
        if path.suffix.lower() in {".py", ".md"}:
            text = path.read_text(encoding="utf-8")
            if re.search(r"(?i)[a-z]:[\\/]+(?:数值文档|vgame(?:[\\/]|_design))", text):
                portability.append(row["repositoryPath"])
            if path.suffix.lower() == ".md" and re.search(r"专武(?:已|当前版本)?废弃|专武（已废弃）|当前版本已移除专武系统", text):
                outdated_ew_conclusions.append(row["repositoryPath"])

    counts = manifest["counts"]
    check("M01 CompleteInventory", len(rows) == counts["files"] and not missing, {"files": len(rows), "missing": missing})
    check(
        "M02 ImmutableMigrationHashes",
        not changed and manifest.get("contentHashPolicy") == "TEXT_UTF8_NORMALIZED_LF_BINARY_RAW_SHA256",
        {"changed": changed, "contentHashPolicy": manifest.get("contentHashPolicy")},
    )
    python_count = sum(row["repositoryPath"].endswith(".py") for row in rows)
    check("M03 AllProductionScripts", python_count == counts["originalPythonFiles"] == counts["migratedPythonFiles"], {"original": counts["originalPythonFiles"], "migrated": python_count})
    workbook_count = sum(row["repositoryPath"].endswith(".xlsx") for row in rows)
    check("M04 ControlledWorkbookInputs", workbook_count == counts["inputWorkbooks"], {"expected": counts["inputWorkbooks"], "actual": workbook_count})
    expected_workbooks = {row["repositoryPath"] for row in rows if row["repositoryPath"].endswith(".xlsx")}
    actual_workbooks = {path.relative_to(REPO_ROOT).as_posix() for path in WORKFLOW_ROOT.rglob("*.xlsx")}
    check("M04B NoGeneratedWorkbooksInSource", actual_workbooks == expected_workbooks, {"unexpected": sorted(actual_workbooks - expected_workbooks), "missing": sorted(expected_workbooks - actual_workbooks)})
    legacy_count = sum(row["role"] == "LEGACY_EDITABLE_SOURCE_WORKBOOK" for row in rows)
    check("M05 SiblingWorkbookCompatibility", legacy_count == counts["legacyWorkbooks"], {"expected": counts["legacyWorkbooks"], "actual": legacy_count})
    check("M06 PortableNumericalSources", not portability and manifest["legacyExternalSourceRequiredAtRuntime"] is False, {"machinePaths": portability, "externalNumericalSourceRequired": manifest["legacyExternalSourceRequiredAtRuntime"]})

    guarded = [row for row in rows if row["requiresExplicitFormalWriteApproval"]]
    guard_errors = []
    for row in guarded:
        path = REPO_ROOT / row["repositoryPath"]
        text = path.read_text(encoding="utf-8")
        if 'VGAME_ALLOW_FORMAL_CONFIG_WRITE") != "USER_APPROVED"' not in text:
            guard_errors.append({"tool": row["repositoryPath"], "reason": "guard missing"})
            continue
        env = os.environ.copy()
        env.pop("VGAME_ALLOW_FORMAL_CONFIG_WRITE", None)
        env["PYTHONUTF8"] = "1"
        attempt = subprocess.run([sys.executable, os.fspath(path)], cwd=REPO_ROOT, env=env, text=True, capture_output=True, encoding="utf-8", errors="replace", check=False)
        if attempt.returncode == 0 or "explicit user authorization required" not in attempt.stderr:
            guard_errors.append({"tool": row["repositoryPath"], "returncode": attempt.returncode, "stderr": attempt.stderr[-500:]})
    check("M07 FormalConfigWriteDenied", bool(guarded) and not guard_errors and overrides["formalConfigWriteDefault"] == "DENY", {"guardedTools": len(guarded), "errors": guard_errors})

    rv_override = overrides["rules"]["RULING-RV-C"]
    expected_rv = list(zip(rv_override["randomStrengtheningProgress"], rv_override["weights"]))
    actual_rv = rv_rows(WORKFLOW_ROOT / rv_override["productionParameterSource"])
    check("M08 RvLatestRulingC", rulings["RULING-RV-C"]["decisionLabel"] == "C" and actual_rv == expected_rv, {"expected": expected_rv, "actual": actual_rv})

    ew = overrides["rules"]["RULING-EW-B"]
    stage_source = (WORKFLOW_ROOT / "framework" / "02_AI规则" / "stage_final_documents_from_md.py").read_text(encoding="utf-8")
    check("M09 ExclusiveWeaponCompatibilityB", rulings["RULING-EW-B"]["decisionLabel"] == "B" and ew["compatibilityMajorVersions"] == 1 and ew["compatibilityArtifact"] in stage_source, {"decision": rulings["RULING-EW-B"]["decisionLabel"], "compatibilityMajorVersions": ew["compatibilityMajorVersions"], "implementationStatus": ew["implementationStatus"]})
    check("M09B NoSupersededExclusiveWeaponConclusion", not outdated_ew_conclusions, {"outdatedConclusions": outdated_ew_conclusions})
    check("M10 SingleCanonicalAuthority", manifest["authority"] == "knowledge-base/README.md" and overrides["independentFinalAcceptance"] == "PENDING", {"authority": manifest["authority"], "independentFinalAcceptance": overrides["independentFinalAcceptance"]})
    stale_knowledge_locators = []
    legacy_numeric_disk = re.compile(r"(?i)[a-z]:[\\/]+数值文档[\\/]+数值文档[\\/]+框架v2")
    for path in (REPO_ROOT / "knowledge-base").rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md"} and legacy_numeric_disk.search(path.read_text(encoding="utf-8-sig")):
            stale_knowledge_locators.append(path.relative_to(REPO_ROOT).as_posix())
    stale_skill_routes = []
    for path in (
        REPO_ROOT / "skills" / "game-numerical-analysis" / "SKILL.md",
        REPO_ROOT / "skills" / "senior-game-economy" / "SKILL.md",
        REPO_ROOT / "skills" / "vgame-core-understanding" / "references" / "evidence-map.md",
    ):
        text = path.read_text(encoding="utf-8-sig")
        if re.search(r"VGAME_SOURCE_DOCS_ROOT[^\r\n]*框架v2", text):
            stale_skill_routes.append(path.relative_to(REPO_ROOT).as_posix())
    check(
        "M10B SingleRepositoryKnowledgeLocators",
        not stale_knowledge_locators and not stale_skill_routes,
        {"staleKnowledgeLocators": stale_knowledge_locators, "staleSkillRoutes": stale_skill_routes},
    )

    if report_path is not None:
        report = load_json(report_path)
        check("M11 FullProductionRun", report.get("status") == "PASS" and report.get("generationJobs") == counts["mainGenerationJobs"], {"status": report.get("status"), "jobs": report.get("generationJobs")})
        check("M12 FinalArtifactCount", report.get("finalWorkbookCount") == counts["expectedFinalWorkbooks"], {"expected": counts["expectedFinalWorkbooks"], "actual": report.get("finalWorkbookCount")})
        check("M13 DynamicValidation", report.get("dynamicValidationStatus") == "PASS" and report.get("dynamicGateCount") == 6, {"status": report.get("dynamicValidationStatus"), "gates": report.get("dynamicGateCount")})
        check("M14 ExternalNumericalDiskDisabled", report.get("externalNumericalSourceAvailable") is False, {"externalNumericalSourceAvailable": report.get("externalNumericalSourceAvailable")})

    return checks, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-report", type=Path)
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args()
    checks, manifest = run_checks(args.production_report)
    payload = {"schema": "vgame-numerical-production-migration-validation/v1", "overallStatus": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "passed": sum(item["status"] == "PASS" for item in checks), "total": len(checks), "counts": manifest["counts"], "checks": checks}
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overallStatus"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
