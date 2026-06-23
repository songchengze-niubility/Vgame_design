@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ================================================================
echo   Vgame 驾驭工程 — 一键安装
echo ================================================================
echo.

:: ============================================================
:: Step 1: 检查 Git
:: ============================================================
echo [1/6] 检查 Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git，请先安装 Git: https://git-scm.com/downloads
    pause
    exit /b 1
)
for /f "tokens=3" %%v in ('git --version') do echo   Git: %%v

:: ============================================================
:: Step 2: 检查 Python
:: ============================================================
echo [2/6] 检查 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+: https://python.org/downloads
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo   Python: %%v

:: ============================================================
:: Step 3: 安装 openpyxl
:: ============================================================
echo [3/6] 检查 openpyxl...
python -c "import openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo   openpyxl 未安装，正在安装...
    pip install openpyxl >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] openpyxl 安装失败，请手动运行: pip install openpyxl
        pause
        exit /b 1
    )
    echo   openpyxl 安装完成
) else (
    echo   openpyxl 已安装
)

:: ============================================================
:: Step 4: 生成 local.env.bat
:: ============================================================
echo [4/6] 配置本地路径...
if exist local.env.bat (
    echo   local.env.bat 已存在，跳过
) else (
    echo   正在生成 local.env.bat...
    :: 尝试自动检测 Vgame 路径
    set "DETECTED_ROOT="
    if exist "D:\Vgame" set "DETECTED_ROOT=D:\Vgame"
    if exist "E:\Vgame" set "DETECTED_ROOT=E:\Vgame"
    if exist "C:\Vgame" set "DETECTED_ROOT=C:\Vgame"

    if defined DETECTED_ROOT (
        echo   检测到 Vgame 目录: !DETECTED_ROOT!
        (
            echo set "VGAME_ROOT=!DETECTED_ROOT!"
            echo set "VGAME_CONFIG_DATAS=!DETECTED_ROOT!\Config\GameConfig\Datas"
        ) > local.env.bat
        echo   local.env.bat 已生成
    ) else (
        echo   [提示] 未自动检测到 Vgame 目录
        echo   请手动编辑 local.env.bat，填入你的本机路径：
        echo     set "VGAME_ROOT=你的Vgame路径"
        echo     set "VGAME_CONFIG_DATAS=你的Vgame路径\Config\GameConfig\Datas"
        (
            echo set "VGAME_ROOT=请修改为你的路径"
            echo set "VGAME_CONFIG_DATAS=请修改为你的路径\Config\GameConfig\Datas"
        ) > local.env.bat
    )
)

:: ============================================================
:: Step 5: 验证知识图谱
:: ============================================================
echo [5/6] 验证知识图谱...
if exist "knowledge-graph\config-schema.json" (
    for %%F in ("knowledge-graph\config-schema.json") do echo   config-schema.json: %%~zF bytes
) else (
    echo   [警告] config-schema.json 不存在
)

if exist "knowledge-graph\knowledge-graph.json" (
    for %%F in ("knowledge-graph\knowledge-graph.json") do echo   knowledge-graph.json: %%~zF bytes
) else (
    echo   [警告] knowledge-graph.json 不存在
)

:: ============================================================
:: Step 6: 运行门禁检查
:: ============================================================
echo [6/6] 运行门禁检查...
powershell -ExecutionPolicy Bypass -File scripts\check.ps1 >nul 2>&1
if %errorlevel% equ 0 (
    echo   门禁检查通过
) else (
    echo   [提示] 门禁检查有告警，可稍后处理
)

:: ============================================================
:: 完成
:: ============================================================
echo.
echo ================================================================
echo   安装完成！
echo ================================================================
echo.
echo   下一步：
echo   1. 双击 新人上手指南.html 了解如何使用
echo   2. 用 OpenCode 打开此目录，AI 会自动加载 Skills
echo   3. 需要查配置表？直接问 AI：帮我查 XXX 表的字段
echo   4. 需要写设计？问 AI：帮我写一份 XXX 系统的 Design Doc
echo.
echo   常用命令：
echo     更新知识图谱:  双击 knowledge-graph\更新知识图谱.bat
echo     门禁检查:      powershell -ExecutionPolicy Bypass -File scripts\check.ps1
echo.
pause
