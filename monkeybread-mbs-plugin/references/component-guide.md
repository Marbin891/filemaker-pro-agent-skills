# MBS component guide

Original selection guidance for this project. It names components and functions
from the local catalog; it does not reproduce vendor descriptions. Check each
function's signature, platform flags and `status` before use.

## Contents

1. Choosing a component
2. PDF and office documents
3. HTTP, SQL and data
4. Files, paths and processes
5. Dialogs and interface
6. Web and windows
7. Images, text and system
8. Events, contacts and calendar
9. Licensing notes

## 1. Choosing a component

Resolve the component name in `references/index.json`, then read one group file.
The largest components are not automatically the best choice: DynaPDF, XL and
Saxon are specialized add-ons with separate licences, and many window or dialog
functions are desktop-only.

A practical sequence:

1. Decide whether a native FileMaker function already covers the task.
2. Identify the component by object type (PDF, SQL, JSON, file, window, event).
3. Check the user's platform and product (Pro, Go, Server, iOS SDK).
4. Check `status` and add-on requirements.
5. Check `version_introduced` against the installed plug-in.
6. Read the exact signature and `see_also` links.

## 2. PDF and office documents

- **DynaPDF** — PDF creation, import, text, images, forms and page operations.
  Requires a DynaPDF licence. Start with `DynaPDF.New`, then the operation
  functions, and release the document.
- **PDFKit** — platform PDF viewing and document access. Check macOS/Windows
  availability.
- **XL** — reading and writing Excel workbooks. Requires a LibXL licence.
- **Saxon** — XSLT 2.0/3.0 transformation. Requires Saxon-PE or Saxon-EE.
- **XML** — XML parsing and serialization when a full XSLT engine is not needed.

For a one-off PDF, check whether FileMaker's native PDF and container features
are sufficient before adding an add-on licence.

## 3. HTTP, SQL and data

- **CURL** — HTTP, FTP, mail and other libcurl protocols. Create a handle
  (`CURL.New`), set options (`CURL.SetOptionURL` and related functions), perform
  (`CURL.Perform`), read the result, then release (`CURL.Release`). Always release
  handles, including on error paths.
- **SQL** — connections, commands and result sets. `SQL.NewConnection`,
  `SQL.SetCommandText`, `SQL.Execute`, result functions and `SQL.FreeConnection`
  are separate steps. Do not assume a connection or command is implicitly closed.
- **JSON** — parse or manipulate JSON with a reference-based API. Release parsed
  references with `JSON.Release` where applicable.
- **MongoDB** — document database operations; check server compatibility and
  connection lifecycle.
- **Socket** — low-level TCP/UDP. Use CURL for HTTP unless raw sockets are
  required.

## 4. Files, paths and processes

- **Files** — read, write, inspect and set file attributes. Use POSIX paths and
  verify the destination directory.
- **Path** — path construction and normalization.
- **Shell** — run shell commands and capture output. Treat command text as
  untrusted; prefer argument passing.
- **Process** — inspect or control processes. Desktop and server permissions
  differ.
- **SSH** — remote command and transfer workflows. Credentials belong in a
  protected store.
- **Archive** — compression and extraction functions; check the exact component
  key in the index.

## 5. Dialogs and interface

- **Dialog** — message, input and button configuration. Set the message and
  buttons, run the dialog, then read the result. Some button functions are
  licensed.
- **ListDialog**, **QuickList**, **MenuItem** — selection lists and menus.
- **PrintDialog** — print configuration; desktop-only.
- **Clipboard** — read and write clipboard data.
- **DragDrop**, **ImagePicker**, **AVPlayer**, **AVRecorder** — interactive
  desktop features.

Desktop dialogs and UI automation generally do not work in Perform Script on
Server or schedules.

## 6. Web and windows

- **WebView** — load content, run JavaScript, inspect the DOM and capture
  output. Web viewer state is window-specific.
- **Window** — open, close, position and inspect windows.
- **MapView** — map display and annotation; platform-dependent.
- **Socket** and **CURL** are the network choices; WebView is for rendered
  content, not a general HTTP client.

## 7. Images, text and system

- **GMImage** — image conversion and manipulation through GraphicsMagick.
- **Text** — encodings, case, search and transformation beyond native functions.
- **SystemInfo** — machine and environment information.
- **Plugin** — plug-in registration and version information.
- **Audit** — change tracking and audit helpers; check server support.

Prefer native text and JSON functions for simple operations; MBS adds value for
binary, image, encoding and platform-specific work.

## 8. Events, contacts and calendar

- **Events**, **CNContact**, **CNContactStore**, **CNContactPicker** — modern
  calendar and contact access.
- **Calendar**, **Addressbook** — older components; check whether they are
  deprecated in favour of Events/Contacts.
- **UserNotification**, **UNNotification** — local notifications; platform and
  product restrictions apply.

Access to personal data requires user permission and a clear data-handling
policy. Do not read contacts or calendars without explicit authorization.

## 9. Licensing notes

`free` means the vendor documents unregistered use without a reminder dialog.
`licensed` means the function still runs unregistered but triggers a periodic
reminder until the base plug-in is registered. `unknown_license` means the vendor
page did not state either status; do not describe it as free.

DynaPDF, XL and Saxon require separate paid add-ons. The local catalog records
the requirement but not prices or current terms. Direct licensing questions to
Monkeybread.
