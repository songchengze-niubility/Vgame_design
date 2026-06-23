"""Portable local-path resolution for Vgame_design tools."""

from __future__ import annotations

import os
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
USER_CONFIG = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Vgame" / "design-harness.env.bat"
REPO_CONFIG = REPO_ROOT / "local.env.bat"
SET_PATTERN = re.compile(r'^\s*set\s+"?([A-Za-z_][A-Za-z0-9_]*)=(.*?)"?\s*$', re.IGNORECASE)


def _read_bat_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.lower().startswith(("rem ", "::", "@echo")):
            continue
        match = SET_PATTERN.match(line)
        if match:
            values[match.group(1).upper()] = match.group(2).rstrip('"')
    return values


LOCAL_VALUES = _read_bat_env(USER_CONFIG)
LOCAL_VALUES.update(_read_bat_env(REPO_CONFIG))


def _value(name: str) -> str:
    value = os.environ.get(name) or LOCAL_VALUES.get(name.upper(), "")
    for key, replacement in LOCAL_VALUES.items():
        value = value.replace(f"%{key}%", replacement).replace(f"${{{key}}}", replacement)
    return value.strip()


def _env_path(name: str) -> Path | None:
    value = _value(name)
    return Path(value).expanduser() if value else None


def vgame_root() -> Path:
    return _env_path("VGAME_ROOT") or (REPO_ROOT.parent / "Vgame")


def design_root() -> Path:
    return REPO_ROOT


def harness_root() -> Path:
    return REPO_ROOT / "驾驭工程"


def config_datas() -> Path:
    return _env_path("VGAME_CONFIG_DATAS") or (vgame_root() / "Config" / "GameConfig" / "Datas")


def client_graph() -> Path:
    configured = _env_path("VGAME_CLIENT_GRAPH")
    if configured and configured.is_file():
        return configured
    return REPO_ROOT / "knowledge-graph" / "client" / "knowledge-graph.json"


def code_root() -> Path:
    return _env_path("VGAME_CODE_ROOT") or (
        vgame_root() / "HorizonFlyProject" / "Packages" / "VGame"
    )


def skill_root() -> Path:
    return _env_path("VGAME_SKILL_ROOT") or (REPO_ROOT / "skills")


def source_docs_root() -> Path:
    return _env_path("VGAME_SOURCE_DOCS_ROOT") or (vgame_root() / "策划")


def output_root() -> Path:
    return _env_path("VGAME_OUTPUT_ROOT") or (REPO_ROOT / "output")
