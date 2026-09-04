import assert from 'node:assert/strict';

export function table(rows, key) {
  const h = rows.findIndex((r, i) => i < 6 && r.some(v => String(v).split('\n').at(-1) === key));
  assert(h >= 0, `Missing ${key}`);
  const heads = rows[h].map(v => v == null ? null : String(v).split('\n').at(-1));
  const records = rows.slice(h + 1).map((r, i) => ({row: i + h + 1,
    data: Object.fromEntries(heads.flatMap((k, c) => k ? [[k, r[c] ?? null]] : []))
  })).filter(x => typeof x.data[key] === 'number' && x.data['##var'] !== '##');
  return {h, heads, records};
}
const pairs = value => String(value).split(';').map(x => x.split(',').map(Number));
const grades = value => [...new Set(pairs(value).filter(([,w]) => w > 0).map(([g]) => g))].sort((a,b) => a-b);
const badge = gs => gs.length === 1 ? `Lv.${gs[0]}` : `Lv.${gs[0]}-${gs.at(-1)}`;

// Pure, idempotent cell patch generation. No historical package regeneration.
export function previewPatches(books, sources) {
  const items = table(books['Items.xlsx'].items, 'Id');
  const ui = table(books['UIlevel.xlsx'].level, 'LevelId');
  const drop = table(sources['Drop_dungeon.xlsx'].Drop, 'DropId');
  const generate = table(sources['SpecialEquipmentGenerate.xlsx'].SpecialEquipment, 'Id');
  const itemById = new Map(items.records.map(x => [x.data.Id, x]));
  const generateById = new Map(generate.records.map(x => [x.data.Id, x.data]));
  const patches = [], annotations = [];
  const write = (file, sheet, row, col, value) => {
    const old = books[file][sheet][row]?.[col] ?? null;
    assert(!(typeof old === 'string' && old.startsWith('=')), 'Formula protected');
    if (old !== value) patches.push({file, sheet, row, col, old, value});
  };
  assert(items.heads.indexOf('SpecialShow') === -1 || items.heads.indexOf('SpecialShow') === 20,
    'SpecialShow moved; re-review schema');
  if (!items.heads.includes('SpecialShow')) {
    assert(books['Items.xlsx'].items.every(r => r.slice(20).every(v => v == null)), 'Column U occupied');
    write('Items.xlsx', 'items', items.h, 20, '特殊显示\nSpecialShow');
  }
  assert.equal(ui.records.length, 150);
  for (let id = 4403; id <= 4445; id++) {
    const item = itemById.get(id); assert(item, `Missing CHG-019 item ${id}`);
    const match = item.data.Name.match(/^(\d+)级/);
    assert(match && !item.data.ItemSubType && !item.data.ParaList, `Unexpected preview identity ${id}`);
    const g = Number(match[1]); assert(g >= 5 && g <= 60 && g % 5 === 0);
    write('Items.xlsx', 'items', item.row, 20, `Lv.${g}`);
    annotations.push({id, kind:'常规', grades:[g], text:`Lv.${g}`});
  }
  for (let layer = 1; layer <= 30; layer++) {
    const entry = ui.records.find(x => x.data.LevelId === 250000 + layer * 10 + 1)?.data;
    assert(entry && entry.FirstRewardDrop === 20000009 + layer, `Missing first-clear root L${layer}`);
    const actual = drop.records.map(x=>x.data).filter(x => x.DropId === entry.FirstRewardDrop &&
      itemById.get(x.DropItem_id)?.data.ItemSubType === 'ItemSubType_SpecialEquip_Box');
    assert.equal(actual.length,1); const reward = actual[0];
    assert(reward.DropType === 'fixed_' && reward.DropItemNumMin === 1 && reward.DropItemNumMax === 1);
    const box = itemById.get(reward.DropItem_id).data;
    const generated = generateById.get(Number(box.ParaList)); assert(generated);
    const gs = grades(generated.GradeList); assert(gs.length && generated.GenerateMin === 1 && generated.GenerateMax === 1);
    if (layer === 3) assert(box.Id === 4375 && badge(gs) === 'Lv.10' && generated.QualityList === 'Orange,1000');
    const id = 4372 + layer, preview = itemById.get(id); assert(preview);
    write('Items.xlsx', 'items', preview.row, 20, badge(gs));
    annotations.push({id, kind:'首通', layer, actualId:box.Id, grades:gs, text:badge(gs)});
    for (let variant=1; variant<=5; variant++) {
      const record = ui.records.find(x => x.data.LevelId === 250000 + layer*10 + variant); assert(record);
      assert(pairs(record.data.FirstReward).some(([i,n]) => i === id && n === 1));
      const r = pairs(record.data.Reward); assert(r.every(([,n])=>n === -1));
      const boxes = r.filter(([i])=>i>=4403 && i<=4445);
      assert.equal(new Set(boxes.map(([i])=>itemById.get(i).data.ItemQuality)).size,boxes.length);
      if (layer>=6) {
        const main = r.filter(([i]) => i>=4355 && i<=4363 || i===4446 || i===4447);
        const sub = r.filter(([i])=>i===4364);
        assert(main.length===1 && sub.length===1 && r.length === boxes.length+2, `Unexpected rewards L${layer}`);
        const value = [...main,...boxes,...sub].map(x=>x.join(',')).join(';');
        write('UIlevel.xlsx','level',record.row,ui.heads.indexOf('Reward'),value);
      } else assert.equal(r.length,boxes.length);
    }
  }
  return {patches, annotations};
}
