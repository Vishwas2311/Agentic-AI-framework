<!-- GENESIS PIPELINE TEMPLATE — BRD Understanding Gate (Stage 4) -->
<!-- RENDER RULE: Load this file and display it VERBATIM after the BRD summary. -->
<!-- Replace {{APP_NAME}}, {{CONFIDENCE}}, {{SCREEN_COUNT}}, {{FEATURE_COUNT}} -->
<!-- with live values. All options A–F must always appear. Never drop any option. -->

## BRD Understanding Gate
**{{APP_NAME}}** · Stage 4 · Confidence: **{{CONFIDENCE}}%**

Genesis extracted the following from your BRD:

- **{{SCREEN_COUNT}} screens** — {{SCREEN_NAMES}}
- **{{ROLE_COUNT}} roles** — {{ROLE_NAMES}}
- **{{FEATURE_COUNT}} functional requirements** extracted
- **{{WORKFLOW_COUNT}} workflows** confirmed
- **{{ACCEPTANCE_COUNT}} acceptance criteria / test cases** captured
- **{{IMAGE_COUNT}}** — {{IMAGE_NOTE}}
- **Stack conflict flagged** — {{STACK_CONFLICT_NOTE}}

Please give one decision before Genesis proceeds to stack selection:

---

**A. Approve**
`Proceed Immediately`
Understanding is correct. Use the extracted BRD plan as the source of truth for all downstream planning, stack selection, and code generation.

---

**B. Approve with assumptions**
`Proceed with Notes`
Correct overall but something may have been missed. Genesis will carry the assumption notes visibly into downstream stages so nothing is silently dropped.

---

**C. Add missing evidence**
`Pause Pipeline`
I want to add images, a logo, correct a feature, or provide business clarification before Genesis continues. Pipeline pauses until evidence is added.

---

**D. Edit BRD**
`Semantic Patch`
I want to change something in what Genesis understood. Tell Genesis what to change — it will apply a semantic patch and show the updated understanding before proceeding.

---

**E. Auto-close gaps (Claude + cross-reference)**
`Gap Engine` · `70% Target` · `Stage 4 Wired`
Run the BRD gap-closing engine: cross-reference all artifacts and ask Claude targeted questions per WARN/BLOCK item until average confidence reaches 70%. Fully wired at Stage 4 — no semantic graph required.

---

**F. Force 100% coverage (max confidence push)**
`Gap Engine` · `95% Target` · `Stage 4 Wired`
Run the BRD gap-closing engine at maximum intensity — 95% confidence target, looping across all screens, workflows, acceptance criteria, and security constraints until all areas are evidence-backed or max iterations exhausted. Fully wired at Stage 4 — no semantic graph required.

---

Which decision? **(A / B / C / D / E / F)**
