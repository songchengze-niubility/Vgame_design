import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
import {previewPatches, table} from './rules.mjs';

const here=path.dirname(fileURLToPath(import.meta.url)), framework=path.resolve(here,'../..');
const base=JSON.parse(await fs.readFile(path.join(here,'baseline.json'),'utf8'));
const out=base.out, stage=path.join(here,'outputs'), previews=path.join(here,'previews');
const sha=async p=>crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex');
const result=previewPatches(base.before,base.sources), books={};
await fs.mkdir(previews,{recursive:true});
for(const f of base.files) books[f]=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out,f)));
if(process.argv.includes('--check-current')) {
  for(const f of ['Drop_dungeon.xlsx','SpecialEquipmentGenerate.xlsx']) assert.equal(await sha(path.join(out,f)),base.candidateHashes[f],`Source changed: ${f}`);
  const current=Object.fromEntries(Object.entries(books).map(([f,b])=>[f,Object.fromEntries(Object.keys(base.before[f]).map(sn=>[sn,b.worksheets.getItem(sn).getUsedRange().values]))]));
  const check=previewPatches(current,base.sources);
  console.log(JSON.stringify({currentPendingPatches:check.patches.length,annotations:check.annotations.length}));
  process.exit(check.patches.length ? 1 : 0);
}
async function render(file,sheet,range,label){
  const p=await books[file].render({sheetName:sheet,range,scale:1.2,format:'png'});
  await fs.writeFile(path.join(previews,label+'.png'),new Uint8Array(await p.arrayBuffer()));
}
if(process.argv.includes('--inspect')) {
  await render('Items.xlsx','items','O298:T305','before-items');
  await render('UIlevel.xlsx','level','Q28:R32','before-ui');
  await render('00_配置清单.xlsx','配置清单','A1:E5','before-index');
  console.log(JSON.stringify({patches:result.patches.length,annotations:result.annotations.length}));
  process.exit(0);
}
for(const [f,h] of Object.entries(base.candidateHashes)) assert.equal(await sha(path.join(out,f)),h,`Concurrent candidate change: ${f}`);
for(const [p,h] of Object.entries(base.formalHashes)) assert.equal(await sha(p),h,`Formal baseline changed: ${p}`);
const backup=path.join(framework,'05_验算核算/映射装备CHG026_候选备份',new Date().toISOString().replace(/[-:]/g,'').slice(0,15));
await fs.mkdir(backup,{recursive:true});
for(const f of base.files) await fs.copyFile(path.join(out,f),path.join(backup,f));
await fs.copyFile(path.join(here,'baseline.json'),path.join(backup,'baseline.json'));

const metadata=[];
function set(file,sheet,row,col,value){
  const cell=books[file].worksheets.getItem(sheet).getCell(row,col);
  assert(!cell.formulas[0]?.[0],`Formula protected: ${file}/${sheet}/${row}/${col}`);
  metadata.push({file,sheet,row,col,value}); cell.values=[[value]];
}
for(const p of result.patches){
  const c=books[p.file].worksheets.getItem(p.sheet).getCell(p.row,p.col);
  assert.equal(c.values[0]?.[0]??null,p.old); assert(!c.formulas[0]?.[0]); c.values=[[p.value]];
}
const itemSheet=books['Items.xlsx'].worksheets.getItem('items');
itemSheet.getRange('U4').copyFrom(itemSheet.getRange('O4'),'all');
itemSheet.getRange('U4').values=[['特殊显示\nSpecialShow']];
itemSheet.getRange('U4:U327').format={columnWidth:18,wrapText:true,font:{name:'Microsoft YaHei',size:11},horizontalAlignment:'center'};
const notes={
  'Items.xlsx':'CHG-026：U列为SpecialShow，前20列及323条道具不变。43个常规箱显示Lv.等级，30个首通箱显示真实等级范围；4375为实际蓝色箱，固定10级金装。等级替代数量角标，复用该道具的界面也受影响。仅06候选，未写SVN。',
  'UIlevel.xlsx':'CHG-026：第6～30层125条Reward改为随机主材→原品质顺序箱子→随机副材；前5层不变。150条FirstReward、所有数量和Drop引用不变。正式表多Power列，必须按字段映射；仅06候选，未导表或运行验收。'
};
for(const f of Object.keys(notes)) {
  set(f,'中文说明',2,1,'CHG-026 / 2026-08-27 / 保留CHG-019～025 / 仅06候选');
  set(f,'中文说明',3,1,'预览角标及顺序修复；SVN和游戏内未同步');
  set(f,'中文说明',7,1,'只按Id/LevelId与具名字段映射；不可整行粘贴。Items.SpecialShow在候选U列，对应正式同名字段；尾部控制列不导入。');
  set(f,'中文说明',8,1,notes[f]);
  const s=books[f].worksheets.getItem('中文说明');
  s.getRange('B8:B9').format.wrapText=true;s.getRange('A8:B8').format.rowHeight=80;s.getRange('A9:B9').format.rowHeight=120;
}
const index=base.before['00_配置清单.xlsx']['配置清单'];
index.forEach((r,i)=>{if(notes[r[1]]){
  set('00_配置清单.xlsx','配置清单',i,3,'CHG-026：候选，按字段导入');
  set('00_配置清单.xlsx','配置清单',i,6,notes[r[1]]);
}});
set('00_配置清单.xlsx','CHG019概率展示',39,0,'当前预览：CHG-026补73个箱子的SpecialShow；第6层起随机主材→箱子→随机副材。首通箱按真实开箱等级显示，4375为Lv.10；数量角标被等级替代。CHG-019概率及原箱品质/等级分配不变。仅06候选，SVN未修改。');
const reportSheet=books['00_配置清单.xlsx'].worksheets.getOrAdd('CHG026预览角标');
reportSheet.getRange('A1:F1').merge();reportSheet.getRange('A1').values=[['CHG-026｜箱子等级角标与主材前置（仅06候选）']];
reportSheet.getRange('A2:F2').merge();reportSheet.getRange('A2').values=[['首通区仍在常规区前；等级占用数量位。真实奖励、开箱规则及SVN未修改。']];
reportSheet.getRange('A4:F4').values=[['预览ItemId','类型','层','真实首通箱Id','可能装备等级','SpecialShow']];
const rows=result.annotations.map(a=>[a.id,a.kind,a.layer??null,a.actualId??null,a.grades.join('/'),a.text]);
reportSheet.getRangeByIndexes(4,0,rows.length,6).values=rows;
reportSheet.getRange('A1:F77').format={font:{name:'Microsoft YaHei',size:11},rowHeight:24,columnWidth:18};
reportSheet.getRange('A1:F1').format={fill:'#17365D',font:{bold:true,color:'#FFFFFF',size:16},rowHeight:34};
reportSheet.getRange('A2:F2').format={wrapText:true,rowHeight:48};
reportSheet.getRange('A4:F4').format={fill:'#DCE6F1',font:{bold:true},rowHeight:30};
reportSheet.getRange('A5:D77').setNumberFormat('0');reportSheet.freezePanes.freezeRows(4);reportSheet.showGridLines=false;

await render('Items.xlsx','items','O298:U305','after-items');
await render('Items.xlsx','items','U250:U260','after-normal');
await render('Items.xlsx','中文说明','A1:B9','after-items-notes');
await render('UIlevel.xlsx','level','Q28:R32','after-ui');
await render('UIlevel.xlsx','中文说明','A1:B9','after-ui-notes');
for(const [sheet,range,label] of [
  ['配置清单','A1:G5','after-index'],['CHG019概率展示','A35:M40','after-chg019'],
  ['CHG023稀有词条','A1:H8','after-chg023'],['CHG024具名技能','A1:G8','after-chg024'],
  ['CHG025品质准入','A1:E10','after-chg025'],['CHG026预览角标','A1:F10','after-chg026-normal'],
  ['CHG026预览角标','A48:F55','after-chg026-first']]) await render('00_配置清单.xlsx',sheet,range,label);
await fs.mkdir(stage,{recursive:true});
for(const f of base.files){
  const errors=await books[f].inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',options:{useRegex:true,maxResults:20},maxChars:1500});
  await fs.writeFile(path.join(stage,f+'.errors.ndjson'),errors.ndjson);
  const file=await SpreadsheetFile.exportXlsx(books[f]);await file.save(path.join(stage,f));
}
const stageHashes=Object.fromEntries(await Promise.all(base.files.map(async f=>[f,await sha(path.join(stage,f))])));
await fs.writeFile(path.join(here,'repair.json'),JSON.stringify({revision:'CHG-026',backup,stage,out,files:base.files,stageHashes,...result,metadata},null,2));
console.log(JSON.stringify({staged:base.files,patches:result.patches.length,backup}));
