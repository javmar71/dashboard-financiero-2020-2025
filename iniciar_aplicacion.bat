@echo off
REM Lanzador principal: arranca el dashboard Streamlit de la Fase 10 (2026-09-19)
REM Raiz del repositorio = AUTOMAT ANALISIS FIN (unificacion de lanzadores 2026-09-20)
REM Espera mediante ping (no interactivo, compatible con invocacion automatizada)
REM Uso: doble clic, o iniciar_aplicacion.bat --silent
setlocal
set "ROOT=%~dp0"
set "PYTHONPATH=%ROOT%src"
cd /d "%ROOT%"
if /i "%1"=="--silent" (
    start "" /min "%~dp0..\venv\Scripts\pythonw.exe" -m streamlit run "salidas\dashboard\app.py" --server.address localhost --server.port 8501 --server.headless true --browser.gatherUsageStats false
    echo Dashboard lanzado en segundo plano: http://localhost:8501
    ping 127.0.0.1 -n 11 >nul
    start "" "http://localhost:8501"
) else (
    start "" "http://localhost:8501"
    "%~dp0..\venv\Scripts\python.exe" -m streamlit run "salidas\dashboard\app.py" --server.address localhost --server.port 8501 --server.headless true --browser.gatherUsageStats false
)
endlocal
