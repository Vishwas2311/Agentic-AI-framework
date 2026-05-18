<!-- GENESIS PIPELINE TEMPLATE — Source Discovery Gate (Stage 11) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- source_discovery_gate data, then display verbatim. Never shorten.      -->

## Source Discovery Gate
**{{APP_NAME}}** · Stage 11 · Gate 5 of 14

Genesis has scanned all input sources. Review the discovered inventory before extraction begins.

---

**Sources discovered: {{SOURCE_COUNT}}**

Documents:
{{DOC_LIST}}

Separate image files:
{{IMAGE_LIST}}

Embedded media (inside DOCX/PDF): **{{EMBEDDED_COUNT}}** items

---

**A. Approve — all sources are correct**
`Approve Sources` · `Begin Extraction`
The source inventory is complete and accurate. Genesis proceeds to extract screens, workflows, entities, and components from all listed sources.

---

**B. Add a missing source**
`Add Source` · `Upload or Link`
One or more inputs are missing. Provide the path, URL, or file and Genesis will re-scan before extraction.

---

**C. Mark a source as irrelevant**
`Remove Source` · `Narrow Scope`
One or more discovered items should not be used. Tell Genesis which to exclude and it will update the inventory before extraction begins.

---

Which decision? **(A / B / C)**
