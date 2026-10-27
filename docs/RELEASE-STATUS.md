# Release validation status

This document records the implemented checks and the remaining acceptance
limits. It is not a legal opinion or a guarantee of runtime equivalence.

## Implemented and checked locally

| Criterion | Status | Evidence |
|---|---|---|
| Five independent skills | Implemented | `filemaker-pro`, `goya-be-plugin`, `monkeybread-mbs-plugin`, `beezwax-bbox-plugin`, `fmp-dev-orchestrator` |
| Native FileMaker coverage | Preserved | 368 functions, 216 steps, 292 error codes; catalog hashes checked |
| BaseElements catalog | Implemented | 133 entries, 129 unique functions, 11 deprecated/renamed/removed, 10 constants |
| MBS catalog | Implemented | 7,859 functions, 245 components, 20 group files, index integrity checked |
| bBox catalog | Implemented | 87 functions/script steps, 39 full + 48 demo-confirmed entries |
| Routing | Implemented | Orchestrator contract, deterministic helper and routing cases |
| Progressive disclosure | Implemented | Per-skill `SKILL.md`; MBS index-to-group lookup; one-category or one-entry lookup for BE and bBox |
| Individual skill archives | Built | `dist/skills/*.zip`, one top-level folder and one `SKILL.md` each |
| Multi-skill plugin archive | Built | `dist/plugin.zip`, root `plugin.json` and `skills/` |
| Deterministic packaging | Checked | Repeated builds produce identical bytes and manifest |
| Offline lookup | Checked | Standard-library helpers; socket access blocked in tests |
| Installer | Checked | Staged copies, symlink refusal, overwrite refusal, lock handling, injected failure cleanup |
| Structural compatibility | Checked | Frontmatter, file counts, sizes, paths, modes, CRCs, manifest hashes |
| Notices and provenance | Checked | Root and per-skill notices; pinned commits and source hashes |
| Security | Bounded static review | AST and text checks; no network imports, dynamic execution or `shell=True` in project helpers |
| Plugin identity | Implemented and checked | Unmodified RGBA PNG master; Lanczos 512px logo and 128px composer icon; 48px visual review on light/dark backgrounds |
| Official manifest schema | Checked | Agent Plugins 1.0.0 schema plus OpenAI listing and image rules; see TEST-RESULTS.md |
| Cross-platform CI | PASS | Ubuntu, macOS and Windows; 104 tests per job, no skips; [run 40574499264](https://github.com/Marbin891/filemaker-pro-agent-skills/actions/runs/40574499264) |

## Not executed here

| Gate | Status |
|---|---|
| ChatGPT workspace skill upload and scan | Not run |
| ChatGPT plugin directory submission and review | Not run |
| Codex host model activation and implicit routing accuracy | Not run |
| FileMaker engine parsing, evaluation or script execution | Not run |
| Live BaseElements, MBS or bBox calls | Not run |
| Plug-in licensing or add-on verification | Not run |

## Repository distribution

The initial commit and subsequent validation fixes are stored in the private
repository https://github.com/Marbin891/filemaker-pro-agent-skills. GitHub
reports `PRIVATE`. No release, tag or OpenAI directory publication was created.

## Known limitations

- Catalog snapshots are fixed at the recorded source commits and baselines.
  Newer FileMaker or plug-in releases may add or change functions.
- Platform matrices can change between patch releases. A `Partial` entry remains
  a limitation.
- Implicit routing is host- and model-dependent. The deterministic helper tests a
  documented contract, not measured activation.
- Vendor documentation prose and vendor examples are not redistributed. Each
  entry links to the vendor page for full detail.
- Claris documentation rights are not claimed. See `THIRD-PARTY.md`.
- Logo authorship and public redistribution rights are not established by the
  supplied artwork. See `assets/README.md`; the CC BY text/code notice does not
  independently license the artwork.
- The security audit is a bounded static review, not malware detection or a
  runtime sandbox.

## Acceptance checklist

1. Upload each `dist/skills/*.zip` in a test workspace and confirm the scan,
   reference access and positive/negative cases.
2. Upload `dist/plugin.zip` to a draft plugin submission and resolve automated
   findings.
3. Install skills and the plugin in an isolated Codex project; run
   `tests/routing-cases.json` with explicit and implicit invocation.
4. With a licensed FileMaker development copy, validate selected calculations,
   script steps, platform behaviour and plug-in calls. Record only actual results.
5. Re-run provenance, validation, tests and audit after any source or payload
   change; rebuild both package formats.
