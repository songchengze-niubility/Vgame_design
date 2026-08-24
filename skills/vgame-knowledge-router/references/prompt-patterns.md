# 路由提问与结果解读

## 典型提问

| 用户问题 | 自动档位 | 预期检索范围 |
|---|---|---|
| `Vgame 有哪些战斗外养成系统？` | `quick` | 项目/目录层；不读系统详情、契约或证据 |
| `主线如何解锁系统，改奖励会影响哪些契约？` | `design` | 最多 3 个相关系统详情与 5 个共享契约 |
| `核验当前主线 UIlevel 与 Drop 奖励字段，证据在哪里？` | `audit` | 最多 3 个系统、5 个契约、5 个证据 |
| `这个系统现在是否已经在 LIVE？` | `audit` | 环境/版本/发布证据；工作副本不足时必须回答 `UNKNOWN` |

## 命令模板

自动判断并输出 Markdown：

```powershell
python skills/vgame-knowledge-router/scripts/route_query.py "主线如何解锁系统，改奖励会影响哪些契约？"
```

输出 JSON：

```powershell
python skills/vgame-knowledge-router/scripts/route_query.py "核验当前主线 UIlevel 与 Drop 奖励字段" --format json
```

显式覆盖档位：

```powershell
python skills/vgame-knowledge-router/scripts/route_query.py "主线" --profile design
```

## 结果字段

- `profile`：本次检索深度，不代表事实可信度。
- `systems`：命中的系统。`detailLevel=full` 才可能读取明确的 `detailRef`；`summary` 只允许使用 manifest 摘要。
- `contracts`：跨系统共享规则；保留原有 `provenance`。
- `evidence`：仅在 `audit` 中出现，是下一步允许回源的证据元数据，最多 5 条。
- `readPlan`：实际阅读顺序；不要自行扩展为目录扫描。
- `unknowns`：知识缺口、摘要限制或 LIVE 边界。
- `safety`：固定的来源与读取边界。
- `diagnostics`：说明分类命中和脚本是否枚举详情目录；正常值应为 `systemDetailsDirectoryEnumerated: false`。

## 正确使用摘要系统

摘要系统可以回答：

- 这个系统在框架中的名称、分组和一句话职责。
- manifest 已明确列出的关系、状态和 ID。

摘要系统不能回答：

- 完整流程、公式、字段、异常分支、UI 细节。
- 具体当前值或上线状态。
- manifest 未提供的证据路径。

遇到这些问题时，写明 `UNKNOWN` 或“当前仅有摘要”，并提出需要补充的权威文档/配置/代码证据。

## 禁止模式

- 使用通配符或递归遍历 `system-details/`。
- 为了“看起来完整”而读取所有系统详情。
- 为 `detailLevel=summary` 的系统虚构规则或证据。
- 把本机 SVN 工作副本、配置镜像或设计提案称为 Production/LIVE 事实。
- 超过 3 个系统、5 个契约或 5 个证据的默认硬上限。
- 把路由分数或命中词当作业务结论。
