<!-- GENESIS PIPELINE TEMPLATE — Source Truth Approval Gate (Stage 18) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- source_truth_approval_gate data, then display verbatim. Never shorten. -->

## Source Truth Approval Gate
**{{APP_NAME}}** · Stage 18 · Gate 8 of 14

Genesis resolved **{{CONFLICT_COUNT}} conflict(s)** between input sources. Review resolutions before the IR is built.

---

**Conflict resolutions:**

{{CONFLICT_LIST}}

---

**A. Approve all resolutions** `RECOMMENDED`
`Accept Resolutions` · `Proceed to IR Build`
All conflict resolutions are correct. Genesis uses the resolved source truth as the single authoritative input for the Universal Low-Code IR.

---

**B. Override a specific resolution**
`Override Conflict` · `Manual Resolution`
One or more conflict resolutions are wrong. Tell Genesis which field to override and what the correct value is. The resolution will be updated before IR construction.

---

**C. Add evidence to resolve a conflict**
`Add Evidence` · `Upload or Describe`
A conflict cannot be resolved from existing sources. Provide additional evidence (a document, description, or rule) and Genesis will re-evaluate the conflict before proceeding.

---

Which decision? **(A / B / C)**
