param(
  [ValidateSet("Core", "LocalE2E", "FullLocal", "AuditOnly")]
  [string]$Profile = "LocalE2E",
  [switch]$InstallClaudeAssets,
  [switch]$AllowSystemInstall,
  [switch]$IncludeDeploy,
  [switch]$IncludeSecurityTools,
  [switch]$IncludePowerPlatform,
  [switch]$NoLaunchManual,
  [switch]$DryRun,
  [string]$ClaudeHome = "$env:USERPROFILE\.claude"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
$RuntimeDir = Join-Path $ProjectRoot ".genesis_runtime"
$VenvDir = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

if ($Profile -eq "FullLocal") {
  $IncludeSecurityTools = $true
}

$Report = [ordered]@{
  project = "NoCode2ProCode-Genesis"
  profile = $Profile
  project_root = $ProjectRoot
  started_at = $Timestamp
  dry_run = [bool]$DryRun
  allow_system_install = [bool]$AllowSystemInstall
  include_deploy = [bool]$IncludeDeploy
  launch_manual = -not [bool]$NoLaunchManual
  installed = @()
  skipped = @()
  missing = @()
  manual = @()
  warnings = @()
}

function Add-ReportItem {
  param(
    [ValidateSet("installed", "skipped", "missing", "manual", "warnings")]
    [string]$Bucket,
    [string]$Name,
    [string]$Detail
  )
  $Report[$Bucket] += [ordered]@{ name = $Name; detail = $Detail }
}

function Test-CommandExists {
  param([string]$Name)
  return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-GenesisStep {
  param(
    [string]$Name,
    [scriptblock]$Action,
    [string]$CommandText,
    [switch]$Optional
  )

  Write-Host ""
  Write-Host "==> $Name" -ForegroundColor Cyan
  if ($CommandText) {
    Write-Host "    $CommandText" -ForegroundColor DarkGray
  }

  if ($DryRun) {
    Add-ReportItem -Bucket "skipped" -Name $Name -Detail "Dry run: $CommandText"
    return
  }

  try {
    & $Action
    Add-ReportItem -Bucket "installed" -Name $Name -Detail $CommandText
  } catch {
    if ($Optional) {
      Add-ReportItem -Bucket "warnings" -Name $Name -Detail $_.Exception.Message
      Write-Host "WARN: $($_.Exception.Message)" -ForegroundColor Yellow
    } else {
      Add-ReportItem -Bucket "missing" -Name $Name -Detail $_.Exception.Message
      throw
    }
  }
}

function Ensure-Command {
  param(
    [string]$Name,
    [string]$WingetId,
    [string]$ManualMessage,
    [switch]$Optional
  )

  if (Test-CommandExists $Name) {
    $Source = (Get-Command $Name -ErrorAction SilentlyContinue).Source
    Add-ReportItem -Bucket "installed" -Name $Name -Detail "Found: $Source"
    return $true
  }

  if ($AllowSystemInstall -and $WingetId -and (Test-CommandExists "winget")) {
    Invoke-GenesisStep -Name "Install $Name with winget" -CommandText "winget install --id $WingetId" -Optional:$Optional -Action {
      & winget install --id $WingetId -e --silent --accept-package-agreements --accept-source-agreements
      if ($LASTEXITCODE -ne 0) { throw "winget failed for $Name with exit code $LASTEXITCODE" }
    }
    if (Test-CommandExists $Name) {
      return $true
    }
    Add-ReportItem -Bucket "warnings" -Name $Name -Detail "Installed or queued by winget, but this terminal may need restart before PATH sees it."
    return $false
  }

  if ($Optional) {
    Add-ReportItem -Bucket "manual" -Name $Name -Detail $ManualMessage
  } else {
    Add-ReportItem -Bucket "missing" -Name $Name -Detail $ManualMessage
  }
  return $false
}

function Write-InstallReports {
  $JsonPath = Join-Path $RuntimeDir "install_report.json"
  $MarkdownPath = Join-Path $RuntimeDir "install_report.md"
  $Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

  $Lines = @()
  $Lines += "# Genesis Install Report"
  $Lines += ""
  $Lines += "- Project: NoCode2ProCode-Genesis"
  $Lines += "- Profile: $Profile"
  $Lines += "- Project root: $ProjectRoot"
  $Lines += "- Started: $Timestamp"
  $Lines += "- Dry run: $([bool]$DryRun)"
  $Lines += ""
  foreach ($Bucket in @("installed", "skipped", "missing", "manual", "warnings")) {
    $Lines += "## $Bucket"
    if ($Report[$Bucket].Count -eq 0) {
      $Lines += "- None"
    } else {
      foreach ($Item in $Report[$Bucket]) {
        $Lines += "- $($Item.name): $($Item.detail)"
      }
    }
    $Lines += ""
  }
  $Lines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8
  Write-Host ""
  Write-Host "Install report written:" -ForegroundColor Green
  Write-Host "  $JsonPath"
  Write-Host "  $MarkdownPath"
}

function Get-GenesisManualPath {
  $Preferred = @(
    "Full User Manual - Genesis.html",
    "Full User Manual -agents-pro-v8.html",
    "trustengine-landing-agents-pro-v8.html",
    "Nocode2Procode-Genesis-Experience.html",
    "Nocode2Procode-Genesis-Pro.html",
    "Nocode2Procode-Genesis.html"
  )
  foreach ($Name in $Preferred) {
    $Candidate = Join-Path $ProjectRoot $Name
    if (Test-Path -LiteralPath $Candidate) {
      return (Resolve-Path -LiteralPath $Candidate).Path
    }
  }
  $Fallback = Get-ChildItem -LiteralPath $ProjectRoot -File -Filter "*.html" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "manual|genesis" } |
    Sort-Object Name |
    Select-Object -First 1
  if ($Fallback) {
    return $Fallback.FullName
  }
  return $null
}

function Open-GenesisManual {
  if ($NoLaunchManual) {
    Add-ReportItem -Bucket "skipped" -Name "Genesis user manual launch" -Detail "Skipped because -NoLaunchManual was passed."
    return
  }

  $ManualPath = Get-GenesisManualPath
  if (-not $ManualPath) {
    Add-ReportItem -Bucket "warnings" -Name "Genesis user manual launch" -Detail "No Genesis HTML manual was found in the project root."
    return
  }

  if ($DryRun) {
    Add-ReportItem -Bucket "skipped" -Name "Genesis user manual launch" -Detail "Dry run: would open $ManualPath"
    Write-Host ""
    Write-Host "Dry run manual launch: $ManualPath" -ForegroundColor DarkGray
    return
  }

  Write-Host ""
  Write-Host "Opening Genesis Full User Manual..." -ForegroundColor Cyan
  Write-Host "  $ManualPath" -ForegroundColor DarkGray
  Start-Process -FilePath $ManualPath
  Add-ReportItem -Bucket "installed" -Name "Genesis user manual launch" -Detail "Opened $ManualPath"
}

Push-Location $ProjectRoot
try {
  Write-Host "NoCode2ProCode-Genesis one-command installer" -ForegroundColor Cyan
  Write-Host "Project root: $ProjectRoot"
  Write-Host "Profile: $Profile"

  Ensure-Command -Name "git" -WingetId "Git.Git" -ManualMessage "Install Git, or rerun with -AllowSystemInstall." | Out-Null
  Ensure-Command -Name "python" -WingetId "Python.Python.3.11" -ManualMessage "Install Python 3.11+, or rerun with -AllowSystemInstall." | Out-Null
  Ensure-Command -Name "node" -WingetId "OpenJS.NodeJS.LTS" -ManualMessage "Install Node.js LTS 20+, or rerun with -AllowSystemInstall." | Out-Null
  Ensure-Command -Name "npm" -WingetId "OpenJS.NodeJS.LTS" -ManualMessage "Install npm with Node.js LTS 20+, or rerun with -AllowSystemInstall." | Out-Null

  if ($Profile -eq "AuditOnly") {
    Add-ReportItem -Bucket "skipped" -Name "package install" -Detail "AuditOnly profile does not install packages."
    Write-InstallReports
    return
  }

  if (-not (Test-CommandExists "python")) { throw "Python is required before Genesis can create its local virtual environment." }
  if (-not (Test-CommandExists "node")) { throw "Node.js is required before Genesis can install local browser/UI tooling." }
  if (-not (Test-CommandExists "npm")) { throw "npm is required before Genesis can install local browser/UI tooling." }

  if (-not (Test-Path -LiteralPath $VenvDir)) {
    Invoke-GenesisStep -Name "Create Genesis Python virtual environment" -CommandText "python -m venv .venv" -Action {
      & python -m venv $VenvDir
      if ($LASTEXITCODE -ne 0) { throw "python -m venv failed with exit code $LASTEXITCODE" }
    }
  } else {
    Add-ReportItem -Bucket "installed" -Name "Python virtual environment" -Detail "Found: $VenvDir"
  }

  if (-not (Test-Path -LiteralPath $PythonExe)) {
    if ($DryRun) {
      Add-ReportItem -Bucket "skipped" -Name "Virtual environment Python validation" -Detail "Dry run: $PythonExe will exist after venv creation."
    } else {
      throw "Virtual environment Python not found at $PythonExe"
    }
  }

  Invoke-GenesisStep -Name "Upgrade Python package installer" -CommandText ".venv python -m pip install --upgrade pip setuptools wheel" -Action {
    & $PythonExe -m pip install --upgrade pip setuptools wheel
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed with exit code $LASTEXITCODE" }
  }

  $PythonExtra = if ($Profile -eq "Core") { ".[dev]" } else { ".[dev,local-e2e]" }
  Invoke-GenesisStep -Name "Install Genesis Python package and local E2E libraries" -CommandText ".venv python -m pip install -e `"$PythonExtra`"" -Action {
    & $PythonExe -m pip install -e $PythonExtra
    if ($LASTEXITCODE -ne 0) { throw "Genesis Python install failed with exit code $LASTEXITCODE" }
  }

  if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "package.json"))) {
    Invoke-GenesisStep -Name "Create local Node workspace manifest" -CommandText "npm init -y" -Action {
      & npm init -y | Out-Null
      if ($LASTEXITCODE -ne 0) { throw "npm init failed with exit code $LASTEXITCODE" }
    }
  } else {
    Add-ReportItem -Bucket "installed" -Name "Node workspace manifest" -Detail "Found package.json"
  }

  $NodePackages = @(
    "@playwright/test",
    "@axe-core/playwright",
    "pixelmatch",
    "pngjs",
    "motion",
    "lighthouse",
    "typescript",
    "eslint",
    "prettier",
    "@openapitools/openapi-generator-cli",
    "@asyncapi/generator"
  )
  Invoke-GenesisStep -Name "Install Genesis browser, visual QA, API, and motion libraries" -CommandText "npm install -D $($NodePackages -join ' ')" -Action {
    & npm install -D @playwright/test @axe-core/playwright pixelmatch pngjs motion lighthouse typescript eslint prettier @openapitools/openapi-generator-cli @asyncapi/generator
    if ($LASTEXITCODE -ne 0) { throw "npm package install failed with exit code $LASTEXITCODE" }
  }

  Invoke-GenesisStep -Name "Install Playwright Chromium browser" -CommandText "npx playwright install chromium" -Action {
    & npx playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw "Playwright browser install failed with exit code $LASTEXITCODE" }
  }

  if ($InstallClaudeAssets) {
    $ClaudeInstaller = Join-Path $ProjectRoot "scripts\install_genesis.ps1"
    if (Test-Path -LiteralPath $ClaudeInstaller) {
      Invoke-GenesisStep -Name "Install Genesis Claude commands and skill files" -CommandText "scripts\install_genesis.ps1 -InstallSkill" -Action {
        & $ClaudeInstaller -ClaudeHome $ClaudeHome -InstallSkill
        if ($LASTEXITCODE -ne 0) { throw "Claude asset install failed with exit code $LASTEXITCODE" }
      }
    } else {
      Add-ReportItem -Bucket "warnings" -Name "Claude assets" -Detail "scripts\install_genesis.ps1 not found."
    }
    if (-not (Test-CommandExists "claude")) {
      Add-ReportItem -Bucket "manual" -Name "Claude Code CLI/extension" -Detail "Claude app/extension is account-managed. This installer copied commands and skills, but cannot configure corporate Claude access."
    }
  }

  if ($IncludeSecurityTools) {
    Ensure-Command -Name "semgrep" -WingetId "" -ManualMessage "Installed through Python virtualenv; use .venv Scripts path if global command is unavailable." -Optional | Out-Null
    Ensure-Command -Name "gitleaks" -WingetId "Gitleaks.Gitleaks" -ManualMessage "Install Gitleaks or rerun with -AllowSystemInstall." -Optional | Out-Null
    Ensure-Command -Name "syft" -WingetId "Anchore.Syft" -ManualMessage "Install Syft or rerun with -AllowSystemInstall." -Optional | Out-Null
    Ensure-Command -Name "grype" -WingetId "Anchore.Grype" -ManualMessage "Install Grype or rerun with -AllowSystemInstall." -Optional | Out-Null
    Ensure-Command -Name "trivy" -WingetId "AquaSecurity.Trivy" -ManualMessage "Install Trivy or rerun with -AllowSystemInstall." -Optional | Out-Null
    Ensure-Command -Name "osv-scanner" -WingetId "Google.OSV-Scanner" -ManualMessage "Install OSV Scanner or rerun with -AllowSystemInstall." -Optional | Out-Null
  } else {
    Add-ReportItem -Bucket "skipped" -Name "system security scanners" -Detail "Pass -IncludeSecurityTools to attempt Gitleaks/Syft/Grype/Trivy/OSV Scanner."
  }

  if ($IncludePowerPlatform) {
    if (Test-CommandExists "dotnet") {
      Invoke-GenesisStep -Name "Install or update Microsoft Power Platform CLI" -CommandText "dotnet tool update --global Microsoft.PowerApps.CLI.Tool" -Optional -Action {
        & dotnet tool update --global Microsoft.PowerApps.CLI.Tool
        if ($LASTEXITCODE -ne 0) {
          & dotnet tool install --global Microsoft.PowerApps.CLI.Tool
          if ($LASTEXITCODE -ne 0) { throw "Power Platform CLI install failed with exit code $LASTEXITCODE" }
        }
      }
    } else {
      Add-ReportItem -Bucket "manual" -Name "Power Platform CLI" -Detail "Install .NET SDK first, then run dotnet tool install --global Microsoft.PowerApps.CLI.Tool."
    }
  } else {
    Add-ReportItem -Bucket "skipped" -Name "Power Platform CLI" -Detail "Pass -IncludePowerPlatform when PowerApps exports need PAC CLI support."
  }

  if ($IncludeDeploy) {
    Ensure-Command -Name "docker" -WingetId "Docker.DockerDesktop" -ManualMessage "Install Docker Desktop or configure company-approved container runtime." -Optional | Out-Null
    Ensure-Command -Name "kubectl" -WingetId "Kubernetes.kubectl" -ManualMessage "Install kubectl only for Kubernetes delivery workflows." -Optional | Out-Null
    Ensure-Command -Name "helm" -WingetId "Helm.Helm" -ManualMessage "Install Helm only for Kubernetes delivery workflows." -Optional | Out-Null
    Ensure-Command -Name "terraform" -WingetId "Hashicorp.Terraform" -ManualMessage "Install Terraform only for infra delivery workflows." -Optional | Out-Null
  } else {
    Add-ReportItem -Bucket "skipped" -Name "deployment CLIs" -Detail "LocalE2E skips Docker/Kubernetes/Terraform. Pass -IncludeDeploy when needed."
  }

  Add-ReportItem -Bucket "manual" -Name "UI/UX Pro Max external skill" -Detail "Install/configure this in the active Claude/Codex skill environment if your company allows external skills."
  Add-ReportItem -Bucket "manual" -Name "21st.dev Magic MCP" -Detail "Requires 21st.dev account access and MCP configuration; installer cannot authenticate it silently."
  Add-ReportItem -Bucket "manual" -Name "Figma/Firecrawl/Context7/E2B/PostgreSQL/GitHub MCPs" -Detail "These require account tokens, scoped permissions, or read-only credentials. Configure them after company approval."

  $EnvExample = Join-Path $ProjectRoot ".env.example"
  $EnvLocal = Join-Path $ProjectRoot ".env.local"
  if ((Test-Path -LiteralPath $EnvExample) -and -not (Test-Path -LiteralPath $EnvLocal)) {
    Invoke-GenesisStep -Name "Create local credential placeholder file" -CommandText "Copy .env.example to .env.local" -Action {
      Copy-Item -LiteralPath $EnvExample -Destination $EnvLocal -Force
    }
  } elseif (Test-Path -LiteralPath $EnvLocal) {
    Add-ReportItem -Bucket "installed" -Name ".env.local" -Detail "Found existing local credential placeholder file; preserved it."
  } else {
    Add-ReportItem -Bucket "warnings" -Name ".env.example" -Detail "Credential template is missing; cloud/MCP setup cannot be guided from template."
  }

  Invoke-GenesisStep -Name "Validate Genesis configuration" -CommandText ".venv python -m genesis_framework.cli validate --project `"$ProjectRoot`"" -Optional -Action {
    & $PythonExe -m genesis_framework.cli validate --project $ProjectRoot
    if ($LASTEXITCODE -ne 0) { throw "Genesis validation failed with exit code $LASTEXITCODE" }
  }

  Invoke-GenesisStep -Name "Write Genesis install plan" -CommandText ".venv python -m genesis_framework.cli install-plan --project `"$ProjectRoot`"" -Optional -Action {
    & $PythonExe -m genesis_framework.cli install-plan --project $ProjectRoot
    if ($LASTEXITCODE -ne 0) { throw "Genesis install-plan failed with exit code $LASTEXITCODE" }
  }

  Open-GenesisManual
  Write-InstallReports
  Write-Host ""
  Write-Host "Genesis LocalE2E install complete." -ForegroundColor Green
  Write-Host "Next: put source files in migration_inputs and run:"
  Write-Host "  .\.venv\Scripts\nocode2procode.exe migrate" -ForegroundColor Cyan
} finally {
  Pop-Location
}
