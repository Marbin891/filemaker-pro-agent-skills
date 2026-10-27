# Source and design notes

## Repositories

The project was assembled from pinned, reviewed local clones. No upstream code
was executed. Each skill records source hashes in `references/provenance.json`;
the native FileMaker inventory is in `filemaker-pro/references/source-inventory.json`.

| Repository | Version | Commit |
|---|---|---|
| https://github.com/CadenceUX/claris-filemaker-pro-skill | 2.2.1 | `bda594e15f4a6981e93403c4b187d262ca820116` |
| https://github.com/CadenceUX/fmp-dev-design-patterns | 2.1.1 | `17471d6d0a3fd1e53a1714d0c265dc3afad718cc` |
| https://github.com/CadenceUX/goya-be-plugin-skill | 1.4.1 | `29579288cba843286b5c15275cd5d23e7bb37f40` |
| https://github.com/CadenceUX/monkeybread-mbs-plugin-skill | 2.0.1 | `946bdca12c2117defb4dc2b8959ee00f04c74086` |
| https://github.com/CadenceUX/beezwax-bbox-plugin-skill | 1.1.1 | `0c4179ddfd5428f514f85f75f2a68d1001ec4483` |
| https://github.com/CadenceUX/fmp-dev-orchestrator-skill | 2.1.3 | `1fe0b8f8682a0bf569a8c4df3ab9aaeab94f405e` |

Catalog baselines: FileMaker 26.0.3 (upstream snapshot checked 2026-10-02),
BaseElements 5.1.0.6, MBS 16.4 and bBox 1.06.7.

## Audit corrections: vendor checks on 2026-10-27

- **Execution hosts:** Claris explicitly excludes plug-ins from Go. Its iOS App
  SDK guide permits app-specific plug-ins in separate Xcode app builds; this is
  not Go support or evidence of a currently available BaseElements iOS binary.
  WebDirect uses compatible server WPE plug-ins, while PSoS/schedules use FMSE.
  Sources and operational limits are in
  [BaseElements patterns](../goya-be-plugin/references/patterns.md#execution-hosts-and-compatibility-evidence).
- **MBS coverage:** the live index still advertises 7,971 functions. All 169
  linked component pages produce 7,593 distinct primary-table names. The
  deprecated table contains 400 names, of which 134 overlap: the union is exactly
  **7,859**, equal to the local catalog. No omissions were proved in that scope.
  `Plugin.LibXSLTVersion`, mentioned in Plugin release notes, is already in the
  XML primary table and local Plugin namespace bucket. The catalog's 245 buckets
  are not the same unit as the vendor's 169 pages. The cause of the 112-function
  headline residual is unresolved; neither a stale counter nor hidden functions
  are established explanations. [Packaged evidence](../monkeybread-mbs-plugin/references/coverage-review.json)
  records the method, index/page hashes, name-set digest and limits. Full vendor
  page prose is not redistributed; live pages may change.
- **Artwork provenance:** the project owner reports ChatGPT generation for this
  project. This establishes the reported origin only, not exclusive rights,
  copyright eligibility or third-party clearance. Claris legal notices remain.

## Native catalog

The native snapshot contains **368 distinct functions**, **216 distinct script
steps in 16 categories**, **292 listed error codes**, six data types, three field
kinds, eight summary operations and the original field/index/storage options.
Get functions remain separate named entries.

The three JSON catalogs retain every upstream value and add a project-owned
top-level `adaptation` field. Semantic hashes are recorded in
`tests/reference-baseline.json`. This is preservation of a snapshot, not a claim
that every option is available in every FileMaker release.

## Plug-in catalogs

The vendor documentation sites do not declare a redistribution licence for their
prose or examples. The catalogs therefore retain factual API metadata and
CadenceUX CC BY 4.0 synthesis, and omit vendor descriptions, parameter prose,
notes and examples. Each entry links to the vendor page.

### BaseElements

- 133 category entries covering 129 unique functions; four functions are
  cross-listed in more than one category.
- 11 deprecated, renamed or removed entries.
- 10 named constants in four groups.
- Original category notes and constants guidance are retained as CadenceUX
  synthesis.

### MBS

- 7,859 functions enumerated from vendor component pages and the deprecated
  listing.
- 245 components; 20 group files bin-packed by size.
- Licensing status `free`, `licensed` or `unknown_license` is retained per
  function.
- DynaPDF, XL and Saxon require separate add-ons.
- `references/index.json` resolves a component to one group file, avoiding a
  full-corpus read.

### bBox

- 87 functions and script steps in 15 categories.
- 39 entries with a dedicated wiki page; 48 confirmed from the vendor demo file
  and/or compiled plug-in but without a dedicated page.
- Shared mode-flag, error-reference, container, bridge, thread-safety and PSoS
  tables are retained as CadenceUX synthesis.
- bBox runs on macOS and Ubuntu, not Windows.

## OpenAI packaging

Final branding checks additionally used the official listing/image requirements:

- https://developers.openai.com/plugins/deploy/submission#icons-and-screenshots
- https://developers.openai.com/plugins/deploy/submission#listing-metadata
- https://developers.openai.com/plugins/deploy/submission-errors#image-errors
- https://agent-plugins.org/schemas/1.0.0/plugin.schema.json

The portable schema was validated with jsonschema, not just a hand-written
profile. Its reviewed bytes have SHA-256
`0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883`.
OpenAI-specific extension fields are not constrained by the portable schema, so
the local validator separately checks listing limits and logo/composerIcon PNGs.
The 512px and 128px targets are project policy; OpenAI accepts square icons from
48px to 4096px, at most 5 MiB, in the supported formats. No dark-specific
alternate design is generated.

Official pages consulted on 2026-10-27:

- https://developers.openai.com/codex/skills
- https://developers.openai.com/plugins/build/skills
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/submission
- https://help.openai.com/articles/20001066-skills-in-chatgpt
- https://developers.openai.com/api/docs/guides/tools-skills

Design consequences:

- A skill is a directory with `SKILL.md`; optional `references/`, `scripts/` and
  `agents/openai.yaml` are used.
- Codex user skills live under `$HOME/.agents/skills`; project skills under
  `.agents/skills`.
- A portable plugin uses root `plugin.json` with the Agent Plugins schema and a
  root `skills/` directory.
- Individual skill ZIPs and the plugin ZIP are different formats and are kept in
  separate paths.
- Local plugin testing uses a personal or repository marketplace.
- Public plugin distribution goes through the submission portal.

The workspace UI, rollout and administrator controls remain product-dependent.
ZIP acceptance by a specific workspace is not established by the local build.

## Evidence model

- **catalog-checked**: matched a local entry.
- **documentation-checked**: checked the linked Claris or vendor page.
- **engine syntax-validated**: parsed by a FileMaker engine.
- **engine-evaluated**: evaluated by a FileMaker engine.
- **written and read back**: applied to a solution and verified.

Python tests and catalog checks do not establish engine behaviour.

## Licensing and rights boundary

CadenceUX declares CC BY 4.0 in its README files. That declaration covers
CadenceUX's original work to the extent CadenceUX owns it; it cannot license
Claris or vendor material. The project therefore:

1. preserves factual API metadata;
2. retains attributed CadenceUX synthesis;
3. rewrites native worked examples and diagnostic summaries;
4. omits vendor prose and vendor examples;
5. bundles no plug-in binary, licence key or Claris software.

Claris documentation terms require written permission for copies or
distribution. No such permission is claimed. See `ATTRIBUTION.md`,
`THIRD-PARTY.md` and `docs/RELEASE-STATUS.md`.
