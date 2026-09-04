"""Read-only workbook extraction and immutable baseline for CHG-026."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
FRAMEWORK = HERE.parent.parent
OUT = FRAMEWORK / '06_最终配置/映射装备'
FILES = ['Items.xlsx', 'UIlevel.xlsx', '00_配置清单.xlsx']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot(path, data_only=False):
    book = load_workbook(path, read_only=True, data_only=data_only)
    result = {}
    for sheet in book:
        sheet.reset_dimensions()  # Existing artifact exports can have A1-only dimensions.
        result[sheet.title] = [list(row) for row in sheet.values]
    book.close()
    return result


def table(rows, key):
    for index, row in enumerate(rows[:6]):
        heads = [str(v).split('\n')[-1] if v is not None else None for v in row]
        if key in heads:
            records = []
            for r, values in enumerate(rows[index + 1:], index + 1):
                item = {h: values[c] if c < len(values) else None for c, h in enumerate(heads) if h}
                if isinstance(item.get(key), (int, float)) and item.get('##var') != '##':
                    records.append((r, item))
            return index, heads, records
    raise ValueError(f'Missing header {key}')


if __name__ == '__main__':
    target = HERE / 'baseline.json'
    if target.exists():
        raise SystemExit('baseline.json already exists; keep this run immutable and use a new run directory for a new baseline.')
    sys.path.insert(0, str(HERE.parents[4] / 'scripts'))
    from vgame_paths import config_datas
    config = config_datas()
    watched = [config / 'items/Items.xlsx', config / 'level/UIlevel.xlsx',
               config / 'Drop/Drop_dungeon.xlsx', config / 'SpecialEquipment/SpecialEquipmentGenerate.xlsx']
    hashes = {p.name: sha(p) for p in OUT.glob('*.xlsx')}
    before = {name: snapshot(OUT / name) for name in FILES}
    sources = {name: snapshot(OUT / name, True) for name in ['Drop_dungeon.xlsx', 'SpecialEquipmentGenerate.xlsx']}
    assert all(sha(OUT / name) == digest for name, digest in hashes.items()), 'Concurrent candidate change'
    data = {'revision': 'CHG-026', 'createdAt': datetime.now(timezone.utc).isoformat(),
            'out': str(OUT), 'files': FILES, 'before': before, 'sources': sources,
            'candidateHashes': hashes, 'formalHashes': {str(p): sha(p) for p in watched}}
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'files': FILES, 'candidateFiles': len(hashes),
                      'sheets': {f: list(b) for f, b in before.items()}}, ensure_ascii=False))
