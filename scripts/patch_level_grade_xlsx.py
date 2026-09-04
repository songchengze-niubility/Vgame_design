# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def worksheet_part(archive: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relation_id = None
    for sheet in workbook.findall(f"{{{MAIN_NS}}}sheets/{{{MAIN_NS}}}sheet"):
        if sheet.attrib.get("name") == sheet_name:
            relation_id = sheet.attrib[f"{{{REL_NS}}}id"]
            break
    if relation_id is None:
        raise AssertionError(f"工作簿缺少页签：{sheet_name}")
    relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target = None
    for relation in relations.findall(f"{{{PKG_REL_NS}}}Relationship"):
        if relation.attrib.get("Id") == relation_id:
            target = relation.attrib["Target"]
            break
    if target is None:
        raise AssertionError(f"页签关系缺失：{sheet_name}/{relation_id}")
    if target.startswith("/"):
        return target.lstrip("/")
    return str(PurePosixPath("xl") / target)


def patch_cells(xml: bytes, writes: list[dict]) -> bytes:
    result = xml
    for write in writes:
        coordinate = write["cell"]
        pattern = re.compile(
            rb'(<c\b(?=[^>]*\br="' + re.escape(coordinate.encode("ascii")) + rb'")[^>]*>.*?<v>)([^<]*)(</v>.*?</c>)',
            re.DOTALL,
        )
        matches = list(pattern.finditer(result))
        if len(matches) != 1:
            raise AssertionError(f"{coordinate} XML命中数量异常：{len(matches)}")
        old_text = matches[0].group(2).decode("utf-8")
        if float(old_text) != float(write["old_grade"]):
            raise AssertionError(
                f"{coordinate} 旧Grade不一致：XML={old_text} plan={write['old_grade']}"
            )
        new_text = str(int(write["new_grade"])).encode("ascii")
        result = pattern.sub(lambda match: match.group(1) + new_text + match.group(3), result, count=1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    writes = plan["level_writes"]
    if len(writes) != 526:
        raise AssertionError(f"Grade写入数量应为526，实际{len(writes)}")

    with zipfile.ZipFile(args.base, "r") as source:
        part = worksheet_part(source, "level")
        infos = source.infolist()
        contents = {info.filename: source.read(info.filename) for info in infos}
        names = [info.filename for info in infos]
        patched_sheet = patch_cells(contents[part], writes)
        with tempfile.NamedTemporaryFile(
            prefix="level-grade-", suffix=".xlsx", dir=args.target.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
        try:
            with zipfile.ZipFile(temporary, "w") as destination:
                for info in infos:
                    data = patched_sheet if info.filename == part else contents[info.filename]
                    destination.writestr(info, data)
            with zipfile.ZipFile(temporary, "r") as check:
                bad = check.testzip()
                if bad is not None:
                    raise AssertionError(f"xlsx压缩包损坏：{bad}")
                if check.namelist() != names:
                    raise AssertionError("xlsx包内文件清单发生变化")
                for name in names:
                    if name != part and check.read(name) != contents[name]:
                        raise AssertionError(f"非目标包内容发生变化：{name}")
            os.replace(temporary, args.target)
        finally:
            if temporary.exists():
                temporary.unlink()
    print(json.dumps({"status": "PASS", "target": str(args.target), "worksheet_part": part, "writes": len(writes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
