@echo off
setlocal EnableExtensions

set "UA_ROOT=%~dp0understand-anything-new"
set "GRAPH_DIR=%~dp0"
set "DASHBOARD_VITE=understand-anything-plugin\packages\dashboard\node_modules\.bin\vite.cmd"
set "CORE_SCHEMA=understand-anything-plugin\packages\core\dist\schema.js"

where node >nul 2>nul
if errorlevel 1 goto :missing_node

where corepack >nul 2>nul
if errorlevel 1 goto :missing_corepack

if not exist "%UA_ROOT%\package.json" goto :missing_source
cd /d "%UA_ROOT%"

if not exist "%DASHBOARD_VITE%" (
    echo [SETUP] Installing dashboard dependencies...
    call corepack pnpm@10.6.2 install --frozen-lockfile --ignore-scripts
    if errorlevel 1 goto :install_failed
)

if not exist "%CORE_SCHEMA%" (
    echo [SETUP] Building dashboard core package...
    call corepack pnpm@10.6.2 --filter @understand-anything/core build
    if errorlevel 1 goto :build_failed
)

echo [START] Opening the Vgame knowledge graph dashboard...
echo [INFO] Keep this window open. Press Ctrl+C to stop.
call corepack pnpm@10.6.2 --filter @understand-anything/dashboard dev
exit /b %errorlevel%

:missing_node
echo [ERROR] Node.js was not found. Install Node.js 20 or newer.
goto :failed

:missing_corepack
echo [ERROR] Corepack was not found. Reinstall or repair Node.js.
goto :failed

:missing_source
echo [ERROR] Dashboard source was not found: %UA_ROOT%
goto :failed

:install_failed
echo [ERROR] Dashboard dependency installation failed.
goto :failed

:build_failed
echo [ERROR] Dashboard core build failed.
goto :failed

:failed
pause
exit /b 1
