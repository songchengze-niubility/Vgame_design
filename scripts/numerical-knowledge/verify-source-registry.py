#!/usr/bin/env python3
"""Verify the current external numerical source against the captured registry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=r"D:\数值文档\数值文档\框架v2")
    parser.add_argument("--registry", default=str(Path(__file__).resolve().parents[2] / "knowledge-base" / "numerical" / "source-registry.json"))
    parser.add_argument("--report")
    args = parser.parse_args()
    root = Path(args.source).resolve()
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8-sig"))
    current = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
    expected = {row["relativePath"]: row for row in registry["files"]}
    missing = sorted(set(expected) - set(current))
    extra = sorted(set(current) - set(expected))
    mismatched = []
    for rel in sorted(set(expected) & set(current)):
        actual = digest(current[rel])
        if actual != expected[rel]["sha256"]:
            mismatched.append({"relativePath": rel, "expected": expected[rel]["sha256"], "actual": actual})
    report = {"schema": "vgame-numerical-source-verification/v2", "passed": not missing and not extra and not mismatched, "registered": len(expected), "current": len(current), "missing": missing, "extra": extra, "mismatched": mismatched}
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
