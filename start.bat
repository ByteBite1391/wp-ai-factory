@echo off
cd /d %~dp0
if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo [2/3] Installing requirements...
pip install -r requirements.txt --quiet
echo [3/3] Starting WP AI Factory...
python app.py
pause