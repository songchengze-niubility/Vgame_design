@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."
if exist "local.env.bat" call "local.env.bat"

echo Vgame 图谱监控每 30 秒检查一次，按 Ctrl+C 停止。
python "scripts\watch_vgame_graph.py" --interval 30
pause
