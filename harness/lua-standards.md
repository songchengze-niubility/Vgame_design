# Lua Standards For Vgame

> **当前状态**：Vgame 客户端基于 C#/Unity，知识图谱中 1550 个客户端节点均为 C#。本文件为前瞻性占位规范，**当前未被任何实际代码使用**。若后续接入 Lua 热更新或脚本层，按本规范执行；若长期不接入，应删除本文件以避免误导。

## 命名

| 类型 | 规则 | 示例 |
|---|---|---|
| 模块文件 | PascalCase + `.lua` | `BattleMgr.lua` |
| 配置导出 | snake_case + `.lua` | `hero_skill.lua` |
| 函数 | camelCase | `calcDamage()` |
| 局部变量 | camelCase | `local heroList` |
| 常量 | UPPER_SNAKE_CASE | `local MAX_LEVEL = 100` |

## 模块结构

```lua
local M = {}

function M.init()
end

return M
```

## 基本约束

- 所有变量默认 `local`。
- 模块必须显式 `return M` 或返回清晰对象。
- 避免全局污染。
- 文件超过 500 行需要拆分或登记债务。
- 配置读取逻辑与战斗逻辑分层，不在战斗中硬编码表字段含义。

## 与配置表交互

- 不直接写死魔法 ID，优先引用枚举、常量或配置索引。
- 读取字段前确认 schema。
- 对缺失配置、空引用、非法 DropId/LevelId 给出明确错误。

