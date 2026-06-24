#!/usr/bin/env python3
"""Validate a Vgame editable-Figma handoff manifest."""

from __future__ import annotations

import argparse
import json
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PAGE_ID = re.compile(r"PAGE-\d{3,}")
COMP_ID = re.compile(r"COMP-\d{3,}")
FLOW_ID = re.compile(r"FLOW-\d{3,}")
NODE_ID = re.compile(r"\d+[:\-]\d+")
RULE_ID = re.compile(r"(?:R-\d+|RULE-\d+)")
PLAN_GATE_BLOCK = re.compile(r"```planning-workflow-gate\s*(\{.*?\})\s*```", re.DOTALL)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--require-previews", action="store_true")
    return parser.parse_args()


def load_json(path: Path, result: Result) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result.error(f"manifest does not exist: {path}")
        return {}
    except json.JSONDecodeError as exc:
        result.error(f"manifest is invalid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        result.error("manifest root must be an object")
        return {}
    return data


def nonempty_string(value: Any, label: str, result: Result) -> str | None:
    if not isinstance(value, str) or not value.strip():
        result.error(f"{label} must be a non-empty string")
        return None
    return value.strip()


def validate_png(path: Path, label: str, result: Result) -> None:
    if not path.is_file():
        result.error(f"{label} does not exist: {path}")
        return
    try:
        header = path.read_bytes()[:24]
    except OSError as exc:
        result.error(f"{label} cannot be read: {exc}")
        return
    if len(header) < 24 or header[:8] != PNG_SIGNATURE:
        result.error(f"{label} is not a valid PNG: {path.name}")
        return
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        result.error(f"{label} has invalid dimensions: {width}x{height}")


def collect_contract_rule_ids(path: Path | None, result: Result) -> set[str] | None:
    if path is None:
        return None
    if not path.is_file():
        result.error(f"contract does not exist: {path}")
        return set()
    return set(RULE_ID.findall(path.read_text(encoding="utf-8")))


def validate_plan_approval(plan_path: Path, result: Result) -> None:
    if not plan_path.is_file():
        result.error(f"UI plan does not exist: {plan_path}")
        return
    text = plan_path.read_text(encoding="utf-8")
    if "figma_ui_plan_confirmed=true" not in text:
        result.error("UI plan does not declare figma_ui_plan_confirmed=true")
    approved_gate = False
    for raw in PLAN_GATE_BLOCK.findall(text):
        try:
            gate = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if gate.get("phase") == "figma_ui_plan" and gate.get("outcome") == "success":
            approved_gate = bool(str(gate.get("evidence", "")).strip())
            break
    if not approved_gate:
        result.error("UI plan lacks an approved figma_ui_plan success gate with evidence")


def validate_figma_target(target_path: Path, result: Result) -> dict[str, Any]:
    try:
        target = json.loads(target_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result.error(f"Figma target does not exist: {target_path}")
        return {}
    except json.JSONDecodeError as exc:
        result.error(f"Figma target is invalid JSON: {exc}")
        return {}
    if not isinstance(target, dict):
        result.error("Figma target root must be an object")
        return {}

    if target.get("schema_version") != "1.0":
        result.error("Figma target schema_version must be '1.0'")
    nonempty_string(target.get("feature"), "Figma target feature", result)
    if target.get("source") not in ("existing_file", "created_blank_file"):
        result.error("Figma target source must be existing_file or created_blank_file")
    file_key = nonempty_string(target.get("file_key"), "Figma target file_key", result)
    file_url = nonempty_string(target.get("url"), "Figma target url", result)
    if file_url and "figma.com/design/" not in file_url:
        result.error("Figma target url must be a Figma design URL")
    if file_key and file_url and file_key not in file_url:
        result.error("Figma target url does not contain its file_key")

    node_id = target.get("target_node_id")
    page_name = target.get("target_page_name")
    if node_id is not None and (not isinstance(node_id, str) or not NODE_ID.fullmatch(node_id)):
        result.error(f"Figma target target_node_id is invalid: {node_id!r}")
    if node_id is None and (not isinstance(page_name, str) or not page_name.strip()):
        result.error("Figma target requires target_node_id or target_page_name")
    if target.get("access_verified") is not True:
        result.error("Figma target access_verified must be true")
    if target.get("confirmed") is not True:
        result.error("Figma target confirmed must be true")
    nonempty_string(target.get("approval_evidence"), "Figma target approval_evidence", result)
    return target


def validate_figma_target_link(
    record: Any,
    manifest_path: Path,
    target_path: Path | None,
    result: Result,
) -> dict[str, Any]:
    if not isinstance(record, dict):
        result.error("figma_target must be an object")
        return {}
    source = nonempty_string(record.get("source"), "figma_target.source", result)
    if record.get("confirmed") is not True:
        result.error("figma_target.confirmed must be true")
    if target_path is None:
        return {}
    if source:
        expected = (manifest_path.parent / source).resolve()
        if expected != target_path.resolve():
            result.error(f"figma_target.source does not match --target: {source}")
    return validate_figma_target(target_path, result)


def validate_ui_plan(
    record: Any,
    manifest_path: Path,
    plan_path: Path | None,
    result: Result,
) -> None:
    if not isinstance(record, dict):
        result.error("ui_plan must be an object")
        return
    source = nonempty_string(record.get("source"), "ui_plan.source", result)
    if record.get("confirmed") is not True:
        result.error("ui_plan.confirmed must be true")
    nonempty_string(record.get("approval_evidence"), "ui_plan.approval_evidence", result)

    if plan_path is None:
        return
    if source:
        expected = (manifest_path.parent / source).resolve()
        if expected != plan_path.resolve():
            result.error(f"ui_plan.source does not match --plan: {source}")
    validate_plan_approval(plan_path, result)


def validate_rule_ids(
    values: Any,
    label: str,
    contract_ids: set[str] | None,
    result: Result,
) -> None:
    if not isinstance(values, list) or not values:
        result.error(f"{label} must be a non-empty array")
        return
    for index, value in enumerate(values):
        if not isinstance(value, str) or not RULE_ID.fullmatch(value):
            result.error(f"{label}[{index}] is not a valid rule ID: {value!r}")
        elif contract_ids is not None and value not in contract_ids:
            result.error(f"{label}[{index}] is absent from the design contract: {value}")


def validate_preview(
    record: dict[str, Any],
    label: str,
    manifest_dir: Path,
    require_previews: bool,
    seen_files: set[str],
    result: Result,
) -> None:
    value = record.get("preview_file")
    if value is None:
        if require_previews:
            result.error(f"{label}.preview_file is required")
        return
    relative = nonempty_string(value, f"{label}.preview_file", result)
    if relative is None:
        return
    normalized = Path(relative)
    if normalized.is_absolute() or ".." in normalized.parts:
        result.error(f"{label}.preview_file must stay inside the Figma handoff directory")
        return
    if normalized.suffix.lower() != ".png":
        result.error(f"{label}.preview_file must be PNG: {relative}")
        return
    posix = normalized.as_posix()
    if posix in seen_files:
        result.error(f"duplicate preview file: {posix}")
    seen_files.add(posix)
    validate_png(manifest_dir / normalized, f"{label}.preview_file", result)


def validate_manifest(
    manifest_path: Path,
    contract_path: Path | None,
    plan_path: Path | None,
    target_path: Path | None,
    require_previews: bool,
) -> Result:
    result = Result()
    manifest = load_json(manifest_path, result)
    if not manifest:
        return result

    if manifest.get("schema_version") != "1.0":
        result.error("schema_version must be '1.0'")
    nonempty_string(manifest.get("feature"), "feature", result)
    nonempty_string(manifest.get("rule_id_source"), "rule_id_source", result)
    validate_ui_plan(manifest.get("ui_plan"), manifest_path, plan_path, result)
    target = validate_figma_target_link(manifest.get("figma_target"), manifest_path, target_path, result)

    figma_file = manifest.get("figma_file")
    if not isinstance(figma_file, dict):
        result.error("figma_file must be an object")
        figma_file = {}
    file_key = nonempty_string(figma_file.get("file_key"), "figma_file.file_key", result)
    file_url = nonempty_string(figma_file.get("url"), "figma_file.url", result)
    nonempty_string(figma_file.get("name"), "figma_file.name", result)
    if file_url and "figma.com/design/" not in file_url:
        result.error("figma_file.url must be a Figma design URL")
    if file_key and file_url and file_key not in file_url:
        result.error("figma_file.url does not contain figma_file.file_key")
    if target:
        if manifest.get("feature") != target.get("feature"):
            result.error("manifest feature does not match the confirmed Figma target")
        if file_key != target.get("file_key"):
            result.error("figma_file.file_key does not match the confirmed Figma target")
        if file_url != target.get("url"):
            result.error("figma_file.url does not match the confirmed Figma target")

    viewport = manifest.get("reference_viewport")
    if not isinstance(viewport, dict):
        result.error("reference_viewport must be an object")
        viewport = {}
    for key in ("width", "height"):
        value = viewport.get(key)
        if not isinstance(value, int) or value <= 0:
            result.error(f"reference_viewport.{key} must be a positive integer")
    safe_area = viewport.get("safe_area_percent")
    if not isinstance(safe_area, (int, float)) or not 50 <= safe_area <= 100:
        result.error("reference_viewport.safe_area_percent must be between 50 and 100")

    contract_ids = collect_contract_rule_ids(contract_path, result)
    manifest_dir = manifest_path.parent
    seen_previews: set[str] = set()

    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        result.error("pages must be a non-empty array")
        pages = []
    page_ids: set[str] = set()
    node_ids: set[str] = set()
    for index, page in enumerate(pages):
        label = f"pages[{index}]"
        if not isinstance(page, dict):
            result.error(f"{label} must be an object")
            continue
        page_id = page.get("id")
        if not isinstance(page_id, str) or not PAGE_ID.fullmatch(page_id):
            result.error(f"{label}.id is invalid: {page_id!r}")
        elif page_id in page_ids:
            result.error(f"duplicate page ID: {page_id}")
        else:
            page_ids.add(page_id)
        nonempty_string(page.get("name"), f"{label}.name", result)
        node_id = page.get("node_id")
        if not isinstance(node_id, str) or not NODE_ID.fullmatch(node_id):
            result.error(f"{label}.node_id is invalid: {node_id!r}")
        elif node_id in node_ids:
            result.error(f"duplicate Figma node ID: {node_id}")
        else:
            node_ids.add(node_id)
        validate_rule_ids(page.get("rule_ids"), f"{label}.rule_ids", contract_ids, result)
        validate_preview(page, label, manifest_dir, require_previews, seen_previews, result)

    components = manifest.get("components")
    if not isinstance(components, list) or not components:
        result.error("components must be a non-empty array")
        components = []
    component_ids: set[str] = set()
    for index, component in enumerate(components):
        label = f"components[{index}]"
        if not isinstance(component, dict):
            result.error(f"{label} must be an object")
            continue
        component_id = component.get("id")
        if not isinstance(component_id, str) or not COMP_ID.fullmatch(component_id):
            result.error(f"{label}.id is invalid: {component_id!r}")
        elif component_id in component_ids:
            result.error(f"duplicate component ID: {component_id}")
        else:
            component_ids.add(component_id)
        nonempty_string(component.get("name"), f"{label}.name", result)
        if component.get("page_id") not in page_ids:
            result.error(f"{label}.page_id does not reference a page: {component.get('page_id')!r}")
        node_id = component.get("node_id")
        if not isinstance(node_id, str) or not NODE_ID.fullmatch(node_id):
            result.error(f"{label}.node_id is invalid: {node_id!r}")
        elif node_id in node_ids:
            result.error(f"duplicate Figma node ID: {node_id}")
        else:
            node_ids.add(node_id)
        states = component.get("states")
        if not isinstance(states, list) or not states or any(not isinstance(x, str) or not x for x in states):
            result.error(f"{label}.states must be a non-empty string array")
        elif len(states) != len(set(states)):
            result.error(f"{label}.states contains duplicates")
        validate_rule_ids(component.get("rule_ids"), f"{label}.rule_ids", contract_ids, result)
        validate_preview(component, label, manifest_dir, require_previews, seen_previews, result)

    flows = manifest.get("flows")
    if not isinstance(flows, list):
        result.error("flows must be an array")
        flows = []
    flow_ids: set[str] = set()
    for index, flow in enumerate(flows):
        label = f"flows[{index}]"
        if not isinstance(flow, dict):
            result.error(f"{label} must be an object")
            continue
        flow_id = flow.get("id")
        if not isinstance(flow_id, str) or not FLOW_ID.fullmatch(flow_id):
            result.error(f"{label}.id is invalid: {flow_id!r}")
        elif flow_id in flow_ids:
            result.error(f"duplicate flow ID: {flow_id}")
        else:
            flow_ids.add(flow_id)
        if flow.get("from_page_id") not in page_ids or flow.get("to_page_id") not in page_ids:
            result.error(f"{label} references an unknown page")
        nonempty_string(flow.get("trigger"), f"{label}.trigger", result)
        validate_rule_ids(flow.get("rule_ids"), f"{label}.rule_ids", contract_ids, result)

    handoff = manifest.get("handoff")
    if not isinstance(handoff, dict):
        result.error("handoff must be an object")
        handoff = {}
    nonempty_string(handoff.get("target_engine"), "handoff.target_engine", result)
    for key in (
        "editable_source_confirmed",
        "component_instances_confirmed",
        "prototype_links_confirmed",
        "export_specs_confirmed",
        "nine_slice_annotations_confirmed",
        "safe_area_confirmed",
        "localization_stress_tested",
    ):
        if handoff.get(key) is not True:
            result.error(f"handoff.{key} must be true")
    if not isinstance(handoff.get("unresolved_items"), list):
        result.error("handoff.unresolved_items must be an array")
    elif handoff["unresolved_items"]:
        result.warn(f"handoff has {len(handoff['unresolved_items'])} unresolved item(s)")

    return result


def main() -> int:
    args = parse_args()
    result = validate_manifest(
        args.manifest.resolve(),
        args.contract.resolve() if args.contract else None,
        args.plan.resolve() if args.plan else None,
        args.target.resolve() if args.target else None,
        args.require_previews,
    )
    for warning in result.warnings:
        print(f"[WARN] {warning}")
    for error in result.errors:
        print(f"[FAIL] {error}")
    if result.errors:
        print(f"Validation failed: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
        return 1
    print(f"Validation passed: 0 errors, {len(result.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
