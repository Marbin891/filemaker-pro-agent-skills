# FileMaker Pro Agent Skills

<p align="center">
  <img src="assets/logo-512.png" alt="FileMaker Pro Agent Skills project logo" width="128" height="128">
</p>

A modular, local-first reference set for **Claris FileMaker** development with
**ChatGPT and Codex**. It covers native calculations, script steps, errors and
APIs, together with the BaseElements, MBS and bBox plug-in dialects. Each area
is a separate Agent Skill; a routing skill selects the smallest useful set and
keeps detailed catalogs out of context until they are needed.

The project is distributed in two formats:

- **One portable plugin** containing all five skills.
- **Five independent skills** that can be installed or uploaded one at a time.

No plug-in binary, licence key or live FileMaker connection is required to read
the reference material. Executing a `BE_`, `MBS` or `bBox` call still requires
the corresponding plug-in in the target FileMaker environment.

[Español](README.es.md) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md) ·
[Attribution](ATTRIBUTION.md) · [Third-party boundaries](THIRD-PARTY.md)

## Purpose

FileMaker development spans several vocabularies: native calculation functions,
script steps, error codes, server products and optional plug-ins. Generic model
knowledge often mixes those dialects, invents signatures or applies a behaviour
to the wrong platform.

This project provides a bounded alternative:

- local catalogs with exact names, signatures, parameters, versions and platform
  data;
- explicit routing between native FileMaker and each plug-in;
- progressive disclosure, so a request loads one skill and one reference rather
  than the whole corpus;
- deterministic, read-only lookup helpers with no network access;
- reproducible packages with integrity manifests and per-package notices.

## Coverage

| Area | Included |
|---|---|
| Native FileMaker | **368 calculation functions**, **216 script steps** in 16 categories, **292 error codes**, full field-type catalog |
| Native references | Architecture, professional patterns, compatibility, SQL, Data API, OData, FileMaker Go, WebDirect, HTTP/integration guidance, worked examples |
| BaseElements | **133 catalog entries** covering **129 unique `BE_` functions**, 11 deprecated/renamed/removed entries, 10 named constants, 18 categories |
| MBS | **7,859 functions** in **245 components**, split into 20 lookup groups, with platform and licensing status |
| bBox | **87 functions and script steps** in 15 categories: 39 with dedicated vendor pages, 48 confirmed from vendor primary sources |
| Routing | One orchestrator, a routing matrix and deterministic contract cases |

Catalog baselines:

| Source | Baseline |
|---|---|
| Native FileMaker snapshot | FileMaker 26.0.3, upstream snapshot checked 2026-10-02 |
| BaseElements | Plug-in 5.1.0.6 |
| MBS | Plug-in 16.4 |
| bBox | Plug-in 1.06, build 1.06.7 |

A catalog match means that an entry exists in the snapshot. It is not a claim
that the feature behaves identically in every FileMaker or plug-in release, and
it is not an engine test. See [compatibility](filemaker-pro/references/compatibility.md)
and [test results](docs/TEST-RESULTS.md).

## Skills

| Skill | Responsibility | Example triggers |
|---|---|---|
| `filemaker-pro` | Native functions, steps, errors, schema, architecture, APIs, product behaviour, safety | FileMaker calculation, script step, Data API, OData, WebDirect, FileMaker Go, ExecuteSQL |
| `goya-be-plugin` | BaseElements functions, constants and operational patterns | `BE_HTTP_POST`, BaseElements, `BE_` |
| `monkeybread-mbs-plugin` | MBS components, signatures, platform and licensing | `MBS( ... )`, Monkeybread, DynaPDF, LibXL, Saxon |
| `beezwax-bbox-plugin` | bBox functions, script steps, mode flags, shell and language integration | `bBox_Shell`, `bBox_Zsh`, Beezwax |
| `fmp-dev-orchestrator` | Selects and combines the owning skills; does not duplicate catalogs | “Which skill handles this?”, mixed native/plug-in requests |

### Compatibility

- **ChatGPT:** skills and plugins, subject to workspace plan, role and
  administrator controls. Standalone skills are uploaded individually; the
  multi-skill package is a plugin.
- **Codex:** user and project skills in the documented `.agents/skills`
  locations; the plugin can also be installed through a local marketplace.
- **Python:** helpers require Python 3.10 or newer. The Markdown and JSON
  references can be read without Python.
- **FileMaker:** native guidance covers Pro, Go, WebDirect, Server, Cloud, Data
  API and CWP where the catalogs record support. `Partial` is a limitation, not
  a synonym for `Yes`.
- **BaseElements:** documented baseline 5.1.0.6. Platform support is per
  function; the plug-in must be installed and permitted by the file or server.
- **MBS:** documented baseline 16.4. Some functions require a paid base licence;
  DynaPDF, XL and Saxon require separate add-on licences.
- **bBox:** documented baseline 1.06.7. bBox runs on macOS and Ubuntu, not
  Windows.

## Installation

### ChatGPT: individual skills

1. Open an eligible ChatGPT workspace with skills or plugin permissions.
2. Open the skills area (**Plugins → Skills** in the current plugin directory,
   or **Skills** in the desktop app).
3. Choose **Create** or **Upload from your computer**.
4. Upload one archive from `dist/skills/`:
   - `filemaker-pro.zip`
   - `goya-be-plugin.zip`
   - `monkeybread-mbs-plugin.zip`
   - `beezwax-bbox-plugin.zip`
   - `fmp-dev-orchestrator.zip`
5. Wait for the workspace scan to finish and resolve any review finding.

Each archive has **one top-level skill folder** and one `SKILL.md`. Do not upload
the repository, `dist/plugin.zip`, or a GitHub source snapshot as an individual
skill.

### ChatGPT: the plugin

Use `dist/plugin.zip` for plugin distribution. Its root contains `plugin.json`
and a `skills/` directory; it is not a single-skill archive.

- **Public directory:** upload the ZIP through the OpenAI plugin submission
  portal, resolve automated findings and submit it for review.
- **Local testing:** install the plugin into a personal or repository
  marketplace, restart the desktop app, then install it from the Plugins
  directory.

```sh
# Personal marketplace: ~/.codex/plugins + ~/.agents/plugins/marketplace.json
python3 scripts/install_codex.py --scope user --plugin --register-marketplace

# Repository marketplace: <project>/plugins + <project>/.agents/plugins/marketplace.json
python3 scripts/install_codex.py --scope project --project /absolute/path/to/project --plugin --register-marketplace
```

Official references: [Build skills](https://developers.openai.com/plugins/build/skills),
[Package a plugin](https://developers.openai.com/plugins/build/plugins),
[Submit a plugin](https://developers.openai.com/plugins/deploy/submission).

### Codex: individual skills

```sh
# All five skills for the current user
python3 scripts/install_codex.py --scope user --all

# One skill only
python3 scripts/install_codex.py --scope user --skill goya-be-plugin

# A specific existing project
python3 scripts/install_codex.py --scope project --project /absolute/path/to/project --all
```

Windows PowerShell:

```powershell
py -3 scripts/install_codex.py --scope user --all
py -3 scripts/install_codex.py --scope project --project 'C:\work\my-project' --all
```

Destinations:

- user: `$HOME/.agents/skills/<skill-name>`
- project: `<project>/.agents/skills/<skill-name>`

The installer uses an allowlisted payload, stages the copy outside skill
discovery, promotes it only when complete and refuses to overwrite an existing
skill or follow a symlink. It never deletes an older installation.

### Codex: the plugin

```sh
python3 scripts/install_codex.py --scope user --plugin --register-marketplace
```

This copies the plugin to `~/.codex/plugins/filemaker-pro-agent-skills` and adds
one local entry to `~/.agents/plugins/marketplace.json`. Restart the app after
installation. The plugin is multi-skill; individual skills remain available
through the commands above.

### Manual installation

- Individual skill: extract `dist/skills/<name>.zip` into a documented
  `.agents/skills/` directory. Keep the single top-level folder.
- Plugin: extract `dist/plugin.zip` into a marketplace plugin directory and
  point the marketplace entry at it.
- Verify downloads with `dist/SHA256SUMS` and `dist/manifest.json`.

Codex detects skill changes automatically. Invoke a skill explicitly with
`$skill-name` or through `/skills`. Implicit activation is host- and
model-dependent.

## Examples

### Native FileMaker

> Use `filemaker-pro` to review this FileMaker 19.6.1 Server script. Keep the
> supplied table-occurrence and field names, check error handling and identify
> steps that are incompatible with Server.

> In FileMaker 26.0.3, build a typed JSON parameter without accessing a live
> solution. Show the calculation and a verification procedure.

> Compare Go and WebDirect support for `Go to Layout`. Treat `Partial` as a
> limitation and cite the catalog entry.

### Plug-in functions

> Use `goya-be-plugin` to look up `BE_HTTP_POST`, show its parameters and the
> error signal I should check after the call.

> Use `monkeybread-mbs-plugin` to find an MBS function for reading a text file,
> then state its platform and licence requirements.

> Use `beezwax-bbox-plugin` to explain `bBox_Zsh` mode flags and whether the
> function is suitable for Perform Script on Server.

### Mixed request

> Use `fmp-dev-orchestrator`. Write a FileMaker script that reads a file with
> bBox, validates it and exits with a JSON result. Load only the skills needed.

### Local lookup

```sh
# Native
python3 filemaker-pro/scripts/catalog.py function JSONSetElement --version 16
python3 filemaker-pro/scripts/catalog.py step 'Open Transaction' --version 19.6.1 --platform Server
python3 filemaker-pro/scripts/catalog.py error 401

# Plug-ins
python3 goya-be-plugin/scripts/catalog.py function BE_HTTP_POST
python3 monkeybread-mbs-plugin/scripts/catalog.py function "Dialog.SetMessage"
python3 beezwax-bbox-plugin/scripts/catalog.py function bBox_Shell

# Routing
python3 fmp-dev-orchestrator/scripts/route.py route "Why does bBox_Zsh fail in a server script?"
```

Installed lookup and routing helpers are read-only, use the Python standard library and make no network
requests.

## Architecture

### Project identity

The project logo is distinct from vendor marks. `assets/logo.png` is the PNG
master; 512px and 128px transparent Lanczos variants are used for the listing,
GitHub display and composer. Only those two optimized PNGs are bundled with the
plugin; individual skills remain independent of plugin artwork.

Regeneration and artwork notices: [assets/README.md](assets/README.md).

```text
filemaker-pro-agent-skills/
├── plugin.json                 # portable plugin manifest
├── filemaker-pro/              # canonical source for each skill
├── goya-be-plugin/
├── monkeybread-mbs-plugin/
├── beezwax-bbox-plugin/
├── fmp-dev-orchestrator/
├── scripts/                    # import, validate, build, install, audit
├── tests/
├── docs/
└── dist/
    ├── skills/<name>.zip       # single-skill archives
    ├── plugin.zip              # multi-skill plugin archive
    ├── manifest.json
    └── SHA256SUMS
```

The repository keeps each skill in its own top-level directory so it can be
edited and installed independently. The builder creates the plugin layout at
package time: `plugin.json`, notices, and `skills/<skill-name>/...`.

### Progressive disclosure

1. The host reads each skill's `name` and `description`.
2. It loads one `SKILL.md` when the request matches.
3. The skill loads a specific reference only when needed.
4. Large catalogs expose an index first:
   - MBS resolves a component through `references/index.json` and then reads one
     group file;
   - BaseElements and bBox load one category or one entry;
   - native FileMaker uses the lookup helper and matching reference guide.

The orchestrator contains no function catalog. It routes and hands off, so
signatures and vendor references are never duplicated across skills.

### Catalog policy

The catalogs retain factual API metadata and CC BY 4.0 CadenceUX synthesis:
names, signatures, parameter names and flags, results, versions, platform
support, licensing status and source URLs. Vendor documentation prose and vendor
example code are not redistributed. Each entry links to the authoritative page.
Original examples in this project are marked as such. See
[THIRD-PARTY.md](THIRD-PARTY.md) for the detailed boundary.

### Evidence

Answers should distinguish:

- **catalog-checked** — matched a local entry;
- **documentation-checked** — checked the linked vendor or Claris page;
- **engine syntax-validated** — parsed by a FileMaker engine;
- **engine-evaluated** — evaluated by a FileMaker engine;
- **written and read back** — applied and verified in a solution.

A catalog lookup or a Python test is not an engine test.

## Validation and limitations

Catalog lookup, installation and packaging need only Python's standard library.
Image regeneration and full development validation additionally use the pinned
tools in `requirements-dev.txt`:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/generate_assets.py --check
```

```sh
python3 scripts/validate.py
python3 scripts/import_plugin_catalogs.py ../sources   # maintainers; reviewed clones
python3 scripts/verify_provenance.py ../sources
python3 scripts/verify_plugin_provenance.py ../sources
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/lint_examples.py
python3 scripts/audit.py
```

The automated suite checks catalog integrity, plug-in lookups, routing
contracts, skill independence, package structure, notices and bounded static
security properties. It does not run a FileMaker engine, a live plug-in, a
ChatGPT workspace scan or a Codex model session.

Known limits:

- catalog snapshots age; newer plug-in or FileMaker releases may add functions;
- platform matrices can change between patch releases;
- implicit routing depends on the host and model;
- plug-ins, add-on licences and FileMaker itself are separate installations;
- vendor pages, not this project, are authoritative for vendor behaviour.

See [test results](docs/TEST-RESULTS.md), [security](SECURITY.md),
[research notes](docs/RESEARCH.md) and [release status](docs/RELEASE-STATUS.md).

## Updates and contributions

The update procedure is documented in [docs/UPDATING.md](docs/UPDATING.md).
Source commits are pinned and checked before import. Catalog changes must update
the expected counts, provenance records, tests and packages together.

Contributions are welcome through issues or pull requests. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Do not include
credentials, customer data, vendor binaries or unlicensed documentation copies.

## Licenses and attribution

- Original project text, routing logic, lookup helpers and original examples:
  **CC BY 4.0**.
- CadenceUX material: **CC BY 4.0**, original work by Darrin Southern /
  CadenceUX. Exact commits are recorded in [ATTRIBUTION.md](ATTRIBUTION.md) and
  each skill's `references/provenance.json`.
- Claris, Goya, Monkeybread and Beezwax material: not relicensed by this project.
  Factual API metadata is retained; vendor prose, vendor examples, binaries and
  licence keys are not bundled. See [THIRD-PARTY.md](THIRD-PARTY.md).

This is an independent adaptation. It is not affiliated with or endorsed by
CadenceUX, Claris, Goya, Monkeybread Software, Beezwax or OpenAI. Product names
are used only to identify interoperability.
