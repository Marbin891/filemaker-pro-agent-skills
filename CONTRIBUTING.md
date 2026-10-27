# Contributing

Small, evidenced corrections are welcome. Before contributing:

- Read `LICENSE`, `ATTRIBUTION.md`, `THIRD-PARTY.md` and `SECURITY.md`.
- Do not submit vendor documentation excerpts, vendor example code, plug-in
  binaries, preview software or community code without explicit redistribution
  rights. Attribution is necessary but not sufficient.
- Never include real database files, credentials, customer exports or
  identifying logs.
- Keep the five skills independent. Do not duplicate a catalog or a vendor
  reference across skills; the orchestrator routes instead.
- Keep `SKILL.md` concise and references task-focused. No automatic networking
  or tools that alter a solution without scoped authorization.
- Include a source URL, release/platform context and a test for a technical
  correction.
- Test missing or invalid input, exact patch versions, `Partial`/`No` support,
  offline lookup and package structure.
- Explain exceptions to practices rather than turning personal style into
  universal rules.

Installed helpers and packaging require Python 3.10+ and the standard library.
Full development checks (including Lanczos image verification) additionally use:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/generate_assets.py --check
```

Then run:

```sh
python3 scripts/validate.py
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/lint_examples.py
python3 scripts/audit.py
```

For catalog updates, follow [UPDATING](docs/UPDATING.md). Code review covers
security, licensing, deterministic packaging and whether claims match executed
tests. CC BY 4.0 applies to original project contributions; do not claim to
license third-party rights you do not hold.

## Adding or changing a skill

1. Create or edit a top-level directory whose name matches the `name` in
   `SKILL.md`.
2. Use only `name` and `description` in frontmatter. Put version, licence and
   compatibility requirements in the body.
3. Add the skill to `scripts/build.py` and `scripts/validate.py`, with an
   allowlisted payload.
4. Add the skill to the orchestrator routing table and routing cases.
5. Add at least one positive and one negative test for its scope.
6. Rebuild both package formats and update the README coverage table.
