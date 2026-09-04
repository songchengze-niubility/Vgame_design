"""Independent semantic and full-cell checks; never writes XLSX."""
import json
import re
import sys
from pathlib import Path
from prepare import HERE, FRAMEWORK, OUT, snapshot, table, sha

base = json.loads((HERE / 'baseline.json').read_text(encoding='utf-8'))
target = OUT if '--final' in sys.argv else HERE / 'outputs'
books = {f: snapshot(target / f) for f in base['files']}
checks = []


def check(name, ok, detail=None):
    checks.append({'name': name, 'pass': bool(ok), 'detail': detail})


def value(rows, r, c):
    return rows[r][c] if r < len(rows) and c < len(rows[r]) else None


def pairs(text):
    return [tuple(map(int, x.split(','))) for x in str(text).split(';')]


def positive_grades(text):
    return sorted({g for g, w in pairs(text) if w > 0})


_, ih, ir = table(books['Items.xlsx']['items'], 'Id')
_, uh, ur = table(books['UIlevel.xlsx']['level'], 'LevelId')
items = {x['Id']: x for _, x in ir}
uis = {x['LevelId']: x for _, x in ur}
before_ui = {x['LevelId']: x for _, x in table(base['before']['UIlevel.xlsx']['level'], 'LevelId')[2]}
drop = [x for _, x in table(base['sources']['Drop_dungeon.xlsx']['Drop'], 'DropId')[2]]
gen = {x['Id']: x for _, x in table(base['sources']['SpecialEquipmentGenerate.xlsx']['SpecialEquipment'], 'Id')[2]}
expected_badges, expected_details = {}, {}
check('323条Items，Id唯一', len(items) == len(ir) == 323)
check('150条关卡，LevelId唯一', len(uis) == len(ur) == 150)
check('U列SpecialShow且无重复字段', ih.index('SpecialShow') == 20 and ih.count('SpecialShow') == 1)

for item_id in range(4403, 4446):
    item = items[item_id]
    grade = int(re.match(r'(\d+)级', item['Name'])[1])
    expected_badges[item_id] = f'Lv.{grade}'
    check(f'常规预览道具身份:{item_id}', not item['ParaList'] and not item['ItemSubType'])
    check(f'常规预览等级:{item_id}', item['SpecialShow'] == f'Lv.{grade}')
    expected_details[item_id] = [item_id, '常规', None, None, str(grade), f'Lv.{grade}']
check('43个常规占位不进入真实Drop', not any(4403 <= x['DropItem_id'] <= 4445 for x in drop if isinstance(x.get('DropItem_id'), int)))

quality_rank = {'Green': 0, 'Blue': 1, 'Purple': 2, 'Orange': 3, 'Red': 4}
for layer in range(1, 31):
    entry = uis[250000 + layer * 10 + 1]
    first = [d for d in drop if d['DropId'] == entry['FirstRewardDrop']]
    actual = [d for d in first if items.get(d['DropItem_id'], {}).get('ItemSubType') == 'ItemSubType_SpecialEquip_Box']
    check(f'首通固定一箱与一匙:L{layer}', len(actual) == 1 and actual[0]['DropType'] == 'fixed_' and
          actual[0]['DropItemNumMin'] == actual[0]['DropItemNumMax'] == 1 and
          any(d['DropItem_id'] == 25 and d['DropItemNumMin'] == d['DropItemNumMax'] == 1 for d in first))
    box = items[actual[0]['DropItem_id']]
    generated = gen[int(box['ParaList'])]
    gs = positive_grades(generated['GradeList'])
    text = f'Lv.{gs[0]}' if len(gs) == 1 else f'Lv.{gs[0]}-{gs[-1]}'
    preview_id = 4372 + layer
    expected_badges[preview_id] = text
    expected_details[preview_id] = [preview_id, '首通', layer, box['Id'], '/'.join(map(str, gs)), text]
    check(f'首通等级源链:L{layer}', items[preview_id]['SpecialShow'] == text and generated['GenerateMin'] == generated['GenerateMax'] == 1)
    if layer == 3:
        check('第三层4375真实蓝箱固定10级金装', box['Id'] == 4375 and box['ItemQuality'] == 'Blue' and gs == [10] and generated['QualityList'] == 'Orange,1000')
    normal_grades = sorted(positive_grades(gen[4201 + (layer - 1) * 5]['GradeList']), reverse=True)
    expected_quality = list(reversed(['Green', 'Blue', 'Purple'] + (['Orange'] if layer >= 10 else []) + (['Red'] if layer >= 20 else [])))
    per_grade, extra = divmod(len(expected_quality), len(normal_grades))
    allocation = [g for index, g in enumerate(normal_grades) for _ in range(per_grade + (index >= len(normal_grades) - extra))]
    for variant in range(1, 6):
        level_id = 250000 + layer * 10 + variant
        row, old = uis[level_id], before_ui[level_id]
        reward, old_reward = pairs(row['Reward']), pairs(old['Reward'])
        first_reward = pairs(row['FirstReward'])
        boxes = [(i, n) for i, n in reward if 4403 <= i <= 4445]
        check(f'常规真实品质和等级分配:{level_id}',
              [items[i]['ItemQuality'] for i, _ in boxes] == expected_quality and
              [int(re.match(r'(\d+)级', items[i]['Name'])[1]) for i, _ in boxes] == allocation)
        if layer >= 6:
            main = [(i, n) for i, n in old_reward if 4355 <= i <= 4363 or i in (4446, 4447)]
            expected = main + [(i, n) for i, n in old_reward if 4403 <= i <= 4445] + [(4364, -1)]
            check(f'主材前置且原箱顺序不变:{level_id}', len(main) == 1 and reward == expected)
        else:
            check(f'前5层无材料且预览不变:{level_id}', reward == old_reward == boxes)
        check(f'首通未改且箱数1:{level_id}', row['FirstReward'] == old['FirstReward'] and (preview_id, 1) in first_reward)
        check(f'首次和重复联合预览引用完整:{level_id}', all(i in items or i == 25 for i, _ in first_reward + reward))
        check(f'数量负一且图标等级可见:{level_id}', all(n == -1 for _, n in reward) and all(items[i]['SpecialShow'] for i, _ in boxes))

check('仅73个目标箱有新SpecialShow', {i for i, d in items.items() if d.get('SpecialShow')} == set(expected_badges))
check('125条Reward变化', sum(uis[i]['Reward'] != before_ui[i]['Reward'] for i in uis) == 125)
changed_business = []
for f, before in base['before'].items():
    expected_sheets = set(before) | ({'CHG026预览角标'} if f == '00_配置清单.xlsx' else set())
    check(f'页签完整:{f}', set(books[f]) == expected_sheets)
    for sn, old_rows in before.items():
        now = books[f][sn]
        allowed = set()
        if sn == 'items':
            allowed = {(3, 20)} | {(r, 20) for r, d in ir if d['Id'] in expected_badges}
        elif sn == 'level':
            allowed = {(r, uh.index('Reward')) for r, d in ur if 250061 <= d['LevelId'] <= 250305}
        elif sn == '中文说明':
            allowed = {(r, 1) for r in [2, 3, 7, 8]}
        elif sn == '配置清单':
            allowed = {(r, c) for r, row in enumerate(old_rows) if len(row) > 1 and row[1] in ['Items.xlsx', 'UIlevel.xlsx'] for c in [3, 6]}
        elif sn == 'CHG019概率展示':
            allowed = {(39, 0)}
        differences, formula_differences = [], []
        for r in range(max(len(now), len(old_rows))):
            for c in range(max(len(now[r]) if r < len(now) else 0, len(old_rows[r]) if r < len(old_rows) else 0)):
                a, b = value(old_rows, r, c), value(now, r, c)
                if a != b:
                    if sn in ['items', 'level']: changed_business.append((f, r, c))
                    if (r, c) not in allowed: differences.append((r+1, c+1, a, b))
                    if isinstance(a, str) and a.startswith('='): formula_differences.append((r+1, c+1))
        check(f'未授权字段保留:{f}/{sn}', not differences, differences[:10])
        check(f'原公式原样保留:{f}/{sn}', not formula_differences, formula_differences)
    cached = snapshot(target / f, True)
    errors = [(sn, r+1, c+1, v) for sn, rows in cached.items() for r, row in enumerate(rows) for c, v in enumerate(row)
              if isinstance(v, str) and v in ['#REF!', '#VALUE!', '#DIV/0!', '#NAME?', '#NUM!', '#N/A', '#SPILL!']]
    check(f'保存后可读且无公式错误:{f}', not errors, errors)
check('业务仅199处变化含新表头', len(changed_business) == 199)
detail = books['00_配置清单.xlsx']['CHG026预览角标']
check('清单73行等级链与实际配置一致', [r[:6] for r in detail[4:77]] ==
      [expected_details[i] for i in list(range(4403, 4446)) + list(range(4373, 4403))])
for f, digest in base['candidateHashes'].items():
    if f not in base['files']:
        check(f'未改候选哈希:{f}', sha(OUT / f) == digest)
for p, digest in base['formalHashes'].items():
    check(f'SVN未改:{p}', sha(p) == digest)
report = {'revision': 'CHG-026', 'target': str(target), 'passed': sum(c['pass'] for c in checks),
          'total': len(checks), 'allPassed': all(c['pass'] for c in checks),
          'fileHashes': {f: sha(target / f) for f in base['files']}, 'checks': checks,
          'scope': '06候选；无SVN导表或运行时/用户验收'}
filename = 'mapping-equip-preview-CHG026-validation.json' if '--final' in sys.argv else 'validation-staged.json'
destination = FRAMEWORK / '05_验算核算' / filename if '--final' in sys.argv else HERE / filename
destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ['passed', 'total', 'allPassed']}, ensure_ascii=False))
for c in checks:
    if not c['pass']: print(json.dumps(c, ensure_ascii=False))
sys.exit(0 if report['allPassed'] else 1)
