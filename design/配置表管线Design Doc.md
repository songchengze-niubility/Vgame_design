# 配置表管线 — Design Doc

## 元信息
| 项 | 内容 |
|----|------|
| 功能名称 | 配置表管线（Config Pipeline） |
| 作者 | 反推整理 |
| 创建日期 | 2026-06-19 |
| 状态 | `Draft` |
| 风险档位 | HIGH |
| 关联 Proposal | — |

## 背景与目标
### 背景
Vgame 使用 Luban 工具链管理配置表管线。Excel 源文件（`D:\Vgame\Config\GameConfig\Datas\`）采用 4 行头格式（##var / ##type / ##group / ##），通过 `__tables__.xlsx` 注册逻辑表名到物理文件的映射。Luban 工具将 Excel 编译为 server_json 目录下的 JSON 和 C# 代码。部分逻辑表合并多个 Excel 文件（如 Drop = 8 个文件）。Excel 为唯一数据源，生成的 JSON 不作为直接编辑对象。公式列（ID / DropId / DropId2）有安全保护。

### 目标
- 规范配置表的添加、修改、导出全流程
- 明确 Excel 源文件格式要求和注册机制
- 定义 Luban 导出的验证步骤与安全规则
- 确保公式列不被误写导致数据损坏

### 非目标
- Luban 工具本身的编译原理
- 服务器端配置热更新机制
- 单个表格的业务逻辑详解

## 核心规则

### R-01: Excel 源文件格式规范
- **触发条件**：策划新建或修改配置表 Excel 时
- **前置限制**：使用 Luban 兼容的 Excel 格式
- **操作流程**：
  1. Excel 文件存放于 `Config\GameConfig\Datas\` 目录
  2. 前 4 行为 Luban 头部：
     - 第 1 行（`##var`）：字段名（snake_case 或 PascalCase）
     - 第 2 行（`##type`）：字段类型（int / float / string / enum / bean 等）
     - 第 3 行（`##group`）：分组标签（可选，分组导出用）
     - 第 4 行（`##`）：注释/描述行
  3. 第 5 行起为数据行
  4. 每行必须有主键列（通常命名为 Id）
- **状态变化**：Excel 保存 → 等待 Luban 导出
- **资源变化**：Excel 文件更新
- **UI 反馈**：无（Excel 内操作）
- **异常边界**：头部行格式错误 → Luban 导出时报错并给出具体行号；主键为空或重复 → Luban 导出时警告/报错
- **落地点**：`Config\GameConfig\Datas\*.xlsx`

### R-02: __tables__.xlsx 注册机制
- **触发条件**：新增逻辑表时必须在 `__tables__.xlsx` 中注册
- **前置限制**：Excel 源文件已创建且格式正确
- **操作流程**：
  1. 在 `__tables__.xlsx` 中添加一行，设置逻辑表名（如 "Skill"、"Drop"）和对应的源 Excel 文件名
  2. 一个逻辑表可映射多个 Excel 文件（如 Drop = Drop1.xlsx + Drop2.xlsx + ... 共 8 个），Luban 自动合并
  3. 修改已有逻辑表的源文件列表时同步更新注册
- **状态变化**：注册表更新 → Luban 重建映射
- **资源变化**：`__tables__.xlsx` 文件变更
- **UI 反馈**：无
- **异常边界**：注册的源文件不存在 → Luban 导出报错；逻辑表名重复 → 后者覆盖前者，导出警告
- **落地点**：`Config\GameConfig\Datas\__tables__.xlsx`

### R-03: Luban 导出流程
- **触发条件**：策划完成配置编辑后执行导出
- **前置限制**：Luban 工具链已安装，Excel 文件格式无误
- **操作流程**：
  1. 执行 Luban 编译命令 → Luban 解析 `__tables__.xlsx` 获取所有表映射
  2. 逐表解析 Excel → 验证 4 行头格式、类型一致性、主键唯一性
  3. 生成输出：
     - `server_json\*.json`：运行时读取的 JSON 数据
     - 生成的 C# 代码：强类型访问类（反序列化 + 查询方法）
  4. 枚举（`__enums__.xlsx`）和 Bean（`__beans__.xlsx`）同时编译
- **状态变化**：Excel → Luban 编译 → JSON + C# 代码生成
- **资源变化**：server_json 目录中 JSON 文件更新，C# 生成代码文件更新
- **UI 反馈**：Luban 命令行输出编译进度和错误信息
- **异常边界**：编译失败时回滚上次成功的导出（不写入不完整的 JSON）；类型不匹配报错并给出字段名
- **落地点**：`Config\GameConfig\server_json\`（输出目录）

### R-04: 生成 JSON 的使用规则
- **触发条件**：运行时加载配置数据时
- **前置限制**：Luban 导出成功，JSON 文件已部署
- **操作流程**：游戏启动/关卡加载时 → Luban 生成的 C# 反序列化类读取 JSON → 构造强类型数据对象 → 提供查询 API（如 `Tables.Instance.TbSkill.Get(skillId)`）
- **状态变化**：JSON 文件 → 内存中的配置字典
- **资源变化**：内存中加载配置数据
- **UI 反馈**：无
- **异常边界**：JSON 文件缺失 → 启动时报错并使用兜底空表；JSON 解析失败 → 报错并回退到空表，不崩溃
- **落地点**：`Config\GameConfig\server_json\` → `Tables.Instance`

### R-05: 公式列安全保护
- **触发条件**：任何涉及 Drop 表公式列（ID / DropId / DropId2）的修改操作时
- **前置限制**：已明确标识哪些列包含 Excel 公式
- **操作流程**：
  1. Drop 表中的 ID、DropId、DropId2 列为 Excel 公式列（包含自动计算逻辑）
  2. 策划/脚本 **绝不直接写入或覆盖** 这些列的公式
  3. 修改数据时仅编辑公式依赖的源列
  4. vgame-config-quality-audit 脚本校验：检查公式列是否存在硬编码值替代公式的情况
- **状态变化**：无
- **资源变化**：公式列自动重新计算
- **UI 反馈**：Excel 内公式自动更新值
- **异常边界**：公式列被误写为常量 → audit 脚本检测并报错；公式依赖的源列修改导致公式错误 → audit 脚本检测 #REF! 等 Excel 错误
- **落地点**：`Drop*.xlsx` 公式列 → `vgame-config-quality-audit` 脚本定期检查

### R-06: 枚举与 Bean 管理
- **触发条件**：新增/修改枚举值或复合数据结构时
- **前置限制**：无
- **操作流程**：
  - `__enums__.xlsx`：定义所有枚举类型和值。修改后 Luban 重新生成 C# 枚举类
  - `__beans__.xlsx`：定义 Bean（复合结构体），供其他 Excel 表引用为字段类型。修改后 Luban 重新生成 C# Bean 类
  - 使用枚举/Bean 的 Excel 表需在 Luban 头部第 2 行正确标注类型名
- **状态变化**：Excel → Luban → 重新生成枚举/Bean C# 代码
- **资源变化**：生成的 C# 枚举文件和 Bean 类文件更新
- **UI 反馈**：Luban 输出中显示枚举/Bean 编译状态
- **异常边界**：枚举值被引用但已被删除 → Luban 报引用错误；Bean 字段类型与引用处不一致 → 编译时类型检查报错
- **落地点**：`__enums__.xlsx` / `__beans__.xlsx` → `Config\GameConfig\server_json\`

### R-07: 质量审计与验证
- **触发条件**：Luban 导出完成后、配置提交至版本控制前
- **前置限制**：Luban 编译已通过（无语法错误）
- **操作流程**：
  1. Luban 编译检查：自动检查格式、类型、主键唯一性
  2. vgame-config-quality-audit 脚本：业务逻辑校验，包括公式列安全、外键引用完整性、数值范围合理性
  3. 审计通过 → 允许提交配置变更
  4. 审计失败 → 输出详细错误报告 → 修复后重新审计
- **状态变化**：Luban 通过 → Audit 通过 → Ready for Commit
- **资源变化**：审计报告（错误列表 / 通过标记）
- **UI 反馈**：审计脚本输出带颜色标记的检查结果（绿色通过 / 红色失败 + 具体行号）
- **异常边界**：审计脚本本身崩溃 → 配置未审计不阻塞提交但发出强警告；外键引用指向不存在的表 → 标记为必须修复
- **落地点**：`Luban compile` → `vgame-config-quality-audit` 脚本
