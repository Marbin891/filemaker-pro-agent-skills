# Executed checks

Environment: macOS arm64, Python 3.14 with Pillow 12.0.0, jsonschema 4.25.1 and PyYAML 6.0.3
in an isolated development environment. Production, helper and test source also
passes a Python 3.10 grammar check; that is not equivalent to executing on
Python 3.10. No FileMaker engine, live plug-in, eligible ChatGPT workspace or
running Codex host was used.

## Results

| Check | Result |
|---|---|
| `python3 scripts/validate.py` | PASS: frontmatter, links, catalog counts, plugin manifest and notices |
| `python3 -m unittest discover -s tests -v` | **104 tests passed**, 0 failures, 0 errors, 0 skips |
| `python3 scripts/lint_examples.py` | PASS: native/plug-in call inventory and bounded BE/MBS argument counts |
| `python3 scripts/audit.py` | PASS: no automated findings in the bounded checks |
| `python3 scripts/verify_provenance.py ../sources` | PASS: 43 source hashes; 368 functions, 216 steps and 292 errors preserved |
| `python3 scripts/verify_plugin_provenance.py ../sources` | PASS: BE, bBox and MBS catalogs reproducible from pinned sources |
| Deterministic build | Two consecutive builds produce identical artifacts and manifest |
| Extracted-package lookup | PASS from unrelated temporary directories |
| Installer | PASS: individual skills and plugin; overwrite, symlink and lock refusal; injected-failure cleanup |
| `python3 scripts/generate_assets.py --check` | PASS: exact RGBA/Lanczos pixel equality with the unchanged master |
| Official Agent Plugins 1.0.0 schema | PASS with jsonschema; downloaded schema SHA-256 `0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883` |
| OpenAI presentation fields | PASS: final listing text limits, logo/composerIcon paths, PNG dimensions, CRCs and 5 MiB limit |
| 48 × 48 visual review | Profile and database silhouette remain recognizable on light and dark backgrounds; no alternate design |
| Workflow YAML | PASS: safe structural parsing and regression test for typed `run` steps |

## GitHub Actions

[Run 40574499264](https://github.com/Marbin891/filemaker-pro-agent-skills/actions/runs/40574499264)
validated commit `36cadcb0b9743965fe63bcc0fa811b09011c4832` successfully:

| Runner | Python | Test result | Full job |
|---|---|---|---|
| Ubuntu | 3.10 | 104 passed, no skips | PASS |
| macOS | 3.10 | 104 passed, no skips | PASS |
| Windows | 3.10 | 104 passed, no skips | PASS |

All three jobs checked source provenance, exact catalog transformations,
Lanczos pixels, skill/package structure, deterministic rebuilds and the bounded
audit. Ubuntu additionally validated the hash-pinned official manifest schema.
The first two runs stopped during workflow definition validation; the YAML and
path-initialization corrections are covered by the successful run above.

Raw unittest output: [TEST-RUN.txt](TEST-RUN.txt).
Machine-readable static report: [STATIC-AUDIT.json](STATIC-AUDIT.json).
Native-call scan: [EXAMPLE-LINT.json](EXAMPLE-LINT.json).

## Artifacts

The authoritative file counts, byte sizes and per-file SHA-256 hashes are in
[`dist/manifest.json`](../dist/manifest.json). Archive digests are also in
[`dist/SHA256SUMS`](../dist/SHA256SUMS). The static report checks exact payload
bytes against the allowlist and manifest, including the two packaged PNGs.

All artifacts are below the documented Agent Plugins submission envelope
(100 MB ZIP, 500 files, 25 MB uncompressed per file). Individual skill archives
contain one top-level folder and one `SKILL.md`; the plugin archive contains a
root `plugin.json`, five skills under `skills/`, and only `assets/logo-512.png`
and `assets/icon-128.png`. The PNG master and preview sheet are not packaged.

## Test coverage

- **Native catalogs:** 368 functions, 216 steps, 292 errors, field types,
  version comparison, platform `Partial`/`No`, errata and offline lookup.
- **BaseElements:** 133 entries, 129 unique functions, 11 deprecated entries,
  10 constants, lookup/search/constants CLI and catalog field policy.
- **MBS:** 7,859 functions, 245 components, index-to-group integrity,
  licensing status, add-ons and component/function/search CLI.
- **bBox:** 87 entries, 39 full + 48 demo-confirmed, shared reference tables,
  lookup and mode-flag access.
- **Routing:** 15 positive/negative/ambiguity cases, deterministic helper,
  orchestrator contract and native/plug-in boundary.
- **Packages:** deterministic rebuild, manifest hashes, one-folder skill ZIPs,
  root-manifest plugin ZIP, extracted-package lookup and installers.
- **Security and notices:** no network imports in production helpers, no
  dynamic execution or `shell=True`, credential patterns, archive paths/modes/
  CRCs, notices and provenance pins.
- **Branding:** unchanged master digest; 512px/128px RGBA dimensions,
  Lanczos pixel equality, alpha preservation, non-square transparent padding,
  metadata stripping, 48px coverage, manifest references and installed assets.
- **Corrections:** invalid BaseElements names and missing SMTP arguments now fail
  lint; example SQL command lifecycle and JSON parameter groups were corrected.
- **Oracles:** 374 independent text/date equality assertions and the existing
  numeric/specialty oracle checks. These are Python models, not FileMaker
  evaluation.

## Not executed

1. ChatGPT workspace skill upload, scan and routing.
2. ChatGPT plugin submission, review or publication.
3. Codex host discovery, explicit invocation and implicit activation accuracy.
4. FileMaker parsing, evaluation, script execution, privileges, transactions,
   Data API/OData calls or plug-in behaviour.
5. Live BaseElements, MBS or bBox calls, licensing or add-on verification.
6. Cross-platform engine and live plug-in behaviour. CI checks Python helpers,
   data, images and packaging, not the FileMaker runtime.
7. A legal determination or written permission for Claris material or public
   redistribution of the supplied logo artwork.

Catalog preservation, structural validation and Python tests do not establish
runtime equivalence with FileMaker or vendor behaviour.
