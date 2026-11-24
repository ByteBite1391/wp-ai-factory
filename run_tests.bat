@echo off
cd /d %~dp0
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
) else if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo [ERROR] venv not found. Run: python -m venv .venv
    pause
    exit /b 1
)
pip install -r requirements-dev.txt --quiet
pytest
pause