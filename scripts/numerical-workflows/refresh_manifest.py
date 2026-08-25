#!/usr/bin/env python3
"""在受审生产兼容修复后刷新 Git 权威蓝图的迁入哈希。"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "numerical-workflows" / "v2" / "workflow-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    changed = []
    for row in manifest["files"]:
        target = root / row["repositoryPath"]
        value = hashlib.sha256(target.read_bytes()).hexdigest()
        if value != row["migratedSha256"]:
            row["migratedSha256"] = value
            row["bytes"] = target.stat().st_size
            row["repositoryCompatibilityAdaptation"] = True
            changed.append(row["repositoryPath"])
    manifest["refreshedAt"] = datetime.now().astimezone().isoformat(timespec="seconds")
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": len(changed), "paths": changed}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
