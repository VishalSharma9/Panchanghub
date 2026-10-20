@echo off
title PanchangHub Unified Server (Website + API)
echo ========================================================
echo   Starting PanchangHub Unified Server (Website + API)
echo ========================================================
echo   - Local Website:  http://localhost:8080/
echo   - API Docs:       http://localhost:8080/api/docs
echo   - Shodashavargas: http://localhost:8080/vargas
echo   - Classical Yogas:http://localhost:8080/yogas
echo   - Vedic Reading:  http://localhost:8080/reading
echo ========================================================
cd /d "%~dp0api"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
pause
