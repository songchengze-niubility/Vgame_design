#!/usr/bin/env python3
"""Route a Vgame question to the smallest relevant knowledge pack."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
KB_ROOT = Path(os.environ.get(
    "VGAME_KNOWLEDGE_OUTPUT",
    REPO_ROOT / "output" / "knowledge-framework" / "knowledge-base",
))
MANIFEST_PATH = KB_ROOT / "router-manifest.json"
PROFILE_ORDER = {"quick": 0, "design": 1, "audit": 2}
GROUP_ALIASES = {
    "system-in": ("战斗内", "局内系统"),
    "system-out-gameplay": ("战斗外玩法", "玩法系统", "玩法"),
    "system-out-growth": ("战斗外养成", "养成系统", "养成"),
    "system-out-support": ("周边系统", "外围系统", "周边", "商业化", "社交"),
}
# 目录型查询信号：问"有哪些/清单"，要的是受控目录而不是深挖审计；强制 quick，防止被运行质询词误升级。
CATALOG_SIGNALS = (
    "有哪些", "哪些系统", "哪些玩法", "列出", "列一下", "清单", "目录", "全部系统", "所有系统", "都有什么",
)
NUMERIC_SIGNALS = (
    "数值", "公式", "参数", "概率", "权重", "倍率", "成长曲线", "战力曲线", "成本", "产出", "消耗",
    "收入", "天数", "节奏", "难度线", "定价", "经济", "掉落率", "期望", "模拟", "强化",
)
NUMERIC_DOMAIN_ALIASES = {
    "shared-foundation": ("共享", "底座", "术语", "属性", "定价"),
    "combat": ("战斗", "伤害", "dps", "ttk", "怪物", "boss"),
    "growth": ("养成", "成长", "升级", "升星", "突破", "专武", "房车", "装备", "战力"),
    "economy": ("经济", "资源", "产出", "消耗", "成本", "收入", "货币"),
    "pacing": ("节奏", "开放", "天数", "日程", "难度线", "里程碑"),
    "probability": ("概率", "随机", "权重", "保底", "抽卡"),
    "reward-drop": ("奖励", "掉落", "drop", "首通"),
    "monetization-liveops": ("商业化", "付费", "月卡", "礼包", "通行证", "活动", "赛季"),
    "validation-delivery": ("验算", "核算", "验证", "配置", "落表", "回执"),
}


def normalize(value: Any) -> str:
    text = str(value or "").casefold()
    return re.sub(r"[\s_\-—–·:：/\\,.，。;；!?！？（）()\[\]{}<>《》]+", "", text)


def unique(values: Iterable[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values:
        if value is None or value == "":
            continue
        key = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(text_blob(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(text_blob(item) for item in value)
    return str(value or "")


def relative_to_repo(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def choose_numeric_atoms(manifest: dict[str, Any], query: str, profile: str) -> tuple[list[dict[str, Any]], list[str]]:
    """仅在数值语义明确时加载原子注册，不对普通系统查询扩大知识包。"""
    query_norm = normalize(query)
    numeric_signal_hits = [term for term in NUMERIC_SIGNALS if normalize(term) in query_norm]
    matched_domains = [
        domain for domain, aliases in NUMERIC_DOMAIN_ALIASES.items()
        if any(normalize(alias) in query_norm for alias in aliases)
    ]
    if not numeric_signal_hits:
        return [], []
    numeric_meta = manifest.get("numerical") or {}
    ref = numeric_meta.get("atomIndexRef")
    if not ref:
        return [], ["路由清单未登记数值原子索引，数值知识层为 UNKNOWN。"]
    candidate = (KB_ROOT / ref).resolve()
    try:
        candidate.relative_to(KB_ROOT.resolve())
    except ValueError:
        return [], ["数值原子索引路径越出知识库，已拒绝读取。"]
    if not candidate.exists():
        return [], [f"数值原子索引不存在：{relative_to_repo(candidate)}。"]
    registry = load_json(candidate)
    scored: list[dict[str, Any]] = []
    for atom in registry.get("atoms") or []:
        if atom.get("status") != "ACTIVE":
            continue
        score = 0
        matches: list[str] = []
        if atom.get("domain") in matched_domains:
            score += 30
            matches.append(atom.get("domain"))
        fields = [atom.get("title"), atom.get("statement"), *(atom.get("numericStatements") or []), *(atom.get("coveredSystems") or [])]
        blob = normalize(" ".join(str(item or "") for item in fields))
        title_norm = normalize(atom.get("title"))
        title_core = re.sub(r"[a-z0-9]+", "", title_norm)
        if len(title_core) >= 2 and title_core in query_norm:
            score += 180
            matches.append(atom.get("title"))
        if atom.get("atomType") == "HUMAN_RULING" and any(token in query_norm for token in ("房车", "专武", "迁移", "强化")):
            score += 120
            matches.append("最新人工裁决")
        for term in unique([*numeric_signal_hits, *NUMERIC_SIGNALS]):
            term_norm = normalize(term)
            if term_norm and term_norm in query_norm and term_norm in blob:
                score += 18 + min(len(term_norm), 12)
                matches.append(term)
        # 直接命中标题中的系统词要高于仅命中宽域。
        for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z0-9_]{3,}", query):
            token_norm = normalize(token)
            if token_norm and token_norm in title_norm:
                score += 60
                matches.append(token)
        if score > 0:
            scored.append({**atom, "_score": score, "_matches": unique(matches)})
    scored.sort(key=lambda item: (-item["_score"], item.get("atomId", "")))
    limit = {"quick": 5, "design": 12, "audit": 20}[profile]
    selected = scored[:limit]
    unknowns = []
    if len(scored) > limit:
        unknowns.append(f"数值原子命中 {len(scored)} 个，本次按 {profile} 档只返回前 {limit} 个；请缩小系统或参数范围以继续。")
    if not selected:
        unknowns.append("检测到数值意图，但未命中具体数值原子；不得自行补写参数。")
    return selected, unknowns


# 硬编码的 audit 实质信号：询问运行/LIVE/开放/迁移裁决/入账/空壳/源码实现等需要核验证据的问题，
# 不应只依赖 manifest.intentSignals（那里缺少"能玩/开放/迁移/入账/空壳/源码"这类运行质询词）。
AUDIT_EXTRAS = (
    "能不能玩", "是否已开放", "是否开放", "已开放", "能否玩", "可以玩", "可不可以玩",
    "开放了吗", "能玩吗", "能打吗", "能进吗", "能玩", "能进", "打开了吗", "能开启",
    "迁移", "已迁移", "迁移到", "入账", "到账", "实装", "空壳", "占位", "有没有实装",
    "账本", "货币", "发给", "发了吗", "发放",
    "运行", "上线", "灰度", "Production", "生产环境", "LIVE", "是否生效", "当前状态",
    "证据", "源码", "代码", "配置为", "开不开放", "值不值", "奖励发不发",
    "会不会发", "发不发", "发不", "发不发",
)


def detect_profile(query: str, manifest: dict[str, Any], override: str | None) -> tuple[str, list[str]]:
    if override:
        return override, [f"用户显式指定 {override}"]
    query_norm = normalize(query)
    # 目录型查询优先固定 quick：即使句中出现"正式/当前"等词，也不升级为 audit（防"玩法有哪些"被误判为运行核验）。
    catalog_hits = [signal for signal in CATALOG_SIGNALS if normalize(signal) and normalize(signal) in query_norm]
    if catalog_hits:
        return "quick", [f"目录型查询（命中 {catalog_hits[0]}），使用最小概览档输出受控目录"]
    matched: dict[str, list[str]] = {}
    for profile, signals in (manifest.get("intentSignals") or {}).items():
        matched[profile] = [signal for signal in signals if normalize(signal) and normalize(signal) in query_norm]
    # "在哪里/赋值/胜利条件"等定位类问题需要读正文，至少 design。
    locate_terms = ("在哪里", "在哪", "赋值", "定义在哪", "写在哪个", "胜利条件", "胜负条件", "怎么判定")
    locate_hits = [term for term in locate_terms if normalize(term) in query_norm]
    if locate_hits:
        matched.setdefault("design", []).append(locate_hits[0])
    # 运行/证据质询优先升到 audit，即使 manifest 只标了 design/quick。
    audit_hits = []
    for signal in AUDIT_EXTRAS:
        norm = normalize(signal)
        if norm and norm in query_norm:
            audit_hits.append(signal)
    if audit_hits:
        matched.setdefault("audit", []).extend(audit_hits)
        matched["audit"] = unique(matched["audit"])
    for profile in ("audit", "design", "quick"):
        if matched.get(profile):
            return profile, matched[profile]
    return "quick", ["未命中深层信号，采用最小概览档"]


def matched_group_ids(query_norm: str) -> list[str]:
    """具体分组词优先于「战斗外」宽组扩展。

    「战斗外+养成」同时出现时只取养成分组，不得把玩法/周边一起拉进来；
    只有单独出现「战斗外」这类宽词时才扩展为三个战斗外分组。"""
    specific: list[str] = []
    for group_id, aliases in GROUP_ALIASES.items():
        if any(normalize(alias) in query_norm for alias in aliases):
            specific.append(group_id)
    if specific:
        return unique(specific)
    if "战斗外" in query_norm:
        return ["system-out-gameplay", "system-out-growth", "system-out-support"]
    return []


def code_file_tokens(query: str) -> list[str]:
    """从问题中提取代码/配置文件名 token（如 MysteryMode.cs、FriendSystem.lua、seasonrankreward）。
    用于让"哪一文件的空壳/实现/状态"类问题命中对应系统的证据标签。"""
    tokens: list[str] = []
    for m in re.finditer(r"[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+", query):
        token = normalize(m.group(0))
        if len(token) >= 3:
            tokens.append(token)
        for part in token.split("."):
            if len(part) >= 3:
                tokens.append(part)
    return unique(tokens)


def is_negated_term(query_norm: str, term_norm: str) -> bool:
    """屏蔽明确否定的词组，避免“不是全员死亡，而是断线”反向召回失败契约。"""
    start = query_norm.find(term_norm)
    if start < 0:
        return False
    prefix = query_norm[max(0, start - 12):start]
    negative_at = max((prefix.rfind(marker) for marker in ("不是", "并非", "不属于", "不包含", "无关")), default=-1)
    positive_at = max(prefix.rfind("而是"), prefix.rfind("实际是"))
    return negative_at >= 0 and negative_at > positive_at


def score_system(system: dict[str, Any], query: str, query_norm: str, group_ids: list[str]) -> tuple[int, list[str]]:
    score = 0
    matches: list[str] = []
    if normalize(system.get("id")) and normalize(system["id"]) in query_norm:
        score += 180
        matches.append(system["id"])
    all_keywords = unique([system.get("name"), *(system.get("aliases") or []), *(system.get("keywords") or []), *(system.get("relations") or [])])
    # 代码/配置文件 token 命中：query 提到 MysteryMode.cs / Mysteries，若系统关键词或证据标签含该 token 则高置信命中。
    for tok in code_file_tokens(query):
        for kw in all_keywords:
            if not kw:
                continue
            kw_norm = normalize(kw)
            # token 作为关键词的一部分（MysteryMode.cs 出现在 "MysteryMode.cs（占位空类）" 内）
            if tok in kw_norm and len(kw_norm) >= len(tok):
                score += 70 + min(len(tok), 20)
                matches.append(f"文件:{tok}")
                break
    for alias in unique([system.get("name"), *(system.get("aliases") or [])]):
        alias_norm = normalize(alias)
        if not alias_norm:
            continue
        if is_negated_term(query_norm, alias_norm):
            continue
        if alias_norm == query_norm:
            score += 170
            matches.append(str(alias))
        elif alias_norm in query_norm:
            score += 75 + min(len(alias_norm), 18)
            matches.append(str(alias))
    for keyword in all_keywords:
        keyword_norm = normalize(keyword)
        if len(keyword_norm) >= 2 and keyword_norm in query_norm and not is_negated_term(query_norm, keyword_norm):
            score += 12 + min(len(keyword_norm), 8)
            matches.append(str(keyword))
    if system.get("groupId") in group_ids:
        score += 40
        matches.append(system.get("groupName") or system.get("groupId"))
    summary_norm = normalize(system.get("summary"))
    for token in re.findall(r"[A-Za-z0-9]{2,}", query):
        if token.casefold() in summary_norm:
            score += 6
            matches.append(token)
    return score, unique(matches)


def choose_systems(
    query: str,
    manifest: dict[str, Any],
    profile: str,
    max_systems_override: int | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    query_norm = normalize(query)
    group_ids = matched_group_ids(query_norm)
    scored: list[dict[str, Any]] = []
    for system in manifest.get("systems") or []:
        score, matches = score_system(system, query, query_norm, group_ids)
        if score > 0:
            scored.append({**system, "_score": score, "_matches": matches})
    scored.sort(key=lambda item: (-item["_score"], item.get("id", "")))
    if profile == "quick" and group_ids:
        scored = [item for item in scored if item.get("groupId") in group_ids]
    elif scored:
        relevance_floor = max(20, int(scored[0]["_score"] * 0.15))
        scored = [item for item in scored if item["_score"] >= relevance_floor]

    profile_limits = manifest.get("profiles") or {}
    detail_limit = int((profile_limits.get(profile) or {}).get("maxSystemDetails", 0))
    if profile == "quick":
        selection_limit = 12
    else:
        selection_limit = max(1, detail_limit or 3)
    if max_systems_override is not None:
        selection_limit = max(1, min(selection_limit, max_systems_override))
    selected = scored[:selection_limit]
    unknowns: list[str] = []
    if len(scored) > selection_limit:
        unknowns.append(f"系统摘要命中 {len(scored)} 个，本次只返回前 {selection_limit} 个；需要完整清单时改用更明确的分类问题。")
    if not selected:
        unknowns.append("未命中具体系统；只能使用项目/模块级目录，不得推断具体规则。")
    return selected, unknowns


def query_terms(
    query: str,
    manifest: dict[str, Any],
    systems: list[dict[str, Any]],
    profile_signals: list[str],
) -> list[str]:
    query_norm = normalize(query)
    candidates: list[str] = list(profile_signals)
    for system in systems:
        candidates.extend(system.get("_matches") or [])
    for contract in manifest.get("contracts") or []:
        candidates.extend(contract.get("keywords") or [])
        candidates.append(contract.get("name"))
    candidates.extend(["主线", "扫荡", "体力", "储能", "奖励", "掉落", "星级", "评价", "解锁", "开放", "任务", "失败", "断线", "LIVE"])
    return unique(term for term in candidates if len(normalize(term)) >= 2 and normalize(term) in query_norm and not is_negated_term(query_norm, normalize(term)))


def choose_contracts(
    manifest: dict[str, Any],
    systems: list[dict[str, Any]],
    profile: str,
    terms: list[str],
) -> list[dict[str, Any]]:
    if PROFILE_ORDER[profile] < PROFILE_ORDER["design"]:
        return []
    limit = int(((manifest.get("profiles") or {}).get(profile) or {}).get("maxContracts", 0))
    if limit <= 0:
        return []
    broad_system_terms = {
        normalize(term)
        for system in systems
        for term in [system.get("name"), *(system.get("_matches") or [])]
    }
    contract_terms = [term for term in terms if normalize(term) not in broad_system_terms]
    # 命中系统自己的 contractRefs 优先：这些是本系统真正消费/实现的契约，先于关键词泛召回。
    system_contract_refs = unique(
        ref for system in systems for ref in (system.get("contractRefs") or [])
    )
    # 泛化词不得单独把扫荡/奖励契约拉进来：只有契约语义本身或被系统 contractRefs 引用才入选。
    weak_generic = {normalize(term) for term in ("奖励", "掉落", "体力", "储能", "星级", "评价", "解锁", "开放", "失败", "断线", "LIVE")}
    contract_terms = [term for term in contract_terms if normalize(term) not in weak_generic]

    scored: list[dict[str, Any]] = []
    for contract in manifest.get("contracts") or []:
        score = 0
        matches: list[str] = []
        cid = contract.get("id")
        if cid in system_contract_refs:
            score += 400
            matches.append(f"contractRefs:{cid}")
        blob_norm = normalize(text_blob(contract))
        for term in contract_terms:
            if normalize(term) in blob_norm:
                score += 35
                matches.append(term)
        if score > 0:
            scored.append({**contract, "_score": score, "_matches": unique(matches)})
    scored.sort(key=lambda item: (-item["_score"], item.get("id", "")))
    return scored[:limit]


def detail_path(system: dict[str, Any]) -> Path | None:
    ref = system.get("detailRef")
    if not ref:
        return None
    candidate = (KB_ROOT / ref).resolve()
    try:
        candidate.relative_to(KB_ROOT.resolve())
    except ValueError:
        return None
    return candidate


def evidence_candidates(
    systems: list[dict[str, Any]],
    profile: str,
    manifest: dict[str, Any],
    terms: list[str],
    raw_query: str = "",
) -> tuple[list[dict[str, Any]], int, list[str]]:
    if profile != "audit":
        return [], 0, []
    limit = int(((manifest.get("profiles") or {}).get(profile) or {}).get("maxEvidenceFiles", 0))
    opened = 0
    candidates: dict[str, dict[str, Any]] = {}
    unknowns: list[str] = []
    atom_keys = ("rules", "conditions", "rewards", "exceptions", "ui", "configs", "relationships", "openQuestions")
    broad_system_terms = {
        normalize(term)
        for system in systems
        for term in [system.get("name"), *(system.get("_matches") or [])]
    }
    focused_terms = [term for term in terms if normalize(term) not in broad_system_terms] or terms
    generic_audit_terms = {normalize(term) for term in ("真实", "当前", "核验", "证据", "配置", "字段", "Excel", "代码", "源码")}
    specific_terms = [term for term in focused_terms if normalize(term) not in generic_audit_terms]
    if specific_terms:
        focused_terms = specific_terms
    query_code_tokens = unique(code_file_tokens(raw_query or ""))
    for system in systems:
        path = detail_path(system)
        if system.get("detailLevel") != "full" or path is None or not path.exists():
            if system.get("detailLevel") != "full":
                unknowns.append(f"{system.get('id')} {system.get('name')} 当前只有摘要索引，无法路由其原始证据。")
            continue
        detail = load_json(path)
        opened += 1
        boosted_refs: dict[str, int] = {}
        for key in atom_keys:
            for atom in detail.get(key) or []:
                atom_blob = normalize(text_blob(atom))
                atom_score = sum(30 for term in focused_terms if normalize(term) in atom_blob)
                if atom_score:
                    for ref in atom.get("evidenceRefs") or []:
                        boosted_refs[ref] = max(boosted_refs.get(ref, 0), atom_score)
        for evidence in detail.get("evidence") or []:
            evidence_id = evidence.get("id") or f"{system.get('id')}:{evidence.get('path')}"
            score = boosted_refs.get(evidence.get("id"), 0)
            evidence_blob = normalize(text_blob(evidence))
            matches: list[str] = []
            for term in focused_terms:
                if normalize(term) in evidence_blob:
                    score += 12
                    matches.append(term)
            # 代码/配置文件名 token 直接命中证据（如 MysteryMode.cs）：保证"MMode.cs 是不是空壳"召回其直接证据。
            for tok in query_code_tokens:
                if tok and tok in evidence_blob:
                    score += 45
                    matches.append(f"文件:{tok}")
            if score > 0 and evidence.get("kind") == "source-excel" and specific_terms:
                score += 20
            if score > 0:
                prior = candidates.get(evidence_id)
                item = {
                    **evidence,
                    "systemId": system.get("id"),
                    "systemName": system.get("name"),
                    "_score": score,
                    "_matches": unique(matches),
                }
                if prior is None or item["_score"] > prior["_score"]:
                    candidates[evidence_id] = item
    selected = sorted(candidates.values(), key=lambda item: (-item["_score"], item.get("id", "")))[:limit]
    if opened and not selected:
        unknowns.append("已检查命中系统的证据元数据，但没有足够相关的证据候选；不要随意打开其他证据。")
    return selected, opened, unknowns


def inherit_audit_unknowns(systems: list[dict[str, Any]]) -> list[str]:
    """audit 档：继承命中系统的运行/冲突/缺口未知，不依赖用户是否写出 LIVE/运行 等关键词。

    从命中系统详情读取 statusAxes 与 openQuestions，把 P0_CONFLICT / UNKNOWN_LIVE / GAP /
    缺运行证据 / 缺发布证据 的结论显式写入 unknowns，保证"现在能不能玩/迁移了没/发不发奖励"
    一类问题即使不提 LIVE 也能返回正确边界。"""
    unknowns: list[str] = []
    for system in systems:
        path = detail_path(system)
        if not path or not path.exists():
            continue
        try:
            detail = load_json(path)
        except (OSError, ValueError):
            continue
        sid = system.get("id")
        name = system.get("name") or sid
        for axis in detail.get("statusAxes") or []:
            st = str(axis.get("status") or "")
            val = str(axis.get("value") or "")
            axis_name = str(axis.get("axis") or "")
            if "UNKNOWN_LIVE" in st:
                unknowns.append(f"{sid} {name}·{axis_name}：{st}（{val}）。缺集中发布台账（版本/开关/发布时间/运行消费链），不能确认 LIVE。")
            elif "P0_CONFLICT" in st or "P0_GAP" in st:
                unknowns.append(f"{sid} {name}·{axis_name}：{st}（{val}）为 P0 冲突/缺口，需项目负责人裁决。")
            elif "GAP" in st:
                unknowns.append(f"{sid} {name}·{axis_name}：{st}（{val}）为缺口，尚缺规则/运行证据。")
        for q in detail.get("openQuestions") or []:
            prior = str(q.get("priority") or "")
            if prior in ("P0", "P1"):
                unknowns.append(f"{sid} {name} 待裁决问题 Q{q.get('id')}（{prior}）：{q.get('question')}")
    return unique(unknowns)


def choose_modules(manifest: dict[str, Any], query: str) -> list[dict[str, Any]]:
    """专业模块（M01/M02）直达：问题提到模块 ID、模块名或其章节名时直接路由，不与系统混排。"""
    query_norm = normalize(query)
    picked: list[dict[str, Any]] = []
    for module in manifest.get("specialistModules") or []:
        short_name = str(module.get("name") or "").replace("专业正文", "")
        candidates = unique([module.get("id"), module.get("name"), short_name, *(module.get("aliases") or []),
                             *(module.get("keywords") or [])])
        hit = next((kw for kw in candidates if kw and len(normalize(kw)) >= 3 and normalize(kw) in query_norm), None)
        if hit:
            picked.append({**module, "_match": hit})
    return picked


def clean_module(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "module": item.get("module"),
        "moduleName": item.get("moduleName"),
        "path": item.get("path"),
        "summary": item.get("summary"),
        "status": item.get("status"),
        "detailLevel": item.get("detailLevel"),
        "detailRef": item.get("detailRef"),
        "sourceDoc": item.get("sourceDoc"),
        "sectionIds": item.get("sectionIds") or [],
        "matchedTerm": item.get("_match"),
    }


def l1_boundary_notes(systems: list[dict[str, Any]]) -> list[str]:
    """quick/design 档也输出命中系统的 L1 状态边界（UNKNOWN_LIVE/冲突/候选），不升级读取详情。"""
    notes: list[str] = []
    for system in systems:
        status = str(system.get("status") or "")
        if any(token in status for token in ("UNKNOWN", "冲突", "候选", "封存", "待裁决", "待核", "待统一")):
            notes.append(f"{system.get('id')} {system.get('name')}：状态边界——{status}。这是工作副本/知识层口径，不证明 Production/LIVE，详见该系统正文 statusAxes。")
    return unique(notes)


def clean_system(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "groupId": item.get("groupId"),
        "groupName": item.get("groupName"),
        "path": item.get("path"),
        "summary": item.get("summary"),
        "status": item.get("status"),
        "detailLevel": item.get("detailLevel"),
        "detailRef": item.get("detailRef"),
        "contractRefs": item.get("contractRefs") or [],
        "relatedIds": item.get("relatedIds") or [],
        "score": item.get("_score"),
        "matchedTerms": item.get("_matches") or [],
    }


def clean_contract(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "summary": item.get("summary"),
        "provenance": item.get("provenance"),
        "status": item.get("status"),
        "score": item.get("_score"),
        "matchedTerms": item.get("_matches") or [],
    }


def clean_evidence(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "systemId": item.get("systemId"),
        "kind": item.get("kind"),
        "label": item.get("label"),
        "path": item.get("path"),
        "location": item.get("location"),
        "status": item.get("status"),
        "score": item.get("_score"),
        "matchedTerms": item.get("_matches") or [],
    }


def build_read_plan(
    profile: str,
    systems: list[dict[str, Any]],
    contracts: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    modules: list[dict[str, Any]] | None = None,
    numeric_atoms: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = [{
        "order": 1,
        "layer": "L1",
        "ref": "ROUTER_OUTPUT",
        "reason": "使用本脚本已筛选出的目录摘要；不要再次全文读取 router-manifest.json。",
    }]
    order = 2
    if numeric_atoms:
        plan.append({
            "order": order,
            "layer": "L1" if profile == "quick" else "L2",
            "ref": "ROUTER_OUTPUT.numericAtoms",
            "reason": "使用路由已筛选的最小数值原子；需要完整上下文或精确源表值时再按 sourceLocator 回源。",
        })
        order += 1
    for module in modules or []:
        source_doc = module.get("sourceDoc")
        if source_doc:
            if PROFILE_ORDER[profile] <= PROFILE_ORDER["quick"]:
                plan.append({
                    "order": order,
                    "layer": "L1",
                    "ref": f"ROUTER_OUTPUT.specialistModules[{module.get('id')}]",
                    "reason": f"直接使用路由输出中的专业模块 {module.get('id')} 摘要、状态轴与 sectionIds；quick 档不读取整份 Markdown 或 L2 canonical。",
                })
            else:
                plan.append({
                    "order": order,
                    "layer": "L2",
                    "ref": relative_to_repo(KB_ROOT / source_doc),
                    "reason": f"读取专业模块 {module.get('id')} {module.get('name')} 的正文（结构化 canonical 见 {module.get('detailRef')}）。",
                })
            order += 1
    if PROFILE_ORDER[profile] >= PROFILE_ORDER["design"]:
        for system in systems:
            path = detail_path(system)
            if system.get("detailLevel") == "full" and path and path.exists():
                plan.append({
                    "order": order,
                    "layer": "L2",
                    "ref": relative_to_repo(path),
                    "reason": f"读取 {system.get('id')} {system.get('name')} 的完整系统正文。",
                })
                order += 1
        if contracts:
            plan.append({
                "order": order,
                "layer": "L2",
                "ref": "ROUTER_OUTPUT.contracts",
                "reason": "共享契约摘要已包含在路由输出；无需读取完整注册表。",
            })
            order += 1
    for item in evidence:
        plan.append({
            "order": order,
            "layer": "L3",
            "ref": item.get("path"),
            "location": item.get("location"),
            "reason": f"核验 {item.get('label')}；读取前先确认文件存在且保持只读。",
        })
        order += 1
    return plan


def route(args: argparse.Namespace) -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"router manifest not found: {MANIFEST_PATH}; "
            "run pwsh -File scripts/knowledge-framework/rebuild.ps1 first"
        )
    manifest = load_json(MANIFEST_PATH)
    profile, signals = detect_profile(args.query, manifest, args.profile)
    systems, unknowns = choose_systems(args.query, manifest, profile, args.max_systems)
    terms = query_terms(args.query, manifest, systems, signals)
    contracts = choose_contracts(manifest, systems, profile, terms)
    evidence, opened_details, evidence_unknowns = evidence_candidates(systems, profile, manifest, terms, args.query)
    unknowns.extend(evidence_unknowns)
    query_norm = normalize(args.query)
    if profile == "audit":
        # 继承命中系统的 P0_CONFLICT/UNKNOWN_LIVE/GAP/缺运行/缺发布 到 unknowns，不受关键词限制。
        unknowns.extend(inherit_audit_unknowns(systems))
        evidence_kinds = {normalize(item.get("kind")) for item in evidence}
        asks_runtime_authority = any(normalize(term) in query_norm for term in ("真实", "运行", "读取", "消费方", "生效"))
        has_runtime_evidence = any("sourcecode" in kind or "runtime" in kind or "源码" in kind or "代码" in kind for kind in evidence_kinds)
        if asks_runtime_authority and not has_runtime_evidence:
            unknowns.append("当前只路由到设计/配置证据，尚无运行时代码消费方证据；真实读取字段与运行权威源为 UNKNOWN，应继续进入对应配置/代码专项 Skill 核验。")
        asks_live = any(normalize(term) in query_norm for term in ("LIVE", "上线", "生产", "Production"))
        has_release_evidence = any("release" in kind or "live" in kind or "发布" in kind for kind in evidence_kinds)
        if asks_live and not has_release_evidence:
            unknowns.append("没有版本、开关、发布时间或 Production 运行证据，不能确认 LIVE。")
    for system in systems:
        if PROFILE_ORDER[profile] >= PROFILE_ORDER["design"] and system.get("detailLevel") != "full":
            unknowns.append(f"{system.get('id')} {system.get('name')} 只有摘要索引；具体规则、字段、异常和证据为 UNKNOWN。")
    # quick/design 档也带出 L1 状态边界（UNKNOWN_LIVE/冲突/候选），audit 档由 inherit_audit_unknowns 深读详情。
    if profile != "audit":
        unknowns.extend(l1_boundary_notes(systems))
    modules = choose_modules(manifest, args.query)
    numeric_atoms, numeric_unknowns = choose_numeric_atoms(manifest, args.query, profile)
    unknowns.extend(numeric_unknowns)
    # Fix: 如果命中专业模块但未命中具体系统，将"未命中具体系统"替换为更准确的描述
    if modules and not systems:
        unknowns = [u for u in unknowns if "未命中具体系统" not in u]
        unknowns.append(f"命中专业模块 {[m.get('id') for m in modules]}，未命中系统级规则；可使用模块正文与章节目录，不得推断未引用的系统规则。")
    # Fix: 目录型查询按状态分层——使用受控优先级枚举，禁止模糊字符串包含。
    # UNKNOWN_LIVE 必须先于 LIVE 判定（"UNKNOWN_LIVE" 包含 "LIVE" 子串）。
    catalog_layers: dict[str, list[str]] | None = None
    catalog_hit = any(normalize(sig) in query_norm for sig in CATALOG_SIGNALS)
    if catalog_hit and systems:
        unknown_live: list[str] = []
        confirmed: list[str] = []
        working_copy: list[str] = []
        candidate: list[str] = []
        closed: list[str] = []
        current_framework: list[str] = []
        for sys_item in systems:
            sid = sys_item.get("id") or ""
            sname = sys_item.get("name") or ""
            status_str = str(sys_item.get("status") or "")
            label = f"{sid} {sname}"
            # 优先级从高到低：unknown_live → closed_or_deprecated → candidate_pending → confirmed_live → working_copy_observed → current_framework
            if "UNKNOWN_LIVE" in status_str or "运行UNKNOWN" in status_str:
                unknown_live.append(label)
            elif any(t in status_str for t in ("封存", "关闭", "CloseSys", "DEPRECATED", "NOT_OPEN", "未开放", "废弃")):
                closed.append(label)
            elif any(t in status_str for t in ("候选", "待裁决", "migrates-to", "PENDING", "待确认", "待核", "待统一")):
                candidate.append(label)
            elif any(t in status_str for t in ("LIVE", "已开放", "正式运行", "ConfigReady")):
                # 此处 LIVE 不会误匹配 UNKNOWN_LIVE，因为上面已优先拦截。
                confirmed.append(label)
            elif any(t in status_str for t in ("WORKING_COPY", "工作副本", "部分落地", "落地待核")):
                working_copy.append(label)
            else:
                current_framework.append(label)
        catalog_layers = {
            "current_framework": current_framework,
            "confirmed_live": confirmed,
            "working_copy_observed": working_copy,
            "candidate_pending": candidate,
            "closed_or_deprecated": closed,
            "unknown_live": unknown_live,
        }
    limits = (manifest.get("profiles") or {}).get(profile) or {}
    result = {
        "schema": "vgame-knowledge-route/v1",
        "query": args.query,
        "profile": profile,
        "profileReason": signals,
        "limits": {
            "maxSystemDetails": limits.get("maxSystemDetails", 0),
            "maxContracts": limits.get("maxContracts", 0),
            "maxEvidenceFiles": limits.get("maxEvidenceFiles", 0),
        },
        "matchedTerms": terms,
        "systems": [clean_system(item) for item in systems],
        "specialistModules": [clean_module(item) for item in modules],
        "numericAtoms": [{
            "atomId": item.get("atomId"), "domain": item.get("domain"), "title": item.get("title"),
            "statement": item.get("statement"), "numericStatements": item.get("numericStatements") or [],
            "sourceNature": item.get("sourceNature"), "sourceLocator": item.get("sourceLocator"),
            "coveredSystems": item.get("coveredSystems") or [], "skillIds": item.get("skillIds") or [],
            "configCandidates": item.get("configCandidates") or [], "matchedTerms": item.get("_matches") or [],
        } for item in numeric_atoms],
        "catalogLayers": catalog_layers,
        "contracts": [clean_contract(item) for item in contracts],
        "evidence": [clean_evidence(item) for item in evidence],
        "readPlan": build_read_plan(profile, systems, contracts, evidence, modules, numeric_atoms),
        "unknowns": unique(unknowns),
        "provenance": manifest.get("provenance") or [],
        "safety": [
            "只读取 readPlan；禁止通配符或递归枚举 system-details。",
            "工作副本与配置镜像不证明 Production/LIVE。",
            "summary 系统只能使用路由输出中的摘要、状态和关系。",
            "路由分数与匹配词仅用于检索，不是业务证据。",
        ],
        "diagnostics": {
            "manifest": relative_to_repo(MANIFEST_PATH),
            "manifestVersion": manifest.get("version"),
            "systemDetailsDirectoryEnumerated": False,
            "detailFilesOpenedForEvidenceMetadata": opened_details,
        },
    }
    return result


def markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Vgame 知识路由结果",
        "",
        f"- 问题：{result['query']}",
        f"- 档位：**{result['profile']}**",
        f"- 判定：{'、'.join(result['profileReason'])}",
        f"- 上限：系统正文 {result['limits']['maxSystemDetails']} / 契约 {result['limits']['maxContracts']} / 证据 {result['limits']['maxEvidenceFiles']}",
        "",
        "## 命中系统",
        "",
    ]
    if result["systems"]:
        lines.extend(["| ID | 系统 | 分类 | 详情 | 状态 | 命中 |", "|---|---|---|---|---|---|"])
        for item in result["systems"]:
            lines.append(f"| {item['id']} | {item['name']} | {item['groupName']} | {item['detailLevel']} | {item['status']} | {'、'.join(item['matchedTerms']) or '-'} |")
    else:
        lines.append("- 未命中具体系统。")
    lines.extend(["", "## 数值原子", ""])
    if result.get("numericAtoms"):
        for item in result["numericAtoms"]:
            lines.append(f"- **{item['atomId']} {item['title']}**（{item['domain']} / {item['sourceNature']}）：{item['statement']}；来源 `{item['sourceLocator']}`")
    else:
        lines.append("- 本问题未触发数值原子层。")
    if result.get("catalogLayers"):
        lines.extend(["", "## 目录分层（按运行状态）", ""])
        layer_labels = {
            "current_framework": "当前框架（已归类系统，无独立 LIVE 声明）",
            "confirmed_live": "已确认 LIVE / 正式运行",
            "working_copy_observed": "工作副本已观察（不证明 LIVE）",
            "candidate_pending": "候选 / 待裁决",
            "closed_or_deprecated": "封存 / 未开放 / 废弃",
            "unknown_live": "运行状态 UNKNOWN_LIVE（不能确认 LIVE）",
        }
        for key, label in layer_labels.items():
            items = result["catalogLayers"].get(key) or []
            if items:
                lines.append(f"- **{label}**：{'; '.join(items)}")
            else:
                lines.append(f"- **{label}**：无")
    lines.extend(["", "## 共享契约", ""])
    if result["contracts"]:
        for item in result["contracts"]:
            lines.append(f"- **{item['id']} {item['name']}**（{item['provenance']}）：{item['summary']}")
    else:
        lines.append("- 本档位或本问题无需加载共享契约。")
    lines.extend(["", "## 证据候选", ""])
    if result["evidence"]:
        for item in result["evidence"]:
            lines.append(f"- **{item['id']} {item['label']}**：`{item['path']}`；{item.get('location') or '未标位置'}；{item.get('status') or 'UNKNOWN'}")
    else:
        lines.append("- 本档位未读取原始证据元数据，或没有足够相关的候选。")
    lines.extend(["", "## 阅读计划", ""])
    for item in result["readPlan"]:
        location = f"；{item['location']}" if item.get("location") else ""
        lines.append(f"{item['order']}. [{item['layer']}] `{item['ref']}`{location} — {item['reason']}")
    lines.extend(["", "## 缺口与边界", ""])
    if result["unknowns"]:
        lines.extend(f"- {item}" for item in result["unknowns"])
    else:
        lines.append("- 本次路由未发现额外摘要限制；事实结论仍需按来源性质表达。")
    lines.extend([
        "",
        f"- 诊断：未枚举详情目录 = `{str(not result['diagnostics']['systemDetailsDirectoryEnumerated']).lower()}`；审计元数据读取详情 = {result['diagnostics']['detailFilesOpenedForEvidenceMetadata']} 个。",
    ])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="自然语言 Vgame 项目问题")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--profile", "--depth", dest="profile", choices=("quick", "design", "audit"))
    parser.add_argument("--max-systems", type=int, default=None, help="进一步收紧返回系统数；不能放宽档位上限")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args(argv or sys.argv[1:])
    try:
        result = route(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"route_query.py: {error}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
