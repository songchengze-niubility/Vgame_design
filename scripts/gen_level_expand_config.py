# -*- coding: utf-8 -*-
"""生成「主线关卡扩展配置表_初版结构.xlsx」，参照 chest_config.xlsx 的多 sheet 拆表 + 双表头 + 字段说明约定。
结构：关卡节点表(扩展) / 支线关卡表 / 支线奖励表 / 引导关卡表 / 房车演出表 / 字段说明 / 设计说明。
示例数据以「主线A→支线A'→主线B→小游戏B'→引导C'」拓扑填充。"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(os.path.dirname(REPO_ROOT), 'Output')
os.makedirs(OUT_DIR, exist_ok=True)

HDR1_FILL = PatternFill('solid', start_color='305496')
HDR1_FONT = Font(bold=True, color='FFFFFF')
HDR2_FILL = PatternFill('solid', start_color='8EA9DB')
HDR2_FONT = Font(bold=True, color='1F3864')
NOTE_FILL = PatternFill('solid', start_color='FFF2CC')
WRAP = Alignment(wrap_text=True, vertical='top')
TOP = Alignment(vertical='top', horizontal='left')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
THIN = Side(style='thin', color='BFBFBF')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

NODE_FIELDS = [
    ('node_id', 'int', '节点ID(全局唯一)', '20101'),
    ('chapter_id', 'int', '章节ID', '2'),
    ('node_type', 'enum', '节点类型', 'main / side / minigame / tutorial'),
    ('pos_x', 'int', '地图X坐标', '500'),
    ('pos_y', 'int', '地图Y坐标', '300'),
    ('parent_main_node_id', 'int', '旁挂节点依赖的主线节点ID(主线节点为空)', '20100'),
    ('is_count_progress', 'bool', '是否计入章节进度', 'main=true / 其余=false'),
    ('next_node', 'int', '下一节点ID(主线链路,旁挂节点为空)', '20102'),
    ('icon', 'string', '节点图标资源', 'icon_side'),
    ('level_ref_id', 'int', '关联关卡ID(主线→level.xlsx / 支线→side_id / 小游戏→game_id / 引导→tutorial_id)', '3001'),
    ('description', 'string', '描述', '支线A'),
]

SIDE_FIELDS = [
    ('side_id', 'int', '支线ID', '3001'),
    ('node_id', 'int', '对应地图节点ID(外键)', '20101'),
    ('story_id', 'string', '支线剧情ID', 'ST_CH2_SIDE_01'),
    ('recommend_power', 'int', '推荐战力', '12000'),
    ('vitality', 'int', '体力消耗', '10'),
    ('scene_path', 'string', '场景资源', 'scene_ch2_side_01'),
    ('first_reward_id', 'int', '首通奖励ID(引用SideReward)', '4001'),
    ('is_story_replay', 'bool', '是否允许重复复看剧情', 'true'),
    ('description', 'string', '说明', '第二章支线A'),
]

REWARD_FIELDS = [
    ('reward_id', 'int', '奖励ID', '4001'),
    ('side_id', 'int', '支线ID(外键)', '3001'),
    ('drop_group_id', 'string', '掉落组ID(独立配置,不复用主线Drop)', 'DG_SIDE_3001'),
    ('reward_tier', 'enum', '档位', 'standard / rich / scare'),
    ('description', 'string', '说明', '标准支线首通'),
]

TUTORIAL_FIELDS = [
    ('tutorial_id', 'int', '引导关ID', '5001'),
    ('node_id', 'int', '对应地图节点ID(外键)', '20103'),
    ('target_play_id', 'int', '教学目标玩法ID(引用小游戏game_id或系统ID)', '101'),
    ('force_first_trigger', 'bool', '是否首次强制触发', 'true'),
    ('vitality', 'int', '体力消耗', '0'),
    ('guide_ui_path', 'string', '引导UI资源(高亮/手势)', 'guide_gear_highlight'),
    ('is_replayable', 'bool', '是否可重复复习', 'true'),
    ('description', 'string', '说明', '齿轮啮合教学'),
]

TRANSITION_FIELDS = [
    ('transition_id', 'int', '演出ID', '6001'),
    ('from_node', 'int', '起始节点ID', '20100'),
    ('to_node', 'int', '目标节点ID', '20101'),
    ('mode', 'enum', '演出模式', 'move / flash'),
    ('duration', 'float', '时长(秒)', '0.8'),
    ('is_chapter_cross', 'bool', '是否章间切换', 'false'),
    ('skippable', 'bool', '是否可跳过', 'true'),
    ('description', 'string', '说明', '主线A→支线A'),
]

NODE_ROWS = [
    [20100, 2, 'main', 400, 300, None, True, 20102, 'icon_sword', 21010, '主线A(原有)'],
    [20101, 2, 'side', 500, 260, 20100, False, None, 'icon_side', 3001, '支线A'],
    [20102, 2, 'main', 600, 300, None, True, 20104, 'icon_sword', 21011, '主线B'],
    [20103, 2, 'minigame', 700, 260, 20102, False, None, 'icon_gear', 101, '小游戏B(齿轮啮合)'],
    [20104, 2, 'main', 800, 300, None, True, 20110, 'icon_sword', 21012, '主线C(Boss)'],
    [20105, 2, 'tutorial', 900, 260, 20104, False, None, 'icon_question', 5001, '引导C(齿轮教学)'],
]

SIDE_ROWS = [
    [3001, 20101, 'ST_CH2_SIDE_01', 12000, 10, 'scene_ch2_side_01', 4001, True, '第二章支线A'],
]

REWARD_ROWS = [
    [4001, 3001, 'DG_SIDE_3001', 'standard', '标准支线首通(≈主线同级80%)'],
]

TUTORIAL_ROWS = [
    [5001, 20105, 101, True, 0, 'guide_gear_highlight', True, '齿轮啮合教学(首次强制)'],
]

TRANSITION_ROWS = [
    [6001, 20100, 20101, 'move', 0.8, False, True, '主线A→支线A'],
    [6002, 20101, 20102, 'move', 0.8, False, True, '支线A→主线B'],
    [6003, 20102, 20103, 'move', 0.6, False, True, '主线B→小游戏B'],
    [6004, 20103, 20104, 'flash', 0.4, False, True, '小游戏B→主线C'],
    [6005, 20104, 20105, 'move', 0.6, False, True, '主线C→引导C'],
    [6006, 20104, 30100, 'flash', 0.8, True, True, '章末Boss→下章首关(章间黑屏+标题)'],
]

DESIGN_NOTES = [
    ('设计目标', '在现有主线节点链基础上扩展支线/小游戏/引导三类独立节点 + 节点间轻量房车演出，不破坏主线推进轴与首通经济。'),
    ('表关系', '关卡节点表(节点布局)按node_type分流:main→level.xlsx(原有);side→支线关卡表→支线奖励表;minigame→小游戏配置表(game_id);tutorial→引导关卡表。房车演出表FromNode/ToNode引用节点ID。'),
    ('节点拓扑', '三类新增节点为地图独立节点(旁挂在主线节点旁),非主线节点内分支。解锁依赖parent_main_node_id指向的主线节点通关。'),
    ('章节进度', 'is_count_progress控制是否计入章节进度:仅main=true,side/minigame/tutorial=false。进度公式不变,新增节点不污染主线进度。'),
    ('支线产出', '支线走独立SideReward配置,不复用主线Drop组。一次性首通产出,无重复产出。重复进入仅复看剧情(is_story_replay=true)。'),
    ('体力规则', 'main=10/side=10/minigame=0/tutorial=0。小游戏与引导免费,降低教学抵触与节奏调节门槛。'),
    ('房车演出', '仅move(直线平移+尾尘)与flash(淡入淡出+黑屏)两模式,轻量可跳过。章间用flash+略长黑屏+章节标题。不做复杂分镜。'),
    ('扩展约定', '新增节点只需在关卡节点表加行(node_id递增)并配置对应类型表+演出表,无需改表结构。node_type为分流键。'),
    ('示例填充', '以第二章「主线A→支线A→主线B→小游戏B(齿轮)→主线C(Boss)→引导C」拓扑填充范例。'),
    ('数值来源', '示例数值取自 design/主线关卡扩展-支线·小游戏·引导·节点演出Design Doc.md,md为单一事实源。'),
    ('后续待确认', 'node_id编号段是否与现有MainLevel.xlsx冲突;SideReward的drop_group_id是否复用通用Drop通道还是独立奖励发放器;引导关target_play_id是否需扩展到非小游戏系统。'),
]


def write_table_sheet(wb, name, fields, rows):
    ws = wb.create_sheet(name)
    for ci, (fkey, ftype, fdesc, fsample) in enumerate(fields, 1):
        c = ws.cell(row=1, column=ci, value=fdesc)
        c.fill = HDR1_FILL
        c.font = HDR1_FONT
        c.alignment = CENTER
        c.border = BORDER
        c2 = ws.cell(row=2, column=ci, value=fkey)
        c2.fill = HDR2_FILL
        c2.font = HDR2_FONT
        c2.alignment = CENTER
        c2.border = BORDER
        c3 = ws.cell(row=3, column=ci, value=f'类型: {ftype}')
        c3.fill = NOTE_FILL
        c3.font = Font(italic=True, size=9, color='7F6000')
        c3.alignment = CENTER
        c3.border = BORDER
    for ri, row in enumerate(rows, 4):
        for ci, val in enumerate(row, 1):
            c = ws.cell(row=ri, column=ci, value=val if val is not None else '')
            c.alignment = WRAP
            c.border = BORDER
    widths = []
    for ci, (fkey, ftype, fdesc, fsample) in enumerate(fields, 1):
        mx = max(len(fdesc), len(fkey), len(str(fsample)))
        for row in rows:
            v = row[ci - 1]
            if v is not None:
                for seg in str(v).split('\n'):
                    mx = max(mx, len(seg))
        widths.append(min(mx + 4, 42))
    for ci, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=ci).column_letter].width = w
    ws.freeze_panes = 'A4'
    return ws


def write_field_def_sheet(wb, tables):
    ws = wb.create_sheet('字段说明')
    hdr = ['表名', '字段名', '类型', '必填', '说明', '取值示例']
    for ci, h in enumerate(hdr, 1):
        c = ws.cell(row=1, column=ci, value=h)
        c.fill = HDR1_FILL
        c.font = HDR1_FONT
        c.alignment = CENTER
        c.border = BORDER
    r = 2
    required_keys = {'node_id', 'node_type', 'side_id', 'reward_id', 'tutorial_id',
                     'transition_id', 'story_id', 'from_node', 'to_node', 'mode'}
    for tname, fields in tables:
        for i, (fkey, ftype, fdesc, fsample) in enumerate(fields):
            required = '是' if fkey in required_keys else '条件'
            ws.cell(row=r, column=1, value=tname if i == 0 else '').alignment = TOP
            ws.cell(row=r, column=2, value=fkey).alignment = TOP
            ws.cell(row=r, column=3, value=ftype).alignment = CENTER
            ws.cell(row=r, column=4, value=required).alignment = CENTER
            ws.cell(row=r, column=5, value=fdesc).alignment = WRAP
            ws.cell(row=r, column=6, value=fsample).alignment = WRAP
            for ci in range(1, 7):
                ws.cell(row=r, column=ci).border = BORDER
            r += 1
    widths = [16, 22, 10, 8, 40, 34]
    for ci, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=ci).column_letter].width = w
    ws.freeze_panes = 'A2'


def write_design_notes_sheet(wb, notes):
    ws = wb.create_sheet('设计说明')
    for ci, h in enumerate(['项目', '说明'], 1):
        c = ws.cell(row=1, column=ci, value=h)
        c.fill = HDR1_FILL
        c.font = HDR1_FONT
        c.alignment = CENTER
        c.border = BORDER
    for ri, (k, v) in enumerate(notes, 2):
        ws.cell(row=ri, column=1, value=k).alignment = TOP
        ws.cell(row=ri, column=1).font = Font(bold=True)
        ws.cell(row=ri, column=2, value=v).alignment = WRAP
        for ci in range(1, 3):
            ws.cell(row=ri, column=ci).border = BORDER
        ws.row_dimensions[ri].height = max(28, min(90, len(v) // 3 + 16))
    ws.column_dimensions['A'].width = 16
    ws.column_dimensions['B'].width = 72
    ws.freeze_panes = 'A2'


def main():
    wb = Workbook()
    wb.remove(wb.active)
    write_table_sheet(wb, '关卡节点表(扩展)', NODE_FIELDS, NODE_ROWS)
    write_table_sheet(wb, '支线关卡表', SIDE_FIELDS, SIDE_ROWS)
    write_table_sheet(wb, '支线奖励表', REWARD_FIELDS, REWARD_ROWS)
    write_table_sheet(wb, '引导关卡表', TUTORIAL_FIELDS, TUTORIAL_ROWS)
    write_table_sheet(wb, '房车演出表', TRANSITION_FIELDS, TRANSITION_ROWS)
    write_field_def_sheet(wb, [
        ('关卡节点表(扩展)', NODE_FIELDS),
        ('支线关卡表', SIDE_FIELDS),
        ('支线奖励表', REWARD_FIELDS),
        ('引导关卡表', TUTORIAL_FIELDS),
        ('房车演出表', TRANSITION_FIELDS),
    ])
    write_design_notes_sheet(wb, DESIGN_NOTES)
    out = os.path.join(OUT_DIR, '主线关卡扩展配置表_初版结构.xlsx')
    wb.save(out)
    print(f'-> {os.path.basename(out)}')


if __name__ == '__main__':
    main()
