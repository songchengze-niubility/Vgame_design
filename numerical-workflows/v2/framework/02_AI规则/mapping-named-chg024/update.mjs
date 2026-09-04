import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
throw new Error('CHG-024 FixEffect写入已撤回；使用mapping-special-chg025/update.mjs，禁止重放旧字段配置。');

const here=path.dirname(fileURLToPath(import.meta.url));
const framework=path.resolve(here,'../..');
const out=path.join(framework,'06_最终配置/映射装备');
const pre=JSON.parse(await fs.readFile(path.join(here,'preflight.json'),'utf8'));
const rules=JSON.parse(await fs.readFile(path.join(here,'rules.json'),'utf8'));
const sha=async p=>createHash('sha256').update(await fs.readFile(p)).digest('hex');
const read=s=>s.getUsedRange().values.map(r=>r.map(v=>v??null));
for(const f of pre.files)assert.equal(await sha(path.join(out,f)),pre.candidateHashes[f],`Concurrent change: ${f}`);
const books={};
for(const f of pre.files)books[f]=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out,f)));
await fs.mkdir(path.join(here,'previews'),{recursive:true});
async function render(f, sheetName, range, tag){
  const blob=await books[f].render({sheetName,range,scale:1.1,format:'png'});
  await fs.writeFile(path.join(here,'previews',`${tag}-${f}-${sheetName}.png`),new Uint8Array(await blob.arrayBuffer()));
}
if(process.argv.includes('--inspect')){
  for(const f of pre.files){
    console.log(f,(await books[f].inspect({kind:'sheet',include:'id,name',maxChars:1500})).ndjson);
    const first=books[f].worksheets.getItemAt(0).name;
    await render(f,first,f==='SpecialEquipment.xlsx'?'B389:F400':f==='SpecialEquipmentEffect.xlsx'?'A1:I8':'B10:E14','before');
  }
  process.exit(0);
}
const eq=books[pre.files[0]].worksheets.getItem('SpecialEquipment');
for(const c of pre.changes){
  const cell=eq.getCell(c.row-1,c.col);
  assert.equal(cell.values[0][0]??null,c.old);
  assert(!cell.formulas[0]?.[0],`Target formula ${c.row}/${c.col}`);
  cell.values=[[c.new]];
}
const effect=books[pre.files[1]].worksheets.getItem('SpecialEquipment');
const ers=read(effect), eh=ers[0], templateIndex=ers.findIndex(r=>r[eh.indexOf('Id')]===rules.effectTemplateId);
assert(templateIndex>=4);
const ids=Object.values(rules.skills).sort((a,b)=>a-b);
ids.forEach((id,i)=>{
  assert(!ers.some(r=>r[1]===id));
  const row=[...ers[templateIndex]];
  row[eh.indexOf('Id')]=id;row[eh.indexOf('SkillList')]=id;
  const dest=effect.getRangeByIndexes(ers.length+i,0,1,eh.length);
  dest.copyFrom(effect.getRangeByIndexes(templateIndex,0,1,eh.length),'all');
  dest.values=[row];
});
const notes={
  [pre.files[0]]:'CHG-024：仅红装FixEffect按名称绑定21种具名技能，共22件（35/55级白色针织劳保手套均30602）。10个红装占位名称按正式Id同步；三组别名已确认；虚空突袭之刃不绑定。RareEffect六档、原SpecialEffect、属性值及非红装备不变。',
  [pre.files[1]]:'CHG-024：追加21条具名技能Effect，Id与SkillId同号30101～30802（保留Skill编号间隔）。ParameterLimit=1、Score=150沿用3101；SkillList仅1个技能。原918条不变，当前939条；只用于红装FixEffect。'
};
for(const f of pre.files.slice(0,2)){
  const n=books[f].worksheets.getItem('中文说明');
  n.getRange('B3').values=[['CHG-024 / 2026-08-27 / 仅06候选，未写Datas']];
  n.getRange('B4').values=[['红装具名技能绑定候选，SpecialEquipment与Effect配套']];
  n.getRange('B7').values=[[f===pre.files[0]?480:939]];
  const old=String(n.getRange('B9').values[0][0]??'');
  n.getRange('B9').values=[[old+'\n'+notes[f]]];
  n.getRange('A9:B9').format.rowHeight=240;
}
const idx=books[pre.files[2]].worksheets.getItemAt(0), irs=read(idx);
for(let r=1;r<irs.length;r++){
  const f=irs[r][1];if(!notes[f])continue;
  for(const col of [3,4,6])assert(!idx.getCell(r,col).formulas[0]?.[0]);
  idx.getCell(r,3).values=[['CHG-024：红装具名技能绑定，06候选']];
  idx.getCell(r,4).values=[[f===pre.files[0]?480:939]];
  idx.getCell(r,6).values=[[String(irs[r][6]??'')+'\n'+notes[f]]];
  idx.getRangeByIndexes(r,0,1,7).format.rowHeight=150;
}
const audit=books[pre.files[2]].worksheets.add('CHG024具名技能');
audit.getRange('A1:H1').merge();audit.getRange('A1').values=[['CHG-024｜红装具名技能绑定（仅06候选）']];
audit.getRange('A3:H3').values=[['装备ID','正式装备名称','等级','部位','设计技能名称','FixEffect / SkillId','绑定字段','设计源行']];
audit.getRange('A4:H25').values=pre.bindings.map(b=>[b.equipmentId,b.name,b.grade,b.part.replace('SEPart_',''),b.skillName,b.skillId,'FixEffect',b.sourceRow]);
audit.getRange('A27:H29').merge();audit.getRange('A27').values=[['名称按正式Id核对；三组别名获用户确认；两件同名手套共用30602。80393虚空突袭之刃无技能设计，暂不绑定。固定绑定不等于技能100%触发。金红六档RareEffect及原SpecialEffect随机池均不改。']];
audit.getRange('A31:H33').merge();audit.getRange('A31').values=[['来源：用户《映射装备.xlsx》“映射装备包装、技能”C99:E133；本机正式SpecialEquipment、Skill。链路：FixEffect → Effect.Id → SkillList → SkillId。仅配置绑定；未写正式Datas、未做运行时验收。']];
audit.showGridLines=false;
audit.getRange('A1:H33').format={font:{name:'Microsoft YaHei',size:10},wrapText:true,rowHeight:26};
for(const [col,w] of [['A',13],['B',25],['C',8],['D',13],['E',25],['F',20],['G',13],['H',11]])audit.getRange(`${col}:${col}`).format.columnWidth=w;
audit.getRange('A4:A25').setNumberFormat('0');audit.getRange('C4:C25').setNumberFormat('0');audit.getRange('F4:F25').setNumberFormat('0');
for(const range of ['A1:H1','A3:H3'])audit.getRange(range).format={fill:'#17365D',font:{bold:true,color:'#FFFFFF'},rowHeight:34};
audit.getRange('A4:H25').format.borders={insideHorizontal:{style:'thin',color:'#E2E8F0'}};
audit.freezePanes.freezeRows(3);
await fs.mkdir(path.join(here,'staged'),{recursive:true});
for(const f of pre.files){
  console.log(f,(await books[f].inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',options:{useRegex:true,maxResults:10},maxChars:1000})).ndjson);
  for(const sheetName of Object.keys(pre.before[f])){
    const range=sheetName==='SpecialEquipment'?(f===pre.files[0]?'J389:M400':'A923:I930'):sheetName==='中文说明'?'A1:B9':sheetName==='CHG023稀有词条'?'A1:G29':sheetName==='CHG019概率展示'?'A28:M31':'B10:E14';
    await render(f,sheetName,range,'after');
  }
  if(f===pre.files[2])await render(f,'CHG024具名技能','A1:H33','after');
  await (await SpreadsheetFile.exportXlsx(books[f])).save(path.join(here,'staged',f));
}
console.log(JSON.stringify({status:'STAGED',files:pre.files,equipmentBindings:22,newEffects:21,nameUpdates:10}));
