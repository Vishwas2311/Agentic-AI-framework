# Install Genesis E2E

When the user says `install Genesis E2E`, `install NoCode2ProCode E2E`, `setup Genesis fully`, or asks to install all Genesis prerequisites on a copied machine, run the local full installer from the project root.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullLocal -AllowSystemInstall -IncludeSecurityTools
```

Expected behavior:

- Create `.venv`
- Install the Genesis CLI and Python libraries
- Install local E2E, QA, security, and browser-support libraries
- Install local Node packages for Playwright, visual QA, API tooling, and Motion
- Install Chromium for Playwright
- Copy Genesis Claude command files
- Copy the Genesis skill into the Claude skills folder
- Create `.env.local` from `.env.example` when missing
- Validate Genesis configuration
- Write `.genesis_runtime/install_report.md`
- Open `Full User Manual - Genesis.html` after successful install
- Continue without exposing secrets

If deployment tooling is explicitly requested, add `-IncludeDeploy`.
If the user wants terminal-only installation, add `-NoLaunchManual`.

Never hardcode or print secrets. For GitHub, Figma, 21st.dev Magic, Firecrawl, E2B, PostgreSQL, Claude account access, or other cloud/MCP integrations, preserve placeholders in `.env.local` and report missing credentials in the install report.
