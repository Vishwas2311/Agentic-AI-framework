# /nocode2procode-deploy

Prepare or run approved deployment for a NoCode2ProCode by TrustEngines generated app.

## Required Behavior

1. Read `.genesis/genesis.deploy.yaml` and `.genesis/genesis.policy.yaml`.
2. Confirm deployment target and human approval before any deploy action.
3. Generate or update Docker, compose, Kubernetes, Helm, and CI/CD artifacts as requested.
4. Run smoke tests after deployment and produce `deployment_report.md` plus `staging_url.json` when available.
