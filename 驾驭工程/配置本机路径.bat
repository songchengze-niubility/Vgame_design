@echo off
chcp 65001 >nul 2>nul
setlocal EnableExtensions EnableDelayedExpansion

set "HARNESS_COMMON="
for %%F in ("%~dp0_*.bat") do if not defined HARNESS_COMMON set "HARNESS_COMMON=%%~fF"
if not defined HARNESS_COMMON (
    echo [ERROR] Shared launcher configuration was not found.
    pause
    exit /b 1
)
call "%HARNESS_COMMON%"

echo.
echo ================================================================
echo   Vgame Local Path Configuration
echo ================================================================
echo Press Enter to keep the current value.
echo The design repository and harness paths follow this Git checkout.
echo.

echo Current Vgame project: %VGAME_ROOT%
set "INPUT_VALUE="
set /p "INPUT_VALUE=Vgame SVN root: "
if defined INPUT_VALUE for %%I in ("!INPUT_VALUE!") do set "VGAME_ROOT=%%~fI"
if not exist "!VGAME_ROOT!\Config\GameConfig\Datas\__tables__.xlsx" (
    echo [ERROR] Invalid Vgame project root: !VGAME_ROOT!
    pause
    exit /b 1
)

echo Current source docs: %VGAME_SOURCE_DOCS_ROOT%
set "INPUT_VALUE="
set /p "INPUT_VALUE=Source design documents root: "
if defined INPUT_VALUE for %%I in ("!INPUT_VALUE!") do set "VGAME_SOURCE_DOCS_ROOT=%%~fI"

echo Current output root: %VGAME_OUTPUT_ROOT%
set "INPUT_VALUE="
set /p "INPUT_VALUE=Personal output root: "
if defined INPUT_VALUE for %%I in ("!INPUT_VALUE!") do set "VGAME_OUTPUT_ROOT=%%~fI"

for %%I in ("%~dp0.") do set "VGAME_HARNESS_ROOT=%%~fI"
for %%I in ("%~dp0..") do set "VGAME_DESIGN_ROOT=%%~fI"
set "VGAME_CONFIG_DATAS=!VGAME_ROOT!\Config\GameConfig\Datas"
set "VGAME_CODE_ROOT=!VGAME_ROOT!\HorizonFlyProject\Packages\VGame"
set "VGAME_SKILL_ROOT=!VGAME_DESIGN_ROOT!\skills"
set "VGAME_CLIENT_GRAPH=!VGAME_DESIGN_ROOT!\knowledge-graph\client\knowledge-graph.json"

if not exist "%VGAME_HARNESS_USER_DIR%" mkdir "%VGAME_HARNESS_USER_DIR%"
call :write_config "%VGAME_HARNESS_USER_CONFIG%"
call :write_config "!VGAME_DESIGN_ROOT!\local.env.bat"

echo.
echo [DONE] Local paths were saved outside Git and SVN.
pause
exit /b 0

:write_config
(
    echo @echo off
    echo set "VGAME_ROOT=!VGAME_ROOT!"
    echo set "VGAME_DESIGN_ROOT=!VGAME_DESIGN_ROOT!"
    echo set "VGAME_HARNESS_ROOT=!VGAME_HARNESS_ROOT!"
    echo set "VGAME_DESIGN_REMOTE=!VGAME_DESIGN_REMOTE!"
    echo set "VGAME_DESIGN_BRANCH=!VGAME_DESIGN_BRANCH!"
    echo set "VGAME_CONFIG_DATAS=!VGAME_CONFIG_DATAS!"
    echo set "VGAME_CODE_ROOT=!VGAME_CODE_ROOT!"
    echo set "VGAME_SKILL_ROOT=!VGAME_SKILL_ROOT!"
    echo set "VGAME_CLIENT_GRAPH=!VGAME_CLIENT_GRAPH!"
    echo set "VGAME_SOURCE_DOCS_ROOT=!VGAME_SOURCE_DOCS_ROOT!"
    echo set "VGAME_OUTPUT_ROOT=!VGAME_OUTPUT_ROOT!"
) > "%~1"
exit /b 0
