# Website To UI Prompt

Use this prompt with Firecrawl and Playwright evidence.

## Goal

Convert an existing website into content, UI, interaction, and asset evidence.

## Required Output

Produce:

- `website_ast.json`
- page inventory
- route map
- content inventory
- asset inventory
- layout/component candidates
- interaction evidence from Playwright

## Rules

- Firecrawl is for content and crawl structure.
- Playwright is for interactions, screenshots, and runtime behavior.
- Do not clone protected assets without license review.

