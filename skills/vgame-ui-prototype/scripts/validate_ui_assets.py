#!/usr/bin/env python3
"""Validate Vgame UI prototype HTML, PNG files, and traceability manifest."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


ID_PATTERNS = {
    "page": re.compile(r"^PAGE-[A-Z0-9][A-Z0-9-]*$"),
    "component": re.compile(r"^COMP-[A-Z0-9][A-Z0-9-]*$"),
    "rule": re.compile(r"^(?:R-[A-Z0-9][A-Z0-9-]*|RULE-[A-Z0-9][A-Z0-9-]*)$"),
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


class UiMarkerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.markers: dict[tuple[str, str], list[dict[str, str]]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        kind = values.get("data-ui-kind")
        item_id = values.get("data-ui-id")
        if kind in ID_PATTERNS and item_id:
            self.markers.setdefault((kind, item_id), []).append(values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ui-dir", required=True, type=Path, help="Directory containing index.html and UI assets")
    parser.add_argument("--require-components", action="store_true", help="Require at least one component record")
    return parser.parse_args()


def read_json(path: Path, result: Validation) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        result.error(f"missing manifest: {path.name}")
        return None
    except (OSError, json.JSONDecodeError) as exc:
        result.error(f"cannot parse {path.name}: {exc}")
        return None
    if not isinstance(data, dict):
        result.error("manifest root must be an object")
        return None
    return data


def safe_asset_path(ui_dir: Path, relative: Any, result: Validation, label: str) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        result.error(f"{label}.file must be a non-empty string")
        return None
    candidate = (ui_dir / relative).resolve()
    try:
        candidate.relative_to(ui_dir.resolve())
    except ValueError:
        result.error(f"{label}.file escapes ui directory: {relative}")
        return None
    if candidate.suffix.lower() != ".png":
        result.error(f"{label}.file must be PNG: {relative}")
    return candidate


def png_dimensions(path: Path, result: Validation, label: str) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError as exc:
        result.error(f"cannot read {label} PNG {path.name}: {exc}")
        return None
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        result.error(f"{label}.file is not a valid PNG: {path.name}")
        return None
    width, height = struct.unpack(">II", header[16:24])
    if width < 1 or height < 1:
        result.error(f"{label}.file has invalid dimensions: {path.name}")
        return None
    return width, height


def validate_rule_ids(value: Any, result: Validation, label: str) -> set[str]:
    valid: set[str] = set()
    if not isinstance(value, list) or not value:
        result.error(f"{label}.rule_ids must be a non-empty array")
        return valid
    for rule_id in value:
        if not isinstance(rule_id, str) or not ID_PATTERNS["rule"].fullmatch(rule_id):
            result.error(f"{label} has invalid rule ID: {rule_id!r}")
        else:
            valid.add(rule_id)
    return valid


def validate_record(
    record: Any,
    kind: str,
    index: int,
    ui_dir: Path,
    markers: dict[tuple[str, str], list[dict[str, str]]],
    result: Validation,
) -> tuple[str | None, str | None, str | None]:
    label = f"{kind}[{index}]"
    if not isinstance(record, dict):
        result.error(f"{label} must be an object")
        return None, None, None

    item_id = record.get("id")
    if not isinstance(item_id, str) or not ID_PATTERNS[kind].fullmatch(item_id):
        result.error(f"{label}.id is invalid: {item_id!r}")
        item_id = None
    else:
        matched_markers = markers.get((kind, item_id), [])
        if not matched_markers:
            result.error(f"{label}.id is not marked as {kind} in index.html: {item_id}")
        elif len(matched_markers) > 1:
            result.error(f"{label}.id is not unique in index.html: {item_id}")

    name = record.get("name")
    if not isinstance(name, str) or not name.strip():
        result.error(f"{label}.name must be a non-empty string")

    selector = record.get("selector")
    if not isinstance(selector, str) or not selector.strip():
        result.error(f"{label}.selector must be a non-empty string")

    state = record.get("state")
    if not isinstance(state, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", state):
        result.error(f"{label}.state must be lowercase kebab-case")
        state = None

    rule_ids = validate_rule_ids(record.get("rule_ids"), result, label)
    if item_id:
        matched_markers = markers.get((kind, item_id), [])
        if len(matched_markers) == 1:
            marker_rule_ids = set(matched_markers[0].get("data-rule-ids", "").split())
            missing_rules = rule_ids - marker_rule_ids
            if missing_rules:
                result.error(
                    f"{label}.rule_ids missing from HTML marker {item_id}: "
                    + ", ".join(sorted(missing_rules))
                )
    asset_path = safe_asset_path(ui_dir, record.get("file"), result, label)
    relative_file = record.get("file") if isinstance(record.get("file"), str) else None
    if item_id and state and relative_file:
        suffix = item_id.split("-", 1)[1].lower()
        expected_file = f"page-{suffix}.png" if kind == "page" else f"component-{suffix}-{state}.png"
        if relative_file != expected_file:
            result.error(f"{label}.file must be {expected_file!r}, got {relative_file!r}")
    if asset_path:
        if not asset_path.is_file():
            result.error(f"{label}.file does not exist: {relative_file}")
        else:
            png_dimensions(asset_path, result, label)

    return item_id, state, relative_file


def validate(ui_dir: Path, require_components: bool) -> Validation:
    result = Validation()
    if not ui_dir.is_dir():
        result.error(f"ui directory does not exist: {ui_dir}")
        return result

    html_path = ui_dir / "index.html"
    try:
        html = html_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        result.error("missing index.html")
        html = ""
    except OSError as exc:
        result.error(f"cannot read index.html: {exc}")
        html = ""

    marker_parser = UiMarkerParser()
    try:
        marker_parser.feed(html)
    except Exception as exc:
        result.error(f"cannot parse index.html markers: {exc}")

    manifest = read_json(ui_dir / "ui-asset-manifest.json", result)
    if manifest is None:
        return result

    if manifest.get("schema_version") != "1.0":
        result.error("schema_version must be '1.0'")
    if manifest.get("source_html") != "index.html":
        result.error("source_html must be 'index.html'")

    viewport = manifest.get("viewport")
    if not isinstance(viewport, dict):
        result.error("viewport must be an object")
    else:
        for key in ("width", "height"):
            if not isinstance(viewport.get(key), int) or viewport[key] < 1:
                result.error(f"viewport.{key} must be a positive integer")
        scale = viewport.get("device_scale_factor", 1)
        if not isinstance(scale, (int, float)) or scale <= 0:
            result.error("viewport.device_scale_factor must be positive")

    pages = manifest.get("pages")
    components = manifest.get("components")
    if not isinstance(pages, list) or not pages:
        result.error("pages must be a non-empty array")
        pages = []
    if not isinstance(components, list):
        result.error("components must be an array")
        components = []
    if require_components and not components:
        result.error("at least one component is required")

    page_ids: set[str] = set()
    record_keys: set[tuple[str, str, str]] = set()
    files: set[str] = set()

    for index, record in enumerate(pages):
        item_id, state, relative_file = validate_record(record, "page", index, ui_dir, marker_parser.markers, result)
        if item_id:
            if item_id in page_ids:
                result.error(f"duplicate page ID: {item_id}")
            page_ids.add(item_id)
        if item_id and state:
            key = ("page", item_id, state)
            if key in record_keys:
                result.error(f"duplicate page state: {item_id}/{state}")
            record_keys.add(key)
        if relative_file:
            if relative_file in files:
                result.error(f"duplicate asset file: {relative_file}")
            files.add(relative_file)

    for index, record in enumerate(components):
        item_id, state, relative_file = validate_record(record, "component", index, ui_dir, marker_parser.markers, result)
        page_id = record.get("page_id") if isinstance(record, dict) else None
        if page_id not in page_ids:
            result.error(f"component[{index}].page_id does not reference a page: {page_id!r}")
        if item_id:
            matched_markers = marker_parser.markers.get(("component", item_id), [])
            if len(matched_markers) == 1 and matched_markers[0].get("data-page-id") != page_id:
                result.error(
                    f"component[{index}].page_id does not match index.html marker: "
                    f"{page_id!r} != {matched_markers[0].get('data-page-id')!r}"
                )
        if item_id and state:
            key = ("component", item_id, state)
            if key in record_keys:
                result.error(f"duplicate component state: {item_id}/{state}")
            record_keys.add(key)
        if relative_file:
            if relative_file in files:
                result.error(f"duplicate asset file: {relative_file}")
            files.add(relative_file)

    # Only rendered page/component exports belong to the manifest. Static source
    # artwork under ui/assets/ is allowed by the asset contract and is validated
    # indirectly through the browser render, so it must not be treated as an
    # orphan export.
    disk_pngs = {
        path.relative_to(ui_dir).as_posix()
        for path in ui_dir.rglob("*.png")
        if "assets" not in path.relative_to(ui_dir).parts
    }
    for orphan in sorted(disk_pngs - files):
        result.error(f"PNG has no manifest record: {orphan}")
    for missing in sorted(files - disk_pngs):
        result.error(f"manifest references missing PNG: {missing}")

    return result


def main() -> int:
    args = parse_args()
    result = validate(args.ui_dir.resolve(), args.require_components)
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
    sys.exit(main())
