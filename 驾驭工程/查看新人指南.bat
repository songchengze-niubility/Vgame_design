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

if not exist "%VGAME_DESIGN_ROOT%\BEGINNER-GUIDE.html" (
    echo [ERROR] Beginner guide was not found. Run the setup launcher first.
    pause
    exit /b 1
)

start "" "%VGAME_DESIGN_ROOT%\BEGINNER-GUIDE.html"
exit /b 0
