import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
process.on('uncaughtException',e=>{console.error(e.stack?.split('\n').slice(0,5).join('\n')??e.message);process.exit(1);});
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const out=path.join(root,'06_最终配置/映射装备');
const previewDir=path.join(here,'previews');
const source=JSON.parse(await fs.readFile(path.join(here,'source.json'),'utf8'));
const files=['Drop_dungeon.xlsx','UIlevel.xlsx','Items.xlsx','00_配置清单.xlsx'];
const books={};
const read=s=>s.getUsedRange().values.map(r=>r.map(v=>v??null));
const sha=async p=>crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex');
await fs.mkdir(previewDir,{recursive:true});
for(const f of files)books[f]=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out,f)));
async function render(file,sheet,range,name){
 const blob=await books[file].render({sheetName:sheet,range,scale:1.2,format:'png'});
 await fs.writeFile(path.join(previewDir,name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
if(process.argv.includes('--inspect')){
 await render(files[0],'Drop','B5:M14','before-drop');
 await render(files[1],'level','R5:R14','before-ui');
 await render(files[2],'items','A298:J300','before-items');
 await render(files[3],'配置清单','A1:E5','before-index');
 console.log('Rendered four baseline sheets');process.exit(0);
}
for(const [p,h] of Object.entries(source.formalHashes))assert.equal(await sha(p),h,p);
for(const f of files)assert.equal(await sha(path.join(out,f)),source.candidateHashes[f],f);
const backup=path.join(root,'05_验算核算/映射装备CHG021_候选备份',new Date().toISOString().replaceAll(/[-:]/g,'').slice(0,15));
await fs.mkdir(backup,{recursive:true});
for(const f of files)await fs.copyFile(path.join(out,f),path.join(backup,f));
await fs.copyFile(path.join(here,'source.json'),path.join(backup,'source.json'));
const drop=books[files[0]].worksheets.getItem('Drop');
const original=read(drop),oldDrop=original.slice(4).filter(r=>r[1]!==null);
assert.equal(oldDrop.length,690,'Requires CHG-020 baseline');
assert(drop.getUsedRange().formulas.flat().every(x=>!x),'Do not replace formulas');
const regular=oldDrop.filter(r=>r[1]<20000010||r[1]>20000039);
assert.equal(regular.length,620);
const newDrop=[...source.firstRows,...regular],width=Math.max(...original.map(r=>r.length));
assert.equal(newDrop.length,695);
// Preserve full row metadata and the existing worksheet structure; no row insertion/deletion.
drop.getRangeByIndexes(4,0,newDrop.length,width).values=newDrop.map(r=>Array.from({length:width},(_,c)=>r[c]??null));
if(original.length>newDrop.length+4)drop.getRangeByIndexes(newDrop.length+4,0,original.length-newDrop.length-4,width).values=Array.from({length:original.length-newDrop.length-4},()=>Array(width).fill(null));
const ui=books[files[1]].worksheets.getItem('level'),uiRows=read(ui);
let uiCount=0;
for(let i=4;i<uiRows.length;i++){
 const id=uiRows[i][1];if(!id)continue;
 const layer=Math.floor((id-250000)/10),e=source.rules[String(layer)];
 assert(e,`Unknown layer ${id}`);ui.getCell(i,17).values=[[e.firstPreview]];uiCount++;
}
assert.equal(uiCount,150);
const items=books[files[2]].worksheets.getItem('items');
const itemRows=read(items).slice(4).filter(r=>r[0]!==null);
assert.equal(itemRows.length,296);assert.equal(source.newItems.length,27);
assert(source.newItems.every(r=>!itemRows.some(old=>old[0]===r[0])));
const itemWidth=Math.max(...read(items).map(r=>r.length));
for(let n=0;n<source.newItems.length;n++){
 const dest=items.getRangeByIndexes(itemRows.length+4+n,0,1,itemWidth);
 dest.copyFrom(items.getRangeByIndexes(297,0,1,itemWidth),'all');
 dest.values=[Array.from({length:itemWidth},(_,c)=>source.newItems[n][c]??null)];
 dest.format={font:{name:'Calibri',size:11},wrapText:true,rowHeight:110};
}
const notes={
 'Drop_dungeon.xlsx':'CHG-021：30层首通按经济MD固定返还钥匙1、对应品质宝箱1，保留15条材料；无首通随机子池。695条数据；CHG-019常规掉落不变。仅06候选，SVN未修改，不得整表覆盖正式表。',
 'UIlevel.xlsx':'CHG-021：150条FirstReward按层统一：钥匙1、正式已有首通展示占位1、原有材料1；不乘品质变体编号。Reward、Des及其他字段保持CHG-019口径。',
 'Items.xlsx':'CHG-021：补齐正式已有首通展示引用4373～4402（本次新增27条，前次已有3条）；仅展示、不可发放。既有296条不变，共323条，含CHG-019常规展示4403～4447。'
};
const counts={'Drop_dungeon.xlsx':695,'UIlevel.xlsx':150,'Items.xlsx':323};
for(const f of files.slice(0,3)){
 const s=books[f].worksheets.getItem('中文说明');
 s.getRange('B3').values=[['CHG-019 + CHG-020 + CHG-021 / 2026-08-27 / 仅06候选']];
 s.getRange('B4').values=[['30层首通及150条预览按经济MD校正；SVN未修改，运行时发奖需另行验证']];
 s.getRange('B7').values=[[counts[f]]];s.getRange('B9').values=[[notes[f]]];
}
const index=books[files[3]].worksheets.getItem('配置清单'),indexRows=read(index);
for(let i=1;i<indexRows.length;i++){
 const f=indexRows[i][1];if(!notes[f])continue;
 index.getCell(i,3).values=[['CHG-019 + CHG-021：候选修复']];
 index.getCell(i,4).values=[[counts[f]]];index.getCell(i,6).values=[[notes[f]]];
}
books[files[3]].worksheets.getItem('CHG019概率展示').getRange('A40').values=[['CHG-019常规掉落概率口径保持：主材品质占比在命中后计算；固定箱池10000，额外箱池200000，主材池8000000。CHG-021将30层首通统一为钥匙1、文档固定箱1、原有材料1，150条预览不乘品质变体；仅06候选，不能整表覆盖正式配置。']];
await render(files[0],'Drop','B5:M14','after-drop');
await render(files[1],'level','R5:R14','after-ui');
await render(files[2],'items','A301:J303','after-items');
await render(files[3],'配置清单','A1:E5','after-index');
for(const f of files.slice(0,3))await render(f,'中文说明','A1:B9',`after-notes-${f}`);
await render(files[3],'CHG019概率展示','A28:M40','after-probabilities');
const staging=path.join(here,'outputs');await fs.mkdir(staging,{recursive:true});
for(const f of files){const x=await SpreadsheetFile.exportXlsx(books[f]);await x.save(path.join(staging,f));}
await fs.writeFile(path.join(here,'repair.json'),JSON.stringify({revision:'CHG-021',backup,staging,out,files,source},null,2));
console.log(JSON.stringify({staged:4,dropRows:695,uiCount,itemCount:323,backup}));
