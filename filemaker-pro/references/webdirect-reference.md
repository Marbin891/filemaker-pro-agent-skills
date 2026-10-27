# WebDirect: browser workflows, not desktop automation

Snapshot boundary: FileMaker **26.0.3**, upstream verification **2026-10-02**.
For 216 cataloged steps, WebDirect counts are **106 Yes / 35 Partial / 75 No**.
These measured catalog totals are not real-engine/browser test results from this adaptation.

## Execution model

WebDirect exposes a hosted custom app through a browser; Pro remains the authoring tool.
Configure the hosted file and grant the intended accounts the `fmwebdirect` privilege.
Server and Cloud are deployment alternatives, not identical administration environments.
Never treat a browser client as a FileMaker Pro process with access to its user's filesystem.
WebDirect is also not the Data API: a browser session and a REST session have separate contracts.
Record host patch version, browser/OS versions and privilege set in any compatibility claim.
Exact supported browser versions and connection limits must be checked for that deployment.

## Compatibility means checking options

Consult `script-steps-catalog.json` and `compatibility.md` for the actual step exceptions.
An absent WebDirect exception means Yes only within this snapshot. Partial is not full support.
Unsupported steps are skipped and return error 3; design explicit alternatives instead of
assuming a desktop-only command will abort the script safely.
Capture `Get ( LastError )` immediately after the action whose failure changes business logic.
Check file/upload/download outcomes as well as step errors; a dialog is not proof of delivery.
Examples requiring scrutiny include window/navigation steps, import/export and clipboard steps.
Do not use these script counts to approve calculation functions; their platform notes are separate.

## Design the UI for a browser

Use Form or List View rather than expecting desktop Table View behavior.
Provide visible navigation and completion buttons; do not rely on custom menus.
Test a narrow/mobile browser viewport independently from FileMaker Go layouts.
Keep grouped objects within one layout part; a group spanning parts does not render as on desktop.
Choose commonly available fonts because browser substitution changes wrapping and geometry.
Avoid business rules that depend on animation or gestures; the checked guide excludes them.
Portal editing can delay record updates until the user leaves the field; verify commit timing.
Use a clear active-record style in List View instead of relying on a desktop current-record marker.
Do not change production layouts under active users without a controlled deployment plan.
Check security with the real account, not merely by hiding buttons or layout objects.

## Files, paths and the 26.0.3 PDF boundary

Browser upload/download is a user-facing exchange, not direct access to arbitrary local paths.
`Get ( DocumentsPath )` in WebDirect is unsupported and returns an empty string.
By contrast, that function in a server-side script refers to the host's script Documents area.
Do not concatenate an empty WebDirect path and interpret the result as a safe destination.
Pass business identifiers to server work; do not pass a workstation path as if it were shared.

In the 26.0.3 snapshot, `Open PDF`, `Append PDF` and `Close PDF` are Yes for WebDirect.
Earlier 26.0.x behavior was Partial; minimum introduction version alone cannot approve options.
For file input, the WebDirect PDF workflow asks the browser user to upload the PDF.
For `Close PDF` with **Save to: File**, output is staged temporarily on the host and offered
as a browser download; **Output file** and **Create folders** options are ignored.
Closing that dialog or ending the session removes the temporary host file.
Consequently a successful PDF close does not prove the user retained a downloaded copy.
For durable evidence, store the generated artifact in an authorized container/workflow first.
Do not extrapolate these PDF semantics to every import/export step without checking its notes.

## Server work is a separate session

Use a supported server-side operation for host-local processing when appropriate.
Pass explicit inputs, establish context and return structured status or a retrievable artifact ID.
Client globals, current record and found set are not an implicit server execution contract.
Separate authorization for generating a document from authorization for retrieving it.
Use unique temporary names and cleanup policy; host paths can be shared by multiple sessions.
A server script cannot select a file on the user's computer or click a browser download dialog.

## Sessions and capacity without a timeless hard limit

Each tab/window can consume its own connection; discourage duplicate app tabs.
An abandoned browser window may leave a session until timeout, even though the user has gone.
Provide an explicit sign-out flow; distinguish sign-out from merely closing a tab.
When capacity appears exhausted, inspect sessions in the applicable Server/Cloud Admin Console.
Disconnect a specific stale session when appropriate; closing a hosted file disconnects everyone.
Determine the maximum from the licensed product, version and deployment topology's specifications.
This document intentionally provides no evergreen numeric connection cap.

## Practical acceptance cases

Test unsupported-step fallback, upload cancellation, PDF download cancellation and session expiry.
Repeat with least-privileged accounts and two concurrent sessions editing the same record.
Verify browser-specific UI behavior before approving desktop-to-web reuse.
Unknown browser/version behavior remains unverified, not automatically compatible.

## Evidence and attribution

Official URLs consulted:
- https://help.claris.com/en/webdirect-guide/content/index.html
- https://help.claris.com/en/webdirect-guide/content/general.html
- https://help.claris.com/en/webdirect-guide/content/maximum-number-of-connections.html
- https://help.claris.com/en/pro-help/content/close-pdf.html
- https://help.claris.com/en/pro-help/content/get-documentspath.html
- https://help.claris.com/en/pro-help/content/open-pdf.html
- https://help.claris.com/en/pro-help/content/extended-privileges.html

Local factual check: `sources/claris-filemaker-pro-skill/references/webdirect-reference.md`.
Credit: Darrin Southern / CadenceUX, https://github.com/CadenceUX/claris-filemaker-pro-skill,
declared CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. New prose and synthetic
workflow guidance only; the upstream license does not grant rights to Claris documentation.
