# -*- coding: utf-8 -*-
"""
audit_economy_system_coverage.py — P4d 经济系统覆盖查漏

只读扫描正式配置与 v2 经济账本，判断是否还有经济相关系统未纳入 P4。
输出：
  - 经济/经济系统覆盖查漏报告.xlsx
  - 经济/_reports/P4d_经济系统覆盖查漏.md
"""
import io
import os
import re
import sys
import warnings
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ECONOMY_DIR = os.path.dirname(HERE)
V2_DIR = os.path.dirname(ECONOMY_DIR)
NUM_DIR = os.path.dirname(V2_DIR)
CONFIG_ROOT = os.environ.get("VGAME_CONFIG_DATAS", "")

SUMMARY = os.path.join(ECONOMY_DIR, "全资源产销总表.xlsx")
SOURCE_ECONOMY = os.path.join(NUM_DIR, "Vgame经济框架.xlsx")
REPORT_XLSX = os.path.join(ECONOMY_DIR, "经济系统覆盖查漏报告.xlsx")
REPORT_MD = os.path.join(ECONOMY_DIR, "_reports", "P4d_经济系统覆盖查漏.md")

ECONOMIC_RE = re.compile(
    r"(reward|drop|price|cost|consume|item|prop|num|pay|currency|vitality|exp|gain|chest|shop|resolve|craft|gift|mail|active|score|rank|lv|level)",
    re.I,
)

SYSTEM_AUDIT = [
    {
        "优先级": "P2",
        "系统": "月卡",
        "覆盖判定": "暂不纳入",
        "正式配置": "MonthCard/MonthCard.xlsx",
        "证据字段": "Price, PayProductId, CostItem, firstReward, dailyReward, TotalReward, PowerLimitUP",
        "当前P4状态": "用户裁决：当前阶段没有商业化内容，月卡不纳入 P4 经济层待办。",
        "风险": "未来若启用商业化，月卡长期投放会影响元晶、体力、抽卡券常态供给。",
        "建议动作": "商业化启动后再新增 `外循环_月卡` 模块；展开 firstReward/dailyReward Drop，并接 PayProducts。",
    },
    {
        "优先级": "P2",
        "系统": "付费商品/充值",
        "覆盖判定": "暂不纳入",
        "正式配置": "Pay/PayProducts.xlsx；Shop/ShopGoods.xlsx.PayProduct；Battlepass/BattlePass.xlsx.*PayProduct",
        "证据字段": "Price, ProductType, RelateId, PayProduct, BasicEditionPayProduct, AdvancedEditionPayProduct",
        "当前P4状态": "用户裁决：当前阶段没有商业化内容，付费商品/充值不纳入 P4 经济层待办。",
        "风险": "未来若启用商业化，需要校验付费礼包、通行证/月卡价格和奖励价值。",
        "建议动作": "商业化启动后再新增 `商业化_付费商品` 模块；PayProducts 作为付费主索引，反查 ShopGoods/BattlePass/MonthCard。",
    },
    {
        "优先级": "P2",
        "系统": "限时活动/活动奖励",
        "覆盖判定": "暂不纳入",
        "正式配置": "Activity/Activity.xlsx, ActiveReward.xlsx, DoubleDropActivity.xlsx, FourteenDayActivity.xlsx, Drop_TimeLimitedActivity.xlsx",
        "证据字段": "ActiveItemId, RewardId, DoubleCount, TaskList, Drop_TimeLimitedActivity",
        "当前P4状态": "用户裁决：当前阶段先不处理商业化/运营活动类内容。",
        "风险": "未来若启用活动，周期性投放和效率加成会改变经济供给。",
        "建议动作": "活动系统进入当前版本后，再新增 `外循环_活动` 模块并区分活动奖励、活动任务、双倍掉落倍率和限时 Drop。",
    },
    {
        "优先级": "P2",
        "系统": "邮件/预发奖励",
        "覆盖判定": "暂不纳入",
        "正式配置": "mail/PresendMail.xlsx, mail/Mail.xlsx",
        "证据字段": "Unlock, MailId, Drop, ExpirationTime",
        "当前P4状态": "用户裁决：当前阶段先不处理运营/预发类奖励。",
        "风险": "未来若启用预发、补偿或解锁邮件，可能形成大额非玩法投放。",
        "建议动作": "上线运营投放前再新增 `外循环_邮件` 模块并展开 PresendMail.Drop。",
    },
    {
        "优先级": "P2",
        "系统": "玩家等级升级奖励",
        "覆盖判定": "暂不纳入",
        "正式配置": "Player/PlayerLv.xlsx",
        "证据字段": "UpgradeCostExp, UpgradeGetPhy, UpgradeGetItem",
        "当前P4状态": "当前先不作为 P0 经济补强项；节奏层已生成等级曲线，经济层暂不展开升级返体力/道具。",
        "风险": "若 PlayerLv 的升级体力返还启用，会改变前期可玩时长和日资源入口。",
        "建议动作": "节奏层定稿后再决定是否新增 `外循环_玩家等级` 或并入节奏经济。",
    },
    {
        "优先级": "P0",
        "系统": "BOSS挑战正式配置",
        "覆盖判定": "已补强",
        "正式配置": "BossDungeon/Boss_Dungeon.xlsx",
        "证据字段": "LevelId, Reward, BestReward",
        "当前P4状态": "已读取正式 Boss_Dungeon 的 Reward/BestReward，并写入 `玩法_世界BOSS`/BOSS挑战追溯明细约 140 行。",
        "风险": "后续仍需在 Drop 展开链完成后校验奖励包内资源。",
        "建议动作": "保持正式表追溯；Drop 权重展开进入下一轮统一处理。",
    },
    {
        "优先级": "P0",
        "系统": "映射装备养成/分解/打孔/鉴定",
        "覆盖判定": "已补强",
        "正式配置": "SpecialEquipment/*.xlsx",
        "证据字段": "CostExp, IdentifyCost, IdentifyCostCurrency, HoleCost, HoleCostCurrency, ExtraItemList, EffectDrop",
        "当前P4状态": "已新增 `养成_映射装备` 模块，读取 LvUp/Quality/EffectDrop，覆盖升级经验、鉴定、打孔、额外道具和词条池入口约 452 行。",
        "风险": "后续仍需确认分解/生成是否有独立正式产销字段。",
        "建议动作": "保持 `养成_映射装备` 独立模块；下一轮只补确认为正式的分解/生成链。",
    },
    {
        "优先级": "P0",
        "系统": "旅券正式养成/分解/制作",
        "覆盖判定": "已补强",
        "正式配置": "strategy/*.xlsx, item_craft/StrategyCraft.xlsx, Shop/StrategyCardShop.xlsx",
        "证据字段": "UpgradeCostExp, ResolveGetItem, RandomCostItem, CostItem, FixMainAttrCostItem, CostCurrency, Price",
        "当前P4状态": "已扩展 `养成_旅券` 模块，读取 StrategyLv/StrategyResolve/StrategyCraft/StrategyCardShop，覆盖升级、分解、制作、商店兑换约 527 行。",
        "风险": "后续需结合 Drop 展开链确认随机制作产物与商店商品价值。",
        "建议动作": "保持正式表追溯；随机产物权重和商品价值进入下一轮统一处理。",
    },
    {
        "优先级": "P2",
        "系统": "宝箱/礼包/开箱",
        "覆盖判定": "暂不纳入",
        "正式配置": "valuablebox/Chest.xlsx, ValuableBox.xlsx, items/ItemChest.xlsx, Drop_GiftBox.xlsx",
        "证据字段": "ChestId, ItemId, NumMin, NumMax, Weight, DropId, ChestOpenMode",
        "当前P4状态": "当前先不作为 P0 经济补强项；礼包/宝箱类二级包等待活动与商业化口径明确后处理。",
        "风险": "未来若宝箱作为礼包、活动、任务奖励的二级包启用，会导致真实奖励低估。",
        "建议动作": "活动/礼包进入当前版本后再新增 `外循环_宝箱礼包` 模块。",
    },
    {
        "优先级": "P2",
        "系统": "通行证付费档/补差/买等级",
        "覆盖判定": "暂不纳入",
        "正式配置": "Battlepass/BattlePass.xlsx, BattlePassLevel.xlsx, BattlePassReward.xlsx",
        "证据字段": "BasicEditionPayProduct, BasicEditionCost, AdvancedEditionPayProduct, PayTheDifference*, AdvancedEditionAddLv",
        "当前P4状态": "通行证奖励线已覆盖较多；付费 SKU、补差和买等级属于当前未启用商业化口径，暂不处理。",
        "风险": "未来若启用通行证商业化，付费价值和付费获得等级会影响经济价值判断。",
        "建议动作": "商业化启动后再在 `外循环_通行证` 模块补付费商品、价格和经验/等级购买项。",
    },
    {
        "优先级": "P1",
        "系统": "竞技场连胜奖励",
        "覆盖判定": "已补强",
        "正式配置": "Arena/ArenaWinStreak.xlsx, ArenaWinStreakBonus.xlsx",
        "证据字段": "WinNum, DropId",
        "当前P4状态": "已读正式 ArenaWinStreak.DropId，登记为正式赛季累胜引用；ArenaWinStreakBonus 为竞技积分加成规则，不作为道具产销。",
        "风险": "连胜奖励是重复或阶段性竞技供给，可能影响竞技币/材料投放。",
        "建议动作": "真实包内容待 Drop 展开；如需竞技积分加成经济化，再单独评审 ArenaWinStreakBonus。",
    },
    {
        "优先级": "P1",
        "系统": "大秘境排行奖励",
        "覆盖判定": "已补强",
        "正式配置": "mythic_dungeon/SeasonRankReward.xlsx",
        "证据字段": "RankPer, Rank, DropId",
        "当前P4状态": "已读正式 SeasonRankReward.DropId，登记为正式赛季排行奖励引用。",
        "风险": "赛季排行奖励影响高端玩家长期投放和竞争驱动。",
        "建议动作": "真实包内容待 Drop 展开。",
    },
    {
        "优先级": "P1",
        "系统": "公会建设/议价/委托等级",
        "覆盖判定": "部分",
        "正式配置": "Guild/GuildBuilding.xlsx, GuildBargaining.xlsx, GuildComission.xlsx, GuildLv.xlsx",
        "证据字段": "Price, Reward, RandomReward, Exp, GuildWeeklyDropNum",
        "当前P4状态": "P4 记录了公会任务、派遣和公会商店；建设/议价/等级周掉落等未建完整链。",
        "风险": "公会集体资源、个人代币和周掉落可能存在额外产销。",
        "建议动作": "扩展 `外循环_商店公会` 或拆 `外循环_公会`。",
    },
    {
        "优先级": "P1",
        "系统": "角色技能/能效/额外奖励",
        "覆盖判定": "部分",
        "正式配置": "Hero/HeroSkillLv.xlsx, CalibrationPoints.xlsx, HeroEnergyEfficiencyMap.xlsx, HeroExtraReward.xlsx",
        "证据字段": "CostItem, MoneyCost, CosumeItem, CostCalibrationPoint, FirstReward, RepeatReward",
        "当前P4状态": "P4 覆盖角色升级/升阶/星盘/升星；技能升级、校准点/能效、角色重复额外奖励未覆盖。",
        "风险": "若这些是正式养成消耗，会低估角色养成刚性成本。",
        "建议动作": "确认能效/校准是否当前正式；若正式，补进 `养成_角色`。",
    },
    {
        "优先级": "P1",
        "系统": "专武分解/重复奖励",
        "覆盖判定": "部分",
        "正式配置": "ExclusiveWeapon/ExclWeaponResolve.xlsx, WeaponDuplicateReward.xlsx",
        "证据字段": "ResolveGetItem, FirstReward, RepeatReward",
        "当前P4状态": "P4 覆盖专武升级/突破/升星和抽卡重复转化的设计值；正式重复/分解表未展开。",
        "风险": "抽卡重复与分解返还影响专武系统回收率。",
        "建议动作": "补进 `养成_专武` 和 `抽卡_角色专武`。",
    },
    {
        "优先级": "P1",
        "系统": "任务旁支/见闻/系统引导任务",
        "覆盖判定": "部分",
        "正式配置": "task/Jottings.xlsx, JottingsTask.xlsx, SystemGuideTask.xlsx",
        "证据字段": "DropID, TaskId",
        "当前P4状态": "P4 覆盖每日/每周/阶段任务和 7日任务；正式旁支任务表未检查。",
        "风险": "一次性任务奖励可能漏入早期投放。",
        "建议动作": "补充 `外循环_任务` 正式任务族扫描。",
    },
    {
        "优先级": "P1",
        "系统": "章节任务/章节星级正式表",
        "覆盖判定": "部分",
        "正式配置": "level/ChapterStarReward.xlsx, ChapterTasks.xlsx",
        "证据字段": "ChapterId, Star, DropId, TaskIdList",
        "当前P4状态": "P4 从设计页登记主线星级奖励；未用正式表逐章校验。",
        "风险": "主线一次性奖励可能和正式配置不同。",
        "建议动作": "补进 `玩法_主线` 的正式配置强校验。",
    },
    {
        "优先级": "P1",
        "系统": "抽卡正式卡池/保底/概率",
        "覆盖判定": "部分",
        "正式配置": "Activity/DrawCard/*.xlsx, Drop_draw.xlsx",
        "证据字段": "DropId, TenDropId, OnePrice, TenPrice, Pool, DrawWeight, XiaoBaoDiTriggerNum, DaBaoDiTriggerNum",
        "当前P4状态": "P4 只记录 150 钻价值锚点和重复转化；正式 OnePrice 是抽卡券，概率池未展开。",
        "风险": "抽卡是最高敏感经济系统，价格/保底/概率都未完整入账。",
        "建议动作": "升级 `抽卡_角色专武` 模块，以正式 DrawCard/Drop_draw 为主。",
    },
    {
        "优先级": "P1",
        "系统": "正式关卡/UIlevel奖励包",
        "覆盖判定": "部分",
        "正式配置": "level/level.xlsx, UIlevel.xlsx",
        "证据字段": "FirstReward, FallReward, FirstRewardDrop, FallRewardDrop, ThreeStarRewardDrop, HighRewardDrop, Vitality",
        "当前P4状态": "P4 用设计页产销；P4c 已指出主线/资源本/旅券本/映射本缺 LevelId/DropId 主键。",
        "风险": "玩法实际体力消耗和 Drop 奖励可能和设计页不一致。",
        "建议动作": "补 LevelId/LevelType 映射后按正式 UIlevel/level 强校验。",
    },
    {
        "优先级": "P0",
        "系统": "无限挑战（无限之旅）/neural_roam",
        "覆盖判定": "已并入",
        "正式配置": "neural_roam/NR_HighestScoreReward.xlsx, NR_RankReward.xlsx, NR_Layer.xlsx",
        "证据字段": "Score, DropId, Gain, BattlePointGain",
        "当前P4状态": "用户确认 neural_roam = 无限挑战（无限之旅）；已并入 `玩法_无限挑战`，读取 NR_HighestScoreReward 与 NR_Layer 约 891 行，NR_RankReward 当前 DropId 为空。",
        "风险": "后续若 RankReward 配置 DropId，需要补入排行奖励链。",
        "建议动作": "继续归入 `玩法_无限挑战`；RankReward 出现有效 DropId 后再补追溯。",
    },
    {
        "优先级": "P1",
        "系统": "WorldMap探索/声望/采集/小游戏",
        "覆盖判定": "待确认",
        "正式配置": "WorldMap/*.xlsx",
        "证据字段": "GainList, DropId, ConsumeItem, CostExp, OutputNum, WorldScheduleReward.Drop",
        "当前P4状态": "P4 没有 WorldMap 模块；核心口径未把它列为当前正式经济层。",
        "风险": "如果世界地图探索正式上线，会漏声望、采集、宝箱、小游戏奖励。",
        "建议动作": "请确认 WorldMap 是否本版本正式经济系统；若是，新增 `玩法_世界地图`。",
    },
    {
        "优先级": "P2",
        "系统": "旧装备/equipment",
        "覆盖判定": "待确认/可能不纳入",
        "正式配置": "equipment/*.xlsx",
        "证据字段": "UpgradeCostExp, ItemConsume, ResolveGetItem, StarCostItem",
        "当前P4状态": "未覆盖；核心口径将旧主角装备本/宝石本/铭文本视为非正式或已删除，但正式表仍在。",
        "风险": "若客户端仍消费旧装备表，会漏旧装备养成成本。",
        "建议动作": "确认 equipment 是否已废弃；若未废弃，拆成旧装备养成模块。",
    },
    {
        "优先级": "P2",
        "系统": "Rouge/Rogue肉鸽",
        "覆盖判定": "不纳入",
        "正式配置": "Rogue/*.xlsx, level/Rouge/*.xlsx",
        "证据字段": "rewardList, FirstDrop, FallDrop, Price, RougeReward",
        "当前P4状态": "经济源表 `肉鸽（废弃）` 已标不纳入；正式配置仍残留两套肉鸽表。",
        "风险": "只有在复活肉鸽玩法时才影响经济层。",
        "建议动作": "继续不纳入；如版本恢复肉鸽，再单独建模块。",
    },
    {
        "优先级": "P2",
        "系统": "展示/索引类道具表",
        "覆盖判定": "不作为产销源",
        "正式配置": "items/Items.xlsx, ItemAccess.xlsx, TopAssets.xlsx, ItemSweep.xlsx, ItemChest.xlsx",
        "证据字段": "AccessList, ShowItemIds, ItemId, ChestId",
        "当前P4状态": "Items 已用于 ItemId 校验；AccessList/TopAssets 不是实际产出。",
        "风险": "容易把展示途径误当来源。",
        "建议动作": "只保留为校验索引；ItemChest 归入宝箱展开链。",
    },
]


def clean(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return value


def header_values(ws, row_idx, max_probe=256):
    values = []
    last = 0
    for row in ws.iter_rows(min_row=row_idx, max_row=row_idx, max_col=max_probe, values_only=True):
        for col, value in enumerate(row, start=1):
            value = clean(value)
            values.append(value)
            if value != "":
                last = col
        break
    return values[:last]


def scan_formal_tables():
    rows = []
    for dirpath, _dirs, files in os.walk(CONFIG_ROOT):
        for name in sorted(files):
            lower = name.lower()
            if not lower.endswith(".xlsx") or lower.startswith("~$") or ".bak" in lower or name.startswith("__"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, CONFIG_ROOT).replace("\\", "/")
            try:
                wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            except Exception as exc:
                rows.append({
                    "相对路径": rel,
                    "页签": "",
                    "行数": "",
                    "列数": "",
                    "经济字段": "",
                    "字段/注释命中": "读取失败: %s" % exc,
                    "目录": rel.split("/")[0],
                })
                continue
            for sheet in wb.sheetnames[:3]:
                ws = wb[sheet]
                headers = header_values(ws, 1, 256)
                types = header_values(ws, 2, 256)
                comments = header_values(ws, 4, 256)
                text = " ".join(str(x) for x in headers + types + comments + [rel])
                eco_headers = [str(h) for h in headers if h and ECONOMIC_RE.search(str(h))]
                if eco_headers or ECONOMIC_RE.search(text):
                    rows.append({
                        "相对路径": rel,
                        "页签": sheet,
                        "行数": ws.max_row,
                        "列数": ws.max_column,
                        "经济字段": ", ".join(eco_headers[:30]),
                        "字段/注释命中": text[:500],
                        "目录": rel.split("/")[0],
                    })
            wb.close()
    return rows


def load_current_coverage():
    coverage = []
    sources = set()
    systems = set()
    if not os.path.exists(SUMMARY):
        return coverage, sources, systems
    wb = openpyxl.load_workbook(SUMMARY, read_only=True, data_only=True)
    if "覆盖状态" in wb.sheetnames:
        ws = wb["覆盖状态"]
        headers = [clean(c.value) for c in next(ws.iter_rows(min_row=1, max_row=1))]
        for row in ws.iter_rows(min_row=2, values_only=True):
            d = {headers[i]: clean(row[i]) if i < len(row) else "" for i in range(len(headers))}
            if d.get("页签"):
                coverage.append(d)
    if "追溯_全明细" in wb.sheetnames:
        ws = wb["追溯_全明细"]
        headers = [clean(c.value) for c in next(ws.iter_rows(min_row=1, max_row=1))]
        idx = {h: i for i, h in enumerate(headers)}
        for row in ws.iter_rows(min_row=2, values_only=True):
            src = clean(row[idx["来源页"]]) if "来源页" in idx else ""
            sys_name = clean(row[idx["系统"]]) if "系统" in idx else ""
            if src:
                sources.add(src)
            if sys_name:
                systems.add(sys_name)
    wb.close()
    return coverage, sources, systems


def load_design_sheets():
    if not os.path.exists(SOURCE_ECONOMY):
        return []
    wb = openpyxl.load_workbook(SOURCE_ECONOMY, read_only=True, data_only=True)
    rows = [{"页签": s, "行数": wb[s].max_row, "列数": wb[s].max_column} for s in wb.sheetnames]
    wb.close()
    return rows


def write_xlsx(formal_rows, coverage_rows, design_rows, sources, systems):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "结论"
    ws.append(["P4d 经济系统覆盖查漏"])
    ws.cell(1, 1).font = Font(bold=True, size=14)
    ws.append([])
    ws.append(["正式配置根", CONFIG_ROOT])
    ws.append(["当前P4来源页数", len(sources)])
    ws.append(["当前P4系统数", len(systems)])
    ws.append(["自动扫描命中经济字段表/页", len(formal_rows)])
    ws.append(["系统级漏项/部分覆盖项", len(SYSTEM_AUDIT)])
    counts = Counter(row["覆盖判定"] for row in SYSTEM_AUDIT)
    ws.append([])
    ws.append(["覆盖判定", "数量"])
    for key, count in counts.most_common():
        ws.append([key, count])

    def add_sheet(name, headers, rows):
        s = wb.create_sheet(name)
        s.append(headers)
        for cell in s[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="D9E1F2")
            cell.alignment = Alignment(horizontal="center")
        for row in rows:
            s.append([row.get(h, "") for h in headers])
        s.freeze_panes = "A2"
        widths = [12, 18, 18, 36, 44, 44, 44, 48]
        for i, width in enumerate(widths[:len(headers)], start=1):
            s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
        for r in s.iter_rows():
            for cell in r:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        return s

    add_sheet("系统级查漏", ["优先级", "系统", "覆盖判定", "正式配置", "证据字段", "当前P4状态", "风险", "建议动作"], SYSTEM_AUDIT)
    add_sheet("正式配置自动扫描", ["目录", "相对路径", "页签", "行数", "列数", "经济字段", "字段/注释命中"], formal_rows)
    add_sheet("当前P4覆盖状态", ["页签", "行数", "列数", "处理状态", "说明"], coverage_rows)
    add_sheet("经济源页签全集", ["页签", "行数", "列数"], design_rows)
    add_sheet("当前P4来源页", ["来源页"], [{"来源页": s} for s in sorted(sources)])
    add_sheet("当前P4系统", ["系统"], [{"系统": s} for s in sorted(systems)])
    wb.save(REPORT_XLSX)


def write_md(formal_rows, _coverage_rows, _design_rows, sources, systems):
    os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
    counts = Counter(row["覆盖判定"] for row in SYSTEM_AUDIT)
    priority_counts = Counter(row["优先级"] for row in SYSTEM_AUDIT)
    dir_counts = Counter(row["目录"] for row in formal_rows)

    lines = [
        "# P4d · 经济系统覆盖查漏",
        "",
        "> 目标：从正式配置全集反查 P4 经济层是否漏系统。只读正式配置，不修改 SVN 配置。",
        "",
        "## 结论",
        "",
        f"- 正式配置根: `{CONFIG_ROOT}`",
        f"- 当前 P4 来源页: {len(sources)} 个；系统: {len(systems)} 个。",
        f"- 自动扫描命中经济字段的正式表/页: {len(formal_rows)} 条。",
        f"- 系统级判定项: {len(SYSTEM_AUDIT)} 条。",
        f"- Excel 报告: `{REPORT_XLSX}`",
        "",
        "| 覆盖判定 | 数量 |",
        "|---|---:|",
    ]
    for key, count in counts.most_common():
        lines.append(f"| {key} | {count} |")
    lines += ["", "| 优先级 | 数量 |", "|---|---:|"]
    for key, count in sorted(priority_counts.items()):
        lines.append(f"| {key} | {count} |")

    lines += [
        "",
        "## 需要补的系统",
        "",
        "| 优先级 | 系统 | 判定 | 关键正式配置 | 建议 |",
        "|---|---|---|---|---|",
    ]
    for row in SYSTEM_AUDIT:
        if row["覆盖判定"] in ("漏", "部分", "待确认"):
            lines.append("| {优先级} | {系统} | {覆盖判定} | `{正式配置}` | {建议动作} |".format(**row))

    lines += [
        "",
        "## 已补强/已并入",
        "",
        "| 系统 | 判定 | 当前记录 | 后续边界 |",
        "|---|---|---|---|",
    ]
    for row in SYSTEM_AUDIT:
        if row["覆盖判定"] in ("已补强", "已并入"):
            lines.append("| {系统} | {覆盖判定} | {当前P4状态} | {建议动作} |".format(**row))

    lines += [
        "",
        "## 暂不纳入/只作索引",
        "",
        "| 系统 | 判定 | 原因 |",
        "|---|---|---|",
    ]
    for row in SYSTEM_AUDIT:
        if row["覆盖判定"] in ("暂不纳入", "不纳入", "不作为产销源", "待确认/可能不纳入"):
            lines.append("| {系统} | {覆盖判定} | {当前P4状态} |".format(**row))

    lines += ["", "## 自动扫描命中最多的目录", "", "| 目录 | 命中表/页数 |", "|---|---:|"]
    for dirname, count in dir_counts.most_common(25):
        lines.append(f"| {dirname} | {count} |")

    lines += [
        "",
        "## 本轮边界",
        "",
        "- 这是系统覆盖查漏，不直接判断每个数值是否合理。",
        "- 字段自动扫描会包含部分战斗/展示/旧系统误报，所以最终以 `系统级查漏` 页的人工分级为准。",
        "- `Rogue/level/Rouge` 已按当前项目口径暂不纳入；如果后续恢复肉鸽，需要单独建经济模块。",
        "- `Items/ItemAccess/TopAssets` 只作索引和展示途径，不直接当真实来源。",
    ]
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    coverage_rows, sources, systems = load_current_coverage()
    design_rows = load_design_sheets()
    formal_rows = scan_formal_tables()
    write_xlsx(formal_rows, coverage_rows, design_rows, sources, systems)
    write_md(formal_rows, coverage_rows, design_rows, sources, systems)
    print("经济系统覆盖查漏完成")
    print("[报告Excel] %s" % REPORT_XLSX)
    print("[报告MD] %s" % REPORT_MD)
    print("系统级判定: %s" % " / ".join("%s=%s" % (k, v) for k, v in Counter(row["覆盖判定"] for row in SYSTEM_AUDIT).most_common()))


if __name__ == "__main__":
    main()
