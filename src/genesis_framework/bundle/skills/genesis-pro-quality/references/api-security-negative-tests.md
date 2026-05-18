# API And Defensive Security Rules

Inspired by local API security, broken-authentication, IDOR, and XSS testing skills. Use only safe local defensive checks.

## API Negative Matrix

For each discovered API route, generate or verify:

- expected 2xx happy path where safe
- 400 for invalid payload
- 401 for missing auth when protected
- 403 for wrong role when role-protected
- 404 for missing object/id
- no raw stack traces in response bodies
- consistent JSON error shape

## Runtime Security Checks

- Protected pages redirect when unauthenticated.
- Protected API routes reject missing or invalid auth.
- Cross-user or cross-role object access is denied where applicable.
- XSS-like input is escaped in rendered UI.
- Destructive actions require explicit confirmation or safe method checks.
- Missing API keys degrade clearly instead of crashing the app.

## Required Outputs

- `api_negative_test_report.json`
- `security_abuse_case_report.json`
- `security_review.json`
- `qa_evidence_manifest.json`

## Safety Boundary

Do not run offensive scans against external targets. Only test local generated apps or explicitly approved internal QA URLs.
