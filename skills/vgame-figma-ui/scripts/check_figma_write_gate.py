#!/usr/bin/env python3
"""Require approved UI plan and exact Figma target before content writes."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_figma_handoff import Result, validate_figma_target, validate_plan_approval


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    args = parser.parse_args()

    result = Result()
    validate_plan_approval(args.plan.resolve(), result)
    validate_figma_target(args.target.resolve(), result)
    for error in result.errors:
        print(f"[BLOCKED] {error}")
    if result.errors:
        print("Figma content write gate is closed")
        return 1
    print("Figma content write gate is open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
