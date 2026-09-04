import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

// CHG-019: candidate mirrors only. Never writes to VGAME_ROOT/Datas.
const here = path.dirname(fileURLToPath(import.meta.url));
const framework = path.resolve(here, '../..');
const arg = process.argv.indexOf('--out');
const out = arg >= 0 ? path.resolve(process.argv[arg + 1]) : path.join(framework, '06_最终配置/映射装备');
assert(out.startsWith(path.join(framework, '06_最终配置') + path.sep));
const inspectOnly = process.argv.includes('--inspect');
const previewDir = path.join(here, 'previews');
await fs.mkdir(previewDir, { recursive: true });
const files = ['Drop_dungeon.xlsx', 'Items.xlsx', 'UIlevel.xlsx', '00_配置清单.xlsx'];
const books = {};
for (const file of files) books[file] = await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out, file)));
const generate = await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out, 'SpecialEquipmentGenerate.xlsx')));
const read = sheet => sheet.getUsedRange().values.map(r => r.map(v => v ?? null));
const original = Object.fromEntries(files.map(f => [f, read(books[f].worksheets.getItemAt(0))]));

async function render(wb, sheet, range, name) {
  const blob = await wb.render({ sheetName: sheet, range, scale: 1.3, format: 'png' });
  await fs.writeFile(path.join(previewDir, name + '.png'), new Uint8Array(await blob.arrayBuffer()));
}
if (process.argv.includes('--inspect-final')) {
  await render(books['Items.xlsx'], 'items', 'A253:F259', 'final-new-items');
  await render(books['UIlevel.xlsx'], 'level', 'P130:R133', 'final-high-level-preview');
  process.exit(0);
}
if (inspectOnly) {
  for (const file of files) {
    const wb = books[file];
    console.log(file, (await wb.inspect({kind:'sheet', include:'id,name', maxChars:1500})).ndjson);
    await render(wb, wb.worksheets.getItemAt(0).name, file === '00_配置清单.xlsx' ? 'A1:E7' : 'A1:F8', 'before-' + file);
  }
  process.exit(0);
}

const timestamp = new Date().toISOString().replaceAll(/[-:]/g, '').slice(0, 15);
const backup = path.join(framework, '05_验算核算/映射装备CHG019_候选备份', timestamp);
await fs.mkdir(backup, { recursive: true });
for (const file of files) await fs.copyFile(path.join(out, file), path.join(backup, file));

const checks = [];
function check(name, condition) { assert(condition, name); checks.push({ name, result: 'PASS' }); }
function eq(a,b) { return JSON.stringify(a) === JSON.stringify(b); }
const qualities = ['Green','Blue','Purple','Orange','Red'];
const names = ['绿色','蓝色','紫色','金色','红色'];
// Observed CHG-012 green/blue curves, frozen from the user-reviewed baseline.
const green = [5150,5093,5036,4980,4923,4865,4808,4751,4695,4538,4391,4244,4097,3951,3804,3656,3509,3363,3216,3019,2837,2655,2474,2292,2110,1927,1745,1564,1382,1200];
const blue = [3000,2993,2986,2979,2972,2966,2959,2952,2945,2938,2931,2924,2917,2910,2903,2897,2890,2883,2876,2869,2862,2855,2848,2841,2834,2828,2821,2814,2807,2800];
const expectedHit = [0,0,0,0,0,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000,4100,4200,4300,4500];
const extraHit = [0,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,6000,7000,8000,9000,0,1000,2000,3000,4000,5000,6000,7000,8000,9000,0,2500,5000,7500,0];
const materialTiers = [10,10,10,10,10,10,10,10,20,30,30,30,30,30,30,40,40,40,40,40,40,45,45,45,50,50,55,55,60,60];
const tiers = [10,20,30,40,45,50,55,60];
const boxWeights = l => {
  const gold = l < 10 ? 0 : 100 + 25*(l-10);
  const red = l < 20 ? 0 : 30 + 12*(l-20);
  return [green[l-1],blue[l-1],10000-green[l-1]-blue[l-1]-gold-red,gold,red];
};
const materialQuality = l => {
  const gold = l < 10 ? 0 : (60+13*(l-10))/4000;
  const red = l < 20 ? 0 : (5+(l-20))/1000;
  return [1-gold-red,gold,red];
};
const dropData = original['Drop_dungeon.xlsx'].slice(4).filter(r => r[1] !== null);
const pools = new Map();
for (const row of dropData) {
  if (!pools.has(row[1])) pools.set(row[1], []);
  pools.get(row[1]).push([...row]);
}
const oldPools = new Map([...pools].map(([id,rows]) => [id, structuredClone(rows)]));
const layers = [];
for (let l=1;l<=30;l++) {
  const w=boxWeights(l);
  const fixed=pools.get(22100+l);
  check(`L${l} fixed box shape`, fixed.length===5);
  for (const row of fixed) row[12]=w[(row[9]-4201)%5];
  check(`L${l} fixed weights`, w.every(x=>x>=0) && w.reduce((a,b)=>a+b,0)===10000);
  const extra=pools.get(22200+l);
  const oldSum=extra.reduce((a,r)=>a+r[12],0);
  const oldHit=extra.filter(r=>r[9]!==0).reduce((a,r)=>a+r[12],0)/oldSum;
  check(`L${l} extra chance baseline`, Math.abs(oldHit-extraHit[l-1]/10000)<1e-12);
  if (l>=10 && extraHit[l-1]>0) {
    // 200000 is exactly divisible for all fixed-quality weights and extra chances.
    for (const row of extra) row[12]=row[9]===0 ? (10000-extraHit[l-1])*20 : w[(row[9]-4201)%5]*extraHit[l-1]/500;
    check(`L${l} extra weights exact`, extra.every(r=>Number.isInteger(r[12])) && extra.reduce((a,r)=>a+r[12],0)===200000);
  }
  if (l>=10) {
    const current=pools.get(22300+l);
    const sum=current.reduce((a,r)=>a+r[12],0);
    check(`L${l} main hit baseline`, Math.abs(1-current.find(r=>r[9]===0)[12]/sum-expectedHit[l-1]/10000)<1e-12);
    const result=[];
    const miss=[...current.find(r=>r[9]===0)];
    miss[12]=(10000-expectedHit[l-1])*800;
    result.push(miss);
    const quality=materialQuality(l);
    for (let c=0;c<3;c++) for (let q=0;q<3;q++) {
      if (quality[q]===0) continue;
      const item=1080+tiers.indexOf(materialTiers[l-1])*9+c*3+q;
      const row=[...(current.find(r=>r[9]===item) ?? current.find(r=>r[9]!==0))];
      row[2]=`${materialTiers[l-1]}档${['武器','防具','首饰'][c]}${['紫','金','红'][q]}主材`;
      row[9]=item;
      const exact=8000000*(expectedHit[l-1]/10000)*quality[q]*[.2,.55,.25][c];
      check(`L${l} item${item} exact integer`, Math.abs(exact-Math.round(exact))<1e-6);
      row[12]=Math.round(exact);
      result.push(row);
    }
    check(`L${l} main total`, result.reduce((a,r)=>a+r[12],0)===8000000);
    pools.set(22300+l,result);
  }
  layers.push({layer:l,box:w,mainHit:expectedHit[l-1]/10000,main:materialQuality(l),tier:materialTiers[l-1]});
}
const changedIds=new Set([...Array(30)].flatMap((_,i)=>[22101+i,22201+i]).concat([...Array(21)].map((_,i)=>22310+i)));
for (const [id,rows] of pools) if (!changedIds.has(id)) check(`unchanged DropId ${id}`,eq(rows,oldPools.get(id)));
const newDrops=[...pools.values()].flat();
check('Drop candidate row count 696', newDrops.length===696);
check('18 added records against original pre-CHG019 mirror', newDrops.length===678+18);

const genRows=read(generate.worksheets.getItemAt(0));
const gradeMap=new Map();
for (let l=1;l<=30;l++) {
  const boxes=genRows.slice(4).filter(r=>r[1]>=4201+(l-1)*5 && r[1]<=4205+(l-1)*5);
  check(`L${l} five same grade pools`,boxes.length===5 && boxes.every(r=>r[4]===boxes[0][4]));
  gradeMap.set(l,boxes[0][4].split(';').map(s=>s.split(',').map(Number)).filter(([,w])=>w>0).map(([g])=>g).sort((a,b)=>b-a));
}
const pairMap=new Map();
for (const l of layers) {
  l.grades=gradeMap.get(l.layer);
  const qs=l.box.map((w,q)=>({w,q})).filter(x=>x.w>0).map(x=>x.q).reverse();
  const n=qs.length, m=l.grades.length, base=Math.floor(n/m), remainder=n%m;
  const allocated=[];
  l.grades.forEach((grade,index)=>{for(let k=0;k<base+(index>=m-remainder?1:0);k++) allocated.push(grade);});
  l.pairs=qs.map((q,i)=>({grade:allocated[i],quality:q,key:`${allocated[i]}:${q}`}));
  check(`L${l.layer} all grades represented`,eq([...new Set(allocated)].sort((a,b)=>b-a),l.grades));
  for (const pair of l.pairs) pairMap.set(pair.key,pair);
}
const pairs=[...pairMap.values()].sort((a,b)=>a.grade-b.grade||a.quality-b.quality);
pairs.forEach((p,i)=>p.id=4403+i);
const currentItems=original['Items.xlsx'].slice(4).filter(r=>r[0]!==null);
const itemRows=currentItems.map(r=>[...r]);
const previewTemplate=currentItems.find(r=>r[0]===4351);
function upsert(row) {
  const i=itemRows.findIndex(r=>r[0]===row[0]);
  if (i>=0) {
    check(`UI id ${row[0]} belongs to this revision`,itemRows[i][10]?.includes('CHG-019'));
    itemRows[i]=row;
  } else itemRows.push(row);
}
for (const p of pairs) {
  const row=[...previewTemplate];
  row[0]=p.id; row[1]=`${p.grade}级${names[p.quality]}映射装备箱`;
  row[6]=`UIRes/UIAtlas/Icon/Items/item_specialequipment_${p.quality+1}.png`;
  row[8]=qualities[p.quality];
  row[9]=`本层可能掉落${names[p.quality]}宝箱，并开出${p.grade}级映射装备；全部可能装备等级见关卡说明。`;
  row[10]='CHG-019 UI展示占位；不可掉落、不可获得';
  upsert(row);
}
const materialPreview=new Map();
for(const row of currentItems) if(row[0]>=4355&&row[0]<=4363) {
  const grade=Number(row[1].match(/\d+/)[0]);
  materialPreview.set(`${grade}:${row[8]}`,row[0]);
}
let next=4403+pairs.length;
for (const grade of [40,45]) {
  const row=[...currentItems.find(r=>r[0]===4359)];
  row[0]=next++; row[1]=`${grade}级随机打造主材`; row[8]='Red';
  row[9]=`本层可能掉落${grade}级随机打造主材，最高为红色品质。`;
  row[10]='CHG-019 UI展示占位；不可掉落、不可获得';
  upsert(row); materialPreview.set(`${grade}:Red`,row[0]);
}
const newItemIds=new Set(pairs.map(p=>p.id).concat([next-2,next-1]));
const itemIds=new Set(itemRows.map(r=>r[0]));
check('all item IDs unique', itemIds.size===itemRows.length);
check('preview IDs never occur in real Drop', newDrops.every(r=>!newItemIds.has(r[9])));
const uiData=original['UIlevel.xlsx'].slice(4).filter(r=>r[1]!==null).map(r=>[...r]);
const uiHead=original['UIlevel.xlsx'][0];
const desCol=uiHead.indexOf('Des'), rewardCol=uiHead.indexOf('Reward');
for (const row of uiData) {
  const l=layers.find(l=>250000+l.layer*10+1<=row[1]&&row[1]<=250000+l.layer*10+5);
  assert(l,`Unexpected UI LevelId ${row[1]}`);
  let reward=l.pairs.map(p=>`${pairMap.get(p.key).id},-1`);
  if(l.layer>=6) {
    const top=l.main[2]>0?'Red':l.main[1]>0?'Orange':'Purple';
    const id=materialPreview.get(`${l.tier}:${top}`);
    assert(id,`Missing main preview ${l.tier}:${top}`);
    reward.push(`${id},-1`,'4364,-1');
  }
  row[rewardCol]=reward.join(';');
  const old=String(row[desCol]??'').replace(/^可能掉落装备等级：[^\n]*\n/,'');
  row[desCol]=`可能掉落装备等级：${l.grades.map(g=>g+'级').join('、')}。\n${old}`;
  l.preview=l.pairs.map(p=>`${p.grade}级${names[p.quality]}`).join(' → ');
  check(`UI ${row[1]} valid references`,reward.every(s=>itemIds.has(Number(s.split(',')[0]))));
  const before=original['UIlevel.xlsx'].slice(4).find(r=>r[1]===row[1]);
  check(`UI ${row[1]} only Reward Des changed`,row.every((v,c)=>c===desCol||c===rewardCol||v===before[c]));
}
check('UI 150 rows',uiData.length===150);
check('user example 60red 60gold 55purple 55blue 55green',layers[29].preview==='60级红色 → 60级金色 → 55级紫色 → 55级蓝色 → 55级绿色');

function writeRows(wb, rows) {
  const sheet=wb.worksheets.getItemAt(0), width=original[files.find(f=>books[f]===wb)][0].length;
  const oldLength=read(sheet).length;
  for(let r=oldLength;r<rows.length+4;r++) sheet.getRangeByIndexes(r,0,1,width).copyFrom(sheet.getRangeByIndexes(oldLength-1,0,1,width),'all');
  sheet.getRangeByIndexes(4,0,rows.length,width).values=rows.map(r=>Array.from({length:width},(_,c)=>r[c]??null));
}
writeRows(books['Drop_dungeon.xlsx'],newDrops);
writeRows(books['Items.xlsx'],itemRows);
writeRows(books['UIlevel.xlsx'],uiData);
const noteText={
  'Drop_dungeon.xlsx':'CHG-019：仅常规宝箱/主材更新；696行。固定箱池权重和10000；有触发的第10层起额外箱池200000；第10～30层主材池8000000，按权重总和归一化。主材新增18行；落正式表需人工预建行，禁止覆盖公式列。候选IsValid/状态不是正式字段。首通沿用本次前镜像，不作为与正式表一致的证明。',
  'Items.xlsx':`CHG-019：新增${pairs.length}个等级×品质箱预览和2个红主材预览（${4403}～${next-1}）；仅用于UI，不能发放。旧占位与真实道具保持不变。`,
  'UIlevel.xlsx':'CHG-019：仅更新150行Reward和Des；品质降序，每种品质1箱，等级降序均分、余数给低等级；所有正概率等级均可见。材料展示随最高可掉品质；FirstReward与其他字段不变。'
};
for(const file of files.slice(0,3)) {
  const s=books[file].worksheets.getItem('中文说明');
  s.getRange('B3').values=[['CHG-019 / 2026-08-27 / 06候选配置，未同步Datas']];
  s.getRange('B4').values=[['本次常规掉落/展示候选更新完成，正式落表仍须门禁']];
  s.getRange('B7').values=[[(file==='Drop_dungeon.xlsx'?newDrops:file==='Items.xlsx'?itemRows:uiData).length]];
  s.getRange('B9').values=[[noteText[file]]];
  s.getRange('B9').format.wrapText=true;
  s.getRange('A9:B9').format.rowHeight=120;
}
const index=books['00_配置清单.xlsx'].worksheets.getItemAt(0);
for(let r=1;r<original['00_配置清单.xlsx'].length;r++) {
  const file=original['00_配置清单.xlsx'][r][1];
  if(!noteText[file]) continue;
  index.getCell(r,3).values=[['CHG-019：候选更新，未落正式']];
  index.getCell(r,4).values=[[(file==='Drop_dungeon.xlsx'?newDrops:file==='Items.xlsx'?itemRows:uiData).length]];
  index.getCell(r,6).values=[[noteText[file]]];
  index.getRangeByIndexes(r,0,1,7).format.rowHeight=110;
}
const audit=books['00_配置清单.xlsx'].worksheets.getOrAdd('CHG019概率展示');
audit.getRange('A1:M1').merge();audit.getRange('A1').values=[['CHG-019｜30层常规掉落与展示（06候选，未落正式）']];
audit.getRange('A2:G5').values=[['参数','起始层','起始概率','终止层','终止概率','每层增量','口径'],['金箱',10,.01,30,.06,null,'单个已掉落箱'],['红箱',20,.003,30,.015,null,'单个已掉落箱'],['金主材',10,.015,30,.08,null,'已命中主材内']];
audit.getRange('A6:G6').values=[['红主材',20,.005,30,.015,null,'已命中主材内']];
for(let r=3;r<=6;r++) audit.getRange(`F${r}`).formulas=[[`=(E${r}-C${r})/(D${r}-B${r})`]];
audit.getRange('C3:C6').setNumberFormat('0.000%');audit.getRange('E3:F6').setNumberFormat('0.000%');
audit.getRange('A8:M8').values=[['层','绿箱','蓝箱','紫箱','金箱','红箱','主材总掉率','主材内紫','主材内金','主材内红','可能等级（降序）','宝箱展示（品质降序）','主材档位']];
for(const l of layers) {
  const r=l.layer+8;
  audit.getRange(`A${r}:M${r}`).values=[[l.layer,green[l.layer-1]/10000,blue[l.layer-1]/10000,null,null,null,l.mainHit,null,null,null,l.grades.join('/'),l.preview,l.tier]];
  for(const [c,formula] of Object.entries({D:`=1-B${r}-C${r}-E${r}-F${r}`,E:`=IF(A${r}<$B$3,0,$C$3+(A${r}-$B$3)*$F$3)`,F:`=IF(A${r}<$B$4,0,$C$4+(A${r}-$B$4)*$F$4)`,H:`=1-I${r}-J${r}`,I:`=IF(A${r}<$B$5,0,$C$5+(A${r}-$B$5)*$F$5)`,J:`=IF(A${r}<$B$6,0,$C$6+(A${r}-$B$6)*$F$6)`})) audit.getRange(`${c}${r}`).formulas=[[formula]];
}
audit.getRange('A40:M42').merge();audit.getRange('A40').values=[['概率口径：主材品质占比仅在已命中主材后计算；每次通关实得金/红主材概率=主材总掉率×对应品质占比。固定箱池10000；调整后的额外箱池200000；调整后的主材池8000000，均按整池权重归一化，精确保留目标概率和20%/55%/25%大类比例。箱数量、等级权重、副材及首通保持本次前镜像；首通与正式工作副本的已有差异未在本次重基。']];
audit.getRange('A1:M42').format.font.name='Microsoft YaHei';
audit.getRange('A1:M42').format.font.size=10;
audit.getRange('A1:M1').format={fill:'#17365D',font:{color:'#FFFFFF',bold:true},rowHeight:32};
audit.getRange('A8:M8').format={fill:'#17365D',font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:40};
audit.getRange('B9:J38').setNumberFormat('0.000%');
audit.getRange('A2:G6').format.rowHeight=24;
audit.getRange('A9:M38').format.rowHeight=48;
audit.getRange('A1:M42').format.wrapText=true;
audit.getRange('A:A').format.columnWidth=6;audit.getRange('B:J').format.columnWidth=12;
audit.getRange('K:K').format.columnWidth=20;audit.getRange('L:L').format.columnWidth=48;audit.getRange('M:M').format.columnWidth=12;
audit.getRange('A40:M42').format.rowHeight=32;
audit.freezePanes.freezeRows(8);

for (const file of files) {
  const wb=books[file];
  const result=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',options:{useRegex:true,maxResults:20},maxChars:3000});
  console.log(file,'errors',result.ndjson);
  for(let i=0;i<(file==='00_配置清单.xlsx'?2:2);i++) {
    const s=wb.worksheets.getItemAt(i);
    const range=s.name==='CHG019概率展示'?'A28:M38':s.name==='中文说明'?'A1:B9':file==='00_配置清单.xlsx'?'A1:E7':'A1:F8';
    await render(wb,s.name,range,`after-${file}-${i}`);
  }
  const xlsx=await SpreadsheetFile.exportXlsx(wb);
  await xlsx.save(path.join(out,file));
}
const report={revision:'CHG-019',generatedAt:new Date().toISOString(),output:out,scope:'06候选镜像；未写入Datas',backup,files,dropRows:newDrops.length,newMainRows:18,newBoxPreviewItems:pairs.length,newMainPreviewItems:2,newPreviewRange:[4403,next-1],itemRows:itemRows.length,uiRows:uiData.length,layers,checks};
await fs.writeFile(path.join(framework,'05_验算核算/mapping-equip-drop-preview-CHG019.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({files:4,checks:checks.length,dropRows:newDrops.length,itemRows:itemRows.length,previewRange:report.newPreviewRange,backup}));
