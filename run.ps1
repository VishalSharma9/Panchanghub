Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting PanchangHub Unified Server (Website + API)   " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  - Local Website:   http://localhost:8080/" -ForegroundColor Green
Write-Host "  - API Docs:        http://localhost:8080/api/docs" -ForegroundColor Green
Write-Host "  - Shodashavargas:  http://localhost:8080/vargas" -ForegroundColor Green
Write-Host "  - Classical Yogas: http://localhost:8080/yogas" -ForegroundColor Green
Write-Host "  - Vedic Reading:   http://localhost:8080/reading" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location "$PSScriptRoot\api"
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
