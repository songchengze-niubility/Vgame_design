import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url)),framework=path.resolve(here,'../..');
const out=path.join(framework,'06_最终配置/映射装备');
const pre=JSON.parse(await fs.readFile(path.join(here,'preflight.json'),'utf8'));
const sha=async p=>createHash('sha256').update(await fs.readFile(p)).digest('hex');
const books={};
for(const f of pre.files){assert.equal(await sha(path.join(out,f)),pre.candidateHashes[f]);books[f]=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out,f)));}
await fs.mkdir(path.join(here,'previews'),{recursive:true});
async function render(f,sheetName,range,tag){
 const b=await books[f].render({sheetName,range,scale:1.05,format:'png'});
 await fs.writeFile(path.join(here,'previews',`${tag}-${f}-${sheetName}.png`),new Uint8Array(await b.arrayBuffer()));
}
if(process.argv.includes('--inspect')){
 for(const f of pre.files){
  const sn=books[f].worksheets.getItemAt(0).name;
  console.log(f,(await books[f].inspect({kind:'sheet',include:'name',maxChars:900})).ndjson);
  await render(f,sn,f==='SpecialEquipment.xlsx'?'I389:M400':f==='SpecialEquipmentEffectDrop.xlsx'?'A258:C263':f==='SpecialEquipmentEffect.xlsx'?'A923:I928':'B10:E14','before');
 }
 process.exit(0);
}
const eq=books['SpecialEquipment.xlsx'].worksheets.getItem('SpecialEquipment');
for(const c of pre.changes){const cell=eq.getCell(c.row-1,c.col);assert.equal(cell.values[0][0]??null,c.old);assert(!cell.formulas[0]?.[0]);cell.values=[[c.new]];}
const pool=books['SpecialEquipmentEffectDrop.xlsx'].worksheets.getItem('SpecialEquipment');
const oldPools=pre.before['SpecialEquipmentEffectDrop.xlsx']['SpecialEquipment'];
const ids=Object.values(pre.skills).sort((a,b)=>a-b);
ids.forEach((id,i)=>{
 const dest=pool.getRangeByIndexes(oldPools.length+i,0,1,3);
 dest.copyFrom(pool.getRangeByIndexes(4,0,1,3),'all');dest.values=[[null,id,`${id},100`]];
});
const counts={'SpecialEquipment.xlsx':480,'SpecialEquipmentEffectDrop.xlsx':280,'SpecialEquipmentEffect.xlsx':939};
const notes={
 'SpecialEquipment.xlsx':'CHG-025现行：绿/蓝/紫RareEffect为空；金/红RareEffect保持6001～6006六档。非红SpecialEffect为空，红装仅22件按名称引用21个单技能池，其他红装为空。撤回CHG-024新增FixEffect，目前FixEffect全空。三组别名与双手套映射不变。普通属性、刷新数量和掉落不改。',
 'SpecialEquipmentEffectDrop.xlsx':'CHG-025现行：共280池。原259池内容不改；新增21个具名单技能池，PoolId=EffectId=SkillId（30101～30802按既有技能编号保留间隔），EffectList为同号Effect,100。仅由红装SpecialEffect引用；不是把SkillId直接当池使用。',
 'SpecialEquipmentEffect.xlsx':'CHG-025现行：业务939条全部保留。21条具名Effect的Id与SkillList同号，ParameterLimit=1、Score=150。正确链为SpecialEquipment.SpecialEffect→EffectDrop.Id→EffectList→Effect.Id→SkillList→SkillId；不使用FixEffect。72条稀有增伤与600条普通副属性定义不改。'
};
for(const f of pre.files.slice(0,3)){
 const n=books[f].worksheets.getItem('中文说明');
 n.getRange('B3').values=[['CHG-025 / 2026-08-27 / 仅06候选，未写Datas']];
 n.getRange('B4').values=[['按品质隔离RareEffect / SpecialEffect，纠正具名技能池引用']];
 n.getRange('B7').values=[[counts[f]]];
 n.getRange('B9').values=[[notes[f]]];
 n.getRange('A9:B9').format.rowHeight=100;
}
const wb=books['00_配置清单.xlsx'],index=wb.worksheets.getItemAt(0),irs=index.getUsedRange().values;
for(let r=1;r<irs.length;r++){
 const f=irs[r][1];if(!notes[f])continue;
 for(const c of [3,4,6])assert(!index.getCell(r,c).formulas[0]?.[0]);
 index.getCell(r,3).values=[['CHG-025：品质准入与具名SpecialEffect纠正']];index.getCell(r,4).values=[[counts[f]]];index.getCell(r,6).values=[[notes[f]]];
 index.getRangeByIndexes(r,0,1,7).format.rowHeight=110;
}
const named=wb.worksheets.getItem('CHG024具名技能');
named.getRange('A1').values=[['具名技能映射｜CHG-025纠正：仅红装SpecialEffect（取代原FixEffect）']];
named.getRange('F3').values=[['SpecialEffect池ID']];
named.getRange('G4:G25').values=pre.bindings.map(()=>['SpecialEffect']);
named.getRange('A27').values=[['当前：三组别名及两件同名手套对应不变；80393虚空无设计不绑定。具名技能使用SpecialEffect单技能池，FixEffect错误绑定已撤回。绿蓝紫RareEffect为空，非红SpecialEffect为空；金红六档增伤保留。']];
named.getRange('A31').values=[['链路：SpecialEffect → EffectDrop.Id → EffectList → Effect.Id → SkillList → SkillId。PoolId、EffectId、SkillId三者同号但均有独立配置定义。刷新数量维持原配置；未写Datas，未做实机验证。']];
named.getRange('G:G').format.columnWidth=16;
const rare=wb.worksheets.getItem('CHG023稀有词条');
rare.getRange('A27').values=[['CHG-025当前品质规则：RareEffect仅金/红，绿蓝紫为空。六档池每池12条、权重100；具名技能另走仅红装SpecialEffect单技能池，不使用FixEffect。稀有/特殊刷新数量不改；未做实机验证。']];
const a=wb.worksheets.add('CHG025品质准入');
a.getRange('A1:E1').merge();a.getRange('A1').values=[['CHG-025｜品质 × 词条字段（纠正后）']];
a.getRange('A3:E3').values=[['品质','装备数','有RareEffect','有SpecialEffect','有FixEffect']];
a.getRange('A4:E8').values=[['绿',96,0,0,0],['蓝',96,0,0,0],['紫',96,0,0,0],['金',96,96,0,0],['红',96,96,22,0]];
a.getRange('A10:E13').merge();a.getRange('A10').values=[['红装SpecialEffect：22件装备引用21个同名具名技能池；每池仅1条同号Effect、权重100。其余74件红装SpecialEffect为空。金红RareEffect仍为6001～6006六档。']];
a.getRange('A15:E18').merge();a.getRange('A15').values=[['撤回上轮误配：清空288条低品质RareEffect；清空384条非红及74条无对应设计红装SpecialEffect；22件红装改用具名池；清空22条误写FixEffect。装备名、主副属性、刷新数量、掉落与正式Datas不改。']];
a.showGridLines=false;a.getRange('A1:E18').format={font:{name:'Microsoft YaHei',size:10},wrapText:true,rowHeight:27};a.getRange('A:E').format.columnWidth=22;
for(const range of ['A1:E1','A3:E3'])a.getRange(range).format={fill:'#17365D',font:{bold:true,color:'#FFFFFF'},rowHeight:32};
a.getRange('B4:E8').setNumberFormat('0');
await fs.mkdir(path.join(here,'staged'),{recursive:true});
for(const f of pre.files){
 console.log(f,(await books[f].inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',options:{useRegex:true,maxResults:10},maxChars:900})).ndjson);
 for(const sn of Object.keys(pre.before[f])){
  const range=sn==='SpecialEquipment'?(f==='SpecialEquipment.xlsx'?'I389:M400':f==='SpecialEquipmentEffectDrop.xlsx'?'A264:C271':'A923:I928'):sn==='中文说明'?'A1:B9':sn==='CHG019概率展示'?'A28:M31':sn==='CHG023稀有词条'?'A1:G29':sn==='CHG024具名技能'?'A1:H33':'B10:E14';
  await render(f,sn,range,'after');
 }
 if(f==='00_配置清单.xlsx')await render(f,'CHG025品质准入','A1:E18','after');
 await(await SpreadsheetFile.exportXlsx(books[f])).save(path.join(here,'staged',f));
}
console.log('CHG-025 STAGED: 4 workbooks; Rare cleared 288, Special corrected 480, Fix cleared 22; new single-skill pools 21.');
