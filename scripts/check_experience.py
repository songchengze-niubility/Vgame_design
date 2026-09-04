#!/usr/bin/env python3
"""校验 knowledge-base/experience/ 经验沉淀条目的完整性与引用有效性。

经验层是驾驭工程自进化回路的收口（写入：planning-feature-workflow 第 9 步；
召回：vgame-knowledge-router）。本脚本由 scripts/check.ps1 自动调用：
- FAIL 阻断提交：字段缺失、id 非法或重复、refs 指向不存在的文件；
- WARN 不阻断：正文过短、缺现象/根因小节、条目数为零。

用法：python scripts/check_experience.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIENCE_ROOT = REPO_ROOT / "knowledge-base" / "experience"

ID_PATTERN = re.compile(r"^EXP-(\d{8})-(\d{2,3})$")
STATUS_VOCAB = {"active", "incorporated", "obsolete"}
CATEGORY_SUGGESTED = {"harness", "config", "numerical", "workflow", "ui", "economy", "combat", "process"}
REQUIRED_KEYS = ("id", "date", "title", "category", "tags", "triggerTerms", "status", "source")
DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Report:
    def __init__(self) -> None:
        self.fails = 0
        self.warns = 0

    def fail(self, message: str) -> None:
        self.fails += 1
        print(f"[FAIL] {message}")

    def warn(self, message: str) -> None:
        self.warns += 1
        print(f"[WARN] {message}")

    def ok(self, message: str) -> None:
        print(f"[PASS] {message}")


def split_terms(raw: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,，;；]", raw or "") if item.strip()]


def parse_header(text: str) -> tuple[dict[str, str], str]:
    """解析文件头部的简单键值块；返回 (键值字典, 头部之后的正文)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    header: dict[str, str] = {}
    end_index = -1
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
        line = lines[index]
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            header[key.strip()] = value.strip()
    if end_index < 0:
        return {}, text
    return header, "\n".join(lines[end_index + 1:])


def check_entry(path: Path, report: Report, seen_ids: dict[str, str]) -> None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    text = path.read_text(encoding="utf-8-sig")
    header, body = parse_header(text)

    missing = [key for key in REQUIRED_KEYS if not header.get(key)]
    if missing:
        report.fail(f"{rel} 缺少必填字段：{'、'.join(missing)}")
        return
    report.ok(f"{rel} 必填字段齐全")

    entry_id = header["id"]
    match = ID_PATTERN.match(entry_id)
    if not match:
        report.fail(f"{rel} id 格式非法：{entry_id}（应为 EXP-YYYYMMDD-NN）")
    else:
        stem_date = re.search(r"exp-(\d{4}-\d{2}-\d{2})-", path.name)
        compact = f"{match.group(1)[:4]}-{match.group(1)[4:6]}-{match.group(1)[6:]}"
        if stem_date and stem_date.group(1) != compact:
            report.fail(f"{rel} 文件名日期 {stem_date.group(1)} 与 id 日期 {compact} 不一致")
        if entry_id in seen_ids:
            report.fail(f"{rel} id 重复：{entry_id} 已被 {seen_ids[entry_id]} 使用")
        else:
            seen_ids[entry_id] = rel

    raw_date = header.get("date", "")
    if not DATE_ONLY.match(raw_date):
        report.fail(f"{rel} date 格式非法：{raw_date}（应为 YYYY-MM-DD）")

    status = header.get("status", "")
    if status not in STATUS_VOCAB:
        report.fail(f"{rel} status 必须是 {'/'.join(sorted(STATUS_VOCAB))}，当前为 {status}")

    if split_terms(header.get("tags", "")):
        pass
    else:
        report.fail(f"{rel} tags 至少需要 1 个（供人工浏览）")
    if not split_terms(header.get("triggerTerms", "")):
        report.fail(f"{rel} triggerTerms 至少需要 1 个（否则路由永远无法召回该条目）")

    category = header.get("category", "")
    if category not in CATEGORY_SUGGESTED:
        report.warn(f"{rel} category `{category}` 不在常用清单内（harness/config/numerical/workflow/ui/economy/combat/process），确认后可保留")

    refs = split_terms(header.get("refs", ""))
    for ref in refs:
        target = REPO_ROOT / ref
        if not target.exists():
            report.fail(f"{rel} refs 指向不存在的路径：{ref}")

    clean_body = body.strip()
    if len(clean_body) < 30:
        report.warn(f"{rel} 正文过短（{len(clean_body)} 字符），教训细节应写满现象/根因/处理/规则化建议")
    for section in ("现象", "根因"):
        if section not in clean_body:
            report.warn(f"{rel} 正文缺少「{section}」内容")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    report = Report()

    print("=== Vgame Experience Knowledge Check ===")
    print(f"Entry root: {EXPERIENCE_ROOT.relative_to(REPO_ROOT).as_posix()}")

    for scaffold in ("README.md", "_TEMPLATE.md"):
        if (EXPERIENCE_ROOT / scaffold).exists():
            report.ok(f"{scaffold} 存在")
        else:
            report.fail(f"缺少 {scaffold}（收口规范与模板必须先于条目存在）")

    entries = sorted(EXPERIENCE_ROOT.glob("exp-*.md"))
    if not entries:
        report.warn("没有任何 exp-*.md 条目；经验层为空，请确认交付流程是否真的无教训可记")
    seen_ids: dict[str, str] = {}
    obsolete = incorporated = active = 0
    for path in entries:
        check_entry(path, report, seen_ids)
        status_line = next((line for line in path.read_text(encoding="utf-8-sig").splitlines()
                            if line.startswith("status:")), "")
        status_value = status_line.partition(":")[2].strip()
        if status_value == "active":
            active += 1
        elif status_value == "incorporated":
            incorporated += 1
        elif status_value == "obsolete":
            obsolete += 1
    if entries:
        report.ok(f"条目总数 {len(entries)}（active {active} / incorporated {incorporated} / obsolete {obsolete}）")

    print(f"=== 检查完成: FAIL {report.fails}, WARN {report.warns} ===")
    return 1 if report.fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
