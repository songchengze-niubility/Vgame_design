# Lua Standards For Vgame

本文件参考 TKL harness 的 Lua 约束，作为 Vgame 后续接入客户端脚本或热更新代码时的默认规范。若 Vgame 实际技术栈不同，以真实工程为准，并更新本文件。

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

