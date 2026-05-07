param(
  [string]$ClaudeHome = "$env:USERPROFILE\.claude",
  [switch]$InstallSkill
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Installing NoCode2ProCode by TrustEngines Claude command files..."
New-Item -ItemType Directory -Force -Path "$ClaudeHome\commands" | Out-Null
Copy-Item -Path "$ProjectRoot\.claude\commands\*.md" -Destination "$ClaudeHome\commands" -Force

if ($InstallSkill) {
  Write-Host "Installing NoCode2ProCode by TrustEngines skill..."
  New-Item -ItemType Directory -Force -Path "$ClaudeHome\skills" | Out-Null
  Copy-Item -Path "$ProjectRoot\skills\nocode2procode-genesis" -Destination "$ClaudeHome\skills" -Recurse -Force
}

Write-Host "NoCode2ProCode by TrustEngines Claude command install complete."
Write-Host "Preferred slash commands now use /nocode2procode-*; /genesis-* remains installed as a compatibility alias."
Write-Host "Next: install Python package with: pip install -e `"$ProjectRoot[dev]`""
