# Install Genesis E2E

When the user says `install Genesis E2E`, `install NoCode2ProCode E2E`, `setup Genesis fully`, or asks to install all Genesis prerequisites on a copied machine, run the root wrapper from the project root. Do not call `scripts/install_genesis_all.ps1` directly unless the user explicitly asks for an internal/debug install, because the wrapper installs Claude commands and the Genesis skill by default.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullPipeline -AllowSystemInstall
```

For OCR/video/semantic ML extraction on a capable machine, use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullLocalAI -AllowSystemInstall -IncludeSecurityTools
```

Expected behavior:

- Create `.venv`
- Install the Genesis CLI and Python libraries
- Install local E2E, QA, security, and browser-support libraries
- Install local Node packages for Playwright, visual QA, and API tooling
- Warm the shared Genesis npm cache; Motion remains a generated-app dependency when a selected UI stack requires it
- Install Chromium for Playwright
- Validate Lighthouse, LHCI, k6, QAOSAgent, and required FullPipeline security/runtime tools
- Validate FullPipeline linkage and installer tool coverage reports
- Copy Genesis Claude command files
- Copy the Genesis skill into the Claude skills folder
- Create `.env.local` from `.env.example` when missing
- Validate Genesis configuration
- Write `.genesis_runtime/install_report.md`
- Write `.genesis_runtime/install_capability_matrix.json`
- Open `trustengine-landing-agents-pro-v8.html` after successful install
- Continue without exposing secrets

If deployment tooling is explicitly requested, add `-IncludeDeploy`.
If the user wants terminal-only installation, add `-NoLaunchManual`.

Never hardcode or print secrets. For GitHub, Figma, 21st.dev Magic, Firecrawl, E2B, PostgreSQL, Claude account access, or other cloud/MCP integrations, preserve placeholders in `.env.local` and report missing credentials in the install report.
