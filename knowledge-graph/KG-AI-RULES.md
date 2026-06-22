# Vgame 知识图谱 AI 查询规则

> 涉及项目事实时，图谱用于定位证据，不替代真实配置表、代码和专项 skill 的最终确认。

## 硬约束

1. 先查 `knowledge-graph/.understand-anything/knowledge-graph.json` 定位节点和关联。
2. 涉及配置字段时，再查 `config-schema.json` 与真实 Excel 表头。
3. `depends_on` 可能来自字段名推断，只能作为导航线索，不能直接视为已确认外键。
4. `cs_refs` 只表示扫描命中；没有命中不等于客户端没有使用该表。
5. 图谱中的 `safe_write_columns` 当前仅表示“未发现公式”，不代表业务上允许直接写入。
6. 修改奖励、关卡、角色或经济配置时，仍须路由到对应 Vgame 专项 skill。
7. 未经用户明确要求，不修改 `${VGAME_ROOT}` 下的真实配置表与项目代码。

## 查询顺序

| 场景 | 第一入口 | 二次确认 |
|---|---|---|
| 配置表字段与引用 | `config-schema.json` | 源 Excel、`__tables__.xlsx` |
| 系统与代码结构 | 统一总图的 client 节点 | 客户端源代码 |
| 策划规则与变更背景 | 统一总图的 design 节点 | `design/`、`proposals/`、项目 skill |
| 跨系统影响 | 节点的一跳边与 layer | 各源文件逐项核实 |

## 置信度口径

- **高**：真实源文件明确声明，或多个独立来源一致。
- **中**：代码扫描、注册表或稳定命名规则命中。
- **低**：字段名、相似度或语义推断；输出时必须标注“待确认”。

## 图谱入口

- Dashboard 总图：`knowledge-graph/.understand-anything/knowledge-graph.json`
- Dashboard 精简图：`knowledge-graph/.understand-anything/knowledge-graph-lite.json`
- 配置表 Schema：`knowledge-graph/config-schema.json`
- 设计文档图谱：`knowledge-graph/design-docs.json`
- 生成元数据：`knowledge-graph/.understand-anything/meta.json`
