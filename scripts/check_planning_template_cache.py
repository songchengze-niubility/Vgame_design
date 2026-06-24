#!/usr/bin/env python3
"""Check (or incrementally build) the planning-template cache.

策划案第1步用：在不全量扫描项目、不每次重建全部缓存的前提下，确认"模板索引"是否
可用且新鲜，并列出可选主/辅模板候选，供 project-researcher 选一个主模板。

约定（工作假设，可用参数或环境变量覆盖；见 tech-debt DEBT-0006）：
- 模板源目录 ``--template-root`` / ``VGAME_TEMPLATE_ROOT``，默认
  ``${VGAME_SOURCE_DOCS_ROOT}/模板``。
- 索引文件 ``--index``，默认 ``${VGAME_OUTPUT_ROOT}/.template-index.json``。
  索引是生成产物，不入库。

用法::

    python scripts/check_planning_template_cache.py            # 只检查
    python scripts/check_planning_template_cache.py --build    # 增量构建/刷新索引

退出码：0 索引新鲜可用；1 索引缺失或已过期（需 --build 增量刷新）；2 配置/IO 错误。
本脚本只扫描模板源目录，不扫描整个项目。

实现依据：skills/planning-feature-workflow/SKILL.md 第1步（第94-98行）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vgame_paths  # noqa: E402

SCHEMA_VERSION = "1.0"
TEMPLATE_SUFFIXES = {".xlsx", ".xlsm", ".xls", ".md"}
DEFAULT_MAX_AGE_DAYS = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--template-root", type=Path, default=None,
                        help="模板源目录；默认 VGAME_TEMPLATE_ROOT 或 ${VGAME_SOURCE_DOCS_ROOT}/模板")
    parser.add_argument("--index", type=Path, default=None,
                        help="索引文件路径；默认 ${VGAME_OUTPUT_ROOT}/.template-index.json")
    parser.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS,
                        help=f"索引超过该天数给出 WARN（默认 {DEFAULT_MAX_AGE_DAYS}）")
    parser.add_argument("--build", action="store_true",
                        help="增量扫描模板源目录并写入/刷新索引")
    parser.add_argument("--output-root", type=Path, default=None, help="覆盖 VGAME_OUTPUT_ROOT")
    return parser.parse_args()


def resolve_template_root(arg: Path | None) -> Path:
    if arg:
        return arg.resolve()
    env = os.environ.get("VGAME_TEMPLATE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return (vgame_paths.source_docs_root() / "模板").resolve()


def resolve_index(arg: Path | None, out_root: Path) -> Path:
    if arg:
        return arg.resolve()
    return (out_root / ".template-index.json").resolve()


def scan_templates(template_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(template_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEMPLATE_SUFFIXES:
            continue
        if path.name.startswith("~$"):  # Excel 临时锁文件
            continue
        stat = path.stat()
        rel = path.relative_to(template_root).as_posix()
        name = path.stem
        kind = "primary" if any(k in name for k in ("主", "main", "Main")) else \
               "aux" if any(k in name for k in ("辅", "aux", "Aux")) else "unknown"
        entries.append({
            "id": rel,
            "path": rel,
            "title": name,
            "suffix": path.suffix.lower(),
            "kind": kind,
            "mtime": int(stat.st_mtime),
            "size": stat.st_size,
        })
    return entries


def build_index(template_root: Path, index_path: Path) -> int:
    if not template_root.is_dir():
        print(f"[FAIL] 模板源目录不存在: {template_root}")
        return 2
    entries = scan_templates(template_root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "template_root": str(template_root),
        "count": len(entries),
        "templates": entries,
    }
    try:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    except OSError as exc:
        print(f"[FAIL] 无法写入索引: {exc}")
        return 2
    print(f"[OK] 索引已刷新: {index_path}（{len(entries)} 个模板）")
    return 0


def load_index(index_path: Path) -> dict[str, Any] | None:
    try:
        with index_path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def check_index(template_root: Path, index_path: Path, max_age_days: int) -> int:
    if not index_path.is_file():
        print(f"[STALE] 索引缺失: {index_path}")
        print("        FIX: 运行 --build 增量构建（只扫描模板源目录）")
        return 1
    index = load_index(index_path)
    if index is None:
        print(f"[STALE] 索引无法解析: {index_path}")
        print("        FIX: 运行 --build 重新生成")
        return 1

    indexed = {e.get("id"): e for e in index.get("templates", []) if isinstance(e, dict)}
    print(f"已索引模板: {len(indexed)} 个（template_root={index.get('template_root')}）")

    primaries = [e["title"] for e in indexed.values() if e.get("kind") == "primary"]
    if primaries:
        print(f"主模板候选: {', '.join(primaries)}")
    else:
        print("主模板候选: （未按命名标记，需 project-researcher 人工挑选）")

    if not template_root.is_dir():
        print(f"[WARN] 模板源目录不在本机: {template_root}（无法校验新鲜度，按索引内容使用）")
        return 0

    disk = {e["id"]: e for e in scan_templates(template_root)}
    added = sorted(set(disk) - set(indexed))
    removed = sorted(set(indexed) - set(disk))
    changed = sorted(
        rid for rid in set(disk) & set(indexed)
        if disk[rid]["mtime"] != indexed[rid].get("mtime")
        or disk[rid]["size"] != indexed[rid].get("size")
    )

    stale = added or removed or changed
    if stale:
        if added:
            print(f"[STALE] 新增 {len(added)} 个: {', '.join(added[:10])}")
        if removed:
            print(f"[STALE] 移除 {len(removed)} 个: {', '.join(removed[:10])}")
        if changed:
            print(f"[STALE] 变更 {len(changed)} 个: {', '.join(changed[:10])}")
        print("        FIX: 运行 --build 增量刷新")
        return 1

    generated_at = index.get("generated_at", "")
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(generated_at)
        if age.days > max_age_days:
            print(f"[WARN] 索引已 {age.days} 天未刷新（阈值 {max_age_days}），建议 --build")
    except (TypeError, ValueError):
        print("[WARN] 索引缺少可解析的 generated_at")

    print("[OK] 索引新鲜可用")
    return 0


def main() -> int:
    args = parse_args()
    out_root = args.output_root.resolve() if args.output_root else vgame_paths.output_root()
    template_root = resolve_template_root(args.template_root)
    index_path = resolve_index(args.index, out_root)

    if args.build:
        return build_index(template_root, index_path)
    return check_index(template_root, index_path, args.max_age_days)


if __name__ == "__main__":
    sys.exit(main())
