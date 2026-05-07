# 21st.dev Magic Selector Prompt

Use this prompt before calling 21st.dev Magic.

Required selection:

- Project type: `component` or `website`
- Creation type: `from_scratch` or `get_inspired`
- Website goal: `lead_generation`, `drive_sales`, `interactive_quiz`, `subscriptions`, or `custom`
- Component/system target: shadcn/ui, Material UI, Angular Material, Tailwind, or custom enterprise library

Selection logic:

- `component`: buttons, cards, forms, metric cards, login panels, pricing cards, tables, filters, navbars, modals, empty states, loading states.
- `website`: complete page, dashboard, portal screen, landing page, checkout flow, settings screen, admin shell, multi-section page.
- `from_scratch`: no reference website URL flow. User may still provide screenshot, sketch, Figma export image, logo, low-code export, existing code, data/API shape, or text brief as source evidence.
- `get_inspired`: user gives website/reference URL. Use Firecrawl and Playwright evidence first, then choose full rebuild, modernized rebuild, or style inspiration according to user intent and license/privacy gates.
- `lead_generation`: forms, booking, quote, demo, inquiry, contact.
- `drive_sales`: product, pricing, cart, checkout, ecommerce.
- `interactive_quiz`: assessment, survey, recommender, onboarding, configurator.
- `subscriptions`: plans, memberships, recurring billing, SaaS signup.
- `custom`: dashboards, portals, internal apps, workflows, regulated systems, migrations.

URL rules:

- URL + "rebuild this website/page/dashboard" means `website` + `get_inspired` + primary website evidence.
- URL + "make this card/navbar/form/sidebar like this" means `component` + `get_inspired` + component style reference.
- URL + "inspired by this" means style DNA only, not a clone.
- URL + "rebuild better" means preserve useful content/structure and improve UX, accessibility, responsiveness, and visual polish.
- Always inspect/crawl the URL before selecting content structure, page sections, navigation, and interaction behavior.

Image rules:

- Uploaded screenshot of full page/screen means `website` + `from_scratch` unless user asks for one component.
- Uploaded screenshot of one element means `component` + `from_scratch`.
- Uploaded sketch means `from_scratch` with professional interpretation.
- Uploaded brand/logo means extract design tokens before using Magic.
- Uploaded mobile screenshot means apply mobile safe areas, touch targets, thumb zones, and native-feel patterns.

Magic prompt requirements:

- Include domain, user role, task goal, target stack, component library, design tokens, states, responsive behavior, and accessibility requirements.
- Include exact source constraints from `visual_lock_spec.json` when fidelity mode is exact.
- Include whether the source is URL evidence, uploaded image evidence, style inspiration, brand seed, or product brief.
- Tell Magic which files it may create or update.
- Tell Magic to use project design tokens and existing component conventions.
- After Magic returns output, run visual QA and integrate manually if needed.

Never:

- Ask Magic to copy a protected website directly.
- Let Magic invent navigation for a migrated workflow without source evidence.
- Let Magic ignore an uploaded image or URL.
- Accept Magic output if it breaks tokens, accessibility, responsiveness, or source layout constraints.
