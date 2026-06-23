@echo off
setlocal EnableExtensions
set "SETUP_LAUNCHER="
for /d %%D in ("%~dp0*") do (
    for %%F in ("%%~fD\*.bat") do (
        findstr /c:"Vgame Design Harness Setup" "%%~fF" >nul 2>nul
        if not errorlevel 1 set "SETUP_LAUNCHER=%%~fF"
    )
)
if not defined SETUP_LAUNCHER (
    echo [ERROR] The design harness setup launcher was not found.
    pause
    exit /b 1
)
call "%SETUP_LAUNCHER%"
exit /b %errorlevel%
