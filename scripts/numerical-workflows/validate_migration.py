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
FORMAL_DOCUMENT_ROOT = WORKFLOW_ROOT / "framework" / "04_数值文档"
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


def parameter_payload(parameter_path: Path) -> dict:
    text = parameter_path.read_text(encoding="utf-8")
    block = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    if block.startswith("```json"):
        block = block[len("```json") :].lstrip("\r\n")
    if block.endswith("```"):
        block = block[:-3].rstrip("\r\n")
    return json.loads(block)


def rv_rows(parameter_path: Path) -> list[tuple[int, int]]:
    payload = parameter_payload(parameter_path)
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
    actual_workbooks = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in WORKFLOW_ROOT.rglob("*.xlsx")
        if FORMAL_DOCUMENT_ROOT not in path.parents
    }
    check(
        "M04B NoGeneratedWorkbooksInSource",
        actual_workbooks == expected_workbooks,
        {"unexpected": sorted(actual_workbooks - expected_workbooks), "missing": sorted(expected_workbooks - actual_workbooks)},
    )

    final_root_relative = FORMAL_DOCUMENT_ROOT.relative_to(REPO_ROOT).as_posix()
    final_workbooks = sorted(FORMAL_DOCUMENT_ROOT.rglob("*.xlsx")) if FORMAL_DOCUMENT_ROOT.is_dir() else []
    final_manifest_path = FORMAL_DOCUMENT_ROOT / "generation-manifest.json"
    final_manifest = load_json(final_manifest_path) if final_manifest_path.is_file() else None
    final_manifest_paths = {
        item["path"] for item in final_manifest.get("artifacts", [])
    } if final_manifest is not None else set()
    actual_final_paths = {path.relative_to(FORMAL_DOCUMENT_ROOT).as_posix() for path in final_workbooks}
    final_hash_errors = []
    if final_manifest is not None:
        for artifact in final_manifest.get("artifacts", []):
            artifact_path = FORMAL_DOCUMENT_ROOT / artifact["path"]
            if not artifact_path.is_file() or digest(artifact_path) != artifact["sha256"]:
                final_hash_errors.append(artifact["path"])
    ignore_check = subprocess.run(
        ["git", "check-ignore", "-q", "--", final_root_relative],
        cwd=REPO_ROOT,
        check=False,
    )
    final_state_valid = (
        not FORMAL_DOCUMENT_ROOT.exists()
        or (
            len(final_workbooks) == counts["expectedFinalWorkbooks"]
            and final_manifest is not None
            and final_manifest.get("xlsx_count") == counts["expectedFinalWorkbooks"]
            and actual_final_paths == final_manifest_paths
            and not final_hash_errors
        )
    )
    check(
        "M04C VersionControlledFormalDocuments",
        manifest.get("formalDocumentRoot") == final_root_relative
        and manifest.get("formalDocumentsVersionControlled") is True
        and ignore_check.returncode == 1
        and final_state_valid,
        {
            "root": final_root_relative,
            "expected": counts["expectedFinalWorkbooks"],
            "actual": len(final_workbooks),
            "publicationState": "PUBLISHED" if final_workbooks else "AWAITING_FIRST_PUBLICATION",
            "gitIgnored": ignore_check.returncode != 1,
            "missingFromManifest": sorted(actual_final_paths - final_manifest_paths),
            "missingFromDirectory": sorted(final_manifest_paths - actual_final_paths),
            "hashErrors": final_hash_errors,
        },
    )
    parameter_registry = load_json(REPO_ROOT / "knowledge-base" / "numerical" / "parameter-registry.json")
    baseline_errors = []
    for scope in ("共享", "养成", "战斗", "节奏"):
        baseline_path = WORKFLOW_ROOT / "framework" / "03_沉淀MD" / "参数基线" / f"{scope}参数基线.md"
        locator = f"03_沉淀MD/参数基线/{scope}参数基线.md#"
        matches = [item for item in parameter_registry["parameterSets"] if item["sourceLocator"].startswith(locator)]
        if len(matches) != 1:
            baseline_errors.append({"scope": scope, "reason": "parameter-registry-match", "actual": len(matches)})
            continue
        parameter = matches[0]
        if parameter["value"] != parameter_payload(baseline_path):
            baseline_errors.append({"scope": scope, "reason": "parameter-payload-drift"})
        if parameter.get("canonicalSourcePath") != baseline_path.relative_to(REPO_ROOT).as_posix():
            baseline_errors.append({"scope": scope, "reason": "canonical-source-path-drift"})
        if parameter.get("canonicalSourceSha256") != digest(baseline_path):
            baseline_errors.append({"scope": scope, "reason": "canonical-source-hash-drift"})
        if parameter.get("authorityRole") != "GIT_MANAGED_PARAMETER_BASELINE":
            baseline_errors.append({"scope": scope, "reason": "canonical-authority-missing"})
    check("M04D CanonicalParameterBaselinesCurrent", not baseline_errors, {"baselines": 4, "errors": baseline_errors})
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
        final_target = REPO_ROOT / report.get("publishedRoot", "")
        validation_target = final_target if final_target.is_dir() else REPO_ROOT / report.get("validatedStagingRoot", "")
        validated_final_count = sum(1 for _ in validation_target.rglob("*.xlsx")) if validation_target.is_dir() else 0
        check(
            "M12 FinalArtifactCount",
            report.get("finalWorkbookCount") == counts["expectedFinalWorkbooks"]
            and validated_final_count == counts["expectedFinalWorkbooks"]
            and report.get("formalDocumentRoot") == final_root_relative
            and (
                report.get("publicationMode") == "STAGING_ONLY"
                or report.get("publishedRoot") == final_root_relative
            ),
            {
                "expected": counts["expectedFinalWorkbooks"],
                "reported": report.get("finalWorkbookCount"),
                "actual": validated_final_count,
                "formalRoot": report.get("formalDocumentRoot"),
                "publicationMode": report.get("publicationMode"),
            },
        )
        check("M13 DynamicValidation", report.get("dynamicValidationStatus") == "PASS" and report.get("dynamicGateCount") == 6, {"status": report.get("dynamicValidationStatus"), "gates": report.get("dynamicGateCount")})
        check("M14 ExternalNumericalDiskDisabled", report.get("externalNumericalSourceAvailable") is False, {"externalNumericalSourceAvailable": report.get("externalNumericalSourceAvailable")})
        check(
            "M15 SourceAndMdZeroDifferences",
            report.get("sourceMdSyncMode") == "CHECK_ONLY"
            and report.get("canonicalSourceOwnedDifferences") == 0
            and report.get("stagingSourceOwnedChanges") == 0,
            {
                "mode": report.get("sourceMdSyncMode"),
                "canonicalDifferences": report.get("canonicalSourceOwnedDifferences"),
                "stagingMutations": report.get("stagingSourceOwnedChanges"),
            },
        )

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
