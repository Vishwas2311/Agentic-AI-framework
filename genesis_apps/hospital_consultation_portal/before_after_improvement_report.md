# Before/After Improvement Report
## Hospital Online Consultation Portal

### Preserved from Source (BRD)
- All 7 pages: Login, Welcome, Dashboard, Book, Consultations, Prescriptions, Sign Out
- All 10 happy-path test cases (TC_001-TC_010)
- Patient journey: Login > Welcome > Dashboard > Book > Track > Prescription > Sign Out
- Consultation data model (all 12 fields), sample credentials, demo disclaimers
- Status lifecycle and prescription availability logic
- Filter + search + live metric updates

### Improved from Source
- Stack: Streamlit upgraded to Next.js 14 + Tailwind + shadcn/ui + motion/react (user decision)
- Layout: proper React sidebar nav vs Streamlit approximation
- Visual fidelity: pixel-matched to BRD mockups via extracted design tokens
- Accessibility: WCAG 2.1 AA (focus rings, aria-labels, role=alert, password toggle)
- TypeScript: full type safety, zero tsc errors

### Intentionally Changed
- Stack upgrade per explicit user decision (recorded in stack_decision_report.json)
- In-memory React state (same behavior as st.session_state - resets on reload)

### Remaining Risks
- Page reload clears session (demo limitation, same as BRD Streamlit design)
- Google Fonts requires internet connection on first load
