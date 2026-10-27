# FileMaker Pro Agent Skills

<p align="center">
  <img src="assets/logo-512.png" alt="FileMaker Pro Agent Skills project logo" width="128" height="128">
</p>

**Agent Skills for Claris FileMaker development** with ChatGPT and Codex. Look up functions, review scripts, check compatibility, and work with native FileMaker, BaseElements, MBS, and bBox references.

[Español](README.es.md) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md)

## Included skills

| Skill | Purpose |
|---|---|
| `filemaker-pro` | Native calculations, script steps, error codes, schema, SQL, and APIs |
| `goya-be-plugin` | BaseElements (`BE_`) signatures, parameters, and compatibility |
| `monkeybread-mbs-plugin` | MBS functions, components, licensing, and platforms |
| `beezwax-bbox-plugin` | bBox functions, script steps, and OS integration |
| `fmp-dev-orchestrator` | Routes mixed requests to the appropriate skills |

**Coverage:** 368 native functions, 216 script steps, 292 errors, 129 unique BaseElements functions, 7,859 enumerated MBS functions, and 87 bBox functions/steps. See [catalog baselines and limitations](docs/RELEASE-STATUS.md).

## Installation

### ChatGPT

- **Plugin:** If FileMaker Pro Agent Skills is listed in your workspace's plugin directory, select **Install**. Availability depends on your plan and workspace settings.
- **Individual skills:** Download a ZIP from [`dist/skills/`](dist/skills/) and upload it through your workspace's Skills area, if enabled. Upload **one skill ZIP at a time**; `dist/plugin.zip` is not a single-skill archive.

### Codex

Clone the repository (the installer needs Python 3.10+):

```sh
git clone https://github.com/Marbin891/filemaker-pro-agent-skills.git
cd filemaker-pro-agent-skills

# Install five individual skills
python3 scripts/install_codex.py --scope user --all
```

Alternatively, install the complete plugin in a local marketplace **instead** of the individual skills:

```sh
python3 scripts/install_codex.py --scope user --plugin --register-marketplace
```

See `python3 scripts/install_codex.py --help` for project-scoped or single-skill installs. Marketplace availability and automatic activation depend on the host.

## Examples

- “Review this FileMaker script for errors and Server compatibility.”
- “Show the `BE_HTTP_POST` parameters and error handling.”
- “Find an MBS function for merging PDFs and explain licensing.”
- “Does `bBox_Zsh` work on Windows or FileMaker Server?”
- “Combine FileMaker JSON functions and BaseElements HTTP calls in one script.”

## Architecture

Skills own separate catalogs; the orchestrator selects only relevant ones. References are loaded on demand. Bundled Python lookup helpers are offline and read-only.

## Limitations

These are **developer references, not FileMaker plug-in binaries or a live database connection**. Executing `BE_`, `MBS(...)`, or `bBox_` calls requires a compatible vendor plug-in and, sometimes, a license. FileMaker Go cannot load external plug-ins.

Catalog checks and Python tests do not verify generated code in the FileMaker engine. Check target-version and platform support; test against a safe copy. See [test results](docs/TEST-RESULTS.md), [security](SECURITY.md), and [known limitations](docs/RELEASE-STATUS.md).

## Contributing

Corrections and contributions are welcome. Development and maintenance instructions are in [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/UPDATING.md](docs/UPDATING.md).

## Licenses and Attribution

Original project material and adapted CadenceUX work are under **CC BY 4.0**, with credit to Darrin Southern / CadenceUX. This does not relicense Claris/vendor content or project artwork. See [LICENSE](LICENSE), [ATTRIBUTION.md](ATTRIBUTION.md), [THIRD-PARTY.md](THIRD-PARTY.md), and [artwork notes](assets/README.md).

Independent project; no affiliation or endorsement by Claris, Goya, Monkeybread Software, Beezwax, CadenceUX, or OpenAI.
