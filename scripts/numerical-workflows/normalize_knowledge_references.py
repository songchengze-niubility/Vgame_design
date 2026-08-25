#!/usr/bin/env python3
"""将知识正文中的旧数值盘定位收敛为单仓资产或可追溯历史证据。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge-base"
LEGACY_PREFIX = re.compile(r"^(?:file:///)?[a-z]:[\\/]+数值文档[\\/]+数值文档[\\/]+框架v2[\\/]*", re.IGNORECASE)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def classify(value: str, repository_assets: dict[str, str]) -> tuple[str, str] | None:
    match = LEGACY_PREFIX.match(value)
    if match is None:
        return None
    relative = value[match.end() :].replace("\\", "/").strip("/")
    canonical = repository_assets.get(relative)
    if canonical is not None:
        return "canonical", canonical
    return "historical", f"vgame-numeric-source://框架v2/{relative}"


def normalize(item: object, repository_assets: dict[str, str], counts: dict[str, int]) -> object:
    if isinstance(item, list):
        return [normalize(value, repository_assets, counts) for value in item]
    if not isinstance(item, dict):
        return item

    for key, value in list(item.items()):
        if key in {"path", "href"} and isinstance(value, str):
            result = classify(value, repository_assets)
            if result is None:
                continue
            disposition, replacement = result
            if key == "href":
                item[key] = f"../../../{replacement}" if disposition == "canonical" else "../../../knowledge-base/numerical/source-registry.json"
            else:
                item[key] = replacement
            if disposition == "historical":
                item["historicalEvidenceOnly"] = True
                item["sourceRegistryRef"] = "knowledge-base/numerical/source-registry.json"
            counts[disposition] += 1
        else:
            item[key] = normalize(value, repository_assets, counts)
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只检查是否还有旧数值盘路径")
    args = parser.parse_args()
    manifest = load(REPO_ROOT / "numerical-workflows" / "v2" / "workflow-manifest.json")
    repository_assets = {
        item["sourceRelativePath"]: item["repositoryPath"]
        for item in manifest["files"]
    }
    files = [KNOWLEDGE_ROOT / "evidence" / "evidence-registry.json", *sorted((KNOWLEDGE_ROOT / "system-details").glob("*.json"))]
    changed_files = 0
    totals = {"canonical": 0, "historical": 0}

    for path in files:
        payload = load(path)
        counts = {"canonical": 0, "historical": 0}
        normalize(payload, repository_assets, counts)
        if not any(counts.values()):
            continue
        changed_files += 1
        for key, value in counts.items():
            totals[key] += value
        if not args.check:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status = "FAIL" if args.check and changed_files else "PASS"
    print(json.dumps({"status": status, "files": changed_files, **totals, "mode": "check" if args.check else "normalize"}, ensure_ascii=False))
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
