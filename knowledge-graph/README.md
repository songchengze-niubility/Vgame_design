# Vgame Knowledge Graph

## 定位

这里保存 Vgame 的只读事实索引：客户端代码结构、290 张配置表 Schema，以及本仓库的策划与治理文档。图谱用于定位证据和影响面，不替代真实 Excel、代码与项目 skill。

## 核心产物

| 文件 | 内容 |
|---|---|
| `config-schema.json` | 注册配置表、字段、类型、公式列、推断引用与 C# 扫描命中 |
| `design-docs.json` | Design、Proposal、Task、Plan、Harness 文档索引 |
| `knowledge-graph.json` | 统一图谱的仓库版本 |
| `.understand-anything/knowledge-graph.json` | UA Dashboard 使用的总图 |
| `.understand-anything/knowledge-graph-lite.json` | 排除函数节点后的精简图 |
| `.understand-anything/meta.json` | 节点、边、来源可用性与生成时间 |

## 数据来源

| 来源 | 路径 | 写入策略 |
|---|---|---|
| 配置表 | `${VGAME_CONFIG_DATAS}` | 只读 |
| 客户端图谱 | `${VGAME_CLIENT_GRAPH}` | 只读 |
| 策划文档 | 当前仓库约定目录 | 读取并生成索引 |

## 一键操作

首次使用先复制仓库根目录的 `local.env.example.bat` 为 `local.env.bat`，设置本机的 `VGAME_ROOT`。其他路径变量不设置时会从工程根目录推导。

- `更新知识图谱.bat`：全量重建并发布。
- `检查图谱状态.bat`：只读检查，不生成文件。
- `启动监控.bat`：监听来源变化后自动重建。
- `启动UA图谱.bat`：启动本地可视化；首次运行会安装前端依赖。

命令行等价操作：

```powershell
python scripts/build_vgame_graph.py --skip-cs-refs
python scripts/check_vgame_graph.py
python scripts/watch_vgame_graph.py --once
```

## AI 查询边界

- `depends_on` 当前可能由 `XxxId` 命名启发式推断，不能当作已确认外键。
- `safe_write_columns` 当前仅表示“未检测到公式”，其中可能包含 `Id`、`IsValid` 等关键控制字段。
- `cs_refs` 为有限模式扫描；零命中不代表没有代码使用。
- 修改真实配置前必须回到源 Excel，并读取对应项目 skill。

完整规则见 [KG-AI-RULES.md](KG-AI-RULES.md)，更新机制见 [知识图谱自动更新方案.md](知识图谱自动更新方案.md)。

## 与 Skill 的关系

| Skill | 图谱用途 |
|---|---|
| `vgame-config-schema` | 定位表、字段、公式与注册来源 |
| `vgame-reward-drop-sync` | 定位 Drop、UIlevel 与奖励引用链 |
| `vgame-config-quality-audit` | 查找跨表引用和潜在悬空关系 |
| `vgame-economy-source-map` | 扫描物品产出、消耗和表级入口 |
| `vgame-level-progression-map` | 定位 Level、Unlock、SystemOpen 与章节链 |
