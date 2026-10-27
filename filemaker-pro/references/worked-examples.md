# Small original examples

## Version and verification contract
- Exact authoring target for these examples: FileMaker Pro 19.6.1.
- JSONSetElement originated in 16.0; native transactions originated in 19.6.1.
- The target is an example compatibility baseline, not a claim about an installed build.
- No FileMaker runtime, ADT validation, or hosted solution was available here.
- All expected outcomes below are reasoned expectations, not observed engine output.
- Script notation describes Script Workspace steps; it is not an import file or ADT schema.
- Review privileges, triggers, and client compatibility before using an adapted version.

## 1. A self-contained calculation
Purpose: produce a typed JSON description of a synthetic packing calculation.
This uses constants only, with no schema references or external calls.

```filemaker
Let ( [
    packages = 7 ;
    unitsPerPackage = 6
] ;
    JSONSetElement ( "{}" ;
        [ "unitCount" ; packages * unitsPerPackage ; JSONNumber ] ;
        [ "requiresReview" ; packages > 10 ; JSONBoolean ] ;
        [ "batchKey" ; "DEMO-042" ; JSONString ]
    )
)
```

Expected semantic values: unitCount is 42, requiresReview is false, batchKey is text.
Do not assert a particular JSON key order or whitespace representation.
The literal `DEMO-042` is fictional data, not a key in an existing file.

## 2. Build a small script parameter
The contract accepts a synthetic key with only ASCII letters, digits, or hyphens.
Restricting the alphabet here prevents these examples from accepting find operators.
This restriction is an example policy, not a recommended universal key format.

```filemaker
JSONSetElement ( "{}" ;
    [ "lookupKey" ; "DEMO-042" ; JSONString ]
)
```

Pass the calculation's result as a script parameter after adapting the target script.
For a production contract, validate root shape and JSON value types explicitly.
This example instead uses a canonical round-trip to accept only this narrow envelope.
Extra keys or a numeric lookupKey are rejected, not silently coerced into a broader request.

## 3. A bounded find with immediate error capture
Precondition: Browse mode on an authorized development layout with no pending edits.
The caller owns that context; this fragment intentionally does not navigate or restore it.
The layout must use the placeholder occurrence `DemoDispatch`.
`DemoDispatch::LookupKey` is a placeholder text field; replace both names with verified schema.
It should have unique, nonempty keys under the example alphabet policy.
This script changes the found set but does not edit records or contact external services.

```text
Set Error Capture [ On ]
Set Variable [ $p ; Value: Get ( ScriptParameter ) ]
Set Variable [ $key ; Value: JSONGetElement ( $p ; "lookupKey" ) ]
Set Variable [ $allowed ; Value: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-" ]
Set Variable [ $canonical ; Value: JSONSetElement ( "{}" ; "lookupKey" ; $key ; JSONString ) ]
If [ JSONFormatElements ( $p ) ≠ JSONFormatElements ( $canonical ) or IsEmpty ( $key ) or Length ( $key ) > 64 or Filter ( $key ; $allowed ) ≠ $key ]
    Exit Script [ Text Result: "INVALID_PARAMETER" ]
End If
Enter Find Mode [ Pause: Off ]
Set Variable [ $modeError ; Value: Get ( LastError ) ]
If [ $modeError ≠ 0 ]
    Exit Script [ Text Result: "FIND_MODE_ERROR:" & $modeError ]
End If
Set Field [ DemoDispatch::LookupKey ; "==" & $key ]
Set Variable [ $criterionError ; Value: Get ( LastError ) ]
If [ $criterionError ≠ 0 ]
    Enter Browse Mode [ Pause: Off ]
    Exit Script [ Text Result: "CRITERION_ERROR:" & $criterionError ]
End If
Perform Find [ ]
Set Variable [ $findError ; Value: Get ( LastError ) ]
If [ $findError = 401 ]
    Exit Script [ Text Result: "NO_MATCH" ]
End If
If [ $findError ≠ 0 ]
    Exit Script [ Text Result: "FIND_ERROR:" & $findError ]
End If
If [ Get ( FoundCount ) ≠ 1 ]
    Exit Script [ Text Result: "NON_UNIQUE_MATCH" ]
End If
Exit Script [ Text Result: "ONE_MATCH" ]
```

The `==` prefix requests a whole-field match; the restricted key has no find metacharacters.
After 401, the helper exits without Show All Records or any update action.
The result strings form a deliberately small example contract, not a general error framework.
Unexpected setup failures require caller cleanup; this is not a context-preserving service.
Do not extend this find fragment into a write workflow without transaction and lock design.

## 4. Review tests before any authorized execution
1. Valid envelope with DEMO-042 and one synthetic match: expect ONE_MATCH.
2. Unknown permitted key: expect NO_MATCH and no broadening of the result set.
3. Empty key, wildcard, extra JSON key, or numeric key: expect INVALID_PARAMETER.
4. Duplicate permitted key in a deliberately invalid fixture: expect NON_UNIQUE_MATCH.
5. Denied field access: expect a captured error rather than continuing with stale criteria.
6. Confirm that record contents remain unchanged in every case.

## Official factual references
- https://help.claris.com/en/pro-help/content/jsonsetelement.html
- https://help.claris.com/en/pro-help/content/get-lasterror.html
- https://help.claris.com/en/pro-help/content/open-transaction.html
These links support signatures and behavior; no Claris example block was reused.
