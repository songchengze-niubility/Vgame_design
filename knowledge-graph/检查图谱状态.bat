@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."
if exist "local.env.bat" call "local.env.bat"

python "scripts\check_vgame_graph.py"
set "RESULT=%errorlevel%"
echo.
pause
exit /b %RESULT%
