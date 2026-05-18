# Browser UI Dogfooding Rules

Inspired by local browser automation, GStack browser QA, and E2E testing skills.

## Purpose

Generated apps must be opened, clicked, and observed like a real user before approval.

## Required Checks

- Start the app locally or use the approved runtime URL.
- Visit every discovered route.
- Fail on severe console errors, page errors, Next.js overlays, failed critical requests, or broken navigation.
- Click buttons, links, tabs, menus, dialogs, selects, filters, and upload controls where safe.
- Capture desktop and mobile screenshots for important routes.
- Preserve traces/screenshots as evidence artifacts.
- Use stable auth/session setup to avoid port/callback mismatch.

## Generated Test Inventory

Build or validate:

- `route_interaction_inventory.json`
- `functional_sanity_report.json`
- `ui_click_coverage_report.json`
- `console_error_report.json`

## Common Runtime Bugs To Catch

- invalid Radix/shadcn values such as `SelectItem value=""`
- protected route redirect loops
- wrong `NEXTAUTH_URL` / callback URL
- external font/CDN calls in corporate/offline mode
- controls that render but crash when opened
- buttons with no effect or hidden blocking errors
