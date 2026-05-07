$ErrorActionPreference = "Continue"

$commands = @(
  "python",
  "git",
  "node",
  "npm",
  "claude",
  "docker",
  "kubectl",
  "helm",
  "terraform",
  "semgrep",
  "gitleaks",
  "syft",
  "grype",
  "trivy"
)

foreach ($cmd in $commands) {
  $found = Get-Command $cmd -ErrorAction SilentlyContinue
  if ($found) {
    Write-Host "[OK] $cmd -> $($found.Source)"
  } else {
    Write-Host "[MISSING] $cmd"
  }
}

