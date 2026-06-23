@echo off
chcp 65001 >nul 2>nul
setlocal EnableExtensions EnableDelayedExpansion
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

where git >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Git was not found.
    pause
    exit /b 1
)

if not exist "%VGAME_DESIGN_ROOT%\.git" (
    echo [ERROR] Design repository not found: %VGAME_DESIGN_ROOT%
    echo Run the setup launcher first.
    pause
    exit /b 1
)

for /f %%C in ('git -C "%VGAME_DESIGN_ROOT%" status --porcelain 2^>nul ^| find /c /v ""') do set "DIRTY_COUNT=%%C"
if not "!DIRTY_COUNT!"=="0" (
    echo [ERROR] Design repository has local changes. Commit or stash them before updating.
    pause
    exit /b 1
)

git -C "%VGAME_DESIGN_ROOT%" pull --ff-only
if errorlevel 1 (
    echo [ERROR] Update failed. Resolve local changes or branch issues first.
    pause
    exit /b 1
)

echo [DONE] Design repository is up to date.
pause
exit /b 0
