# -*- coding: utf-8 -*-
"""自动化回归测试：验证 vgame-knowledge-router 的 route_query.py 关键路由行为。

样例组 A（最终返工第 7 条，4 个）：大秘境开放 / 专武迁移 / 好友友情点 / MysteryMode 空壳。
样例组 B（2026-08-19 收尾修复回归，8 个）：养成目录 / ResultHash / CoinMode / M01 / M02 /
当前正式玩法目录 / 大秘境是什么 / 收容物是什么。

运行：python test_route.py （在 scripts 目录下），全绿打印 PASS，任一失败置退出码 1。
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MODULE = "route_query"
SPEC = importlib.util.spec_from_file_location(MODULE, os.path.join(HERE, "route_query.py"))
RQ = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RQ)

SAMPLES = {
    "Q1_大秘境开放": {
        "query": "大秘境现在开放了吗？玩家能玩吗？",
        "must_hit": ["SYS-OUT-GP-09"],
        "must_unknown": ["UNKNOWN_LIVE", "缺", "发布台账"],
        "must_contract": ["CONTRACT-REWARD-SETTLEMENT"],
        "forbid_system": [],
    },
    "Q2_专武迁移": {
        "query": "专武迁移到收容物了吗？是不是已经替代了？",
        "must_hit": ["SYS-OUT-GR-05", "SYS-OUT-GR-10"],
        "must_unknown": ["一个大版本"],
        "must_contract": ["CONTRACT-ITEM-LEDGER"],
        "forbid_system": [],
    },
    "Q3_好友友情点": {
        "query": "好友友情点入账了吗？发的币能拿到吗？",
        "must_hit": ["SYS-OUT-SU-12"],
        "must_unknown": ["友情点", "UNKNOWN", "计入", "账本"],
        "must_contract": ["CONTRACT-ITEM-LEDGER"],
        "forbid_contract": ["CONTRACT-SWEEP"],
    },
    "Q4_MysteryMode空壳": {
        "query": "MysteryMode.cs 战斗词缀实装了吗？能打开吗？",
        "must_hit": ["SYS-OUT-GP-09"],
        "must_evidence": ["SYS-OUT-GP-09-EV05"],
        "forbid_system": [],
    },
    # ---- 样例组 B：2026-08-19 收尾修复回归 ----
    "R1_战斗外养成目录": {
        "query": "Vgame 有哪些战斗外养成系统？",
        "must_profile": "quick",
        "must_hit": ["SYS-OUT-GR-01", "SYS-OUT-GR-05", "SYS-OUT-GR-10"],
        "all_systems_in_group": "system-out-growth",
        "min_system_count": 8,
        "forbid_group": ["system-out-gameplay", "system-out-support", "system-in"],
        "must_empty": ["contracts", "evidence"],
        "plan_no_detail": True,
    },
    "R2_ResultHash赋值": {
        "query": "ResultHash 在哪里赋值？",
        "must_profile": "design",
        "must_hit": ["SYS-IN-06", "SYS-IN-08"],
        "plan_must_include": ["SYS-IN-06.json", "SYS-IN-08.json"],
    },
    "R3_CoinMode胜利条件": {
        "query": "CoinMode 的胜利条件是什么？",
        "must_hit": ["SYS-IN-06"],
        "plan_must_include": ["SYS-IN-06.json"],
    },
    "R4_M01直达": {
        "query": "M01 战斗专业正文",
        "must_module": "M01",
        "plan_must_include": ["ROUTER_OUTPUT.specialistModules[M01]"],
    },
    "R5_M02直达": {
        "query": "数值框架 v2",
        "must_module": "M02",
        "plan_must_include": ["ROUTER_OUTPUT.specialistModules[M02]"],
    },
    "R6_当前正式玩法目录": {
        "query": "当前正式玩法有哪些？",
        "must_profile": "quick",
        "must_hit": ["SYS-OUT-GP-01", "SYS-OUT-GP-12"],
        "all_systems_in_group": "system-out-gameplay",
        "min_system_count": 12,
        "must_catalog_layers": True,
    },
    "R7_大秘境是什么": {
        "query": "大秘境是什么？",
        "must_hit": ["SYS-OUT-GP-09"],
        "must_unknown": ["UNKNOWN_LIVE"],
    },
    "R8_收容物是什么": {
        "query": "收容物是什么？",
        "must_hit": ["SYS-OUT-GR-05"],
        "forbid_unknown": ["C-001", "未裁决"],
    },
    # ---- 样例组 C：2026-08-20 路由语义加固回归 ----
    "R9_M01直达quick档不加载L2": {
        "query": "M01 战斗专业正文",
        "must_module": "M01",
        "plan_must_include": ["ROUTER_OUTPUT.specialistModules[M01]"],
        "plan_must_not_include": ["M01-战斗专业正文.md"],
        "plan_no_detail": True,
        "plan_reason_must_include": ["quick", "sectionIds"],
    },
    "R10_M02直达quick档不加载L2": {
        "query": "数值框架 v2",
        "must_module": "M02",
        "plan_must_include": ["ROUTER_OUTPUT.specialistModules[M02]"],
        "plan_must_not_include": ["M02-数值框架v2专业正文.md"],
        "plan_no_detail": True,
        "plan_reason_must_include": ["quick", "sectionIds"],
    },
    "R11_当前正式玩法状态分层": {
        "query": "当前正式玩法有哪些？",
        "must_profile": "quick",
        "must_catalog_layers": True,
        "catalog_layers_must_have_keys": ["current_framework", "confirmed_live", "working_copy_observed", "candidate_pending", "closed_or_deprecated", "unknown_live"],
    },
    "R12_M01直达未命中系统时不矛盾": {
        "query": "M01 战斗专业正文",
        "must_module": "M01",
        "forbid_unknown": ["未命中具体系统"],
        "must_unknown": ["命中专业模块"],
    },
    # ---- 样例组 D：2026-08-20 P0-B 成员级断言（禁止模糊字符串包含判断状态） ----
    "R13_大秘境不得进入confirmed_live": {
        "query": "当前正式玩法有哪些？",
        "must_profile": "quick",
        "must_catalog_layers": True,
        "catalog_member_must_not_be_in": {"SYS-OUT-GP-09": ["confirmed_live"]},
        "catalog_member_must_be_in": {"SYS-OUT-GP-09": ["unknown_live"]},
    },
    "R14_跑商待确认不得进入working_copy": {
        "query": "当前正式玩法有哪些？",
        "must_profile": "quick",
        "must_catalog_layers": True,
        "catalog_member_must_not_be_in": {"SYS-OUT-GP-12": ["working_copy_observed"]},
        "catalog_member_must_be_in": {"SYS-OUT-GP-12": ["candidate_pending"]},
    },
    "R15_收容物候选不得进入confirmed_live": {
        "query": "战斗外养成系统有哪些？",
        "must_profile": "quick",
        "must_catalog_layers": True,
        "catalog_member_must_not_be_in": {"SYS-OUT-GR-05": ["confirmed_live", "working_copy_observed"]},
        "catalog_member_must_be_in": {"SYS-OUT-GR-05": ["candidate_pending"]},
    },
    "R16_全员死亡只召回失败状态契约": {
        "query": "全员死亡触发战斗失败的规则是什么",
        "must_profile": "design",
        "must_hit": ["SYS-IN-02"],
        "must_contract": ["CONTRACT-FAILURE-STATE"],
        "forbid_contract": ["CONTRACT-FAILURE-IDEMPOTENCY"],
    },
    "R17_否定全员死亡不应召回失败状态": {
        "query": "这不是全员死亡导致的，而是断线重连后如何防止重复结算",
        "profile": "design",
        "must_contract": ["CONTRACT-FAILURE-IDEMPOTENCY"],
        "forbid_contract": ["CONTRACT-FAILURE-STATE"],
    },
}


def sys_ids(result):
    return [item.get("id") for item in result.get("systems", [])]


def sys_groups(result):
    return [item.get("groupId") for item in result.get("systems", [])]


def module_ids(result):
    return [item.get("id") for item in result.get("specialistModules", [])]


def evidence_ids(result):
    return [item.get("id") for item in result.get("evidence", [])]


def evidence_blob(result):
    parts = []
    for item in result.get("evidence", []):
        parts.extend(
            [item.get("id") or "", item.get("label") or "", item.get("location") or str(item.get("path") or "")]
        )
    return " ".join(parts)


def contract_ids(result):
    return [item.get("id") for item in result.get("contracts", [])]


def check_sample(name, spec):
    args = RQ.parse_args([spec["query"]])
    result = RQ.route(args)
    errors = []

    profile = result.get("profile", "")
    if profile not in ("quick", "design", "audit"):
        errors.append(f"profile 非法: {profile}")
    if spec.get("must_profile") and profile != spec["must_profile"]:
        errors.append(f"档位应为 {spec['must_profile']}，实际 {profile}")

    ids = sys_ids(result)
    for must in spec.get("must_hit", []):
        if must not in ids:
            errors.append(f"未命中系统 {must} (命中: {ids})")
    for forbid in spec.get("forbid_system", []):
        if forbid in ids:
            errors.append(f"误命中系统 {forbid} (命中: {ids})")

    groups = sys_groups(result)
    for forbid_group in spec.get("forbid_group", []):
        leaked = [sid for sid, gid in zip(ids, groups) if gid == forbid_group]
        if leaked:
            errors.append(f"误混入分组 {forbid_group}: {leaked}")
    if spec.get("all_systems_in_group"):
        bad = [sid for sid, gid in zip(ids, groups) if gid != spec["all_systems_in_group"]]
        if bad:
            errors.append(f"存在非 {spec['all_systems_in_group']} 系统: {bad}")
    if spec.get("min_system_count") and len(ids) < spec["min_system_count"]:
        errors.append(f"目录结果不完整: {len(ids)} < {spec['min_system_count']} (命中: {ids})")

    for field in spec.get("must_empty", []):
        if result.get(field):
            errors.append(f"{field} 应为空（quick 最小读取），实际 {len(result[field])} 项")

    mods = module_ids(result)
    must_modules = spec.get("must_module") or []
    if isinstance(must_modules, str):
        must_modules = [must_modules]
    for must_mod in must_modules:
        if must_mod not in mods:
            errors.append(f"未路由到专业模块 {must_mod} (模块: {mods})")

    plan_text = " ".join(str(p.get("ref") or "") for p in result.get("readPlan", []))
    for token in spec.get("plan_must_include", []):
        if token not in plan_text:
            errors.append(f"readPlan 未包含 {token}: {plan_text[:120]}")
    for token in spec.get("plan_must_not_include", []):
        if token in plan_text:
            errors.append(f"readPlan 不应包含 {token}: {plan_text[:120]}")
    if spec.get("plan_no_detail"):
        deep = [p.get("ref") for p in result.get("readPlan", []) if p.get("layer") != "L1"]
        if deep:
            errors.append(f"quick 档 readPlan 出现非 L1 项: {deep}")

    unknowns = " ".join(result.get("unknowns", []))
    for token in spec.get("must_unknown", []):
        if token not in unknowns:
            errors.append(f"unknowns 缺少「{token}」。unknowns={result.get('unknowns', [])}")

    cids = contract_ids(result)
    for must in spec.get("must_contract", []):
        if must not in cids:
            errors.append(f"契约缺失 {must} (契约: {cids})")
    for forbid in spec.get("forbid_contract", []):
        if forbid in cids:
            errors.append(f"误召回契约 {forbid} (契约: {cids})")

    for ev in spec.get("must_evidence", []):
        if ev not in evidence_ids(result):
            errors.append(f"证据缺失 {ev} (证据: {evidence_ids(result)})")
            continue
        blob = evidence_blob(result)
        if "MysteryMode" in " ".join(spec.get("must_evidence", [])) and "MysteryMode" not in blob:
            errors.append(f"证据 {ev} 内容未引用 MysteryMode 源码")

    plan = result.get("readPlan", [])
    if not plan:
        errors.append("readPlan 为空，无法引导读取核心证据")

    # catalogLayers 检查
    if spec.get("must_catalog_layers"):
        cl = result.get("catalogLayers")
        if not cl:
            errors.append("catalogLayers 应存在但为空/缺失")
        else:
            for key in spec.get("catalog_layers_must_have_keys", []):
                if key not in cl:
                    errors.append(f"catalogLayers 缺少键 {key}: {list(cl.keys())}")
            # 成员级断言：检查指定系统 ID 是否在/不在指定层
            for sys_id, must_layers in spec.get("catalog_member_must_be_in", {}).items():
                found_in = [layer for layer, items in cl.items() if any(sys_id in item for item in items)]
                for must_layer in must_layers:
                    if must_layer not in found_in:
                        errors.append(f"catalogLayers 成员级断言失败：{sys_id} 应在 {must_layer} 层，实际在 {found_in}")
            for sys_id, forbid_layers in spec.get("catalog_member_must_not_be_in", {}).items():
                for forbid_layer in forbid_layers:
                    layer_items = cl.get(forbid_layer, [])
                    if any(sys_id in item for item in layer_items):
                        errors.append(f"catalogLayers 成员级断言失败：{sys_id} 不应在 {forbid_layer} 层，实际存在: {layer_items}")

    # readPlan reason 内容检查
    plan_reasons = " ".join(str(p.get("reason") or "") for p in result.get("readPlan", []))
    for token in spec.get("plan_reason_must_include", []):
        if token not in plan_reasons:
            errors.append(f"readPlan reason 未包含「{token}」: {plan_reasons[:120]}")

    # unknowns 禁止包含
    for token in spec.get("forbid_unknown", []):
        if token in unknowns:
            errors.append(f"unknowns 不应包含「{token}」。unknowns={result.get('unknowns', [])}")

    status = "PASS" if not errors else "FAIL"
    print(f"[{status}] {name}")
    for err in errors:
        print(f"      - {err}")
    print(f"      profile={profile} systems={ids if len(ids) <= 12 else ids[:12] + ['...']} modules={mods} contracts={len(cids)} evidence={len(evidence_ids(result))}")
    return status, errors


def main():
    all_fail = 0
    for name, spec in SAMPLES.items():
        status, errors = check_sample(name, spec)
        if status == "FAIL":
            all_fail += len(errors)
    if all_fail == 0:
        print(f"\n全部 {len(SAMPLES)} 个路由样例 PASS。")
        return 0
    print(f"\n{all_fail} 处路由样例失败。")
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
