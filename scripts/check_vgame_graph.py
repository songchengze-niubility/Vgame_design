"""只读检查 Vgame 知识图谱的完整性与来源状态。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from vgame_paths import client_graph, config_datas


ROOT = Path(__file__).resolve().parents[1]
KG = ROOT / "knowledge-graph"
CLIENT = client_graph()
CONFIG_SOURCE = config_datas() / "__tables__.xlsx"
PROJECT_FIELDS = {"name", "languages", "frameworks", "description", "analyzedAt", "gitCommitHash"}
NODE_COMPLEXITIES = {"simple", "moderate", "complex"}
EDGE_DIRECTIONS = {"forward", "backward", "bidirectional"}
EDGE_TYPES = {
    "imports", "exports", "contains", "inherits", "implements", "calls", "subscribes",
    "publishes", "middleware", "reads_from", "writes_to", "transforms", "validates",
    "depends_on", "tested_by", "configures", "related", "similar_to", "deploys", "serves",
    "provisions", "triggers", "migrates", "documents", "routes", "defines_schema",
    "contains_flow", "flow_step", "cross_domain", "cites", "contradicts", "builds_on",
    "exemplifies", "categorized_under", "authored_by",
}


def load(path: Path) -> dict | None:
    if not path.exists():
        print(f"[FAIL] 缺少: {path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"[PASS] {path.name}: {path.stat().st_size / 1024:.1f} KB")
        return data
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] 无法解析 {path}: {exc}")
        return None


def main() -> int:
    failures = 0
    print("=== Vgame 知识图谱只读体检 ===")
    for label, source in (("客户端图谱", CLIENT), ("配置注册表", CONFIG_SOURCE)):
        if source.exists():
            print(f"[PASS] {label}: {source}")
        else:
            print(f"[WARN] {label}不存在: {source}")

    config = load(KG / "config-schema.json")
    design = load(KG / "design-docs.json")
    graph = load(KG / ".understand-anything" / "knowledge-graph.json")
    lite = load(KG / ".understand-anything" / "knowledge-graph-lite.json")
    meta = load(KG / ".understand-anything" / "meta.json")
    failures += sum(item is None for item in (config, design, graph, lite, meta))

    if graph:
        project = graph.get("project", {})
        missing_project = sorted(PROJECT_FIELDS - set(project))
        if missing_project:
            print(f"[FAIL] UA project metadata 缺少字段: {', '.join(missing_project)}")
            failures += 1
        else:
            print("[PASS] UA project metadata 完整")

        node_ids = {node.get("id") for node in graph.get("nodes", [])}
        invalid_nodes = [
            node for node in graph.get("nodes", [])
            if not isinstance(node.get("summary"), str)
            or not isinstance(node.get("tags"), list)
            or node.get("complexity") not in NODE_COMPLEXITIES
        ]
        invalid_edges = [
            edge for edge in graph.get("edges", [])
            if edge.get("type") not in EDGE_TYPES
            or edge.get("direction") not in EDGE_DIRECTIONS
            or not isinstance(edge.get("weight"), (int, float))
            or not 0 <= edge.get("weight", -1) <= 1
        ]
        if invalid_nodes:
            print(f"[FAIL] {len(invalid_nodes)} 个节点不符合 UA Schema")
            failures += 1
        else:
            print("[PASS] 所有节点符合 UA Schema")
        if invalid_edges:
            print(f"[FAIL] {len(invalid_edges)} 条边不符合 UA Schema")
            failures += 1
        else:
            print("[PASS] 所有边符合 UA Schema")

        dangling = [
            edge
            for edge in graph.get("edges", [])
            if edge.get("source") not in node_ids or edge.get("target") not in node_ids
        ]
        if dangling:
            print(f"[WARN] 存在 {len(dangling)} 条悬空边，可能来自跨源引用或缺失代码节点")
        else:
            print("[PASS] 所有边均可定位到节点")
        print(
            f"[INFO] 总图: {len(graph.get('nodes', []))} 节点, "
            f"{len(graph.get('edges', []))} 边, {len(graph.get('layers', []))} 层"
        )

    print(f"=== 检查完成: FAIL {failures} ===")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
