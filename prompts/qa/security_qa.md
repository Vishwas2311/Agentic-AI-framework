# Security QA Prompt

Run deterministic security checks first.

## Tools

- Semgrep
- CodeQL
- Gitleaks
- OWASP ZAP
- Syft
- Grype
- Trivy
- OSV Scanner

## Rules

- Critical and high findings block approval.
- Secrets in generated files block approval.
- SBOM is required before PR.

