#!/usr/bin/env python3
"""把 Git 管理的参数基线同步到知识库机器参数注册表。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK_ROOT = REPO_ROOT / "numerical-workflows" / "v2" / "framework"
PARAMETER_ROOT = FRAMEWORK_ROOT / "03_沉淀MD" / "参数基线"
REGISTRY_PATH = REPO_ROOT / "knowledge-base" / "numerical" / "parameter-registry.json"
SCOPES = ("共享", "养成", "战斗", "节奏")

sys.path.insert(0, str(FRAMEWORK_ROOT))

from _shared.md_parameter_reader import read_parameter_payload


def portable_digest(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只检查知识库参数与 Git 管理 MD 是否一致")
    parser.add_argument("--json-report", type=Path, help="把同步结果写入指定的可重新生成报告")
    args = parser.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    refreshed = []

    for scope in SCOPES:
        parameter_path = PARAMETER_ROOT / f"{scope}参数基线.md"
        relative_path = parameter_path.relative_to(REPO_ROOT).as_posix()
        legacy_locator = f"03_沉淀MD/参数基线/{scope}参数基线.md#"
        matches = [item for item in registry["parameterSets"] if item["sourceLocator"].startswith(legacy_locator)]
        if len(matches) != 1:
            raise SystemExit(f"参数域 {scope} 必须且只能对应一个机器参数块，当前为 {len(matches)}")

        row = matches[0]
        payload = read_parameter_payload(parameter_path)
        expected_hash = portable_digest(parameter_path)
        expected_metadata = {
            "canonicalSourcePath": relative_path,
            "canonicalSourceSha256": expected_hash,
            "authorityRole": "GIT_MANAGED_PARAMETER_BASELINE",
        }
        if row["value"] == payload and all(row.get(key) == value for key, value in expected_metadata.items()):
            continue

        refreshed.append({
            "scope": scope,
            "parameterSetId": row["parameterSetId"],
            "historicalSourceId": row["sourceId"],
            "canonicalSourcePath": relative_path,
            "canonicalSourceSha256": expected_hash,
        })
        if not args.check:
            row["value"] = payload
            row.update(expected_metadata)

    if refreshed and not args.check:
        registry["refreshedAt"] = datetime.now().astimezone().isoformat(timespec="seconds")
        REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema": "vgame-numerical-parameter-baseline-sync/v1",
        "status": "FAIL" if args.check and refreshed else "PASS",
        "mode": "CHECK_ONLY" if args.check else "SYNC_GIT_CANONICAL",
        "baselineCount": len(SCOPES),
        "changedCount": len(refreshed),
        "historicalSourceRegistryChanged": False,
        "stableParameterSetIdsPreserved": True,
        "baselines": refreshed,
    }
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
