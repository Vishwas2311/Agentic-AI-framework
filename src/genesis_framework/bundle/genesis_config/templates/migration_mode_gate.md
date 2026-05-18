<!-- GENESIS PIPELINE TEMPLATE — Migration Output Mode Gate (Stage 7) -->
<!-- RENDER RULE: Load this file and display it VERBATIM.                   -->
<!-- Replace {{APP_NAME}} and {{STACK_LABEL}} with live values.             -->
<!-- All three options A/B/C must always appear. Never drop any option.     -->

## Migration Output Mode Gate
**{{APP_NAME}}** · Stage 7

Stack locked: **{{STACK_LABEL}}**

Which delivery mode should Genesis target for this migration?

---

**A. Production E2E App**
`Full Production` · `Complete DevOps` · `Deploy-Ready`
Genesis builds the complete application end-to-end with all production requirements — auth, routing, data layer, CI/CD, IaC, monitoring, testing, and full DevOps hand-off package. Takes longer but the output is ready to deploy to a live environment without further engineering work.

---

**B. Hybrid Pilot App**
`RECOMMENDED DEFAULT` · `Pilot Build` · `Production Path Included`
Genesis builds a working pilot app with core features complete and a production upgrade path documented alongside it. Faster delivery. The DevOps team receives the pilot plus a clear migration spec for the full production build.

---

**C. Local Demo App**
`Demo Only` · `No DevOps` · `Fastest Delivery`
Genesis builds a locally runnable demo app — no CI/CD, no deployment manifests, no production infrastructure. Suitable for internal stakeholder demonstrations only. Not ready for any live environment.

---

Which delivery mode? **(A / B / C)**
