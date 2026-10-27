# Specialty Functions — Examples (Aggregate, Japanese, Mobile, Miscellaneous)

Adapted from **Darrin Southern / CadenceUX**, [claris-filemaker-pro-skill](https://github.com/CadenceUX/claris-filemaker-pro-skill), commit `bda594e15f4a6981e93403c4b187d262ca820116`, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Changes: retained the CadenceUX synthesis, sections, signatures and factual metadata; replaced all concrete examples and added explicit setup, safety and verification notes. Corrected the sorted-relationship running-total misconception. No FileMaker engine or iOS device was available: **all outputs are expected, not observed in FileMaker**. Hardware, database, layout, IME and container-dependent results are placeholders or conditional fixtures, not claims about existing objects. Every `Demo` schema/object name must be created or mapped before use.

## Contents
- [Aggregate Functions](#filemaker-aggregate-functions--syntax--examples): Average, Count, List, Max, Min, StDev, StDevP, Sum, Variance, VarianceP, Common patterns
- [Japanese Functions](#filemaker-japanese-functions--syntax--examples): DayNameJ, MonthNameJ, YearName, Furigana, Hiragana, Katakana, KanaHankaku, KanaZenkaku, RomanHankaku, RomanZenkaku, KanjiNumeral, NumToJText, Normalisation pattern
- [Mobile Functions](#filemaker-mobile-functions--syntax--examples): GetAVPlayerAttribute, GetSensor, Location, LocationValues, RangeBeacons
- [Miscellaneous Functions](#filemaker-miscellaneous-functions--syntax--examples): ConvertFromFileMakerPath, ConvertToFileMakerPath, GetAddonInfo, GetBaseTableName, GetFieldName, GetLayoutObjectAttribute, GetLayoutObjectOwnerInfo, GetRecordIDsFromFoundSet, LayoutObjectUUID
- [Persistent Data Functions](#filemaker-persistent-data-functions--syntax--examples-fm-26): GetPersistentData, ListPersistentDataIDs

---

# FileMaker Aggregate Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/aggregate-functions.html  
All 10 aggregate functions with syntax, parameters, return types, and usage patterns. These signatures are retained from upstream, not engine-tested here.

**Overview:** Aggregate functions operate across repeating field repetitions OR across related records via a relationship. A related field is aggregated across all related records in the current relationship context; this supports subtotals, counts and lists without scripting.

**Key distinction:** in the hypothetical fixtures below, `DemoReadings` is a related table occurrence with numeric `Minutes` = 2, 6, 10 and a fourth record whose Minutes is empty. `DemoSession::Intervals` is instead a repeating numeric field in the current record with repetitions 2, 6, 10, empty.
```filemaker
Sum ( DemoReadings::Minutes )   // expected 18 across related records
Sum ( DemoSession::Intervals ) // expected 18 across repetitions
```
Self-joins and loops still depend on relationship context; neither expression inherently aggregates the current layout's found set.

## Average ( field {; field...} )
Returns the arithmetic mean of all non-empty values.  
Parameters: one or more field references (related or repeating). Returns: number.
```filemaker
Average ( DemoReadings::Minutes ) // expected 6 for the related fixture
```
Exclude outliers with a filtered relationship: define hypothetical `DemoReadings_InRange` with range predicates selecting readings from 3 through 9:
```filemaker
Average ( DemoReadings_InRange::Minutes ) // expected 6 (only the middle reading)
```
In a summary context, a non-related field uses its repetitions, not other found records:
```filemaker
Average ( DemoSession::Intervals ) // expected 6 across this record's populated repetitions
```

## Count ( field {; field...} )
Returns the number of non-empty values.  
Parameters: one or more fields. Returns: number.
```filemaker
Count ( DemoReadings::Minutes ) // expected 3; ignores the empty fourth reading
```
Count with a condition: create related text `State` = "Accepted", "Retry", "Accepted", "Retry" and numeric calculation `AcceptedMarker` whose definition is:
```filemaker
Case ( State = "Accepted" ; 1 ; "" )
```
Then count populated markers:
```filemaker
Count ( DemoReadings::AcceptedMarker ) // expected 2
```
Unlike Count, Get(FoundCount) reports the current layout's found set. A zero marker would still count; the rejected branch must be empty for this pattern.

## List ( field {; field...} )
Returns the non-blank values as a return-delimited list (no trailing ¶). Accepts related fields, repeating fields, several fields, and variables. Returns: text.
```filemaker
Let ( [ first = "Copper" ; second = "Indigo" ] ; List ( first ; second ) )
// expected Copper¶Indigo
List ( DemoReadings::Minutes ) // expected 2¶6¶10 in the fixture's relationship order
```
⚠️ With **several** related fields, List uses only the **first** related record. Create `DemoCrew` sorted by `Sequence`, with two related rows: role/name = Pilot/Mina, Navigator/Omar:
```filemaker
List ( DemoCrew::Role ; DemoCrew::Name ) // expected Pilot¶Mina, not both crew rows
```
To list a combination per record, define related text calculation `RosterLine`:
```filemaker
Role & ": " & Name
```
Then aggregate that single field:
```filemaker
List ( DemoCrew::RosterLine ) // expected Pilot: Mina¶Navigator: Omar
```
Comma-separated string:
```filemaker
Substitute ( List ( DemoCrew::Name ) ; ¶ ; ", " ) // expected Mina, Omar
```

## Max ( field {; field...} )
Returns the largest value across all non-empty values.  
Parameters: one or more fields. Returns: number, date, time, or timestamp (matches field type).
Fixture: related `DemoInspections::CheckedOn` dates are 2027-03-04 and 2027-03-09:
```filemaker
Max ( DemoInspections::CheckedOn ) // expected date 2027-03-09; display depends on locale
Max ( DemoReadings::Minutes ) // expected 10
```

## Min ( field {; field...} )
Returns the smallest value across all non-empty values.  
Parameters: one or more fields. Returns: number, date, time, or timestamp.
Fixture: related `DemoOffers::LeadDays` = 14, 9, 21; `DemoProbes::Voltage` = 3.1, 2.9, 3.3:
```filemaker
Min ( DemoOffers::LeadDays ) // expected 9, shortest quoted lead time
Min ( DemoProbes::Voltage ) // expected 2.9
```

## StDev ( field {; field...} )
Returns the sample standard deviation (divides by n−1).  
Parameters: one or more fields. Returns: number.
```filemaker
StDev ( DemoReadings::Minutes ) // expected 4
```
Useful in quality-control / statistical-process-control calculations when the related measurements are a sample.

## StDevP ( field {; field...} )
Returns the population standard deviation (divides by n).  
Parameters: one or more fields. Returns: number.
```filemaker
StDevP ( DemoReadings::Minutes ) // expected approximately 3.265986323710904
```
Use this when those related records constitute the entire population, not merely a sample.

## Sum ( field {; field...} )
Returns the total of all non-empty numeric values.  
Parameters: one or more fields. Returns: number.
```filemaker
Sum ( DemoReadings::Minutes ) // expected 18 recorded minutes
```
Conditional sum: define numeric `AcceptedMinutes` on the related reading table:
```filemaker
If ( State = "Accepted" ; Minutes ; 0 )
```
With the states defined above:
```filemaker
Sum ( DemoReadings::AcceptedMinutes ) // expected 12: accepted 2 and 10
```
Running total in a portal: define a **self-join with predicates**, not merely a sorted relationship. On a hypothetical reading row, match its `SessionID` to related `SessionID` and its `Sequence ≥ related Sequence`; name this occurrence `DemoReadings_ThroughRow`:
```filemaker
Sum ( DemoReadings_ThroughRow::Minutes )
// expected 8 at sequence 2 when the session's first readings are 2, 6, 10
```
Sorting alone never selects only the rows above the current portal row. Evaluate in the reading-row context and use a stable sequence/tie policy.

## Variance ( field {; field...} )
Returns the sample variance (square of StDev — divides by n−1).  
Parameters: one or more fields. Returns: number.
```filemaker
Variance ( DemoReadings::Minutes ) // expected 16
```

## VarianceP ( field {; field...} )
Returns the population variance (square of StDevP — divides by n).  
Parameters: one or more fields. Returns: number.
```filemaker
VarianceP ( DemoReadings::Minutes ) // expected approximately 10.66666666666667
```

## Common patterns

**Invoice sub-total, tax, total:** a hypothetical service invoice relates to `DemoCharges`, with `Net` values 40, 75, 25, and `TaxBase` values 40, 0, 25. Evaluate in its parent context at tax rate 0.08:
```filemaker
Let ( [
  net = Sum ( DemoCharges::Net ) ;
  levy = Sum ( DemoCharges::TaxBase ) * 0.08
] ;
  JSONSetElement ( "{}" ;
    [ "subtotal" ; net ; JSONNumber ] ;
    [ "tax" ; levy ; JSONNumber ] ;
    [ "total" ; net + levy ; JSONNumber ]
  )
) // expected subtotal 140, tax 5.2, total 145.2
```
**Count related with status filter:** define `DemoTasks_Pending` to relate parent key and state "Pending"; count its nonblank primary keys:
```filemaker
Count ( DemoTasks_Pending::TaskID ) // expected <number of matching tasks>
```
**Duplicate detection:** define self-join `DemoAssets_SameSerial` matching `Serial = Serial`, including the current record:
```filemaker
Count ( DemoAssets_SameSerial::AssetID ) > 1
// expected 1 if at least one other record shares this nonempty serial
```
**Summary string:** combine a related name list and a related count, retaining relationship order:
```filemaker
Let ( [ labels = Substitute ( List ( DemoCrew::Name ) ; ¶ ; ", " ) ;
        crewCount = Count ( DemoCrew::Name ) ] ;
  crewCount & " aboard: " & labels
) // expected "2 aboard: Mina, Omar"
```
**Most recent related date:**
```filemaker
Max ( DemoInspections::CheckedOn ) // expected date 2027-03-09 in the date fixture
```
**Running total in a portal / list:** the same-session and current-sequence ≥ related-sequence self-join selects "this and earlier"; sort it for display as needed:
```filemaker
Sum ( DemoReadings_ThroughRow::Minutes ) // expected 18 at sequence 3
```
For a report, a running-total summary field is simpler. A relationship's sort order alone does not restrict its record membership.

---

# FileMaker Japanese Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/japanese-functions.html  
All 12 Japanese language functions with syntax, parameters, return types, and usage patterns.

**Overview:** FileMaker's Japanese functions handle text transformations specific to the Japanese writing system. They cover conversion between kana scripts (hiragana ↔ katakana), width normalisation (hankaku ↔ zenkaku), kanji numeral rendering, number-to-Japanese-text conversion, furigana generation, and Japanese calendar / date-name functions. These functions are particularly important for Japanese-locale databases where data may be entered in multiple scripts or character widths.

**Japanese writing system quick reference:**
- **Hiragana** (ひらがな) — cursive phonetic script; typically used for native Japanese words and grammar.
- **Katakana** (カタカナ) — angular phonetic script; typically used for foreign loan words.
- **Kanji** (漢字) — Chinese-origin logographic characters.
- **Hankaku** (半角) — half-width characters (standard ASCII width).
- **Zenkaku** (全角) — full-width characters (double-width, standard in Japanese typography).
- **Furigana** (振り仮名) — phonetic reading annotations (ruby text) for kanji.

## DayNameJ ( date )
Returns the Japanese weekday name. Returns: text.
```filemaker
DayNameJ ( Date ( 3 ; 9 ; 2027 ) ) // expected 火曜日 (Tuesday)
```

## MonthNameJ ( date )
Returns the Japanese month name. Returns: text.
```filemaker
MonthNameJ ( Date ( 11 ; 18 ; 2027 ) ) // expected 11月
```

## YearName ( date ; format )
Returns the Japanese era (emperor) year for a date. `format`: `0` long era name · `1` abbreviated era in parentheses · `2` roman letter (M, T, S, H, R). Any other value means 0. Dates before 8 Sept 1868 return the Western (Seireki) year. The first year of an era shows as 元 with format 1. Returns: text.
```filemaker
YearName ( Date ( 10 ; 8 ; 2027 ) ; 0 ) // expected 令和9
YearName ( Date ( 10 ; 8 ; 2027 ) ; 1 ) // expected (令)9
YearName ( Date ( 10 ; 8 ; 2027 ) ; 2 ) // expected R9
YearName ( Date ( 12 ; 12 ; 1989 ) ; 1 ) // expected (平)元, first Heisei year
```
Eras: Reiwa (令和) from 1 May 2019 · Heisei (平成) 1989–2019 · Shōwa (昭和) 1926–1989.

## Furigana ( text {; option } )
Converts Japanese text (including kanji) to its reading — useful as a sort key, because kanji sort meaningfully only by reading. *Originated: 14.0*  
`option`: `1` hiragana · `2` full-width katakana · `3` full-width romaji · `4` half-width katakana · `5` half-width romaji. Omitted or any other value → hiragana. Returns: text.
An address-import reading fixture using "大阪":
```filemaker
Furigana ( "大阪" )     // expected candidate おおさか
Furigana ( "大阪" ; 2 ) // expected candidate オオサカ
Furigana ( "大阪" ; 4 ) // expected candidate ｵｵｻｶ
Furigana ( "大阪" ; 5 ) // expected candidate oosaka
```
These are linguistic expectations, **not observed IME output**. Verify actual readings/romanisation on the deployment platform and support manual corrections for names.

## Hiragana ( text )
Converts katakana — half-width and full-width — to hiragana. Returns: text.
```filemaker
Hiragana ( "サクラ" ) // expected さくら
Hiragana ( "ｻｸﾗ" )  // expected さくら
```

## Katakana ( text )
Converts hiragana to full-width (zenkaku) katakana. Returns: text.
```filemaker
Katakana ( "つばめ" ) // expected ツバメ
```

## KanaHankaku ( text )
Converts full-width (zenkaku) katakana to half-width (hankaku) katakana. Returns: text.
```filemaker
KanaHankaku ( "ガラス" ) // expected ｶﾞﾗｽ; voiced mark becomes a separate half-width mark
```

## KanaZenkaku ( text )
Converts half-width (hankaku) katakana to full-width (zenkaku) katakana. Returns: text.
```filemaker
KanaZenkaku ( "ﾍﾟﾝ" ) // expected ペン
```

## RomanHankaku ( text )
Converts full-width (zenkaku) letters, digits and symbols to half-width (standard ASCII). Returns: text.
```filemaker
RomanHankaku ( "Ｒａｃｋ－７" ) // expected Rack-7
```

## RomanZenkaku ( text )
Converts half-width letters, digits and symbols to full-width (zenkaku). Returns: text.
```filemaker
RomanZenkaku ( "Bay-42" ) // expected Ｂａｙ－４２
```

## KanjiNumeral ( text )
Converts Arabic digits in text to kanji digits, digit by digit (no place values — for those, use NumToJText). Returns: text.
```filemaker
KanjiNumeral ( "第408号" ) // expected 第四〇八号, not 四百八
```

## NumToJText ( number ; separator ; characterType )
Converts a number to Japanese text. Blank or out-of-range values for either option mean 0.  
`separator`: `0` none · `1` comma every 3 digits · `2` 万 / 億 units · `3` every unit (十, 百, 千, 万, 億).  
`characterType`: `0` half-width digits · `1` full-width digits · `2` kanji · `3` traditional kanji (大字). Returns: text.
Compare grouped ledger amounts and a formal numeral rendering:
```filemaker
NumToJText ( 246813579 ; 1 ; 0 ) // expected 246,813,579
NumToJText ( 246813579 ; 2 ; 0 ) // expected 2億4681万3579
NumToJText ( 246813579 ; 3 ; 2 ) // expected 二億四千六百八十一万三千五百七十九
NumToJText ( 3024 ; 3 ; 3 ) // expected candidate 参阡弐拾四
```
Traditional glyph conventions require confirmation in FileMaker; this is an unobserved candidate, not a certified legal cheque format.

## Normalisation pattern (common data-entry workflow)

Japanese users may enter the same data in multiple character forms. A normalisation calculation ensures consistent storage. This mixed-script product label fixture canonicalises kana width, then Roman width, then hiragana to katakana:
```filemaker
Let ( rawLabel = "ﾍﾟﾝ Ｂ７ あお" ;
  Katakana ( RomanHankaku ( KanaZenkaku ( rawLabel ) ) )
) // expected "ペン B7 アオ"
```
This does not infer readings for kanji or decide whether visually similar labels represent the same product.

---

# FileMaker Mobile Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/mobile-functions.html  
All 5 mobile functions with syntax, parameters, return types, and usage patterns.

**Overview:** these functions read device hardware in **FileMaker Go** (iOS / iPadOS): location, sensors, AV player state and iBeacons. Elsewhere they return empty, so branch on the client first. Permissions and hardware availability remain necessary even on Go.

**Platform guard pattern:** check the application-version prefix; iPhone identifies as "Go …", iPad as "Go_iPad …":
```filemaker
Case ( Left ( Get ( ApplicationVersion ) ; 2 ) ≠ "Go" ;
  "Sensor capture requires FileMaker Go" ;
  GetSensor ( "available" )
) // expected <supported-sensor list on Go>, otherwise the explanatory message
```

## GetAVPlayerAttribute ( attributeName )
FileMaker Go only. Returns a setting of the audio, video or image currently (or most recently) played. Before anything has played: empty or 0. *Originated: 14.0*  
Main attributes:
- `playbackState` — 0 stopped · 1 playing · 2 paused.
- `position`, `startOffset`, `endOffset`, `duration` — seconds.
- `sourceType` (0 none · 1 URL · 2 field · 3 layout object · 4 active object) and `source`.
- `presentation` — 0 embedded · 1 full screen · 2 full screen only · 3 audio only · 4 embedded only.
- `volume`, `zoom`, `hideControls`, `disableInteraction`, `pictureInPicture`, `externalPlayback` …
- `triggerEvent`, `triggerEventDetail` — why OnObjectAVPlayerChange / OnFileAVPlayerChange fired.
- `all` — every attribute.

Returns: text or number. Script fixture: after a test clip has been paused, resume it only if the operator explicitly chose Resume:
```filemaker
If [ GetAVPlayerAttribute ( "playbackState" ) = 2 ]
  AVPlayer Set Playback State [ Playing ]
End If
```
Expected: paused playback resumes; other states are unchanged. Observed: not run, no AV player/device available.

## GetSensor ( sensorName {; option1 ; option2 } )
FileMaker Go only (iOS / iPadOS). Returns a sensor reading; availability depends on the device. *Originated: 17.0*  
Sensor names (case as shown):
- Battery: `batteryLevel` (0.0–1.0), `batteryStatus` (1 unplugged · 2 charging · 3 full).
- Location: `location`, `locationValues` — option1 accuracy (m), option2 timeout (s).
- Motion: `attitude` (roll, pitch, yaw), `rotationRate`, `accelerationByUser`, `accelerationByGravity`, `speed`, `heading`.
- Magnetic: `magneticField`, `compassMagneticHeading`, `compassTrueHeading`.
- Pedometer: `stepCount`, `stepDistance`, `stepFloorsUp`, `stepFloorsDown` — option1 seconds to look back.
- `airPressure`.
- `available` — lists the sensors this device supports.

Multi-value readings come back as return-delimited lists. Returns: text or number.
```filemaker
GetSensor ( "stepCount" ; 900 ) // expected <steps measured over the previous 15 minutes>
Let ( supported = GetSensor ( "available" ) ; supported )
// expected <return-delimited supported sensor names for this device>
```
Do not substitute a fabricated step count for an actual reading.

## Location ( accuracy {; timeout } )
FileMaker Go only — FileMaker Pro returns empty. Returns one line: `latitude, longitude, accuracy` (accuracy in metres achieved). `accuracy` is the requested accuracy in metres; `timeout` is in seconds, **default 60**. Returns empty if no location is received. Returns: text.
```filemaker
Location ( 25 ; 12 ) // expected <latitude, longitude, achieved accuracy> or empty
```
Store coordinates by splitting commas. Hypothetical numeric targets `DemoVisit::Latitude` and `Longitude` must exist; test location permission and authorised write intent first:
```filemaker
Set Variable [ $fix ; Value: Location ( 15 ; 18 ) ]
If [ not IsEmpty ( $fix ) ]
  Set Variable [ $parts ; Value: Substitute ( $fix ; "," ; ¶ ) ]
  Set Field [ DemoVisit::Latitude ; GetAsNumber ( Trim ( GetValue ( $parts ; 1 ) ) ) ]
  Set Field [ DemoVisit::Longitude ; GetAsNumber ( Trim ( GetValue ( $parts ; 2 ) ) ) ]
End If
```
Expected: received coordinates are stored, or no fields are overwritten on an empty fix. For separate values plus altitude, use LocationValues.

## LocationValues ( accuracy {; timeout } )
FileMaker Go only. Returns **six** return-delimited values: latitude · longitude · altitude (m) · horizontal accuracy (m) · vertical accuracy (m) · age of the reading (minutes). Timeout default 60 s. Returns: text.
```filemaker
LocationValues ( 30 ; 15 )
// expected <latitude>¶<longitude>¶<altitude>¶<horizontal accuracy>¶<vertical accuracy>¶<age>
// or empty when no reading is available
```
Reject missing or imprecise fixes before assembling JSON; a blank fix must not silently become numeric zero coordinates:
```filemaker
Let ( fix = LocationValues ( 12 ; 10 ) ;
  Case (
    IsEmpty ( fix ) ; "No position acquired" ;
    GetAsNumber ( GetValue ( fix ; 4 ) ) > 35 ; "Horizontal error exceeds 35 m" ;
    JSONSetElement ( "{}" ;
      [ "latitude" ; GetAsNumber ( GetValue ( fix ; 1 ) ) ; JSONNumber ] ;
      [ "longitude" ; GetAsNumber ( GetValue ( fix ; 2 ) ) ; JSONNumber ] ;
      [ "altitudeMetres" ; GetAsNumber ( GetValue ( fix ; 3 ) ) ; JSONNumber ]
    )
  )
)
```
Expected: a diagnostic message or JSON populated from the device's actual fix; no coordinates were observed here.

## RangeBeacons ( UUID {; timeout ; major ; minor } )
FileMaker Go only. Returns one line per nearby iBeacon matching `UUID` (and optional major / minor), as **comma-separated** values: UUID, major, minor, proximity, accuracy (m; negative = unknown), RSSI (dB). `timeout` defaults to **5 seconds**. *Originated: 15.0*  
`proximity`: `0` unknown · `1` immediate · `2` near · `3` far. Empty if nothing matches or Location Services is off; `?` for an invalid query. Returns: text.
```filemaker
RangeBeacons ( $configuredBeaconUUID ; 3 ; 12 ; 4 )
// expected <UUID, 12, 4, proximity, accuracy, RSSI> per matching beacon, or empty
```
Setup: bind `$configuredBeaconUUID` to a real configured transmitter UUID; it is intentionally not an invented beacon identity. Invalid or unbound input may yield `?`, not a nearby-beacon fixture.

---

# FileMaker Miscellaneous Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/miscellaneous-functions.html  
All 9 miscellaneous functions with syntax, parameters, return types, and usage patterns.

**Overview:** The Miscellaneous category contains utility functions that do not fit neatly into other categories. They cover path conversion (FileMaker ↔ native OS formats), add-on metadata, field name introspection, layout object attribute inspection, found-set record ID retrieval, and layout object UUID access. Several are essential for dynamic scripting and add-on development.

## ConvertFromFileMakerPath ( filemakerPath ; format )
Converts a FileMaker path (`file:`, `filemac:`, `filewin:`, `image:`, `movie:`, `fmnet:` …) to a standard path. *Originated: 19.0*  
`format` (named constant or number): `PosixPath` (1) — slash-separated native path · `WinPath` (2) — drive-letter native path · `URLPath` (3) — file URL, or fmp URL for a network FileMaker path. Returns `?` if the path can't be converted to that format. Returns: text.
Use the current platform's actual DocumentsPath instead of assuming a boot-volume name:
```filemaker
Let ( fm = Get ( DocumentsPath ) & "inspection notes.txt" ;
  ConvertFromFileMakerPath ( fm ; PosixPath )
) // expected <native POSIX documents path>/inspection notes.txt on macOS
Let ( fm = Get ( DocumentsPath ) & "inspection notes.txt" ;
  ConvertFromFileMakerPath ( fm ; URLPath )
) // expected <file URL with space encoding appropriate to this path>
```
Pass a native path to a plug-in or shell command (conversion does not itself execute anything):
```filemaker
ConvertFromFileMakerPath ( Get ( TemporaryPath ) & "sensor-readings.json" ; PosixPath )
// expected <native temporary-directory path>/sensor-readings.json on macOS
```

## ConvertToFileMakerPath ( standardPath ; format )
The reverse: converts a standard path in `format` (`PosixPath` 1, `WinPath` 2, `URLPath` 3) to a FileMaker path. fmp URLs become network FileMaker paths; everything else gets the `file` prefix. *Originated: 19.0* Returns: text.
```filemaker
ConvertToFileMakerPath ( "/Users/Shared/Survey/ring-plan.pdf" ; PosixPath )
// expected file:/<actual macOS boot-volume name>/Users/Shared/Survey/ring-plan.pdf
ConvertToFileMakerPath ( "D:\\Survey\\Exports\\ring-plan.pdf" ; WinPath )
// expected file:/D:/Survey/Exports/ring-plan.pdf
```
The macOS volume component is environment-dependent. These synthetic paths need not exist; conversion does not create or validate the file. Backslashes are escaped in the FileMaker string literal.

## GetAddonInfo ( addonID )
Returns JSON describing an installed or packaged add-on, looked up by its UUID. Keys: `APIVers`, `Installed` (`Name`, `UUID`, `UsesLayoutPayload`, `UsesRelationship`) and `Package` (`Name`, `UUID`). *Originated: 19.2.2* Returns: text (JSON).
```filemaker
Let ( addon = $installedAddonUUID ; GetAddonInfo ( addon ) )
// expected <metadata JSON for the real add-on UUID supplied by the caller>
```
Bind the variable from actual installation metadata; no installed add-on is asserted. Pair with GetLayoutObjectOwnerInfo to discover an object's owning add-on.

## GetBaseTableName ( field )
Returns the name of the **base table** (not the table occurrence) that contains the specified field. Useful when multiple table occurrences point to the same base table.
Parameters: `field` — a field reference (not a field name string — use the field itself as the parameter). Returns: text.
Custom-function fixture: declare a field-reference parameter `targetRef`:
```filemaker
Let ( base = GetBaseTableName ( targetRef ) ; "Base: " & base )
// expected Base: <base-table name of the supplied reference>
```
Resolve a caller-supplied, trusted fully qualified field name; `$qualifiedField` must refer to a real accessible field, not arbitrary untrusted code:
```filemaker
Let ( referenceText = $qualifiedField ; GetBaseTableName ( Evaluate ( referenceText ) ) )
// expected <base table of the named field>
```
Active-field introspection, guarded against the absence of field focus:
```filemaker
Let ( active = Get ( ActiveFieldName ) ;
  If ( IsEmpty ( active ) ; "No field focus" ; GetBaseTableName ( Evaluate ( active ) ) )
) // expected <focused field's base table>, or the diagnostic
```
Validation: hypothetical occurrence `DemoAssets_BySerial` points to base table `DemoAssets` and has field `AssetID`:
```filemaker
Case ( GetBaseTableName ( DemoAssets_BySerial::AssetID ) = "DemoAssets" ;
  "Relationship target OK" ; "Unexpected relationship target"
) // expected Relationship target OK when the fixture is configured as specified
```

## GetFieldName ( field )
Returns the **fully qualified field name** (TableOccurrence::FieldName) of a field reference as a text string. Unlike a literal field-name string, a reference remains tied to a renamed field or occurrence when the calculation is re-evaluated. Critical for dynamic scripting.
Parameters: `field` — a field reference. Returns: text.
Custom-function fixture with field-reference parameter `targetRef`:
```filemaker
Let ( qualified = GetFieldName ( targetRef ) ; "Field: " & qualified )
// expected Field: <qualified name of supplied field>
```
Trusted caller-supplied field-name resolution:
```filemaker
Let ( referenceText = $qualifiedField ; GetFieldName ( Evaluate ( referenceText ) ) )
// expected <qualified name resolved from the supplied trusted field name>
```
Focused field, if any:
```filemaker
Let ( active = Get ( ActiveFieldName ) ;
  If ( IsEmpty ( active ) ; "No field focus" ; GetFieldName ( Evaluate ( active ) ) )
)
```
Dynamic sort/find: hypothetical field `DemoInspections::CheckedOn` supplies a script parameter instead of embedding a potentially stale literal name:
```filemaker
JSONSetElement ( "{}" ;
  [ "sortBy" ; GetFieldName ( DemoInspections::CheckedOn ) ; JSONString ]
) // expected {"sortBy":"DemoInspections::CheckedOn"} before any schema rename
```
The consuming script still needs to implement the dynamic operation; this expression does not sort by itself.
Self-referential validation, in a field calculation context supporting Self:
```filemaker
"Validation source: " & GetFieldName ( Self )
// expected <label followed by the validating field's qualified name>
```

## GetLayoutObjectAttribute ( objectName ; attributeName {; repetitionNumber ; portalRowNumber } )
Returns an attribute of a **named** object on the current layout. *Originated: 8.5*  
Attributes:
- State: `objectType`, `hasFocus`, `containsFocus`, `isFrontPanel`, `isActive`, `isObjectHidden` (1 when hidden for the current record).
- Geometry: `bounds` (space-separated: left top right bottom rotation), `left`, `right`, `top`, `bottom`, `width`, `height`, `rotation`, `startPoint`, `endPoint`.
- Content: `source` (web viewer URL, field name, container reference…), `content` (displayed content), `enclosingObject`, `containedObjects`.

Returns: text. Setup: create a named web viewer `DemoRouteMap` and a named panel/object `DemoLegend` on the current layout. The script captures a source without writing database fields:
```filemaker
Set Variable [ $routeURL ; Value: GetLayoutObjectAttribute ( "DemoRouteMap" ; "source" ) ]
// expected <configured web viewer source>
Case ( GetLayoutObjectAttribute ( "DemoLegend" ; "isObjectHidden" ) = 1 ;
  "Legend unavailable for this record" ; "Legend visible"
) // expected <message reflecting the actual hide condition>
```

## GetLayoutObjectOwnerInfo ( objectID )
Returns JSON about who owns a layout object — its layout and, if any, add-on instance. `objectID` is the object's **UUID** (see LayoutObjectUUID) or an add-on instance's owner ID, as text. *Originated: 19.2.2*  
Returns: text (JSON — `APIVers`, `Object.UUID`, `Object.Index`, `Object.Name`, `Object.Owners.Add-on.InstanceID`, `Object.Owners.Layout.UUID` / `.Name`).
```filemaker
Let ( object = $capturedViewerUUID ; GetLayoutObjectOwnerInfo ( object ) )
// expected <owner JSON for a real UUID previously captured in a web viewer>
```
Setup: bind the variable from the actual viewer's LayoutObjectUUID, not an invented UUID or object name.

## GetRecordIDsFromFoundSet ( type { ; tableOccurrenceOrPortal } )
Returns record IDs of the current found set in its current order. Optional second parameter (FM 26) returns records related through a table occurrence (relationship sort order), or shown in a named portal (including its filter and sort). *Originated: 22.0* Returns: text.

Illustrative **hypothetical** found-set IDs, in order: 8, 9, 10, 24, 3. Actual record IDs are FileMaker internal IDs, not user primary keys; obtain them from a real file rather than assuming these IDs exist.

| type | Constant | Expected representation for the illustrative order |
|---|---|---|
| 0 | `ValueNumber` | `8¶9¶10¶24¶3` |
| 1 | `JSONString` | `["8","9","10","24","3"]` |
| 2 | `JSONNumber` | `[8,9,10,24,3]` |
| 3 | `ValueNumberRanges` | `8-10¶24¶3` |
| 4 | `JSONStringRanges` | `["8-10","24","3"]` |

An empty found set returns empty text (types 0 and 3) or `[]` (JSON types). Pass the result to **Go to List of Records** to restore the found set later.
Membership check: bind `$candidateRecordID` to a real internal ID. Use exact list-value matching, not a substring that could confuse 8 and 18:
```filemaker
not IsEmpty ( FilterValues ( GetRecordIDsFromFoundSet ( ValueNumber ) ; $candidateRecordID ) )
// expected 1 iff that internal ID occurs in the current found set
```
Pass the found set and layout to a script under a nested request object:
```filemaker
JSONSetElement ( "{}" ;
  [ "selection.ids" ; GetRecordIDsFromFoundSet ( JSONNumber ) ; JSONArray ] ;
  [ "selection.layoutName" ; Get ( LayoutName ) ; JSONString ]
) // expected <request JSON using the actual found set and current layout>
```

## LayoutObjectUUID
Returns the UUID of the layout object whose calculation is being evaluated. Works **only** in a web viewer's **Web Address** calculation — anywhere else, including scripts, it returns `?`. *Originated: 19.2.2* Returns: text.
Within the Web Address calculation, use a caller-configured global variable `$$expectedViewerUUID` containing a real UUID for an identity test:
```filemaker
Case ( LayoutObjectUUID = $$expectedViewerUUID ; "Matched viewer" ; "Different viewer" )
// expected Matched viewer only for the viewer whose real UUID was configured
```
This fragment teaches identity comparison; a production Web Address must ultimately return a valid URL. Pass the viewer's own UUID to JavaScript in a self-contained Web Address:
```filemaker
"data:text/html," & GetAsURLEncoded (
  "<html><body><script>window.viewerContext={objectId:"
  & Quote ( LayoutObjectUUID ) & "};</script></body></html>"
)
// expected <data URL whose script receives this actual web viewer UUID>
```

---

# FileMaker Persistent Data Functions — Syntax & Examples (FM 26+)

Source: https://help.claris.com/en/pro-help/content/persistent-data-functions.html  
2 persistent data functions, introduced in FileMaker Pro 26.

**Overview:** the persistent data store is a set of named values saved in the file's **schema**, not its record data. Entries persist across sessions until deleted and are shared by every user of the file. Each entry is a **name** plus an optional **instance ID** (a namespace, such as an add-on instance), holding any FileMaker data type.
- Write or delete with **Configure Persistent Data** — requires **Full Access** (or a script granted it). Reading does not.
- Names and instance IDs are not case-sensitive.
- Entries travel with a clone, but the **Data Migration Tool does not copy them** because they are schema, not record data. Re-create them after migration.

## GetPersistentData ( name ; instanceID )
Returns the stored value in its original data type. **No matching entry returns `?`** (error 10), not empty. An empty instanceID matches an entry stored without one. *Originated: 26.0*  
Returns: text, number, date, time, timestamp or container.
Fixture to configure with explicit authorisation: name `demo.viewer.theme`, no instance ID, text value `night`:
```filemaker
GetPersistentData ( "demo.viewer.theme" ; "" ) // expected night only after fixture setup
```
Fall back to a default when a caller's namespace has no entry:
```filemaker
Let ( stored = GetPersistentData ( "demo.viewer.preferences" ; $actualInstanceID ) ;
  Case ( stored = "?" ; "{\"contrast\":\"standard\"}" ; stored )
) // expected stored preferences, or the default JSON text on a missing entry
```
Bind `$actualInstanceID` from actual configuration. A legitimate stored text value `?` is indistinguishable in this simple sentinel-based pattern; choose a store contract appropriate to your application. Container values are not fabricated or tested here.

## ListPersistentDataIDs ( name )
Returns instance IDs stored under `name`, in creation order. An entry with an empty instance ID appears as a blank line. Empty if none exist. *Originated: 26.0* Returns: text (return-delimited).
```filemaker
ListPersistentDataIDs ( "demo.viewer.preferences" )
// expected <first actual instance ID>¶<second actual instance ID>¶¶<later actual instance ID>
// only if setup created entries in that order, including one unnamespaced entry
```
Read every instance (script), preserving empty namespace lines. This variant counts delimiters explicitly so a trailing empty namespace isn't lost. An empty list can mean no entries or an empty namespace only; probe that namespace separately:
```filemaker
Set Variable [ $name ; Value: "demo.viewer.preferences" ]
Set Variable [ $ids ; Value: ListPersistentDataIDs ( $name ) ]
Set Variable [ $single ; Value: GetPersistentData ( $name ; "" ) ]
Set Variable [ $count ; Value: If ( IsEmpty ( $ids ) ; If ( $single = "?" ; 0 ; 1 ) ; PatternCount ( $ids ; ¶ ) + 1 ) ]
Set Variable [ $position ; Value: 1 ]
Loop [ Flush: Always ]
  Exit Loop If [ $position > $count ]
  Set Variable [ $namespace ; Value: GetValue ( $ids ; $position ) ]
  Set Variable [ $entry ; Value: GetPersistentData ( $name ; $namespace ) ]
  # Process $entry here using the application's authorised read-only consumer.
  Set Variable [ $position ; Value: $position + 1 ]
End Loop
```
Expected: each actual namespace's stored value is read in creation order, including an empty namespace where present. This simple probe assumes `?` is not a legitimate stored value. Test empty/trailing-line cases in FileMaker before deployment. Use the real IDs returned, not guessed namespace identifiers; a nonexistent identifier returns `?`.
