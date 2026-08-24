#!/usr/bin/env python3
"""把外部数值框架原子化登记到受 Git 管理的策划知识库。

这是一次 authoring/import 工具，不属于离线重建依赖。输出只包含来源清单、结构、
规范化摘要、数值陈述和映射，不复制工作簿或整份 Markdown 正文。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


DOMAIN_RULES = [
    ("combat", ("战斗", "伤害", "属性", "技能系数", "怪物", "boss", "难度")),
    ("growth", ("养成", "升级", "升星", "突破", "星盘", "能效", "专武", "旅券", "映射装备", "炮台", "房车", "收容物", "战力")),
    ("pacing", ("节奏", "开放", "日程", "主角等级", "天数", "里程碑")),
    ("probability", ("概率", "抽卡", "随机", "权重", "保底")),
    ("monetization-liveops", ("商业化", "月卡", "礼包", "付费", "通行证", "活动", "赛季", "开服")),
    ("reward-drop", ("奖励", "掉落", "drop", "首通", "扫荡", "体力")),
    ("economy", ("经济", "产销", "定价", "资源", "金币", "钻石", "商店", "成本", "消耗", "收入")),
    ("validation-delivery", ("验算", "核算", "校验", "验证", "配置", "落表", "回执", "报告")),
]

SYSTEM_RULES = [
    (("主线",), ("SYS-OUT-GP-01",)), (("困难主线", "高难主线"), ("SYS-OUT-GP-02",)),
    (("资源副本", "金币副本", "角色经验"), ("SYS-OUT-GP-03",)), (("旅券副本",), ("SYS-OUT-GP-04",)),
    (("映射副本", "映射装备副本"), ("SYS-OUT-GP-05",)), (("无限挑战",), ("SYS-OUT-GP-06",)),
    (("竞技场", "pvpve"), ("SYS-OUT-GP-07",)), (("爬塔",), ("SYS-OUT-GP-08",)),
    (("大秘境",), ("SYS-OUT-GP-09",)), (("boss挑战",), ("SYS-OUT-GP-10",)),
    (("扫荡",), ("SYS-OUT-GP-11",)), (("跑商",), ("SYS-OUT-GP-12",)),
    (("主角等级", "玩家等级"), ("SYS-OUT-GR-01",)), (("角色升级", "角色升阶", "突破"), ("SYS-OUT-GR-02",)),
    (("角色升星",), ("SYS-OUT-GR-03",)), (("星盘", "能效"), ("SYS-OUT-GR-04",)),
    (("收容物养成",), ("SYS-OUT-GR-05",)), (("旅券属性", "旅券养成"), ("SYS-OUT-GR-06",)),
    (("映射装备",), ("SYS-OUT-GR-07",)), (("炮台", "基地"), ("SYS-OUT-GR-08",)),
    (("房车",), ("SYS-OUT-GR-09",)), (("专武",), ("SYS-OUT-GR-10",)),
    (("角色抽卡", "新手卡池"), ("SYS-OUT-SU-01",)), (("收容物抽卡",), ("SYS-OUT-SU-02",)),
    (("碎片回收", "招募商店"), ("SYS-OUT-SU-03",)), (("物品", "货币", "资源"), ("SYS-OUT-SU-04",)),
    (("掉落", "奖励", "drop"), ("SYS-OUT-SU-05",)), (("商店",), ("SYS-OUT-SU-06",)),
    (("任务",), ("SYS-OUT-SU-07",)), (("签到",), ("SYS-OUT-SU-08",)),
    (("邮件",), ("SYS-OUT-SU-09",)), (("通行证",), ("SYS-OUT-SU-10",)),
    (("公会",), ("SYS-OUT-SU-11",)), (("好友", "聊天"), ("SYS-OUT-SU-12",)),
    (("新手", "开放"), ("SYS-OUT-SU-13",)), (("活动", "赛季", "liveops", "开服"), ("SYS-OUT-SU-14",)),
    (("月卡", "礼包", "付费", "商业化"), ("SYS-OUT-SU-15",)),
    (("伤害", "战斗公式", "战斗属性"), ("SYS-IN-01", "SYS-IN-02", "SYS-IN-03")),
    (("怪物", "boss", "ai"), ("SYS-IN-04",)), (("关卡", "遭遇", "难度"), ("SYS-IN-05", "SYS-IN-06")),
    (("结算", "胜负"), ("SYS-IN-08",)),
]

SKILLS_BY_DOMAIN = {
    "shared-foundation": ["game-numerical-analysis", "vgame-config-schema"],
    "combat": ["game-numerical-analysis", "vgame-battle-tuning-helper"],
    "growth": ["game-numerical-analysis", "vgame-growth-combat-conversion-map", "vgame-player-progression-simulator"],
    "economy": ["senior-game-economy", "vgame-economy-source-map", "vgame-player-progression-simulator"],
    "pacing": ["outer-loop-progression-pacing", "vgame-level-progression-map", "vgame-player-progression-simulator"],
    "probability": ["game-numerical-analysis", "senior-game-economy"],
    "reward-drop": ["vgame-reward-drop-sync", "vgame-economy-source-map"],
    "monetization-liveops": ["game-monetization", "planning-liveops-readiness", "senior-game-economy"],
    "validation-delivery": ["game-numerical-analysis", "vgame-config-quality-audit", "vgame-config-schema"],
}

FRAMEWORK_BY_DOMAIN = {
    "shared-foundation": ["PFN-13", "PFN-14", "PFN-15"], "combat": ["PFN-10", "PFN-12", "PFN-13"],
    "growth": ["PFN-06", "PFN-13", "PFN-16"], "economy": ["PFN-07", "PFN-13", "PFN-16"],
    "pacing": ["PFN-05", "PFN-09", "PFN-13"], "probability": ["PFN-08", "PFN-13"],
    "reward-drop": ["PFN-07", "PFN-13", "PFN-14"], "monetization-liveops": ["PFN-08", "PFN-09", "PFN-13"],
    "validation-delivery": ["PFN-13", "PFN-18", "PFN-19"],
}


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:12].upper()}"


def disposition(rel: str, suffix: str) -> tuple[str, str]:
    low = rel.lower().replace("\\", "/")
    if any(x in low for x in ("/_backups/", "99_备份/", "_backups/", ".bak", "正式配置备份/")):
        return "ARCHIVE_TRACE_ONLY", "历史/备份证据，仅保留哈希与路径"
    if any(x in low for x in ("_staging", "06_最终配置/")):
        return "MIRROR_OR_STAGING_TRACE_ONLY", "配置镜像或临时产物，不进入正式正文"
    if any(x in low for x in ("/_reports/", "_reports/", "04_数值文档/", "节奏/生成_", "生成_")):
        return "REGENERATABLE_OR_READING_OUTPUT", "派生阅读/报告/生成物，仅登记来源"
    if low.startswith("05_验算核算/"):
        return "VALIDATION_EVIDENCE", "验算与交付回执证据"
    if suffix in (".py", ".json") or low.startswith(("_shared/", "02_ai规则/")):
        return "TOOLING_OR_RULE_EVIDENCE", "工具或机器规则证据"
    if low.startswith("01_源表/") or "经济/模块产销表/" in low:
        return "SOURCE_WORKBOOK_EVIDENCE", "人可编辑源表或模块产销源表"
    if low.startswith(("00_总览/", "03_沉淀md/")) or low in ("readme.md", "输入文档更新流程.md"):
        return "NORMALIZED_INTO_CANONICAL", "内容按章节原子化迁入"
    return "REGISTERED_EVIDENCE", "纳入证据账本，按需回源"


def infer_domain(text: str) -> str:
    low = text.lower()
    for domain, words in DOMAIN_RULES:
        if any(word in low for word in words):
            return domain
    return "shared-foundation"


def systems_for(text: str, domain: str) -> list[str]:
    low = text.lower().replace(" ", "")
    found: list[str] = []
    for words, ids in SYSTEM_RULES:
        if any(word.lower().replace(" ", "") in low for word in words):
            found.extend(ids)
    if not found:
        found = {
            "combat": ["SYS-IN-01"], "growth": ["SYS-OUT-GR-01"], "economy": ["SYS-OUT-SU-04"],
            "pacing": ["SYS-OUT-SU-13"], "probability": ["SYS-OUT-SU-01"], "reward-drop": ["SYS-OUT-SU-05"],
            "monetization-liveops": ["SYS-OUT-SU-14"], "validation-delivery": ["SYS-OUT-SU-04"],
            "shared-foundation": ["SYS-OUT-SU-04"],
        }[domain]
    return list(dict.fromkeys(found))


def config_candidates(text: str) -> list[str]:
    low = text.lower()
    rules = [
        (("掉落", "奖励", "副本", "首通"), "Drop / UIlevel"), (("角色", "英雄"), "Hero*"),
        (("技能", "buff"), "HeroSkill / Buff*"), (("专武",), "Weapon* / HeroExclusiveWeapon*"),
        (("映射装备",), "Equip* / MappingEquip*"), (("房车",), "RV* / Motorhome*"),
        (("抽卡", "概率"), "Gacha* / Pool*"), (("商店",), "Shop*"), (("任务",), "Task*"),
        (("关卡", "主线", "难度"), "Level* / UIlevel"), (("物品", "货币", "经济"), "Item / Currency*"),
    ]
    found = [target for words, target in rules if any(w in low for w in words)]
    return found or ["UNKNOWN_REQUIRES_SOURCE_LOOKUP"]


def markdown_sections(text: str, fallback_title: str) -> list[tuple[str, int, str]]:
    matches = list(re.finditer(r"(?m)^(#{1,4})\s+(.+?)\s*$", text))
    if not matches:
        return [(fallback_title, 1, text)]
    result = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result.append((match.group(2).strip(), text.count("\n", 0, match.start()) + 1, text[match.end():end].strip()))
    return result


def clean_summary(body: str, title: str) -> str:
    lines = []
    in_fence = False
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line or line.startswith(("<!--", "|---", "#")):
            continue
        line = re.sub(r"^[-*+>]\s*", "", line)
        line = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", line)
        lines.append(line)
        if sum(map(len, lines)) >= 420:
            break
    summary = " ".join(lines)[:500].strip()
    return summary or f"{title}（源章节未提供可直接摘要的自然语言正文）"


def normalize_portable_text(value: str) -> str:
    """把旧机绝对路径转换为仓库相对路径或逻辑证据 URI。"""
    value = re.sub(r"(?i)[a-z]:[\\/]+vgame_design[\\/]+", "", value)
    value = re.sub(r"(?i)[a-z]:[\\/]+数值文档[\\/]+数值文档[\\/]+框架v2[\\/]+", "vgame-numeric-source://框架v2/", value)
    value = re.sub(r"(?i)[a-z]:[\\/]+数值文档[\\/]+数值文档[\\/]+", "vgame-numeric-source://", value)
    return value.replace("\\", "/")


def numeric_statements(body: str) -> list[str]:
    out = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or len(line) > 600 or line.startswith(("```", "<!--")):
            continue
        if re.search(r"\d", line) and re.search(r"[%+\-*/=<>～~：:]|权重|概率|倍率|天|级|层|成本|产出", line, re.I):
            line = re.sub(r"\s+", " ", line)
            if line not in out:
                out.append(line)
    return out


def apply_latest_ruling_status(atom: dict) -> dict:
    blob = " ".join([atom.get("title", ""), atom.get("statement", ""), *(atom.get("numericStatements") or [])]).lower()
    ew_stale = (
        r"专武（已废弃）", r"专武(?:系统|抽卡)?已废弃", r"当前版本已移除专武", r"旧消耗不得迁移到收容物",
        r"专武进度和专武属性贡献", r"移除专武进度", r"不接入当前验算",
    )
    rv_stale = (r"固定\s*\+?100", r"不参与随机强化", r"不参与随机结果")
    if any(re.search(pattern, blob) for pattern in ew_stale):
        atom["status"] = "SUPERSEDED_SOURCE_CONTEXT"
        atom["sourceNature"] = "SOURCE_EXPLICIT_SUPERSEDED"
        atom["supersededBy"] = "RULING-EW-B"
        atom["validation"] = ["TRACE_ONLY", "DO_NOT_ROUTE_AS_CURRENT"]
    elif any(re.search(pattern, blob) for pattern in rv_stale):
        atom["status"] = "SUPERSEDED_SOURCE_CONTEXT"
        atom["sourceNature"] = "SOURCE_EXPLICIT_SUPERSEDED"
        atom["supersededBy"] = "RULING-RV-C"
        atom["validation"] = ["TRACE_ONLY", "DO_NOT_ROUTE_AS_CURRENT"]
    elif re.search(r"变更记录|更新记录|历史版本|历史口径", atom.get("title", ""), re.I) or re.search(r"d:[/\\]vgame_design", blob, re.I):
        atom["status"] = "HISTORICAL_SOURCE_CONTEXT"
        atom["sourceNature"] = "SOURCE_EXPLICIT_HISTORICAL"
        atom["validation"] = ["TRACE_ONLY", "DO_NOT_ROUTE_AS_CURRENT"]
        if re.search(r"d:[/\\]vgame_design", blob, re.I):
            atom["legacyPathNote"] = "历史路径仅用于证据追溯；当前权威仓库为本仓库根目录。"
    return atom


def workbook_sheets(path: Path) -> tuple[list[str], str | None]:
    try:
        with zipfile.ZipFile(path) as zf:
            root = ET.fromstring(zf.read("xl/workbook.xml"))
            ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            return [x.attrib.get("name", "") for x in root.findall(".//m:sheets/m:sheet", ns)], None
    except Exception as exc:  # malformed and legacy backups still remain traceable
        return [], f"{type(exc).__name__}: {exc}"


def authoritative_markdown(rel: str) -> bool:
    low = rel.lower().replace("\\", "/")
    if "废弃口径/" in low:
        return False
    return low.startswith(("00_总览/", "01_源表/readme.md", "02_ai规则/", "03_沉淀md/")) or low in ("readme.md", "输入文档更新流程.md")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=os.environ.get("VGAME_NUMERICAL_FRAMEWORK_ROOT"))
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    args = parser.parse_args()
    if not args.source:
        raise SystemExit("source missing: pass --source or set VGAME_NUMERICAL_FRAMEWORK_ROOT")
    source = Path(args.source).resolve()
    repo = Path(args.repo).resolve()
    out = repo / "knowledge-base" / "numerical"
    if not source.is_dir():
        raise SystemExit(f"source missing: {source}")

    files = sorted((p for p in source.rglob("*") if p.is_file()), key=lambda p: p.relative_to(source).as_posix().casefold())
    source_rows, workbook_rows, atoms, formulas, parameters = [], [], [], [], []
    disposition_counts: Counter[str] = Counter()
    authoritative_md_files = 0
    source_workbooks = 0

    for path in files:
        rel = path.relative_to(source).as_posix()
        suffix = path.suffix.lower()
        digest = sha256(path)
        disp, reason = disposition(rel, suffix)
        disposition_counts[disp] += 1
        sid = stable_id("NSRC", rel)
        domain = infer_domain(rel)
        source_rows.append({
            "sourceId": sid, "relativePath": rel, "extension": suffix or "NO_EXTENSION", "bytes": path.stat().st_size,
            "sha256": digest, "domain": domain, "disposition": disp, "reason": reason,
            "authorityRole": "EVIDENCE_INPUT", "sourceUri": f"vgame-numeric-source://框架v2/{rel}",
        })

        is_source_workbook = suffix == ".xlsx" and disp == "SOURCE_WORKBOOK_EVIDENCE"
        if is_source_workbook:
            source_workbooks += 1
            sheets, error = workbook_sheets(path)
            workbook_rows.append({
                "workbookId": stable_id("NWB", rel), "sourceId": sid, "relativePath": rel, "sha256": digest,
                "domain": domain, "sheets": [{"sheetId": stable_id("NSHEET", f"{rel}#{name}"), "name": name} for name in sheets],
                "inspectionError": error, "status": "STRUCTURE_REGISTERED" if not error else "STRUCTURE_READ_FAILED_TRACEABLE",
            })

        if suffix == ".md" and authoritative_markdown(rel):
            authoritative_md_files += 1
            raw = path.read_text(encoding="utf-8-sig", errors="replace")
            for title, line, body in markdown_sections(raw, path.stem):
                locator = f"{rel}#L{line}:{title}"
                aid = stable_id("NATOM", locator)
                combined = f"{rel} {title} {body[:3000]}"
                atom_domain = infer_domain(combined)
                statements = numeric_statements(body)
                system_ids = systems_for(combined, atom_domain)
                skill_ids = list(dict.fromkeys(["vgame-knowledge-router", *SKILLS_BY_DOMAIN[atom_domain]]))
                atom = {
                    "atomId": aid, "atomType": "NUMERIC_KNOWLEDGE_SECTION", "domain": atom_domain, "title": title,
                    "statement": clean_summary(body, title), "numericStatements": statements,
                    "sourceId": sid, "sourceLocator": locator, "sourceSha256": digest,
                    "coveredSystems": system_ids, "skillIds": skill_ids, "evidenceRefs": [sid],
                    "configCandidates": config_candidates(combined), "frameworkNodeIds": FRAMEWORK_BY_DOMAIN[atom_domain],
                    "sourceNature": "SOURCE_EXPLICIT", "status": "ACTIVE", "validation": ["SOURCE_HASH_MATCH", "ROUTE_RESOLVES", "NO_LIVE_INFERENCE"],
                }
                atom = apply_latest_ruling_status(atom)
                atom["statement"] = normalize_portable_text(atom["statement"])
                atom["numericStatements"] = [normalize_portable_text(value) for value in atom["numericStatements"]]
                statements = atom["numericStatements"]
                atoms.append(atom)
                for statement in statements:
                    if "=" in statement or re.search(r"公式|计算|倍率|期望|概率|权重", statement):
                        formulas.append({
                            "formulaId": stable_id("NFORM", f"{aid}:{statement}"), "atomId": aid, "domain": atom_domain,
                            "expressionOrRule": statement, "sourceId": sid, "sourceLocator": locator,
                            "status": "SOURCE_EXTRACTED_NEEDS_CONTEXT" if atom["status"] == "ACTIVE" else atom["status"],
                            **({"supersededBy": atom["supersededBy"]} if atom.get("supersededBy") else {}),
                        })
                for fence in re.findall(r"```(?:json|JSON)\s*(.*?)```", body, flags=re.S):
                    try:
                        value = json.loads(fence)
                    except json.JSONDecodeError:
                        continue
                    parameters.append({
                        "parameterSetId": stable_id("NPARAM", f"{aid}:{fence}"), "atomId": aid, "domain": atom_domain,
                        "value": value, "sourceId": sid, "sourceLocator": locator,
                        "status": "MACHINE_READABLE_SOURCE_EXTRACTED" if atom["status"] == "ACTIVE" else atom["status"],
                        **({"supersededBy": atom["supersededBy"]} if atom.get("supersededBy") else {}),
                    })

    # 旧专武/房车口径只保留来源追溯；权威规则由 governance ruling 注入，确保查询没有歧义。
    ruling_atoms = [
        {
            "atomId": "NATOM-RULING-RV-C", "atomType": "HUMAN_RULING", "domain": "growth", "title": "房车随机强化 C",
            "statement": "房车采用随机强化 +30/+60/+100，权重 50/30/20。", "numericStatements": ["+30/+60/+100；权重 50/30/20"],
            "sourceId": "RULING-RV-C", "sourceLocator": "knowledge-base/governance/rulings.json#RULING-RV-C", "sourceSha256": "CANONICAL_GOVERNANCE",
            "coveredSystems": ["SYS-OUT-GR-09"], "skillIds": ["vgame-knowledge-router", "game-numerical-analysis", "vgame-player-progression-simulator"],
            "evidenceRefs": ["RULING-RV-C"], "configCandidates": ["RV* / Motorhome*"], "frameworkNodeIds": ["PFN-06", "PFN-13", "PFN-19"],
            "sourceNature": "HUMAN_DECISION", "status": "ACTIVE", "validation": ["LATEST_RULING_ONLY"],
        },
        {
            "atomId": "NATOM-RULING-EW-B", "atomType": "HUMAN_RULING", "domain": "growth", "title": "专武兼容迁移 B",
            "statement": "专武保留一个大版本的兼容迁移期。", "numericStatements": ["兼容迁移期 = 一个大版本"],
            "sourceId": "RULING-EW-B", "sourceLocator": "knowledge-base/governance/rulings.json#RULING-EW-B", "sourceSha256": "CANONICAL_GOVERNANCE",
            "coveredSystems": ["SYS-OUT-GR-10", "SYS-OUT-GR-05"], "skillIds": ["vgame-knowledge-router", "game-numerical-analysis", "vgame-player-progression-simulator"],
            "evidenceRefs": ["RULING-EW-B"], "configCandidates": ["Weapon* / HeroExclusiveWeapon*"], "frameworkNodeIds": ["PFN-06", "PFN-13", "PFN-19"],
            "sourceNature": "HUMAN_DECISION", "status": "ACTIVE", "validation": ["LATEST_RULING_ONLY"],
        },
    ]
    atoms.extend(ruling_atoms)

    now = datetime.now(timezone.utc).isoformat()
    dump(out / "source-registry.json", {"schema": "vgame-numerical-source-registry/v2", "generatedAt": now, "sourceRoot": "vgame-numeric-source://框架v2/", "count": len(source_rows), "files": source_rows})
    dump(out / "workbook-registry.json", {"schema": "vgame-numerical-workbook-registry/v2", "generatedAt": now, "count": len(workbook_rows), "workbooks": workbook_rows})
    dump(out / "atom-registry.json", {"schema": "vgame-numerical-atom-registry/v2", "generatedAt": now, "count": len(atoms), "atoms": atoms})
    dump(out / "formula-registry.json", {"schema": "vgame-numerical-formula-registry/v2", "generatedAt": now, "count": len(formulas), "formulas": formulas})
    dump(out / "parameter-registry.json", {"schema": "vgame-numerical-parameter-registry/v2", "generatedAt": now, "count": len(parameters), "parameterSets": parameters})

    mappings = {
        "numeric-to-system.json": {"schema": "vgame-numeric-to-system/v2", "mappings": [{"atomId": a["atomId"], "systemIds": a["coveredSystems"]} for a in atoms]},
        "numeric-to-skill.json": {"schema": "vgame-numeric-to-skill/v2", "mappings": [{"atomId": a["atomId"], "skillIds": a["skillIds"]} for a in atoms]},
        "numeric-to-evidence.json": {"schema": "vgame-numeric-to-evidence/v2", "mappings": [{"atomId": a["atomId"], "evidenceRefs": a["evidenceRefs"]} for a in atoms]},
        "numeric-to-config.json": {"schema": "vgame-numeric-to-config/v2", "mappings": [{"atomId": a["atomId"], "configCandidates": a["configCandidates"], "mappingStatus": "CANDIDATE_NOT_LIVE_PROOF"} for a in atoms]},
        "numeric-to-framework-node.json": {"schema": "vgame-numeric-to-framework-node/v2", "mappings": [{"atomId": a["atomId"], "frameworkNodeIds": a["frameworkNodeIds"]} for a in atoms]},
    }
    for name, data in mappings.items():
        dump(out / "mappings" / name, data)

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for atom in atoms:
        by_domain[atom["domain"]].append(atom)
    domain_names = {
        "shared-foundation": "共享底座", "combat": "战斗数值", "growth": "养成数值", "economy": "经济资源",
        "pacing": "节奏与开放", "probability": "概率与随机", "reward-drop": "奖励与掉落",
        "monetization-liveops": "商业化与运营", "validation-delivery": "验算与配置交付",
    }
    for domain, label in domain_names.items():
        rows = sorted(by_domain.get(domain, []), key=lambda x: (x["title"], x["atomId"]))
        lines = [f"# {label}", "", f"本域共登记 {len(rows)} 个原子。正文只给出规范化导航；精确上下文按 `sourceLocator` 回源。", "", "| 原子 | 状态 | 标题 | 规范化陈述 | 系统 | Skill |", "|---|---|---|---|---|---|"]
        for atom in rows:
            statement = atom["statement"].replace("|", "\\|").replace("\n", " ")[:180]
            lines.append(f"| `{atom['atomId']}` | {atom['status']} | {atom['title'].replace('|', '｜')} | {statement} | {'、'.join(atom['coveredSystems'])} | {'、'.join(atom['skillIds'])} |")
        (out / "domains").mkdir(parents=True, exist_ok=True)
        (out / "domains" / f"{domain}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    readme = f"""# 全栈数值知识层

本目录是 `knowledge-base/README.md` 下的数值权威子层，不是第二个正式入口。外部数值框架共纳管 **{len(source_rows)}** 个文件；其中 **{authoritative_md_files}** 个权威 Markdown 文件已按章节形成 **{len(atoms) - 2}** 个来源原子，另注入 2 个人工裁决原子；**{source_workbooks}** 个源工作簿已登记结构。

## 查询顺序

1. 先由 `vgame-knowledge-router` 选择系统和数值域。
2. 从 `atom-registry.json` 加载最小原子及五类映射。
3. 需要完整上下文、源表值或真实配置时，按 `sourceLocator`、`sourceId` 与配置候选回源。
4. `sourceNature` 为 `SOURCE_EXPLICIT` 只证明源文明确；不能据此推断 Production/LIVE。

## 机器入口

- `source-registry.json`：全部源文件及唯一处置。
- `workbook-registry.json`：权威源工作簿/工作表结构。
- `atom-registry.json`：规范化数值知识原子。
- `formula-registry.json`：公式和计算规则候选。
- `parameter-registry.json`：机器可读参数块。
- `mappings/`：数值原子到系统、Skill、证据、配置、项目框架节点。

## 治理边界

- 旧源文件继续是证据，不是本仓库正式正文。
- 备份、报告、最终配置镜像和 staging 只做可追溯登记。
- 房车 C 与专武 B 以 `knowledge-base/governance/rulings.json` 及本层的裁决原子为准。
- 本目录全部是 Git 跟踪源；网页、索引、切片和图谱必须能在没有外部数值盘的环境中重建。
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    summary = {
        "schema": "vgame-numerical-migration-summary/v2", "generatedAt": now, "sourceFiles": len(source_rows),
        "authoritativeMarkdownFiles": authoritative_md_files, "sourceWorkbooks": source_workbooks,
        "atoms": len(atoms), "activeAtoms": sum(1 for atom in atoms if atom["status"] == "ACTIVE"),
        "supersededAtoms": sum(1 for atom in atoms if atom["status"] == "SUPERSEDED_SOURCE_CONTEXT"),
        "historicalAtoms": sum(1 for atom in atoms if atom["status"] == "HISTORICAL_SOURCE_CONTEXT"),
        "formulas": len(formulas), "parameterSets": len(parameters),
        "dispositions": dict(sorted(disposition_counts.items())), "status": "AUTHORED_PENDING_GATES",
    }
    dump(out / "migration-summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
