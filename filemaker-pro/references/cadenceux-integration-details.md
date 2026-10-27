# Integration and client details: coverage supplement

This supplements, rather than replaces, [Data API](data-api-reference.md), [OData](odata-api-reference.md), [SQL](sql-reference.md), [Go](filemaker-go-reference.md), and [WebDirect](webdirect-reference.md). Read the corresponding main guide for baseline addressing, authentication, CRUD, authorization and safety. Details below restore the additional coverage in the source references; omission from a short main guide is not a declaration that a capability is unavailable.

Adapted from Darrin Southern / CadenceUX, [claris-filemaker-pro-skill](https://github.com/CadenceUX/claris-filemaker-pro-skill/tree/bda594e15f4a6981e93403c4b187d262ca820116), commit `bda594e15f4a6981e93403c4b187d262ca820116`, the five corresponding `references/*-reference.md` files, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Reusable CadenceUX synthesis is retained/adapted; expressive request/query examples are original synthetic replacements. Claris documentation is separately licensed. No engine, HTTP integration, browser or device execution was performed for this adaptation. Historical upstream verification statements below are attributed source evidence, not our own tests. No live web access is required to use these notes.

## Contents
- [Data API additional contracts](#data-api-additional-contracts)
- [OData additional capabilities and exceptions](#odata-additional-capabilities-and-exceptions)
- [SQL additional syntax and functions](#sql-additional-syntax-and-functions)
- [Go option-level differences](#go-option-level-differences)
- [WebDirect complete exception snapshot](#webdirect-complete-exception-snapshot)
- [Evidence boundaries](#evidence-boundaries)

## Data API additional contracts

### Version, sessions and headers

The source uses `/fmi/data/v1/databases/<DB>`; documented version selectors include `v1`, `v2`, `vLatest`. Select a version supported by the target host. Here `D` denotes that database URL and `L = D/layouts/<LAYOUT>`; neither is a literal path segment. Percent-encode each substituted name.

- Validate a session: `GET https://<HOST>/fmi/data/v1/validateSession`, `Authorization: Bearer <DATABASE_SESSION_TOKEN>`; it is **not** under `D`.
- Login uses Basic file credentials (Server) or `FMID` identity token (Cloud); subsequent requests use the database session Bearer token. See the main guide for the Cloud token-header distinction, which corrects the source's generic `response.token` shorthand.
- Source idle expiry: 15 minutes, reset by authenticated activity. Concurrent-session capacity is configurable in Admin Console, not an unlimited entitlement.
- JSON POST/PATCH bodies: `Content-Type: application/json`; multipart upload: `Content-Type: multipart/form-data` **including the client's generated boundary**. Let a multipart library set the header.
- The source states CORS is unsupported. Treat this as the snapshot's server-side integration recommendation, not a universal prohibition against every separately configured proxy/deployment. Never expose file-account credentials to browsers to work around it.
- Normal JSON result envelopes contain `response` and `messages` with code/message entries. Check HTTP/transport failures too: do not assume a proxy error is a FileMaker JSON envelope. Code `"0"` denotes FileMaker success; nonzero codes require interpretation.

### Global fields

`PATCH D/globals` sets session global fields, with Bearer authorization and a JSON body. Original synthetic request:
```json
{"globalFields":{"IntegrationControl::ReviewBatch_g":"<BATCH_UUID>","IntegrationControl::DryRun_g":"1"}}
```
Expected only if those global fields exist and are writable: values set in this API session. They are not an account-wide, desktop-session or durable configuration store. Follow-up scripts must use the intended session/context.

### Container upload

`POST L/records/<RECORD_ID>/containers/<FIELD_NAME>/<REPETITION>` uploads container data. The source's final `1` is the first repetition, not a record ID. Include Bearer authentication. The multipart form field is `upload`; do not embed a local filename as JSON and expect the server to read the client disk.

Original synthetic command template (replace all placeholders; not executed):
```sh
curl --request POST \
  --header 'Authorization: Bearer <DATABASE_SESSION_TOKEN>' \
  --form 'upload=@./survey-evidence.bin' \
  'https://example.invalid/fmi/data/v1/databases/Habitat/layouts/API_Observation/records/<RECORD_ID>/containers/Evidence/1'
```
The host and schema are fictional. Expected result if the request is permitted and valid: uploaded bytes in that record's first `Evidence` repetition, with a FileMaker response to inspect. Check upload limits, container storage/security, privilege and content validation separately. A subsequent authorized download/readback is an acceptance test, not a claim made here. Official source endpoint: https://help.claris.com/en/data-api-guide/content/upload-container-data.html

### Script hooks and results

The main guide covers `GET L/script/<SCRIPT_NAME>?script.param=<ENCODED_TEXT>`. The one text parameter may contain JSON. `Exit Script` text appears in `response.scriptResult` (possibly absent if no result); `response.scriptError` is the script's FileMaker error code. For record/find hooks:

| Stage | Name / parameter keys | Result / error keys in response |
|---|---|---|
| Before request | `script.prerequest`, `script.prerequest.param` | `scriptResult.prerequest`, `scriptError.prerequest` |
| Before sort | `script.presort`, `script.presort.param` | `scriptResult.presort`, `scriptError.presort` |
| After action/sort | `script`, `script.param` | `scriptResult`, `scriptError` |

Order: prerequest → requested action → presort → sort → final `script`. Check each executed stage independently; a successful outer messages code does not establish a successful script contract. Metadata listing paths remain `GET D/layouts`, `GET L`, `GET D/scripts`. External-source login and OAuth are separate login variants; their documentation paths are preserved in [help-sitemap.md](help-sitemap.md), not silently replaced by file-account Basic login.

## OData additional capabilities and exceptions

The source claims verification of 57 guide pages on **2026-07-25**, FileMaker 26. FileMaker implements intermediate OData conformance with exceptions. Both OData and Data API require a hosted Server/Cloud file and enabled access; neither requires an installed driver. OData uses tables directly, while Data API uses layouts and offers portals. OData is suited to interoperability with other OData systems, replacing some ODBC/JDBC integrations, and batch/transaction workflows; Data API exposes FileMaker layout concepts. `v4` is the OData protocol version, not the FileMaker product release.

### Terms and query options

| OData term | FileMaker interpretation |
|---|---|
| entity | record |
| entity set | table |
| property | field |
| entity container | grouping that need not be a record (source example concept: database name and URL) |
| raw value | binary byte representation, rather than structured JSON/Atom |

A table path can use its name or FileMaker Table ID (FMTID). Keys are a separate metadata concern; FMTID is not a record key. Server accounts/passwords use HTTP Basic; follow the main guide's Cloud `FMID` token contract. The source describes a Cloud OAuth sign-in flow, not permission to send Claris ID passwords as Basic credentials to every endpoint.

| Option | Additional source detail |
|---|---|
| `$filter` | Return rows whose expression evaluates true. Dates/times/timestamps use ISO 8601; offsets are interpreted relative to server time zone. Double-quote field names with spaces or underscores. |
| `$select` | Project named fields. |
| `$expand` | Include related entities, e.g. the fictional relationship name `Observations`. |
| `$orderby` | Order rows. |
| `$top`, `$skip` | Take/omit N; each works alone or together. |
| `$count` | Return record count. |
| `$apply` | Aggregation/grouping transformations; this is not a synonym for arbitrary SQL. |

Original logical filter before URL encoding:
```text
GET <DATABASE_ROOT>/SurveySites?$filter=Category eq 'Marsh' or startswith(Category,'Coast')&$select=SiteCode,Category&$top=12
```
Expected membership: sites classified exactly `Marsh` or whose category starts `Coast`, subject to permissions. Encode the query with a URL library; this is not a tested response.

### Batch, atomic sets and schema

`POST <DATABASE_ROOT>/$batch` submits multiple operations. FileMaker supports atomic operation sets within batch requests: failure of an operation in such a set rolls back that set; do not assume every independently submitted batch part is one global transaction. OData supports schema create/modify/delete, unlike the Data API. Capabilities in the source include create/delete tables, add fields, create/delete indexes, and schema alteration. HTTP POST/PATCH/DELETE apply to the relevant schema resources, **not** SQL text sent to `ExecuteSQL`.

The main guide establishes `POST <DATABASE_ROOT>/FileMaker_Tables` and the `tableName`, `fields`, field `name`/`type` representation. Exact alter/index resource URLs, batch MIME/JSON representation, atomicity-group syntax, request dependencies, rollback scope with invoked scripts and webhook payload options are not specified by the source quick reference. They remain targeted implementation questions, not grounds to omit the capabilities. Do not fabricate those wire contracts; validate a saved version-matched official specification before implementing them. The source's optional online index is https://help.claris.com/markdown/en/odata-guide/index.md.

### Script contract and unsupported features

`POST <DATABASE_ROOT>/Script.<SCRIPT_NAME>` has a completely empty body for no parameter; otherwise supply `scriptParameterValue` (string, number or JSON object). Result keys are `scriptResult.code` and `scriptResult.resultParameter`, the latter carrying Exit Script text. Original synthetic response-shape illustration, not an observed response:
```json
{"scriptResult":{"code":0,"resultParameter":"{\"reviewed\":12}"}}
```
Names cannot start with a number or include special characters such as `@`, `&`, `/`; scripts must run without user interaction.

Unsupported intermediate-conformance features: `$search`; lambda operators `any` and `all`; canonical functions `fractionalseconds()`, `isof()`, `geo.distance()`, `geo.length()`, `geo.intersects()`.

Standard OData calls do not expose external ODBC data-source data, fire script triggers, or support calculations dependent on plug-ins, host filesystem information (`Get(TemporaryPath)`), plug-in information or script-trigger information. Source workaround: explicitly invoke a server-side script (PSOS-like execution) for logic requiring script context. This does not guarantee an absent plug-in is installed or a trigger fires automatically; establish resources and implement required logic explicitly.

Historical catalog context: of 216 script steps, DataAPI had **99 No / 26 Partial** and CWP had **91 No / 26 Partial** in the source. CWP is a contextual comparison, **not an OData compatibility matrix**; inspect the individual step and actual OData execution support. FM 26 added `Export Field Contents` support in Server, Data API and OData contexts.

### Release and error details

- **26.0.1**: `$metadata` includes table/field comments and field AI annotations.
- **26.0.1**: number-field `?` returns `null` instead of invalid JSON; timestamp-looking text remains text.
- **26.0.2 Cloud**: decimal writes no longer round to six significant figures.
- Source shared REST errors: **1700–1715**. Error **953** is “Exceeded limit on data the FileMaker Data API and OData can transmit.” Treat it as a transfer-limit issue; the source's “response too large” shorthand does not prove that merely shrinking one page fixes every licensing/usage condition.

## SQL additional syntax and functions

`ExecuteSQL` is SELECT-only and returns text. ODBC/JDBC provides driver-supported SELECT and data/schema changes (INSERT, UPDATE, DELETE, CREATE/DROP TABLE/INDEX); OData's schema resources are HTTP APIs, not a SQL execution surface. The main guide covers parameter binding, identifier quoting, joins and result safety.

### SELECT clauses and data types

Source grammar coverage, shown schematically rather than as an executable query:
```text
SELECT [DISTINCT] <columns>
FROM <table-occurrence> [AS <alias>]
[JOIN <table-occurrence> ON <predicate>]
[WHERE <predicate>]
[GROUP BY <columns>]
[HAVING <predicate>]
[ORDER BY <columns> [ASC|DESC]]
[OFFSET <n> ROWS]
[FETCH FIRST <n> ROWS ONLY]
```

| FileMaker type | Source SQL mapping / handling |
|---|---|
| Text | VARCHAR, CHAR |
| Number | NUMERIC, DECIMAL, INT, FLOAT |
| Date | DATE; literal `DATE '2026-09-17'` |
| Time | TIME; literal `TIME '14:25:00'` |
| Timestamp | TIMESTAMP; literal `TIMESTAMP '2026-09-17 14:25:00'` |
| Container | Source marks not queryable via SQL; do not infer this bans driver-specific container functions/representations. Ordinary text SELECT is not a portable binary-download contract. |
| Calculation | Queryable according to result type, subject to context/support restrictions. |

### SQL function subset

| Function | Purpose |
|---|---|
| `COUNT(*)` | Row count |
| `SUM(column)` | Sum |
| `AVG(column)` | Arithmetic average |
| `MIN(column)`, `MAX(column)` | Extrema |
| `TRIM(text)` | Strip leading/trailing spaces |
| `UPPER(text)`, `LOWER(text)` | Case conversion |
| `SUBSTR(text, start, length)` | Substring |
| `LENGTH(text)` | String length |
| `CAST(value AS type)` | Type conversion |
| `COALESCE(a, b, ...)` | First non-NULL argument |
| `CASE WHEN ... THEN ... ELSE ... END` | Conditional expression |

These are SQL functions within a query, not automatically interchangeable with FileMaker calculation functions. Exact accepted types and overloads need version-matched validation.

### Original query examples

Synthetic schema: occurrences `HabitatSite(SiteUUID, Label)` and `Visit(VisitUUID, SiteUUID, VisitDate, Minutes, Note)`. They must exist before any example can execute. Outputs below are expectations, not engine observations.
```filemaker
ExecuteSQL (
  "SELECT \"VisitUUID\", \"Minutes\" FROM \"Visit\" WHERE \"Minutes\" >= ? ORDER BY \"VisitUUID\""
  ; Char ( 9 ) ; Char ( 13 ) ; 45 )
// Expected: qualifying identifiers/minutes as tab-separated text; no matches gives empty text.
```
```sql
SELECT s.Label, v.VisitDate
FROM HabitatSite AS s INNER JOIN Visit AS v ON s.SiteUUID = v.SiteUUID
WHERE v.VisitDate >= DATE '2026-09-17'
ORDER BY s.Label

SELECT SiteUUID, COUNT(*), SUM(Minutes), AVG(Minutes), MIN(Minutes), MAX(Minutes)
FROM Visit GROUP BY SiteUUID HAVING COUNT(*) > 1

SELECT UPPER(TRIM(Note)), SUBSTR(Note, 1, 5), LENGTH(Note),
       COALESCE(Note, 'not entered'), CAST(Minutes AS VARCHAR(30)),
       CASE WHEN Minutes >= 60 THEN 'extended' ELSE 'brief' END
FROM Visit

SELECT ROWID, ROWMODID FROM Visit WHERE ROWMODID > 8
```
The join uses explicit key equality, not Relationships Graph joins. INNER and LEFT OUTER JOIN are supported; RIGHT and FULL OUTER JOIN are not. Subqueries include `IN (SELECT ...)`, `EXISTS`, `= ANY` and `> ALL`. NULL requires `IS NULL` / `IS NOT NULL`, not `= NULL`. SELECT results remain text when called through ExecuteSQL; convert individual numeric/date values deliberately.

`ROWID` corresponds to `Get(RecordID)`; `ROWMODID` corresponds to `Get(RecordModificationCount)`. The source corrected earlier **incorrect** `RECORDID` / `MODID` names on 2026-07-25. FM 26 permits double-quoted `"ROWID"` / `"ROWMODID"` and exposes both as named constants. System-column evidence URL: https://help.claris.com/markdown/en/sql-reference/filemaker-system-columns.md; system tables: https://help.claris.com/markdown/en/sql-reference/filemaker-system-tables.md.

### Driver DDL details

Source `table_element_list` grammar, retained as technical syntax (not executable as a whole):
```text
field_name field_type [[repetitions]]
[DEFAULT expr] [UNIQUE | NOT NULL | PRIMARY KEY | GLOBAL]
[FOREIGN KEY REFERENCES table_name(column_name)]
[EXTERNAL relative_path_string [SECURE | OPEN calc_path_string] [FEWER_FOLDERS]]
```
FM 26 adds FOREIGN KEY syntax to CREATE TABLE and ALTER TABLE. This is driver SQL syntax; do not send it to the ExecuteSQL calculation or equate it with an OData JSON schema request. Names have a **100-character limit**; names not beginning with an alphabetic character require double-quoted identifiers (quoting does not waive the length limit). Quote reserved words and spaces as well.

Original synthetic driver-only DDL:
```sql
CREATE TABLE "_HABITAT_TAG" (TagID INT PRIMARY KEY, "_LABEL" VARCHAR(40))
```
Expected only on an authorized compatible driver surface: a new table with those definitions. No schema was created here. The grammar above does not establish every constraint's enforcement behavior; verify it rather than assuming foreign-key syntax supplies a complete application integrity policy.

Reference paths under `https://help.claris.com/en/sql-reference/content/`: `sql-statements.html`, `sql-clauses.html`, `sql-expressions.html`, `sql-functions.html`, `filemaker-system-objects.html`, `filemaker-sql-error-codes.html`, `reserved-sql-keywords.html`.

## Go option-level differences

Upstream verification: Go Help **29 pages** and Development Guide **9 pages**, plus compatibility tables, **2026-07-25**, FM 26. Source catalog totals: **216 steps; 154 Yes, 20 Partial, 42 No**. These are historical catalog measurements, not tests performed here. Unsupported steps are skipped silently with error **3** (Command is unavailable); they do not safely stop subsequent logic. Capture error immediately. Never classify an unrecognized client as desktop by default.

Common Partial steps: `Print`, `Print Setup`, `Print PDF`, `Save Records as PDF`, `Export Records`, `Export Field Contents`, `Import Records`, `Insert File`, `New Window`, `Move/Resize Window`, `Adjust Window`, `Replace Field Contents`, `Save Records as Snapshot Link`.

Source Go-only relative to Pro: `AVPlayer Play`, `AVPlayer Set Options`, `AVPlayer Set Playback State`, `Configure NFC Reading`, `Configure Region Monitor Script`, `Insert from Device`. `Enable Touch Keyboard` also works on Windows touch devices (Partial in Pro), not only Go.

### Missing authoring and formatting features

Go cannot create/modify tables, fields, relationships, data sources, privileges, layouts, scripts, value lists or custom menus. No hosting, plug-ins, text baselines, Excel/XML record import or FMP12/XML record export. Layout and Preview modes are absent; generate/view a PDF for preview-style output.

In Go, users cannot remove views/layouts, add/remove fields, or switch through the Layouts menu to a layout omitted from it; provide a navigation button for such a layout. They cannot define/assign value lists (except permitted value editing in drop-downs/pop-up menus). Tooltips, tab-control leader characters such as `...`, and layout-object shadows are not displayed as on Pro.

The date/time picker cannot select seconds/fractions: switch to keyboard entry. Scripted/calculated time values can still display seconds. Pro print options do not carry over to Go, or vice versa; explicitly set margins for labels/preprinted forms where spacing matters.

### Custom-menu behavior

The Close File item cannot be removed. New menu items must map to existing Go menu items. Custom menus cannot override Quick Find in the ordinary manner; the source directs use of the Edit Custom Menu dialog. Removed items may remain visible but unavailable. iOS/iPadOS system shortcuts and Go shortcuts take precedence over custom-menu shortcuts. Validate the intended custom-menu configuration in Pro and on the device; this is not a promise of desktop menu parity.

### Device capabilities and secure transfer

| Capability | Surface |
|---|---|
| Location/GPS | `Location()`, `LocationValues()` |
| Device sensors | `GetSensor()` |
| iBeacons | `RangeBeacons()` |
| Barcode | Insert from Device / Go scan-barcode feature |
| Camera, photo, video, audio, signature | `Insert from Device`; FM 26 back-camera Flash On/Off/Auto |
| Playback | AVPlayer steps and `GetAVPlayerAttribute()` |
| NFC | `Configure NFC Reading` |
| Regions | `Configure Region Monitor Script` |
| Kiosk-state detection | FM 26 `Get(GuidedAccessState)` returns 1 when iOS Guided Access is active |
| Siri Shortcuts | Go development-guide capability |
| Host credentials and permitted hosts | Go keychain/permitted-host management |

Go opens local or hosted files; HTTPS host tunnelling can be enabled. Keychain manages stored host credentials, and permitted hosts can be explicitly managed. Main-guide transfer/offline/security guidance still applies. Exact OS requirements, Siri Shortcut setup, host-tunnelling configuration, keychain/permitted-host procedures and transfer UI vary by release and are not supplied by the source quick reference. Optional indexes: https://help.claris.com/markdown/en/go-help/index.md and https://help.claris.com/markdown/en/go-development-guide/index.md. Guided Access detection is not a substitute for configuring a secure kiosk policy.

## WebDirect complete exception snapshot

The source attributes its guide review (**40 pages**) to **2026-07-25** and compatibility review to **2026-10-02**, FileMaker **26.0.3**. Counts: **216 steps; 106 Yes, 35 Partial, 75 No**. Consult the bundled catalog's `platform_exceptions.WebDirect` for this snapshot; absent exceptions mean supported **within that catalog**, not universally across releases. No steps run for this adaptation.

No = skipped, error **3**, no alert, no automatic script halt. Partial = executes with option/behavior differences; it is not full support. The source lists these exceptions:

### Not supported (75)

- **Control:** Configure Local Notification; Configure NFC Reading; Configure Region Monitor Script.
- **Navigation:** Enter Preview Mode; Scroll Window.
- **Editing:** Insert from Index; Perform Find/Replace.
- **Fields:** Set Use System Formats; Insert from Device.
- **Records:** Copy Record/Request; Copy All Records/Requests; Save Records as Excel.
- **Windows:** Arrange All Windows; Set Zoom Level; Show/Hide Text Ruler.
- **Files:** Close File; Convert File; New File; Open File; Recover File; Save Records as JSONL; Save a Copy as; Set Multi-User; Close Data File; Create Data File; Delete File; Get Data File Position; Get File Exists; Get File Size; Open Data File; Read from Data File; Rename File; Save a Copy as XML; Set Data File Position; Write to Data File.
- **Spelling:** Check Found Set; Check Record; Check Selection; Correct Word; Edit User Dictionary; Select Dictionaries; Set Dictionary; Spelling Options.
- **Open Menu Item:** Open Manage Database; Open Manage Value Lists; Open Manage Data Sources; Open Settings; Open File Options; Open Help; Open Edit Saved Finds; Open Favorites; Open Find/Replace; Open Hosts; Open Manage Containers; Open Manage Layouts; Open Manage Themes; Open Script Workspace; Open Upload To Host.
- **Miscellaneous:** Beep; Speak (macOS); Flush Cache to Disk; Install Menu Set; Send DDE Execute (Windows); Send Event; Flush Web Viewer Cookies; Allow Formatting Bar; Enable Touch Keyboard; Perform AppleScript (macOS); Save a Copy as Add-on Package; AVPlayer Play; AVPlayer Set Options; AVPlayer Set Playback State; Dial Phone; Get Folder Path.
- **AI:** Configure Machine Learning Model.

### Partial (35)

- **Navigation:** Go to Layout; Go to Related Record; Go to Portal Row; Select Window.
- **Editing:** Insert File; Insert Picture; Insert Audio/Video; Insert PDF; Replace Field Contents; Export Field Contents; Cut; Copy; Paste; Clear.
- **Fields:** Set Selection.
- **Records:** Delete Portal Row; Import Records; Export Records; Save Records as Snapshot Link.
- **Found Sets:** Go to List of Records.
- **Windows:** New Window; Move/Resize Window; Show/Hide Menubar; Adjust Window; View As.
- **Accounts:** Re-Login.
- **Open Menu Item:** Open Sharing; Open URL.
- **Miscellaneous:** Exit Application; Send Mail; Set Web Viewer; Execute SQL.
- **PDF Files:** Save Records as PDF; Print PDF.
- **Printing:** Print Setup.

`Open PDF`, `Append PDF`, `Close PDF` became fully supported in **26.0.3**; earlier 26.0.x hosts treated them as Partial. **From: File** prompts a browser PDF upload; Close PDF **Save to: File** offers a download. The main guide contains the temporary-host-file and ignored-option details. Do not confuse `Execute SQL` (ODBC script step, Partial) with the `ExecuteSQL` calculation function.

### Layout and text limitations

Web users can choose enabled layouts/views but cannot create/delete/modify schema, fields, layouts, scripts, relationships or value lists. **Table View is unsupported**: a default Table View layout uses another enabled view, or List View if none are enabled. Options switching into Table View do not work.

Objects behind other objects cannot be selected, even if the front object is transparent or a click hits empty grouped space. Prefer calculated tab labels, button icons rather than overlaid images, and applying button behavior to a group.

No text highlighting, paragraph styles or tab stops. Rich text is limited to browser-supported button/layout text. Fields show object style rather than field rich text; web users cannot enter rich text, and **editing a field removes existing rich-text formatting**. Custom menus are unsupported.

### Sessions, historical limits and operational design

The source says **generally up to 100 connections per server machine**. Preserve that historical planning figure, **not** an evergreen hard cap: licensed product, release, topology and technical specifications determine the actual maximum. Excess clients see an error when opening the app. Each browser tab/window consumes its own connection. Improper sign-out can hold a connection until timeout; disconnect the specific stale session in Admin Console where possible. Closing the hosted file also reclaims connections but affects all its users.

Design specifically for mobile browsers where needed; hide menu/status bars for controlled UI, but provide explicit navigation/sign-out/file-close controls (there is no desktop application quit). The `Close File` step being unsupported is not permission to omit a supported sign-out flow. Review functions, scripts and triggers separately. Host every required file in a multi-file solution and configure reachable external data sources deliberately.

`Get(ApplicationVersion)` helps identify runtime context, but function support is not established by script-step counts. Error **1225** signals a calculation function unsupported in that context. Claris function pages do not have the script-step Compatibility tables; use function-specific notes and actual tests. Browser matrices, custom-homepage setup, HTTP POST sign-in and release-specific Admin Console settings remain deployment-specific. Optional source index: https://help.claris.com/markdown/en/webdirect-guide/index.md.

## Evidence boundaries

Coverage is source-complete at the quick-reference level when read with the five main guides. This is not a claim of complete vendor documentation. Residual questions are specific: exact OData batch/schema wire representations; per-version driver function/container/constraint behavior; current licensed connection caps and browser/OS requirements; and target-client option behavior. Those require matching specifications or runtime tests, not blanket exclusion of CadenceUX's reusable text. No automatic update check, Claude-specific tooling, or online-fetch prerequisite is introduced.
