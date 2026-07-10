@echo off
REM Regenerates site\index.html from every data\week-*.json file and opens it.
cd /d "%~dp0"

python generate_site.py
if errorlevel 1 (
    echo.
    echo Site generation failed - see error above.
    pause
    exit /b 1
)

start "" "site\index.html"
