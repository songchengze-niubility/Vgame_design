# Vgame 驾驭工程使用说明

## 这套仓库解决什么

`Vgame_design` 是策划 Agent 的项目总控仓库。它把设计规则、提案、任务、项目 skill 和知识图谱接成一条可追踪链路，但不替代 `${VGAME_ROOT}` 中的真实项目与配置表。

## 标准工作流

完整图文版见 [`驾驭工程使用说明.html`](驾驭工程使用说明.html)。正式功能交付使用“项目适配 Step 0 + 九步流程”：

```text
Step 0  挂载 Vgame 项目适配层
Step 1  任务登记与参考选择
Step 2  需求契约与范围确认
Step 3  逐条澄清与决策冻结
Step 4  核心设计
Step 5  按需专项设计
Step 6  一致性评审与规则冻结
Step 7  UI 资产制作
Step 8  正式 Excel
Step 9  追踪、校验与用户验收
```

只读分析和建议任务走最小路径，不为了流程完整而强制制造 UI、Excel 或中间文档。

## 常用入口

| 需求 | 入口 |
|---|---|
| 快速了解项目与路由 | `AGENTS.md` |
| 新系统设计 | `design/TEMPLATE.md` |
| 形成可评审方案 | `proposals/TEMPLATE.md` |
| 拆执行任务 | `tasks/TEMPLATE.md` |
| 查配置表与代码关系 | `knowledge-graph/启动UA图谱.bat` |
| 更新图谱 | `knowledge-graph/更新知识图谱.bat` |
| 运行仓库门禁 | `scripts/check.ps1` |
| 检查策划文档 | `scripts/doc-check.ps1` |

## 本机路径配置

仓库不保存任何成员的盘符。首次使用时复制 `local.env.example.bat` 为 `local.env.bat`，并按本机情况设置：

```bat
set "VGAME_ROOT=<游戏工程根目录>"
set "VGAME_CONFIG_DATAS=<配置表 Datas 目录>"
set "VGAME_CLIENT_GRAPH=<客户端 knowledge-graph.json>"
set "VGAME_CODE_ROOT=<需要扫描的客户端代码目录>"
set "VGAME_SKILL_ROOT=<Vgame 项目 skill 目录>"
```

只有 `VGAME_ROOT` 是基础变量，其余变量不填时会从它推导。`local.env.bat` 已加入 `.gitignore`，不会上传个人路径。

## AI 正确使用方式

1. 先从 `AGENTS.md` 判断任务类型和专项 skill。
2. 用图谱缩小来源范围，不直接把推断边当结论。
3. 回到真实表、代码或设计文档核实关键事实。
4. 输出中区分事实、推断、经验权重和待确认项。
5. 未获明确授权时，只读分析 `${VGAME_ROOT}`。

## 图谱日常维护

- 配置表新增、删除或改字段后：运行一次全量更新。
- 仅新增策划文档时：监控器会自动增量触发，也可手工更新。
- Dashboard 首次启动需要联网安装前端依赖，之后可离线运行。
- 图谱异常时先运行 `检查图谱状态.bat`，再看 `meta.json` 的来源可用性。

## 提交前

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
powershell -ExecutionPolicy Bypass -File scripts/doc-check.ps1
python scripts/check_vgame_graph.py
```

真实配置和代码的跨仓改动还要登记到 `CROSS-REPO-CHANGES.md`。
