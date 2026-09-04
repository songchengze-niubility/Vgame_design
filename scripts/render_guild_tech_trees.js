const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const outputDir = path.resolve(__dirname, '..', 'design', 'assets');
fs.mkdirSync(outputDir, { recursive: true });

const palette = {
  bg: '#09111f',
  panel: '#111c30',
  panelAlt: '#0e192b',
  border: '#2b3b58',
  line: '#6f83a6',
  text: '#f4f7fb',
  muted: '#aebbd0',
  task: '#2656a8',
  dispatch: '#14766f',
  org: '#a85c18',
  supply: '#6842a8',
  shop: '#2e7d4f',
  terminal: '#ad7a13',
  attribute: '#285ea8',
  burst: '#7045a6',
  cycle: '#14766f',
};

function esc(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function svgBase(width, height, title, subtitle, body, footer) {
  return `
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000000" flood-opacity="0.28"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="${palette.line}"/>
    </marker>
    <linearGradient id="bg-gradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b1630"/>
      <stop offset="100%" stop-color="${palette.bg}"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg-gradient)"/>
  <text x="70" y="74" fill="${palette.text}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="42" font-weight="700">${esc(title)}</text>
  <text x="72" y="116" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="22">${esc(subtitle)}</text>
  ${body}
  <text x="70" y="${height - 34}" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="20">${esc(footer)}</text>
</svg>`;
}

function nodeBox(node, options = {}) {
  const w = node.w || options.w || 270;
  const h = node.h || options.h || 152;
  const color = node.color || options.color || palette.attribute;
  const x = node.x;
  const y = node.y;
  const lines = [
    { text: `${node.id}${node.coord ? ` · ${node.coord}` : ''}`, size: 18, color: '#d7e2f3', weight: 700 },
    { text: node.name, size: 25, color: palette.text, weight: 700 },
    { text: node.lv, size: 18, color: '#d7e2f3', weight: 400 },
    { text: node.effect, size: 20, color: palette.text, weight: 500 },
    { text: node.cost, size: 17, color: '#d7e2f3', weight: 400 },
  ].filter((line) => line.text);
  const lineY = [30, 62, 91, 119, 143];
  const text = lines.map((line, index) =>
    `<text x="${x + w / 2}" y="${y + lineY[index]}" text-anchor="middle" fill="${line.color}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="${line.size}" font-weight="${line.weight}">${esc(line.text)}</text>`
  ).join('\n');
  return `
  <g filter="url(#shadow)">
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="18" fill="${color}" stroke="#ffffff" stroke-opacity="0.18" stroke-width="2"/>
    ${text}
  </g>`;
}

function nodeCenter(node, side) {
  const w = node.w || 270;
  const h = node.h || 152;
  if (side === 'left') return { x: node.x, y: node.y + h / 2 };
  if (side === 'right') return { x: node.x + w, y: node.y + h / 2 };
  return { x: node.x + w / 2, y: node.y + h / 2 };
}

function connect(from, to, label = '') {
  const a = nodeCenter(from, 'right');
  const b = nodeCenter(to, 'left');
  const bend = Math.max(60, (b.x - a.x) * 0.45);
  const pathData = `M ${a.x} ${a.y} C ${a.x + bend} ${a.y}, ${b.x - bend} ${b.y}, ${b.x - 8} ${b.y}`;
  const labelMarkup = label
    ? `<text x="${(a.x + b.x) / 2}" y="${(a.y + b.y) / 2 - 10}" text-anchor="middle" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="16">${esc(label)}</text>`
    : '';
  return `<path d="${pathData}" fill="none" stroke="${palette.line}" stroke-width="4" marker-end="url(#arrow)"/>${labelMarkup}`;
}

function legendItem(x, y, color, label) {
  return `<rect x="${x}" y="${y - 18}" width="28" height="28" rx="7" fill="${color}"/><text x="${x + 40}" y="${y + 4}" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="20">${esc(label)}</text>`;
}

function panel(x, y, w, h, title, subtitle) {
  return `
  <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="24" fill="${palette.panel}" stroke="${palette.border}" stroke-width="2"/>
  <text x="${x + 34}" y="${y + 48}" fill="${palette.text}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="27" font-weight="700">${esc(title)}</text>
  <text x="${x + 34}" y="${y + 80}" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="18">${esc(subtitle)}</text>`;
}

function createPersonalTree() {
  const nodes = {
    P198: { id: 'P198', name: '基础强攻', lv: '最高 5 级', effect: '固定攻击 +1,500', cost: '总耗 700', x: 90, y: 410, color: palette.attribute },
    P199: { id: 'P199', name: '基础体魄', lv: '最高 5 级', effect: '固定生命 +5,000', cost: '总耗 1,300', x: 400, y: 410, color: palette.attribute },
    P200: { id: 'P200', name: '基础防护', lv: '最高 5 级', effect: '固定防御 +1,000', cost: '总耗 2,000', x: 710, y: 410, color: palette.attribute },
    P201: { id: 'P201', name: '强攻训练', lv: '最高 5 级', effect: '攻击 +10%', cost: '总耗 4,000', x: 1020, y: 410, color: palette.attribute },
    P202: { id: 'P202', name: '生命训练', lv: '最高 5 级', effect: '生命 +10%', cost: '总耗 4,500', x: 1330, y: 410, color: palette.attribute },
    P203: { id: 'P203', name: '防御训练', lv: '最高 5 级', effect: '防御 +10%', cost: '总耗 5,000', x: 1640, y: 410, color: palette.attribute },
    P204: { id: 'P204', name: '暴击训练', lv: '最高 3 级', effect: '暴击等级 +900', cost: '总耗 6,000', x: 1980, y: 220, color: palette.burst },
    P205: { id: 'P205', name: '暴伤训练', lv: '最高 3 级', effect: '暴伤等级 +1,100', cost: '总耗 6,500', x: 2290, y: 220, color: palette.burst },
    P210: { id: 'P210', name: '强攻进阶', lv: '最高 3 级', effect: '攻击 +7%', cost: '总耗 7,000', x: 2600, y: 220, color: palette.burst },
    P208: { id: 'P208', name: '生命进阶', lv: '最高 3 级', effect: '生命 +7%', cost: '总耗 6,000', x: 1980, y: 600, color: palette.cycle },
    P209: { id: 'P209', name: '防御进阶', lv: '最高 3 级', effect: '防御 +7%', cost: '总耗 6,500', x: 2290, y: 600, color: palette.cycle },
    P206: { id: 'P206', name: '能量循环', lv: '最高 3 级', effect: '能量回复等级 +900', cost: '总耗 7,000', x: 2600, y: 600, color: palette.cycle },
    P207: { id: 'P207', name: '技能循环', lv: '最高 3 级', effect: '冷却等级 +1,300', cost: '总耗 7,500', x: 2940, y: 410, color: palette.cycle },
    P211: { id: 'P211', name: '全域增幅', lv: '最高 2 级', effect: '伤害加成 +3%', cost: '总耗 15,000', x: 3270, y: 410, color: palette.terminal, w: 285 },
  };

  const connectors = [
    connect(nodes.P198, nodes.P199), connect(nodes.P199, nodes.P200), connect(nodes.P200, nodes.P201),
    connect(nodes.P201, nodes.P202), connect(nodes.P202, nodes.P203),
    connect(nodes.P203, nodes.P204), connect(nodes.P204, nodes.P205), connect(nodes.P205, nodes.P210),
    connect(nodes.P203, nodes.P208), connect(nodes.P208, nodes.P209), connect(nodes.P209, nodes.P206),
    connect(nodes.P210, nodes.P207), connect(nodes.P206, nodes.P207), connect(nodes.P207, nodes.P211),
  ].join('\n');

  const body = `
  ${legendItem(90, 170, palette.attribute, '基础 / 进阶属性')}
  ${legendItem(370, 170, palette.burst, '爆发属性支线')}
  ${legendItem(650, 170, palette.cycle, '技能循环支线')}
  ${legendItem(930, 170, palette.terminal, '毕业节点')}
  <text x="3075" y="386" text-anchor="middle" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="17">P210、P206 满级</text>
  ${connectors}
  ${Object.values(nodes).map((n) => nodeBox(n)).join('\n')}
  <text x="1980" y="200" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="19">爆发支线</text>
  <text x="1980" y="790" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="19">生存续航支线</text>`;

  return svgBase(
    3650,
    930,
    '个人科技树',
    '横向主干 → 双支线 → 合流；上下支线不互斥，升级即时生效并永久绑定玩家',
    body,
    '全树：14 个节点 · 53 个升级等级 · 79,000 个人代币 · 前期固定属性 15 级'
  );
}

function createGuildTree() {
  const nodes = {
    G101: { id: 'G101', coord: '(1,2)', name: '流程精简Ⅰ', lv: '最高 2 级', effect: '任务要求 -5%', cost: '总耗 3.2万', x: 110, y: 420, color: palette.task, w: 340 },
    G102: { id: 'G102', coord: '(2,1)', name: '任务协同Ⅰ', lv: '1 级', effect: '任务贡献 +2%', cost: '总耗 2万', x: 750, y: 305, color: palette.task, w: 340 },
    G103: { id: 'G103', coord: '(3,1)', name: '任务协同Ⅱ', lv: '1 级', effect: '任务贡献 +3%', cost: '总耗 2.5万', x: 1310, y: 305, color: palette.task, w: 340 },
    G104: { id: 'G104', coord: '(2,3)', name: '派遣统筹Ⅰ', lv: '1 级', effect: '派遣代币 +2%', cost: '总耗 2万', x: 750, y: 545, color: palette.dispatch, w: 340 },
    G105: { id: 'G105', coord: '(3,3)', name: '派遣统筹Ⅱ', lv: '1 级', effect: '派遣代币 +3%', cost: '总耗 2.5万', x: 1310, y: 545, color: palette.dispatch, w: 340 },
    G106: { id: 'G106', coord: '(4,2)', name: '调度扩充Ⅰ', lv: '1 级', effect: '免费刷新 +1', cost: '总耗 2.9万', x: 2100, y: 420, color: palette.dispatch, w: 340 },
    G107: { id: 'G107', coord: '(5,2)', name: '组织扩编Ⅰ', lv: '1 级', effect: '成员上限 +1', cost: '总耗 3.4万', x: 2930, y: 420, color: palette.org, w: 340 },

    G108: { id: 'G108', coord: '(6,1)', name: '任务协同Ⅲ', lv: '1 级', effect: '任务贡献 +2%', cost: '总耗 3.9万', x: 670, y: 880, color: palette.task, w: 340 },
    G109: { id: 'G109', coord: '(7,1)', name: '任务协同Ⅳ', lv: '1 级', effect: '任务贡献 +3%', cost: '总耗 4.4万', x: 1190, y: 880, color: palette.task, w: 340 },
    G110: { id: 'G110', coord: '(8,1)', name: '流程精简Ⅱ', lv: '最高 2 级', effect: '任务要求 -5%', cost: '总耗 10万', x: 1710, y: 880, color: palette.task, w: 340 },
    G111: { id: 'G111', coord: '(6,3)', name: '派遣统筹Ⅲ', lv: '1 级', effect: '派遣代币 +2%', cost: '总耗 3.9万', x: 670, y: 1110, color: palette.dispatch, w: 340 },
    G112: { id: 'G112', coord: '(7,3)', name: '派遣统筹Ⅳ', lv: '1 级', effect: '派遣代币 +3%', cost: '总耗 4.4万', x: 1190, y: 1110, color: palette.dispatch, w: 340 },
    G113: { id: 'G113', coord: '(8,3)', name: '调度扩充Ⅱ', lv: '1 级', effect: '免费刷新 +1', cost: '总耗 4.9万', x: 1710, y: 1110, color: palette.dispatch, w: 340 },
    G114: { id: 'G114', coord: '(9,2)', name: '流程精简Ⅲ', lv: '最高 2 级', effect: '任务要求 -5%', cost: '总耗 11万', x: 2280, y: 995, color: palette.task, w: 340 },
    G115: { id: 'G115', coord: '(10,2)', name: '管理扩编Ⅰ', lv: '1 级', effect: '副会长上限 +1', cost: '总耗 5.8万', x: 2820, y: 995, color: palette.org, w: 340 },
    G116: { id: 'G116', coord: '(11,2)', name: '组织扩编Ⅱ', lv: '1 级', effect: '成员上限 +1', cost: '总耗 6.3万', x: 3360, y: 995, color: palette.org, w: 340 },

    G117: { id: 'G117', coord: '(12,1)', name: '补给节流Ⅰ', lv: '最高 2 级', effect: '补给成本 -1500', cost: '总耗 13.8万', x: 500, y: 1460, color: palette.supply, w: 380 },
    G118: { id: 'G118', coord: '(13,1)', name: '补给强化Ⅰ', lv: '1 级', effect: '奖励升至等级1', cost: '总耗 7.3万', x: 980, y: 1460, color: palette.supply, w: 380 },
    G119: { id: 'G119', coord: '(14,1)', name: '补给节流Ⅱ', lv: '最高 2 级', effect: '补给成本 -1500', cost: '总耗 15.8万', x: 1460, y: 1460, color: palette.supply, w: 380 },
    G120: { id: 'G120', coord: '(15,1)', name: '补给强化Ⅱ', lv: '1 级', effect: '奖励升至等级2', cost: '总耗 8.2万', x: 1940, y: 1460, color: palette.supply, w: 380 },
    G121: { id: 'G121', coord: '(16,1)', name: '补给节流Ⅲ', lv: '最高 2 级', effect: '补给成本 -2000', cost: '总耗 17.6万', x: 2420, y: 1460, color: palette.supply, w: 380 },
    G122: { id: 'G122', coord: '(17,1)', name: '补给强化Ⅲ', lv: '1 级', effect: '奖励升至等级3', cost: '总耗 9.2万', x: 2900, y: 1460, color: palette.supply, w: 380 },
    G123: { id: 'G123', coord: '(12,3)', name: '商店议价Ⅰ', lv: '最高 2 级', effect: '白名单价格 -5%', cost: '总耗 13.8万', x: 500, y: 1740, color: palette.shop, w: 380 },
    G124: { id: 'G124', coord: '(13,3)', name: '采购扩容Ⅰ', lv: '1 级', effect: '周限购 +1', cost: '总耗 7.3万', x: 980, y: 1740, color: palette.shop, w: 380 },
    G125: { id: 'G125', coord: '(14,3)', name: '商店议价Ⅱ', lv: '最高 2 级', effect: '价格额外 -7%', cost: '总耗 15.8万', x: 1460, y: 1740, color: palette.shop, w: 380 },
    G126: { id: 'G126', coord: '(15,3)', name: '采购扩容Ⅱ', lv: '1 级', effect: '周限购 +1', cost: '总耗 8.2万', x: 1940, y: 1740, color: palette.shop, w: 380 },
    G127: { id: 'G127', coord: '(16,3)', name: '商店议价Ⅲ', lv: '最高 2 级', effect: '价格额外 -8%', cost: '总耗 17.6万', x: 2420, y: 1740, color: palette.shop, w: 380 },
    G128: { id: 'G128', coord: '(17,3)', name: '采购扩容Ⅲ', lv: '1 级', effect: '周限购 +1', cost: '总耗 9.2万', x: 2900, y: 1740, color: palette.shop, w: 380 },
    G129: { id: 'G129', coord: '(18,2)', name: '组织扩编Ⅲ', lv: '1 级', effect: '成员上限 +1', cost: '总耗 9.7万', x: 3470, y: 1600, color: palette.org, w: 340 },

    G130: { id: 'G130', coord: '(19,1)', name: '组织扩编Ⅳ', lv: '1 级', effect: '成员上限 +1', cost: '总耗 10.2万', x: 1000, y: 2220, color: palette.org, w: 360 },
    G131: { id: 'G131', coord: '(20,1)', name: '流程精简Ⅳ', lv: '最高 2 级', effect: '任务要求 -5%', cost: '总耗 21.6万', x: 1710, y: 2220, color: palette.task, w: 360 },
    G132: { id: 'G132', coord: '(19,3)', name: '管理扩编Ⅱ', lv: '1 级', effect: '副会长上限 +1', cost: '总耗 10.2万', x: 1000, y: 2460, color: palette.org, w: 360 },
    G133: { id: 'G133', coord: '(21,2)', name: '组织扩编Ⅴ', lv: '毕业节点', effect: '成员上限 +1', cost: '总耗 11.4万', x: 2730, y: 2340, color: palette.terminal, w: 420 },
  };

  const phaseStarts = {
    s1: { id: '', name: '', lv: '', effect: '', cost: '', x: 0, y: 0 },
    s2: { id: 'G107', name: '承接上一阶段', lv: '', effect: '', cost: '', x: 110, y: 995, color: palette.org, w: 340 },
    s3: { id: 'G116', name: '承接上一阶段', lv: '', effect: '', cost: '', x: 80, y: 1600, color: palette.org, w: 340 },
    s4: { id: 'G129', name: '承接上一阶段', lv: '', effect: '', cost: '', x: 150, y: 2340, color: palette.org, w: 340 },
  };

  const connectors = [
    connect(nodes.G101, nodes.G102), connect(nodes.G102, nodes.G103), connect(nodes.G103, nodes.G106),
    connect(nodes.G101, nodes.G104), connect(nodes.G104, nodes.G105), connect(nodes.G105, nodes.G106), connect(nodes.G106, nodes.G107),
    connect(phaseStarts.s2, nodes.G108), connect(nodes.G108, nodes.G109), connect(nodes.G109, nodes.G110), connect(nodes.G110, nodes.G114),
    connect(phaseStarts.s2, nodes.G111), connect(nodes.G111, nodes.G112), connect(nodes.G112, nodes.G113), connect(nodes.G113, nodes.G114),
    connect(nodes.G114, nodes.G115), connect(nodes.G115, nodes.G116),
    connect(phaseStarts.s3, nodes.G117), connect(nodes.G117, nodes.G118), connect(nodes.G118, nodes.G119), connect(nodes.G119, nodes.G120), connect(nodes.G120, nodes.G121), connect(nodes.G121, nodes.G122), connect(nodes.G122, nodes.G129),
    connect(phaseStarts.s3, nodes.G123), connect(nodes.G123, nodes.G124), connect(nodes.G124, nodes.G125), connect(nodes.G125, nodes.G126), connect(nodes.G126, nodes.G127), connect(nodes.G127, nodes.G128), connect(nodes.G128, nodes.G129),
    connect(phaseStarts.s4, nodes.G130), connect(nodes.G130, nodes.G131), connect(nodes.G131, nodes.G133),
    connect(phaseStarts.s4, nodes.G132), connect(nodes.G132, nodes.G133),
  ].join('\n');

  const body = `
  ${legendItem(80, 160, palette.task, '任务')}
  ${legendItem(250, 160, palette.dispatch, '派遣')}
  ${legendItem(420, 160, palette.supply, '补给')}
  ${legendItem(590, 160, palette.shop, '商店')}
  ${legendItem(760, 160, palette.org, '组织管理')}
  ${legendItem(1000, 160, palette.terminal, '毕业节点')}
  ${panel(60, 205, 3780, 540, '阶段 1｜任务与派遣起步', 'G101 → 双分支 → G106 合流 → G107')}
  ${panel(60, 780, 3780, 520, '阶段 2｜任务与派遣深化', '承接 G107 → 双分支 → G114 合流 → 管理与扩编')}
  ${panel(60, 1335, 3780, 650, '阶段 3｜补给与商店', '承接 G116 → 两条六节点长支线 → G129 合流')}
  ${panel(60, 2020, 3780, 650, '阶段 4｜组织毕业', '承接 G129 → 短双分支 → G133；毕业节点要求 G101～G132 全部满级')}
  ${connectors}
  ${Object.values(phaseStarts).filter((n) => n.id).map((n) => nodeBox(n, { h: 152 })).join('\n')}
  ${Object.values(nodes).map((n) => nodeBox(n)).join('\n')}
  <text x="2940" y="2310" fill="${palette.muted}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="19">前置：G101～G132 全部满级</text>`;

  return svgBase(
    3900,
    2740,
    '公会科技树',
    '横向推进；四段“短双分支 → 合流”结构。上下支线不互斥，科技无研究时间且不受公会等级限制',
    body,
    '全树：33 个节点 · 43 个升级等级 · 2,800,000 集体代币'
  );
}

async function main() {
  const target = process.env.TREE_TARGET;
  const files = [
    { base: 'personal-tech-tree', svg: createPersonalTree(), width: 3650, height: 930 },
    { base: 'guild-tech-tree', svg: createGuildTree(), width: 3900, height: 2740 },
  ].filter((file) => !target || file.base.startsWith(target));

  const browser = await chromium.launch({ headless: true, executablePath: process.env.BROWSER_PATH || undefined });
  try {
    for (const file of files) {
      const svgPath = path.join(outputDir, `${file.base}.svg`);
      const pngPath = path.join(outputDir, `${file.base}.png`);
      fs.writeFileSync(svgPath, file.svg.trimStart(), 'utf8');
      const page = await browser.newPage({ viewport: { width: file.width, height: file.height }, deviceScaleFactor: 1 });
      await page.setContent(`<style>html,body{margin:0;padding:0;background:#09111f;overflow:hidden}</style>${file.svg}`);
      await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: file.width, height: file.height } });
      await page.close();
      console.log(`${path.basename(pngPath)} ${file.width}x${file.height}`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
