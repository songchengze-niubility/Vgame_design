import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const run=path.join(root,'05_验算核算/章节任务纠偏_20260827');
const plan=JSON.parse(await fs.readFile(path.join(run,'plan.json'),'utf8'));
const file=plan.files.find(f=>f.file.endsWith('00_配置清单.xlsx'));
const before=process.argv.includes('--before');
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(file.source));
if(!before){
  for(const e of file.edits){
    const s=w.worksheets.getItem(e.sheet),c=s.getRange(e.cell);
    if((c.values[0][0]??null)!==e.old)throw Error(`Baseline drift: ${e.sheet}!${e.cell}`);
    c.values=[[e.new]];
    c.format.wrapText=true;
  }
  const s=w.worksheets.add('章节任务落点');
  const order={'映射装备':0,'舱室':1,'玩家等级':2};
  const audited=plan.chapter_audit.verified_existing_chapter_rows.sort((a,b)=>order[a.category]-order[b.category]||a.chapter-b.chapter);
  const values=[['类别','章节','组ID','TaskId','TargetId','任务目标 / ParamList','DropId','实际奖励','本轮处理'],
    ...audited.map(x=>[x.category,x.chapter,x.group_id,x.task_id,x.target_id,`${x.description}\n参数：${x.param}`,x.drop_id,
      x.rewards.map(r=>r.item===25?`映射之匙×${r.min}`:`道具${r.item}×${r.min}`).join('；'),'已在06，核对保留'])];
  s.getRange(`A1:I${values.length}`).values=values;
  s.getRange(`A1:I${values.length}`).format={font:{name:'Microsoft YaHei',size:11},wrapText:true,rowHeight:48};
  s.getRange('A1:I1').format={fill:'#1F4E78',font:{bold:true,color:'#FFFFFF'},rowHeight:30};
  for(const [col,width] of Object.entries({A:85,B:50,C:65,D:80,E:85,F:325,G:105,H:160,I:165}))s.getRange(`${col}:${col}`).format.columnWidthPx=width;
  s.getRange(`B2:E${values.length}`).setNumberFormat('0');
  s.getRange(`G2:G${values.length}`).setNumberFormat('0');
  const key=w.worksheets.getItem('钥匙来源核对');
  key.getRange('A9:F9').copyFrom(key.getRange('A7:F7'),'all');
  key.getRange('A9:F9').values=[['章节映射装备任务',3,6,null,'一次性','第二至七章各1条；不并入每周产出']];
  key.getRange('D9').formulas=[['=B9*C9']];
  key.getRange('A9:F9').format.rowHeight=45;
  for(const row of [3,4,10])w.worksheets.getItem('配置清单').getRange(`A${row}:D${row}`).format.rowHeight=90;
  w.worksheets.getItem('任务总览').getRange('A4:D4').format.rowHeight=150;
}
const outdir=path.join(run,before?'before':'after');await fs.mkdir(outdir,{recursive:true});
const previews=before?[['任务总览','A1:D5'],['数值校验','A1:D11']]:[
  ['章节任务落点','A1:I7'],['章节任务落点','A8:I19'],['钥匙来源核对','A1:F9'],
  ['配置清单','A1:D14'],['任务总览','A1:D5'],['落地说明','A1:C10'],['数值校验','A1:D11']];
for(const [sheetName,range] of previews){
  const blob=await w.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(outdir,`${sheetName}_${range.replace(':','-')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
if(!before){
  const dest=path.join(run,'stage',file.file);await fs.mkdir(path.dirname(dest),{recursive:true});
  await(await SpreadsheetFile.exportXlsx(w)).save(dest);
}
console.log(before?'Rendered original manifest':'Staged corrected manifest; existing chapter configs unchanged');
