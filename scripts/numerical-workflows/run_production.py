#!/usr/bin/env python3
"""从 Git 权威源隔离重建全部数值终稿；门禁通过后发布到受版本管理的工作流目录。"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ROOT = REPO_ROOT / "numerical-workflows" / "v2"
OUTPUT_ROOT = REPO_ROOT / "output" / "numerical-production-workflow-v2"
FORMAL_DOCUMENT_ROOT = WORKFLOW_ROOT / "framework" / "04_数值文档"


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def local_settings() -> dict[str, str]:
    path = REPO_ROOT / "local.env.bat"
    if not path.is_file():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r'^\s*set\s+"?([A-Za-z_][A-Za-z0-9_]*)=(.*?)"?\s*$', line)
        if match:
            result[match.group(1)] = match.group(2).rstrip('"')
    return result


def command(name: str, arguments: list[str], *, cwd: Path, env: dict[str, str], log_dir: Path) -> None:
    print(f"[RUN] {name}", flush=True)
    process = subprocess.run(arguments, cwd=cwd, env=env, text=True, capture_output=True, encoding="utf-8", errors="replace", check=False)
    log_path = log_dir / f"{name}.log"
    log_path.write_text(process.stdout + ("\n[STDERR]\n" + process.stderr if process.stderr else ""), encoding="utf-8")
    if process.returncode:
        print(process.stdout[-5000:], file=sys.stderr)
        if process.stderr:
            print(process.stderr[-5000:], file=sys.stderr)
        raise RuntimeError(f"{name} failed with exit={process.returncode}; log={log_path}")
    for line in process.stdout.splitlines()[-4:]:
        print(f"  {line}", flush=True)


def publish_documents(stage: Path, published: Path, previous_root: Path, run_id: str) -> tuple[Path | None, str]:
    if not published.exists():
        stage.rename(published)
        return None, "DIRECTORY_SWAP"

    previous_root.mkdir(exist_ok=True)
    archived_previous = previous_root / f"workflow-{run_id}"
    try:
        published.rename(archived_previous)
    except PermissionError:
        # Windows 允许其他应用持有目录句柄；此时仍可替换未被锁定的单个文件。
        print("[WARN] 正式目录被占用；完整归档后使用可回滚的逐文件原子发布。", flush=True)
        shutil.copytree(published, archived_previous)
        old_files = {
            path.relative_to(published).as_posix()
            for path in published.rglob("*")
            if path.is_file()
        }
        new_files = {
            path.relative_to(stage).as_posix()
            for path in stage.rglob("*")
            if path.is_file()
        }
        if old_files != new_files:
            raise RuntimeError(
                "占用目录的安全发布要求新旧文件清单完全一致；"
                f"新增={sorted(new_files - old_files)}，缺失={sorted(old_files - new_files)}"
            )

        replaced: list[str] = []
        ordered = sorted(new_files, key=lambda relative: (relative == "generation-manifest.json", relative))
        try:
            for relative in ordered:
                os.replace(stage / relative, published / relative)
                replaced.append(relative)
        except Exception as exc:
            rollback_errors = []
            for relative in reversed(replaced):
                try:
                    shutil.copy2(archived_previous / relative, published / relative)
                except Exception as rollback_exc:
                    rollback_errors.append({"path": relative, "error": str(rollback_exc)})
            if rollback_errors:
                raise RuntimeError(f"正式文档发布失败且回滚不完整：{rollback_errors}") from exc
            raise RuntimeError("正式文档发布失败；已从完整归档恢复原版本") from exc
        return archived_previous, "IN_PLACE_FILE_SWAP_WITH_ARCHIVE"

    try:
        stage.rename(published)
    except Exception:
        if not published.exists():
            archived_previous.rename(published)
        raise
    return archived_previous, "DIRECTORY_SWAP"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    parser.add_argument("--config-root", type=Path, help="正式 Datas 只读来源；默认读取本机配置")
    parser.add_argument("--no-publish", action="store_true", help="仅完成 output staging 与验算，不更新 Git 管理的正式数值文档")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("--run-id 只能包含字母、数字、下划线和连字符")

    manifest = json.loads((WORKFLOW_ROOT / "workflow-manifest.json").read_text(encoding="utf-8"))
    settings = local_settings()
    configured_root = args.config_root or Path(os.environ.get("VGAME_CONFIG_DATAS") or settings.get("VGAME_CONFIG_DATAS", ""))
    if not configured_root.is_dir() or not (configured_root / "items" / "Items.xlsx").is_file():
        raise SystemExit("VGAME_CONFIG_DATAS 必须指向可读的正式 Datas；真实配置只作只读证据，不会写入。")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    run_root = OUTPUT_ROOT / "runs" / args.run_id
    run_root.mkdir(parents=True, exist_ok=False)
    runtime_root = run_root / "framework-v2"
    report_root = run_root / "reports"
    report_root.mkdir()
    stage = runtime_root / f"_staging_04_{args.run_id}"
    published = FORMAL_DOCUMENT_ROOT
    legacy_published = OUTPUT_ROOT / "04_数值文档"
    started_at = now()

    env = os.environ.copy()
    env.update({
        "VGAME_DESIGN_ROOT": os.fspath(REPO_ROOT),
        "VGAME_CONFIG_DATAS": os.fspath(configured_root.resolve()),
        "VGAME_NUMERICAL_RUNTIME_ROOT": os.fspath(runtime_root),
        "VGAME_NUMERICAL_LEGACY_INPUT_ROOT": os.fspath(run_root),
        "VGAME_SOURCE_DOCS_ROOT": os.fspath(run_root / "external-numerical-disk-disabled"),
        "VGAME_NUMERICAL_PRODUCTION_ISOLATED": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    })
    env.pop("VGAME_ALLOW_FORMAL_CONFIG_WRITE", None)

    try:
        command("01-migration-preflight", [sys.executable, os.fspath(REPO_ROOT / "scripts" / "numerical-workflows" / "validate_migration.py"), "--json-report", os.fspath(report_root / "migration-preflight.json")], cwd=REPO_ROOT, env=env, log_dir=report_root)
        # 正式交付文档属于 Git 管理结果，不得作为本次生成的输入或模板。
        shutil.copytree(
            WORKFLOW_ROOT / "framework",
            runtime_root,
            ignore=shutil.ignore_patterns("04_数值文档"),
        )
        for workbook in (WORKFLOW_ROOT / "legacy-inputs").glob("*.xlsx"):
            shutil.copy2(workbook, run_root / workbook.name)
        for relative in ("_reports", "养成/_reports", "战斗/_reports", "经济/_reports", "节奏/_reports", "05_验算核算", "06_最终配置"):
            (runtime_root / relative).mkdir(parents=True, exist_ok=True)

        source_sync_report = report_root / "source-sync-check.json"
        command("01b-source-md-consistency", [sys.executable, os.fspath(runtime_root / "02_AI规则" / "sync_global_sources_to_md.py"), "--report", os.fspath(source_sync_report)], cwd=runtime_root, env=env, log_dir=report_root)
        command("02-full-generation", [sys.executable, os.fspath(runtime_root / "run_all.py")], cwd=runtime_root, env=env, log_dir=report_root)
        command("03-clean-stage", [sys.executable, os.fspath(runtime_root / "02_AI规则" / "stage_final_documents_from_md.py"), os.fspath(stage)], cwd=runtime_root, env=env, log_dir=report_root)
        dynamic_json = report_root / "dynamic-validation.json"
        command("04-dynamic-validation", [sys.executable, os.fspath(runtime_root / "05_验算核算" / "scripts" / "validate_rebuild.py"), "--target", os.fspath(stage), "--expected-count", str(manifest["counts"]["expectedFinalWorkbooks"]), "--xlsx-report", os.fspath(report_root / "dynamic-validation.xlsx"), "--json-report", os.fspath(dynamic_json)], cwd=runtime_root, env=env, log_dir=report_root)

        validation = json.loads(dynamic_json.read_text(encoding="utf-8"))
        workbook_count = sum(1 for _ in stage.rglob("*.xlsx"))
        governance = json.loads((WORKFLOW_ROOT / "governance-overrides.json").read_text(encoding="utf-8"))
        ew_artifact = stage / governance["rules"]["RULING-EW-B"]["compatibilityArtifact"]
        if validation.get("overall_status") != "PASS" or workbook_count != manifest["counts"]["expectedFinalWorkbooks"] or not ew_artifact.is_file():
            raise RuntimeError("dynamic validation, workbook count or exclusive-weapon compatibility gate failed")

        target = stage if args.no_publish else published
        report = {
            "schema": "vgame-numerical-production-run/v1",
            "status": "PASS",
            "startedAt": started_at,
            "finishedAt": now(),
            "runId": args.run_id,
            "authority": "knowledge-base/README.md",
            "workflowSourceRoot": "numerical-workflows/v2/",
            "runRoot": run_root.relative_to(REPO_ROOT).as_posix(),
            "formalDocumentRoot": FORMAL_DOCUMENT_ROOT.relative_to(REPO_ROOT).as_posix(),
            "validatedStagingRoot": stage.relative_to(REPO_ROOT).as_posix(),
            "publicationMode": "STAGING_ONLY" if args.no_publish else "VERSION_CONTROLLED_WORKFLOW",
            "publicationStrategy": "STAGING_ONLY" if args.no_publish else "PENDING",
            "publishedRoot": target.relative_to(REPO_ROOT).as_posix(),
            "generationJobs": manifest["counts"]["mainGenerationJobs"],
            "inputGateCount": 2,
            "sourceMdSyncMode": "CHECK_ONLY",
            "canonicalSourceOwnedDifferences": json.loads(source_sync_report.read_text(encoding="utf-8"))["difference_count"],
            "stagingSourceOwnedChanges": json.loads(source_sync_report.read_text(encoding="utf-8"))["difference_count"],
            "finalWorkbookCount": workbook_count,
            "dynamicValidationStatus": validation["overall_status"],
            "dynamicGateCount": sum(item["gate"] != "FINAL" and item["status"] == "PASS" for item in validation["run_summary"]),
            "formalConfigWrite": "DENIED",
            "formalConfigEvidenceMode": "READ_ONLY",
            "externalNumericalSourceAvailable": Path(env["VGAME_SOURCE_DOCS_ROOT"]).exists(),
            "rulings": {"rv": "C: +30/+60/+100; weights 50/30/20", "exclusiveWeapon": "B: one-major-version compatibility"},
            "archivedPreviousPublication": None,
            "archivedLegacyOutputPublication": None,
            "independentFinalAcceptance": "PENDING",
        }
        run_report = report_root / "production-report.json"
        run_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        command("05-migration-postflight", [sys.executable, os.fspath(REPO_ROOT / "scripts" / "numerical-workflows" / "validate_migration.py"), "--production-report", os.fspath(run_report), "--json-report", os.fspath(report_root / "migration-postflight.json")], cwd=REPO_ROOT, env=env, log_dir=report_root)

        archived_previous = None
        archived_legacy = None
        if not args.no_publish:
            previous_root = OUTPUT_ROOT / "previous-published"
            archived_previous, report["publicationStrategy"] = publish_documents(stage, published, previous_root, args.run_id)
            if legacy_published.exists():
                previous_root.mkdir(exist_ok=True)
                archived_legacy = previous_root / f"legacy-output-{args.run_id}"
                legacy_published.rename(archived_legacy)
        report["archivedPreviousPublication"] = archived_previous.relative_to(REPO_ROOT).as_posix() if archived_previous is not None else None
        report["archivedLegacyOutputPublication"] = archived_legacy.relative_to(REPO_ROOT).as_posix() if archived_legacy is not None else None
        report["finishedAt"] = now()
        run_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (OUTPUT_ROOT / "latest-production-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        failure = {"schema": "vgame-numerical-production-run/v1", "status": "FAIL", "startedAt": started_at, "finishedAt": now(), "runId": args.run_id, "error": str(exc), "formalPublicationPreserved": published.exists(), "independentFinalAcceptance": "PENDING"}
        (report_root / "production-report-failed.json").write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
