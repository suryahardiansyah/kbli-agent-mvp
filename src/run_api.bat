@echo off
echo ============================================
echo   Starting KBLI Agent API (FastAPI + Uvicorn)
echo ============================================

REM Change to your project folder
cd /d E:\GitHub\kbli-agent-mvp

REM Activate virtual environment if available
IF EXIST venv\Scripts\activate (
    call venv\Scripts\activate
    echo [OK] Virtual environment activated.
) ELSE (
    echo [WARN] No venv found, using system Python.
)

REM Run FastAPI from inside project root (important!)
python -m uvicorn src.api_handler:app --host 0.0.0.0 --port 8000 --reload

pause
