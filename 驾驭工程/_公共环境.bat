@echo off
set "VGAME_HARNESS_DIR=%~dp0"
for %%I in ("%~dp0.") do set "VGAME_HARNESS_ROOT=%%~fI"
for %%I in ("%~dp0..") do set "VGAME_DESIGN_ROOT=%%~fI"
for %%I in ("%VGAME_DESIGN_ROOT%\..\Vgame") do set "VGAME_DEFAULT_ROOT=%%~fI"

set "VGAME_DESIGN_REMOTE=git@code.dobest.com:spark/Vgame_design.git"
set "VGAME_DESIGN_BRANCH=master"
set "VGAME_HARNESS_USER_DIR=%LOCALAPPDATA%\Vgame"
set "VGAME_HARNESS_USER_CONFIG=%VGAME_HARNESS_USER_DIR%\design-harness.env.bat"

if exist "%VGAME_HARNESS_USER_CONFIG%" call "%VGAME_HARNESS_USER_CONFIG%"

rem The harness and design roots always follow this Git checkout.
for %%I in ("%~dp0.") do set "VGAME_HARNESS_ROOT=%%~fI"
for %%I in ("%~dp0..") do set "VGAME_DESIGN_ROOT=%%~fI"
if not defined VGAME_ROOT set "VGAME_ROOT=%VGAME_DEFAULT_ROOT%"
if not defined VGAME_CONFIG_DATAS set "VGAME_CONFIG_DATAS=%VGAME_ROOT%\Config\GameConfig\Datas"
if not defined VGAME_CODE_ROOT set "VGAME_CODE_ROOT=%VGAME_ROOT%\HorizonFlyProject\Packages\VGame"
set "VGAME_SKILL_ROOT=%VGAME_DESIGN_ROOT%\skills"
set "VGAME_CLIENT_GRAPH=%VGAME_DESIGN_ROOT%\knowledge-graph\client\knowledge-graph.json"
if not defined VGAME_SOURCE_DOCS_ROOT set "VGAME_SOURCE_DOCS_ROOT="
if not defined VGAME_OUTPUT_ROOT set "VGAME_OUTPUT_ROOT=%VGAME_DESIGN_ROOT%\output"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
exit /b 0
