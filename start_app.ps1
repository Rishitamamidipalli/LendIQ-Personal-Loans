# Loan Verification Web Application Startup Script
Write-Host "🚀 Starting Loan Verification Web Application..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if backend dependencies are installed
if (-Not (Test-Path "backend\requirements.txt")) {
    Write-Host "❌ Backend requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Check if frontend dependencies are installed
if (-Not (Test-Path "frontend\node_modules")) {
    Write-Host "⚠️  Frontend dependencies not installed!" -ForegroundColor Yellow
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host "✅ Starting Backend Server (FastAPI)..." -ForegroundColor Green
$backendCmd = "cd '$PWD'; .\venv\Scripts\Activate.ps1; cd backend; python main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "✅ Starting Frontend Server (React + Vite)..." -ForegroundColor Green
$frontendCmd = "cd '$PWD\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "✅ Application started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Access Points:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop the servers" -ForegroundColor Yellow
