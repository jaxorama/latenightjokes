@echo off
REM Regenerates docs\index.html from every data\week-*.json file, opens it,
REM and pushes the update to GitHub (which republishes GitHub Pages).
cd /d "%~dp0"

python generate_site.py
if errorlevel 1 (
    echo.
    echo Site generation failed - see error above.
    pause
    exit /b 1
)

start "" "docs\index.html"

git add -A
git commit -m "Update site" --quiet
if errorlevel 1 (
    echo Nothing new to commit.
    exit /b 0
)
git push --quiet
