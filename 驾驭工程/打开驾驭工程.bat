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

if not exist "%VGAME_DESIGN_ROOT%\.git" (
    echo [ERROR] Design repository not found: %VGAME_DESIGN_ROOT%
    echo Run the setup launcher first.
    pause
    exit /b 1
)

start "" explorer.exe "%VGAME_DESIGN_ROOT%"
exit /b 0
