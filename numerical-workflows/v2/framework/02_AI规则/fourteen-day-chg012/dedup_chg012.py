# -*- coding: utf-8 -*-
"""CHG-012 修复：第一次 apply 在 ActiveReward 处报错前已保存三张表，第二次重跑造成重复追加。

去重：删除每张表尾部重复的追加行，使各表恢复为"恰好一份 CHG-012 追加"。
"""
import json
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
CFG = HERE.parents[1] / "06_最终配置" / "任务"

# file -> (sheet, 应删除的尾部行数, 参照表头行数)
DEDUP = {
    "FourteenDayActivity.xlsx": ("FourteenDayActivity", 7),
    "TaskTarget.xlsx": ("TaskTarget", 70),
    "Task.xlsx": ("Task", 70),
    "ActiveReward.xlsx": ("ActiveReward", 7),
    "Drop_TimeLimitedActivity.xlsx": ("Drop", 154),
}

for fname, (sheet, dup_n) in DEDUP.items():
    path = CFG / fname
    wb = load_workbook(path)
    ws = wb[sheet]
    # 找到追加块起点：从末尾向前找 dup_n 行非空行，验证与前一区块重复
    tail = list(ws.iter_rows(values_only=True))
    data_rows = [(i, r) for i, r in enumerate(tail, 1) if any(v is not None for v in r)]
    block2 = data_rows[-dup_n:]
    block1 = data_rows[-2 * dup_n:-dup_n]
    if len(block1) != dup_n or len(block2) != dup_n:
        raise SystemExit(f"{fname}: 尾部结构不符合重复追加特征")
    v1 = [tuple(c if c is not None else "" for c in r) for _, r in block1]
    v2 = [tuple(c if c is not None else "" for c in r) for _, r in block2]
    if v1 != v2:
        raise SystemExit(f"{fname}: 尾部两块内容不一致，不敢删")
    last_row = block2[-1][0]
    first_dup = block2[0][0]
    ws.delete_rows(first_dup, last_row - first_dup + 1)
    wb.save(path)
    print(f"{fname}: 删除重复行 {first_dup}~{last_row} 共{last_row - first_dup + 1}行")
print("done")
