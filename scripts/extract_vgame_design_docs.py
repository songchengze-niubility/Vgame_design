"""从 Vgame_design 的 Markdown 文档提取轻量设计知识图谱。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "knowledge-graph" / "design-docs.json"
SCAN_DIRS = ("design", "proposals", "tasks", "harness")
def slug(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()[:12]


def title_of(path: Path, text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else path.stem


def summary_of(text: str) -> str:
    for block in re.split(r"\n\s*\n", text):
        value = re.sub(r"^#+\s*", "", block.strip())
        value = re.sub(r"\s+", " ", value)
        if value and not value.startswith(("```", "|", ">")):
            return value[:240]
    return ""


def collect_files() -> list[Path]:
    files: set[Path] = set()
    for directory in SCAN_DIRS:
        root = REPO_ROOT / directory
        if root.exists():
            files.update(root.rglob("*.md"))
    files.update(REPO_ROOT.glob("*.md"))
    return sorted(files)


def pair_key(path: Path) -> str | None:
    stem = path.stem.replace("Proposal Doc", "").replace("Design Doc", "").strip(" -_")
    if stem.lower() in {"readme", "template", "reverse-engineering-template"}:
        return None
    return stem


def classify(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel.startswith("design/"):
        return "design"
    if rel.startswith("proposals/"):
        return "proposal"
    if rel.startswith("tasks/"):
        return "task"
    if rel.startswith("harness/"):
        return "harness"
    return "governance"


def extract(output: Path) -> dict:
    files = collect_files()
    nodes = []
    by_stem: dict[tuple[str, str], str] = {}

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(REPO_ROOT).as_posix()
        category = classify(path)
        node_id = f"document:{slug(path)}"
        nodes.append(
            {
                "id": node_id,
                "type": "document",
                "name": title_of(path, text),
                "filePath": rel,
                "summary": summary_of(text),
                "tags": ["vgame", "design-doc", category],
                "complexity": "simple" if len(text) < 8000 else "moderate",
                "layer": "design",
                "metadata": {
                    "category": category,
                    "line_count": len(text.splitlines()),
                    "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                },
            }
        )
        key = pair_key(path)
        if key:
            by_stem[(category, key)] = node_id

    edges = []
    for path in files:
        if classify(path) != "proposal":
            continue
        key = pair_key(path)
        source = by_stem.get(("proposal", key)) if key else None
        target = by_stem.get(("design", key)) if key else None
        if source and target:
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "type": "documents",
                    "metadata": {"source_rule": "same_filename_stem", "confidence": 1.0},
                }
            )

    layer = {
        "id": "layer:design-docs",
        "name": "策划与治理文档",
        "description": f"Vgame 设计、提案、任务、计划和 Harness 文档（{len(nodes)}份）",
        "nodeIds": [node["id"] for node in nodes],
    }
    result = {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "nodes": nodes,
        "edges": edges,
        "layers": [layer],
        "statistics": {"documents": len(nodes), "edges": len(edges)},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[INFO] 设计文档: {len(nodes)} 节点, {len(edges)} 边 -> {output}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Vgame design document graph extractor")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    extract(args.output)


if __name__ == "__main__":
    main()
