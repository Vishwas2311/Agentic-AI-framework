param(
  [ValidateSet("Core", "LocalE2E", "FullLocal", "AuditOnly")]
  [string]$Profile = "LocalE2E",
  [switch]$AllowSystemInstall,
  [switch]$IncludeDeploy,
  [switch]$IncludeSecurityTools,
  [switch]$IncludePowerPlatform,
  [switch]$NoClaudeAssets,
  [switch]$NoLaunchManual,
  [switch]$DryRun,
  [string]$ClaudeHome = "$env:USERPROFILE\.claude"
)

$ErrorActionPreference = "Stop"
$Installer = Join-Path $PSScriptRoot "scripts\install_genesis_all.ps1"

if (-not (Test-Path -LiteralPath $Installer)) {
  throw "Genesis installer not found: $Installer"
}

$InstallerArgs = @{
  Profile = $Profile
  ClaudeHome = $ClaudeHome
}

if (-not $NoClaudeAssets) { $InstallerArgs.InstallClaudeAssets = $true }
if ($AllowSystemInstall) { $InstallerArgs.AllowSystemInstall = $true }
if ($IncludeDeploy) { $InstallerArgs.IncludeDeploy = $true }
if ($IncludeSecurityTools) { $InstallerArgs.IncludeSecurityTools = $true }
if ($IncludePowerPlatform) { $InstallerArgs.IncludePowerPlatform = $true }
if ($DryRun) { $InstallerArgs.DryRun = $true }
if ($NoLaunchManual) { $InstallerArgs.NoLaunchManual = $true }

& $Installer @InstallerArgs
exit $LASTEXITCODE
