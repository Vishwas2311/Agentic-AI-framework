# Migration Inputs

Put source evidence for a migration in this folder before running:

```powershell
nocode2procode migrate
```

Recommended simple folder model:

```text
migration_inputs/
  migration_request.yaml
  raw_data/
  images/
  videos/
```

Use this rule:

- If it is visual, put it in `images/`.
- If it moves, put it in `videos/`.
- Everything else goes in `raw_data/`.

`raw_data/` can hold any source/business evidence:

- Power Platform solution zip
- `.msapp`
- `Src/*.pa.yaml`
- XML / JSON / YAML metadata
- SQL / CSV / Excel
- screenshots
- video walkthroughs
- BRD / PDF / DOCX / PPTX
- website reference notes with URLs
- OpenAPI / Postman / API docs

`images/` is for UI references:

- current app screenshots
- target UI references
- mockups and wireframes
- brand/color/component references

`videos/` is for runtime references:

- click walkthroughs
- screen recordings
- happy-path demos
- defect/edge-case recordings

Recommended companion file:

- `migration_request.yaml`

That request file can describe the app name, target stack, delivery mode, domain, and any notes that the pipeline should use while planning the migration.

Optional visual/runtime manifests:

- `images/image_manifest.yaml`
- `videos/video_manifest.yaml`
- `raw_data/raw_data_manifest.yaml`

The manifests let you tell Genesis which screen/flow each file belongs to and whether a reference is exact, inspirational, brand-only, or component-level.
