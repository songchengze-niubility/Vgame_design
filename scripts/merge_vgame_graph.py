r"""
Vgame Knowledge Graph Merger
==============================
将客户端代码图谱、配置表 Schema 和设计文档图谱合并为统一总图。

Usage:
    python merge_vgame_graph.py
    python merge_vgame_graph.py --client "<client-graph-path>"
"""

import argparse
import json
import os
import time
from pathlib import Path

from vgame_paths import client_graph

DEFAULT_CLIENT_GRAPH = str(client_graph())
SCRIPT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_SCHEMA = str(SCRIPT_ROOT / "knowledge-graph" / "config-schema.json")
DEFAULT_DESIGN_GRAPH = str(SCRIPT_ROOT / "knowledge-graph" / "design-docs.json")
DEFAULT_OUTPUT = str(SCRIPT_ROOT / "knowledge-graph" / "knowledge-graph.json")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_graphs(client_path: str, config_path: str, design_path: str) -> dict:
    """合并客户端代码图谱、配置表 Schema 和设计文档图谱。"""

    nodes = []
    edges = []
    layers = []
    tour = []

    # === 1. 加载客户端代码图谱 ===
    if os.path.exists(client_path):
        client = load_json(client_path)
        client_nodes = client.get("nodes", [])
        client_edges = client.get("edges", [])
        client_layers = client.get("layers", [])
        client_tour = client.get("tour", [])

        # 给客户端节点打 layer 标签（如果没有的话）
        for node in client_nodes:
            if "source" not in node:
                node["source"] = "client"
            # UA 节点 ID 以类型前缀开头（file/config/document 等）。
            # 仅对完全没有前缀的旧节点补 client，避免节点改名后边端点悬空。
            if ":" not in node["id"]:
                node["id"] = f"client:{node['id']}"

        nodes.extend(client_nodes)
        edges.extend(client_edges)
        layers.extend(client_layers)
        tour.extend(client_tour)
        print(f"[INFO] 客户端图谱: {len(client_nodes)} 节点, {len(client_edges)} 边, {len(client_layers)} 层")
    else:
        print(f"[WARN] 客户端图谱不存在: {client_path}")

    # === 2. 加载配置表 Schema ===
    if os.path.exists(config_path):
        config = load_json(config_path)
        config_nodes = config.get("nodes", [])
        config_edges = config.get("edges", [])

        # 配置表节点已经有 "table:" 前缀和 layer="config"
        for node in config_nodes:
            node["source"] = "config"

        nodes.extend(config_nodes)
        edges.extend(config_edges)

        # 为配置表创建一个统一 layer
        config_node_ids = [n["id"] for n in config_nodes]
        layers.append({
            "id": "layer:config-tables",
            "name": "配置表",
            "description": f"Luban Excel 配置表（{len(config_nodes)}张，含字段、类型、外键关系）",
            "nodeIds": config_node_ids,
        })
        print(f"[INFO] 配置表 Schema: {len(config_nodes)} 节点, {len(config_edges)} 边")
    else:
        print(f"[WARN] 配置表 Schema 不存在: {config_path}")

    # === 3. 加载设计文档图谱 ===
    if os.path.exists(design_path):
        design = load_json(design_path)
        design_nodes = design.get("nodes", [])
        design_edges = design.get("edges", [])
        for node in design_nodes:
            node["source"] = "design"
        nodes.extend(design_nodes)
        edges.extend(design_edges)
        layers.extend(design.get("layers", []))
        print(f"[INFO] 设计文档图谱: {len(design_nodes)} 节点, {len(design_edges)} 边")
    else:
        print(f"[WARN] 设计文档图谱不存在: {design_path}")

    # === 4. 构建跨源边（代码引用配置表）===
    cross_edges = []
    # 从配置表的 cs_refs 字段中提取代码→配置表的引用关系
    if os.path.exists(config_path):
        config = load_json(config_path)
        for node in config.get("nodes", []):
            cs_refs = node.get("metadata", {}).get("cs_refs", [])
            table_id = node["id"]
            for ref_path in cs_refs:
                # 尝试匹配客户端节点
                # ref_path 格式如 "VGame.Lockstep/Runtime/Logic/Managers/LLevelMgr.cs"
                matching_nodes = [n for n in nodes if n.get("filePath", "").endswith(ref_path) or ref_path in n.get("id", "")]
                for mn in matching_nodes:
                    cross_edges.append({
                        "source": mn["id"],
                        "target": table_id,
                        "type": "reads_from",
                        "metadata": {"description": f"C# code reads from config table"},
                    })

    edges.extend(cross_edges)
    if cross_edges:
        print(f"[INFO] 跨源边（代码→配置表）: {len(cross_edges)} 条")

    # === 5. 去重 ===
    # 节点按 ID 去重（保留最后出现的）
    seen_nodes = {}
    for node in nodes:
        seen_nodes[node["id"]] = node
    nodes = list(seen_nodes.values())

    # 边按 (source, target, type) 去重
    seen_edges = set()
    unique_edges = []
    for edge in edges:
        key = (edge.get("source"), edge.get("target"), edge.get("type"))
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(edge)
    edges = unique_edges

    # === 6. 组装统一总图 ===
    unified = {
        "version": "1.0.0",
        "project": {
            "name": "Vgame",
            "description": "5人小队养成驱动跑酷战斗射击游戏 - 统一知识图谱",
            "languages": ["C#", "Lua"],
            "frameworks": ["Unity", "Luban"],
            "analyzedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sources": ["client-code", "config-tables", "design-docs"],
        },
        "nodes": nodes,
        "edges": edges,
        "layers": layers,
        "tour": tour,
        "statistics": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "total_layers": len(layers),
            "tour_steps": len(tour),
            "sources": {
                "client": sum(1 for n in nodes if n.get("source") == "client"),
                "config": sum(1 for n in nodes if n.get("source") == "config"),
                "design": sum(1 for n in nodes if n.get("source") == "design"),
            },
        },
    }

    return unified


def main():
    parser = argparse.ArgumentParser(description="Vgame Knowledge Graph Merger")
    parser.add_argument("--client", default=DEFAULT_CLIENT_GRAPH, help="客户端代码图谱路径")
    parser.add_argument("--config", default=DEFAULT_CONFIG_SCHEMA, help="配置表 Schema 路径")
    parser.add_argument("--design", default=DEFAULT_DESIGN_GRAPH, help="设计文档图谱路径")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="输出统一总图路径")
    args = parser.parse_args()

    print("[INFO] Vgame Knowledge Graph Merger")
    print(f"[INFO] 客户端: {args.client}")
    print(f"[INFO] 配置表: {args.config}")
    print(f"[INFO] 设计文档: {args.design}")

    unified = merge_graphs(args.client, args.config, args.design)

    # 写入
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(unified, f, ensure_ascii=False, indent=2)

    output_size = os.path.getsize(args.output) / 1024
    stats = unified["statistics"]

    print(f"\n{'='*50}")
    print(f"  合并完成")
    print(f"{'='*50}")
    print(f"  总节点: {stats['total_nodes']}")
    print(f"  总边:   {stats['total_edges']}")
    print(f"  总层:   {stats['total_layers']}")
    print(f"  导览:   {stats['tour_steps']} 步")
    print(
        "  来源:   "
        f"客户端 {stats['sources']['client']} + "
        f"配置表 {stats['sources']['config']} + "
        f"设计文档 {stats['sources']['design']}"
    )
    print(f"  输出:   {args.output} ({output_size:.1f} KB)")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
