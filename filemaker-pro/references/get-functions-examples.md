# FileMaker Get() functions: complete snapshot and original examples

Adapted from Darrin Southern / CadenceUX, [claris-filemaker-pro-skill](https://github.com/CadenceUX/claris-filemaker-pro-skill/tree/bda594e15f4a6981e93403c4b187d262ca820116), `references/get-functions-examples.md`, commit `bda594e15f4a6981e93403c4b187d262ca820116`, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Category synthesis, all 138 entries, enumerations and notes are retained; worked examples are replaced with original synthetic calculations and script outlines. No FileMaker engine was available: outputs are conditional expectations, never observed results. Claris documentation has separate rights.

Official function index: https://help.claris.com/en/pro-help/content/get-functions.html

## Contents
- [Date and time](#date-and-time)
- [Account and privileges](#account-and-privileges)
- [File and database](#file-and-database)
- [Paths and file system](#paths-and-file-system)
- [Record and found set](#record-and-found-set)
- [Layout and window](#layout-and-window)
- [Script and trigger](#script-and-trigger)
- [Field and object state](#field-and-object-state)
- [Sorting and printing](#sorting-and-printing)
- [Network and connectivity](#network-and-connectivity)
- [Device and screen](#device-and-screen)
- [Calculation context](#calculation-context)
- [Common patterns](#common-patterns)

The source snapshot includes FM 26 additions `AccountPasswordDaysRemaining`, `GuidedAccessState` and `WindowUUID`. Get functions report the evaluating context, not necessarily the caller's device or account privileges. Enumerations differ: `Get(Device)` 3 means iPad; `Get(SystemPlatform)` 3 means iOS/iPadOS. Only documented parameter names exist: `Get ( RecordCount )` is invalid (source reports calculation error 1215), not a synonym for `FoundCount` or `TotalRecordCount`. Availability and actual output remain version/platform/context dependent.

## Date and time

| Function | Returns | Notes |
|---|---|---|
| `Get(CurrentDate)` | date | Today's date per system clock |
| `Get(CurrentTime)` | time | Current time per system clock |
| `Get(CurrentTimestamp)` | timestamp | Current date+time |
| `Get(CurrentTimeUTCMilliseconds)` | number | Milliseconds since **1/1/0001** UTC (not the Unix epoch). Unix ms = this − 62135596800000 |
| `Get(CurrentTimeUTCMicroseconds)` | number | Microseconds since **1/1/0001** UTC (not the Unix epoch) |
| `Get(CurrentHostTimestamp)` | timestamp | Server-side timestamp (consistent across all clients) |

Original examples: assume the system date is 17 September 2026, and `Loan::ReturnBy` is 14 September 2026. Expected overdue days: 3. Capture once so midnight cannot split the ISO date components. Display formats depend on locale; a host timestamp is an evaluation-time value, not a synchronized frozen value across separate calls.
```filemaker
Let ( today = Get ( CurrentDate ) ;
  Max ( 0 ; today - Loan::ReturnBy )
)

Let ( today = Get ( CurrentDate ) ;
  Year ( today ) & "-" & Right ( "0" & Month ( today ) ; 2 ) & "-" &
  Right ( "0" & Day ( today ) ; 2 )
)
// Expected ISO date under the stated clock: "2026-09-17"

Get ( CurrentTimeUTCMilliseconds ) - 62135596800000
// Expected unit: milliseconds since the Unix epoch, not a fixed clock reading.
Get ( CurrentTimeUTCMicroseconds ) / 1000 - 62135596800000
// Expected comparable unit; precision is not a promise of clock accuracy.
Get ( CurrentTime )
Get ( CurrentTimestamp )
Get ( CurrentHostTimestamp )
// Environment-dependent time values; verify host/client context before auditing.
```

## Account and privileges

| Function | Returns | Notes |
|---|---|---|
| `Get(AccountName)` | text | Current user's account name |
| `Get(AccountType)` | text | `FileMaker File`, `Guest`, `External`, `Apple ID`, `Amazon`, `Google`, `Azure`, `Custom OAuth`, or `Claris ID <Team Name>` |
| `Get(AccountGroupName)` | text | External server group name (LDAP/Active Directory) |
| `Get(AccountPrivilegeSetName)` | text | Name of the current privilege set |
| `Get(AccountExtendedPrivileges)` | text | Return-delimited list of extended privilege keywords |
| `Get(AccountPasswordDaysRemaining)` | number | **FM 26+** — days until the password must change; `0` if expired; `-1` if no expiry, no password, or not a FileMaker File account |
| `Get(CurrentPrivilegeSetName)` | text | Privilege set **evaluating this calculation** — `[Full Access]` inside a script set to run with full access, even when the account's set differs |
| `Get(CurrentExtendedPrivileges)` | text | Extended privileges of the privilege set currently in effect (differs from the account's under full-access scripts) |
| `Get(UserName)` | text | User name set in FileMaker Pro / Go Settings (not the OS login, not the account); `[WebDirect-xxxxx]` in WebDirect |
| `Get(UserCount)` | number | Number of users connected to the hosted file |

Original diagnostics; assume the signed-in account is `lab_reader`, its privilege set is `Review`, and a script is configured to run with full access. Expected account/current privilege sets differ. UI user names are not authentication identities. Source extended-privilege examples include `fmapp`, `fmwebdirect`, `fmrest`, `fmodata`, `fmxml`, `fmphp`, `fmurlscript`, `fmextscriptaccess`, `fmreauthenticate10`.
```filemaker
List ( Get ( AccountName ) ; Get ( AccountPrivilegeSetName ) ;
  Get ( CurrentPrivilegeSetName ) ; Get ( UserCount ) )
// Expected first three lines in this fixture: lab_reader, Review, [Full Access].
// Connected-user count is environment-dependent.

not IsEmpty ( FilterValues ( Get ( AccountExtendedPrivileges ) ; "fmwebdirect" ) )
// Expected true only when the exact keyword is a list member, not a substring.
Get ( CurrentPrivilegeSetName ) = "[Full Access]"
// Tests evaluating privileges; use AccountPrivilegeSetName for the account itself.
```

## File and database

| Function | Returns | Notes |
|---|---|---|
| `Get(FileName)` | text | File name without extension |
| `Get(FilePath)` | text | Full path to the file on disk |
| `Get(FileSize)` | number | File size in bytes |
| `Get(EncryptionState)` | text | `0` not encrypted; `1¶<shared ID>` if encrypted at rest |
| `Get(FileLocaleElements)` | text | JSON of file locale settings |
| `Get(HostName)` | text | Server hostname or "localhost" |
| `Get(HostIPAddress)` | text | IP address of the host |
| `Get(HostApplicationVersion)` | text | FileMaker Server version string |
| `Get(ApplicationVersion)` | text | FileMaker Pro/Go/WebDirect version |
| `Get(ApplicationLanguage)` | text | UI language of the application |
| `Get(ApplicationArchitecture)` | text | `x86_64` (Intel Mac, Windows, Server, Cloud, WebDirect…) or `arm64` (Apple silicon, Go, ARM Linux Server) |
| `Get(FileMakerPath)` | text | Path to the **folder** of the running FileMaker app (Pro and Server only) |
| `Get(CacheFileName)` | text | Name of the local cache file (hosted files) |
| `Get(CacheFilePath)` | text | Path to the local cache file |
| `Get(OpenDataFileInfo)` | text | Info about any open data files |
| `Get(SessionIdentifier)` | text | Value set by **Set Session Identifier** in this session on a hosted file; otherwise empty |
| `Get(SystemVersion)` | text | OS version string |
| `Get(SystemDrive)` | text | Boot drive path |
| `Get(SystemIPAddress)` | text | Client's IP address (newline-delimited if multiple) |
| `Get(SystemNICAddress)` | text | Network interface card MAC address |
| `Get(SystemLanguage)` | text | OS language setting |
| `Get(SystemPlatform)` | number | `1` macOS · `-2` Windows · `3` iOS/iPadOS · `4` WebDirect · `5` CentOS Linux · `8` Ubuntu Linux |
| `Get(SystemAppearance)` | text | macOS/iOS: the system appearance name (e.g. `Dark`); Windows: the active high-contrast scheme name, else empty |
| `Get(SystemLocaleElements)` | text | JSON of OS locale settings |
| `Get(SystemStorageAvailable)` | number | Available storage in bytes |
| `Get(MultiUserState)` | number | `0` sharing off · `1` sharing on, accessed on the host · `2` sharing on, accessed from a client |
| `Get(InstalledFMPlugins)` | text | Return-delimited list of installed plug-ins |
| `Get(InstalledFMPluginsAsJSON)` | text | JSON array of installed plug-in details |

Original diagnostic: in a local file named `HabitatLog.fmp12`, expected `FileName` is `HabitatLog`; do not predict an actual disk/network path. Paths may be `file:` locally or `fmnet:` when hosted. Version engine labels include Pro, Go, Go_iPad, Server, Web Publishing Engine and FileMaker Data API Engine; do not infer capability from architecture alone. Appearance and encryption output follow the table, not a guaranteed value.
```filemaker
JSONSetElement ( "{}" ;
  [ "file" ; Get ( FileName ) ; JSONString ] ;
  [ "engine" ; Get ( ApplicationVersion ) ; JSONString ] ;
  [ "architecture" ; Get ( ApplicationArchitecture ) ; JSONString ] ;
  [ "appearance" ; Get ( SystemAppearance ) ; JSONString ] ;
  [ "encryption" ; Get ( EncryptionState ) ; JSONString ]
)

Case ( Get ( SystemPlatform ) = 1 ; "macOS route" ;
  Get ( SystemPlatform ) = -2 ; "Windows route" ;
  Get ( SystemPlatform ) = 3 ; "mobile route" ;
  Get ( SystemPlatform ) = 4 ; "browser route" ; "review environment" )
// Expected on iPadOS: "mobile route"; unknown/server platforms require review.

If ( Get ( SystemAppearance ) = "Dark" ; RGB ( 230 ; 230 ; 230 ) ; RGB ( 25 ; 25 ; 25 ) )
// Original color choice, not a complete accessibility policy.
```

## Paths and file system

| Function | Returns | Notes |
|---|---|---|
| `Get(DesktopPath)` | text | Path to the Desktop folder |
| `Get(DocumentsPath)` | text | Path to the Documents folder |
| `Get(DocumentsPathListing)` | text | Return-delimited file listing of Documents folder |
| `Get(PreferencesPath)` | text | Path to the application preferences folder |
| `Get(TemporaryPath)` | text | Path to the system temporary folder |

Original export-path construction avoids locale-dependent timestamp punctuation:
```filemaker
Get ( TemporaryPath ) & "habitat-" & Get ( UUID ) & ".csv"
// Expected: a unique proposed temporary path; this does not create a file.
List ( Get ( DesktopPath ) ; Get ( DocumentsPath ) ; Get ( PreferencesPath ) )
Get ( DocumentsPathListing )
// Actual paths/listing require a supported client and permissions; not observed here.
```
Use the path prefix/format required by the receiving script step. A server Documents path is not the client's, and WebDirect does not provide a desktop filesystem.

## Record and found set

| Function | Returns | Notes |
|---|---|---|
| `Get(RecordID)` | number | Internal unique record ID (never reused) |
| `Get(RecordNumber)` | number | Position in current found set (1-based) |
| `Get(ActiveRecordNumber)` | number | Record number shown in the status toolbar (position in the found set) — not a portal row |
| `Get(TotalRecordCount)` | number | All records in the table |
| `Get(FoundCount)` | number | Records in current found set |
| `Get(RecordOpenCount)` | number | Number of records currently open/locked |
| `Get(RecordOpenState)` | number | `0` closed (committed) · `1` **new** uncommitted · `2` **modified** uncommitted · `3` deleted uncommitted |
| `Get(RecordModificationCount)` | number | Cumulative modification count for current record |
| `Get(RecordAccess)` | number | `0` no view/edit · `1` view only · `2` edit (privilege-set record access for the current record) |
| `Get(ModifiedFields)` | text | Return-delimited list of modified field names (unsaved) |

Original fixture: current found set contains 9 of 80 records, current record is position 4, internal ID 620, modified-but-uncommitted state 2, modification count 6; edited field `Observation`. Expected diagnostic values depend on establishing that exact context; internal ID is not the business key.
```filemaker
JSONSetElement ( "{}" ;
  [ "row" ; Get ( RecordNumber ) ; JSONNumber ] ;
  [ "matches" ; Get ( FoundCount ) ; JSONNumber ] ;
  [ "internalID" ; Get ( RecordID ) ; JSONNumber ] ;
  [ "state" ; Get ( RecordOpenState ) ; JSONNumber ] ;
  [ "revision" ; Get ( RecordModificationCount ) ; JSONNumber ] ;
  [ "dirtyFields" ; Get ( ModifiedFields ) ; JSONString ] )
// Expected fixture values: 4, 9, 620, 2, 6, "Observation".
```
Unsaved-record prompt is script syntax, not an `If()` calculation containing a script step:
```text
If [ Get ( RecordOpenState ) > 0 ]
  Show Custom Dialog [ "Pending observation" ; "Save or discard using the provided controls before leaving." ]
  Exit Script [ Text Result: "pending-record" ]
End If
Exit Script [ Text Result: "ready" ]
```
Original progress calculation: `Get ( RecordNumber ) & " / " & Get ( FoundCount )`; expected `4 / 9` under the fixture.

## Layout and window

| Function | Returns | Notes |
|---|---|---|
| `Get(LayoutName)` | text | Current layout name |
| `Get(LayoutNumber)` | number | Layout's position in layout list |
| `Get(LayoutCount)` | number | Total number of layouts |
| `Get(LayoutTableName)` | text | Table occurrence the layout is based on |
| `Get(LayoutViewState)` | number | 0=form, 1=list, 2=table |
| `Get(LayoutAccess)` | number | `0` no access · `1` view only (also for read-only files) · `2` modifiable — via this layout |
| `Get(WindowName)` | text | Current window title |
| `Get(WindowHeight)` | number | Window height in points |
| `Get(WindowWidth)` | number | Window width in points |
| `Get(WindowTop)` | number | Window top position in points |
| `Get(WindowLeft)` | number | Window left position in points |
| `Get(WindowContentHeight)` | number | Usable content area height |
| `Get(WindowContentWidth)` | number | Usable content area width |
| `Get(WindowDesktopHeight)` | number | Total desktop/screen height |
| `Get(WindowDesktopWidth)` | number | Total desktop/screen width |
| `Get(WindowMode)` | number | `0` Browse · `1` Find · `2` Preview · `3` printing · `4` Layout mode (Data Viewer only; scripts switch to Browse) |
| `Get(WindowStyle)` | number | `0` document · `1` floating document · `2` dialog · `3` card |
| `Get(WindowZoomLevel)` | text | Zoom percentage of the current window; WebDirect returns 100 |
| `Get(WindowVisible)` | number | 1=visible, 0=hidden |
| `Get(WindowOrientation)` | number | Pro & Go: `-2` landscape left · `-1` landscape right · `0` square · `1` portrait · `2` portrait upside down |
| `Get(WindowUUID)` | text | **FM 26+** — Unique stable UUID for the active window; useful for managing multiple windows of the same file |
| `Get(ActiveLayoutObjectName)` | text | Name of the currently focused layout object |
| `Get(StatusAreaState)` | number | `0` hidden · `1` visible · `2` visible & locked · `3` hidden & locked |
| `Get(MenubarState)` | number | `0` hidden & unlocked · `1` visible & unlocked · `2` visible & locked · `3` hidden & locked |
| `Get(CustomMenuSetName)` | text | Name of the active custom menu set |
| `Get(AllowFormattingBarState)` | number | 1 if formatting bar is allowed |
| `Get(TextRulerVisible)` | number | 1 if text ruler is visible |
| `Get(TouchKeyboardState)` | number | FileMaker Go and Windows: `1` touch keyboard enabled · `0` disabled |

Original layout fixture: layout `Habitat Review` based on `Habitat.Observations`, Browse mode, content width 900 points, portrait, visible status toolbar, menu set `Review Controls`. Read the diagnostic rather than assuming these values on every device.
```filemaker
List ( Get ( LayoutName ) ; Get ( LayoutTableName ) ; Get ( WindowMode ) ;
  Get ( WindowContentWidth ) ; Get ( WindowOrientation ) ;
  Get ( StatusAreaState ) ; Get ( CustomMenuSetName ) )
// Expected lines under the fixture: Habitat Review, Habitat.Observations, 0, 900, 1, 1, Review Controls.
Case ( Get ( WindowContentWidth ) < 700 ; "compact controls" ; "wide controls" )
// Expected for 900 points: wide controls.
If ( Get ( WindowMode ) = 1 ; "" ; Habitat::Summary )
// Expected in Find mode: empty; otherwise the field value in this context.
```

## Script and trigger

| Function | Returns | Notes |
|---|---|---|
| `Get(ScriptName)` | text | Currently running script name |
| `Get(ScriptParameter)` | text | Parameter passed to current script |
| `Get(ScriptResult)` | text | Result returned by a called sub-script |
| `Get(LastError)` | number | Error code from last script step (0=none) |
| `Get(LastErrorDetail)` | text | Detail message for the last error |
| `Get(LastErrorLocation)` | text | Script name and step where last error occurred |
| `Get(LastMessageChoice)` | number | Button pressed in last dialog (1=first, 2=second, 3=third) |
| `Get(LastStepTokensUsed)` | text | JSON for the last AI script step: `model`, `summary` (records embedded/skipped), `usage` (`prompt_tokens`, `total_tokens`) |
| `Get(ErrorCaptureState)` | number | 1 if Set Error Capture is On |
| `Get(AllowAbortState)` | number | 1 if Allow User Abort is On |
| `Get(ScriptAnimationState)` | number | 1 if script animations are enabled |
| `Get(RequestCount)` | number | Number of find requests defined |
| `Get(RequestOmitState)` | number | 1 if current find request is set to Omit |
| `Get(TransactionOpenState)` | number | 1 if inside an open transaction block |
| `Get(RevertTransactionOnErrorState)` | number | 1 if Revert Transaction on Error is active |
| `Get(TriggerCurrentPanel)` | text | `index¶objectName` of the panel being left (OnPanelSwitch only); `0` if invalid |
| `Get(TriggerTargetPanel)` | text | `index¶objectName` of the panel being switched to (OnPanelSwitch only); `0` if invalid |
| `Get(TriggerGestureInfo)` | text | List (OnGestureTap, Go and Windows): `Tap`, tap count, finger count, x, y, object name |
| `Get(TriggerKeystroke)` | text | Key pressed in an OnObjectKeystroke trigger |
| `Get(TriggerModifierKeys)` | number | Modifier keys held during trigger (bitmask) |
| `Get(TriggerExternalEvent)` | number | FileMaker Go remote-control event: `0` unknown · `1` play · `2` pause · `3` toggle · `4` next · `5` previous · `6` seek · `7` stop |

Original parameter: `{"operation":"review","observationUUID":"<UUID>"}`. Expected parsed operation `review`; validate JSON and types before trusting inputs. A returned script result is text, not automatic proof of business success. LastMessageChoice is only meaningful after a dialog; last error detail/location may be empty and are not guaranteed human-readable descriptions. LastErrorLocation reports script/step/line information when available; capture it before intervening work.
```text
Set Variable [ $operation ; Value: JSONGetElement ( Get ( ScriptParameter ) ; "operation" ) ]
Set Variable [ $observationUUID ; Value: JSONGetElement ( Get ( ScriptParameter ) ; "observationUUID" ) ]
```
Capture error information in **one calculation immediately following the risky step**, before logging/navigation/another operation can replace it:
```text
Set Variable [ $failure ; Value:
  Let ( [ code = Get ( LastError ) ; detail = Get ( LastErrorDetail ) ; location = Get ( LastErrorLocation ) ] ;
    JSONSetElement ( "{}" ; [ "code" ; code ; JSONNumber ] ;
      [ "detail" ; detail ; JSONString ] ; [ "location" ; location ; JSONString ] ) ) ]
If [ JSONGetElement ( $failure ; "code" ) ≠ 0 ]
  Exit Script [ Text Result: $failure ]
End If
```
Expected following a no-match find: captured code 401. This is a template, not a recorded execution. Do not claim that `If` necessarily clears LastError; the reliable rule is capture before any intervening work. For Option/Alt in trigger modifiers, `Mod ( Div ( Get ( TriggerModifierKeys ) ; 8 ) ; 2 ) = 1` tests the bit even when other modifiers are held.

## Field and object state

| Function | Returns | Notes |
|---|---|---|
| `Get(ActiveFieldName)` | text | Name of the field currently in focus |
| `Get(ActiveFieldTableName)` | text | Table name of the focused field |
| `Get(ActiveFieldContents)` | text | Contents of the field currently in focus |
| `Get(ActiveRepetitionNumber)` | number | Repetition number of the active field |
| `Get(ActiveSelectionSize)` | number | Length of the current text selection |
| `Get(ActiveSelectionStart)` | number | Start position of the current text selection |
| `Get(ActiveModifierKeys)` | number | Modifier keys currently held (bitmask) |
| `Get(ActivePortalRowNumber)` | number | Currently active portal row (0 if none) |
| `Get(QuickFindText)` | text | Text currently in the Quick Find search box |

Original fixture: focus `ObserverEmail`, contents `reviewer@example.invalid`, selection begins at 2, active portal row 5, Quick Find text `wetland`. Expected diagnostic lines follow those assumptions; outside a focused field/portal the values differ.
```filemaker
List ( Get ( ActiveFieldName ) ; Get ( ActiveFieldContents ) ;
  Get ( ActiveSelectionStart ) ; Get ( ActivePortalRowNumber ) ; Get ( QuickFindText ) )
```

## Sorting and printing

| Function | Returns | Notes |
|---|---|---|
| `Get(SortState)` | number | 0=unsorted, 1=sorted, 2=semi-sorted |
| `Get(PageNumber)` | number | Current page number (Preview mode only) |
| `Get(PageCount)` | number | Total page count (Preview mode only) |
| `Get(PrinterName)` | text | Name of the current printer |
| `Get(UseSystemFormatsState)` | number | 1 if file is using system date/time formats |

Original report expression, assuming Preview page 2 of a 7-page report: expected `Sheet 2 / 7`. Go lacks Preview mode; do not expect this fixture there.
```filemaker
"Sheet " & Get ( PageNumber ) & " / " & Get ( PageCount )
Case ( Get ( SortState ) = 1 ; "ordered" ; Get ( SortState ) = 2 ; "partly ordered" ; "unordered" )
```

## Network and connectivity

| Function | Returns | Notes |
|---|---|---|
| `Get(NetworkProtocol)` | text | Network protocol in use (e.g. "TCP/IP") |
| `Get(NetworkType)` | number | FileMaker Go: `0` local file · `1` unknown · `2` cellular · `3` Wi-Fi |
| `Get(ConnectionState)` | number | `0` no network connection · `1` unencrypted · `2` encrypted, certificate **not** verified · `3` encrypted & verified |
| `Get(ConnectionAttributes)` | text | Encrypted connection details JSON |
| `Get(PersistentID)` | text | 32-hex-digit ID of the **device / computer** (or WebDirect session) — not the file. On FileMaker Server 26+, stable across restarts and upgrades |
| `Get(UUID)` | text | New 16-byte UUID each evaluation (unstored) |
| `Get(UUIDNumber)` | number | New 24-byte (192-bit) unique number each evaluation; may index faster than Get(UUID) as a key |

Original key expression: `Lower ( Get ( UUID ) )`; expected a newly generated lowercase UUID string, not a predetermined ID. Configure a key's auto-enter policy not to replace an existing value; an unstored calculation would regenerate it. `Get ( ConnectionState ) = 3` is expected true only for an encrypted, certificate-verified connection, not proof that every downstream service is trusted.

## Device and screen

| Function | Returns | Notes |
|---|---|---|
| `Get(Device)` | number | `0` unknown · `1` Mac · `2` Windows · `3` **iPad** · `4` **iPhone** · `5` Android · `6` Linux |
| `Get(ScreenDepth)` | number | Colour depth in bits |
| `Get(ScreenHeight)` | number | Screen height in points |
| `Get(ScreenWidth)` | number | Screen width in points |
| `Get(ScreenScaleFactor)` | number | Display scale factor (2.0 for Retina, 3.0 for Super Retina) |
| `Get(HighContrastState)` | number | 1 if OS high contrast / accessibility mode is active |
| `Get(GuidedAccessState)` | number | **FM 26+, FileMaker Go only** — 1 if iOS Guided Access is currently active; use to detect kiosk/locked-screen mode |
| `Get(RegionMonitorEvents)` | text | JSON of pending region monitor events (Go only) |

Original routing calculation; expected `tablet review` on an iPad. Android in the enumeration does not establish availability of a native FileMaker Go app for Android. Screen dimensions, scale and contrast depend on the actual environment.
```filemaker
Case ( Get ( Device ) = 3 ; "tablet review" ;
  Get ( Device ) = 4 ; "phone capture" ; "inspect client capabilities" )
JSONSetElement ( "{}" ; [ "width" ; Get ( ScreenWidth ) ; JSONNumber ] ;
  [ "scale" ; Get ( ScreenScaleFactor ) ; JSONNumber ] ;
  [ "contrast" ; Get ( HighContrastState ) ; JSONNumber ] )
```

## Calculation context

| Function | Returns | Notes |
|---|---|---|
| `Get(CalculationRepetitionNumber)` | number | Repetition being evaluated in a repeating calc |

Original repeating calculation: `"Sample slot " & Get ( CalculationRepetitionNumber )`; expected `Sample slot 4` when evaluated for repetition 4. Not a portal-row counter.

## Common patterns

Each example is independently constructed. All expected outputs require the stated context; no runtime execution is claimed.

### Audit context and stable synchronization keys
```filemaker
JSONSetElement ( "{}" ; [ "actor" ; Get ( AccountName ) ; JSONString ] ;
  [ "recordedAt" ; GetAsText ( Get ( CurrentHostTimestamp ) ) ; JSONString ] ;
  [ "host" ; Get ( HostName ) ; JSONString ] )
// Expected contextual audit text; use an explicit timezone/format contract for interchange.
```
For synchronization keys, configure an auto-enter `Get ( UUID )` with replacement disabled. This creates an application key; it does not make the internal RecordID globally portable or implement synchronization.

### Responsive sizing
```filemaker
Let ( width = Get ( WindowContentWidth ) ;
  Case ( width < 600 ; "one column" ; width < 1100 ; "two columns" ; "three columns" ) )
// Expected for 900 points: two columns. Breakpoints are this example's design choices.
```

### Context passed explicitly to a subscript
```text
Perform Script [ "Observation: Review" ; Parameter:
  JSONSetElement ( "{}" ; [ "observationUUID" ; Observation::UUID ; JSONString ] ;
    [ "originLayout" ; Get ( LayoutName ) ; JSONString ] ;
    [ "originAccount" ; Get ( AccountName ) ; JSONString ] ;
    [ "sourceRecordID" ; Get ( RecordID ) ; JSONNumber ] ) ]
Set Variable [ $reply ; Value: Get ( ScriptResult ) ]
```
Expected: the callee receives JSON text and the caller captures the callee's explicit Exit Script result. Reauthorize in the callee; caller-provided account text is not authority.

### Server detection and detailed errors
`Position ( Get ( ApplicationVersion ) ; "Server" ; 1 ; 1 ) > 0` is a label-based server-context hint, not a capability guarantee. Confirm scheduled/PSOS engine context independently. Use the single-calculation error snapshot in [Script and trigger](#script-and-trigger) immediately after each operation, then log the captured object. Enable `Set Error Capture [ On ]` only alongside actual checks.

### AI token budget
```text
# Immediately after the AI step, capture diagnostics before another AI operation.
Set Variable [ $usageSnapshot ; Value: Get ( LastStepTokensUsed ) ]
If [ JSONGetElement ( $usageSnapshot ; "usage.total_tokens" ) > 7200 ]
  Exit Script [ Text Result: "review-token-budget" ]
End If
```
Expected only when the prior AI step supplies valid usage JSON and total tokens exceeds 7200. Validate missing/malformed usage and the AI step's error separately; the threshold is synthetic. Source usage keys include `model`, `summary`, `usage.prompt_tokens`, `usage.total_tokens`.
