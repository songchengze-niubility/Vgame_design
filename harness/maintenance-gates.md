# Maintenance Gates

## 运行方式

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```

## 初版检查项

| 检查 | 级别 | 说明 |
|---|---|---|
| 入口文件存在 | FAIL | `AGENTS.md`、`CLAUDE.md`、`ARCHITECTURE.md` 等不能缺 |
| 核心目录存在 | FAIL | `harness/`、`design/`、`proposals/`、`tasks/` 等不能缺 |
| 模板存在 | FAIL | Design、Proposal、Task 模板不能缺 |
| 待办标记扫描 | WARN | 新待办需要登记到 `tech-debt-tracker.md` |
| 大文档扫描 | WARN | 超大文档需要拆分或索引化 |
| 真实配置误提交 | WARN | `.xlsx`、`.xlsm`、`.csv` 需要确认是否只是样例 |
| Skill 根目录检查 | WARN | 缺失时提示，不阻断本仓库维护 |

## 扩展方向

- 校验 Vgame skill 的 `SKILL.md` 与 references 完整性。
- 校验 `config.toml` skill 路由是否存在。
- 接入 `__tables__.xlsx` 注册源表扫描。
- 对 DropId、LevelId、Unlock、UIlevel 引用做只读闭环审查。
- 对角色强度产物做表头、字体、标杆偏差校验。
