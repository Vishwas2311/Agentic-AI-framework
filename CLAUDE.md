# NoCode2ProCode by TrustEngines Governance

Claude Code is the runtime spine for Genesis. Do not improvise the migration flow from the user prompt alone.

## Execution Rule

If the user says **install Genesis E2E**, **install NoCode2ProCode E2E**, **setup Genesis fully**, or any close variation, treat it as the framework bootstrap command. From the project root, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullLocal -AllowSystemInstall -IncludeSecurityTools
```

This installs local prerequisites, Python packages, Node/browser/UI tooling, Playwright Chromium, visual QA tooling, API tooling, Genesis Claude commands, Genesis skills, and local validation reports. Do not invent or request raw secrets in chat. If cloud/MCP credentials are needed, create or preserve `.env.local` from `.env.example`, validate what is present, and report missing credentials in `.genesis_runtime/install_report.md`.

After successful installation, the installer should open the project-local Genesis Full User Manual HTML so the user immediately sees the onboarding, commands, pipeline, agents, capabilities, and next migration steps. If the user asks for terminal-only setup, add `-NoLaunchManual`.

When a user asks for a Genesis migration, read these files first:

1. `.genesis/genesis.flow.yaml`
2. `.genesis/genesis.stack.yaml`
3. `.genesis/genesis.tools.yaml`
4. `.genesis/genesis.policy.yaml`
5. `.genesis/genesis.agents.yaml`
6. `.genesis/genesis.capabilities.yaml`
7. `.genesis/genesis.design.yaml`
8. `.genesis/genesis.design_quality.yaml`
9. `.genesis/genesis.outputs.yaml`

The user prompt tells Genesis what to migrate. The Genesis files tell Claude how to migrate it.

## BRD Stack Rule

For BRD/DOCX/PDF inputs, preserve the BRD's features, pages, workflows, data fields, user journey, tests, and acceptance criteria. Do not treat the BRD's technical stack as final when it conflicts with the user's delivery intent.

If the BRD says Streamlit but the user asks for NoCode2ProCode, proper software, pro-code, production, enterprise, or beyond-expectation quality, create `stack_decision_report.json` and `delivery_mode_decision.json` before generation. Ask one concise question if the correct stack cannot be inferred.

For UI-heavy production portals, dashboards, websites, and patient/customer-facing web apps, prefer the premium web profile: `Next.js + Tailwind + shadcn/ui + Motion`, directed by UI/UX Pro Max and componentized with 21st.dev Magic.

Do not silently choose Streamlit, Gradio, notebooks, or static-only stacks for `production_procode` or `enterprise_migration`. Those stacks are prototype-only unless the user explicitly requests them and the decision is recorded with human approval.

`same software` means same behavior and user journey, not necessarily same prototype stack. `same location` means output path, not stack lock.

Never mark final output APPROVED from functional tests alone. Approval requires stack decision, design decision, visual/design QA, design quality score, visual rejection report, and before/after improvement report.

## Tool Rule

Use only tools allowed for the active stage. If a tool is not listed, treat it as denied.

## Secret Rule

Never request or expose raw secrets in prompts, logs, generated files, reports, or agent context. Use scoped credentials through the vault or MCP gateway.

## Generation Rule

Generate from `canonical_app_spec.json`, not directly from vague prompt memory. If the canonical spec is missing, build it before generating code.

## Design Rule

Before UI generation, run the Genesis design strategy decision from `.genesis/genesis.design.yaml`.
It must decide:

- source material: uploaded image, URL, Figma URL, logo, text brief, existing code, or low-code export
- source usage: primary evidence, style DNA, brand seed, UX audit baseline, or product brief
- 21st.dev Magic project type: `component` or `website`
- 21st.dev Magic creation type: `from_scratch` or `get_inspired`
- website goal: `lead_generation`, `drive_sales`, `interactive_quiz`, `subscriptions`, or `custom`
- UI/UX Pro Max mode and page-level design brief
- Motion intensity and accessibility policy

Improve by default: make the UI cleaner, more accessible, more responsive, and more polished than the input while preserving the requested source truth. URL inputs must be crawled/inspected before choosing full website vs component rebuild. Uploaded images must be treated as evidence, even when Magic creation type is `from_scratch`.

UI/UX Pro Max is the design director. It must create or update:

- `DESIGN.md`
- `design_tokens.json`
- `component_registry.json`
- `visual_acceptance_criteria.md`

Use 21st.dev Magic only after the Magic selection is written. Use Motion only when the motion plan gives a purpose, allowed pattern, reduced-motion fallback, and QA check.

For premium web UI runs, the preferred automation chain is:

- UI/UX Pro Max -> design director, design system, density, layout profile, viewport-fit plan
- 21st.dev Magic -> component/page generation aligned to the selected component pattern
- Motion -> purposeful interaction and transition layer after UI generation
- Claude Code -> orchestration, repair loop, integration, and quality enforcement

## Verification Rule

No generated app is approved until build, tests, visual QA, accessibility, security, SBOM, policy, replay, and evidence gates pass or are explicitly waived by a human.
