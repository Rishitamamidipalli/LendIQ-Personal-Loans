# Clean reinstall script for frontend
Write-Host "🧹 Cleaning up old installation..." -ForegroundColor Yellow

# Remove node_modules
if (Test-Path "node_modules") {
    Write-Host "Removing node_modules..." -ForegroundColor Cyan
    Remove-Item "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
}

# Remove package-lock.json
if (Test-Path "package-lock.json") {
    Write-Host "Removing package-lock.json..." -ForegroundColor Cyan
    Remove-Item "package-lock.json" -Force
}

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔄 Installing dependencies..." -ForegroundColor Yellow

# Install with legacy peer deps
npm install --legacy-peer-deps

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "🚀 Run 'npm run dev' to start the development server" -ForegroundColor Cyan
