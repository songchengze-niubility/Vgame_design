# -*- coding: utf-8 -*-
"""生成「小游戏配置表_初版结构.xlsx」，参照 chest_config.xlsx 的多 sheet 拆表 + 双表头 + 字段说明约定。
结构：小游戏类型表 / 小游戏关卡表 / 小游戏参数表 / 小游戏评价表 / 字段说明 / 设计说明。
示例数据以「齿轮啮合」填充完整，其余玩法在类型表中给出基础行，关/参/评表按同结构扩展。"""
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

TYPES = [
    ('game_id', 'int', '小游戏ID', '101'),
    ('game_name', 'string', '玩法名称', '齿轮啮合'),
    ('game_category', 'enum', '玩法分类', 'reaction反应 / puzzle益智 / casual休闲'),
    ('scene_bg', 'string', '场景背景资源', 'scene_engine_room'),
    ('enter_icon', 'string', '分支节点图标', 'icon_gear'),
    ('enter_desc', 'string', '进入提示文案', '可跳过'),
    ('is_skippable', 'bool', '是否可跳过', 'true'),
    ('repeatable', 'bool', '是否可重复游玩', 'true'),
    ('time_per_play', 'string', '单局预估时长', '1-2分钟'),
    ('reward_module_id', 'string', '奖励模块ID(引用评价表)', 'MG_REWARD_101'),
    ('logic_module', 'string', '逻辑模块名', 'MiniGame_Gear'),
    ('description', 'string', '描述', '齿轮传动链拼装益智'),
]

LEVELS = [
    ('level_id', 'int', '关卡ID(全局唯一)', '10101'),
    ('game_id', 'int', '小游戏ID(外键)', '101'),
    ('level_no', 'int', '等级(1~5)', '1'),
    ('level_name', 'string', '等级名', '入门/初级/中级/高级/挑战'),
    ('time_limit', 'int', '时限(秒)', '30'),
    ('target_score', 'int', '目标分数(空=按通关/存活)', ' '),
    ('capacity', 'string', '容量(空位数/星点数/网格规模)', '2空位'),
    ('material_count', 'int', '备选元素数', '3'),
    ('new_element', 'string', '新增要素描述', '仅尺寸匹配'),
    ('survival_time', 'int', '存活目标时间(秒,沙尘用)', ' '),
    ('description', 'string', '说明', '入门关'),
]

PARAMS = [
    ('param_id', 'int', '参数ID', '1'),
    ('game_id', 'int', '小游戏ID(外键)', '101'),
    ('level_no', 'int', '等级(0=全局)', '0'),
    ('param_key', 'string', '参数键', 'gear_size'),
    ('param_value', 'string', '参数值', '小8齿40px;中12齿60px;大16齿80px'),
    ('remark', 'string', '备注', '齿轮尺寸定义'),
]

GRADES = [
    ('grade_id', 'int', '评价ID', '10101'),
    ('game_id', 'int', '小游戏ID(外键)', '101'),
    ('grade', 'enum', '档位', 'S/A/B/C'),
    ('condition', 'string', '达成条件', '零失误且剩余时间>50%'),
    ('score_threshold', 'string', '分数阈值(空=按条件)', ' '),
    ('reward_group_id', 'string', '奖励掉落组ID(引用Drop系统)', 'DG_MG_101_S'),
    ('is_floor', 'bool', '是否保底(C级)', 'false'),
    ('description', 'string', '说明', 'S档'),
]

TYPE_ROWS = [
    [101, '齿轮啮合', 'puzzle', 'scene_engine_room', 'icon_gear', '可跳过', True, True, '1-2分钟', 'MG_REWARD_101', 'MiniGame_Gear', '齿轮传动链拼装益智'],
    [102, '元能切割', 'reaction', 'scene_fruit_orchard', 'icon_blade', '可跳过', True, True, '1分钟', 'MG_REWARD_102', 'MiniGame_Slice', '切水果式反应玩法'],
    [103, '薯片接食物', 'casual', 'scene_campground', 'icon_samoyed', '可跳过', True, True, '1分钟', 'MG_REWARD_103', 'MiniGame_Catch', '休闲接物玩法'],
    [104, '沙尘躲避', 'reaction', 'scene_desert_storm', 'icon_storm', '可跳过', True, True, '1-2分钟', 'MG_REWARD_104', 'MiniGame_Dodge', '反应躲避玩法'],
    [105, '信号解码', 'puzzle', 'scene_cockpit_radio', 'icon_radio', '可跳过', True, True, '1-3分钟', 'MG_REWARD_105', 'MiniGame_Decode', '密码推理益智'],
    [106, '货物整理', 'puzzle', 'scene_storage', 'icon_cargo', '可跳过', True, True, '1-3分钟', 'MG_REWARD_106', 'MiniGame_Pack', '俄罗斯方块变体装箱'],
    [107, '元能管线拼接', 'puzzle', 'scene_chassis', 'icon_pipe', '可跳过', True, True, '1-3分钟', 'MG_REWARD_107', 'MiniGame_Pipe', '水管工式管道拼接'],
    [108, '星图连线', 'casual', 'scene_night_sky', 'icon_constellation', '可跳过', True, True, '1-3分钟', 'MG_REWARD_108', 'MiniGame_Star', '一笔画连线益智'],
]

LEVEL_ROWS = [
    [10101, 101, 1, '入门', 30, None, '2空位', 3, '仅尺寸匹配(大小相邻交替)', None, '无转向要求'],
    [10102, 101, 2, '初级', 40, None, '3空位', 5, '加入转向约束(输出必顺时针)', None, '需计算奇偶关系'],
    [10103, 101, 3, '中级', 55, None, '4空位', 7, '损坏齿轮干扰+传动比(转速匹配)', None, '损坏齿轮红色裂纹'],
    [10104, 101, 4, '高级', 70, None, '5空位', 9, '双层齿轮(同轴传动)+路线分叉', None, ''],
    [10105, 101, 5, '挑战', 80, None, '6空位', 11, '全部要素+磨损倒计时(15s)', None, '需磨损前完成搭建'],
]

PARAM_ROWS = [
    [1, 101, 0, 'gear_size', '小8齿40px;中12齿60px;大16齿80px', '齿轮尺寸定义'],
    [2, 101, 0, 'speed_rule', '大带小×1.5;小带大×0.67;同尺寸禁用', '传动比规则'],
    [3, 101, 0, 'direction_rule', '相邻齿轮转向必反(奇数位顺/偶数位逆)', '转向规则'],
    [4, 101, 0, 'penalty_size_error', '弹出+扣1s', '尺寸错误惩罚'],
    [5, 101, 0, 'penalty_broken', '卡住2s+扣5s', '损坏齿轮惩罚'],
    [6, 101, 0, 'score_formula', '基础100+剩余时间×5+零失误150+完美传动50', '得分计算'],
    [7, 101, 0, 'wear_countdown', '15s', 'Lv.5磨损倒计时'],
]

GRADE_ROWS = [
    [10101, 101, 'S', '零失误且剩余时间>50%', None, 'DG_MG_101_S', False, '最高档'],
    [10102, 101, 'A', '≤1失误通关', None, 'DG_MG_101_A', False, ''],
    [10103, 101, 'B', '通关', None, 'DG_MG_101_B', False, ''],
    [10104, 101, 'C', '超时未通关', None, 'DG_MG_101_C', True, '保底给奖励'],
]

DESIGN_NOTES = [
    ('设计目标', '为8个章节过渡小游戏提供统一配置骨架，支撑进入/关卡/数值/评价/奖励的可配置化。'),
    ('表关系', '类型表(1)─(N)关卡表；类型表(1)─(N)参数表；类型表(1)─(N)评价表；评价表(N)─(1)Drop掉落组(复用现有Drop系统)。'),
    ('注册源', '类型表 game_id 需在 level.xlsx 的 LevelType=小游戏分支 行中引用；UIlevel.xlsx 配置进入节点图标与跳过UI。'),
    ('与 level.xlsx 关系', '主线关卡内分支节点 LevelType 标记为小游戏分支，MinLevelId 字段指向具体小游戏的起始 level_id。'),
    ('与 Drop 系统关系', '评价表 reward_group_id 引用现有掉落组体系(DG_xxx)，奖励发放走统一 Drop 通道，不单独建奖励表。'),
    ('参数表用途', '承载各玩法特有数值(KV)，避免主表字段爆炸。level_no=0 表示该玩法全局参数，>0 表示某等级专属参数覆盖。'),
    ('扩展约定', '新增小游戏只需在类型表加一行(game_id 递增)，并在关卡/参数/评价表按 game_id 补充配置，无需改表结构。'),
    ('示例填充', '本表以「齿轮啮合(game_id=101)」完整填充关卡/参数/评价作为范例；其余8个玩法类型表已给出基础行，关/参/评表按同结构补全。'),
    ('数值来源', '示例数值取自 design/小游戏-齿轮啮合Design Doc.md，md 为单一事实源，配置表数值变更需先回流 md。'),
    ('后续待确认', 'game_id 编号段是否与现有 level.xlsx ID 体系冲突；reward_group_id 是否复用通用Drop组还是新建小游戏专属组。'),
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
        widths.append(min(mx + 4, 40))
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
    for tname, fields in tables:
        for i, (fkey, ftype, fdesc, fsample) in enumerate(fields):
            required = '是' if fkey in ('game_id', 'level_id', 'grade_id', 'param_id', 'game_name', 'grade') else '条件'
            ws.cell(row=r, column=1, value=tname if i == 0 else '').alignment = TOP
            ws.cell(row=r, column=2, value=fkey).alignment = TOP
            ws.cell(row=r, column=3, value=ftype).alignment = CENTER
            ws.cell(row=r, column=4, value=required).alignment = CENTER
            ws.cell(row=r, column=5, value=fdesc).alignment = WRAP
            ws.cell(row=r, column=6, value=fsample).alignment = WRAP
            for ci in range(1, 7):
                ws.cell(row=r, column=ci).border = BORDER
            r += 1
    widths = [16, 22, 10, 8, 34, 34]
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
        ws.row_dimensions[ri].height = max(28, min(80, len(v) // 3 + 16))
    ws.column_dimensions['A'].width = 16
    ws.column_dimensions['B'].width = 70
    ws.freeze_panes = 'A2'


def main():
    wb = Workbook()
    wb.remove(wb.active)
    write_table_sheet(wb, '小游戏类型表', TYPES, TYPE_ROWS)
    write_table_sheet(wb, '小游戏关卡表', LEVELS, LEVEL_ROWS)
    write_table_sheet(wb, '小游戏参数表', PARAMS, PARAM_ROWS)
    write_table_sheet(wb, '小游戏评价表', GRADES, GRADE_ROWS)
    write_field_def_sheet(wb, [
        ('小游戏类型表', TYPES),
        ('小游戏关卡表', LEVELS),
        ('小游戏参数表', PARAMS),
        ('小游戏评价表', GRADES),
    ])
    write_design_notes_sheet(wb, DESIGN_NOTES)
    out = os.path.join(OUT_DIR, '小游戏配置表_初版结构.xlsx')
    wb.save(out)
    print(f'-> {os.path.basename(out)}')


if __name__ == '__main__':
    main()
