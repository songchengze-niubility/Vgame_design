#!/usr/bin/env python3
"""将旧数值生产蓝图迁入 Git 仓库，并生成机器可读的迁移清单。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESTINATION = REPO_ROOT / "numerical-workflows" / "v2"
LEGACY_WORKBOOKS = (
    "Vgame基本战斗框架.xlsx",
    "Vgame经济框架.xlsx",
    "Vgame新手引导以及开启节奏.xlsx",
    "Vgame养成数值.xlsx",
)
FORMAL_WRITE_SCRIPTS = {"02_AI规则/apply_uilevel_reward_previews_to_formal.py"}


def sha256(path: Path, *, portable_text: bool = False) -> str:
    if portable_text and path.suffix.lower() in {".py", ".md", ".json"}:
        normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select(relative: str, suffix: str) -> tuple[bool, str]:
    normalized = relative.replace("\\", "/")
    if "__pycache__/" in normalized or "/_backups/" in normalized or ".bak_" in normalized:
        return False, "CACHE_OR_BACKUP"
    if normalized == "run_all.py":
        return True, "PRODUCTION_ENTRY"
    if normalized in {"README.md", "输入文档更新流程.md"}:
        return True, "WORKFLOW_DOCUMENT"
    if suffix == ".py":
        return True, "FORMAL_WRITE_TOOL" if normalized in FORMAL_WRITE_SCRIPTS else "PRODUCTION_SCRIPT"
    if normalized.startswith("00_总览/") and suffix == ".md":
        return True, "WORKFLOW_CONTEXT"
    if normalized.startswith("01_源表/") and suffix in {".xlsx", ".md"}:
        return True, "EDITABLE_SOURCE_WORKBOOK" if suffix == ".xlsx" else "SOURCE_DOCUMENT"
    if normalized.startswith("02_AI规则/") and suffix == ".md":
        return True, "EXECUTION_RULE"
    if normalized.startswith("03_沉淀MD/") and suffix == ".md" and "/废弃口径/" not in normalized:
        return True, "MACHINE_PARAMETER_OR_SYSTEM_INPUT"
    if normalized.startswith("经济/模块产销表/") and suffix == ".xlsx" and normalized.count("/") == 2:
        return True, "EDITABLE_ECONOMY_MODULE_WORKBOOK"
    if normalized in {"养成/README.md", "05_验算核算/README.md"}:
        return True, "WORKFLOW_DOCUMENT"
    return False, "GENERATED_OR_HISTORICAL"


def normalize_document(text: str) -> str:
    text = re.sub(r"(?i)[a-z]:[\\/]+vgame[\\/]+_design[\\/]+", "${VGAME_DESIGN_ROOT}/", text)
    text = re.sub(r"(?i)[a-z]:[\\/]+vgame_design[\\/]+", "${VGAME_DESIGN_ROOT}/", text)
    text = re.sub(r"(?i)[a-z]:[\\/]+vgame[\\/]+config[\\/]+gameconfig[\\/]+datas[\\/]*", "${VGAME_CONFIG_DATAS}/", text)
    text = re.sub(r"(?i)[a-z]:[\\/]+数值文档[\\/]+数值文档[\\/]+框架v2[\\/]*", "${VGAME_NUMERICAL_RUNTIME_ROOT}/", text)
    text = re.sub(r"(?i)[a-z]:[\\/]+数值文档[\\/]+数值文档[\\/]*", "${VGAME_NUMERICAL_LEGACY_INPUT_ROOT}/", text)
    text = re.sub(r"(?i)[a-z]:[\\/]+users[\\/]+[^\\/]+[\\/]+downloads[\\/]+", "vgame-input://downloads/", text)
    text = re.sub(r"(?i)[a-z]:[\\/]+vgame(?=[\\/`\s]|$)", "${VGAME_ROOT}", text)
    return text


def ensure_os_import(text: str) -> str:
    if "os.environ" not in text:
        return text
    if re.search(r"(?m)^import\s+os(?:\s|,|$)|^import\s+[^\n]*\bos\b", text):
        return text
    future = re.search(r"(?m)^from __future__ import [^\n]+\n", text)
    if future:
        return text[:future.end()] + "\nimport os\n" + text[future.end():]
    first_import = re.search(r"(?m)^(?:import |from [^\n]+ import )", text)
    if first_import:
        return text[:first_import.start()] + "import os\n" + text[first_import.start():]
    return "import os\n" + text


def normalize_python(text: str) -> str:
    root_pattern = r"Path\(r?[\"'][a-zA-Z]:[\\/]+数值文档[\\/]+数值文档[\\/]+框架v2[\"']\)"
    config_pattern = r"Path\(r?[\"'][a-zA-Z]:[\\/]+Vgame[\\/]+Config[\\/]+GameConfig[\\/]+Datas[\"']\)"
    config_default = r"os\.environ\.get\([\"']VGAME_CONFIG_DATAS[\"'],\s*r?[\"'][a-zA-Z]:[\\/]+Vgame[\\/]+Config[\\/]+GameConfig[\\/]+Datas[\"']\)"
    design_default = r"os\.environ\.get\([\"']VGAME_DESIGN_ROOT[\"'],\s*r?[\"'][a-zA-Z]:[\\/]+Vgame_design[\"']\)"
    text = re.sub(root_pattern, 'Path(os.environ.get("VGAME_NUMERICAL_RUNTIME_ROOT", str(Path(__file__).resolve().parents[1])))', text, flags=re.I)
    text = re.sub(config_pattern, 'Path(os.environ.get("VGAME_CONFIG_DATAS", ""))', text, flags=re.I)
    text = re.sub(config_default, 'os.environ.get("VGAME_CONFIG_DATAS", "")', text, flags=re.I)
    text = re.sub(design_default, 'os.environ.get("VGAME_DESIGN_ROOT", "")', text, flags=re.I)
    text = re.sub(r"(?i)本次未修改[a-z]:[\\/]+vgame[\\/]+config[\\/]+gameconfig[\\/]+datas", "本次未修改正式 Datas", text)
    return ensure_os_import(text)


def copy_file(source: Path, target: Path, role: str = "") -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() in {".py", ".md"}:
        content = source.read_text(encoding="utf-8-sig")
        content = normalize_python(content) if source.suffix.lower() == ".py" else normalize_document(content)
        if source.suffix.lower() == ".py":
            if source.name == "sync_global_sources_to_md.py":
                # 专武源页已被移除；裁决 B 要求兼容期继续使用已沉淀的参数 MD，
                # 不能伪造已不存在的源页，也不能因为兼容期而放弃其他源表校验。
                content = content.replace(
                    '    weapons = source["专武属性分配"]',
                    '    weapons = source["专武属性分配"] if "专武属性分配" in source.sheetnames else None',
                    1,
                )
                content = content.replace(
                    "    for row in range(4, weapons.max_row + 1):",
                    "    for row in (range(4, weapons.max_row + 1) if weapons is not None else ()):",
                    1,
                )
                content = content.replace(
                    "        day = next((day for day, reached, _ in day_curve if reached >= level), None)\n"
                    + '        sync.set("节奏", "主角等级_输入", row, 5, day,\n'
                    + '                 "节奏口径.xlsx/角色等级!P:R", "earliest_day_reaching_level")',
                    "        if day_curve:" + chr(10)
                    + "            day = next((day for day, reached, _ in day_curve if reached >= level), None)\n"
                    + '            sync.set("节奏", "主角等级_输入", row, 5, day,\n'
                    + '                     "节奏口径.xlsx/角色等级!P:R", "earliest_day_reaching_level")',
                    1,
                )
            if role == "FORMAL_WRITE_TOOL":
                main_signature = "def main() -> None:" + chr(10)
                if main_signature not in content:
                    raise ValueError(f"formal write tool has no supported main entry: {source}")
                content = content.replace(
                    main_signature,
                    main_signature
                    + '    if os.environ.get("VGAME_ALLOW_FORMAL_CONFIG_WRITE") != "USER_APPROVED":\n'
                    + '        raise RuntimeError("formal config write denied: explicit user authorization required")\n',
                    1,
                )
            compile(content, os.fspath(source), "exec")
        target.write_text(content.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    else:
        shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Vgame numerical production workflows")
    parser.add_argument("--source", required=True, type=Path, help="旧框架 v2 根目录")
    parser.add_argument("--destination", type=Path, default=DESTINATION)
    args = parser.parse_args()
    source_root = args.source.resolve()
    destination = args.destination.resolve()
    if not source_root.is_dir():
        raise SystemExit(f"source directory missing: {source_root}")
    if REPO_ROOT not in destination.parents:
        raise SystemExit(f"destination must stay inside repository: {destination}")

    framework = destination / "framework"
    legacy_inputs = destination / "legacy-inputs"
    rows = []
    for source in sorted(source_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(source_root).as_posix()
        if relative.startswith((".git/", "_backups/", "99_备份/", "_staging")):
            continue
        include, role = select(relative, source.suffix.lower())
        if not include:
            continue
        target = framework / relative
        copy_file(source, target, role)
        rows.append({
            "sourceRelativePath": relative,
            "repositoryPath": target.relative_to(REPO_ROOT).as_posix(),
            "role": role,
            "sourceSha256": sha256(source),
            "migratedSha256": sha256(target, portable_text=True),
            "bytes": target.stat().st_size,
            "requiresExplicitFormalWriteApproval": role == "FORMAL_WRITE_TOOL",
        })

    for name in LEGACY_WORKBOOKS:
        source = source_root.parent / name
        if not source.is_file():
            raise SystemExit(f"required legacy workbook missing: {source}")
        target = legacy_inputs / name
        copy_file(source, target)
        rows.append({
            "sourceRelativePath": f"../{name}",
            "repositoryPath": target.relative_to(REPO_ROOT).as_posix(),
            "role": "LEGACY_EDITABLE_SOURCE_WORKBOOK",
            "sourceSha256": sha256(source),
            "migratedSha256": sha256(target, portable_text=True),
            "bytes": target.stat().st_size,
            "requiresExplicitFormalWriteApproval": False,
        })

    original_python = [path for path in source_root.rglob("*.py") if "/.git/" not in path.as_posix() and "/_backups/" not in path.as_posix()]
    migrated_python = [row for row in rows if row["repositoryPath"].endswith(".py")]
    manifest = {
        "schema": "vgame-numerical-production-workflow-manifest/v1",
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "authority": "knowledge-base/README.md",
        "workflowRoot": destination.relative_to(REPO_ROOT).as_posix(),
        "runtimeOutputRoot": "output/numerical-production-workflow-v2/",
        "legacyExternalSourceRequiredAtRuntime": False,
        "formalConfigWriteDefault": "DENY",
        "contentHashPolicy": "TEXT_UTF8_NORMALIZED_LF_BINARY_RAW_SHA256",
        "counts": {
            "files": len(rows),
            "originalPythonFiles": len(original_python),
            "migratedPythonFiles": len(migrated_python),
            "legacyWorkbooks": len(LEGACY_WORKBOOKS),
            "inputWorkbooks": sum(row["repositoryPath"].endswith(".xlsx") for row in rows),
            "markdownInputs": sum(row["repositoryPath"].endswith(".md") for row in rows),
            "formalWriteTools": sum(row["requiresExplicitFormalWriteApproval"] for row in rows),
            "mainGenerationJobs": 22,
            "expectedFinalWorkbooks": 44,
        },
        "files": rows,
    }
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "workflow-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"schema": manifest["schema"], "counts": manifest["counts"]}, ensure_ascii=False, indent=2))
    if len(original_python) != len(migrated_python):
        print("[FAIL] not all legacy Python scripts were migrated")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
