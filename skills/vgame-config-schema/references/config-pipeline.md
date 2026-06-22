# Vgame 配置导出链路

## 源与生成物

| 类型 | 路径 | 说明 |
|---|---|---|
| 源 Excel | `D:\Vgame\Config\GameConfig\Datas` | 策划配置源。改配置优先改这里。 |
| 临时 Excel | `D:\Vgame\Config\GameConfig\TempDatas` | 导出时由脚本扁平复制生成。不要手工维护。 |
| 服务端 JSON | `D:\Vgame\Config\GameConfig\server_json` | Luban 生成物。只用于核对，不作为源表修改。 |
| 客户端工程 | `D:\Vgame\HorizonFlyProject` | 客户端代码、Lua、二进制配置输出目标。 |
| Luban 工具 | `D:\Vgame\Config\Tools\Luban\Luban.dll` | 由导出脚本调用。 |

## Luban 配置

`D:\Vgame\Config\GameConfig\luban.conf`：

- `schemaFiles`: `Defines`, `Datas/__tables__.xlsx`, `Datas/__beans__.xlsx`, `Datas/__enums__.xlsx`
- `dataDir`: `TempDatas`
- target `server`: groups `s`, topModule `cfg`
- target `client`: groups `c`, topModule `cfg`
- target `all`: groups `c,s,e`, topModule `config`

## 导出脚本行为

`scripts/export_excel.py` 会先把 `Datas` 下所有 `.xlsx/.xlsm` 扁平复制到 `TempDatas`，再调用 Luban。因为存在扁平复制，`__tables__.xlsx` 里的 input 文件名通常不带子目录。

关键路径来自 `scripts/path_config.py`：

- `EXCEL_DATA_PATH = D:\Vgame\Config\GameConfig\Datas`
- `EXCEL_TMP_DATA_PATH = D:\Vgame\Config\GameConfig\TempDatas`
- `SERVER_JSON_PATH = D:\Vgame\Config\GameConfig\server_json`
- `CLIENT_BYTES_PATH = D:\Vgame\HorizonFlyProject\Assets\GameResources\GameData\ExcelData`
- `CLIENT_LUA_PATH = D:\Vgame\HorizonFlyProject\LuaConfig`
- `LUA_CODE_PATH = D:\Vgame\HorizonFlyProject\Lua\Framework\ExcelData\Generated`

## 常用导出命令

在 `D:\Vgame\Config\GameConfig` 下执行：

```powershell
.\export_server.bat
.\export_client.bat
.\export_all.bat
```

对应脚本参数：

- server: `python scripts\export_excel.py --bat --mode s --full-check`
- client: `python scripts\export_excel.py --bat --mode c`
- all: `python scripts\export_excel.py --bat --mode cs --full-check`

## 操作原则

- 修改前确认源 Excel，不直接改 `server_json`。
- 变更 schema 前确认 `__tables__`、`__beans__`、`__enums__` 与生成代码影响。
- 导出失败时先看 `luban_errors.json`；校验失败时看 `check_rules_errors.json` 和 HTML report。
