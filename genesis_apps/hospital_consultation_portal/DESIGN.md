# Design System — Hospital Online Consultation Portal
## UI/UX Pro Max Design Direction

**Domain:** Healthcare Patient Portal  
**Mode:** Enterprise density — calm, trusted, clinically appropriate  
**Audience:** Non-technical patients; hospital admin demo audiences  
**Motion Intensity:** Subtle  
**Accessibility:** WCAG AA target  

---

## Color Palette

| Token | Value | Use |
|---|---|---|
| `primary-blue` | `#1a73e8` | Primary actions, headings, metric values |
| `primary-blue-hover` | `#1557b0` | Button hover state |
| `bg-white` | `#ffffff` | Card backgrounds, form backgrounds |
| `bg-page` | `#f8fafc` | Page background (Streamlit default) |
| `border-subtle` | `#e8edf2` | Card borders, dividers |
| `text-primary` | `#1f2937` | Body text |
| `text-muted` | `#6b7280` | Labels, captions, secondary text |
| `success-green` | `#16a34a` | Completed status, success messages |
| `success-bg` | `#f0fdf4` | Completed badge background |
| `warning-amber` | `#d97706` | Requested status |
| `warning-bg` | `#fffbeb` | Requested badge background |
| `info-blue` | `#2563eb` | Scheduled status |
| `info-bg` | `#eff6ff` | Scheduled badge background |
| `error-red` | `#dc2626` | Cancelled status, error messages |
| `error-bg` | `#fef2f2` | Cancelled badge background |
| `purple` | `#7c3aed` | In Consultation status |
| `purple-bg` | `#f5f3ff` | In Consultation badge background |
| `demo-yellow` | `#ffc107` | Demo disclaimer banner border |
| `demo-yellow-bg` | `#fff3cd` | Demo disclaimer banner background |

## Typography

| Role | Family | Weight | Size |
|---|---|---|---|
| App heading (H1) | Inter, Segoe UI, system-ui | 700 | 2rem |
| Page heading (H2) | Inter, Segoe UI, system-ui | 600 | 1.5rem |
| Card heading | Inter, Segoe UI, system-ui | 600 | 1rem |
| Metric value | Inter, Segoe UI, system-ui | 700 | 2.2rem |
| Body | Inter, Segoe UI, system-ui | 400 | 1rem |
| Label / caption | Inter, Segoe UI, system-ui | 400 | 0.85rem |
| Badge | Inter, Segoe UI, system-ui | 600 | 0.8rem |

## Spacing & Layout

- Max content width: `1100px`
- Page padding top: `2rem`
- Card padding: `1.2rem 1.5rem`
- Card border radius: `10px`
- Card box shadow: `0 2px 8px rgba(0,0,0,.06)`
- Section gap: `1.5rem`
- Login card max-width: `420px`, centered

## Component Rules

### Status Badges
- Rendered inline via HTML spans with color-coded backgrounds
- Never use bare text for status — always use badge styling
- All 5 statuses have distinct color tokens

### Metric Cards
- 5 cards in a single row on dashboard
- Large numeric value (2.2rem) in primary blue
- Small label in muted grey
- Icon prefix on value for accessibility

### Consultation Cards
- Left-aligned text layout
- Status badge inline with patient name
- Secondary info (department, doctor, mode, date) in muted small text
- Symptoms in grey small text if present
- Status update selectbox below card, full width

### Forms
- All fields use `st.form()` to batch submissions
- Visible labels on all inputs (no hidden labels)
- Placeholder text as guidance, not as labels
- Primary action button at bottom, full width, `type="primary"`
- Caption with demo disclaimer inside form

### Demo Disclaimer Banner
- Yellow background banner at top of every authenticated page
- Text: "⚠️ Demo system. Do not enter real patient data."
- Font size: 0.8rem

## Motion Policy (Subtle)
- No page transitions
- Streamlit default loading states acceptable
- `st.balloons()` on successful consultation booking — purposeful, celebratory
- No decorative animation on data tables or lists

## Accessibility Requirements
- All form inputs have visible labels
- All buttons have clear action names
- Color not the only differentiator for status (icon + color)
- Minimum text contrast ratio: 4.5:1 (WCAG AA)
- All interactive elements reachable by keyboard
- Streamlit's built-in focus management respected
