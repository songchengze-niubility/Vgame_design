#!/usr/bin/env python3
"""Block Figma writes until the exact target address has user approval."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_figma_handoff import Result, validate_figma_target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    args = parser.parse_args()

    result = Result()
    validate_figma_target(args.target.resolve(), result)
    for error in result.errors:
        print(f"[BLOCKED] {error}")
    if result.errors:
        print("Figma target gate is closed")
        return 1
    print("Figma target gate is open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
