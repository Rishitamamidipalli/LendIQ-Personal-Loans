# Setup Script for Loan Verification Web Application
Write-Host "🔧 Setting up Loan Verification Web Application..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "1. Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Step 2: Check Node.js
Write-Host "2. Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "   OK: Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Node.js not found! Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# Step 3: Create Virtual Environment
Write-Host "3. Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   WARNING: Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "   OK: Virtual environment created" -ForegroundColor Green
}

# Step 4: Install Backend Dependencies
Write-Host "4. Installing backend dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install main project requirements if exists
if (Test-Path "requirements.txt") {
    Write-Host "   📦 Installing main project dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

# Install backend requirements
Write-Host "   📦 Installing FastAPI backend dependencies..." -ForegroundColor Cyan
pip install -r backend\requirements.txt

Write-Host "   OK: Backend dependencies installed" -ForegroundColor Green

# Step 5: Install Frontend Dependencies
Write-Host "5. Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..
Write-Host "   OK: Frontend dependencies installed" -ForegroundColor Green

# Step 6: Check Environment Variables
Write-Host "6. Checking environment variables..." -ForegroundColor Yellow
if ($env:GOOGLE_API_KEY) {
    Write-Host "   OK: GOOGLE_API_KEY is set" -ForegroundColor Green
} else {
    Write-Host "   WARNING: GOOGLE_API_KEY not found!" -ForegroundColor Yellow
    Write-Host "   Please set your Google Gemini API key:" -ForegroundColor Yellow
    Write-Host "   `$env:GOOGLE_API_KEY='your_api_key_here'" -ForegroundColor White
}

# Step 7: Verify Directory Structure
Write-Host "7. Verifying directory structure..." -ForegroundColor Yellow
$requiredDirs = @("Documents11", "backend", "frontend")
$allExist = $true
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "   OK: $dir exists" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: $dir not found!" -ForegroundColor Red
        $allExist = $false
    }
}

if (Test-Path "new_applications.json") {
    Write-Host "   OK: new_applications.json exists" -ForegroundColor Green
} else {
    Write-Host "   ERROR: new_applications.json not found!" -ForegroundColor Red
    $allExist = $false
}

Write-Host ""
if ($allExist) {
    Write-Host "SUCCESS: Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the application, run:" -ForegroundColor Cyan
    Write-Host "   .\start_app.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or start manually:" -ForegroundColor Cyan
    Write-Host "   Terminal 1: cd backend && python main.py" -ForegroundColor White
    Write-Host "   Terminal 2: cd frontend && npm run dev" -ForegroundColor White
} else {
    Write-Host "WARNING: Setup completed with warnings. Please fix the issues above." -ForegroundColor Yellow
}
