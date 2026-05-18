# /nocode2procode-figma

Convert a Figma design or Figma export into production UI.

## Required Behavior

1. Prefer Figma MCP when a Figma URL/frame is available.
2. If only an exported image is provided, treat it as visual evidence and create a visual lock spec.
3. Use UI/UX Pro Max for accessibility, responsiveness, design tokens, and component rules.
4. Use 21st.dev Magic for missing or refined components and run design quality gate before approval.
