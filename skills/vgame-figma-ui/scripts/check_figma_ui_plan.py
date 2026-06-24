#!/usr/bin/env python3
"""Block Figma writes until the UI plan has explicit user approval."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_figma_handoff import Result, validate_plan_approval


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()

    result = Result()
    validate_plan_approval(args.plan.resolve(), result)
    for error in result.errors:
        print(f"[BLOCKED] {error}")
    if result.errors:
        print("Figma write gate is closed")
        return 1
    print("Figma write gate is open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
