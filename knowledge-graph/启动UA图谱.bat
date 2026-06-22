@echo off
chcp 65001 >nul
setlocal

set "UA_ROOT=%~dp0understand-anything-new"
set "GRAPH_DIR=%~dp0"

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 20+
    pause
    exit /b 1
)

where corepack >nul 2>nul
if errorlevel 1 (
    echo [ERROR] 未找到 corepack，无法准备 pnpm
    pause
    exit /b 1
)

cd /d "%UA_ROOT%"
if not exist "node_modules" (
    echo [SETUP] 首次启动，正在安装 Dashboard 依赖...
    call corepack pnpm@10.6.2 install --frozen-lockfile --ignore-scripts
    if errorlevel 1 (
        echo [ERROR] Dashboard 依赖安装失败
        pause
        exit /b 1
    )
)

if not exist "understand-anything-plugin\packages\core\dist\schema.js" (
    echo [SETUP] 正在构建 Dashboard 核心包...
    call corepack pnpm@10.6.2 --filter @understand-anything/core build
    if errorlevel 1 (
        echo [ERROR] Dashboard 核心包构建失败
        pause
        exit /b 1
    )
)

echo [START] 浏览器将自动打开带临时访问令牌的本地页面。
call corepack pnpm@10.6.2 --filter @understand-anything/dashboard dev
pause
