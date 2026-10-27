# Updating catalogs and skills

Upstream maintainer tools are not executed. Their source is inspected as data;
the local importer only reads JSON, Markdown and Git metadata from pinned clones.

## 1. Acquire reviewed sources

Clone the six CadenceUX repositories **outside** this repository. Network access
is a maintainer action; skills never check for updates.

```sh
mkdir -p ../sources
for repo in claris-filemaker-pro-skill fmp-dev-design-patterns \
            goya-be-plugin-skill monkeybread-mbs-plugin-skill \
            beezwax-bbox-plugin-skill fmp-dev-orchestrator-skill; do
  git clone https://github.com/CadenceUX/$repo.git ../sources/$repo
done
```

Record the candidate commits, versions, README licence declarations and changed
files. Review new instructions, scripts, examples and hidden configuration before
using them.

## 2. Review licensing

- Keep factual API metadata separate from expressive vendor prose.
- Do not import vendor descriptions, vendor examples, binaries or licence keys
  without a redistribution basis.
- Re-check Claris documentation terms; attribution alone is not permission.
- Update `ATTRIBUTION.md`, `THIRD-PARTY.md` and the affected
  `references/provenance.json` when sources change.

## 3. Update pins and import

The pins are explicit in `scripts/import_plugin_catalogs.py` and
`scripts/import_facts.py`. Change a pin only after review.

```sh
python3 scripts/import_facts.py ../sources
python3 scripts/import_plugin_catalogs.py ../sources
python3 scripts/verify_provenance.py ../sources
```

The importers reject a mismatched commit, modified tracked files, symlinks and
unexpected catalog shapes. They do not fetch, install or execute upstream code.

If a catalog schema changes, update the transformer and the tests together. Do
not silently drop unknown metadata; decide its treatment explicitly.

Keep BaseElements' `compatibility_interpretation` and MBS's corrected `count_note`
in the transformer, not only in generated JSON. Raw `ios` is not Go support;
`fms` is not WPE certification. For a new MBS coverage review, use the method in
`monkeybread-mbs-plugin/references/coverage-review.json`: explicitly download the
linked vendor component pages and deprecated list as a maintainer action, hash
the raw bytes, enumerate primary-table link labels, deduplicate and compare
against local names. Record counts, sorted-name digest, differences, date and
limits. Do not count release-note mentions twice or invent a cause for the
headline residual. Live pages may change; no vendor prose snapshots are bundled.
The pinned importer does not regenerate this separately dated evidence. Update
it after changing the catalog roster; its name-set digest is regression-tested.

## 4. Update expectations

After an import:

- update `VERSION` and `CHANGELOG.md`;
- update the `Release X.Y.Z.` line in every `SKILL.md`;
- update `tests/reference-baseline.json` only through the native importer;
- update expected counts in `scripts/validate.py`, `tests/test_skill.py`,
  `scripts/build.py` and the READMEs when rosters change;
- update `plugin.json` version and the plugin interface copy if needed;
- review `tests/routing-cases.json` if descriptions or boundaries changed.

## 5. Rebuild and verify

For image changes, keep `assets/logo.png` as the master. Install the development
tools from `requirements-dev.txt`, review any master replacement, and regenerate
with `scripts/generate_assets.py`. Never edit derived PNGs manually. Use
`--check` for pixel equality and `--preview` to review 48px legibility. Only the
512px and 128px PNGs are included in the plugin.

```sh
python3 scripts/validate.py
python3 scripts/verify_provenance.py ../sources
python3 scripts/verify_plugin_provenance.py ../sources
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/lint_examples.py
python3 scripts/audit.py
```

Check:

- `dist/manifest.json` counts and hashes;
- individual ZIPs contain one top-level folder and one `SKILL.md`;
- `dist/plugin.zip` contains root `plugin.json` and every skill under `skills/`;
- extracted skills work from an unrelated directory without the repository;
- installers refuse overwrite and symlink destinations;
- no vendor binary, cache, test file or development file is packaged.

## 6. Release checks

A completed local build does not prove:

- ChatGPT workspace upload or plugin review;
- Codex host activation or implicit routing accuracy;
- FileMaker engine parsing, evaluation or script execution;
- live plug-in behaviour or licensing.

Record only checks that were actually run. Keep unrun gates visible in
`docs/RELEASE-STATUS.md`.
