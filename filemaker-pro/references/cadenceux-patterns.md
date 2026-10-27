# FileMaker scripting conventions and solution audits

Adapted from Darrin Southern / CadenceUX, [fmp-dev-design-patterns](https://github.com/CadenceUX/fmp-dev-design-patterns/tree/17471d6d0a3fd1e53a1714d0c265dc3afad718cc), commit `17471d6d0a3fd1e53a1714d0c265dc3afad718cc`, `SKILL.md`, `references/scripting-patterns.md`, and `references/pattern-audit.md`, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Reusable naming/audit synthesis is adapted; concrete scripts/calculations are original synthetic replacements, with corrections to error capture, finds, transaction boundaries, modifier tests and portal assumptions. No FileMaker engine or ADT runtime was used. Readable steps below are implementation templates, not observed successful executions. Optional custom functions are explicitly defined, never assumed installed.

## Contents
- [Agree conventions before changing a solution](#agree-conventions-before-changing-a-solution)
- [Naming and structure](#naming-and-structure)
- [Error capture and scope](#error-capture-and-scope)
- [Parameters, results, loops and finds](#parameters-results-loops-and-finds)
- [Transactions](#transactions)
- [AI and custom functions](#ai-and-custom-functions)
- [Delivery and platform boundaries](#delivery-and-platform-boundaries)
- [Audit inputs and XML extraction](#audit-inputs-and-xml-extraction)
- [Audit measurements and findings](#audit-measurements-and-findings)

## Agree conventions before changing a solution

Ask once whether to apply existing project conventions, audit first and recommend conventions, or audit then merge only accepted recommendations into project configuration. Also agree whether every script opens with `Allow User Abort [ Off ]` and `Set Error Capture [ On ]`, whether to ask per script, or another explicit policy. Do not modify a skill/configuration file just because an audit found a majority convention; obtain approval. Keep solution names and measured statistics in the audit report, not in generalized project standards.

If ADT or a standards pack is available, its baseline can inform the project. An explicitly approved project standard may override it; explain material differences. None of ADT, a particular AI client, a plugin skill, or a network update checker is required to apply these patterns.

## Naming and structure

Suggested conventions, not mandatory renames of an existing solution:

- **Scripts:** `Domain: Action` taxonomy (`Search:`, `Email:`, `Export:`, `Import:`, `Report:`, `Update:`, `Validate:`); `| Variant` suffix; `[Mode]` for mode-based behavior; `[OLD]` for deliberately retained superseded versions. Keep existing `--` divider-script organization or folders consistently; do not introduce folders piecemeal.
- **Fields:** `Entity.Purpose.Detail` namespacing; `_g` for globals; configuration globals centralized in one control/settings table rather than scattered across tables.
- **Table occurrences:** `Anchor.Related.Purpose` context paths; a short prefix such as `xml_` for staging/import occurrences.
- **Comments:** a real purpose header and useful section comments; empty comment steps may separate sections but are not documentation. Add a meaningful comment to new/changed fields.
- **Spacing:** blank lines between logical sections, not every step. Keep a variable-setup run, a loop body or a related series of field assignments together.
- **Termination:** explicit `Exit Script [ Text Result: ... ]` on normal/error paths; reserve `Halt Script` for deliberately named trigger/button utility use, not scattered business logic. Explicit exit makes the contract clear; it does not by itself prove success.

Authoring checklist:
1. Purpose, inputs, outputs, layout/table context and section plan.
2. Approved opening-step policy.
3. Immediate capture/check after every operation whose failure matters.
4. JSON inputs/results where structured values are needed.
5. Exact step/function syntax and client/version support checked.
6. Review globals, disabled code, comments and speculative helpers.
7. Deliver through an authorized tool or readable Script Workspace steps; read back and test separately.

## Error capture and scope

`Set Error Capture [ On ]` suppresses FileMaker dialogs; it is not error handling or automatic rollback. `Allow User Abort [ Off ]` helps prevent an accidental Escape/Command-period interruption, but does not guarantee all interruptions are impossible. Offer deliberate cancellation for long work and clean up owned resources.

Capture LastError immediately after the risky step, before another operation can replace it. **Do not assert that an `If` step necessarily clears LastError**; use a local snapshot regardless of step-specific preservation rules. Capture detail/location in the same calculation if needed:
```text
Allow User Abort [ Off ]
Set Error Capture [ On ]

# PURPOSE: Commit a previously validated observation in the established context.
Commit Records/Requests [ With dialog: Off ]
Set Variable [ $diagnostic ; Value:
  Let ( [ code = Get ( LastError ) ; detail = Get ( LastErrorDetail ) ; where = Get ( LastErrorLocation ) ] ;
    JSONSetElement ( "{}" ; [ "error" ; code ; JSONNumber ] ;
      [ "detail" ; detail ; JSONString ] ; [ "location" ; where ; JSONString ] ) ) ]
If [ JSONGetElement ( $diagnostic ; "error" ) ≠ 0 ]
  Exit Script [ Text Result: $diagnostic ]
End If

Exit Script [ Text Result: JSONSetElement ( "{}" ; [ "error" ; 0 ; JSONNumber ] ) ]
```
Expected only if a real commit is permitted: returned error 0; validation/locking failures return a captured nonzero code. No actual commit was performed here. Detail may be empty; do not promise a descriptive error string for every error. Avoid exposing secrets in diagnostics.

During development, `Set Error Logging [ On ]` writes `ScriptErrors.log` in the user's Documents area (timestamp, script, step, code), not a console. Source scope: stays active for scripts in the file until disabled/file close; check platform support and actual path. Logging complements, not replaces, business error checks.

- `$local` lives for that script invocation.
- `$$sessionGlobal` is shared by scripts in the file/session and clears when the file closes; it does **not** survive closing/reopening.
- Prefer parameters in and explicit script results out, not globals as call/result channels.
- For genuine UI/halt session state, initialize/validate at startup and pair setters with cleanup, including error/early-exit paths.
- Hunt hidden setters in `Let()` custom functions, field calculations and step target variables such as Insert from URL; also casing twins, uninitialized reads and cross-script stale state.
- Disabled dead steps should be reviewed, not silently retained forever. Remove or archive only with permission; do not delete unfamiliar user work automatically.

## Parameters, results, loops and finds

### JSON call/result contract

Original synthetic caller and callee fragments; assume script `Observation: Validate` exists and the caller supplies a string UUID. Validate input JSON structure and required types in the actual implementation.
```text
# Caller
Set Variable [ $request ; Value: JSONSetElement ( "{}" ;
  [ "observationUUID" ; $observationUUID ; JSONString ] ;
  [ "mode" ; "review" ; JSONString ] ) ]
Perform Script [ "Observation: Validate" ; Parameter: $request ]
Set Variable [ $callSnapshot ; Value: Let ( code = Get ( LastError ) ;
  JSONSetElement ( "{}" ; [ "error" ; code ; JSONNumber ] ;
    [ "reply" ; Get ( ScriptResult ) ; JSONString ] ) ) ]
# Inspect invocation error, then validate the reply's JSON/business status.
Exit Script [ Text Result: $callSnapshot ]

# Callee excerpt, after JSON/type validation
Set Variable [ $observationUUID ; Value: JSONGetElement ( Get ( ScriptParameter ) ; "observationUUID" ) ]
Set Variable [ $mode ; Value: JSONGetElement ( Get ( ScriptParameter ) ; "mode" ) ]
# Perform explicitly authorized checks here; do not trust caller account text.
Exit Script [ Text Result: JSONSetElement ( "{}" ;
  [ "status" ; "validated" ; JSONString ] ; [ "observationUUID" ; $observationUUID ; JSONString ] ) ]
```
The `validated` reply is a proposed callee contract after real checks, not a claim those checks ran. `Get(ScriptResult)` is the called script's last Exit Script text. Empty text can mean an intentionally empty result, omitted result or falling off the end; never infer success from emptiness. Simple contracts may use empty text, a status word or `ERROR:<captured code>`; JSON is preferable when callers need multiple fields. Capture errors before constructing a result, not by rereading LastError after logging.

### Iterating a found set

For a read/process/commit loop, establish the correct layout and intended found set first. On an empty found set exit explicitly. Capture/check navigation, work and commit failures individually before advancing. Do not show all records to “fix” an empty set. `Next; Exit after last` is useful for simple stable found sets; for workflows changing sort/membership/deleting rows, first collect stable application keys and process those instead. Preserve/restore caller context when promised. No cursor-loop pattern is an automatic transaction or snapshot under concurrent edits.

Original outline (work placeholder must be replaced and checked):
```text
If [ Get ( FoundCount ) = 0 ]
  Exit Script [ Text Result: "empty-input" ]
End If
Go to Record/Request/Page [ First ]
Set Variable [ $navigationError ; Value: Get ( LastError ) ]
If [ $navigationError ≠ 0 ]
  Exit Script [ Text Result: "ERROR:" & $navigationError ]
End If
Loop
  # Perform approved work; capture/check each operation's error here.
  Commit Records/Requests [ With dialog: Off ]
  Set Variable [ $commitError ; Value: Get ( LastError ) ]
  If [ $commitError ≠ 0 ]
    Exit Script [ Text Result: "ERROR:" & $commitError ]
  End If
  Exit Loop If [ Get ( RecordNumber ) = Get ( FoundCount ) ]
  Go to Record/Request/Page [ Next ]
  Set Variable [ $navigationError ; Value: Get ( LastError ) ]
  If [ $navigationError ≠ 0 ]
    Exit Script [ Text Result: "ERROR:" & $navigationError ]
  End If
End Loop
Exit Script [ Text Result: "iteration-complete" ]
```
Expected under a stable nonempty found set and successful work: each row is visited once. The expectation is untested; commits are per-record and earlier commits remain on a later error.

### Scripted find without widening access

In the required layout, enter Find mode without pause, capture/check that error, set criteria and capture/check that error, then perform the find. Original final find fragment:
```text
# Assumes Find mode and synthetic Observation::Status criterion already established.
Perform Find [ ]
Set Variable [ $findError ; Value: Get ( LastError ) ]
If [ $findError = 401 ]
  Exit Script [ Text Result: "no-matching-observations" ]
Else If [ $findError ≠ 0 ]
  Exit Script [ Text Result: "ERROR:" & $findError ]
End If
Exit Script [ Text Result: JSONSetElement ( "{}" ; [ "matches" ; Get ( FoundCount ) ; JSONNumber ] ) ]
```
Expected no-match outcome: 401, explicitly returned. **No `Show All Records` fallback**: broadening a failed find can expose/process unrelated records. Whether a UI dialog is appropriate depends on the client; server/API scripts must not require interaction.

## Transactions

The source's Open Transaction outside an `If` but Commit Transaction inside it crosses a conditional boundary and must not be copied. **Open Transaction and its matching Commit Transaction belong in the same control-flow block/nesting level.** In particular, a conditional commit cannot close an outer opening. A schematic safe structure is:
```text
# Requires ownership of a new transaction in a supported version/context.
Open Transaction
  # Capture the open error and perform checked record operations.
  # If an operation fails, preserve the original error and Revert Transaction.
Commit Transaction
# Capture commit error immediately, then return an explicit result.
```
The comments are deliberately not pseudo-options or runnable error handling. Implement the lifecycle as follows:

1. Decide ownership before opening: `Get(TransactionOpenState)` detects an existing transaction. A helper must not commit/revert a caller-owned transaction or assume independent nested transactions.
2. Establish context and deliberate handling of already-uncommitted edits; opening is not permission to absorb unrelated user edits.
3. Open and capture its error immediately. Handle opening failure without performing intended writes. Maintain the matched transaction structure when authoring the actual steps.
4. Check **every** modification/navigation/validation operation. Preserve the first error locally; decide whether the current transaction remains open (including `Get(RevertTransactionOnErrorState)` policy and automatic reversion).
5. On a failure in an owned open transaction, `Revert Transaction` explicitly rolls it back. FileMaker skips to the matching Commit Transaction boundary; code after a revert inside the block must not be relied upon for cleanup. Arrange cleanup/result logic after the boundary and retain the original captured error.
6. If no earlier failure, reach the matching Commit Transaction at the **same nesting level** as Open Transaction; capture commit error immediately. Validation/locking/commit failures must be surfaced, not labeled success.
7. Return an explicit structured result only after confirming the transaction outcome. External HTTP calls, emails and unrelated filesystem/plugin side effects are not automatically undone; defer them or use compensating/idempotent design.

For a conditional transaction, put the **whole** open/work/commit structure inside the condition. Do not make two branches contain separate closing boundaries for one outer Open Transaction. Exact rollback/validation behavior and supported options require version-specific engine tests; this reference does not claim to have committed or reverted anything.

## AI and custom functions

### AI step division

`Configure AI Account` configures Account Name, Model Provider, API key and, for custom providers, Endpoint. It has **no Model parameter**. Choose a model on `Generate Response from Model`, whose surfaces are User Prompt, Instructions, Response, Messages and Agentic mode, not fabricated Prompt Template/Input/Target options.

Original design example: configure a permitted provider using a runtime-supplied secret; generate a short classification of synthetic habitat notes into a designated response variable/field using a provider-supported model chosen at deployment. Capture/check the account-configuration error before generating; then capture generation error and usage, validate the returned business format, and write only after authorization. No fixed model name, generated response or API success is asserted here.

`Configure Prompt Template` is a separate named-template step for natural-language/RAG workflows (SQL Query, Find Request, RAG Prompt types, constants such as `:question:` and `:schema:`). It does **not** feed Generate Response from Model by magic. Verify exact options in the local step reference or available engine; don't invent integration parameters.

### Custom-function rules and optional definitions

Custom functions are calculation formulas defined in Manage Custom Functions, not script-step containers. Prefer pure functions; scripts handle writes/navigation/multistep effects. Although formulas can have `Let()` variable side effects, those effects undermine purity and must be documented.

- Names unique file-wide, at most **100 characters**, and not built-in names. Future built-in collisions are not reliably documented; a project `_cf` suffix reduces risk but cannot promise no future collision.
- Editing requires Full Access or the “Manage database, data sources, containers, and custom functions” privilege. Private formulas appear as `<Private Function>` for non-Full-Access users.
- Recursive CFs and `While()` default to **50,000 iterations** in FM 18+. `SetRecursion ( expression ; maxIterations )` changes the limit. Tail recursion avoids pending work, but non-tail recursion can exhaust the stack and produce `?` before the iteration limit. Always define a stopping case.
- Review the project's existing library first; don't install speculative unreferenced helpers. Brian Dunning's community library (https://www.briandunning.com/filemaker-custom-functions/) is an optional source to evaluate, not an automatic dependency. Source reported **2,600+** entries, ratings, examples and platform notes; the figure is historical and each entry's rights/behavior need review.
- Zero-parameter CFs are referenced by bare name, not with parentheses.

**Optional error helpers, not required dependencies:** if preserving an existing CadenceUX convention, explicitly define zero-parameter `AnErrorOccurred` as `Let ( $$LastError = Get ( LastError ) ; $$LastError ≠ 0 )` and `NoErrorOccurred` as `Let ( $$LastError = Get ( LastError ) ; $$LastError = 0 )`. These retained compatibility definitions **assign a global**. Invoke immediately after the operation, copy the global locally immediately if needed, and never treat it as another script's error result or trust it across triggers/sessions. Prefer the direct local capture above for new code. An inline condition may also test empty output/exception markers, but string text alone is not a reliable typed success contract.

**Optional pure replacements:** create `HasError_cf ( code )` with formula `code ≠ 0`, and `HasOptionBit_cf ( mask )` with formula `Mod ( Div ( mask ; 8 ) ; 2 ) = 1`. These formulas take explicit parameters and do not assign globals. Expected `HasOptionBit_cf(8)` and `HasOptionBit_cf(9)` both true; `HasOptionBit_cf(1)` false (use FileMaker semicolon syntax for multiple arguments). Option/Alt is bit **8**; `mask = 8` fails when another modifier is also held. For compatibility, an optional zero-parameter `optionKey` can use `Mod ( Div ( Get ( ActiveModifierKeys ) ; 8 ) ; 2 ) = 1`; use `Get(TriggerModifierKeys)` for trigger-captured rather than live modifiers.

**Optional adjacent-record helpers:** define `PortalNext ( field ; row ; count )` as `Case ( row ≥ 1 and row < count ; GetNthRecord ( field ; row + 1 ) ; "" )`; define `PortalPrev ( field ; row ; count )` as `Case ( row > 1 and row ≤ count ; GetNthRecord ( field ; row - 1 ) ; "" )`. Pass `Get(ActivePortalRowNumber)` and the correct related-record count only when related-record order matches the portal. `GetNthRecord` is not a general visible filtered/sorted portal-row accessor: filtered/sorted portals may require navigation or another explicit mapping. At no active row/first/last row return empty as applicable; empty is ambiguous with a genuinely empty field, so add a structured status contract if needed. These original guarded definitions replace the source's unchecked `Field` placeholder formulas; none is installed automatically.

## Delivery and platform boundaries

If an authorized ADT/tool integration is installed, discover its actual tools; validate calculations with the available engine, write only with permission, then read back and compare intended versus stored steps. Correct differences before claiming a write matches. **Readback is not execution testing.** Without those tools, deliver readable steps for Script Workspace entry; no fabricated tool invocation, clipboard XML or plugin dependency is needed. Historical clipboard/fmxmlsnippet delivery via MBS/BaseElements/agentic-fm/ProofKit was retired upstream in 2.0.0; it is not the default workflow here.

Unsupported client steps may be skipped with error 3 (Go, WebDirect, Server, Data API contexts); branch before unsupported operations using actual environment/capabilities and check results. Use each step's platform notes, not an assumption that desktop-looking syntax works everywhere. Project function restrictions are opt-in configuration; none is invented by this reference. No automatic update/self-check or Claude-specific installation command is carried forward.

## Audit inputs and XML extraction

An audit recommends conventions; it does not authorize refactoring or establish schema integrity. With an installed authorized ADT-like integration, read script names/folders/steps, fields, occurrences and CFs directly, then compute the same measurements below. Without it, obtain a **Save a Copy as XML** export using advanced tools. Large exports may be tens of MB; parse locally with a streaming/full XML parser, not a text-only skim. If code execution is unavailable, ask the developer to run extraction locally. Protect credentials and solution data; disable external entity/network resolution in the parser and avoid uploading a full export unnecessarily.

Root path: `FMSaveAsXML → Structure → AddAction`, then a catalog per object type. Preserve IDs and version/namespaces as encountered; verify the schema against the actual export rather than assuming every release serializes identically.

| Object | XML extraction path | Important detail |
|---|---|---|
| Script names/folders | `ScriptCatalog → Script / Group` | No Groups can mean divider-script organization rather than missing organization. |
| Script steps | `StepsForScripts → Script → ObjectList → Step` | Script ID is on child `ScriptReference`, **not** the enclosing Script element. |
| Calculation text | `Calculation → Calculation → Text` | Outer Calculation text is whitespace; read the nested Text. |
| Comment steps | `Step name="# (comment)" → ParameterValues/Parameter[type=Comment]/Comment` | Empty Comment is a separator, not a written comment. |
| Set Variable targets | `Step → ParameterValues/Parameter[type=Variable]/Name@value` | Assigned variable is an attribute; scanning only formula text misses writes. |
| Fields | `FieldsForTables → FieldCatalog → ObjectList/Field` (one catalog/base table) | Comments in child `Comment`; globals via `Storage@global="True"`. |
| CFs | `CustomFunctionsCatalog → CustomFunction` | Use nested Calculation/Text for formula. |
| Table occurrences | `TableOccurrenceCatalog` | Base table via `BaseTableSourceReference`. |

These exact path/attribute names are retained from the source audit method. Extraction is not executed here, and no unsupported field/schema names are invented.

## Audit measurements and findings

Compute and disclose denominators, scope exclusions and export date:

1. **Script naming:** prefixes before `:`, suffixes `| X` / `[X]`, divider scripts, dev/test/OLD markers and folder usage.
2. **Openers/closers:** percentage with Allow User Abort + Set Error Capture among first steps; any Exit Script; last-step Exit Script; scripts reading Get(ScriptResult). Record disabled steps separately.
3. **Comments:** written comment count versus empty separators; field-comment rate.
4. **Error handling:** Get(LastError)/error-helper usage versus Set Error Capture counts. The gap indicates a silent-failure review surface, not proof of a one-to-one failure count. Inspect control flow to assess actual coverage.
5. **Dead code:** per-script disabled-step counts (`enable="False"`). Recommend review, not automatic deletion.
6. **Global set/clear/read map:** Set Variable `Name@value` beginning `$$`; `$$X =` assignments inside calculation text (Let in scripts, CFs **and field calcs**); other visible step target variables. Clearers are assignments of `""`; readers are `$$X` calculation references. Flag reads with no visible setters (possibly hidden plugin/step writes), casing twins (`$$Result`/`$$result`), missing clearers, cross-script setter/reader pairs and startup initialization/validation gaps. Use syntax-aware analysis where possible; regex hits are review candidates.
7. **CF hygiene:** references from scripts, field calculations and other CFs; match zero-parameter bare calls too. Layout conditional formatting, hide conditions and tooltips are **not covered by this scan**; don't label layout-helper CFs dead without checking layout references. Likewise account for indirect/dynamic calls.
8. **Naming drift:** competing global-prefix/suffix styles, key-field conventions and casing; recommend a majority form only after understanding deliberate exceptions.
9. **Secrets:** credential-like literals and credential-bearing globals/fields; report separately as security observations with redaction, not copied secrets in a style report.

Present **conventions to follow** and **anti-patterns observed**, each with supporting numbers and caveats. Let the developer accept/reject items before changing generalized project configuration. Leave solution names/statistics in the report. Deeper layout-reference or broken-reference findings need actual layout/live-file inspection, not overclaims from this limited scan. There are no observed solution metrics or completed-runtime-test claims in this document.
