# NoCode2ProCode Install

Run this when the user asks to install Genesis, install NoCode2ProCode, bootstrap the framework, or prepare a newly copied project folder.

For full local E2E setup:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullLocal -AllowSystemInstall -IncludeSecurityTools
```

For local migration only, without optional security scanner attempts:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1
```

After install, tell the user:

```powershell
.\.venv\Scripts\nocode2procode.exe migrate
```

Use `.genesis_runtime/install_report.md` to explain installed tools, skipped deployment tools, and credentials that require manual setup.

The installer opens the Genesis Full User Manual HTML at the end so the user can continue from a guided onboarding page. Use `-NoLaunchManual` only when the user explicitly wants no browser/manual launch.
