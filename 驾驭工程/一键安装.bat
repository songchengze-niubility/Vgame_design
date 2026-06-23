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
echo   Vgame Design Harness Setup
echo ================================================================
echo   Design repo : %VGAME_DESIGN_ROOT%
echo   Project root: %VGAME_ROOT%
echo.

echo [1/5] Checking the Git design repository...
where git >nul 2>nul
if errorlevel 1 goto :missing_git
if not exist "%VGAME_DESIGN_ROOT%\.git" goto :missing_design_repo

echo [2/5] Checking the Vgame SVN workspace...
if not exist "%VGAME_ROOT%\Config\GameConfig\Datas\__tables__.xlsx" (
    set "PROJECT_INPUT="
    set /p "PROJECT_INPUT=Enter the Vgame SVN root path: "
    if not defined PROJECT_INPUT goto :missing_project
    for %%I in ("!PROJECT_INPUT!") do set "VGAME_ROOT=%%~fI"
    if not exist "!VGAME_ROOT!\Config\GameConfig\Datas\__tables__.xlsx" goto :missing_project
)
set "VGAME_CONFIG_DATAS=%VGAME_ROOT%\Config\GameConfig\Datas"
set "VGAME_CODE_ROOT=%VGAME_ROOT%\HorizonFlyProject\Packages\VGame"

echo [3/5] Saving machine-local paths...
if not exist "%VGAME_HARNESS_USER_DIR%" mkdir "%VGAME_HARNESS_USER_DIR%"
call :write_config "%VGAME_HARNESS_USER_CONFIG%"
call :write_config "%VGAME_DESIGN_ROOT%\local.env.bat"

echo [4/5] Checking Python dependencies...
where python >nul 2>nul
if errorlevel 1 goto :missing_python
python -c "import openpyxl" >nul 2>nul
if errorlevel 1 (
    echo   Installing openpyxl...
    python -m pip install openpyxl
    if errorlevel 1 goto :python_dependency_failed
)

echo [5/5] Running repository checks...
powershell -NoProfile -ExecutionPolicy Bypass -File "%VGAME_DESIGN_ROOT%\scripts\check.ps1"
if errorlevel 1 goto :check_failed
python "%VGAME_DESIGN_ROOT%\scripts\check_vgame_graph.py"
if errorlevel 1 goto :check_failed

echo.
echo ================================================================
echo   Setup complete
echo ================================================================
echo   Open this Git repository in Codex for Vgame design work.
echo.
pause
exit /b 0

:write_config
(
    echo @echo off
    echo set "VGAME_ROOT=%VGAME_ROOT%"
    echo set "VGAME_DESIGN_ROOT=%VGAME_DESIGN_ROOT%"
    echo set "VGAME_HARNESS_ROOT=%VGAME_HARNESS_ROOT%"
    echo set "VGAME_DESIGN_REMOTE=%VGAME_DESIGN_REMOTE%"
    echo set "VGAME_DESIGN_BRANCH=%VGAME_DESIGN_BRANCH%"
    echo set "VGAME_CONFIG_DATAS=%VGAME_CONFIG_DATAS%"
    echo set "VGAME_CODE_ROOT=%VGAME_CODE_ROOT%"
    echo set "VGAME_SKILL_ROOT=%VGAME_SKILL_ROOT%"
    echo set "VGAME_CLIENT_GRAPH=%VGAME_CLIENT_GRAPH%"
    echo set "VGAME_SOURCE_DOCS_ROOT=%VGAME_SOURCE_DOCS_ROOT%"
    echo set "VGAME_OUTPUT_ROOT=%VGAME_OUTPUT_ROOT%"
) > "%~1"
exit /b 0

:missing_git
echo [ERROR] Git was not found. Install Git and retry.
goto :failed

:missing_design_repo
echo [ERROR] Run this launcher from a cloned Vgame_design Git repository.
goto :failed

:missing_project
echo [ERROR] The selected Vgame SVN project path is invalid.
goto :failed

:missing_python
echo [ERROR] Python was not found. Install Python 3.10 or newer.
goto :failed

:python_dependency_failed
echo [ERROR] Failed to install openpyxl.
goto :failed

:check_failed
echo [ERROR] Repository checks failed. Review the messages above.
goto :failed

:failed
pause
exit /b 1
