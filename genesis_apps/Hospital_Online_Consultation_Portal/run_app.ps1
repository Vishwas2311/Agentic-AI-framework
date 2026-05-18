# Hospital Online Consultation Portal — Genesis v3.1.0
# Run this script to install dependencies and start the dev server

$appDir = Join-Path $PSScriptRoot "frontend"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Hospital Online Consultation Portal" -ForegroundColor Cyan
Write-Host "  NoCode2ProCode by TrustEngines · Genesis v3.1.0" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stack: Next.js 14 + Tailwind + shadcn/ui + Framer Motion" -ForegroundColor Gray
Write-Host "Login: patient@example.com / patient123" -ForegroundColor Yellow
Write-Host ""

Set-Location $appDir

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host ""
Write-Host "Starting dev server at http://localhost:3000" -ForegroundColor Green
Write-Host ""

npm run dev
