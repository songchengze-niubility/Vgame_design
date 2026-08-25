# -*- coding: utf-8 -*-
"""房车养成正式数值文档生成器。

房车整备保持账号全局额外属性口径；出行指南读取沉淀 MD 中的单级节点、
前置关系和逐节点成本，生成可供经济总账继续拆分的完整消耗明细。
"""
import io
import os
import sys
from collections import defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
GROWTH_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(GROWTH_DIR)
sys.path.insert(0, V2_DIR)
from _shared.md_parameter_reader import load_parameter_workbook, parameter_md_path

SHARED_PARAM = parameter_md_path("共享")
GROWTH_PARAM = parameter_md_path("养成")
OUT = os.path.join(GROWTH_DIR, "生成_房车.xlsx")
REPORT = os.path.join(GROWTH_DIR, "_reports", "P房车养成_生成与对照.md")


def clean(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def to_num(value, default=0):
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    text = str(value).strip()
    try:
        num = float(text)
    except ValueError:
        return default
    return int(num) if num.is_integer() else num


def find_row(ws, title):
    for row in range(1, ws.max_row + 1):
        if ws.cell(row, 1).value == title:
            return row
    raise RuntimeError("房车参数缺少区块: %s" % title)


def read_table(ws, title):
    title_row = find_row(ws, title)
    header_row = title_row + 1
    headers = [clean(c.value) for c in ws[header_row]]
    last_col = 0
    for idx, header in enumerate(headers, start=1):
        if header != "":
            last_col = idx
    headers = headers[:last_col]
    rows = []
    row_idx = header_row + 1
    while row_idx <= ws.max_row:
        first = ws.cell(row_idx, 1).value
        if first is None or first == "":
            break
        if isinstance(first, str) and first.endswith("参数") and row_idx > header_row + 1:
            break
        values = [clean(ws.cell(row_idx, col).value) for col in range(1, last_col + 1)]
        rows.append({headers[i]: values[i] if i < len(values) else "" for i in range(len(headers))})
        row_idx += 1
    return rows


def read_key_values(ws, title):
    rows = read_table(ws, title)
    return {row["参数"]: row["值"] for row in rows if row.get("参数")}


def read_shared():
    wb = load_parameter_workbook(SHARED_PARAM, data_only=True, read_only=True)
    sp = wb["标准人"]
    std = {sp.cell(r, 1).value: to_num(sp.cell(r, 2).value) for r in range(2, sp.max_row + 1) if sp.cell(r, 1).value}
    fp = wb["投放系数"]
    rv_coef = None
    for r in range(2, fp.max_row + 1):
        if fp.cell(r, 1).value == "房车整备":
            rv_coef = to_num(fp.cell(r, 2).value)
            break
    wb.close()
    if rv_coef is None:
        raise RuntimeError("共享参数基线 MD 缺少投放系数: 房车整备")
    return std, rv_coef


def read_params():
    wb = load_parameter_workbook(GROWTH_PARAM, data_only=True, read_only=True)
    if "房车参数" not in wb.sheetnames:
        raise RuntimeError("养成参数基线 MD 缺少房车参数页")
    ws = wb["房车参数"]
    general = read_key_values(ws, "房车整备参数")
    cost_bands = read_table(ws, "房车强化消耗分段")
    results = read_table(ws, "房车强化结果")
    careers = read_table(ws, "出行指南职业")
    stages = read_table(ws, "出行指南阶段")
    nodes = read_table(ws, "出行指南节点")
    wb.close()
    return general, cost_bands, results, careers, stages, nodes


def attr_curve(std, coef, level_cap, base_ratio):
    full = {
        "生命": std["生命"] * coef,
        "攻击": std["攻击"] * coef,
        "防御": std["防御"] * coef,
    }
    rows = []
    denom = max(level_cap - 1, 1)
    for lv in range(1, level_cap + 1):
        progress = (lv - 1) / denom
        ratio = base_ratio + (1 - base_ratio) * progress
        rows.append({
            "目标等级": lv,
            "属性进度": progress,
            "生命": full["生命"] * ratio,
            "攻击": full["攻击"] * ratio,
            "防御": full["防御"] * ratio,
        })
    return rows, full


def cost_for_level(cost_bands, lv):
    if lv <= 1:
        return "", ""
    for band in cost_bands:
        lo = int(to_num(band["目标等级下限"]))
        hi = int(to_num(band["目标等级上限"]))
        if lo <= lv <= hi:
            delta = lv - lo
            part = to_num(band["零件基数"]) + to_num(band["零件成长"]) * delta
            gold = to_num(band["金币基数"]) + to_num(band["金币成长"]) * delta
            return part, gold
    return "", ""


def build_node_rows(nodes):
    rows = []
    totals = defaultdict(float)
    for row in nodes:
        max_lv = int(to_num(row["节点等级上限"]))
        inc = to_num(row["属性增量每级"])
        total = to_num(row.get("满级属性增量"), inc * max_lv)
        out = dict(row)
        out["满级属性增量"] = total
        rows.append(out)
        totals[(row["职业"], row["属性"])] += total
    career_rows = []
    for (career, attr), total in sorted(totals.items()):
        career_rows.append({"职业": career, "属性": attr, "满级属性增量": total})
    return rows, career_rows


def build_economy_rows(level_rows, nodes):
    rows = []
    for row in level_rows:
        lv = row["目标等级"]
        if lv <= 1:
            continue
        rows.append({
            "系统": "房车养成",
            "分组": "房车整备",
            "资源/道具": "房车零件",
            "数量": row["房车零件"],
            "进度/条件": "房车目标Lv%s" % lv,
            "口径": "房车整备逐级强化消耗",
            "备注": "",
        })
        rows.append({
            "系统": "房车养成",
            "分组": "房车整备",
            "资源/道具": "金币",
            "数量": row["金币"],
            "进度/条件": "房车目标Lv%s" % lv,
            "口径": "房车整备逐级强化消耗",
            "备注": "",
        })
    for node in nodes:
        max_lv = int(to_num(node["节点等级上限"]))
        if max_lv != 1:
            raise RuntimeError("正式出行指南节点必须全部为单级: %s" % node.get("NodeId"))
        cond = "%s｜%s｜%s｜%s｜节点Lv1" % (
            node["指南"], node["职业"], node["节点名"], node["NodeId"]
        )
        rows.append({
            "系统": "房车养成",
            "分组": "出行指南",
            "资源/道具": node["专属材料"],
            "数量": to_num(node["材料消耗"]),
            "进度/条件": cond,
            "口径": "出行指南单级节点激活消耗",
            "备注": "ItemId=%s" % clean(node.get("专属ItemId")),
        })
        rows.append({
            "系统": "房车养成",
            "分组": "出行指南",
            "资源/道具": "金币",
            "数量": to_num(node["金币消耗"]),
            "进度/条件": cond,
            "口径": "出行指南单级节点激活消耗",
            "备注": "",
        })
    return rows


def validate_branch_plan(careers, stages, nodes):
    expected_stage = {
        "基础": (8, 200, 8500, "1-2-1-1-2-1"),
        "中级": (15, 600, 54000, "1-2-1-1-2-1-2-2-2-1"),
        "高级": (19, 1500, 291000, "1-2-1-1-2-1-2-2-1-2-1-2-1"),
        "精通": (20, 2700, 1011000, "1-2-1-1-2-1-1-2-1-2-2-1-2-1"),
    }
    expected_attrs = {
        "生命%": 0.5,
        "攻击%": 0.5,
        "防御%": 0.5,
        "能量回复等级": 3600,
        "冷却缩减等级": 3900,
        "暴击等级": 2700,
        "暴伤等级": 2200,
        "伤害加成": 0.06,
    }
    if len(careers) != 5 or len(nodes) != 310:
        raise RuntimeError("正式出行指南必须为5职业、310节点")
    stage_rows = {row["阶段"]: row for row in stages}
    if set(stage_rows) != set(expected_stage):
        raise RuntimeError("出行指南阶段集合异常")
    for stage, (count, material, gold, topology) in expected_stage.items():
        row = stage_rows[stage]
        actual = (
            int(to_num(row["节点数"])),
            int(to_num(row["材料预算"])),
            int(to_num(row["金币预算"])),
            str(row["拓扑"]),
        )
        if actual != (count, material, gold, topology):
            raise RuntimeError("阶段参数不一致: %s %s" % (stage, actual))

    by_career = defaultdict(list)
    all_ids = set()
    for node in nodes:
        node_id = str(node["NodeId"])
        if node_id in all_ids:
            raise RuntimeError("重复NodeId: %s" % node_id)
        all_ids.add(node_id)
        if int(to_num(node["节点等级上限"])) != 1:
            raise RuntimeError("节点不是Lv1: %s" % node_id)
        by_career[node["职业"]].append(node)

    if set(by_career) != {row["职业"] for row in careers}:
        raise RuntimeError("职业表与节点职业集合不一致")
    for career, rows in by_career.items():
        if len(rows) != 62:
            raise RuntimeError("%s 节点数不是62" % career)
        material_total = sum(to_num(row["材料消耗"]) for row in rows)
        gold_total = sum(to_num(row["金币消耗"]) for row in rows)
        if material_total != 5000 or gold_total != 1364500:
            raise RuntimeError("%s 成本总量异常: %s/%s" % (career, material_total, gold_total))
        attr_totals = defaultdict(float)
        career_ids = {str(row["NodeId"]) for row in rows}
        edges = defaultdict(list)
        indegree = {node_id: 0 for node_id in career_ids}
        for row in rows:
            attr_totals[row["属性"]] += to_num(row["满级属性增量"])
            current = str(row["NodeId"])
            raw_prev = clean(row.get("前置NodeIds"))
            for previous in [item.strip() for item in str(raw_prev).split(",") if item.strip()]:
                if previous not in career_ids:
                    raise RuntimeError("前置NodeId不存在: %s -> %s" % (previous, current))
                edges[previous].append(current)
                indegree[current] += 1
        queue = [node_id for node_id, degree in indegree.items() if degree == 0]
        seen = 0
        while queue:
            current = queue.pop()
            seen += 1
            for nxt in edges[current]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        if seen != 62:
            raise RuntimeError("%s 节点拓扑存在环" % career)
        for attr, expected in expected_attrs.items():
            if abs(attr_totals[attr] - expected) > 1e-8:
                raise RuntimeError("%s %s总量异常: %s" % (career, attr, attr_totals[attr]))


def append_sheet(wb, title, headers, rows):
    ws = wb.create_sheet(title)
    ws.append(headers)
    fill = PatternFill("solid", fgColor="D9E1F2")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in rows:
        if isinstance(row, dict):
            ws.append([row.get(h, "") for h in headers])
        else:
            ws.append(row)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    widths = {
        "指南": 14, "职业": 12, "阶段": 10, "节点名": 18, "属性": 20,
        "进度/条件": 40, "口径": 24, "备注": 22,
    }
    for idx, header in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = widths.get(header, 14)
    return ws


def fmt(value):
    if isinstance(value, float):
        return round(value, 6)
    return value


def main():
    std, coef = read_shared()
    general, cost_bands, results, careers, stages, nodes = read_params()
    validate_branch_plan(careers, stages, nodes)
    level_cap = int(to_num(general.get("等级上限"), 60))
    base_ratio = float(to_num(general.get("基础占比"), 0.1))

    level_rows, full = attr_curve(std, coef, level_cap, base_ratio)
    for row in level_rows:
        part, gold = cost_for_level(cost_bands, row["目标等级"])
        row["房车零件"] = part
        row["金币"] = gold
    node_rows, career_rows = build_node_rows(nodes)
    flat_basic_attrs = {"生命", "攻击", "防御"}
    percent_basic_attrs = {"生命%", "攻击%", "防御%"}
    flat_basic_node_count = sum(1 for row in node_rows if row.get("属性") in flat_basic_attrs)
    percent_basic_node_count = sum(1 for row in node_rows if row.get("属性") in percent_basic_attrs)
    economy_rows = build_economy_rows(level_rows, node_rows)

    summary_rows = [
        ["标准人生命", std["生命"]],
        ["标准人攻击", std["攻击"]],
        ["标准人防御", std["防御"]],
        ["房车整备投放系数", coef],
        ["房车满级生命", full["生命"]],
        ["房车满级攻击", full["攻击"]],
        ["房车满级防御", full["防御"]],
        ["房车等级上限", level_cap],
        ["出行指南职业数", len(careers)],
        ["出行指南节点数", len(node_rows)],
        ["单职业节点数", 62],
        ["节点等级上限", 1],
    ]
    resource_summary = [
        {"资源/道具": name, "消耗总量": sum(to_num(r["数量"]) for r in economy_rows if r["资源/道具"] == name)}
        for name in sorted({r["资源/道具"] for r in economy_rows})
    ]

    wb = openpyxl.Workbook()
    del wb[wb.sheetnames[0]]
    append_sheet(wb, "口径总览", ["项目", "值"], summary_rows)
    append_sheet(
        wb,
        "房车整备曲线",
        ["目标等级", "属性进度", "生命", "攻击", "防御", "房车零件", "金币"],
        [{k: fmt(v) for k, v in row.items()} for row in level_rows],
    )
    append_sheet(wb, "强化结果", list(results[0].keys()), results)
    append_sheet(wb, "出行指南职业", list(careers[0].keys()), careers)
    append_sheet(wb, "出行指南阶段", list(stages[0].keys()), stages)
    append_sheet(wb, "出行指南节点", list(node_rows[0].keys()), [{k: fmt(v) for k, v in row.items()} for row in node_rows])
    append_sheet(wb, "职业满级属性汇总", ["职业", "属性", "满级属性增量"], career_rows)
    append_sheet(wb, "资源消耗汇总", ["资源/道具", "消耗总量"], resource_summary)
    append_sheet(wb, "经济消耗明细", ["系统", "分组", "资源/道具", "数量", "进度/条件", "口径", "备注"], economy_rows)
    wb.save(OUT)

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    lines = [
        "# 房车养成 · 生成与对照",
        "",
        "> 房车案只取功能拆解，数值口径来自框架v2共享参数与养成参数。",
        "",
        "## 全局升级",
        "",
        "- 房车整备属性分类：账号全局额外属性。",
        "- 投放系数：%s 个标准人。" % coef,
        "- 满级属性：生命 %.0f / 攻击 %.0f / 防御 %.0f。" % (full["生命"], full["攻击"], full["防御"]),
        "- 等级上限：%s；Lv1 基础占比：%s。" % (level_cap, base_ratio),
        "",
        "## 职业天赋",
        "",
        "- 出行指南职业数：%d。" % len(careers),
        "- 出行指南节点数：%d。" % len(node_rows),
        "- 职业节点按角色职业生效，不进入全角色常驻属性预算。",
        "- 每职业节点：62；五职业合计：310；全部节点等级上限为1。",
        "- 职业节点固定基础属性数量：%d（生命/攻击/防御应为 0）。" % flat_basic_node_count,
        "- 职业节点基础百分比属性数量：%d。" % percent_basic_node_count,
        "",
        "## 资源",
        "",
    ]
    for row in resource_summary:
        lines.append("- %s：%s" % (row["资源/道具"], fmt(row["消耗总量"])))
    lines += [
        "",
        "## 产物",
        "",
        "- `养成/生成_房车.xlsx`",
        "- `养成/_reports/P房车养成_生成与对照.md`",
    ]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("房车养成生成完成：整备系数 %.2f，等级 %d，职业 %d，节点 %d" % (coef, level_cap, len(careers), len(node_rows)))
    print("[生成表] %s" % OUT)
    print("[报告] %s" % REPORT)


if __name__ == "__main__":
    main()
