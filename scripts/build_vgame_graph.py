"""构建并发布 Vgame 统一知识图谱。所有项目源文件只读。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from vgame_paths import client_graph


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
KG = ROOT / "knowledge-graph"
UA = KG / ".understand-anything"
CLIENT_GRAPH = client_graph()


def run(script: str, *args: str) -> None:
    command = [sys.executable, str(SCRIPTS / script), *args]
    print(f"[RUN] {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def publish() -> dict:
    source = KG / "knowledge-graph.json"
    graph = json.loads(source.read_text(encoding="utf-8"))
    UA.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, UA / "knowledge-graph.json")

    lite_nodes = [node for node in graph.get("nodes", []) if node.get("type") != "function"]
    lite_ids = {node.get("id") for node in lite_nodes}
    lite_edges = [
        edge
        for edge in graph.get("edges", [])
        if edge.get("source") in lite_ids and edge.get("target") in lite_ids
    ]
    lite = dict(graph)
    lite["nodes"] = lite_nodes
    lite["edges"] = lite_edges
    lite["layers"] = [
        {**layer, "nodeIds": [node_id for node_id in layer.get("nodeIds", []) if node_id in lite_ids]}
        for layer in graph.get("layers", [])
    ]
    (UA / "knowledge-graph-lite.json").write_text(
        json.dumps(lite, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    sources = graph.get("statistics", {}).get("sources", {})
    meta = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "sources": sources,
        "total_nodes": len(graph.get("nodes", [])),
        "total_edges": len(graph.get("edges", [])),
        "lite_nodes": len(lite_nodes),
        "lite_edges": len(lite_edges),
        "layer_count": len(graph.get("layers", [])),
        "source_availability": {
            "client": CLIENT_GRAPH.exists(),
            "config": (KG / "config-schema.json").exists(),
            "design": (KG / "design-docs.json").exists(),
        },
    }
    (UA / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (UA / "config.json").write_text(
        json.dumps({"autoUpdate": False, "outputLanguage": "zh"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Vgame unified knowledge graph")
    parser.add_argument("--skip-config", action="store_true", help="沿用现有配置表 Schema")
    parser.add_argument("--skip-cs-refs", action="store_true", help="配置提取时跳过 C# 引用扫描")
    parser.add_argument("--client", type=Path, default=CLIENT_GRAPH, help="客户端代码图谱")
    args = parser.parse_args()

    if not args.skip_config:
        extract_args = []
        if args.skip_cs_refs:
            extract_args.append("--skip-cs-refs")
        run("extract_vgame_config_schema.py", *extract_args)

    run("extract_vgame_design_docs.py")
    run("merge_vgame_graph.py", "--client", str(args.client))
    meta = publish()
    print(
        "[DONE] Vgame 图谱已发布: "
        f"{meta['total_nodes']} 节点, {meta['total_edges']} 边, "
        f"精简版 {meta['lite_nodes']} 节点"
    )


if __name__ == "__main__":
    main()
