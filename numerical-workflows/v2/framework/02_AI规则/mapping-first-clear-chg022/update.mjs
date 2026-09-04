import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
process.on('uncaughtException',e=>{console.error(e.stack?.split('\n').slice(0,4).join('\n')??e.message);process.exit(1);});
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../..');
const out=path.join(root,'06_最终配置/映射装备');
const source=JSON.parse(await fs.readFile(path.join(here,'source.json'),'utf8'));
const files=source.files,books={},previewDir=path.join(here,'previews');
const sha=async p=>crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex');
await fs.mkdir(previewDir,{recursive:true});
for(const f of files)books[f]=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out,f)));
async function render(f,sheet,range,name){const b=await books[f].render({sheetName:sheet,range,scale:1.2,format:'png'});await fs.writeFile(path.join(previewDir,name+'.png'),new Uint8Array(await b.arrayBuffer()));}
const samples=[['Drop_dungeon.xlsx','Drop','B9:M11','drop'],['Items.xlsx','items','A303:K303','item'],['SpecialEquipmentGenerate.xlsx','SpecialEquipment','B280:K283','generate'],['UIlevel.xlsx','level','R15:R19','ui'],['00_配置清单.xlsx','配置清单','A1:E5','index']];
if(process.argv.includes('--inspect')){for(const a of samples)await render(...a.slice(0,3),'before-'+a[3]);console.log('Baseline rendered');process.exit(0);}
for(const [p,h] of Object.entries(source.formalHashes))assert.equal(await sha(p),h,p);
for(const f of files)assert.equal(await sha(path.join(out,f)),source.candidateHashes[f],f);
const backup=path.join(root,'05_验算核算/映射装备CHG022_候选备份',new Date().toISOString().replaceAll(/[-:]/g,'').slice(0,15));
await fs.mkdir(backup,{recursive:true});
for(const f of files)await fs.copyFile(path.join(out,f),path.join(backup,f));
await fs.copyFile(path.join(here,'source.json'),path.join(backup,'source.json'));
for(const p of source.patches){const s=books[p.file].worksheets.getItem(p.sheet),cell=s.getCell(p.row,p.col);assert.equal(cell.values[0][0],p.old);assert(!cell.formulas[0][0]);cell.values=[[p.new]];}
const g=source.newGenerate,gs=books['SpecialEquipmentGenerate.xlsx'].worksheets.getItem(g.sheet);
const dest=gs.getRangeByIndexes(g.row,0,1,g.values.length);
dest.copyFrom(gs.getRangeByIndexes(4,0,1,g.values.length),'all');dest.values=[g.values];
dest.format={font:{name:'Calibri',size:11},wrapText:true,rowHeight:65};
books['Drop_dungeon.xlsx'].worksheets.getItem('Drop').getRange('C10').format={wrapText:true,rowHeight:55};
const notes={
 'Drop_dungeon.xlsx':'CHG-022：仅第三层首通20000012的箱由4212改4375×1，固定开出10级金装；钥匙25×1及其他Drop不变。常规Drop不能引用4375。SVN未修改。',
 'Items.xlsx':'CHG-022：4375为第三层实际可发放专用箱，蓝色外观，ParaList=4375，开启固定1件10级金装。其他首通展示4373～4374、4376～4402仍为占位；普通预览4403～4447仅展示。',
 'SpecialEquipmentGenerate.xlsx':'CHG-022：追加4375：GradeList=10,1000，QualityList=Orange,1000，GenerateMin/Max=1，保留其他278条。按Id和字段导入；正式表已增加FirstQualityList，候选仍为原11列，禁止整行盲贴。',
 'UIlevel.xlsx':'CHG-022：第三层五变体FirstReward保持25,1;4375,1，现与实际Drop和开箱链对齐；Reward及所有UI数据不变。正式表多Power列，按字段导入；SVN仍有旧首通与常规预览道具缺失，不能声称已同步正式。'
};
const counts={'Drop_dungeon.xlsx':695,'Items.xlsx':323,'SpecialEquipmentGenerate.xlsx':279,'UIlevel.xlsx':150};
for(const f of files.filter(f=>notes[f])){
 const s=books[f].worksheets.getItem('中文说明');
 s.getRange('B3').values=[['CHG-019/021 + CHG-022 / 2026-08-27 / 仅06候选']];
 s.getRange('B4').values=[['第三层4375实际箱链路修复；未同步SVN或做客户端发奖验收']];
 s.getRange('B7').values=[[counts[f]]];s.getRange('B9').values=[[notes[f]]];s.getRange('B9').format.wrapText=true;s.getRange('A9:B9').format.rowHeight=105;
 if(f==='SpecialEquipmentGenerate.xlsx')s.getRange('B6').values=[['既有278条 + CHG-022用户确认4375固定10级金装；按当前候选字段映射']];
}
const idx=books['00_配置清单.xlsx'].worksheets.getItem('配置清单'),rows=idx.getUsedRange().values;
for(let i=1;i<rows.length;i++){const f=rows[i][1];if(!notes[f])continue;idx.getCell(i,3).values=[['CHG-022：候选，按字段导入']];idx.getCell(i,4).values=[[counts[f]]];idx.getCell(i,6).values=[[notes[f]]];}
books['00_配置清单.xlsx'].worksheets.getItem('CHG019概率展示').getRange('A40').values=[['CHG-019常规概率与展示规则保持不变。CHG-022仅第三层首通实际箱改为4375：蓝色外观，固定开出1件10级金装，返还钥匙1。首通预览4375×1不是普通蓝箱概率。正式45个预览道具缺失与旧首通尚未同步；只交付06候选。']];
for(const a of samples)await render(...a.slice(0,3),'after-'+a[3]);
for(const f of files.filter(f=>notes[f]))await render(f,'中文说明','A1:B9','notes-'+f);
await render('00_配置清单.xlsx','CHG019概率展示','A35:M40','probabilities');
const staging=path.join(here,'outputs');await fs.mkdir(staging,{recursive:true});
for(const f of files){const x=await SpreadsheetFile.exportXlsx(books[f]);await x.save(path.join(staging,f));}
await fs.writeFile(path.join(here,'repair.json'),JSON.stringify({revision:'CHG-022',out,backup,staging,source,files},null,2));
console.log(JSON.stringify({staged:files.length,backup,newGenerateId:4375}));
