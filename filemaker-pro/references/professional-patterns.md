# Professional scripting patterns

## Attribution and adaptation
Conceptual influences: Darrin Southern / CadenceUX, `fmp-dev-design-patterns`.
Upstream: https://github.com/CadenceUX/fmp-dev-design-patterns
License: https://creativecommons.org/licenses/by/4.0/
This original adaptation retains modularity, explicit contracts, and read-back review.
It changes error capture, empty-find behavior, and transaction structure for safety.
No upstream prose or worked script blocks are reproduced here.
No custom function, plugin, naming scheme, or tool installation is assumed.

## Agree on a local contract
- Respect an existing solution's names unless the user requests a migration.
- Give each script one business responsibility and a declared execution surface.
- Record input keys, types, optional defaults, and invalid-input behavior.
- Record which file, occurrence, layout, window, and record the script expects.
- Declare whether it owns a transaction or participates in its caller's work.
- Use local `$` variables for intermediate state.
- Reserve `$$` variables for intentional session state, never implicit return values.
- Pass structured parameters and return structured results instead of hidden globals.
- Keep identifiers as strings when leading zeros or nonnumeric identifiers matter.
- Separate user-facing wording from stable machine-readable status codes.

## Capture before branching
The immediate next step after a fallible operation should save its error locally:

```text
Perform Find [ ]
Set Variable [ $findError ; Value: Get ( LastError ) ]
If [ $findError = 401 ]
    Exit Script [ Text Result: "NO_MATCH" ]
End If
```

This is an original fragment, not a complete script or a runtime-tested artifact.
Check all other nonzero errors before continuing to use the found set.
`If` itself is documented not to clear the error; capture-first is a stricter convention.
Do not claim every intervening control step resets `Get ( LastError )`.
Capture additional diagnostics before logging or navigation can obscure their context.
Sanitize diagnostics: errors may include URLs, field contents, or service responses.
Set Error Capture suppresses standard alerts; it does not implement recovery.
Choose Allow User Abort behavior deliberately and document cancellation handling.

## Finds are bounded queries
- Reject missing criteria rather than silently broadening the search.
- Decide whether user text is literal or intentionally uses FileMaker find operators.
- Establish the intended layout and check navigation errors before entering Find mode.
- Check errors from entering Find mode and setting each criterion.
- Treat error 401 as an explicit no-match outcome, not permission to show everything.
- Never follow 401 with Show All Records as an automatic recovery action.
- Stop update workflows when the required target cannot be found uniquely.
- Preserve the empty result or exit the helper's owned context with a clear status.
- Distinguish no match, invalid criteria, privilege denial, and infrastructure failure.

## Subscripts and result handling
- Save a subscript's result immediately after the call, before calling another script.
- Handle invocation failure separately from a valid business-error result.
- Validate returned JSON before interpreting individual keys.
- Use a small envelope: outcome, stable code, optional data, correlation identifier.
- An empty result is not automatically a successful result.
- Explicitly document any navigation, commit, or window-closing side effect.
- Prefer built-in JSON functions; inspect custom function definitions before relying on them.

## Transaction ownership and pairing
- Minimum native transaction version: FileMaker 19.6.1.
- Keep Open Transaction and its matching Commit Transaction as a structural pair.
- Do not put Commit Transaction in an `If` branch with Revert Transaction in `Else`.
- Place conditional Revert Transaction logic inside the paired transaction body.
- A revert transfers control to the matching transaction boundary; plan cleanup accordingly.
- Capture `Get ( LastError )` immediately after the matching Commit Transaction.
- Opening can fail and skip the body; boundary handling must cover that case too.
- Do not exit early from the body as a substitute for a reviewed rollback path.
- Check every write and arrange rollback on any failed invariant or required write.
- Keep schema validation enabled unless an explicit reviewed requirement says otherwise.
- Verify final record values after a successful commit in the authorized test environment.
- Do not pretend nested ownership works: subscript transaction boundaries can be skipped.
- Keep the work in the originating window and avoid context-changing surprises.
- Never promise atomic rollback of HTTP, email, filesystem, or other external effects.

## Loops, retries, and observability
- Check an empty found set before starting a record loop.
- Establish sort order only when the algorithm needs it.
- Define progress and termination independently of portal row positions.
- Bound batches and retries; record the last durable business key processed.
- Retry only classified transient failures, with an idempotency strategy.
- A timeout after a write may leave its outcome unknown; reconcile before retrying.
- Log operation identifiers, durations, counts, and sanitized status codes.
- Do not log credentials, full script parameters, or unrestricted record snapshots.

## Acceptance checks and sources
Test invalid input, 401, multiple matches, denied access, locked records, and failed commit.
Inspect saved scripts and compare their meaningful structure before executing them.
This guidance was documentation-reviewed on 2026-10-27, not engine-tested.
- https://help.claris.com/en/pro-help/content/get-lasterror.html
- https://help.claris.com/en/pro-help/content/open-transaction.html
- https://help.claris.com/en/pro-help/content/jsonsetelement.html
