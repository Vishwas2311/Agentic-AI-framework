# NoCode2ProCode by TrustEngines Governance

Claude Code is the runtime spine for Genesis. Do not improvise the migration flow from the user prompt alone.

## Execution Rule

If the user says **install Genesis E2E**, **install NoCode2ProCode E2E**, **setup Genesis fully**, or any close variation, treat it as the framework bootstrap command. From the project root, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullPipeline -AllowSystemInstall
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

## Gate Display Rule

**This rule applies to every human-approval gate shown during any pipeline run.**

Gate templates are stored verbatim in `.genesis/templates/`. When showing any gate,
load the matching template file and render it EXACTLY as written — every section,
every bullet, every sub-heading, every separator. Do NOT summarise, shorten, reorder,
or collapse any part of the template.

| Gate | Template file |
|------|--------------|
| BRD Understanding Gate (Stage 4) | `.genesis/templates/brd_understanding_gate.md` |
| Stack Decision Gate (Stage 5) | `.genesis/templates/stack_decision_gate.md` |
| Migration Output Mode Gate (Stage 7) | `.genesis/templates/migration_mode_gate.md` |
| Generated App Approval Gate | `.genesis/templates/generated_app_gate.md` |

**Substitution rule:** Replace `{{PLACEHOLDER}}` tokens with live values from the
current run. All other content is rendered verbatim — never rewritten.

**Hard rules that must never be broken:**
- Option letter + label: always **bold**
- Tags: always backtick-wrapped `` `Tag` · `Tag` `` on the same line as the label
- Description: always normal text below the tags line
- Separator: always `---` between every option — never omit it
- Option A of the Stack Decision Gate: always shows ALL DevOps deliverable sub-sections
  (Containerisation, CI/CD Pipeline, Environment & Secrets, Infrastructure as Code,
  Security, CDN & Performance, Load Balancing & Scaling, Database Layer, DNS & Domain,
  Monitoring & Observability, Testing, HIPAA Compliance, Backup & Disaster Recovery,
  Documentation) — every bullet under every sub-section must appear every time
- Closing prompt: always on its own line — `Which stack? **(A / B / C / D / E)**`
- **Never** use plain numbered lists (1. 2. 3.) for gate options
- **Always** mark the Genesis-recommended option with a `RECOMMENDED` tag
- **Never** drop any option from any gate — all options must always be shown

## Output Sandbox Rule

**This is a strict, non-negotiable guardrail for every migration, generation, and pipeline execution.**

### Rule 1 — Project folder required
At the start of every migration run, create a project folder named after the migration project or software being migrated (e.g. `Hospital_Online_Consultation_Portal`). ALL output for that migration MUST go inside:

```
workspace/output/{project_name}/
```

Never write migration files directly into `workspace/output/` — they must always be one level deeper, inside the project folder. Every subpath (artifacts, generated_app, design_ir, docs, deploy, etc.) lives under `workspace/output/{project_name}/`.

### Rule 2 — Framework is read-only during migration
NEVER write files to the project root, `src/`, `scripts/`, `.genesis/`, `.claude/`, `tools/`, or any other framework directory during a migration run. The framework itself is read-only at runtime.

### Rule 3 — No files outside the project output folder
NEVER write files anywhere outside `workspace/output/{project_name}/`. This applies to: artifact JSON files, reports, generated app code, design files, canonical specs, QA reports, replay dashboards, deployment files, temporary scripts, and ALL other pipeline outputs.

### Rule 4 — Enforce at every step
This rule applies to every stage, every agent, every repair loop iteration, and every tool call in the pipeline. If any write would land outside `workspace/output/{project_name}/`, STOP immediately and report the path violation instead of writing.

## Verification Rule

No generated app is approved until build, tests, visual QA, accessibility, security, SBOM, policy, replay, and evidence gates pass or are explicitly waived by a human.

