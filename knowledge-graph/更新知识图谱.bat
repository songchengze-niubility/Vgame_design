@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."
if exist "local.env.bat" call "local.env.bat"

echo ============================================================
echo   Vgame 知识图谱 - 全量更新
echo   只读取 VGAME_ROOT，不修改真实配置表
echo ============================================================
echo.

python "scripts\build_vgame_graph.py"
if errorlevel 1 (
    echo [ERROR] 图谱更新失败
    pause
    exit /b 1
)

echo.
echo [DONE] 图谱已更新并发布到 knowledge-graph\.understand-anything
pause
