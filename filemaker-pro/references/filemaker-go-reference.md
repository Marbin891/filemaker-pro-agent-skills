# FileMaker Go: mobile execution and offline boundaries

Snapshot: FileMaker **26.0.3**, upstream verification date **2026-10-02**.
The local catalog records 216 steps: **154 Yes / 20 Partial / 42 No** for Go.
These are snapshot counts, not new device/engine tests or guarantees for later releases.

## What runs where

Go runs custom apps on iOS/iPadOS. Author schema, layouts and scripts in FileMaker Pro.
Go does not host databases, load FileMaker plug-ins, or provide a schema/script editor.
Distinguish two deployments before designing any data-entry workflow:

| Deployment | Data location and responsibility |
|---|---|
| Open a hosted file | Edits affect host data; connectivity and host privileges matter |
| Open a transferred local file | Edits affect the device copy; synchronization must be designed |

A transferred file does not acquire automatic synchronization when the network returns.
For disconnected collection, define UUID keys, queued changes, conflict policy and deletion
tombstones as application features. A whole-file replacement is not a record merge.
Capture client build, host build and device OS separately in a deployment record.
Minimum OS, supported hardware and licensing remain deployment-specific, not inferred here.

## Reading the compatibility snapshot

Use `script-steps-catalog.json` and `compatibility.md` for individual step facts.
An absent Go exception means Yes in this catalog snapshot; Partial requires option-level review.
Print/export/import and window-management paths deserve particular attention on mobile.
Go skips unsupported steps without an alert and reports error 3. Capture `Get ( LastError )`
immediately after a risky operation; a subsequent step can replace the error you needed.
Do not assume a skipped step stops later writes or rolls back earlier business operations.

Practical dispatch pattern, expressed as design logic rather than a copied script:
1. Determine the client environment using `Get ( ApplicationVersion )`.
2. Select a Go-specific implementation before any unsupported UI/file operation.
3. Run one capability-sensitive action, capture its error and verify its actual output.
4. Continue only with a usable artifact; otherwise return an explicit business failure.
5. Do not classify an unknown client/version as desktop merely because it is not recognized.

## Device UI and capability design

Provide touch-sized controls and explicit navigation; do not depend on desktop window geometry.
No Layout or Preview authoring workflow is available on Go; a PDF can serve as report output.
Camera, scanning, signature and media capture use `Insert from Device` where supported.
NFC uses `Configure NFC Reading`; media playback uses the AVPlayer family.
Do not infer hardware presence or OS permission from a supported script-step label.
Offer a manual-entry fallback when scanning or location is unavailable or denied.
Keep device interaction on the device; a server script cannot operate the user's camera.
Avoid promising identical print setup across Pro and Go; verify margins and output on target devices.
Excel/XML record import and FMP12/XML export are unsupported Go workflows in the checked guide.

## Paths and transfers

`Get ( DocumentsPath )` in Go refers to the current device user's application documents area,
not the database host's Documents folder. The returned path is in FileMaker format without a prefix.
Construct the appropriate supported FileMaker path; never transplant a macOS/Windows literal.
Use temporary output for disposable artifacts and make persistent export/transfer a separate action.
Before replacing an on-device database, back it up and close it; avoid replacing an open file.
For a database with externally stored containers, prepare a self-contained copy in Pro first.
Transfer that copy rather than assuming the original file contains all external container bytes.
Protect both the database and exported files; a downloaded report is a separate disclosure surface.

## When work moves to the server

A hosted file can use a server-side script for appropriate supported operations.
That script runs in its own session: pass the record/business IDs and required inputs explicitly.
Establish layout/context again; do not assume the mobile found set, globals or window state exists.
Server `Get ( DocumentsPath )` denotes the host's shared script location, not the Go sandbox.
Return an identifier or structured status, then retrieve/render output through an approved channel.
Do not pass a local device path expecting the host to read it, or vice versa.
For local-only files, server execution is not an implicit substitute for unsupported mobile steps.

## Acceptance checks before rollout

- Test one successful capture and one denied-permission case on each target device class.
- Test interruption/reconnection separately from genuinely offline local-file use.
- Verify conflict handling with two independent edits to the same application key.
- Open exported artifacts and confirm container completeness after a file transfer.
- Record observed behavior as testing evidence; this document itself supplies no test results.

## Evidence and attribution

Official URLs consulted:
- https://help.claris.com/en/go-development-guide/content/index.html
- https://help.claris.com/en/go-development-guide/content/go-pro-differences.html
- https://help.claris.com/en/go-development-guide/content/working-with-data.html
- https://help.claris.com/en/go-development-guide/content/file-transfers.html
- https://help.claris.com/en/pro-help/content/get-documentspath.html

Local factual cross-check: `sources/claris-filemaker-pro-skill/references/filemaker-go-reference.md`.
Credit: Darrin Southern / CadenceUX, https://github.com/CadenceUX/claris-filemaker-pro-skill,
declared CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. This is original writing;
that attribution does not license Claris prose, which is not reproduced here.
