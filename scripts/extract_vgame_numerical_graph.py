"""从权威数值原子注册表生成 Understand Anything 数值子图。"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
KB = REPO_ROOT / "knowledge-base"
DEFAULT_OUTPUT = REPO_ROOT / "knowledge-graph" / "numerical-knowledge.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_node(node_id: str, node_type: str, name: str, summary: str, tags: list[str], **metadata: object) -> dict:
    return {
        "id": node_id,
        "type": node_type,
        "name": name,
        "summary": summary[:500],
        "tags": tags,
        "complexity": "moderate",
        "layer": "numerical",
        "metadata": metadata,
    }


def make_edge(source: str, target: str, edge_type: str, description: str) -> dict:
    return {
        "source": source,
        "target": target,
        "type": edge_type,
        "direction": "forward",
        "weight": 0.8,
        "metadata": {"description": description},
    }


def extract(output: Path) -> dict:
    atom_registry = load(KB / "numerical" / "atom-registry.json")
    source_registry = load(KB / "numerical" / "source-registry.json")
    skill_registry = load(KB / "registries" / "skill-registry.json")
    framework_registry = load(KB / "registries" / "framework-nodes.json")
    system_mappings = load(KB / "mappings" / "system-to-skill.json")
    production_manifest = load(REPO_ROOT / "numerical-workflows" / "v2" / "workflow-manifest.json")

    atoms = atom_registry["atoms"]
    source_by_id = {item["sourceId"]: item for item in source_registry["files"]}
    skill_by_id = {item["skillId"]: item for item in skill_registry["skills"]}
    framework_by_id = {item["id"]: item for item in framework_registry["nodes"]}
    system_by_id = {item["systemId"]: item for item in system_mappings["mappings"]}

    domain_ids = sorted({item["domain"] for item in atoms})
    used_skill_ids = sorted({value for item in atoms for value in item.get("skillIds", [])})
    used_system_ids = sorted({value for item in atoms for value in item.get("coveredSystems", [])})
    used_framework_ids = sorted({value for item in atoms for value in item.get("frameworkNodeIds", [])})
    used_evidence_ids = sorted({value for item in atoms for value in item.get("evidenceRefs", [])})

    nodes = [
        make_node(
            "numerical-framework:v2",
            "concept",
            "Vgame 数值框架 V2",
            "全栈策划知识框架中的权威数值原子层；正文位于 knowledge-base/numerical。",
            ["vgame", "numerical", "authority", "v2"],
            canonicalPath="knowledge-base/numerical/README.md",
            atomCount=len(atoms),
        )
    ]
    edges = []

    production_counts = production_manifest["counts"]
    production_root_id = "numerical-production:v2"
    nodes.append(
        make_node(
            production_root_id,
            "concept",
            "数值生产工作流 V2",
            (
                f"单仓纳管 {production_counts['migratedPythonFiles']} 个生产脚本、"
                f"{production_counts['inputWorkbooks']} 份受控输入、"
                f"{production_counts['mainGenerationJobs']} 条任务和 "
                f"{production_counts['expectedFinalWorkbooks']} 份 Git 管理的可重建正式终稿。"
            ),
            ["vgame", "numerical", "production", "single-repository"],
            canonicalPath="numerical-workflows/v2/workflow-manifest.json",
            externalNumericalSourceRequired=production_manifest["legacyExternalSourceRequiredAtRuntime"],
            formalConfigWriteDefault=production_manifest["formalConfigWriteDefault"],
            formalDocumentRoot=production_manifest["formalDocumentRoot"],
            **production_counts,
        )
    )
    edges.append(make_edge("numerical-framework:v2", production_root_id, "contains", "数值框架纳入完整单仓生产工作流"))

    production_roles = sorted({item["role"] for item in production_manifest["files"]})
    for role in production_roles:
        category_id = f"numerical-production-category:{role}"
        role_files = [item for item in production_manifest["files"] if item["role"] == role]
        nodes.append(
            make_node(
                category_id,
                "concept",
                f"生产资产：{role}",
                f"{role} 分类下共有 {len(role_files)} 份 Git 管理生产资产。",
                ["vgame", "numerical-production-category", role.lower()],
                role=role,
                fileCount=len(role_files),
            )
        )
        edges.append(make_edge(production_root_id, category_id, "contains", "生产工作流按资产职责分组"))
        for item in role_files:
            path_digest = hashlib.sha256(item["repositoryPath"].encode("utf-8")).hexdigest()[:20]
            asset_id = f"numerical-production-file:{path_digest}"
            nodes.append(
                make_node(
                    asset_id,
                    "file",
                    Path(item["repositoryPath"]).name,
                    f"单仓数值生产资产：{item['repositoryPath']}。",
                    ["vgame", "numerical-production-file", role.lower()],
                    repositoryPath=item["repositoryPath"],
                    role=role,
                    sha256=item["migratedSha256"],
                    requiresExplicitFormalWriteApproval=item["requiresExplicitFormalWriteApproval"],
                )
            )
            edges.append(make_edge(category_id, asset_id, "contains", "生产资产登记了职责、路径和内容哈希"))

    for domain_id in domain_ids:
        domain_node_id = f"numerical-domain:{domain_id}"
        nodes.append(make_node(domain_node_id, "concept", f"数值域：{domain_id}", f"{domain_id} 数值原子集合。", ["vgame", "numerical-domain", domain_id], domain=domain_id))
        edges.append(make_edge("numerical-framework:v2", domain_node_id, "contains", "数值框架包含领域"))

    for skill_id in used_skill_ids:
        skill = skill_by_id.get(skill_id, {})
        nodes.append(make_node(f"skill:{skill_id}", "concept", skill_id, skill.get("responsibility", "数值原子登记的调用 Skill。"), ["vgame", "skill", skill.get("category", "unclassified")], skillId=skill_id, sourcePath=skill.get("sourcePath"), versionStatus=skill.get("versionStatus")))
        if skill_id == "game-numerical-analysis":
            edges.append(make_edge(f"skill:{skill_id}", production_root_id, "routes", "数值专项 Skill 按需调用仓库内生产工作流"))

    for system_id in used_system_ids:
        system = system_by_id.get(system_id, {})
        nodes.append(make_node(f"system:{system_id}", "concept", system.get("systemName", system_id), f"项目系统 {system_id}，由数值原子的 coveredSystems 映射接入。", ["vgame", "system", system_id], systemId=system_id, primarySkill=system.get("primarySkill")))

    for framework_id in used_framework_ids:
        framework = framework_by_id.get(framework_id, {})
        nodes.append(make_node(f"framework:{framework_id}", "concept", framework.get("name", framework_id), framework.get("responsibility", "项目策划框架节点。"), ["vgame", "framework-node", framework_id], frameworkNodeId=framework_id, status=framework.get("status")))

    for evidence_id in used_evidence_ids:
        evidence = source_by_id.get(evidence_id)
        if evidence:
            name = evidence["relativePath"]
            summary = f"数值框架证据：{evidence['relativePath']}（SHA-256 已登记）。"
            metadata = {"evidenceId": evidence_id, "relativePath": evidence["relativePath"], "sha256": evidence["sha256"], "authorityRole": evidence["authorityRole"]}
        else:
            name = evidence_id
            summary = f"治理裁决或非文件证据：{evidence_id}。"
            metadata = {"evidenceId": evidence_id, "authorityRole": "HUMAN_RULING"}
        nodes.append(make_node(f"numerical-evidence:{evidence_id}", "document", name, summary, ["vgame", "numerical-evidence"], **metadata))

    for atom in atoms:
        atom_node_id = f"numerical-atom:{atom['atomId']}"
        nodes.append(make_node(atom_node_id, "concept", atom["title"], atom["statement"], ["vgame", "numerical-atom", atom["domain"], atom["status"]], atomId=atom["atomId"], atomType=atom["atomType"], domain=atom["domain"], status=atom["status"], sourceLocator=atom["sourceLocator"], sourceNature=atom["sourceNature"]))
        edges.append(make_edge(f"numerical-domain:{atom['domain']}", atom_node_id, "contains", "领域包含数值原子"))
        for skill_id in atom.get("skillIds", []):
            edges.append(make_edge(f"skill:{skill_id}", atom_node_id, "routes", "Skill 可按需路由到该数值原子"))
        for system_id in atom.get("coveredSystems", []):
            edges.append(make_edge(atom_node_id, f"system:{system_id}", "related", "数值原子覆盖项目系统"))
        for framework_id in atom.get("frameworkNodeIds", []):
            edges.append(make_edge(atom_node_id, f"framework:{framework_id}", "categorized_under", "数值原子归属策划框架节点"))
        for evidence_id in atom.get("evidenceRefs", []):
            edges.append(make_edge(atom_node_id, f"numerical-evidence:{evidence_id}", "cites", "数值原子引用可追溯证据"))

    layer_groups = {
        "layer:numerical-domains": [item["id"] for item in nodes if item["id"].startswith("numerical-domain:") or item["id"] == "numerical-framework:v2"],
        "layer:numerical-atoms": [item["id"] for item in nodes if item["id"].startswith("numerical-atom:")],
        "layer:numerical-skills": [item["id"] for item in nodes if item["id"].startswith("skill:")],
        "layer:numerical-systems": [item["id"] for item in nodes if item["id"].startswith("system:")],
        "layer:numerical-framework-nodes": [item["id"] for item in nodes if item["id"].startswith("framework:")],
        "layer:numerical-evidence": [item["id"] for item in nodes if item["id"].startswith("numerical-evidence:")],
        "layer:numerical-production": [
            item["id"] for item in nodes
            if item["id"].startswith(("numerical-production:", "numerical-production-category:", "numerical-production-file:"))
        ],
    }
    layer_names = {
        "layer:numerical-domains": "数值框架与领域",
        "layer:numerical-atoms": "数值知识原子",
        "layer:numerical-skills": "数值调用 Skill",
        "layer:numerical-systems": "数值覆盖系统",
        "layer:numerical-framework-nodes": "数值归属策划层",
        "layer:numerical-evidence": "数值证据",
        "layer:numerical-production": "单仓数值生产工作流",
    }
    layers = [{"id": layer_id, "name": layer_names[layer_id], "description": f"由权威数值原子注册表生成（{len(node_ids)} 节点）", "nodeIds": node_ids} for layer_id, node_ids in layer_groups.items()]

    result = {
        "version": "2.0.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "nodes": nodes,
        "edges": edges,
        "layers": layers,
        "statistics": {
            "atoms": len(atoms),
            "activeAtoms": sum(item["status"] == "ACTIVE" for item in atoms),
            "skills": len(used_skill_ids),
            "systems": len(used_system_ids),
            "frameworkNodes": len(used_framework_ids),
            "evidence": len(used_evidence_ids),
            "productionFiles": len(production_manifest["files"]),
            "productionScripts": production_counts["migratedPythonFiles"],
            "productionInputWorkbooks": production_counts["inputWorkbooks"],
            "productionTasks": production_counts["mainGenerationJobs"],
            "nodes": len(nodes),
            "edges": len(edges),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[INFO] 数值知识子图: {len(nodes)} 节点, {len(edges)} 边 -> {output}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Vgame numerical knowledge graph extractor")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    extract(args.output)


if __name__ == "__main__":
    main()
