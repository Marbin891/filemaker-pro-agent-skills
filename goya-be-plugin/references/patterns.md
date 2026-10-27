# BaseElements operational patterns

Original examples for this project. They are written to be readable in a
FileMaker Script Workspace; they are not vendor examples and have not been
executed in a FileMaker engine. Check the exact signatures in
`function-catalog.json` before adapting them.

## Contents

1. HTTP request with explicit failure handling
2. Files and folders
3. SMTP
4. XML and XSLT
5. Arrays and value lists
6. Regular expressions
7. JavaScript
8. PDF and containers
9. Hashing and encryption
10. Operational checklist

## 1. HTTP request with explicit failure handling

Use a sub-script so that each request has one exit path and one response shape.
Store secrets outside the calculation text.

```filemaker
# Parameters: $url, $body
Set Variable [ $curlError ; Value: 0 ]
Set Variable [ $httpStatus ; Value: 0 ]

Set Variable [ $setup ; Value: BE_HTTP_SetCustomHeader ( "Content-Type" ; "application/json" ) ]
Set Variable [ $setup ; Value: BE_CurlSetOption ( "CURLOPT_TIMEOUT" ; 30 ) ]
Set Variable [ $response ; Value: BE_HTTP_POST ( $url ; $body ) ]
Set Variable [ $curlError ; Value: BE_GetLastError ]
Set Variable [ $httpStatus ; Value: BE_HTTP_ResponseCode ]

Set Variable [ $reset ; Value: BE_CurlSetOption ]
Set Variable [ $resetHeaders ; Value: BE_HTTP_SetCustomHeader ]

If [ $curlError <> 0 ]
    Exit Script [ Text Result: JSONSetElement ( "{}" ; [ "kind" ; "curl" ; JSONString ] ; [ "code" ; $curlError ; JSONNumber ] ) ]
Else If [ $httpStatus < 200 or $httpStatus >= 300 ]
    Exit Script [ Text Result: JSONSetElement ( "{}" ; [ "kind" ; "http" ; JSONString ] ; [ "status" ; $httpStatus ; JSONNumber ] ) ]
End If

Exit Script [ Text Result: JSONSetElement ( "{}" ; [ "kind" ; "ok" ; JSONString ] ; [ "body" ; $response ; JSONString ] ) ]
```

Do not log authorization headers, cookies or full response bodies when they may
contain personal data.

## 2. Files and folders

Convert FileMaker paths to native paths once, at the boundary. This example is
for macOS/POSIX with FileMaker 19+; use `WinPath` on Windows:

```filemaker
Set Variable [ $folder ; Value: ConvertFromFileMakerPath ( "file:" & Get ( DocumentsPath ) ; PosixPath ) ]
Set Variable [ $path ; Value: $folder & "export-" & Get ( UUID ) & ".csv" ]
Set Variable [ $written ; Value: BE_FileWriteText ( $path ; $csv ) ]
Set Variable [ $fileError ; Value: BE_GetLastError ]
If [ $fileError <> 0 ]
    Exit Script [ Text Result: "write-failed" ]
End If
```

Check that the destination is inside an approved directory before writing. File
functions can overwrite data; obtain authorization and keep a backup or a
reversible test copy.

## 3. SMTP

Configure the server once per session, then set headers, attach files and send.
Check the plug-in error immediately after sending.

```filemaker
Set Variable [ $configured ; Value: BE_SMTPServer ( $host ; $port ; $user ; $password ) ]
Set Variable [ $sent ; Value: BE_SMTPSend ( $from ; $to ; $subject ; $body ) ]
Set Variable [ $smtpError ; Value: BE_GetLastError ]
```

Use an application-specific credential, not a personal mailbox password. Do not
send mail from a test script without an approved recipient list.

## 4. XML and XSLT

Validate input before transforming it. Treat entity declarations and external
references as untrusted; do not enable resolution of remote resources.

```filemaker
Set Variable [ $transformed ; Value: BE_XSLTApply ( $approvedInputPath ; $stylesheet ; $approvedOutputPath ) ]
Set Variable [ $transformError ; Value: BE_GetLastError ]
If [ $transformError <> 0 ]
    Exit Script [ Text Result: "transform-failed" ]
End If
```

The input and output are native file paths; the stylesheet is XML text, not a
path. This operation writes a file: obtain authorization for that destination.
Use a fixed, reviewed stylesheet rather than accepting arbitrary transformations.

## 5. Arrays and value lists

BE_ arrays are session-scoped handles stored in plug-in memory. Release them
when finished, especially in long-running Server scripts.

```filemaker
Set Variable [ $handle ; Value: BE_ArraySetFromValueList ( $values ; False ) ]
Set Variable [ $count ; Value: BE_ArrayGetSize ( $handle ) ]
Set Variable [ $third ; Value: BE_ArrayGetValue ( $handle ; 3 ) ]
Set Variable [ $removed ; Value: BE_ArrayDelete ( $handle ) ]
```

The handle is not the data. Do not store it in a field or assume it survives a
different session.

## 6. Regular expressions

Keep patterns anchored and test both a match and a non-match. Avoid unbounded
repetition on large attacker-controlled text.

```filemaker
Set Variable [ $code ; Value: BE_RegularExpression ( $input ; "^[A-Z]{2}-[0-9]{4}$" ) ]
If [ IsEmpty ( $code ) ]
    Exit Script [ Text Result: "invalid-code" ]
End If
```

## 7. JavaScript

Run only reviewed script text. The JavaScript context is not a security boundary
and may expose host capabilities depending on the plug-in version. Do not pass
credentials into a script that is logged or displayed.

```filemaker
Set Variable [ $result ; Value: BE_EvaluateJavaScript ( $reviewedScript ) ]
```

## 8. PDF and containers

PDF helpers operate on native paths. Check that source and destination files
exist and that the destination is writable before appending or merging. Verify
page counts or file size after the operation instead of assuming success.

```filemaker
Set Variable [ $pages ; Value: BE_PDFPageCount ( $pdfPath ) ]
If [ $pages = 0 ]
    Exit Script [ Text Result: "empty-pdf" ]
End If
```

## 9. Hashing and encryption

Use native `CryptDigest`, `CryptAuthCode` and the `Crypt*` functions where the
target FileMaker version provides them. Use BE_ functions only when the required
algorithm or container behaviour is unavailable natively. Never invent a key
management scheme in a calculation; keys belong in a protected store.

## 10. Operational checklist

- [ ] Plug-in version and platform checked.
- [ ] Exact signature and optional arguments checked in the catalog.
- [ ] Error signal checked after every network, file, mail or PDF operation.
- [ ] Credentials and personal data kept out of scripts and logs.
- [ ] Writes limited to an approved path, with rollback or backup.
- [ ] Temporary arrays and curl options released.
- [ ] Result reported as catalog-checked, documentation-checked or engine-tested,
      without overstating the evidence.
