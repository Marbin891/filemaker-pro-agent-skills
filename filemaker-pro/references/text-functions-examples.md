# Text & Text Formatting Functions — Examples

Adapted from [Darrin Southern, CadenceUX](https://github.com/CadenceUX/claris-filemaker-pro-skill/blob/bda594e15f4a6981e93403c4b187d262ca820116/references/text-functions-examples.md), commit `bda594e15f4a6981e93403c4b187d262ca820116`, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). CadenceUX explanatory prose is retained/adapted; all concrete examples are independently authored replacements. No endorsement is implied.

Validation: signatures checked against `function-catalog.json`; selected deterministic results checked with local arithmetic/text models, **not FileMaker execution**. Formatting, field values, installed fonts, locale and serialization results are expected kinds, not exact environment-independent outputs. `¶` represents a return delimiter, including trailing returns in results. Examples using fields require those fields to exist. Provenance and test levels: [replacement ledger](replacement-ledger.json), text/date section.

## Contents
- [Text functions](#text-functions): Char, Code, Exact, Filter, FilterValues, GetAsCSS, GetAsDate, GetAsNumber, GetAsSVG, GetAsText, GetAsTime, GetAsTimestamp, GetAsURLEncoded, GetValue, Left, LeftValues, LeftWords, Length, Lower, Middle, MiddleValues, MiddleWords, PatternCount, Position, Proper, Quote, Replace, Right, RightValues, RightWords, SerialIncrement, SortValues, Substitute, Trim, TrimAll, UniqueValues, Upper, ValueCount, WordCount
- [Text formatting functions](#text-formatting-functions): RGB, TextColor, TextColorRemove, TextFont, TextFontRemove, TextFormatRemove, TextSize, TextSizeRemove, TextStyleAdd, TextStyleRemove

## Text functions

All 39 native text functions with format, parameters and examples.
Reference: https://help.claris.com/en/pro-help/content/text-functions.html

### Char ( number )
Returns the character(s) for the given Unicode code point(s).
```filemaker
Char ( 937 ) // → Ω, an electrical-resistance label
Char ( 8594 ) // → →, a workflow direction marker
```

### Code ( text )
Returns the Unicode code points of **all** characters in `text`. With more than one character, each code point is a five-digit group, the first character in the lowest five digits. `""` returns empty. Useful with `Get ( TriggerKeystroke )` (tab = 9, return = 13, arrows = 28–31).
```filemaker
Code ( "Ω" ) // → 937
Code ( "→" ) // → 8594
Code ( "R7" ) // → 5500082, a two-character rack identifier
```

### Exact ( originalText ; comparisonText )
Returns 1 (true) if both values match exactly (case-sensitive); otherwise 0. Text styles are ignored. Container data must also be stored the same way (embedded or by reference).
```filemaker
Exact ( "Rack-B" ; "Rack-B" ) // → 1, matching asset labels
Exact ( "Rack-B" ; "rack-b" ) // → 0, capitalization differs
```

### Filter ( textToFilter ; filterText )
Returns only the characters from *textToFilter* that appear in *filterText*, in original order.
```filemaker
Filter ( "zone:R/slot:S/level:T" ; "RST" ) // → RST, routing initials
Filter ( "crate 48 / bay 206" ; "0123456789" ) // → 48206, inventory digits
```

### FilterValues ( textToFilter ; filterValues )
Returns only the values from *textToFilter* that appear in *filterValues*, in their original order. **Not** case-sensitive. Every returned value ends with ¶.
```filemaker
FilterValues ( "Intake¶Repair¶Dispatch" ; "Dispatch¶Intake" ) // → Intake¶Dispatch¶
FilterValues ( "Intake¶Repair¶Dispatch" ; "dispatch¶intake" ) // → Intake¶Dispatch¶
```

### GetAsCSS ( text )
Returns text with its FileMaker formatting converted to CSS (Cascading Style Sheets) format.
```filemaker
GetAsCSS ( TextStyleAdd ( "Inspection passed" ; Bold ) )
// Expected kind: CSS-bearing representation preserving the bold inspection caption.
```

### GetAsDate ( text )
Returns text interpreted as a date, typed as Date. Text must be in the date format of the system the **file was created on**. For an Australian-format file, an inspection on 18 August 2032 is entered as `18/8/2032`; for a US-format file, `8/18/2032`. Use `Date ( month ; day ; year )` for locale-proof constants. A number is treated as a day ordinal from the 1/1/0001 epoch (that date is day 1).
```filemaker
GetAsDate ( 738945 ) // → Date corresponding to 2/29/2024 in US display
```

### GetAsNumber ( text )
Strips non-numeric characters and returns a Number; numeric punctuation/signs affect interpretation.
```filemaker
GetAsNumber ( "batch 68" ) // → 68
GetAsNumber ( "USD 8,706.25" ) // → 8706.25 in a dot-decimal context
GetAsNumber ( "(315)" ) // → -315, accounting-style adjustment
```

### GetAsSVG ( text )
Returns text with its FileMaker formatting converted to SVG (Scalable Vector Graphics) format.
```filemaker
GetAsSVG ( TextStyleAdd ( "Gallery entrance" ; Italic ) )
// Expected kind: SVG XML representing the italic signage caption.
```

### GetAsText ( data )
Returns any data type as Text. Dates convert using the file's date format. For a container: the external path information, or `?` if the data is embedded.
```filemaker
GetAsText ( 608 ) // → "608", a shelf number exported as text
GetAsText ( Date ( 8 ; 18 ; 2032 ) )
// Expected kind: date text in the file's format (US month/day/year or Australian day/month/year).
```

### GetAsTime ( text )
Returns text interpreted as a time, typed as Time.
```filemaker
GetAsTime ( "6:12:35" ) // → Time value for the morning departure
GetAsTime ( "18:08" ) // → Time value for 6:08:00 PM; display depends on formatting
```

### GetAsTimestamp ( text )
Returns text as a timestamp. Text must be a date then a time, in the date and time formats of the system the **file was created on**. A number is read as seconds since 1/1/0001.
```filemaker
GetAsTimestamp ( 37230 ) // → 1/1/0001 10:20:30 AM in US display
// Locale-proof scheduled equipment inspection:
Timestamp ( Date ( 8 ; 18 ; 2032 ) ; Time ( 6 ; 12 ; 35 ) )
```

### GetAsURLEncoded ( text )
Returns text encoded for use in a URL (percent-encoding).
```filemaker
GetAsURLEncoded ( "loading dock" ) // → loading%20dock
GetAsURLEncoded ( "bin=R7&zone=East Wing" ) // → bin%3DR7%26zone%3DEast%20Wing
```

### GetValue ( listOfValues ; valueNumber )
Returns the value at position *valueNumber* from a return-delimited list.
```filemaker
GetValue ( "Queued¶Testing¶Archived" ; 2 ) // → Testing
GetValue ( "Queued¶Testing¶Archived" ; 6 ) // → empty, beyond list length
```

### Left ( text ; numberOfCharacters )
Returns the first *numberOfCharacters* characters from the left of text.
```filemaker
Left ( "LAB-842" ; 3 ) // → LAB, department prefix
Left ( "Dispatch ready" ; 8 ) // → Dispatch, workflow label
```

### LeftValues ( text ; numberOfValues )
Returns the first *numberOfValues* values from a return-delimited list.
```filemaker
LeftValues ( "Intake¶Wash¶Dry¶Pack" ; 2 ) // → Intake¶Wash¶
```

### LeftWords ( text ; numberOfWords )
Returns the first *numberOfWords* words from text.
```filemaker
LeftWords ( "Secure cold storage access" ; 3 ) // → Secure cold storage
```

### Length ( text )
Returns the number of characters in text, including spaces and special characters.
```filemaker
Length ( "R7-42" ) // → 5, punctuation counts
Length ( "Bay 12 ready" ) // → 12, spaces count
Length ( Left ( "tag" ; 0 ) ) // → 0, an empty generated label
```

### Lower ( text )
Returns all letters in text as lowercase.
```filemaker
Lower ( "NORTH ANNEX" ) // → north annex
Lower ( "LOT83Z" ) // → lot83z, digits unchanged
```

### Middle ( text ; start ; numberOfCharacters )
Returns *numberOfCharacters* characters starting at *start* (values ≤ 1 start at 1).
```filemaker
Middle ( "BOX-739-Q" ; 5 ; 3 ) // → 739, shipment sequence
Middle ( "Gate opens noon" ; 6 ; 5 ) // → opens, notice action
```

### MiddleValues ( text ; startingValue ; numberOfValues )
Returns *numberOfValues* values from a return-delimited list starting at *startingValue*.
```filemaker
MiddleValues ( "Intake¶Wash¶Dry¶Pack" ; 2 ; 2 ) // → Wash¶Dry¶
```

### MiddleWords ( text ; startingWord ; numberOfWords )
Returns *numberOfWords* words starting at *startingWord*.
```filemaker
MiddleWords ( "Keep fragile items upright" ; 2 ; 2 ) // → fragile items
```

### PatternCount ( text ; searchString )
Returns the number of times *searchString* occurs in *text* (case-insensitive).
```filemaker
PatternCount ( "bay-bay-bay" ; "bay" ) // → 3, repeated location token
PatternCount ( "QA ok; qa hold" ; "qa" ) // → 2, mixed-case audit tags
PatternCount ( "sealed crate" ; "open" ) // → 0, absent condition
```

### Position ( text ; searchString ; start ; occurrence )
Returns the character position of the *occurrence*-th instance of *searchString* in *text*, starting search at *start*. Like PatternCount, searching is case-insensitive.
```filemaker
Position ( "rack/slot/bin" ; "/" ; 1 ; 1 ) // → 5, first path boundary
Position ( "rack/slot/bin" ; "/" ; 1 ; 2 ) // → 10, second boundary
Position ( "QA ok; qa hold" ; "qa" ; 1 ; 2 ) // → 8, second audit tag
```

### Proper ( text )
Returns text with the first letter of each word capitalised, all others lowercase.
```filemaker
Proper ( "west loading dock" ) // → West Loading Dock
Proper ( "MIRA PATEL" ) // → Mira Patel, a visitor badge
```

### Quote ( text )
Returns text enclosed in double quotation marks, with special characters escaped — protects text from being run by `Evaluate`.
```filemaker
Quote ( "Dock 7" ) // → "Dock 7" (including enclosing quotation marks)
Quote ( "mark \"fragile\" on crate" ) // → "mark \"fragile\" on crate" (escaped inner quotes)
Evaluate ( Quote ( "8 * 7" ) ) // → text 8 * 7, not the number 56
```

### Replace ( text ; start ; numberOfCharacters ; replacementText )
Replaces *numberOfCharacters* characters in *text* starting at *start* with *replacementText*. Use `0` characters to insert.
```filemaker
Replace ( "Dock closed" ; 6 ; 6 ; "available" ) // → Dock available
Replace ( "R7:084" ; 3 ; 1 ; "-" ) // → R7-084, one-character delimiter replacement
Replace ( "R7084" ; 3 ; 0 ; "-" ) // → R7-084, insertion without deletion
```

### Right ( text ; numberOfCharacters )
Returns the last *numberOfCharacters* characters from the right of text.
```filemaker
Right ( "CRATE-839" ; 3 ) // → 839, shipment suffix
Right ( "Move to annex" ; 5 ) // → annex, destination
```

### RightValues ( text ; numberOfValues )
Returns the last *numberOfValues* values from a return-delimited list.
```filemaker
RightValues ( "Intake¶Wash¶Dry¶Pack" ; 2 ) // → Dry¶Pack¶
```

### RightWords ( text ; numberOfWords )
Returns the last *numberOfWords* words from text.
```filemaker
RightWords ( "Route parcels through north gate" ; 2 ) // → north gate
```

### SerialIncrement ( text ; incrementBy )
Returns text with the trailing number incremented by *incrementBy*.
```filemaker
SerialIncrement ( "CRATE-047" ; 2 ) // → CRATE-049
SerialIncrement ( "CRATE-099" ; 1 ) // → CRATE-100, carry into next place
SerialIncrement ( "SHELF280" ; 15 ) // → SHELF295, larger increment
```

### SortValues ( values {; datatype ; locale } )
Sorts a list of values. Both extra parameters are optional — with neither, values sort as text, ascending, in the file's locale. *Originated: 16.0*
- *datatype*: 1 text · 2 number · 3 date · 4 time · 5 timestamp. **Negative sorts descending** (`-2` = numbers, high to low).
- *locale*: a name such as `English`, `German`, `Japanese`, `Unicode_Raw`; an unrecognised name returns `?`.

Every returned value ends with ¶.
```filemaker
SortValues ( "Wash¶Dry¶Pack" ) // Expected kind: locale-sorted text list with trailing ¶
SortValues ( "80¶7¶120¶4" ; 2 ) // → 4¶7¶80¶120¶, capacities ascending
SortValues ( "95¶420¶26¶61" ; -2 ) // → 420¶95¶61¶26¶, capacities descending
```

### Substitute ( text ; searchString ; replaceString )
Replaces every occurrence of *searchString* in *text* with *replaceString*. **Case-sensitive** (unlike `PatternCount` and `Position`).
```filemaker
Substitute ( "Gate closed" ; "closed" ; "open" ) // → Gate open
Substitute ( "XX--YY" ; "-" ; "/" ) // → XX//YY, all matching characters
```
Multiple substitutions: each bracket is one `[ search ; replace ]` **pair**, applied in order (a later pair can change an earlier pair's output).
```filemaker
Substitute ( "raw parcel" ; [ "raw" ; "checked" ] ; [ "parcel" ; "shipment" ] )
// → checked shipment
Substitute ( "raw parcel" ; [ "raw" ; "parcel" ] ; [ "checked" ; "shipment" ] )
// → parcel parcel: the first pair means replace raw WITH parcel, not two search terms.
Substitute ( "raw parcel" ; [ "raw" ; "checked" ] ; [ "checked" ; "sealed" ] )
// → sealed parcel: the second pair changes the first pair's output.
```

### Trim ( text )
Removes leading and trailing spaces from text.
```filemaker
Trim ( "  Dock 7  " ) // → Dock 7, preserves internal space
Trim ( "   R7084 " ) // → R7084, scanned identifier
```

### TrimAll ( text ; trimSpaces ; trimType )
Removes or inserts spaces, mainly for mixing **roman** and **non-roman** (CJK) text. For plain leading/trailing spaces use `Trim`.
- *trimSpaces*: `1` also removes **full-width** spaces; `0` keeps them.
- *trimType* (spacing between non-roman and roman characters; non-roman ↔ non-roman spaces are always removed): `0` remove; one space between roman words · `1` always one half-width space between non-roman and roman · `2` reduce multiple spaces to one, add none · `3` remove all spaces.
```filemaker
TrimAll ( "North    loading   bay" ; 1 ; 0 ) // → North loading bay
TrimAll ( "  LOT  83 Z " ; 0 ; 3 ) // → LOT83Z
```

### UniqueValues ( values {; datatype ; locale } )
Returns the list with duplicates removed, in original order — it does **not** sort. *datatype* (1–5, as SortValues) and *locale* only change how uniqueness is judged; `Unicode_Raw` makes it case- and accent-sensitive. *Originated: 16.0*
```filemaker
UniqueValues ( "Wash¶Pack¶Wash¶Dry¶Pack" ) // → Wash¶Pack¶Dry¶
UniqueValues ( "72¶410¶9¶410¶9.0" ; 2 ) // → 72¶410¶9¶, numeric equality merges 9 and 9.0
```

### Upper ( text )
Returns all letters in text as uppercase.
```filemaker
Upper ( "north annex" ) // → NORTH ANNEX
Upper ( "fragile" ) // → FRAGILE
```

### ValueCount ( text )
Returns the count of values in a return-delimited list.
```filemaker
ValueCount ( "Intake¶Wash¶Dry¶Pack" ) // → 4, workflow stages
ValueCount ( Left ( "stage" ; 0 ) ) // → 0, empty generated list
```

### WordCount ( text )
Returns the count of words in text.
```filemaker
WordCount ( "Keep all chilled samples upright" ) // → 5
WordCount ( "Dispatch" ) // → 1
WordCount ( Left ( "notice" ; 0 ) ) // → 0
```

Individual reference pages: https://help.claris.com/en/pro-help/content/{function-slug}.html

## Text formatting functions

All 10 native text formatting functions with format, parameters and examples.
Reference: https://help.claris.com/en/pro-help/content/text-formatting-functions.html

Text formatting functions operate on fields of type text, text constants (in quotations), and expressions with a text result. **Note:** Text formatting is lost if the result is stored in a non-text field type.

### RGB ( red ; green ; blue )
Returns an integer from 0 to 16777215 by combining colour values.
Parameters: `red`, `green`, `blue` — each a numeric expression from 0 to 255.
Returns: number. Formula: `red × 65536 + green × 256 + blue`.
```filemaker
RGB ( 196 ; 0 ; 0 ) // → 12845056, red-channel alarm shade
RGB ( 0 ; 176 ; 0 ) // → 45056, green-channel readiness shade
RGB ( 0 ; 0 ; 208 ) // → 208, blue-channel navigation shade
RGB ( 12 ; 12 ; 12 ) // → 789516, near-black ink
RGB ( 244 ; 244 ; 244 ) // → 16053492, near-white background
RGB ( 28 ; 142 ; 164 ) // → 1871524, mixed teal route colour
// Combine TextColor to give a route code and destination different colours:
TextColor ( "R7" ; RGB ( 28 ; 142 ; 164 ) ) & " — " & TextColor ( "Annex" ; RGB ( 124 ; 68 ; 148 ) )
```

### TextColor ( text ; RGB ( red ; green ; blue ) )
Changes the colour of `text` to the colour specified by the RGB function. Not supported in FileMaker WebDirect.
Returns: text (with colour applied).
```filemaker
TextColor ( "Quarantine" ; RGB ( 196 ; 0 ; 0 ) ) // Expected kind: red-shade alert text
TextColor ( Routes::Destination ; RGB ( 28 ; 142 ; 164 ) ) // Expected kind: teal destination field text
```

### TextColorRemove ( text {; RGB ( red ; green ; blue )} )
Removes font colours from text. Without the optional RGB parameter, removes all colours; with it, removes only the specified colour.
Returns: text.
```filemaker
TextColorRemove ( Inspection::Comments ) // Expected kind: comments with all explicit colours removed
TextColorRemove ( Inspection::Comments ; RGB ( 196 ; 0 ; 0 ) )
// Expected kind: only the specified alarm shade removed; other colours retained
```

### TextFont ( text ; fontName )
Changes the font of `text` to `fontName` (exact spelling). Formatting is lost if the result is stored in a non-text field.
Legacy: older releases documented a third `fontScript` parameter. Upstream reports the engine still accepts it, but current Claris docs omit it — don't add it to new code. This legacy assertion was not engine-tested here.
Returns: text.
```filemaker
TextFont ( "Shelf R7" ; "Menlo" ) // Expected kind: monospaced label, if Menlo is installed
TextFont ( Exhibit::Caption ; "Georgia" ) // Expected kind: caption in Georgia, if installed
```

### TextFontRemove ( text {; fontToRemove } )
Removes all fonts, or only `fontToRemove`, reverting that text to the field's default font. (Legacy `fontScript` third parameter: as TextFont.)
Returns: text.
```filemaker
TextFontRemove ( Exhibit::Caption ) // Expected kind: all font assignments removed
TextFontRemove ( Exhibit::Caption ; "Georgia" ) // Expected kind: only Georgia removed; other fonts retained
```

### TextFormatRemove ( text )
Removes all text formatting (colour, font, size, style) from text in a single action.
Returns: text (plain, unformatted). Useful for normalising styled text before storage or comparison.
```filemaker
TextFormatRemove ( Inspection::Comments ) // Expected kind: plain comment text
TextFormatRemove ( TextStyleAdd ( "Seal intact" ; Bold ) )
// → Seal intact, with the constructed bold formatting removed
```

### TextSize ( text ; fontSize )
Changes the font size of `text` to `fontSize` (in points).
Returns: text.
```filemaker
TextSize ( "Evacuation route" ; 24 ) // Expected kind: signage text at 24pt
TextSize ( Inspection::Footnote ; 9 ) // Expected kind: footnote field text at 9pt
```

### TextSizeRemove ( text {; sizeToRemove } )
Removes all font sizes from text, or only the specified `sizeToRemove`.
Returns: text.
```filemaker
TextSizeRemove ( Exhibit::Caption ) // Expected kind: all size assignments removed
TextSizeRemove ( Exhibit::Caption ; 24 ) // Expected kind: only 24pt assignments removed
```

### TextStyleAdd ( text ; styles )
Adds one or more styles to `text`. Combine multiple styles with the `+` operator.
Returns: text.

Available style names (not case-sensitive, no spaces):
`Plain` `Bold` `Italic` `Underline` `HighlightYellow` `Condense` `Extend` `Strikethrough` `SmallCaps` `Superscript` `Subscript` `Uppercase` `Lowercase` `Titlecase` `WordUnderline` `DoubleUnderline` `AllStyles`

**Notes:**
- `Plain` removes all styles when used alone.
- `Plain` is ignored when combined with other styles.
- Negative values are not valid.

```filemaker
TextStyleAdd ( "Handle with care" ; Italic ) // Expected kind: italic handling instruction
TextStyleAdd ( Exhibit::AccessionCode ; Bold + Underline ) // Expected kind: bold, underlined accession code
TextStyleAdd ( "restricted" ; Uppercase )
// Displays as RESTRICTED; stored text remains restricted. Use Upper to change the data.
// Reset then re-style a visitor note in one expression:
TextStyleAdd ( TextStyleAdd ( Visitor::Note ; Plain ) ; Italic )
// Multiple style blocks for a shipping label:
Let ( [
  routeStyle = Bold + SmallCaps ;
  handlingStyle = Plain
] ;
  TextStyleAdd ( Shipment::Route ; routeStyle ) & "¶¶" &
  TextStyleAdd ( Shipment::Handling ; handlingStyle )
)
```

### TextStyleRemove ( text ; styles )
Removes one or more styles from `text`. Use `AllStyles` to strip all styles (not other formatting such as font or colour).
Returns: text.
```filemaker
TextStyleRemove ( Visitor::Note ; Bold ) // Expected kind: bold removed
TextStyleRemove ( Visitor::Note ; AllStyles ) // Expected kind: all styles removed
TextStyleRemove ( Visitor::Note ; Bold + Italic ) // Expected kind: bold and italic removed; other styles kept
```
