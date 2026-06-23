@echo off
chcp 65001 >nul 2>nul
setlocal EnableExtensions
set "HARNESS_COMMON="
for %%F in ("%~dp0_*.bat") do (
    if not defined HARNESS_COMMON set "HARNESS_COMMON=%%~fF"
)
if not defined HARNESS_COMMON (
    echo [ERROR] Shared launcher configuration was not found.
    pause
    exit /b 1
)
call "%HARNESS_COMMON%"

if not exist "%VGAME_DESIGN_ROOT%\knowledge-graph" (
    echo [ERROR] Knowledge graph directory not found. Run the setup launcher first.
    pause
    exit /b 1
)

set "UA_STARTER="
for %%F in ("%VGAME_DESIGN_ROOT%\knowledge-graph\*UA*.bat") do (
    if not defined UA_STARTER set "UA_STARTER=%%~fF"
)

if not defined UA_STARTER (
    echo [ERROR] UA dashboard launcher was not found.
    pause
    exit /b 1
)

call "%UA_STARTER%"
exit /b %errorlevel%
