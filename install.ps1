# Genesis E2E Installer for Windows
# Usage: irm https://raw.githubusercontent.com/Vishwas2311/Agentic-AI-framework/main/install.ps1 | iex

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Genesis Pro - E2E Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found. Install Python 3.11+ from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "OK  Python found" -ForegroundColor Green

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "WARN Node.js not found. Install from https://nodejs.org for full features." -ForegroundColor Yellow
} else {
    Write-Host "OK  Node.js found" -ForegroundColor Green
}

# Check Claude Code
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "WARN Claude Code CLI not found. Install from https://claude.ai/code for full features." -ForegroundColor Yellow
} else {
    Write-Host "OK  Claude Code found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installing genesis-pro from PyPI..." -ForegroundColor Cyan
pip install --upgrade genesis-pro

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed." -ForegroundColor Red
    exit 1
}
Write-Host "OK  genesis-pro installed" -ForegroundColor Green

Write-Host ""
Write-Host "Running Genesis E2E setup..." -ForegroundColor Cyan
genesis install

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Genesis is ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Run: genesis launch   -> opens dashboard" -ForegroundColor White
Write-Host "Run: genesis --help   -> see all commands" -ForegroundColor White
Write-Host ""
