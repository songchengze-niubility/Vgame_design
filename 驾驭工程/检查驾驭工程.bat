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

if not exist "%VGAME_DESIGN_ROOT%\scripts\check.ps1" (
    echo [ERROR] Harness checks were not found. Run the setup launcher first.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%VGAME_DESIGN_ROOT%\scripts\check.ps1"
if errorlevel 1 goto :failed

python "%VGAME_DESIGN_ROOT%\scripts\check_vgame_graph.py"
if errorlevel 1 goto :failed

echo [DONE] Checks completed. Review any WARN messages above.
pause
exit /b 0

:failed
echo [ERROR] One or more checks failed.
pause
exit /b 1
