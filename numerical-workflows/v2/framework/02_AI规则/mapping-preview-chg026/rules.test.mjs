import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {previewPatches} from './rules.mjs';
const base=JSON.parse(fs.readFileSync(new URL('baseline.json',import.meta.url),'utf8'));
test('CHG-026 full matrix and idempotency',()=>{
  const books=structuredClone(base.before);
  const r=previewPatches(books,base.sources);
  assert.equal(r.annotations.length,73);
  assert.equal(r.patches.filter(x=>x.file==='UIlevel.xlsx').length,125);
  assert.equal(r.annotations.find(x=>x.id===4375).text,'Lv.10');
  for(const p of r.patches) books[p.file][p.sheet][p.row][p.col]=p.value;
  assert.deepEqual(previewPatches(books,base.sources).patches,[]);
});
test('Reject occupied new field, missing baseline item and changed box identity',()=>{
  for(const mutate of [
    b=>{b['Items.xlsx'].items[3][20]='OtherField';},
    b=>{const r=b['Items.xlsx'].items.find(r=>r[0]===4403);r[0]=99999;},
    b=>{b['Items.xlsx'].items.find(r=>r[0]===4403)[4]='ItemSubType_SpecialEquip_Box';}
  ]){const b=structuredClone(base.before);mutate(b);assert.throws(()=>previewPatches(b,base.sources));}
});
test('Reject third-floor non-gold or non-10 generation',()=>{
  const sources=structuredClone(base.sources);
  sources['SpecialEquipmentGenerate.xlsx'].SpecialEquipment.find(r=>r[1]===4375)[4]='5,1000';
  assert.throws(()=>previewPatches(base.before,sources));
});
