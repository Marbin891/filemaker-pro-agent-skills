# Design & Container Functions — Examples

Adapted from **Darrin Southern / CadenceUX**, **CC BY 4.0**, upstream commit [`bda594e15f4a6981e93403c4b187d262ca820116`](https://github.com/CadenceUX/claris-filemaker-pro-skill/commit/bda594e15f4a6981e93403c4b187d262ca820116), `references/design-container-functions-examples.md`. [License](https://creativecommons.org/licenses/by/4.0/). Modifications: independently replaced all worked examples and concrete inline scenarios; retained factual coverage and the CadenceUX-authored reference synthesis; added explicit environment/security boundaries. Claris links identify technical sources, not a license for Claris-authored example expression.

**Validation:** static/editorial review only, **not FileMaker-engine tested**. Expected outputs illustrate intended behavior, not recorded execution. Script-step brackets are configuration outlines, not calculation syntax. `<…>` denotes a placeholder requiring explicit setup. Supply the named tables, fields, relationships, layouts, files, keys and assets in a disposable test solution. File/schema metadata, OCR output and exported data can be sensitive; nothing here was sent to a service. Cryptographic keys/passwords must come from an approved secret store, never hard-coded production secrets. Scripts that close windows, write fields, open files/URLs or export data require deliberate review before running.

## Contents

- [Design functions](#design-functions): BaseTableIDs, BaseTableNames, BaseTableComment, DatabaseNames, FieldBounds, FieldComment, FieldAnnotation, FieldDisplayNames, FieldIDs, FieldNames, FieldRepetitions, FieldStyle, FieldType, GetNextSerialValue, LayoutIDs, LayoutNames, LayoutObjectNames, LayoutTableNames (nonexistent-function warning), RelationInfo, ScriptIDs, ScriptNames, TableIDs, TableNames, ValueListIDs, ValueListItems, ValueListNames, WindowNames; common patterns.
- [Container functions](#container-functions): Base64Decode, Base64Encode, Base64EncodeRFC, CryptAuthCode, CryptDecrypt, CryptDecryptBase64, CryptDigest, CryptEncrypt, CryptEncryptBase64, CryptGenerateSignature, CryptVerifySignature, GetContainerAttribute, GetHeight, GetLiveText, GetLiveTextAsJSON, GetTextFromPDF, GetThumbnail, GetWidth, HexDecode, HexEncode, ReadQRCode, TextDecode, TextEncode, VerifyContainer; common patterns.

---

# Design functions

Source: <https://help.claris.com/en/pro-help/content/design-functions.html>. All **26** actual design functions are covered; FM 26 added BaseTableComment, FieldAnnotation and FieldDisplayNames. The additional LayoutTableNames section is a warning, **not** a 27th function.

`fileName` must identify an **already open** file: design functions never open files. `""` means the current file. TableNames/TableIDs describe **table occurrences** in the relationships graph; BaseTableNames/BaseTableIDs describe **base tables**.

**Whole-value matching:** surround the list and searched name with `¶` before PatternCount; a bare search for `"Depot"` would also match `"Depot Annex"`. This is an exact-value boundary technique, not necessarily case-sensitive comparison.

**LayoutTableNames does not exist** in current FileMaker. Use TableNames for occurrences or BaseTableNames for base tables.

Design functions provide schema metadata about tables, fields, layouts, relationships, scripts, value lists and the file's design environment (including the custom-function domain). They support dynamic references, MCP/AI introspection, developer/admin utilities and data dictionaries. Do not infer a native custom-function-listing function from this overview. Prefer stable IDs or validated names where renames matter. For large schemas, cache results once in variables rather than repeatedly using unstored calculations.

## BaseTableIDs ( fileName )

Returns a return-delimited text list of **base-table** IDs in the same order as BaseTableNames. IDs do not indicate creation order. Parameter: open filename/current-file empty string. **Originated: 20.1.**

```filemaker
BaseTableIDs ( "" )
// In the illustrative archive fixture, the IDs might be 142¶149¶153.
// Inspect actual IDs rather than assuming these values.
```
Look up a base-table ID by its name, handling a missing match explicitly:
```filemaker
Let ( [
  names = BaseTableNames ( "" ) ;
  offset = Position ( ¶ & names & ¶ ; ¶ & "Artifacts" & ¶ ; 1 ; 1 ) ;
  index = If ( offset > 0 ; ValueCount ( Left ( names ; offset ) ) ; 0 )
] ;
  If ( index > 0 ; GetValue ( BaseTableIDs ( "" ) ; index ) ; "" )
)
```

## BaseTableNames ( fileName )

Returns a return-delimited text list of base tables; TableNames instead returns occurrences. Parameter: filename. **Originated: 20.1.**

```filemaker
BaseTableNames ( "" )
// Assume the test file lists Artifacts¶Loans¶Restorations in this order.
```

## BaseTableComment ( fileName ; baseTableName )

Returns the base table's Manage Database > Tables comment as text. Parameters: filename and base-table name. **Originated: 26.0**; table comments themselves date to **22.0.1**.

```filemaker
BaseTableComment ( "" ; "Artifacts" )
// Expected: the comment entered for Artifacts in the test file.
```
Assemble local schema context for a potential AI prompt (GetTableDDL requires an occurrence-name **JSON array**; assume an occurrence also named Artifacts exists):
```filemaker
Let ( [
  description = BaseTableComment ( "" ; "Artifacts" ) ;
  schema = GetTableDDL ( JSONMakeArray ( "Artifacts" ; "" ; JSONString ) ; True )
] ;
  "Collection entity: " & description & ¶ & schema
)
```
This builds text only; inspect it before any separate external disclosure.

## DatabaseNames

No parameters. Returns return-delimited text of open filenames without extensions on **this computer/client**. A hosted solution does not make this a server-wide file inventory.

```filemaker
FilterValues ( DatabaseNames ; "<open-archive-file>" )
// With that file open, expected its name plus a trailing return; otherwise empty.
```

## FieldBounds ( fileName ; layoutName ; fieldName )

Returns `left top right bottom rotation` as space-delimited text. Parameters: open filename (Get(FileName) for current), layout name and fully qualified field name.

```filemaker
FieldBounds ( "<open-archive-file>" ; "<artifact-detail-layout>" ; "Artifacts::CatalogueCode" )
// If the object has these bounds, expected: 24 72 224 96 0.
// All three arguments here are text strings.
```
Extract the top position rather than the full bounds:
```filemaker
Let ( bounds = FieldBounds ( Get ( FileName ) ; Get ( LayoutName ) ; "Artifacts::CatalogueCode" ) ;
  GetValue ( Substitute ( bounds ; " " ; ¶ ) ; 2 )
)
// Expected 72 for the configured bounds above.
```

## FieldComment ( fileName ; fieldName )

Returns a field's Manage Database > Fields comment as text. Parameters: filename, field name; qualify fields outside the current table.

```filemaker
FieldComment ( "<open-archive-file>" ; "Loans::ReturnDue" )
// If configured so, expected: Agreed date for return to the collection.
```
For model-facing schema descriptions, **FM 26.0.1** prefers **annotations**; comments are fallback.

## FieldAnnotation ( fileName ; fieldName )

Returns text from the field's **DDL annotation**, not its comment, set in Advanced Options for Field. Parameters: filename and field name. **Originated: 26.0**; the annotation UI option shipped in **26.0.1**.

```filemaker
FieldAnnotation ( "" ; "Artifacts::Material" )
// Expected: the Material annotation configured in the fixture.
```
When any field in a table has an annotation, only annotated fields appear in that table's generated DDL for GetTableDDL and Perform SQL Query by Natural Language.

## FieldDisplayNames ( fileName ; fieldName )

Returns custom field display names as JSON text, from Advanced Options for Field > Customize field display names. Parameters: filename, field name. **Originated: 26.0.** Built-in keys: `fm_common` (default), `fm_export`, `fm_sort`, `fm_table_view`; custom keys are allowed.

```filemaker
FieldDisplayNames ( "" ; "Artifacts::AccessionYear" )
// If configured so: {"fm_common":"Accession Year","fm_table_view":"Acquired"}
JSONGetElement ( FieldDisplayNames ( "" ; "Artifacts::AccessionYear" ) ; "fm_table_view" )
// Expected Acquired
```
Custom-key label in a layout calculation:
```filemaker
JSONGetElement ( FieldDisplayNames ( "" ; "Artifacts::CatalogueCode" ) ; "cabinet_label" )
// Requires a configured cabinet_label display name.
```

## FieldIDs ( fileName ; layoutName )

Returns field IDs as return-delimited numeric text. Parameters: filename and layout name; `""` uses the current/default layout context described by FileMaker. IDs are stable across field renames; pair with FieldNames for change-resilient references.

```filemaker
FieldIDs ( "<open-archive-file>" ; "<artifact-detail-layout>" )
// Expected IDs of the unique fields on the specified test layout.
```

## FieldNames ( fileName ; layoutName )

Returns field names as return-delimited text. A layout name selects its fields; a **table** name selects all its fields. Local names are **unqualified**; related layout fields are `Table::Field`. An empty layout-name string means the default table. Parameters: filename and layout/table name.

```filemaker
FieldNames ( "" ; "Artifacts" )
// In a simple configured fixture: CatalogueCode¶Material¶AccessionYear.
```
Whole-value existence check on an unqualified local name:
```filemaker
PatternCount ( ¶ & FieldNames ( "" ; "Artifacts" ) & ¶ ; ¶ & "Material" & ¶ ) > 0
```

## FieldRepetitions ( fileName ; layoutName ; fieldName )

Returns text with the repetitions **displayed on the layout** and orientation, not the field's defined maximum. A non-repeating field returns `1 vertical`. Parameters: filename, layout name, field name.

```filemaker
FieldRepetitions ( "<open-archive-file>" ; "<condition-layout>" ; "Artifacts::ConditionReadings" )
// If defined for 8 repetitions but displaying 4 horizontally: 4 horizontal.
```
Use FieldType's final value for the defined maximum.

## FieldStyle ( fileName ; layoutName ; fieldName )

Returns control-style text followed by a value-list name if attached. Parameters: filename, layout name, field name. Styles include `Standard`, `Scrolling` (scroll-bar edit box), `Popuplist`, `Popupmenu`, `Checkbox`, `RadioButton`, `Calendar`.

```filemaker
FieldStyle ( "<open-archive-file>" ; "<condition-layout>" ; "Artifacts::InspectionFlags" )
// If configured as a checkbox set: Checkbox Conservation Checks.
```
Test another control style:
```filemaker
LeftWords ( FieldStyle ( "" ; Get ( LayoutName ) ; "Artifacts::Material" ) ; 1 ) = "Popuplist"
```

## FieldType ( fileName ; fieldName )

Returns four space-separated values as text. Parameters: filename, field name.
1. Storage: `Standard`, `StoredCalc`, `UnstoredCalc`, `Summary`, `Global`, `External(Secure)` or `External(Open)`.
2. Data type: `Text`, `Number`, `Date`, `Time`, `Timestamp` or `Container`.
3. `Indexed` or `Unindexed`.
4. Maximum repetitions (1 for a non-repeating field).

```filemaker
FieldType ( "" ; "Artifacts::Material" )
// If configured as ordinary indexed text: Standard Text Indexed 1.
FieldType ( "" ; "Artifacts::ConditionReadings" )
// If unindexed repeating numbers: Standard Number Unindexed 8.
FieldType ( "" ; "SessionSettings::ReferenceTime" )
// If a global time field: Global Time Unindexed 1.
```
Detect a calculation field, which is not directly writable:
```filemaker
PatternCount ( LeftWords ( FieldType ( "" ; "Loans::DaysRemaining" ) ; 1 ) ; "Calc" ) > 0
```

## GetNextSerialValue ( fileName ; fieldName )

Returns the next configured serial value as **text**, since it can have a prefix. Parameters: filename, fully qualified field name. Useful for previewing the next catalogue number without creating a record; do not treat a preview as a reservation in multi-user use.

```filemaker
GetNextSerialValue ( "<open-archive-file>" ; "Artifacts::CatalogueCode" )
// Returns the configured next serial, for example ARC-0048 in a synthetic fixture.
```

## LayoutIDs ( fileName )

Returns a return-delimited text list of all layout IDs. Parameter: filename.

```filemaker
LayoutIDs ( "<open-archive-file>" )
// Inspect the returned IDs for the configured archive layouts.
```

## LayoutNames ( fileName )

Returns all layout names as return-delimited text. Parameter: filename.

```filemaker
LayoutNames ( Get ( FileName ) )
// Run in the disposable archive file to inventory its layouts.
```
Check before navigating:
```filemaker
If [ PatternCount ( ¶ & LayoutNames ( "" ) & ¶ ; ¶ & "<conservation-queue-layout>" & ¶ ) = 0 ]
  Show Custom Dialog [ "Conservation queue layout is unavailable" ]
Else
  Go to Layout [ "<conservation-queue-layout>" ]
End If
```

## LayoutObjectNames ( fileName ; layoutName )

Returns return-delimited text of **named** layout objects. Objects inside a named tab/slide control, group or portal follow that object and are wrapped in `<` and `>`. Parameters: filename, layout name. **Originated: 8.5.**

```filemaker
LayoutObjectNames ( "<open-archive-file>" ; "<condition-layout>" )
// Only objects explicitly named in the fixture are listed.
```
Check before Go to Object (or Refresh Object):
```filemaker
If [ PatternCount ( ¶ & LayoutObjectNames ( "" ; Get ( LayoutName ) ) & ¶ ; ¶ & "conditionNotesPanel" & ¶ ) > 0 ]
  Go to Object [ Object Name: "conditionNotesPanel" ]
End If
```
Account for the documented container markers when inspecting nested names.

## LayoutTableNames ( fileName ) ⚠️ Does not exist

This is **not a valid FileMaker function** and is absent from current Claris help. It is often confused with TableNames (occurrences) or BaseTableNames (base tables).

Use the Get function for a layout's bound occurrence:
```filemaker
Get ( LayoutTableName )
// On the configured conservation layout, this might return Restorations.
```
For the complete occurrence inventory instead:
```filemaker
TableNames ( Get ( FileName ) )
// A configured fixture might return Artifacts¶Loans¶Artifacts_Loans¶Restorations.
```

## RelationInfo ( fileName ; tableName )

Describes every relationship directly attached to the named **table occurrence**. Parameters: filename and occurrence name. Returns text with one block per relationship, separated by a blank line. Each block contains `Source:` data-source name, `Table:` related occurrence, `Options:` (any of `Delete`, `Create`, `Sorted`, or blank) and one fully qualified predicate per line.

```filemaker
RelationInfo ( "<open-archive-file>" ; "Loans" )
```
Synthetic relationship report demonstrating two blocks and a multi-predicate join (assumes the corresponding graph configuration):
```text
Source: <open-archive-file>
Table: Artifacts
Options: Create
Artifacts::ArtifactID = Loans::ArtifactID

Source: <open-archive-file>
Table: LoanChecks
Options: Create Sorted
LoanChecks::LoanID = Loans::LoanID
LoanChecks::CheckedOn >= Loans::DispatchedOn
```
Inspect actual graph options before depending on record creation/deletion behavior.

## ScriptIDs ( fileName )

Returns all script IDs as return-delimited text. Parameter: filename.

```filemaker
ScriptIDs ( "<open-archive-file>" )
// IDs depend on scripts installed in the archive fixture.
```

## ScriptNames ( fileName )

Returns all script names as return-delimited text. Parameter: filename.

```filemaker
ScriptNames ( Get ( FileName ) )
// Inventory scripts before selecting an approved one.
```
Check existence before calling a known script (existence alone does not authorize its effects):
```filemaker
If [ PatternCount ( ¶ & ScriptNames ( "" ) & ¶ ; ¶ & "<rebuild-loan-index-script>" & ¶ ) > 0 ]
  Perform Script [ Specified: By name ; "<rebuild-loan-index-script>" ]
End If
```

## TableIDs ( fileName )

Returns return-delimited text of relationship-graph **occurrence IDs**, not base-table IDs. IDs do not encode creation order. Parameter: filename; use BaseTableIDs for actual base tables.

```filemaker
TableIDs ( Get ( FileName ) )
// Illustrative occurrence IDs: 1065128¶1065132¶1065135.
// Distinct from this fixture's illustrative base IDs 142¶149¶153.
```

## TableNames ( fileName )

Returns occurrence names as return-delimited text, **not** base-table names. Viewing another file's occurrences requires access to that file. Parameter: filename.

```filemaker
TableNames ( Get ( FileName ) )
// Configured fixture: Artifacts¶Loans¶Artifacts_Loans¶Restorations.
```
Whole-value occurrence existence:
```filemaker
PatternCount ( ¶ & TableNames ( "" ) & ¶ ; ¶ & "Restorations" & ¶ ) > 0
```

## ValueListIDs ( fileName )

Returns a return-delimited text list of value-list IDs. Parameter: filename. (The upstream section had no worked example.)

## ValueListItems ( fileName ; valueList )

Returns a value list's items as return-delimited text. Parameters: filename, value-list name. **WebDirect:** current file only; requesting another file returns empty.

```filemaker
ValueListItems ( "<open-archive-file>" ; "<material-code-value-list>" )
```
Convert a configured list to a JSON payload, locally:
```filemaker
JSONMakeArray ( ValueListItems ( "" ; "Conservation Priorities" ) ; "" ; JSONString )
// For Routine¶Soon¶Immediate, expected ["Routine","Soon","Immediate"].
```
Validate against the whole list in a field-validation calculation:
```filemaker
PatternCount ( ¶ & ValueListItems ( "" ; "Conservation Priorities" ) & ¶ ; ¶ & Self & ¶ ) > 0
```

## ValueListNames ( fileName )

Returns all value-list names as return-delimited text. Parameter: filename.

```filemaker
ValueListNames ( "<open-archive-file>" )
// Expected the fixture's configured value-list names, not their individual items.
```

## WindowNames {( fileName )}

Returns open window names as return-delimited text in stacking order: visible, minimized, then hidden. Optional filename limits results to windows based on that file; omit it for **all** open windows.

```filemaker
WindowNames
// A fixture might have Collection Desk¶Loan Review¶Image Audit.
PatternCount ( ¶ & WindowNames & ¶ ; ¶ & "Loan Review" & ¶ ) > 0
// Expected 1 if that window is open.
```
Close every other window **of this file**, after explicitly opting in. This changes UI state and may encounter record-commit prompts; run only in a disposable test session:
```filemaker
If [ $allowClosingOtherTestWindows = 1 ]
  Set Variable [ $windowList ; Value: WindowNames ( Get ( FileName ) ) ]
  Set Variable [ $keepWindow ; Value: Get ( WindowName ) ]
  Set Variable [ $cursor ; Value: ValueCount ( $windowList ) ]
  Loop [ Flush: Always ]
    Exit Loop If [ $cursor < 1 ]
    Set Variable [ $candidateWindow ; Value: GetValue ( $windowList ; $cursor ) ]
    If [ $candidateWindow ≠ $keepWindow ]
      Close Window [ Name: $candidateWindow ; Current file ]
    End If
    Set Variable [ $cursor ; Value: $cursor - 1 ]
  End Loop
End If
```

## Design common patterns

**Data dictionary for every field in a table:**
```filemaker
While ( [ fields = FieldNames ( "" ; "Artifacts" ) ; index = 1 ; dictionary = "" ] ;
  index <= ValueCount ( fields ) ;
  [ name = GetValue ( fields ; index ) ;
    definition = FieldType ( "" ; "Artifacts::" & name ) ;
    dictionary = List ( dictionary ; name & " | " & definition ) ; index = index + 1 ] ;
  dictionary
)
```
FieldNames supplies unqualified names for this table, so qualify them for FieldType.

**Confirm file availability before cross-file navigation** — Open File must be configured as a real file reference; script-context rules may require a target-file script for navigation:
```filemaker
If [ IsEmpty ( FilterValues ( DatabaseNames ; "<conservation-file>" ) ) ]
  Open File [ "<conservation-file-reference>" ]
End If
If [ not IsEmpty ( FilterValues ( DatabaseNames ; "<conservation-file>" ) ) ]
  If [ PatternCount ( ¶ & LayoutNames ( "<conservation-file>" ) & ¶ ; ¶ & "<treatment-board-layout>" & ¶ ) > 0 ]
    Go to Layout [ "<treatment-board-layout>" (<conservation-file>) ]
  End If
End If
```
Design functions do not open the file; this explicit Open File step does. Check privileges/file-opening errors before relying on the result.

**Dynamic field export for the current layout** — builds a local JSON object, no transmission:
```filemaker
While ( [
  fields = FieldNames ( Get ( FileName ) ; Get ( LayoutName ) ) ; index = 1 ; snapshot = "{}"
] ; index <= ValueCount ( fields ) ;
  [ fieldName = GetValue ( fields ; index ) ;
    keyName = Substitute ( fieldName ; "::" ; "__" ) ;
    snapshot = JSONSetElement ( snapshot ; "['" & keyName & "']" ; GetField ( fieldName ) ; JSONString ) ;
    index = index + 1 ] ; snapshot
)
```
This fixture assumes names contain no apostrophes and the key transform has no collisions. All values become JSON strings; review type handling, field access and sensitive-field exclusion before production export.

**Next serial without a new record:**
```filemaker
Set Variable [ $cataloguePreview ; Value: GetNextSerialValue ( Get ( FileName ) ; "Artifacts::CatalogueCode" ) ]
Show Custom Dialog [ "Upcoming catalogue code (not reserved)" ; $cataloguePreview ]
```

---

# Container functions

Source: <https://help.claris.com/en/pro-help/content/container-functions.html>. All **24** container functions are covered with signatures, return types and examples.

**Encryption:** Crypt* functions (**FM 16+**) provide encryption, hashing and signatures. Base64EncodeRFC or HexEncode turn binary cryptographic results into text. Text encoding, hashing and signing must agree on exact input bytes; none of these examples supplies a production key.

## Base64Decode ( text {; fileNameWithExtension } )

Decodes Base64 into container data or text. Parameters: Base64 text and optional filename; a filename stores the result as a named container file. Returns container/text.

```filemaker
Base64Decode ( "U3RhciBtYXA=" ; "star-map.txt" )
// Expected a named text container whose decoded UTF-8 bytes spell Star map.
// For an encoded image, substitute a complete image fixture and matching extension;
// a shortened Base64 prefix is not a usable image.
```

## Base64Encode ( data )

Returns RFC 2045 Base64 text, wrapping at 76 characters and **ending in CR+LF**. Text becomes UTF-8 first; containers are encoded as-is without retaining the filename. Parameter: text/container data. For HTTP headers, tokens or signatures use Base64EncodeRFC(4648) to avoid line breaks.

```filemaker
Base64Encode ( "Cedar" )
// Expected Q2VkYXI= followed by CR+LF.
```

## Base64EncodeRFC ( RFCNumber ; data )

Returns Base64 text for the selected RFC. Parameters: RFC number and text/container data. `1421`: 64-character lines/CRLF; `2045`: 76-character lines/CRLF; `3548`/`4648`: no line breaks; `4880`: 76-character lines/CRLF plus CRC. Unrecognized RFC values fall back to 4648. **Originated: 16.0.**

```filemaker
Base64EncodeRFC ( 4648 ; "Cedar" )
// Expected Q2VkYXI=, with no trailing line break.
```
There is no URL-safe Base64 option: for JWT-style encoding, replace `+` with `-`, `/` with `_`, and remove `=` padding yourself, according to the protocol's requirements.

## CryptAuthCode ( data ; algorithm ; key )

Returns binary HMAC container data. Parameters: data, algorithm, secret key. Algorithms: `MD5`, `SHA1`, `SHA224`, `SHA256`, `SHA384`, `SHA512`; empty algorithm means **SHA512**, unsupported names return `?`. Encode the result to text using Base64EncodeRFC or HexEncode.

```filemaker
Base64EncodeRFC ( 4648 ; CryptAuthCode ( "cabinet=west&seal=17" ; "SHA256" ; $approvedHMACKey ) )
// Expected Base64 representation of the HMAC; key-dependent, no fixed value asserted.
```
`$approvedHMACKey` must be supplied from a secret store. HMAC authenticates with a shared secret; it is not encryption.

## CryptDecrypt ( container ; key )

Decrypts data from CryptEncrypt. Parameters: encrypted container and matching key. Returns container.

```filemaker
CryptDecrypt ( CryptEncrypt ( "Restoration batch R-27" ; $approvedEncryptionKey ) ; $approvedEncryptionKey )
// Round trip returns container data carrying the original text bytes.
```

## CryptDecryptBase64 ( text ; key )

Decrypts Base64 text produced by CryptEncryptBase64. Parameters: ciphertext text and matching key. Returns **container**, not automatically plain text.

```filemaker
CryptDecryptBase64 ( CryptEncryptBase64 ( "Cabinet access interval" ; $approvedEncryptionKey ) ; $approvedEncryptionKey )
// Round trip yields a container; TextDecode can recover text if the encoding is known.
```

## CryptDigest ( data ; algorithm )

Returns a binary hash as container data. Parameters: data and algorithm. Algorithm names are the same as CryptAuthCode; empty means SHA512.

```filemaker
HexEncode ( CryptDigest ( "archive-fixture-27" ; "SHA256" ) )
// Expected a 64-character uppercase hexadecimal SHA-256 digest.
// No engine-derived exact digest is asserted here.
```
An unkeyed digest alone does not establish who sent a message.

## CryptEncrypt ( data ; key )

Encrypts text/container data and returns a container file named `encrypted.data`. Parameters: data, key. Decrypt using CryptDecrypt with the same key. Keep keys outside the database file; consult the FileMaker Security Guide.

```filemaker
CryptEncrypt ( "Loan crate seal register" ; $approvedEncryptionKey )
// The ciphertext is not a deterministic worked-output fixture.
```

## CryptEncryptBase64 ( data ; key )

Encrypts data and Base64-encodes the ciphertext for storage in a text field. Parameters: data, key. Returns text.

```filemaker
CryptEncryptBase64 ( "Conservation locker allocation" ; $approvedEncryptionKey )
// Store the ciphertext text; retain the key only in the approved secret system.
```

## CryptGenerateSignature ( data ; algorithm ; privateRSAKey ; keyPassword )

Returns binary signature container data. Parameters: data to sign, algorithm (`SHA256`, `SHA384`, `SHA512`), private RSA key and its password.

```filemaker
Base64EncodeRFC ( 4648 ; CryptGenerateSignature (
  $approvedManifestBytes ; "SHA384" ; $privateRSAKeyFromSecretStore ; $privateKeyPassword
) )
// Produces unwrapped Base64 suitable for a protocol expecting this signature encoding.
```
Private key material and the password are environment inputs, not fields to populate with production secrets in a sample file.

## CryptVerifySignature ( data ; algorithm ; publicRSAKey ; signature )

Returns number **1** for a valid RSA signature, **0** otherwise. Parameters: exact signed data, matching algorithm, public RSA key, binary signature.

```filemaker
CryptVerifySignature ( $receivedManifestBytes ; "SHA384" ; $trustedPublicRSAKey ;
  Base64Decode ( $receivedSignatureBase64 ; "manifest-signature.bin" )
)
```
Use the same bytes and algorithm used for signing, and obtain the public key through a trusted mechanism.

## GetContainerAttribute ( field ; attributeName )

Returns metadata from a container field/value. Parameters: container, case-insensitive attribute name. Return type varies: text, number, date, time, timestamp or container.

- General: `filename`, `fileSize`, `MD5`, `storageType` (Embedded / External (Secure) / External (Open) / File Reference / Text), `internalSize`, `externalSize`, `externalFiles`.
- Images: `width`, `height`, `dpiWidth`, `dpiHeight`, `transparency`.
- For photo, audio/video, signature and barcode attributes, consult the current Claris page.
- `all` returns every attribute as a list.

```filemaker
GetContainerAttribute ( TextEncode ( "Compass" ; "utf-8" ; 1 ) ; "fileSize" )
// Expected 7 bytes for this ASCII UTF-8 fixture.
```
Some attributes (`photo`, `created`, `modified`, `all`) may be invalid for Windows/Cloud-hosted files read through REST APIs.

## GetHeight ( field )

Returns numeric pixel height for an image container, or **0** for non-image data. Parameter: container field.

```filemaker
GetHeight ( Artifacts::ConditionPhoto )
// Expected 900 if the supplied fixture image is 1200 × 900 pixels.
```

## GetLiveText ( container ; language )

Returns recognized image text via on-device OCR. Parameters: image container, language identifier. Supported **iOS, iPadOS, macOS**, not Windows/Linux. **Originated: 19.5.** Languages: `en-US`, `fr-FR`, `it-IT`, `de-DE`, `es-ES`, `pt-BR`, `zh-Hans`, `ja-JP`, `ko-KR`, `uk-UA`, `th-TH`, `vi-VN`, `ar-SA`, `ars-SA`; the final two require **iOS/iPadOS 18 or macOS 15**. Bare language codes are not accepted substitutes for these identifiers.

Supports PNG, JPEG, GIF, TIFF, BMP and PDF; **transparent-background PNGs are unsupported**.

```filemaker
Set Field [ Artifacts::LabelTranscript ; GetLiveText ( Artifacts::LabelPhoto ; "fr-FR" ) ]
// Requires a supported device and a readable French label-image fixture.
```

## GetLiveTextAsJSON ( container ; language )

Like GetLiveText, but returns JSON text representing an **array**, one object per recognized line with `x`, `y` (pixel positions from the top-left) and `text`. Parameters and language/platform restrictions as above. **Originated: 21.0.**

```filemaker
GetLiveTextAsJSON ( Artifacts::LabelPhoto ; "fr-FR" )
// Synthetic shape, not measured OCR: [{"x":48,"y":92,"text":"Salle des cartes"}]
```

## GetTextFromPDF ( container )

Returns plain text from a PDF container. Parameter: PDF container. **Originated: 22.0.** Returns `?` if empty/not a PDF, no text is found, password-protected or unreadable. On **Windows/Linux**, scanned-image PDFs also return `?`; macOS handles scanned PDFs.

```filemaker
PatternCount ( GetTextFromPDF ( Loans::PackingGuidePDF ) ; "humidity" ) > 0
// Tests for a term in a readable fixture PDF; handle ? separately before relying on this test.
```

## GetThumbnail ( field ; width ; height )

Returns an image container scaled to fit the width × height pixel box, preserving aspect ratio. Parameters: image field and bounding width/height.

```filemaker
Set Field [ Artifacts::PreviewImage ; GetThumbnail ( Artifacts::ConditionPhoto ; 96 ; 64 ) ]
Export Field Contents [ Artifacts::PreviewImage ; "<approved-preview-export-path>" ; Create folders: Off ]
```
Export is a separate write operation; replace the path only after selecting an approved destination.

## GetWidth ( field )

Returns numeric pixel width of a container image, **0** for non-image data. Parameter: container field.

```filemaker
GetWidth ( Artifacts::ConditionPhoto )
// Expected 1200 for the supplied 1200 × 900 fixture image.
```

## HexDecode ( data {; fileNameWithExtension } )

Decodes hexadecimal text into binary container data or text; inverse of HexEncode. Parameters: hex text and optional container filename. Returns container/text.

```filemaker
HexDecode ( "536B796D6170" )
// Expected Skymap
```

## HexEncode ( data )

Returns **uppercase** hexadecimal text. Parameter: text/container. Text becomes UTF-8 before encoding; container bytes are used as-is.

```filemaker
HexEncode ( "Skymap" )
// Expected 536B796D6170
```

## ReadQRCode ( container )

Returns the text value of a QR code in an image. Parameter: image container. For other barcode types, use **Insert from Device in FileMaker Go**. **Originated: 19.5**; Linux requires **Ubuntu 22.04+**.

```filemaker
Set Variable [ $scannedDestination ; Value: ReadQRCode ( Artifacts::CrateTagImage ) ]
Show Custom Dialog [ "Review scanned destination" ; $scannedDestination ]
If [ $allowOpeningReviewedURL = 1 and
     Left ( $scannedDestination ; Length ( "https://<approved-catalogue-host>/" ) ) = "https://<approved-catalogue-host>/" ]
  Open URL [ With dialog: On ; $scannedDestination ]
End If
```
Non-executed outline. Replace the host placeholder and use robust URL parsing/allowlisting in production; a QR code is untrusted input. Decoding does not authorize opening it, and no URL was opened for validation.

## TextDecode ( container ; encoding )

Returns text decoded from a text-file container. Parameters: container and one of the TextEncode encoding names below.

```filemaker
TextDecode ( TextEncode ( "piñata" ; "windows-1252" ; 1 ) ; "windows-1252" )
// Expected piñata
```

## TextEncode ( text ; encoding ; lineEndings )

Returns a text-file container. Parameters: text, encoding name, numeric line-ending mode. Encodings: `utf-8`, `iso-8859-1`, `windows-1251`, `shift_jis`, `windows-1252`, `gb18030`, `euc-kr`, `big5`, `macintosh`; unsupported names return `?`.

Line endings: **1** unchanged; **2** CR (legacy Mac); **3** LF (macOS/Unix/Linux); **4** CRLF (Windows). Unrecognized values, including text rather than numbers, silently behave as unchanged.

```filemaker
Set Field [ Exports::EncodedChecklist ; TextEncode ( Exports::ChecklistText ; "utf-8" ; 3 ) ]
Export Field Contents [ Exports::EncodedChecklist ; "<approved-checklist-export-path>" ; Create folders: Off ]
```
The configured export path should identify a disposable test `.txt` file.

## VerifyContainer ( field )

Checks **externally stored** container data. Parameter: container field. Returns number 0 if the external file was changed/deleted outside FileMaker, 1 if unchanged, or `?` if the argument is not a container field.

```filemaker
If ( VerifyContainer ( Artifacts::ExternalScan ) = 0 ; "Scan needs integrity review" ; "Scan check passed" )
```
For a generalized utility, handle `?` separately rather than treating every nonzero/error result as success.

## Container common patterns

**Encrypt to text storage; decrypt for display:**
```filemaker
// Auto-enter calculation on Loans::EncryptedAccessMemo (key supplied securely):
CryptEncryptBase64 ( Loans::AccessMemo ; $approvedEncryptionKey )

// Display/script calculation; CryptDecryptBase64 itself returns a container:
TextDecode ( CryptDecryptBase64 ( Loans::EncryptedAccessMemo ; $approvedEncryptionKey ) ; "utf-8" )
```
Ensure key availability/lifetime is deliberately configured for the calculation context; do not assume a script-local variable is universally accessible to auto-enter calculations. Keep keys outside the database, even though the outline names a local variable.

**Webhook HMAC verification:**
```filemaker
Let ( [
  bodyBytes = $receivedBodyBytes ;
  signingKey = $approvedWebhookSecret ;
  expectedMAC = Base64EncodeRFC ( 4648 ; CryptAuthCode ( bodyBytes ; "SHA256" ; signingKey ) ) ;
  suppliedMAC = Trim ( $receivedMACHeader )
] ;
  Exact ( expectedMAC ; suppliedMAC )
)
```
Expected 1 only for matching signatures under the agreed protocol. The body must be **byte-for-byte** what was signed: do not normalize whitespace/encoding. Remove a protocol prefix such as `hmac-sha256=` separately if required. Use Base64EncodeRFC, not Base64Encode, whose CRLF would alter the encoded value. Use **Exact**, not FileMaker's case-insensitive `=`: Base64 is case-sensitive. This demonstrates value comparison, not a claimed constant-time authentication implementation; production receivers should also enforce replay protection and their protocol's authentication rules.

**Aspect-ratio-aware thumbnail with non-image/zero guards:**
```filemaker
Let ( [
  width = GetWidth ( Artifacts::ConditionPhoto ) ;
  height = GetHeight ( Artifacts::ConditionPhoto ) ;
  edge = 180
] ;
  If ( width > 0 and height > 0 ;
    Let ( ratio = Min ( edge / width ; edge / height ) ;
      GetThumbnail ( Artifacts::ConditionPhoto ; width * ratio ; height * ratio )
    ) ; ""
  )
)
```

**OCR then extract a catalogue-code line** (rather than merely returning the unparsed OCR):
```filemaker
Let ( recognized = GetLiveText ( Artifacts::LabelPhoto ; "en-US" ) ;
  While ( [ index = 1 ; code = "" ; prefix = "Catalogue: " ] ;
    index <= ValueCount ( recognized ) and IsEmpty ( code ) ;
    [ line = GetValue ( recognized ; index ) ;
      code = If ( Left ( line ; Length ( prefix ) ) = prefix ;
        Trim ( Middle ( line ; Length ( prefix ) + 1 ; Length ( line ) ) ) ; "" ) ;
      index = index + 1 ] ; code
  )
)
```
Uses only native calculations; an application may instead supply a reviewed custom parser or filter. Custom functions can have side effects depending on their implementation; inspect them rather than assuming that “custom function” implies safe/pure behavior. OCR accuracy is input/device-dependent; no recognition result was engine-tested here.
