# DESIGN.md — Hospital Online Consultation Portal
## Genesis Design System · Healthcare Domain · Polished Client Demo

---

## Design Principles

1. **Trust first** — Every visual decision reinforces patient confidence: clean space, strong contrast, calm palette.
2. **Accessible by default** — WCAG AA contrast minimum, visible labels, keyboard nav, 44px touch targets.
3. **Task-first layout** — Operational screens (dashboard, consultations) use full available width efficiently. No marketing containers around patient workflows.
4. **Subtle motion only** — Hover feedback, toast notifications, page transitions. No decorative animation on data tables.
5. **Calm and compact** — Healthcare density: enough space to breathe, enough density to scan efficiently.

---

## Color System

| Token | Value | Use |
|-------|-------|-----|
| `primary` | `#0891b2` | Buttons, links, active nav, focus rings |
| `primary-dark` | `#0e7490` | Button hover, headings |
| `primary-light` | `#cffafe` | Selected state backgrounds, light badges |
| `background` | `#f0f9ff` | Page background |
| `surface` | `#ffffff` | Cards, modals, panels |
| `surface-secondary` | `#f8fafc` | Sidebar, table header |
| `border` | `#e0f2fe` | Card borders, dividers |
| `text-primary` | `#0c4a6e` | Headings, labels |
| `text-secondary` | `#475569` | Body text, descriptions |
| `text-muted` | `#94a3b8` | Placeholder, disabled, hints |
| `success` | `#16a34a` | Completed status, available prescription |
| `success-bg` | `#dcfce7` | Completed badge background |
| `warning` | `#d97706` | Scheduled status, pending |
| `warning-bg` | `#fef9c3` | Scheduled badge background |
| `error` | `#dc2626` | Cancelled status, errors |
| `error-bg` | `#fee2e2` | Cancelled badge background |
| `info` | `#0891b2` | Requested, in-consultation status |
| `info-bg` | `#cffafe` | Info badge background |

---

## Typography

**Font Family:** Inter (Google Fonts), fallback system-ui, sans-serif

| Level | Size | Weight | Use |
|-------|------|--------|-----|
| Display | 2.25rem | 700 | Hero page titles |
| H1 | 1.875rem | 600 | Page headings |
| H2 | 1.5rem | 600 | Section headings |
| H3 | 1.25rem | 600 | Card titles, metric values |
| Body | 1rem | 400 | General body text |
| Small | 0.875rem | 400 | Helper text, timestamps |
| Label | 0.875rem | 500 | Form labels, nav items |
| Caption | 0.75rem | 400 | Badges, fine print |

---

## Spacing Scale

Base unit: 4px (0.25rem)

| Scale | Value | Use |
|-------|-------|-----|
| 1 | 4px | Micro gaps |
| 2 | 8px | Tight pairs |
| 3 | 12px | Form element gaps |
| 4 | 16px | Card internal padding |
| 5 | 20px | Section sub-spacing |
| 6 | 24px | Card padding |
| 8 | 32px | Section gap |
| 10 | 40px | Page section spacing |
| 12 | 48px | Hero / large gaps |

---

## Component Patterns

### Login — Auth Split Screen
- Left panel: 40% width, teal gradient (#0891b2 → #0e7490), white logo + hospital name + trust tagline
- Right panel: 60% width, white background, login card centered vertically, max-width 480px
- Card: white, rounded-xl, shadow-md, 40px padding

### Dashboard — Portal Dashboard (Task First Wide)
- Sidebar: 240px fixed, white, border-r sky-100, vertical nav with icons + labels
- Main: fills remaining width up to 1280px, px-6 py-8
- Metric cards: 4-column grid on lg, 2-col on md, 1-col on sm

### Consultation List — Dense Workspace
- Filter bar: horizontal flex, status pills + search input
- Consultation cards: white cards in vertical list, full available width
- Each card: 2-row layout — top row metadata, bottom row status + action

### Forms (Book, Prescriptions) — Operational Form
- Form card: white, max-width 760px, centered in main area
- Two-column layout for related field pairs on lg
- Labels above inputs, all required fields marked

---

## Motion Contract (Subtle — Healthcare)

| Element | Trigger | Animation | Duration |
|---------|---------|-----------|----------|
| Page sections | Mount | `fadeIn + translateY(8px→0)` | 200ms ease-out |
| Nav items | Hover | `background opacity 0→0.08` | 100ms |
| Cards | Hover | `shadow elevation change` | 150ms |
| Toast | Enter | `slideIn from right + fadeIn` | 200ms |
| Toast | Exit | `fadeOut` | 150ms |
| Metric cards | Mount | `stagger 50ms fadeIn` | 300ms |

All animations respect `prefers-reduced-motion` via `MotionConfig reducedMotion="user"`.

---

## Status Badge Colors

| Status | Text Color | Background | Border |
|--------|-----------|------------|--------|
| Requested | `#0891b2` | `#cffafe` | `#67e8f9` |
| Scheduled | `#d97706` | `#fef9c3` | `#fcd34d` |
| In Consultation | `#7c3aed` | `#ede9fe` | `#c4b5fd` |
| Completed | `#16a34a` | `#dcfce7` | `#86efac` |
| Cancelled | `#dc2626` | `#fee2e2` | `#fca5a5` |

---

## Accessibility

- Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text
- Focus rings: 2px solid `#0891b2`, 2px offset
- All inputs: `id` + `htmlFor` label pairing
- Buttons: descriptive aria-labels where icon-only
- Status badges: include text label (not color-only)
- Playwright locators: heading roles, button text, label text (no hidden labels)
