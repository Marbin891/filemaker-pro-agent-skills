# Changelog

## 2.0.0 — 2026-10-27

- Added the supplied project logo, transparent 512px/128px Lanczos derivatives,
  OpenAI branding metadata, reproducible image generation and 48px review checks.
- Strengthened package integrity and installer validation; fixed BaseElements
  example names/arguments, JSON parameter groups, MBS command lifecycle and
  plug-in call linting.
- Added official-schema and cross-platform provenance checks to GitHub Actions.

- Split the collection into five independent skills: `filemaker-pro`,
  `goya-be-plugin`, `monkeybread-mbs-plugin`, `beezwax-bbox-plugin` and
  `fmp-dev-orchestrator`.
- Added factual, redistributable catalogs for BaseElements (133 entries,
  129 unique functions), MBS (7,859 functions in 245 components) and bBox
  (87 functions and script steps), each linked to its vendor page.
- Added a routing skill, deterministic routing contract cases and a read-only
  routing helper.
- Added a portable Agent Plugins manifest and a multi-skill plugin package,
  while retaining single-skill archives for individual installation.
- Added per-skill provenance, notices, agents metadata and read-only lookup
  helpers.
- Extended validation, packaging, installation and static audit tools for both
  package formats.
- Rewrote README.md and README.es.md with installation, coverage, architecture,
  examples, limitations and licensing information.
- Preserved native FileMaker coverage: 368 functions, 216 script steps and
  292 error codes.
- Added catalog, routing, package, independence, licensing and security tests.

## 1.0.0 — 2026-10-27

- Established a single Agent Skills source for ChatGPT and Codex with optional
  OpenAI metadata, progressive disclosure and no Claude or mandatory ADT
  dependency.
- Pinned CadenceUX reference 2.2.1 and design patterns 2.1.1; inventoried tracked
  files.
- Preserved all three upstream JSON catalogs with a project-owned adaptation
  field: 368 functions, 216 steps, metadata, purpose, notes, parameters,
  versions, types, compatibility matrices and the full field catalog.
- Retained attributed CadenceUX synthesis and restored detailed integrations,
  patterns, function-example references and the help sitemap.
- Added independently worded summaries for all 292 diagnostic codes and
  replacement records in `docs/replacements-*.json`.
- Removed automatic network checks, Claude paths and assumed MCP names.
- Added read-only offline queries, numeric version comparison, a local Codex
  installer, deterministic single-skill packaging, tests, security audit tooling
  and CI.
- Used only `name` and `description` in frontmatter; version, licence and
  requirements remain in the body.
