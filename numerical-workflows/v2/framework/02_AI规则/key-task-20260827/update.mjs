import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
try {
  await fs.access(path.join(root,'05_验算核算/章节任务纠偏_20260827/plan.json'));
  throw Error('Historical batch superseded: do not reapply rejected daily/weekly unlock edits.');
} catch(e) { if(e.code!=='ENOENT')throw e; }
const run=path.join(root,'05_验算核算/映射之匙任务_20260827');
const plan=JSON.parse(await fs.readFile(path.join(run,'plan.json'),'utf8'));
const before=process.argv.includes('--before');
const only=process.argv.find(x=>x.startsWith('--file='))?.slice(7);
const previews=path.join(run,before?'before':'after');
await fs.mkdir(previews,{recursive:true});
const renderIndex=[];
for(const f of plan.files){
  if(only&&f.file!==only) continue;
  const w=await SpreadsheetFile.importXlsx(await FileBlob.load(f.source));
  if(!before){
    if(f.file==='主线高难/Drop_mainlevel.xlsx'){
      const s=w.worksheets.getItem('Drop');
      s.getRangeByIndexes(plan.append_main_row-1,0,1,16).copyFrom(s.getRangeByIndexes(plan.append_main_row-2,0,1,16),'all');
      s.getRangeByIndexes(plan.append_main_row-1,0,1,16).values=[[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null]];
    }
    for(const e of f.edits){
      const s=w.worksheets.getItem(e.sheet);
      const c=s.getCell(e.row-1,e.col-1);
      const actual=c.values?.[0]?.[0]??null;
      if(e.row!==plan.append_main_row || f.file!=='主线高难/Drop_mainlevel.xlsx'){
        if(actual!==e.old) throw Error(`${f.file}/${e.sheet}/${e.row},${e.col}: baseline drift ${actual} != ${e.old}`);
      }
      if(typeof e.new==='string'&&e.new.startsWith('=')) c.formulas=[[e.new]];
      else c.values=[[e.new]];
      if(e.sheet==='中文说明'){
        c.format.wrapText=true;
        s.getRangeByIndexes(e.row-1,0,1,2).format.rowHeight=62;
      }
      if(f.file==='任务/Task.xlsx'&&e.col===12){
        c.format.wrapText=true;
        c.format.rowHeight=28;
      }
    }
    if(f.file==='任务/00_配置清单.xlsx'){
      const s=w.worksheets.add('钥匙来源核对');
      s.getRange('A1:F8').values=[
        ['来源','单次数量','周期内次数','周期总量','周期','依据'],
        ['每日80活跃',3,7,null,'周','DailyActiveReward→1010204'],
        ['每周20/40活跃',10,1,null,'周','1020202×4＋1020204×6'],
        ['神经漫游',2,5,null,'周','2/4/6/8/10千分；四难度互斥'],
        ['每月签到',2,4,null,'月','每月5/12/19/26日'],
        ['第二章36星',5,1,null,'一次性','ChapterStarReward.Id12→11000012'],
        ['七日任务',8,1,null,'一次性','保持原70任务包，合计8把'],
        ['每周常驻合计',null,null,null,'周','不合并月签、一次性或首通返还']
      ];
      for(let r=2;r<=7;r++) s.getRange(`D${r}`).formulas=[[`=B${r}*C${r}`]];
      s.getRange('D8').formulas=[['=SUM(D2:D4)']];
      s.getRange('A1:F8').format={font:{name:'Microsoft YaHei',size:11},rowHeight:30,wrapText:true};
      s.getRange('A1:F1').format={fill:'#1F4E78',font:{bold:true,color:'#FFFFFF'},rowHeight:32};
      s.getRange('A:A').format.columnWidthPx=160;
      s.getRange('B:E').format.columnWidthPx=90;
      s.getRange('F:F').format.columnWidthPx=360;
      s.getRange('B2:D8').setNumberFormat('0');
      const n=w.worksheets.getItem('落地说明');
      n.getRange('A7:C10').copyFrom(n.getRange('A3:C6'),'all');
      for(const e of f.edits.filter(e=>e.sheet==='落地说明'&&e.row>=7)) n.getCell(e.row-1,e.col-1).values=[[e.new]];
      n.getRange('A7:C10').format.wrapText=true;
      n.getRange('A7:C10').format.rowHeight=95;
    }
    if(f.file.endsWith('00_配置清单.xlsx')){
      for(const s of w.worksheets.items){
        if(s.name==='钥匙来源核对')continue;
        const values=s.getUsedRange().values;
        s.getUsedRange().format.wrapText=true;
        for(let ri=0;ri<values.length;ri++){
          const width=f.file.startsWith('任务')?28:45;
          const lines=Math.max(1,...values[ri].map(v=>typeof v==='string'?Math.ceil(v.length/width):1));
          s.getRangeByIndexes(ri,0,1,values[ri].length).format.rowHeight=Math.min(180,Math.max(25,lines*21));
        }
      }
      if(f.file.startsWith('任务')){
        w.worksheets.getItem('任务总览').getRange('A4:D4').format.rowHeight=150;
        w.worksheets.getItem('落地说明').getRange('A2:C10').format.rowHeight=125;
        w.worksheets.getItem('新增任务类型').getRange('A2:E13').format.rowHeight=65;
      }
    }
  }
  for(const s of w.worksheets.items){
    let range;
    const edits=f.edits.filter(e=>e.sheet===s.name);
    const first=edits.length?Math.min(...edits.map(e=>e.row)):1;
    if(s.name==='Drop'){
      const start=Math.max(1,Math.min(first-2, before&&f.file==='主线高难/Drop_mainlevel.xlsx'?998:first));
      range=`B${start}:O${start+8}`;
    }else if(s.name==='Task')range=`H${first}:O${first+4}`;
    else if(s.name==='Sheet1')range='B1:F14';
    else if(s.name==='周奖励预览')range='A1:N11';
    else if(s.name==='周奖励汇总')range='A1:L5';
    else if(s.name==='钥匙来源核对')range='A1:F8';
    else if(s.name==='新增任务类型')range='A1:E13';
    else if(s.name==='中文说明')range=`A1:B${Math.max(6,first)}`;
    else if(s.name==='配置清单')range=f.file.startsWith('签到')?'A1:H6':f.file.startsWith('无限')?'A1:F9':f.file.startsWith('主线')?'A1:E10':'A1:D14';
    else if(s.name==='落地说明')range='A1:C10';
    else if(s.name==='任务总览')range='A1:D5';
    else if(s.name==='数值校验')range='A1:D11';
    else if(s.name==='ID号段')range='A1:D12';
    else range='A1:C11';
    const name=f.file.replace(/[\/]/g,'_').replace('.xlsx','')+'_'+s.name+'.png';
    const p=path.join(previews,name);
    const blob=await w.render({sheetName:s.name,range,scale:1,format:'png'});
    await fs.writeFile(p,new Uint8Array(await blob.arrayBuffer()));
    renderIndex.push({file:f.file,sheet:s.name,range,path:p});
  }
  if(!before){
    const dest=path.join(run,'stage',f.file);
    await fs.mkdir(path.dirname(dest),{recursive:true});
    const out=await SpreadsheetFile.exportXlsx(w);await out.save(dest);
  }
  console.log(JSON.stringify({file:f.file,mode:before?'before':'staged',edits:f.edits.length}));
}
await fs.writeFile(path.join(previews,'index.json'),JSON.stringify(renderIndex,null,2));
