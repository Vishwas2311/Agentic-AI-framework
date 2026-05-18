# Hospital Online Consultation Portal - Demo Runner
# Genesis: NoCode2ProCode by TrustEngines

$ErrorActionPreference = "Stop"
$AppDir = $PSScriptRoot

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Hospital Online Consultation Portal" -ForegroundColor Cyan
Write-Host "  Demo Runner | NoCode2ProCode by TrustEngines" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $AppDir

# Check node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Install deps if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Starting development server..." -ForegroundColor Green
Write-Host "URL: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Demo credentials:" -ForegroundColor Yellow
Write-Host "  Email:    patient@example.com" -ForegroundColor White
Write-Host "  Password: patient123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

npm run dev
