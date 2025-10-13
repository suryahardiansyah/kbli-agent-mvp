@echo off
echo ============================================
echo   Refreshing KBLI Cache from BPS WebAPI
echo ============================================

REM Change to your project directory
cd /d E:\GitHub\kbli-agent-mvp

REM Activate virtual environment if available
IF EXIST venv\Scripts\activate (
    call venv\Scripts\activate
    echo [OK] Virtual environment activated.
) ELSE (
    echo [WARN] No venv found, using system Python.
)

REM Run the loader to refresh KBLI cache
echo [INFO] Fetching latest KBLI data from BPS...
python -m src.loader_bps

echo --------------------------------------------
echo [DONE] Refresh complete. Check data\kbli2020_cache.json
echo --------------------------------------------

pause
