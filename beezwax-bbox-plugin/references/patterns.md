# bBox operational patterns

Original examples for this project. They are written for a FileMaker Script
Workspace and have not been evaluated by a FileMaker engine. Confirm each
signature, mode flag and error reference in `function-catalog.json`.

## Contents

1. Shell command with stderr and error handling
2. Python one-shot versus session
3. JavaScript and the `fm` bridge
4. HTTP with cURL
5. DuckDB
6. Images
7. Web Viewer control
8. Server-side checklist

## 1. Shell command with stderr and error handling

Mode `1+32` skips input line-ending conversion and combines stderr with stdout.
Capture both the result and the error before deciding what happened.

```filemaker
Set Variable [ $script ; Value: "printf '%s' \"$1\"; exit 0" ]
Set Variable [ $output ; Value: bBox_Zsh ( 1+32 ; $script ; "-s" ; "--" ; "payload" ) ]
Set Variable [ $error ; Value: bBox_LastError ( "posix" ) ]
If [ $error <> "0" or IsEmpty ( $output ) ]
    Exit Script [ Text Result: "zsh-failed:" & $error ]
End If
```

Do not interpolate user text into the command string. Pass it as an argument or
through a controlled input file.

## 2. Python one-shot versus session

- `bBox_Python3Run` spawns a separate interpreter and is thread safe, but it
  cannot use the `fm` bridge.
- `bBox_PythonCompile`, `bBox_PythonExecute`, `bBox_PythonEval` and
  `bBox_PythonFinalize` use a session. The Python VM is process-wide and is not
  thread or session safe; add a mutex if calls can overlap.

Use the one-shot form for independent server work. Use a session only when state
must persist across calls, and finalize it.

## 3. JavaScript and the `fm` bridge

`bBox_JavaScript` and `bBox_JavaScriptNode` can expose `fm.evaluate`,
`fm.executesql` and `fm.run`. These calls can change FileMaker state. Obtain
authorization for writes and do not treat JavaScript as a sandbox.

```filemaker
Set Variable [ $count ; Value: bBox_JavaScript ( "fm.evaluate('ValueCount ( List ( 1 ; 2 ; 3 ) )')" ) ]
Set Variable [ $error ; Value: bBox_LastError ( "js" ) ]
```

Prefer native FileMaker calculations for simple expressions; use the bridge when
the script needs a language runtime.

## 4. HTTP with cURL

```filemaker
Set Variable [ $body ; Value: bBox_HTTP_GET ( $url ; $user ; $password ) ]
Set Variable [ $error ; Value: bBox_LastError ( "curl" ) ]
If [ $error <> "0" ]
    Exit Script [ Text Result: "curl-failed:" & $error ]
End If
```

Check whether the call needs headers, a method, a body file or a timeout. Do not
place tokens in the URL or shell history. Keep TLS verification enabled.

## 5. DuckDB

DuckDB sessions are thread and session safe. Open a session, execute the query,
read the result, then close it. Use bind parameters rather than string
concatenation for untrusted values.

```filemaker
Set Variable [ $db ; Value: bBox_DuckDBOpen ( $databasePath ) ]
Set Variable [ $result ; Value: bBox_DuckDBExec ( $db ; $query ) ]
Set Variable [ $queryError ; Value: bBox_LastError ( $db ) ]
Set Variable [ $closed ; Value: bBox_DuckDBClose ( $db ) ]
```

Confirm the exact open/exec/close signatures and result format in the catalog.

## 6. Images

`bBox_GraphicsMagick` and `bBox_Sips` convert images using native paths or a
container reference. Validate the output file and remove temporary container
files when processing large batches.

## 7. Web Viewer control

The `bBox_WebView*` family loads content, runs JavaScript and controls history.
Web Viewer state belongs to a window. Do not assume it is available in
Perform Script on Server. Pass data explicitly rather than relying on a previous
window state.

## 8. Server-side checklist

- [ ] Function is supported on FileMaker Server and the target OS.
- [ ] No AppleScript or UI automation is used in PSoS or schedules.
- [ ] Python sessions are guarded by a mutex or replaced with `bBox_Python3Run`.
- [ ] Result size is below the server ceiling; large data is streamed or batched.
- [ ] Stored calculation fields are not used for shell or Python calls.
- [ ] Temporary files and container references are cleaned up.
- [ ] Errors are checked via the correct `bBox_LastError` reference.
- [ ] Credentials and personal data are absent from commands and logs.
