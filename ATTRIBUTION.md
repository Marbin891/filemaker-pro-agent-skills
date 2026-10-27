# Attribution and source record

## Project identity

The official project identity is the supplied `assets/logo.png`. Optimized
512px and 128px PNGs are Lanczos derivatives, not alternate designs. They do
not represent the marks of Claris, FileMaker or any plug-in vendor. No separate
artwork licence or author metadata accompanied the master; the general CC BY
notice does not independently license this artwork. See `assets/README.md` in
the repository before public redistribution.

This is an independent adaptation for ChatGPT and Codex. It is not affiliated
with or endorsed by CadenceUX, Darrin Southern, Claris, Goya, Monkeybread
Software, Beezwax or OpenAI.

## CadenceUX sources

Original work by **Darrin Southern**, **CadenceUX** (https://cadenceux.com.au).
The upstream README files declare **CC BY 4.0**. The exact commits used for this
adaptation are pinned below.

| Repository | Version | Commit | Role |
|---|---|---|---|
| https://github.com/CadenceUX/claris-filemaker-pro-skill | 2.2.1 | `bda594e15f4a6981e93403c4b187d262ca820116` | Native FileMaker catalogs and reference synthesis |
| https://github.com/CadenceUX/fmp-dev-design-patterns | 2.1.1 | `17471d6d0a3fd1e53a1714d0c265dc3afad718cc` | Professional scripting patterns |
| https://github.com/CadenceUX/goya-be-plugin-skill | 1.4.1 | `29579288cba843286b5c15275cd5d23e7bb37f40` | BaseElements catalog and guidance |
| https://github.com/CadenceUX/monkeybread-mbs-plugin-skill | 2.0.1 | `946bdca12c2117defb4dc2b8959ee00f04c74086` | MBS catalog and guidance |
| https://github.com/CadenceUX/beezwax-bbox-plugin-skill | 1.1.1 | `0c4179ddfd5428f514f85f75f2a68d1001ec4483` | bBox catalog and guidance |
| https://github.com/CadenceUX/fmp-dev-orchestrator-skill | 2.1.3 | `1fe0b8f8682a0bf569a8c4df3ab9aaeab94f405e` | Routing model and skill boundaries |

Changes made for this project:

- provider-neutral instructions and one portable Agent Skills layout;
- one orchestrator plus four specialised skills instead of a single collection;
- removal of Claude-specific manifests, host cache paths and automatic update
  requests;
- factual plugin catalogs with vendor prose and vendor examples omitted for
  redistribution reasons;
- original examples and routing logic;
- exact version checks, read-only lookup helpers, deterministic packaging,
  tests, security documentation and per-package notices;
- rewritten native FileMaker worked examples and independently worded
  diagnostic summaries, recorded in `docs/replacements-*.json`.

No claim is made that upstream tests, engine runs or live host results were
performed here. See `docs/TEST-RESULTS.md` for this project's executed checks.

## Plugin vendor sources

| Catalog | Vendor | Baseline | Source |
|---|---|---|---|
| BaseElements | Goya Pty Ltd | Plug-in 5.1.0.6 | https://github.com/GoyaPtyLtd/BaseElements-Plugin |
| MBS | Monkeybread Software | Plug-in 16.4 | https://www.mbsplugins.eu |
| bBox | Beezwax Datatools, Inc. | Plug-in 1.06.7 | https://github.com/beezwax/bbox-documentation/wiki |

The catalogs retain names, signatures, parameter names and flags, result types,
versions, platform support, licensing status, deprecation links and source URLs.
They do not reproduce vendor descriptions, vendor notes or vendor example code.
The vendor pages remain the authoritative documentation. See
[THIRD-PARTY.md](THIRD-PARTY.md) for the detailed rights boundary.

## Claris material

The native FileMaker catalogs are derived from the pinned CadenceUX snapshot,
which in turn references Claris documentation. Factual API metadata is retained;
potentially Claris-derived expression is treated as follows:

1. The three original JSON catalogs retain every upstream value plus a
   project-owned top-level adaptation field.
2. CadenceUX synthesis is retained with CC BY 4.0 attribution.
3. Worked examples and diagnostic summaries were individually rewritten.
4. No raw help-page mirror, logo, preview binary or Claris software is bundled.

Claris's documentation terms require written permission for copies or
distribution of Claris documentation. No such permission is claimed. This
project does not describe the retained material as legally cleared. Review
`docs/RELEASE-STATUS.md` and `THIRD-PARTY.md` before redistribution.

## Content categories

- **Factual/API material:** names, signatures, parameters, types, versions,
  platform matrices and links.
- **CadenceUX synthesis:** category notes, routing guidance, shared reference
  tables and operational patterns, retained under CC BY 4.0 with attribution.
- **Project original material:** SKILL.md instructions, READMEs, lookup helpers,
  routing logic, tests and original examples.
- **Rewritten expression:** native FileMaker worked examples and error summaries
  that may have originated in Claris documentation.

## Trademarks

Claris and FileMaker are trademarks of Claris International Inc. BaseElements is
a product of Goya Pty Ltd. MBS and Monkeybread Software are marks of Christian
Schmitz Software GmbH. bBox and Beezwax are marks of Beezwax Datatools, Inc.
OpenAI, ChatGPT and Codex are marks of their respective owners. Names are used
solely to identify interoperability. No brand assets are included.
