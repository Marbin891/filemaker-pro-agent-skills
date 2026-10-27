# Logical, JSON & AI Functions — Examples

Adapted from **Darrin Southern / CadenceUX**, licensed **CC BY 4.0**, upstream commit [`bda594e15f4a6981e93403c4b187d262ca820116`](https://github.com/CadenceUX/claris-filemaker-pro-skill/commit/bda594e15f4a6981e93403c4b187d262ca820116), `references/logical-json-ai-functions-examples.md`. [License](https://creativecommons.org/licenses/by/4.0/). Modifications: replaced the worked examples and concrete inline scenarios with independently written teaching examples; retained the factual function coverage and CadenceUX-authored reference synthesis; clarified evaluation safety and external-service prerequisites. Claris documentation links below identify technical sources, not a license for Claris-authored example expression.

**Validation:** editorial/static review only. No FileMaker engine was available; none of these calculations or script outlines has been engine-tested. Outputs are expected illustrations, not recorded execution. Script-step brackets describe configuration, not pasteable calculation syntax. Every `<…>` value is a placeholder to replace deliberately. Tables, fields, relationships, layouts, models and found sets must be supplied in a disposable test file. Remote AI examples are **non-executed outlines**: account names, provider/model selections, endpoints and secrets require explicit configuration and authorization; running them can transmit input/schema to a provider. No data was transmitted to validate this document. Keep secrets in an approved secret store, not source code or a global field.

## Contents

- [Logical functions](#logical-functions): Case, Choose, Evaluate, EvaluationError, ExecuteSQL, ExecuteSQLe, GetAsBoolean, GetField, GetNthRecord, GetSummary, If, IsEmpty, IsValid, IsValidExpression, Let, Lookup, LookupNext, Self, SetRecursion, While; common patterns.
- [JSON functions](#json-functions): JSONDeleteElement, JSONFormatElements, JSONGetElement, JSONGetElementType, JSONListKeys, JSONListValues, JSONMakeArray, JSONParse, JSONParsedState, JSONSetElement; common patterns.
- [AI functions](#ai-functions): AddEmbeddings, ComputeModel, CosineSimilarity, GetEmbedding, GetEmbeddingAsFile, GetEmbeddingAsText, GetFieldsOnLayout, GetModelAttributes, GetRAGSpaceInfo, GetTableDDL, GetTokenCount, NormalizeEmbedding, PredictFromModel, SubtractEmbeddings; common patterns.

---

# Logical functions

Source: <https://help.claris.com/en/pro-help/content/logical-functions.html>. All **20** logical functions are covered below with syntax, parameters, return types and usage patterns. Logical functions control flow, evaluate expressions, access field contents dynamically and bridge scripting with calculations. `Let` and `While` are particularly useful foundations.

## Case ( test1 ; result1 {; test2 ; result2 ; ... ; defaultResult } )

Tests are evaluated in order; the first true test selects its paired result. If none is true, the optional unpaired trailing `defaultResult` is returned, or empty if omitted. Parameters are alternating tests/results and optional default. Returns any type, matching the selected result.

Three-way capacity classification (assume `Crates::SlotsFree` exists):
```filemaker
Case ( Crates::SlotsFree >= 24 ; "Room for a pallet" ;
       Crates::SlotsFree > 6 ; "Room for loose boxes" ; "Nearly full" )
// At 12 free slots, expected: Room for loose boxes
```
Several conditions in one test:
```filemaker
Case (
  Kilns::State = "Running" and Kilns::Temperature > 950 ; "Inspect heat" ;
  Kilns::State = "Running" ; "Monitor cycle" ;
  Kilns::State = "Offline" ; "Maintenance queue" ;
  "State unclassified"
)
```
Nested routing, while preferring flat branches when practical:
```filemaker
Case (
  Parcels::Service = "Frozen" ; Case ( Parcels::HasCoolant ; "Cold dispatch" ; "Add coolant" ) ;
  Parcels::Service = "Fragile" ; "Cushioned dispatch" ;
  "Standard dispatch"
)
```

## Choose ( test ; result0 {; result1 ; result2...} )

Maps an integer index to a result, starting at **0**. Negative or out-of-range indexes return empty. Parameters: integer `test`, then result values. Returns any type. Use Choose rather than Case for index mapping: a numeric test in Case is interpreted as true/false, not as a position.

```filemaker
Choose ( Sensors::ModeIndex ; "Standby" ; "Sampling" ; "Calibrating" )
// ModeIndex = 2 selects Calibrating
```
Another mapping, with an explicit zero-based code convention:
```filemaker
Choose ( Tickets::QueueCode ; "Unassigned" ; "Triage" ; "Workshop" ; "Ready for pickup" )
// QueueCode 0, 1, 2, 3 select those labels in that order.
```

## Evaluate ( expression {; [field1 ; field2 ;...]} )

Evaluates a text expression as a FileMaker calculation at runtime. The optional field-dependency list triggers recalculation when those fields change. Parameters: calculation text and optional dependency fields. Returns the evaluated result, of any type.

Assume `FormulaPad::ExpressionText` contains the text `7 * 6`:
```filemaker
Evaluate ( FormulaPad::ExpressionText )
// Expected number: 42
Evaluate ( "FormulaPad::ExpressionText" )
// Expected text: 7 * 6 (the field reference is evaluated, not its contents again)
Evaluate ( GetField ( "FormulaPad::ExpressionText" ) )
// Expected number: 42
Evaluate ( FormulaPad::ExpressionText ; [ FormulaPad::Hours ] )
// If the expression text is 1.25 * FormulaPad::Hours and Hours = 8, expected: 10
```
Dynamic reference; `$approvedField` must come from an allowlist:
```filemaker
Evaluate ( "Telemetry::" & $approvedField )
```
`Let` can assemble a trusted expression in stages; this is **not** a security boundary:
```filemaker
Let ( expressionText = "Ceiling ( " & GetAsNumber ( Batches::Pieces ) & " / 8 )" ;
  Evaluate ( expressionText )
)
```
Server-side Evaluate text must use **English function names**; localized names are not recognized there. Syntax validation does not establish safety. Evaluate can invoke custom functions or plug-ins with side effects; do not evaluate untrusted input. Use fixed calculations or a narrowly allowlisted expression system instead.

## EvaluationError ( expression )

Returns a numeric error code, or 0 on success. The parameter is an expression, not necessarily text. For formula-text syntax errors, enclose **Evaluate**: checking plain text only evaluates that text value and returns 0.

```filemaker
EvaluationError ( GetField ( "Telemetry::RetiredReading" ) * 2 )
// Expected 102 (field missing) if that field has been removed.
```
Error handling for a trusted dynamic field (not a sandbox; successful evaluation happens twice here):
```filemaker
Let ( referenceText = "Telemetry::" & $approvedField ;
  If ( EvaluationError ( Evaluate ( referenceText ) ) = 0 ;
    Evaluate ( referenceText ) ; "Reading unavailable"
  )
)
EvaluationError ( Evaluate ( "7 *" ) )
// Expected 1204: an operand is missing.
```
Use this only for trusted expressions; the first evaluation can itself have side effects.

## ExecuteSQL ( sqlQuery ; fieldSeparator ; rowSeparator { ; arguments... } )

Runs a SQL SELECT against table occurrences, returning text, or `"?"` on error. Parameters: SQL query text, field separator, row separator, optional values substituted for `?` placeholders. Separators can be commas, return characters or other text.

Assume the named occurrence and fields exist:
```filemaker
ExecuteSQL ( "SELECT Habitat FROM Specimens WHERE AccessionNo = 73" ; "" ; "" )
// If accession 73 has Habitat = Estuary, expected: Estuary.
// Independent of the current record, found set and layout.
```
Parameterized filtering avoids concatenating data into SQL and handles value quoting/types:
```filemaker
ExecuteSQL (
  "SELECT BatchCode, Mass FROM Samples WHERE SiteID = ? AND Phase = ?" ;
  " | " ; ¶ ; Sites::ID ; "Dried"
)
```
Aggregate query:
```filemaker
ExecuteSQL ( "SELECT AVG(Mass) FROM Samples WHERE SiteID = ?" ; "" ; "" ; Sites::ID )
```
Important caveats:
- `FROM` and `JOIN` name **table occurrences**, not base tables.
- Relationships in the graph are ignored: write joins explicitly.
- SELECT only; no INSERT, UPDATE, DELETE or schema modification.
- Any error returns `?`; branch on that result or use ExecuteSQLe for details.
- Date/time literals use ODBC formats `DATE 'YYYY-MM-DD'` and `TIME 'HH:MM:SS'`.
- Bind values with `?`; identifier names still require trusted selection and correct quoting.

## ExecuteSQLe ( sqlQuery ; fieldSeparator ; rowSeparator { ; arguments... } )

Same parameters and SELECT behavior as ExecuteSQL. Returns text results, or a detailed error beginning `? ERROR: FQLnnnn/(line:offset): message`.

```filemaker
ExecuteSQLe ( "SELECT MissingLabel FROM Specimens WHERE AccessionNo = ?" ; "" ; "" ; 73 )
// If MissingLabel is absent, expect an FQL0007 column-resolution error.
// The diagnostic identifies the offending column and its query position.
```
Detect failure, for example, with `Left ( $sqlDiagnostic ; 1 ) = "?"`. Exact message/offset depends on the query and environment.

## GetAsBoolean ( data )

Returns number 1 for data converting to a non-zero number, or a container holding data; otherwise 0. Non-numeric text is false: this is **not** an emptiness test. Parameter: data of any appropriate type.

```filemaker
GetAsBoolean ( "" )                    // Expected 0
GetAsBoolean ( "maintenance pending" ) // Expected 0
GetAsBoolean ( "-12 volts" )           // Expected 1
GetAsBoolean ( Scans::BadgeImage )      // 1 with container data; 0 when empty
```
A numeric checkbox flag:
```filemaker
If ( GetAsBoolean ( Volunteers::SafetyTrained ) ; "Cleared for shift" ; "Training needed" )
```

## GetField ( fieldName )

Returns the contents of the field named by the text parameter. Unqualified names resolve in the current calculation's table context; qualify other fields with `TableOccurrence::FieldName`. Returns any type.

Assume the current table is `Stations`, and `Stations::PreferredReading` holds either `WindSpeed` or `AirPressure`:
```filemaker
GetField ( "WindSpeed" )
// Expected: current Stations::WindSpeed value
GetField ( Stations::PreferredReading )
// Expected: the selected reading field's contents
```
Variable-driven access:
```filemaker
GetField ( "Stations::" & $approvedReadingName )
```
Unlike Evaluate, GetField accepts a **field reference only**, not an arbitrary calculation expression.

## GetNthRecord ( field ; recordNumber )

Returns a field value from the specified **1-based** record position in the current found set. Parameters: field reference and integer position. Returns any type.

```filemaker
GetNthRecord ( Samples::Mass ; 4 )
// Expected: fourth found record's Mass in the current Samples context.
```
Compare adjacent records without navigating; first record has no predecessor:
```filemaker
Let ( [
  position = Get ( RecordNumber ) ;
  foundCount = Get ( FoundCount )
] ;
  If ( foundCount > 0 and position > 1 ;
    List ( GetNthRecord ( Samples::Mass ; position - 1 ) ; Samples::Mass ) ;
    List ( "No preceding sample" ; Samples::Mass )
  )
)
```
Sort order determines which record is “previous.”

## GetSummary ( summaryField ; breakField )

Returns a summary for the current sort group. Blank unless the found set is sorted by the break field. Use the summary field itself as the break field for the grand summary. Parameters: summary-field reference and break-field reference. Returns number, date, time or timestamp; calculations using it are unstored.

```filemaker
GetSummary ( Harvests::TotalWeight ; Harvests::Orchard )
// Requires a TotalWeight summary field and sorting by Orchard.
```
Group percentage, assuming a nonzero grand summary:
```filemaker
GetSummary ( Harvests::TotalWeight ; Harvests::Orchard ) /
GetSummary ( Harvests::TotalWeight ; Harvests::TotalWeight ) * 100
// If group weight is 180 and grand weight 900, expected: 20.
```

## If ( test ; result1 {; result2 } )

Returns result1 when the test converts to a non-zero number; otherwise result2, or empty if omitted. Parameters: test, true-result, optional false-result. Returns any type. Text without digits is false: `If ( "pending" ; "Proceed" ; "Wait" )` is expected to return `Wait`.

```filemaker
If ( Shipments::RequiresChilling ; "Use insulated cage" ; "Use dry cage" )
// With a numeric flag of 0, expected: Use dry cage.
```
Nested binary decisions (prefer Case for more than two branches):
```filemaker
If ( Batteries::Charge >= 85 ; "Ready" ; If ( Batteries::Charge >= 35 ; "Top up" ; "Recharge now" ) )
```
Guard division by zero:
```filemaker
If ( Runs::ElapsedHours ≠ 0 ; Runs::Distance / Runs::ElapsedHours ; 0 )
```

## IsEmpty ( field )

Returns number 1 if empty **or** if the field, related table, relationship or file is missing, or another error occurs. Otherwise returns 0. A numeric zero is not empty; a container holding a file is not empty. Parameter: field/expression to inspect.

```filemaker
IsEmpty ( Specimens::AccessionNo )
// Expected 1 when no accession value exists.
IsEmpty ( 0.0 )
// Expected 0.
```
Required-field feedback before saving:
```filemaker
If ( IsEmpty ( Reservations::DockID ) ; "Choose a dock" ; "Dock supplied" )
```

## IsValid ( field )

Returns number 0 for a value invalid for its data type, such as imported non-date text in a date field; returns 1 if valid **or empty**. Parameter: field. This does not mean that every business validation rule is satisfied.

```filemaker
IsValid ( Permits::ExpiryDate )
// Expected 0 if an invalid textual value was imported into this date field.
```
Check typed dates before subtraction; require nonempty values separately where necessary:
```filemaker
If ( IsValid ( Voyages::DepartureDate ) and IsValid ( Voyages::ArrivalDate ) ;
  Voyages::ArrivalDate - Voyages::DepartureDate ; "Repair voyage dates"
)
```

## IsValidExpression ( expression )

Takes calculation **text** and returns number 1 if syntactically valid, otherwise 0.

```filemaker
IsValidExpression ( "Round ( 17 / 6 ; 1 )" ) // Expected 1
IsValidExpression ( "Round ( 17 / 6 ;" )     // Expected 0
```
Syntax feedback before evaluating an **already trusted/allowlisted** formula:
```filemaker
If ( IsValidExpression ( $approvedCalculationText ) ;
  Evaluate ( $approvedCalculationText ) ; "Repair calculation syntax"
)
```
**Valid syntax is not safe execution.** This check does not authorize arbitrary user formulas. Custom functions and plug-ins can have side effects, and expensive calculations can exhaust resources. Never treat this as a sandbox.

## Let ( {[} var1 = expression1 {; var2 = expression2...]} ; calculation )

Assigns variables in sequence, then evaluates the final calculation. Plain names are calculation-local; `$` and `$$` assign actual local/global variables. A `$` variable set outside a script is file-scoped until a script runs. Parameters: assignment(s), optionally bracketed for multiple values; final expression. Returns any type.

```filemaker
Let ( side = 9 ; side * side )
// Expected 81
Let ( [ side = 9 ; area = side * side ; volume = area * side ] ; volume )
// Expected 729
```
Multi-variable estimate:
```filemaker
Let ( [
  labour = Repairs::Hours * Repairs::HourlyRate ;
  allowance = If ( Repairs::Hours > 16 ; labour * 0.06 ; 0 ) ;
  levy = ( labour - allowance ) * Repairs::LevyRate
] ;
  labour - allowance + levy
)
```
Last token of a space-separated shelf label (not a general personal-name parser):
```filemaker
Let ( [
  tokens = Substitute ( Trim ( Shelves::PrintedLabel ) ; " " ; ¶ ) ;
  finalToken = GetValue ( tokens ; ValueCount ( tokens ) )
] ;
  Trim ( finalToken )
)
// For North Wing Indigo, expected: Indigo
```

## Lookup ( sourceField {; failExpression } )

Returns a source field's value via a relationship. With no related match, returns optional `failExpression`, or empty. Parameters: related source-field reference, optional fallback. Returns any type.

```filemaker
Lookup ( RelatedTariffs::HandlingMinutes ; 15 )
// Related handling allowance; 15 if no matching tariff record exists.
```

## LookupNext ( sourceField ; lower/higherFlag )

Returns the next lower/higher related value when no exact relationship match exists. Parameters: related source-field reference and keyword `lower` or `higher`. Returns any type.

```filemaker
LookupNext ( WeightBands::PostageAllowance ; higher )
// With an appropriate band relationship, select the next higher weight band when no exact band matches.
```

## Self

No parameters. Returns the content of the object in which the calculation is defined: text, number, date, time or timestamp. Available only in conditional formatting, tooltips, placeholder text, **Hide object when**, Accessibility **Title/Help**, and field-definition calculations including auto-enter and validation. **Not available in scripts.**

```filemaker
Self >= 240
// Conditional-format test on a minutes field: true at or above four hours.
```
Another formatting rule:
```filemaker
Abs ( Self ) > 0.25
// Highlight a numeric deviation outside the permitted tolerance.
```

## SetRecursion ( expression ; maxIterations )

Sets the limit for While and recursive custom functions inside the expression. Default **50,000** iterations; exceeding the limit returns `?`. Non-tail-recursive custom functions may exhaust stack space earlier. Parameters: expression, numeric limit. Returns the expression's type.

```filemaker
SetRecursion (
  While ( [ step = 0 ; trace = "" ] ; step < 9 ;
    [ step = step + 1 ; trace = List ( trace ; "Pass " & step ) ] ; trace
  ) ; 4
)
// Expected ?: nine passes exceed a limit of four.
```
Raise the limit above the default only for bounded, reviewed work:
```filemaker
SetRecursion ( While ( n = 0 ; n < 72000 ; n = n + 1 ; n ) ; 80000 )
// Expected 72000; without the wrapper this exceeds the default limit.
```

## While ( [ initialVariable ] ; condition ; [ logic ] ; result )

Initializes variables, repeats logic while the condition is true, then returns the result. Often replaces recursive custom functions. Default limit is 50,000 iterations, adjustable with SetRecursion. Parameters: initial assignments, condition, assignments per iteration, final result. Returns any type.

Repeated multiplication, here 3 to the fourth power:
```filemaker
Let ( [ base = 3 ; exponent = 4 ] ;
  While ( [ product = base ; count = 1 ] ; count < exponent ;
    [ product = product * base ; count = count + 1 ] ; product
  )
)
// Expected 81; this pattern assumes a positive integer exponent.
```
Build a sequence of cubes:
```filemaker
While ( [ n = 2 ; values = "" ] ; n <= 5 ;
  [ values = List ( values ; n ^ 3 ) ; n = n + 1 ] ; values
)
// Expected 8¶27¶64¶125
```
Find the first matching list item, stopping early:
```filemaker
While ( [ labels = $shelfLabels ; index = 1 ; match = "" ] ;
  index <= ValueCount ( labels ) and IsEmpty ( match ) ;
  [ candidate = GetValue ( labels ; index ) ;
    match = If ( Right ( candidate ; 2 ) = "-Q" ; candidate ; "" ) ;
    index = index + 1 ] ; match
)
```

## Logical common patterns

**Zero/empty-safe division** (empty numeric input also behaves as zero here):
```filemaker
Let ( hours = Vehicles::OperatingHours ;
  If ( hours = 0 ; 0 ; Vehicles::FuelUsed / hours )
)
```
**JSON fallback for a missing/empty value:**
```filemaker
Let ( label = JSONGetElement ( $inspectionJSON ; "inspection.outcome" ) ;
  If ( IsEmpty ( label ) ; "Not assessed" ; label )
)
```
This handles an empty result, not all invalid-JSON errors; validate type/error text for untrusted JSON.

**Multi-step elapsed-time charge:**
```filemaker
Let ( [
  elapsed = Get ( CurrentDate ) - Rentals::CheckoutDate ;
  daily = Lookup ( RelatedPlans::DailyCharge ; 0 ) ;
  baseCharge = elapsed * daily ;
  serviceCharge = baseCharge * 0.075
] ;
  baseCharge + serviceCharge
)
```
**While for a simple comma-separated list:**
```filemaker
While ( [ cells = Substitute ( $rackCSV ; "," ; ¶ ) ; index = 1 ; cleaned = "" ] ;
  index <= ValueCount ( cells ) ;
  [ item = Trim ( GetValue ( cells ; index ) ) ;
    cleaned = List ( cleaned ; item ) ; index = index + 1 ] ; cleaned
)
```
This intentionally simple parser does not handle quoted CSV commas, embedded line breaks or preservation of empty cells; use a proper CSV parser when those matter.

---

# JSON functions

Source: <https://help.claris.com/en/pro-help/content/json-functions-category.html>. All **10** native JSON functions are covered. JSONGetElement/JSONSetElement read and write values; JSONListKeys/JSONListValues support iteration. JSONParse/JSONParsedState (**FM 22**) help avoid repeated parsing of large JSON.

**Paths:** a key such as `"rack"`, index `"[2]"`, dot path `"racks[2].code"`, bracket path `"['sensor.v2'][1]"` for a key containing a dot, `"[:]"` for the last array element, and (in JSONSetElement) `"[+]"` for the position after the last element.

**Key order:** returned object keys are alphabetically sorted; do not depend on insertion order.

| Constant | Value | Meaning |
|---|---|---|
| JSONString | 1 | Quoted string |
| JSONNumber | 2 | Number |
| JSONObject | 3 | Object `{}` |
| JSONArray | 4 | Array `[]` |
| JSONBoolean | 5 | `true` or `false` |
| JSONNull | 6 | `null` |
| JSONRaw | 0 | Insert valid JSON as-is; otherwise insert as a JSON string |

These constants apply to JSONSetElement and JSONMakeArray. JSONGetElementType returns types 1–6, **never JSONRaw**.

## JSONDeleteElement ( json ; keyOrIndexOrPath )

Deletes an object member or array element. Parameters: JSON text and key, zero-based index or path. Returns modified JSON text.

```filemaker
JSONDeleteElement ( "{\"draft\":true,\"rack\":8,\"zone\":\"west\"}" ; "draft" )
// Expected {"rack":8,"zone":"west"}
```
Delete by index:
```filemaker
JSONDeleteElement ( "[7,14,21,28,35]" ; 1 )
// Expected [7,21,28,35]; the second item was removed.
```
Delete a nested key:
```filemaker
JSONDeleteElement ( $shipmentJSON ; "route.temporaryStop" )
```

## JSONFormatElements ( json )

Adds tabs/line breaks and alphabetically sorts object keys. Parameter: JSON text. Returns formatted text, or `?` plus an error message for invalid JSON.

```filemaker
JSONFormatElements ( "{\"station\":{\"online\":true,\"code\":\"W7\"}}" )
```
Expected shape (whitespace shown for readability):
```json
{
  "station": {
    "code": "W7",
    "online": true
  }
}
```
Debug a synthetic local payload (do not show secrets in dialogs/logs):
```filemaker
Show Custom Dialog [ "Fixture details" ; JSONFormatElements ( $fixtureJSON ) ]
```

## JSONGetElement ( json ; keyOrIndexOrPath )

Extracts a value, object or array. Parameters: JSON text and key, zero-based index or path. Missing key returns empty. Returns **number** for JSON numbers and Booleans (true 1, false 0); otherwise text, with strings unquoted and objects/arrays serialized as JSON.

```filemaker
JSONGetElement ( "{\"depth\":18,\"rack\":6,\"zone\":\"north\"}" ; "depth" )
// Expected number 18
```
Nested extraction; assume `$habitatJSON` holds `{"pond":{"name":"Willow","depth":18}}`:
```filemaker
JSONGetElement ( $habitatJSON ; "pond.name" )
// Expected Willow
```
Array inside an object:
```filemaker
JSONGetElement ( $shipmentJSON ; "crates[2].label" )
// Label from the third crate.
```
Subobject extraction:
```filemaker
JSONGetElement ( $habitatJSON ; "pond" )
// Expected JSON text {"depth":18,"name":"Willow"}
```

## JSONGetElementType ( json ; keyOrIndexOrPath )

Validates JSON and returns an element's type. **Originated: 19.5.** Parameters as JSONGetElement. Returns number 1–6 when valid. Invalid JSON or a missing key/index returns **text beginning with `?`**, such as `? Incorrect key, index, or path`, never 0. JSONRaw is never returned.

```filemaker
JSONGetElementType ( "{\"depth\":18}" ; "" ) = JSONObject
// Expected 1
JSONGetElementType ( "{depth:18}" ; "" ) = JSONObject
// Expected 0 (the type call itself returned an error string).
JSONGetElementType ( "{\"depth\":18,\"covered\":true}" ; "covered" )
// Expected 5
JSONGetElementType ( "[9,18,27]" ; "7" )
// Expected ? Incorrect key, index, or path
```
Type/error-aware extraction; text dates still need format validation appropriate to the application:
```filemaker
Let ( [
  kind = JSONGetElementType ( $permitJSON ; "expiresOn" ) ;
  rawDate = JSONGetElement ( $permitJSON ; "expiresOn" )
] ;
  Case ( Left ( kind ; 1 ) = "?" ; "" ; kind = JSONNull ; "" ; GetAsDate ( rawDate ) )
)
```

## JSONListKeys ( json ; keyOrIndexOrPath )

Returns a return-delimited text list of object keys or array indexes at a path. Parameters: JSON text, path (`""` for root). Object keys are alphabetically ordered.

```filemaker
JSONListKeys ( "{\"zone\":\"south\",\"bay\":4,\"depth\":9}" ; "" )
// Expected bay¶depth¶zone
JSONListKeys ( "[\"fern\",\"moss\",\"reed\",\"sedge\"]" ; "" )
// Expected 0¶1¶2¶3
JSONListKeys ( "{\"pond\":{\"name\":\"Willow\",\"depth\":18}}" ; "pond" )
// Expected depth¶name
```
Count top-level members:
```filemaker
ValueCount ( JSONListKeys ( $permitJSON ; "" ) )
```
Iterate keys, using bracket paths so dots inside keys remain literal (this fixture assumes no apostrophes in keys):
```filemaker
While ( [ keys = JSONListKeys ( $rackJSON ; "" ) ; index = 1 ; report = "" ] ;
  index <= ValueCount ( keys ) ;
  [ key = GetValue ( keys ; index ) ;
    value = JSONGetElement ( $rackJSON ; "['" & key & "']" ) ;
    report = List ( report ; key & " => " & value ) ; index = index + 1 ] ; report
)
```

## JSONListValues ( json ; keyOrIndexOrPath )

Returns a return-delimited text list of values from an object or array. Parameters as JSONListKeys. Object order follows sorted keys, not insertion order.

```filemaker
JSONListValues ( "{\"zinc\":16,\"copper\":4,\"iron\":12}" ; "" )
// Expected 4¶12¶16
JSONListValues ( "[\"Cedar\",\"Juniper\",\"Larch\",\"Yew\"]" ; "" )
// Expected Cedar¶Juniper¶Larch¶Yew
```

## JSONMakeArray ( listOfValues ; separator ; type )

Converts separated values to a JSON array of one type. **Originated: 21.0.** Parameters: list text, separator (`""` accepts any line separator), JSON type constant. JSONRaw inserts each valid JSON element as-is. Returns JSON-array text.

```filemaker
JSONMakeArray ( "7|42|7.0|105|0" ; "|" ; JSONNumber )
// Expected [7,42,7,105,0]; numeric formatting is normalized.
```
Return-delimited field:
```filemaker
JSONMakeArray ( Seeds::SowingMonths ; "" ; JSONString )
// With March¶April¶September, expected ["March","April","September"].
```
Comma-separated numbers:
```filemaker
JSONMakeArray ( "8,16,32,64" ; "," ; JSONNumber )
// Expected [8,16,32,64]
```
Field-supplied string values:
```filemaker
JSONMakeArray ( Equipment::InspectionCodes ; "|" ; JSONString )
```
Build the occurrence-array input to GetTableDDL (assume these occurrences exist):
```filemaker
GetTableDDL ( JSONMakeArray ( "Stations|Readings|Calibrations" ; "|" ; JSONString ) ; True )
```

## JSONParse ( json )

Parses once, attaching a binary parsed representation to the value. Store in a variable or pass as a script parameter so subsequent JSON functions can skip reparsing. **Originated: 22.0.** Parameter: JSON text. Returns the original unchanged text if valid, or `?` and the parse error.

```filemaker
JSONParse ( "{\"bay\":4}" )
// Expected unchanged text: {"bay":4}
```
Parse once, read repeatedly; the representation travels with the **value**, not a particular variable name:
```filemaker
Set Variable [ $manifest ; Value: JSONParse ( Shipments::ManifestJSON ) ]
Set Variable [ $crateCount ; Value: ValueCount ( JSONListKeys ( $manifest ; "crates" ) ) ]
Set Variable [ $thirdLabel ; Value: JSONGetElement ( $manifest ; "crates[2].label" ) ]
```
A single direct JSONGetElement call on text performs about as well. **Insert from URL (FM 26.0.1+)** already parses `application/json` responses stored in a variable; do not add JSONParse needlessly.

## JSONParsedState ( json )

Reports whether a value carries a parsed representation and whether it is valid. **Originated: 22.0.** Parameter: JSON value, often a variable. Returns number: `0` not parsed; `-1` parsed but invalid; `1`–`6` parsed/valid with that JSON type.

```filemaker
JSONParsedState ( JSONParse ( "{\"bay\":4}" ) )
// Expected 3 (object)
JSONParsedState ( JSONParse ( "{\"bay\":" ) )
// Expected -1
JSONParsedState ( "{\"bay\":4}" )
// Expected 0 for this unparsed literal
JSONParsedState ( JSONSetElement ( "[]" ; "[+]" ; "W7" ; JSONString ) )
// Expected 4 (array)
```
JSONSetElement output is already parsed; no JSONParse is needed after building it.

## JSONSetElement ( json ; keyOrIndexOrPath ; value ; type )

Adds/replaces elements, creating intermediate objects/arrays. Multiple `[ key ; value ; type ]` groups can be supplied. With empty `json`, starts an object, or an array when the path starts with `[`. Parameters: JSON text, key/path (including append `"[+]"`), value, JSON type constant. For JSONBoolean, true/nonzero is true and false/zero is false. Returns modified JSON text.

Add a member to an object:
```filemaker
JSONSetElement ( "{\"bay\":4}" ; "depth" ; 18.5 ; JSONNumber )
// Expected {"bay":4,"depth":18.5}
```
Set several members together:
```filemaker
JSONSetElement ( "{}" ;
  [ "station" ; "W7" ; JSONString ] ;
  [ "samples" ; 48 ; JSONNumber ] ;
  [ "covered" ; False ; JSONBoolean ]
)
// Expected {"covered":false,"samples":48,"station":"W7"}; sorted keys.
```
Create intermediate objects:
```filemaker
JSONSetElement ( "{}" ; "pond.name" ; "Willow" ; JSONString )
// Expected {"pond":{"name":"Willow"}}
```
Append an array member:
```filemaker
JSONSetElement ( "[8,16]" ; "[+]" ; 32 ; JSONNumber )
// Expected [8,16,32]
```
Insert existing JSON without quoting it:
```filemaker
JSONSetElement ( "{}" ; "limits" ; "[8,16]" ; JSONRaw )
// Expected {"limits":[8,16]}
```
Build a prospective model payload locally, without sending it (provider must support the chosen schema):
```filemaker
Let ( request = JSONSetElement ( "{}" ;
  [ "model" ; "<approved-model-id>" ; JSONString ] ;
  [ "temperature" ; 0.25 ; JSONNumber ] ;
  [ "max_tokens" ; 384 ; JSONNumber ]
) ; request )
```

## JSON common patterns

**Default for a missing/empty string** (not a complete invalid-JSON handler):
```filemaker
Let ( result = JSONGetElement ( $fixtureJSON ; "inspection.stage" ) ;
  If ( IsEmpty ( result ) ; "Awaiting inspection" ; result )
)
```
**Prepare a request body for Insert from URL:**
```filemaker
Set Variable [ $requestBody ; Value: JSONSetElement ( "{}" ;
  [ "term" ; $approvedSearchTerm ; JSONString ] ;
  [ "pageSize" ; 6 ; JSONNumber ] ;
  [ "criteria.available" ; True ; JSONBoolean ]
) ]
# Non-executed outline: replace the endpoint only after approving the destination and data.
Insert from URL [ Select ; No dialog ; Target: $reply ;
  URL: "<approved-https-search-endpoint>" ;
  cURL options: "-X POST -H \"Content-Type: application/json\" --data @$requestBody"
]
```
The placeholder is intentionally not a working URL; the cURL variable-body form avoids embedding the body in command text.

**Collect values from an array:**
```filemaker
While ( [
  crates = JSONGetElement ( $manifest ; "crates" ) ;
  length = ValueCount ( JSONListKeys ( crates ; "" ) ) ;
  index = 0 ; labels = ""
] ; index < length ;
  [ labels = List ( labels ; JSONGetElement ( crates ; "[" & index & "].label" ) ) ;
    index = index + 1 ] ; labels
)
```
**Parse a response defensively**, distinguishing malformed JSON from a missing error member:
```filemaker
Let ( [
  raw = $fixtureReply ;
  rootType = JSONGetElementType ( raw ; "" ) ;
  errorType = JSONGetElementType ( raw ; "fault" )
] ;
  Case (
    Left ( rootType ; 1 ) = "?" ; "Malformed response" ;
    Left ( errorType ; 1 ) ≠ "?" ; "Service fault: " & JSONGetElement ( raw ; "fault.detail" ) ;
    JSONGetElement ( raw ; "payload" )
  )
)
```
**Convert a configured FileMaker value list to an API-ready array** (no network call):
```filemaker
JSONMakeArray ( ValueListItems ( Get ( FileName ) ; "Inspection Stages" ) ; ¶ ; JSONString )
// For Queued¶Measuring¶Released, expected ["Queued","Measuring","Released"].
```

---

# AI functions

Source: <https://help.claris.com/en/pro-help/content/artificial-intelligence-functions.html>. All **14** native AI functions are covered.

**Prerequisites:** functions with an `account` parameter require **Configure AI Account** earlier in the current file. Supported providers vary by release; FM 26 added Google Gemini. Consult the current Configure AI Account page rather than assuming a fixed provider list. Not every AI-category function makes a remote call: vector arithmetic/conversion and local model operations are distinct from provider calls.

**Model loading:** ComputeModel and GetModelAttributes use **Core ML** models loaded by **Configure Machine Learning Model**, on iOS, iPadOS and macOS only. PredictFromModel instead uses **regression (Random Forest)** models trained/loaded with **Configure Regression Model**; it is not a Core ML operation.

**Relevant errors:** 877 means the named AI account cannot be found; 882 is an invalid AI request, such as an unsupported image type or oversized image input. Concrete vectors below are artificial arithmetic fixtures, not real model embeddings. Semantic examples assume compatible same-model vectors.

## AddEmbeddings ( v1 ; v2 )

Adds two vectors and **normalizes** the result. Parameters: same-dimension embeddings as JSON-array text or container data. Both must come from the same model. Returns text/container matching input format. **Originated: 22.0.** Returns `?` for differing dimensions or a zero sum (zero cannot be normalized).

```filemaker
AddEmbeddings ( "[2,0,1]" ; "[0,3,1]" )
// Sum [2,3,2], length Sqrt(17); expected approximately [0.48507125,0.72760688,0.48507125].
// Both inputs are text, so the result is a JSON-array text value.
```
Combine concepts to broaden retrieval:
```filemaker
Set Variable [ $gardenSearch ; Value: AddEmbeddings ( Concepts::GardenVector ; Concepts::AccessibleVector ) ]
# Supply $gardenSearch to Perform Semantic Find, Query by: Vector data,
# to explore records related to accessible gardens. Results are model-dependent.
```
Vector analogy, not a guaranteed semantic identity:
```filemaker
Set Variable [ $capitalOffset ; Value: SubtractEmbeddings ( Concepts::MadridVector ; Concepts::SpainVector ) ]
Set Variable [ $analogy ; Value: AddEmbeddings ( $capitalOffset ; Concepts::ItalyVector ) ]
# Compare the transformed vector to the stored Rome concept.
CosineSimilarity ( $analogy ; Concepts::RomeVector )
// May be high if this model encodes the analogy; no particular score is promised.
```

## ComputeModel ( modelName ; parameterName1 ; value1 )

Evaluates a loaded Core ML model and returns JSON prediction data. General format: `ComputeModel ( modelName ; parameterName1 ; value1 )`. Vision format in upstream help: `ComputeModel ( modelName ; "image" ; value1 { ; "confidenceLowerLimit" ; returnAtLeastOne } )`.

Parameters: previously loaded model name; parameter-name/value pairs defined by the model; optional vision `confidenceLowerLimit` (0.0–1.0) excludes lower-confidence results; vision `returnAtLeastOne` (nonzero/1) requests the best result even when all are below the threshold. Returns text (JSON; classification output may be an array rather than an object). **Originated: 19.0. Supported: iOS, iPadOS, macOS only.**

First load the model with Configure Machine Learning Model. Assume `<loaded-leaf-model>` exposes a vision image input:
```filemaker
ComputeModel ( "<loaded-leaf-model>" ; "image" ; Plants::LeafPhoto )
```
Synthetic classification-output fixture, **not measured model output**:
```json
[
  {"classification":"maple leaf","confidence":0.81},
  {"classification":"plane leaf","confidence":0.12},
  {"classification":"vine leaf","confidence":0.05},
  {"classification":"oak leaf","confidence":0.015},
  {"classification":"other foliage","confidence":0.005}
]
```
A consumer might retain a shortened fixture such as `[{"classification":"maple leaf","confidence":0.81}]`; this is an excerpt, not a separate guaranteed return schema. Vision threshold arguments filter results as described above, but the Claris Format line is ambiguous about exact positions. **Fetch the current ComputeModel page before using those optional arguments**; no guessed positional example is supplied here.

## CosineSimilarity ( v1 ; v2 )

Returns a number from **-1** (opposite direction) through **0** (orthogonal/no relationship) to **1** (same direction/high similarity). Parameters: normalized embeddings from the same model and with the same dimensions, supplied as JSON-array text or container fields. **Originated: 21.0.**

```filemaker
CosineSimilarity ( "[1,0,0]" ; "[0.8,0.6,0]" )
// Expected approximately 0.8 for these unit-vector fixtures.
```
Compare approved user text with a stored exhibit description; this outline would send both texts to the configured provider if run:
```filemaker
Configure AI Account [ Account Name: "<embedding-account>" ;
  Model Provider: <approved-provider> ; API key: <secret-from-approved-store> ]
Show Custom Dialog [ "Describe an exhibit to locate" ; $approvedQuery ]
Set Variable [ $queryVector ; Value: GetEmbedding ( "<embedding-account>" ; "<approved-embedding-model>" ; $approvedQuery ) ]
Set Variable [ $exhibitVector ; Value: GetEmbedding ( "<embedding-account>" ; "<approved-embedding-model>" ; Exhibits::PublicDescription ) ]
Show Custom Dialog [ "Exhibit match score" ; CosineSimilarity ( $queryVector ; $exhibitVector ) ]
```
Scores depend on the selected model and source data; a high score is not proof of factual equivalence.

## GetEmbedding ( account ; model ; input )

Sends text or container input to an embedding model and returns **binary container data**. Parameters: AI-account name text, model-name text, input text/container. Image embedding is supported through FileMaker Server AI Model Server. **Originated: 21.0.** Binary embeddings are more compact than JSON text and improve downstream performance.

Non-executed outline; the target layout/field must exist and the account/model must be authorized:
```filemaker
Configure AI Account [ Account Name: "<embedding-account>" ;
  Model Provider: <approved-provider> ; API key: <secret-from-approved-store> ]
Go to Layout [ "<exhibit-detail-layout>" (Exhibits) ; Animation: None ]
Set Field [ Exhibits::DescriptionVector ;
  GetEmbedding ( "<embedding-account>" ; "<approved-embedding-model>" ; "A wind-powered sculpture beside the harbor" ) ]
```
For image input use an image model from the Claris AI Model Server's current model list. Failure returns `?`; EvaluationError can report **877** for no configured account or **882** for unsupported/oversized images.

## GetEmbeddingAsFile ( text {; fileNameWithExtension } )

Converts JSON-array text to binary embedding container data. Parameters: embedding JSON text and optional container filename, for instance a `.fve` name. Returns container. **Originated: 21.0.**

```filemaker
Set Field [ Exhibits::DescriptionVector ;
  GetEmbeddingAsFile ( Exhibits::VectorJSON ; "exhibit-vector.fve" ) ]
```

## GetEmbeddingAsText ( data )

Converts binary embedding container data to JSON-array text. Parameter: container field/variable holding an embedding. Returns text. **Originated: 21.0.**

```filemaker
GetEmbeddingAsText ( $fixtureVectorContainer )
// If built from [0,0.6,0.8], expect the equivalent numeric array (precision may vary).
```
The Claris page's original example mistakenly calls GetEmbeddingAsFile; the intended conversion here is **GetEmbeddingAsText**.

## GetFieldsOnLayout ( layoutName )

Returns a JSON object describing find-accessible fields on a layout; pass `""` for the current layout. Parameter: layout-name text. Returns text (JSON). **Originated: 22.0.**

Excludes fields outside the layout area; hidden fields with **Apply in Find mode**; fields with Find Mode entry disabled; fields excluded from Quick Find; fields lacking read access; and summary, global and container fields.

Description metadata comes from the field **annotation** (Advanced Options, **FM 26.0.1+**) when present, otherwise from its **comment**. A leading `[LLM]` tag is stripped for compatibility with the older convention.

```filemaker
JSONFormatElements ( GetFieldsOnLayout ( "<exhibit-search-layout>" ) )
```
Synthetic shape, assuming the layout shows these accessible fields:
```json
{
  "layout_name":"<exhibit-search-layout>",
  "fields":{
    "Exhibits::Caption":{"type":"string","description":"Public exhibit caption"},
    "Exhibits::Floor":{"type":"number","description":"Visitor floor number"},
    "Exhibits::Wing":{"type":"string"}
  }
}
```
Current-layout form:
```filemaker
GetFieldsOnLayout ( "" )
// Run on the chosen test search layout; output depends on its find-accessible fields.
```
Compare layout-field inventory and find-accessible inventory:
```filemaker
Let ( [
  visibleInventory = SortValues ( FieldNames ( Get ( FileName ) ; Get ( LayoutName ) ) ; 1 ) ;
  findInventory = SortValues ( JSONListKeys ( GetFieldsOnLayout ( "" ) ; "fields" ) ; 1 )
] ;
  "Layout inventory:¶" & visibleInventory & "¶Eligible for find:¶" & findInventory
)
```
FieldNames may return unqualified local names while the JSON uses qualified keys; normalize names before treating this as an automated set comparison.

## GetModelAttributes ( modelName )

Returns metadata JSON about a currently loaded Core ML model. Parameter: model name loaded using Configure Machine Learning Model. Returns text (JSON). **Originated: 19.3. Supported: iOS, iPadOS, macOS only.**

```filemaker
Configure Machine Learning Model [ Operation: Vision ; Name: "<loaded-leaf-model>" ;
  From: ModelAssets::LeafClassifier ]
Set Variable [ $leafMetadata ; Value: JSONFormatElements ( GetModelAttributes ( "<loaded-leaf-model>" ) ) ]
Show Custom Dialog [ "Leaf classifier metadata" ; $leafMetadata ]
```
Returned metadata includes `APIVers`, `configuration` (`computeUnits`), `modelDescription` (`classLabels`, `inputDescriptions`, `metadata`, `outputDescriptions`) and `modelName`.

Inspect whether the first input description includes `sizeRange`, matching a whole key:
```filemaker
Let ( [
  metadata = GetModelAttributes ( "<loaded-leaf-model>" ) ;
  inputKeys = JSONListKeys ( metadata ; "modelDescription.inputDescriptions[0]" )
] ;
  PatternCount ( ¶ & inputKeys & ¶ ; ¶ & "sizeRange" & ¶ ) > 0
)
```
The actual input structure is model-dependent; inspect metadata before relying on this path.

## GetRAGSpaceInfo ( ragAccountName {; spaceID } )

Returns information for all spaces in a RAG account, or one optional space. Parameters: account-name text configured with **Configure RAG Account** and optional space-ID text. Returns text (JSON). **Originated: 22.0.** An unknown space produces `[RAG Space] error. Reason: RAG space {space_id} not found`; an invalid account returns `?`.

All-spaces call and a synthetic output fixture:
```filemaker
GetRAGSpaceInfo ( "<configured-rag-account>" )
```
```json
{
  "rag_space_list":[
    {"space_id":"trail-guides","model":"<configured-rag-embedding-model>"},
    {"space_id":"plant-catalogue","model":"<configured-rag-embedding-model>"}
  ]
}
```
The `rag_space_list` array contains space IDs and their model names; it may contain more or fewer entries.

Specific-space call:
```filemaker
GetRAGSpaceInfo ( "<configured-rag-account>" ; "<trail-guide-space-id>" )
```
The specific-space JSON includes `rag_space_id`, `model`, `entries` and a `values` array containing PDF filenames and text chunks. Treat returned chunks and document names as potentially sensitive.

Check existence before proceeding:
```filemaker
Set Variable [ $spaceDetails ; Value: GetRAGSpaceInfo ( "<configured-rag-account>" ; "<trail-guide-space-id>" ) ]
If [ $spaceDetails = "?" or PatternCount ( $spaceDetails ; "[RAG Space] error" ) > 0 ]
  Show Custom Dialog [ "Guide collection unavailable" ]
Else
  # Continue only after checking the returned space details and access policy.
End If
```

## GetTableDDL ( tableOccurrenceNames ; ignoreError )

Returns schema as SQL CREATE TABLE/DDL for a JSON **array of table-occurrence names**, often to supply context to an LLM generating SQL. Parameters: occurrence-name array, Boolean `ignoreError`. True skips failing occurrences and returns successes; False returns `?` if any fails and logs to the AI call log. Returns text (DDL SQL). **Originated: 21.0.**

Synthetic DDL fixture showing names, data types, field comments, primary/foreign keys and an embedding column; exact generated DDL depends on schema:
```sql
CREATE TABLE "Exhibits" (
  "Caption" varchar(255),
  "Wing" varchar(255),
  "InstalledOn" datetime,
  "OpensAt" datetime,
  "ClosesAt" datetime,
  "VisitMinutes" varchar(255),
  "PublicDescription" varchar(255),
  "ExhibitID" varchar(255), /* Stable exhibit identifier */
  "CreatorAccount" varchar(255), /* Account recording the exhibit */
  "EditorAccount" varchar(255), /* Most recent editor account */
  "CreatedAt" datetime, /* Initial record timestamp */
  "EditedAt" datetime, /* Latest record timestamp */
  "DescriptionVector" varbinary(4096),
  PRIMARY KEY (ExhibitID)
);
CREATE TABLE "ExhibitTags" (
  "ExhibitID" varchar(255), /* Parent exhibit identifier */
  "TagID" varchar(255), /* Tag record identifier */
  "EditorAccount" varchar(255), /* Most recent tag editor */
  "EditedAt" datetime, /* Latest tag edit */
  PRIMARY KEY (TagID),
  FOREIGN KEY (ExhibitID) REFERENCES Exhibits(ExhibitID)
);
```
Build the JSON input cleanly and fail explicitly on missing schema:
```filemaker
Set Variable [ $exhibitDDL ; Value:
  GetTableDDL ( JSONMakeArray ( "Exhibits|ExhibitTags|Galleries" ; "|" ; JSONString ) ; False ) ]
If [ $exhibitDDL = "?" ]
  Show Custom Dialog [ "Exhibit schema unavailable; inspect the AI call log" ]
End If
```
This obtains schema locally; sending that schema to a model is a separate disclosure decision.

## GetTokenCount ( text )

Returns an **approximate** number of tokens in any text expression/field. Guidance only: model tokenizers and billed counts can differ. Returns number. **Originated: 21.0.**

```filemaker
GetTokenCount ( "A lantern beside the harbor" )
// An estimate is returned; no exact count is asserted without the FileMaker engine.
```
Preflight a provider-specific, explicitly chosen size budget (not a universal model limit):
```filemaker
If [ GetTokenCount ( Exhibits::PublicDescription ) > 768 ]
  Show Custom Dialog [ "Description exceeds this workflow's budget; shorten or chunk it" ]
Else
  Insert Embedding [ Account Name: "<embedding-account>" ; Embedding Model: "<approved-embedding-model>" ;
    Source Field: Exhibits::PublicDescription ; Target Field: Exhibits::DescriptionVector ]
End If
```
The Else branch would send the description if executed; configure and authorize first.

## NormalizeEmbedding ( data { ; dimension } )

Normalizes a vector; optional `dimension` truncates to the first N dimensions **before** normalization. Parameters: JSON-array text/container and optional dimension count. Returns text/container matching input format. **Originated: 22.0.**

Most embedding models already return normalized vectors, so normalizing them again is a no-op. Useful for unnormalized models or Matryoshka/MRL dimension reduction; only truncate embeddings when supported by the model and retrieval design.

```filemaker
NormalizeEmbedding ( "[2,3,6]" )
// Length Sqrt(4+9+36) = 7.
// Expected approximately [0.28571429,0.42857143,0.85714286].
// Dividing each component by 7 gives a unit-length vector; floating precision can vary.
```
Dimension reduction, assuming an appropriate MRL model and at least 128 source dimensions:
```filemaker
NormalizeEmbedding ( Exhibits::DescriptionVector ; 128 )
// Keeps the first 128 dimensions and rescales that shorter vector to unit length.
```

## PredictFromModel ( modelName ; v1 )

Returns a number predicted by a trained **regression** model. Parameters: name of a model loaded via Configure Regression Model; features as JSON-array text or binary embedding container. **Originated: 22.0.** First train/load the model. Features must match the training structure/dimensionality. Returns `?` when the model is not loaded or dimensions mismatch.

Numeric-feature prediction, assuming a trained rental-duration model with features `[distanceKm, stops, loadKg]`:
```filemaker
PredictFromModel ( "<loaded-route-duration-model>" ; "[84,5,320]" )
// A duration estimate in the training target's units; no numeric result is asserted.
```
Embedding-based prediction, here estimating request urgency rather than a review score; non-executed external-service outline:
```filemaker
Show Custom Dialog [ "Enter a synthetic maintenance request" ; $approvedRequest ]
Configure AI Account [ Account Name: "<local-model-server-account>" ; Model Provider: Custom ;
  Endpoint: "<approved-ai-model-server-endpoint>" ; API key: <secret-from-approved-store> ]
Insert Embedding [ Account Name: "<local-model-server-account>" ;
  Embedding Model: "<training-compatible-embedding-model>" ; Input: $approvedRequest ; Target: $requestVector ]
Configure Regression Model [ Action: Load Model ; Model Name: "<urgency-regression-model>" ;
  Load Model From: ModelAssets::UrgencyModel ]
Show Custom Dialog [ "Estimated urgency" ; PredictFromModel ( "<urgency-regression-model>" ; $requestVector ) ]
Configure Regression Model [ Action: Unload Model ; Model Name: "<urgency-regression-model>" ]
```
Use the identical embedding model/feature preprocessing used in training; local inference does not make the earlier embedding request private by itself.

## SubtractEmbeddings ( v1 ; v2 )

Subtracts v2 from v1, then normalizes. Parameters: same-dimension, same-model embeddings as JSON-array text or container data. Returns text/container matching input. **Originated: 22.0.** Different dimensions or a zero difference (identical vectors) returns `?`.

```filemaker
SubtractEmbeddings ( "[5,1,3]" ; "[3,4,1]" )
// Difference [2,-3,2], length Sqrt(17).
// Expected approximately [0.48507125,-0.72760688,0.48507125], as text for these text inputs.
```
Remove an aspect of a search concept:
```filemaker
SubtractEmbeddings ( Concepts::FestivalVector ; Concepts::MusicVector )
// Explore festival content less dominated by music; semantic behavior is model-dependent,
// not a guaranteed removal of every music-related record.
```

## AI common patterns

**Full semantic-search pipeline** — non-executed outline with explicit external configuration; batch replacement writes the target fields:
```filemaker
# Configure before provider-backed calls; vector arithmetic alone needs no account.
Configure AI Account [ Account Name: "<embedding-account>" ;
  Model Provider: <approved-provider> ; API key: <secret-from-approved-store> ]
# Review found set and disclosure permission before this batch operation.
Insert Embedding in Found Set [ Account Name: "<embedding-account>" ; Embedding Model: "<approved-embedding-model>" ;
  Source Field: Exhibits::PublicDescription ; Target Field: Exhibits::DescriptionVector ; Replace target contents ]
# Natural-language query mode embeds the query itself.
Perform Semantic Find [ Query by: Natural language ; Account Name: "<embedding-account>" ;
  Embedding Model: "<approved-embedding-model>" ; Text: $approvedExhibitQuery ; Record set: All records ;
  Target field: Exhibits::DescriptionVector ; Return count: 6 ;
  Cosine similarity condition: greater than ; Cosine similarity value: .55 ]
```
Stored and query embeddings must come from the **same model**. Use **Query by: Vector data** to reuse a stored query vector. The threshold/count above are workflow choices, not universally valid relevance settings.

**Schema context for natural-language SQL:**
```filemaker
Set Variable [ $gallerySchema ; Value: GetTableDDL ( "[\"Exhibits\",\"Galleries\"]" ; True ) ]
# Perform SQL Query by Natural Language normally generates this DDL itself.
# Choose Data Tables: By DDL when supplying an edited schema intentionally.
```
Inspect permissions and schema descriptions before sending DDL externally.

**Controlling model-facing descriptions (FM 26.0.1+):** field **annotations** in Advanced Options are preferred. If any field in a table is annotated, only annotated fields appear in that table's generated DDL. GetFieldsOnLayout uses annotations with field comments as fallback. The old leading `[LLM]` comment prefix is still stripped for compatibility.
