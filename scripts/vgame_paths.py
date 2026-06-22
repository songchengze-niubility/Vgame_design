"""Portable local-path resolution for Vgame_design tools."""

from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_path(name: str) -> Path | None:
    value = os.environ.get(name, "").strip()
    return Path(value).expanduser() if value else None


def vgame_root() -> Path:
    return _env_path("VGAME_ROOT") or (REPO_ROOT.parent / "Vgame")


def config_datas() -> Path:
    return _env_path("VGAME_CONFIG_DATAS") or (vgame_root() / "Config" / "GameConfig" / "Datas")


def client_graph() -> Path:
    return _env_path("VGAME_CLIENT_GRAPH") or (
        vgame_root() / "\u77e5\u8bc6\u56fe\u8c31" / "client" / "knowledge-graph.json"
    )


def code_root() -> Path:
    return _env_path("VGAME_CODE_ROOT") or (
        vgame_root() / "HorizonFlyProject" / "Packages" / "VGame"
    )


def skill_root() -> Path | None:
    return _env_path("VGAME_SKILL_ROOT")
