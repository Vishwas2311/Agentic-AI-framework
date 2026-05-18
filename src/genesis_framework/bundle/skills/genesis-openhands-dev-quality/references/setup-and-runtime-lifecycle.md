# Setup And Runtime Lifecycle

Use this reference during dependency setup, runtime launch, QAOS, local run, and final approval.

Genesis should expose runtime state explicitly instead of hiding setup under a summary. Use these lifecycle states:

- `WAITING_FOR_RUNTIME`
- `PREPARING_APP`
- `INSTALLING_DEPENDENCIES`
- `RUNNING_SETUP_SCRIPT`
- `SETTING_UP_TESTS`
- `STARTING_APP`
- `WAITING_FOR_HTTP_READY`
- `RUNNING_BROWSER_QA`
- `RUNNING_API_QA`
- `RUNNING_SECURITY_QA`
- `RUNNING_PERFORMANCE_QA`
- `READY`
- `ERROR`

Runtime approval requires:

- dependencies installed through Genesis dependency manager or a clear `install_skipped` reason;
- matching localhost URL, auth callback URL, and Playwright base URL;
- HTTP readiness evidence;
- server log paths;
- shutdown evidence;
- lifecycle states recorded in `runtime_launch_report.json` and `qa_evidence_manifest.json`.

Do not require Docker, Kubernetes, or OpenHands sandbox runtime unless the selected Genesis stack explicitly requires it.
