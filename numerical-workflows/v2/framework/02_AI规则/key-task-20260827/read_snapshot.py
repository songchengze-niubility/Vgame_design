import json
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
data = {}
for folder in ['任务','签到','主线高难','无限之旅']:
    for p in (ROOT/'06_最终配置'/folder).glob('*.xlsx'):
        wb = load_workbook(p, read_only=True, data_only=False)
        key = f'{folder}/{p.name}'
        data[key] = {s.title:[list(r) for r in s.values] for s in wb}
        print(key, [(s,len(rows),len(rows[3]) if len(rows)>3 else 0) for s,rows in data[key].items()])
        if p.name in ['DailyTask.xlsx','WeeklyTask.xlsx','Task.xlsx','TaskTarget.xlsx','Drop_other.xlsx','DailyActiveReward.xlsx','WeeklyReward.xlsx','DailySign.xlsx','ChapterStarReward.xlsx','__enums__.xlsx']:
            for s,rows in data[key].items():
                if s in ['配置说明','说明']: continue
                print(s,json.dumps(rows[:9],ensure_ascii=False))
        wb.close()
(OUT/'snapshot.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
