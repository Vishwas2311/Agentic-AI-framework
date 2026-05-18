# Genesis Estimation Report
## Hospital Online Consultation Portal

| Field | Value |
|---|---|
| **Report Type** | Dry-Run Discovery & Estimation |
| **Input Source** | `Hospital_Online_Consultation_Portal_BRD.docx` |
| **Source Type** | BRD Document (Structured Text Specification) |
| **Migration Mode** | `greenfield_from_spec` |
| **Target Stack** | Streamlit (Python 3.x) |
| **Generated** | 2026-05-05 |
| **Genesis Version** | 3.1.0 |
| **Stage** | `dry_run_estimate` (No production code generated) |

---

## 1. Executive Summary

The input is a **complete, well-structured BRD** for a Hospital Online Consultation Portal — a demo-grade Streamlit web application. This is a **greenfield generation from specification**, not a migration from a no-code platform. No existing application code, platform export, or runtime evidence exists to resolve against.

The BRD is unusually detailed for a specification-to-code path: it defines 7 UI sections, 10 functional requirement groups, 10 happy-path test cases, explicit file requirements, acceptance criteria, and a demo disclaimer. Confidence is correspondingly high.

**Overall Dry-Run Confidence: 0.93**  
**Estimated Total Effort: 14.5 – 18.5 hours**  
**Estimated Token Cost: $6 – $18 USD**  
**Human Review Gates Required: 1 (design theme — mockup images referenced but not provided)**

---

## 2. Source Discovery Results

### 2.1 Source Classification

| Attribute | Value |
|---|---|
| Source kind | BRD document |
| Source format | `.docx` (structured prose + structured requirements) |
| Platform | None (no no-code/low-code platform involved) |
| Runtime evidence available | No (app does not exist yet) |
| Figma / design files | No |
| Mockup images | Referenced (Figure 1–9) but **not provided** — text descriptions only |
| API contracts | Not provided (not required — in-memory app) |
| Database schema | Not provided (not required — `st.session_state` only) |
| Sample credentials | Included: `patient@example.com` / `patient123` |

### 2.2 Source Completeness Assessment

| BRD Section | Completeness | Notes |
|---|---|---|
| Executive summary | Complete | Clear scope and intent |
| Business goal | Complete | Demo hospital portal |
| Target users | Complete | 5 roles defined; primary = Patient |
| Core features | Complete | 15 features listed |
| Page designs (5.1–5.8) | Partial | Text descriptions only, no actual image assets |
| Functional requirements (6.1–6.9) | Complete | Detailed per-section |
| Sample credentials | Complete | Username + password provided |
| Data fields & values | Complete (embedded) | Dropdowns fully specified |
| Metrics | Complete | 5 metrics defined |
| Happy-path test cases (TC_001–TC_010) | Complete | 10 step-by-step tests |
| UI requirements | Complete | 12 requirements |
| Accessibility requirements | Complete | 5 requirements |
| Security/privacy requirements | Complete | 5 requirements |
| Technical requirements | Complete | File names, library, patterns specified |
| Expected output files | Complete | 11 files listed |
| Acceptance criteria | Complete | 13 pass/fail criteria |
| Demo disclaimer | Complete | Explicit — no real medical data |

**Source completeness score: 0.94** — only gap is the missing visual mockup images (Figures 1–9).

---

## 3. Scope Breakdown

### 3.1 Application Sections (7)

| # | Section | Type | Complexity |
|---|---|---|---|
| 1 | Login Page | Auth gate | Low |
| 2 | Welcome Page | Info/CTA | Low |
| 3 | Main Dashboard | Metrics + Quick Actions | Medium |
| 4 | Book Consultation | Form (10 fields) | Medium |
| 5 | My Consultations | List + Filter + Search + Status Update | High |
| 6 | Prescription / Medical Summary | Conditional display | Medium |
| 7 | Sign Out | Session clear + confirmation | Low |

### 3.2 Files to Generate (15)

| File | Category | Notes |
|---|---|---|
| `app.py` | UI | Main Streamlit app with 7 sections |
| `consultation_logic.py` | Logic | Booking, filtering, search, status, metrics, prescription |
| `test_app.py` | Unit tests | Logic unit tests (~15 test functions) |
| `ui_test.py` | UI tests | Playwright happy-path tests (TC_001–TC_010) |
| `app_contract.json` | Spec | App data contract |
| `brd_analysis.json` | Spec | BRD parsed analysis |
| `ui_design_plan.json` | Design | UI layout and component plan |
| `test_plan.json` | QA | Test plan aligned to acceptance criteria |
| `traceability_matrix.json` | QA | Requirement ↔ test case mapping |
| `bug_report.md` | QA | Post-run bug tracking |
| `final_report.md` | Delivery | APPROVED/REJECTED + summary |

### 3.3 Key Data Entities

| Entity | Fields | Cardinality |
|---|---|---|
| Consultation | patient_name, age, gender, department, doctor, mode, status, date, time, symptoms | 0..N (session) |
| Session State | logged_in, consultations[], current_user | Singleton |

### 3.4 Dropdown Values (Hard-coded per BRD)

| Dropdown | Values |
|---|---|
| Gender | Male, Female, Other |
| Department | General Medicine, Cardiology, Dermatology, Orthopedics, Pediatrics, Neurology |
| Doctor | Dr. Mehta, Dr. Sharma, Dr. Rao, Dr. Iyer, Dr. Khan |
| Consultation Mode | Video Call, Audio Call, Chat |
| Consultation Status | Requested, Scheduled, In Consultation, Completed, Cancelled |
| Status Filter | All, Requested, Scheduled, In Consultation, Completed, Cancelled |

---

## 4. Risk Assessment

### 4.1 Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Mockup images not provided — UI theme chosen by generator | High | Low | Use BRD text descriptions + healthcare domain defaults; flag for human review |
| R-02 | `st.session_state` resets on full page re-run (Streamlit behavior) | Medium | Medium | Use `st.session_state` initialization guard in app.py |
| R-03 | Playwright tests fragile on dynamic Streamlit widget keys | Medium | Medium | Use accessible text/label locators per BRD accessibility requirements |
| R-04 | Status update workflow requires careful state mutation | Low | Medium | Test TC_005 and TC_006 explicitly in unit tests |
| R-05 | No database — data lost on app restart | Low | Low | Accepted per BRD (demo system, no real patient data) |
| R-06 | BRD references "sample credentials" table (Section 7) — table content not extracted | Low | Low | Use `patient@example.com` / `patient123` confirmed in TC_001 |

### 4.2 Unsupported Items

| Item | Reason | Strategy |
|---|---|---|
| Visual mockup images (Figures 1–9) | Not included in `.docx` — only referenced by caption | Generate UI from text descriptions; use healthcare domain design defaults |
| Real database persistence | Explicitly prohibited by BRD (Section 13) | Use `st.session_state` only |
| Real authentication/authorization | Explicitly prohibited by BRD (Section 13/17) | Demo credentials only (`patient@example.com` / `patient123`) |
| Real medical advice / prescriptions | Explicitly prohibited by BRD (Section 17) | Placeholder text + "demo prescription summary" disclaimer |
| Doctor availability / scheduling logic | Not specified in BRD | Simple free-form date/time input with no conflict detection |

---

## 5. Effort Estimation

### 5.1 Effort Matrix Summary

| Phase | Tasks | Min Hours | Max Hours | Confidence |
|---|---|---|---|---|
| Source analysis & IR build | BRD parse, spec extraction, canonical spec | 0.5 | 1.0 | 0.97 |
| Design system | Tokens, component registry, design plan | 1.0 | 1.5 | 0.90 |
| Code generation — logic | `consultation_logic.py` (6 function groups) | 1.5 | 2.5 | 0.95 |
| Code generation — UI | `app.py` (7 sections, session state, routing) | 3.0 | 4.5 | 0.93 |
| Spec artifact generation | `app_contract.json`, `brd_analysis.json`, `ui_design_plan.json`, `test_plan.json`, `traceability_matrix.json` | 1.0 | 1.5 | 0.97 |
| Test generation — unit | `test_app.py` (~15 test functions) | 1.5 | 2.0 | 0.95 |
| Test generation — UI | `ui_test.py` (Playwright, 10 TCs) | 2.0 | 3.0 | 0.88 |
| Quality gates | Build check, unit test run, Playwright run | 1.0 | 1.5 | 0.93 |
| Visual QA & design quality | Screenshot, accessibility scan | 0.5 | 0.75 | 0.88 |
| Reports & final delivery | `bug_report.md`, `final_report.md`, replay dashboard | 1.5 | 1.75 | 0.97 |
| **TOTAL** | | **14.5** | **18.5** | **0.93** |

### 5.2 Lines of Code Estimate

| File | Estimated LOC |
|---|---|
| `app.py` | 350 – 500 |
| `consultation_logic.py` | 120 – 180 |
| `test_app.py` | 150 – 200 |
| `ui_test.py` | 200 – 280 |
| **Total** | **820 – 1,160** |

---

## 6. Cost Estimate

| Resource | Estimate | Basis |
|---|---|---|
| LLM tokens (generation + QA) | ~250,000 – 450,000 tokens | 7 pages + 4 test files + 5 JSON specs |
| Estimated LLM cost | $3 – $10 USD | Claude Sonnet 4.6 pricing |
| E2B sandbox execution | ~20 – 40 min | Build + unit tests + Playwright run |
| E2B cost | $1 – $5 USD | E2B compute pricing |
| Firecrawl / Playwright crawl | 0 pages | No URL source — not needed |
| **Total estimated cost** | **$4 – $15 USD** | Within budget ($500 max) |

---

## 7. Design Strategy Preview

| Decision | Value | Reason |
|---|---|---|
| Source material | Text-only BRD + section descriptions | No images, URL, or Figma provided |
| Magic creation type | `from_scratch` | No reference URL available |
| Magic project type | `website` | Full multi-section app |
| Website goal | `custom` (portal/enterprise) | Patient portal, not a marketing or sales site |
| UI/UX Pro Max mode | Enterprise density — calm, trusted, healthcare-professional | Healthcare domain; primary user is a patient |
| Motion intensity | `subtle` | Healthcare app — hover feedback, skeleton loading, status transitions only |
| Color direction | Clean white/blue-grey palette, accessible contrast ratios, WCAG AA | Hospital trust palette |
| Font pairing | Inter or similar clean sans-serif for readability | Accessibility + clinical trust |

**Human review required:** Design theme selection (Figure 1–9 mockup images not available). Generator will propose a healthcare design system based on text evidence; human should confirm before full UI generation.

---

## 8. Acceptance Criteria Pre-Check

| AC | Description | Pre-Check Result |
|---|---|---|
| AC-01 | Patient can log in | Ready — credentials in BRD |
| AC-02 | Welcome/dashboard visible after login | Ready |
| AC-03 | Book consultation | Ready — all form fields defined |
| AC-04 | Booked consultation in My Consultations | Ready |
| AC-05 | Status update works | Ready — workflow defined in FR 6.5 |
| AC-06 | Status filter works | Ready — filter values defined |
| AC-07 | Search works | Ready — 3 search criteria defined |
| AC-08 | Metrics update correctly | Ready — 5 metrics defined |
| AC-09 | Prescription shows Available for Completed | Ready — logic defined in FR 6.8 |
| AC-10 | Sign out clears state | Ready |
| AC-11 | Returns to login after sign out | Ready |
| AC-12 | All happy path tests pass | Conditional — depends on Playwright locators |
| AC-13 | App does not crash during normal flow | Conditional — requires sandbox validation |

**Pre-check pass rate: 11/13 ready, 2 conditional** (require sandbox execution)

---

## 9. Recommended Next Steps

1. **Run `/genesis-migrate`** — all inputs are sufficient for full migration.
2. **Design review gate** — confirm healthcare design theme before UI generation (no mockup images available).
3. **Playwright locator strategy** — use `getByLabel()` and `getByRole()` per BRD accessibility requirements to maximize test stability.
4. **Sandbox run** — validate unit tests and Playwright tests inside E2B before delivery.
5. **Final report gate** — require APPROVED status from `final_report.md` before any delivery.

---

## 10. Policy Gate Status

| Policy Rule | Status |
|---|---|
| `no_raw_secrets_to_agents` | Pass — credentials are demo-only, low sensitivity |
| `pii_requires_masking` | Pass — demo disclaimer in BRD; no real PHI |
| `low_confidence_requires_review` | Pass — overall confidence 0.93 > 0.75 threshold |
| `protected_media_requires_review` | Pass — no protected media detected |
| `source_truth_conflict_blocks_generation` | Pass — single source, no conflicts |
| `generated_code_must_pass_sandbox` | Pending — sandbox not run (dry-run only) |
| `sbom_required_before_pr` | Pending — pre-generation |
| `deploy_requires_human_approval` | Pending — pre-generation |
