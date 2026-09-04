import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
const framework = path.resolve(here, '../..');
const out = path.join(framework, '06_最终配置/映射装备');
const rules = JSON.parse(await fs.readFile(path.join(here, 'rules.json'), 'utf8'));
const pre = JSON.parse(await fs.readFile(path.join(here, 'preflight.json'), 'utf8'));
const files = ['SpecialEquipment.xlsx', 'SpecialEquipmentEffect.xlsx', 'SpecialEquipmentEffectDrop.xlsx', '00_配置清单.xlsx'];
const books = {};
for (const f of files) books[f] = await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out, f)));
const read = s => s.getUsedRange().values.map(r => r.map(v => v ?? null));
await fs.mkdir(path.join(here, 'previews'), {recursive:true});
async function render(f, index, range, tag) {
  const b = books[f];
  const blob = await b.render({sheetName:b.worksheets.getItemAt(index).name, range, scale:1.2, format:'png'});
  await fs.writeFile(path.join(here, 'previews', `${tag}-${f}-${index}.png`), new Uint8Array(await blob.arrayBuffer()));
}
if (process.argv.includes('--inspect')) {
  for (const f of files) {
    console.log(f, (await books[f].inspect({kind:'sheet', include:'id,name', maxChars:1200})).ndjson);
    await render(f, 0, f === 'SpecialEquipment.xlsx' ? 'D41:M45' : f === '00_配置清单.xlsx' ? 'B10:E14' : 'A1:I8', 'before');
  }
  process.exit(0);
}
const sha = async p => createHash('sha256').update(await fs.readFile(p)).digest('hex');
for (const f of files) assert.equal(await sha(path.join(out,f)), pre.candidateHashes[f], `Concurrent edit: ${f}`);
const backup = path.join(framework,'05_验算核算/映射装备CHG023_候选备份',new Date().toISOString().replaceAll(/[-:]/g,'').slice(0,15));
await fs.mkdir(backup,{recursive:true});
for (const f of files) await fs.copyFile(path.join(out,f),path.join(backup,f));

const equipment = books[files[0]].worksheets.getItemAt(0);
const erows = read(equipment), eh = erows[0];
let changed = 0;
for(let i=4;i<erows.length;i++) {
  const row=erows[i], quality=row[eh.indexOf('Quality')], grade=row[eh.indexOf('Grade')];
  if (!['Orange','Red'].includes(quality)) continue;
  const tier=rules.tiers.find(t=>t.quality===quality&&t.min<=grade&&grade<=t.max);
  assert(tier,`No tier: ${quality}/${grade}`);
  equipment.getCell(i,eh.indexOf('RareEffect')).values=[[tier.poolId]];
  changed++;
}
assert.equal(changed,192);
const effects=books[files[1]].worksheets.getItemAt(0), effectRows=read(effects), effectHead=effectRows[0];
const template=effectRows.find(r=>r[effectHead.indexOf('Id')]===rules.effectTemplateId);
assert(template);
const effectIds=rules.categories.flatMap(c=>rules.tiers.map(t=>c.base+t.suffix)).sort((a,b)=>a-b);
for(let i=0;i<effectIds.length;i++) {
  const row=[...template];
  row[effectHead.indexOf('Id')]=effectIds[i];
  row[effectHead.indexOf('SkillList')]=effectIds[i];
  const dest=effects.getRangeByIndexes(effectRows.length+i,0,1,effectHead.length);
  dest.copyFrom(effects.getRangeByIndexes(effectRows.indexOf(template),0,1,effectHead.length),'all');
  dest.values=[row];
}
const pools=books[files[2]].worksheets.getItemAt(0), poolRows=read(pools), poolHead=poolRows[0];
for(let i=0;i<rules.tiers.length;i++) {
  const tier=rules.tiers[i], row=Array(poolHead.length).fill(null);
  row[poolHead.indexOf('Id')]=tier.poolId;
  row[poolHead.indexOf('EffectList')]=rules.categories.map(c=>`${c.base+tier.suffix},${rules.weight}`).join(';');
  const dest=pools.getRangeByIndexes(poolRows.length+i,0,1,poolHead.length);
  dest.copyFrom(pools.getRangeByIndexes(poolRows.length-1,0,1,poolHead.length),'all');
  dest.values=[row];
  dest.format.rowHeight=50;
}
const counts={[files[0]]:erows.length-4,[files[1]]:effectRows.length-4+72,[files[2]]:poolRows.length-4+6};
const notes={
  [files[0]]:'CHG-023：金/红192条装备仅修改RareEffect；5～20、25～40、45～60级分别对应金1/2/3与红1/2/3，池6001～6006。绿蓝紫、普通Effect、SpecialEffect、FixEffect及刷新数量保持不变。',
  [files[1]]:'CHG-023：追加72条增伤技能效果定义，EffectId与SkillId同号（31101～32206，按12类×6档保留技能编号间隔）。每条SkillList仅绑定一个技能；ParameterLimit=1、Score=150沿用既有纯技能效果模板3101，不改原有846条。',
  [files[2]]:'CHG-023：追加6001～6006共6个稀有词条池，每池12个同档增伤Effect，权重均为100；金1/2/3为6%/12%/18%，红1/2/3为15%/20%/25%。原253池不改。'
};
for(const f of files.slice(0,3)) {
  const n=books[f].worksheets.getItem('中文说明');
  n.getRange('B3').values=[['CHG-023 / 2026-08-27 / 仅06候选，未写Datas']];
  n.getRange('B4').values=[['稀有词条六档候选配置，需三表配套落地']];
  n.getRange('B7').values=[[counts[f]]];
  n.getRange('B9').values=[[String(n.getRange('B9').values[0][0]??'')+'\n'+notes[f]]];
  n.getRange('A9:B9').format.rowHeight=180;
}
const index=books[files[3]].worksheets.getItemAt(0), indexRows=read(index);
for(let r=1;r<indexRows.length;r++) {
  const f=indexRows[r][1];
  if(!notes[f])continue;
  index.getCell(r,3).values=[['CHG-023：稀有词条六档，06候选']];
  index.getCell(r,4).values=[[counts[f]]];
  index.getCell(r,6).values=[[String(indexRows[r][6]??'')+'\n'+notes[f]]];
  index.getRangeByIndexes(r,0,1,7).format.rowHeight=120;
}
const audit=books[files[3]].worksheets.add('CHG023稀有词条');
audit.getRange('A1:G1').merge();audit.getRange('A1').values=[['CHG-023｜稀有词条六档映射（仅06候选）']];
audit.getRange('A3:G3').values=[['档位','品质','最低等级','最高等级','RareEffect池ID','增伤','装备条数']];
audit.getRange('A4:G9').values=rules.tiers.map(t=>[t.name,t.quality,t.min,t.max,t.poolId,t.bonus,pre.tierCounts[t.name]]);
audit.getRange('F4:F9').setNumberFormat('0%');
audit.getRange('A12:G12').values=[['技能类别',...rules.tiers.map(t=>t.name)]];
audit.getRange('A13:G24').values=rules.categories.map(c=>[c.name,...rules.tiers.map(t=>c.base+t.suffix)]);
audit.getRange('A27:G29').merge();audit.getRange('A27').values=[['引用：SpecialEquipment.RareEffect → EffectDrop.Id → EffectList中的EffectId → Effect.SkillList → Skill.SkillId。每池12条等权100；普通属性、特殊技能、稀有词条刷新数量不变。技能ID来自用户新设计，已核对本机Skill表72条均存在；未执行正式导表或运行时测试。']];
audit.getRange('A1:G29').format.font.name='Microsoft YaHei';audit.getRange('A1:G29').format.font.size=10;
audit.getRange('A1:G29').format.wrapText=true;
audit.getRange('A:G').format.columnWidth=16;
audit.getRange('A1:G29').format.rowHeight=24;
for(const r of ['A1:G1','A3:G3','A12:G12'])audit.getRange(r).format={fill:'#17365D',font:{bold:true,color:'#FFFFFF'},rowHeight:30};
audit.freezePanes.freezeRows(3);
for(const f of files) {
  console.log(f,(await books[f].inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',options:{useRegex:true,maxResults:10},maxChars:1000})).ndjson);
  await render(f,0,f===files[0]?'D293:M297':f===files[1]?'A851:I856':f===files[2]?'A258:Q263':'B10:E14','after');
  await render(f,1,f===files[3]?'A28:M31':'A1:B9','after');
  if(f===files[3])await render(f,2,'A1:G29','after');
  const xlsx=await SpreadsheetFile.exportXlsx(books[f]);
  const temp=path.join(here,f);
  await xlsx.save(temp);
  assert.equal(await sha(path.join(out,f)),pre.candidateHashes[f],`Concurrent edit before commit: ${f}`);
  await fs.copyFile(temp,path.join(out,f));
  await fs.unlink(temp);
}
const report={revision:rules.revision,backup,files,counts,equipmentChanged:changed,newEffects:72,newPools:6,formalHashes:pre.formalHashes,candidateHashes:pre.candidateHashes};
await fs.writeFile(path.join(framework,'05_验算核算/mapping-rare-CHG023.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report));
