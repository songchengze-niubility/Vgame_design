import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
process.on('uncaughtException', e => { console.error(e.message); process.exit(1); });

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const out = path.join(root, '06_最终配置/映射装备');
const previewDir = path.join(here, 'previews');
const source = JSON.parse(await fs.readFile(path.join(here, 'source.json'), 'utf8'));
const files = ['Drop_dungeon.xlsx', 'UIlevel.xlsx', 'Items.xlsx', '00_配置清单.xlsx'];
const targets = new Map([[20000036, 4334], [20000038, 4345], [20000039, 4350]]);
const retired = new Set([22451, 22452, 22453]);
const books = {};
const read = s => s.getUsedRange().values.map(r => r.map(v => v ?? null));
await fs.mkdir(previewDir, {recursive: true});
for (const file of files) books[file] = await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out, file)));
async function render(file, sheet, range, name) {
  const b = await books[file].render({sheetName: sheet, range, scale: 1.2, format: 'png'});
  await fs.writeFile(path.join(previewDir, `${name}.png`), new Uint8Array(await b.arrayBuffer()));
}
if (process.argv.includes('--inspect')) {
  console.log((await books['Drop_dungeon.xlsx'].inspect({kind:'computedStyle',sheetId:'Drop',range:'B65:F74',maxChars:1200})).ndjson);
  await render('Drop_dungeon.xlsx', 'Drop', 'B65:M74', 'before-drop');
  await render('UIlevel.xlsx', 'level', 'R145:R154', 'before-ui');
  await render('Items.xlsx', 'items', 'A295:J297', 'before-items');
  await render('00_配置清单.xlsx', '配置清单', 'A1:E5', 'before-index');
  process.exit(0);
}

// Abort if the observed baseline or formal source changed while this repair was prepared.
for (const [p, expected] of Object.entries(source.formalHashes)) {
  assert.equal(crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex'), expected, p);
}
for (const file of files) {
  assert.equal(crypto.createHash('sha256').update(await fs.readFile(path.join(out,file))).digest('hex'), source.candidateHashes[file], file);
}
const backup = path.join(root, '05_验算核算/映射装备CHG020_候选备份', new Date().toISOString().replaceAll(/[-:]/g,'').slice(0,15));
await fs.mkdir(backup, {recursive:true});
for (const file of files) await fs.copyFile(path.join(out,file), path.join(backup,file));
await fs.copyFile(path.join(out,'SpecialEquipmentGenerate.xlsx'),path.join(backup,'SpecialEquipmentGenerate.xlsx'));
await fs.copyFile(path.join(here,'source.json'),path.join(backup,'source.json'));

const drop = books['Drop_dungeon.xlsx'].worksheets.getItem('Drop');
const dropRows = read(drop).slice(4).filter(r => r[1] !== null);
assert.equal(dropRows.length, 696, 'Expected CHG-019 baseline');
const patches=[];
for (const [id, box] of targets) {
  const rowIndex = dropRows.findIndex(r => r[1] === id && r[4] > 0);
  assert(rowIndex >= 0 && retired.has(dropRows[rowIndex][4]), `legacy parent ${id}`);
  const r=[...dropRows[rowIndex]];
  r[2]=id===20000036?'首通金箱':'首通红箱'; r[4]=0; r[5]='fixed_';
  r[6]=1; r[7]=1; r[9]=box; r[10]=1; r[11]=1; r[12]=10000;
  // Candidate B/E contain literal IDs, not formal-table formula columns.
  assert(drop.getRange(`A${rowIndex+5}:O${rowIndex+5}`).formulas.flat().every(x=>!x));
  for (const c of [2,4,5,6,7,9,10,11,12]) drop.getCell(rowIndex+4,c).values=[[r[c]]];
  patches.push({dropId:id,row:rowIndex+5,item:box,old:dropRows[rowIndex],new:r});
}
const retiredRows=dropRows.map((r,i)=>({r,index:i+5})).filter(x=>retired.has(x.r[1]));
assert.equal(retiredRows.length,6);
assert(retiredRows.every((x,i)=>x.index===695+i), 'Retired pools must be the final six rows');
assert(dropRows.filter(r=>!targets.has(r[1])).every(r=>!retired.has(r[4])), 'Other parent references retired pool');
// No insert/delete operations: clear only retired literal data at the tail, preserve formatting.
drop.getRangeByIndexes(694,0,6,dropRows[0].length).values=Array.from({length:6},()=>Array(dropRows[0].length).fill(null));
const finalDrop=read(drop).slice(4).filter(r=>r[1]!==null);
assert.equal(finalDrop.length,690);
assert(finalDrop.every(r=>!retired.has(r[1])&&!retired.has(r[4])));

const ui=books['UIlevel.xlsx'].worksheets.getItem('level');
const uiRows=read(ui);
let uiCount=0;
for(let i=4;i<uiRows.length;i++) {
  const value=source.previews[String(uiRows[i][1])];
  if(value!==undefined) {ui.getCell(i,17).values=[[value]];uiCount++;}
}
assert.equal(uiCount,15);

const items=books['Items.xlsx'].worksheets.getItem('items');
const itemRows=read(items).slice(4).filter(r=>r[0]!==null);
assert(source.items.every(r=>!itemRows.some(old=>old[0]===r[0])));
// Preserve the existing candidate's category grouping and every existing row position.
// These IDs already exist in Datas; append reference rows, never renumber them.
const newItems=[...itemRows,...source.items];
assert(items.getUsedRange().formulas.flat().every(x=>!x));
const itemWidth = Math.max(...newItems.map(r=>r.length));
items.getRangeByIndexes(4,0,newItems.length,itemWidth).values=newItems.map(r=>Array.from({length:itemWidth},(_,c)=>r[c]??null));
const addedStart=itemRows.length+4;
items.getRangeByIndexes(addedStart,0,3,itemWidth).format={font:{name:'Calibri',size:11},wrapText:true,rowHeight:110};

const notes={
 'Drop_dungeon.xlsx':'CHG-020：仅修复27/29/30层首通固定箱，清除22451～22453旧随机池；690条数据。保留CHG-019常规掉落；其他层首通尚未重基。不得整表覆盖正式表。',
 'UIlevel.xlsx':'CHG-020：仅27/29/30层共15条FirstReward同步正式已有首通占位4399/4401/4402，数量1；保留钥匙与材料。CHG-019的Reward、Des及其他字段不变。',
 'Items.xlsx':'CHG-020：仅补齐正式已存在的首通展示占位4399/4401/4402；不可发放。保留既有293条候选记录，含CHG-019常规展示4403～4447。'
};
const counts={'Drop_dungeon.xlsx':690,'UIlevel.xlsx':150,'Items.xlsx':296};
for(const file of files.slice(0,3)) {
 const s=books[file].worksheets.getItem('中文说明');
 s.getRange('B3').values=[['CHG-019 + CHG-020 / 2026-08-27 / 仅修复06候选']];
 s.getRange('B4').values=[['三个首通包及对应预览已对齐；SVN未修改，其他首通差异保留']];
 s.getRange('B7').values=[[counts[file]]];s.getRange('B9').values=[[notes[file]]];
}
const index=books['00_配置清单.xlsx'].worksheets.getItem('配置清单');
const indexRows=read(index);
for(let i=1;i<indexRows.length;i++) {
 const f=indexRows[i][1];if(!notes[f])continue;
 index.getCell(i,3).values=[['CHG-019 + CHG-020：候选修复']];
 index.getCell(i,4).values=[[counts[f]]];index.getCell(i,6).values=[[notes[f]]];
}
const audit=books['00_配置清单.xlsx'].worksheets.getItem('CHG019概率展示');
audit.getRange('A40').values=[['CHG-019概率口径保持不变：主材品质占比在命中后计算；固定箱池10000，调整后的额外箱池200000，主材池8000000。CHG-020仅对齐第27/29/30层固定首通及展示，清除22451～22453旧池；其他层首通差异仍保留，不能整表覆盖正式配置。']];

await render('Drop_dungeon.xlsx','Drop','B65:M74','after-drop');
await render('UIlevel.xlsx','level','R145:R154','after-ui');
await render('Items.xlsx','items',`A${addedStart+1}:J${addedStart+3}`,'after-items');
await render('00_配置清单.xlsx','配置清单','A1:E5','after-index');
for(const file of files.slice(0,3))await render(file,'中文说明','A1:B9',`after-notes-${file}`);
await render('00_配置清单.xlsx','CHG019概率展示','A28:M38','after-probabilities');
const staging=path.join(here,'outputs');await fs.mkdir(staging,{recursive:true});
for(const file of files) {
 const xlsx=await SpreadsheetFile.exportXlsx(books[file]);await xlsx.save(path.join(staging,file));
}
// Validation reads the staged files before promotion to the user-facing candidates.
const report={revision:'CHG-020',backup,staging,out,files,patches,removedPools:[...retired],uiCount,source};
await fs.writeFile(path.join(here,'repair.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({staged:4,dropRows:690,uiCount,itemsAdded:3,backup}));
