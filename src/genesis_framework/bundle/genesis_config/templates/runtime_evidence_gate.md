<!-- GENESIS PIPELINE TEMPLATE — Runtime Evidence Gate (Stage 16) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- runtime_evidence_gate data, then display verbatim. Never shorten.      -->

## Runtime Evidence Gate
**{{APP_NAME}}** · Stage 16 · Gate 6 of 14

Source type: **{{SOURCE_TYPE}}** · Runtime captures found: **{{CAPTURE_COUNT}}**

Runtime evidence (live screen recordings, browser captures, or API trace logs) increases extraction accuracy. Decide whether to add captures now or waive them and proceed on static sources only.

---

**A. Proceed without runtime captures** `RECOMMENDED`
`Static Sources Only` · `Waive Runtime Evidence` · `Faster`
Genesis uses BRD documents, images, and design specs only. Sufficient for BRD-input migrations where the app does not yet exist in a live environment.

---

**B. Add runtime evidence now**
`Capture Now` · `Higher Accuracy` · `Live App Required`
Provide a URL or screen recording for Genesis to capture live runtime behavior. This increases extraction confidence by 5–15% for existing applications.

---

**C. Waive runtime evidence permanently**
`Permanent Waiver` · `Skip All Captures`
Record that runtime evidence is intentionally excluded from this migration run. Genesis will not prompt for it again in this pipeline execution.

---

Which decision? **(A / B / C)**
