#!/usr/bin/env python3
"""Refresh registered Skill source hashes and V2 numerical evidence links."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RELEVANT = {
    "vgame-core-understanding", "vgame-knowledge-router", "game-numerical-analysis",
    "senior-game-economy", "outer-loop-progression-pacing", "vgame-player-progression-simulator",
    "vgame-config-schema", "vgame-config-quality-audit", "vgame-economy-source-map",
    "vgame-growth-combat-conversion-map", "vgame-battle-tuning-helper", "vgame-level-progression-map",
    "vgame-reward-drop-sync", "game-monetization", "planning-liveops-readiness",
}


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "knowledge-base" / "registries" / "skill-registry.json"
    registry = json.loads(path.read_text(encoding="utf-8-sig"))
    registry["schema"] = "vgame-skill-registry/v2"
    registry["version"] = "2.0.0"
    for skill in registry["skills"]:
        source = repo / skill["sourcePath"]
        skill["sourceSha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        if skill["skillId"] in RELEVANT:
            evidence = skill.setdefault("evidenceSources", [])
            if "knowledge-base/numerical/atom-registry.json" not in evidence:
                evidence.append("knowledge-base/numerical/atom-registry.json")
            layers = skill.setdefault("knowledgeLayers", [])
            if "PFN-13" not in layers:
                layers.append("PFN-13")
            skill["versionStatus"] = "ACTIVE_V2_NUMERICAL"
    registry["count"] = len(registry["skills"])
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    evidence_map_path = repo / "knowledge-base" / "mappings" / "skill-to-evidence.json"
    evidence_map = json.loads(evidence_map_path.read_text(encoding="utf-8-sig"))
    evidence_map["schema"] = "vgame-skill-to-evidence/v2"
    by_id = {skill["skillId"]: skill for skill in registry["skills"]}
    for row in evidence_map["mappings"]:
        row["evidenceSources"] = by_id[row["skillId"]]["evidenceSources"]
    evidence_map_path.write_text(json.dumps(evidence_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    layer_path = repo / "knowledge-base" / "mappings" / "skill-to-knowledge-layer.json"
    layer_map = json.loads(layer_path.read_text(encoding="utf-8-sig"))
    layer_map["schema"] = "vgame-skill-to-layer/v2"
    for row in layer_map["mappings"]:
        row["frameworkNodeIds"] = by_id[row["skillId"]]["knowledgeLayers"]
    layer_path.write_text(json.dumps(layer_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"refreshed {len(registry['skills'])} skills; V2 numerical coverage {len(RELEVANT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
