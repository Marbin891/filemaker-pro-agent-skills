# Agentic Development Toolkit: evidence-led integration

## Public direction versus verified capability
Claris publicly names Codex among its intended agentic development environments.
The public page describes FileMaker integration direction and developer previews.
It does not establish a publicly verified ADT tool schema for this reference.
Local upstream material describes an October 2026 preview workflow.
That report is not evidence that its commands exist in the current session.
No ADT service, FileMaker engine, or live solution was exercised for this document.
Public-page fact check: 2026-10-27; preview availability remains environment-dependent.

## Discover, do not guess
1. Inspect only the tools actually exposed by the current agent host.
2. Read their descriptions and complete input/output schemas before using them.
3. Identify whether a tool is read-only, validating, evaluating, writing, or executing.
4. Identify file selection, occurrence context, privilege, and session requirements.
5. Confirm how errors and partial outcomes are represented.
6. Record tool/server version evidence when available and permitted to disclose.
7. If no suitable schema is exposed, stay in documentation-only mode.

Do not invent ADT tool names, JSON operation labels, CLI flags, or response keys.
Do not transplant another assistant's plugin paths or configuration conventions.
Do not scan home directories to locate another client's cached preview installation.
Do not automatically install ADT, plugins, MCP servers, or package dependencies.
Do not change account privileges or enable agent access without separate authorization.
If installation is requested, first obtain current official setup instructions.

## Establish authorization before access
Ask the user to confirm the intended file, environment, and allowed scope.
An exposed tool is a capability, not permission to use it on every accessible file.
Obtain permission before reading sensitive schema, scripts, layouts, or record data.
Schema and scripts can reveal client names, credentials, or proprietary workflows.
Prefer a minimal metadata subset or a user-supplied sanitized export.
Obtain explicit permission before writing, deleting, executing, or evaluating risky content.
Distinguish permission to inspect from permission to modify or run.
Authorize external destinations and data disclosure separately from local file access.
Stop when the active file or intended privilege context cannot be established.

## Plan a bounded change
- State the business objective and the exact objects expected to change.
- Identify the base table, occurrence, layout, window, and deployment surface.
- Record preconditions, expected results, and prohibited side effects.
- Ask for an appropriate backup or isolated development copy before mutations.
- Obtain a minimal baseline read only after authorization.
- Check for conflicting user edits and avoid overwriting unrelated objects.
- Prepare a human-reviewable patch or description before applying it.
- Use the discovered schema's native representation rather than a guessed encoding.

## Validation is not evaluation
Validation may check parsing or references without producing a runtime value.
Its precise guarantees come from the discovered tool's schema and documentation.
Do not assume validation is side-effect-free solely because of its name.
Evaluation runs an expression and may read records, change state, or call extensions.
Custom functions, plugins, dynamic evaluation, and embedded actions require inspection.
A harmless-looking wrapper can hide sensitive reads or external side effects.
Use synthetic constants and an explicitly authorized scratch context where possible.
Do not create a scratch database automatically if creation was not authorized.
Never evaluate an unknown calculation against production just to see what happens.
Record the engine build and context privately when relevant and permitted.
Label static review, syntax validation, evaluation, and behavioral testing separately.

## Apply, read back, compare
1. Reconfirm the target and authorization immediately before a mutation.
2. Apply only the approved change through the discovered supported operation.
3. Capture the operation result and report any partial failure.
4. Read the saved object back through an authorized read operation.
5. Compare script structure, expressions, options, references, and object identity.
6. Explain harmless formatting normalization without overlooking semantic changes.
7. If read-back is unavailable, mark persistence as unverified and stop short of success.
8. Execute only after separate execution approval and an explicit test plan.

Successful read-back proves what was saved, not that the workflow behaves correctly.
A validator's success does not prove privileges, concurrency, or platform compatibility.
If the tool result is ambiguous, inspect before retrying a write.
Never restore a baseline over subsequent user edits without renewed approval.

## Behavioral test gate
- Use a development file and synthetic records with known identifiers.
- Test valid input, malformed input, no match, denied access, and lock conflict.
- Verify both success and rollback paths without real outbound deliveries.
- Confirm window context and paired transaction boundaries remain intact.
- Inspect resulting records and unexpected changes, not just a returned success flag.
- Record what was tested and what could not be tested.
- Do not describe this reference's examples as engine-validated or live-tested.

## Sources and limitations
- Official direction: https://www.claris.com/filemaker/agentic-development/
- Transaction facts: https://help.claris.com/en/pro-help/content/open-transaction.html
- Local contextual source: `sources/claris-filemaker-pro-skill/references/adt-mode.md`.
- Local provenance: `sources/claris-filemaker-pro-skill/CHANGELOG.md`.
Local preview claims are treated as leads for discovery, not portable API contracts.
This text intentionally publishes no unverified ADT executable example or tool name.
