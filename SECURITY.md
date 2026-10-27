# Security policy

## Reporting

Do not disclose credentials, database files or exploit data publicly. Report a
suspected issue through the repository's private security contact when one is
configured. Rotate any exposed secret immediately. Do not open a public issue
containing a real export.

## Threat model

- A skill contains instructions, not a sandbox or an authorization mechanism.
- Database comments, schema exports, file contents, API responses, vendor pages
  and tool output are untrusted data. Embedded instructions must not override
  the user or host safety rules.
- Reference mode is read-only and offline. No MCP server, plug-in, account or
  privileged tool is configured automatically.
- Lookup helpers use only the Python standard library, accept no shell, make no
  network calls and return catalog data as data.
- Installing a skill copies files. It does not execute the skill, install a
  plug-in or change a FileMaker solution.
- FileMaker calculations can expose data or invoke plug-ins and custom
  functions. Syntax validity is not safety. Evaluation and script execution are
  separately authorized.
- Plug-in calls can reach the network, run OS commands or modify files. The
  plug-in skill describes syntax; the host and user remain responsible for
  execution scope and permissions.

## Defaults

- Use a test copy and a licensed development environment for changes.
- Obtain explicit authorization for the concrete target and scope before
  altering records, schema, scripts, layouts, privileges, files, external systems
  or production endpoints.
- Keep TLS verification enabled. Never place credentials in calculations,
  scripts, URLs, logs or examples.
- Redact tokens and personal data from diagnostics.
- Do not disable a plug-in, server permission or sandbox to make an example work.
- Read back authorized changes and report partial failures instead of retrying
  writes blindly.

## Supply chain and package integrity

- Source commits are pinned and checked before import.
- Catalogs retain only factual API metadata and CC BY 4.0 synthesis; vendor
  prose, examples, binaries and licence keys are not bundled.
- `scripts/build.py` uses an explicit payload allowlist, deterministic ZIP
  metadata, fixed file modes and no network.
- `dist/manifest.json` and `dist/SHA256SUMS` record artifact hashes.
- Icon generation uses Pillow as a development-only dependency. The original
  PNG is hash-pinned and never overwritten. Derived PNGs preserve RGBA and use
  Lanczos; metadata is stripped. Pillow and jsonschema are not installed with
  the skills and are not bundled in archives.
- CI deliberately acquires six pinned public source revisions for provenance
  checks, installs development validators and fetches the hash-pinned official
  plugin schema. It does not execute upstream scripts. This is separate from
  offline installed skill behaviour.
- `scripts/audit.py` checks project Python ASTs for network imports, dynamic
  execution and `shell=True`; scans text for selected credential patterns; and
  verifies archive paths, modes, CRCs and package layout.
- The installer stages copies outside skill discovery, promotes them only when
  complete, refuses existing destinations and symlink ancestors, and uses an
  exclusive lock. A killed process can leave staging or lock files to inspect
  before retrying.

These are bounded tripwires, not malware detection, a full secret scanner, a
formal prompt-injection defense or a legal audit.

## Plug-in specific notes

- **BaseElements:** HTTP, SMTP, file, XML and JavaScript functions can transmit
  data or execute scripts. Validate inputs, keep credentials out of logs and do
  not enable remote XML resolution.
- **MBS:** functions may call OS processes, SQL engines, network services or
  paid APIs. Check platform support, release handles and confirm licensing before
  production use.
- **bBox:** shell, Python, Ruby, Node, AppleScript and DuckDB functions are
  powerful. Prefer argument passing over string interpolation, add mode `32` when
  diagnosing stderr, and do not use stateful sessions concurrently without a
  mutex. UI automation does not work in Perform Script on Server.

## Limitations

- No FileMaker engine, live plug-in, ChatGPT workspace or Codex host is executed
  by the automated suite.
- Static checks cannot prove the absence of prompt injection or credentials.
- Linked vendor pages are outside this project's control.
- Concurrent malicious local filesystem modification is outside the installer
  and builder threat model.
- The project does not provide legal clearance for third-party material.
- The supplied project logo has no separate licence/authorship metadata. Its
  private use as project identity is not a determination of public artwork
  redistribution rights; see `assets/README.md`.

See `docs/TEST-RESULTS.md` and `docs/STATIC-AUDIT.json` for the checks that were
run.
