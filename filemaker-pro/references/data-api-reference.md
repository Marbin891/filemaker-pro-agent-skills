# Data API: an offline integration contract

Scope: the upstream reference snapshot is FileMaker **26.0.3**, dated **2026-10-02**.
Official pages were also consulted during this adaptation; no requests were engine-tested.
All examples below are original, synthetic templates, not Claris example payloads.

## Addressing and prerequisites

- Base: `https://<HOST>/fmi/data/vLatest/databases`; let `D = <base>/<DB>`.
- Let `L = D/layouts/<LAYOUT>`; these aliases are explanatory, not literal URL syntax.
- Percent-encode database, layout, field and script names as individual path segments.
- `vLatest` follows the host's latest API; pin a supported version when reproducibility matters.
- Enable the service on the host and grant the account the `fmrest` extended privilege.
- Use a dedicated integration layout containing the required fields and portals.
  Layout context and account privileges both matter; a layout is not an authorization boundary.

## Authentication lifecycle

| Operation | Request and interpretation |
|---|---|
| Server file-account login | `POST D/sessions`, JSON `{}`, `Authorization: Basic <BASE64_ACCOUNT_COLON_PASSWORD>` |
| Cloud Claris ID login | `POST D/sessions`, JSON `{}`, `Authorization: FMID <CLARIS_ID_TOKEN>` |
| Subsequent data calls | `Authorization: Bearer <DATABASE_SESSION_TOKEN>` |
| Logout | `DELETE D/sessions/<DATABASE_SESSION_TOKEN>`; no body |

Send `Content-Type: application/json` for JSON request bodies. Always use HTTPS.
Server login exposes the session token in `response.token` and `X-FM-Data-Access-Token`.
The Cloud login documentation specifies the header and an empty `response` object;
therefore do not require `response.token` to exist for Cloud authentication.
Claris ID credentials/tokens and database session tokens are different secrets.
The documented Data API session idle timeout is 15 minutes after the last token-bearing call.
Cloud identity tokens have a separate documented one-hour lifecycle; refresh the right layer.
Never put credentials in saved examples, URLs, exception text or request logs.

## Record operations relative to L

| Method and suffix | Purpose / request details |
|---|---|
| `POST /records` | Create; JSON `fieldData` contains field/value pairs |
| `GET /records/<RECORD_ID>` | Read one record in the selected layout context |
| `GET /records?_offset=1&_limit=25` | Read a page; offset is one-based |
| `PATCH /records/<RECORD_ID>` | Update only supplied fields; optional top-level `modId` |
| `POST /records/<RECORD_ID>` | Duplicate an existing record |
| `DELETE /records/<RECORD_ID>` | Delete; not a business-key lookup |
| `POST /_find` | Submit FileMaker find criteria, not SQL or OData expressions |

Synthetic create body: `{"fieldData":{"DispatchCode":"<NEW_CODE>","Queue":"staging"}}`.
Synthetic edit body: `{"fieldData":{"Queue":"review"},"modId":"<LAST_READ_MOD_ID>"}`.
Keep `recordId` separate from your UUID/business key. Keep IDs as returned strings.
Supplying the last read `modId` prevents an edit when another edit has changed that version.
On conflict, reload and reconcile; do not automatically overwrite with a fresh modification ID.
Validation applies by default. Do not disable validation just to make an integration succeed.

## Find, pagination and response handling

Original find body (replace the synthetic schema before use):
```json
{"query":[{"Queue":"==staging","Priority":">=4"}],"sort":[{"fieldName":"DispatchCode","sortOrder":"ascend"}],"offset":"1","limit":"25"}
```
Criteria in one query object combine as AND; multiple positive requests provide alternatives.
An omit request uses `"omit":"true"`; remember these are FileMaker find operators.
Find body keys are `offset` / `limit`; GET query-string keys are `_offset` / `_limit`.
Main-record limits do not limit portal rows: portal pagination is a separate concern.
Inspect HTTP status, parseable JSON, and `messages[].code`; `"0"` indicates FileMaker success.
For reads/finds, inspect `response.data` entries: `fieldData`, `portalData`, `recordId`, `modId`.
Creates return identifying data; edits return a new modification ID, not a complete readback.
Treat an empty match as a business outcome, not a reason to retry a write.
After a transport timeout on create, reconcile using a unique application key before retrying.

## Scripts and discovery

Run `GET L/script/<SCRIPT_NAME>?script.param=<URL_ENCODED_PARAMETER>`.
An original parameter could be JSON text `{"batch":"<BATCH_UUID>","mode":"validate"}`.
Check `response.scriptError` independently of `messages`; parse `scriptResult` as your contract.
Some record/find operations accept `script.prerequest`, `script.presort` and `script` hooks.
Keep scripts noninteractive and establish their own layout/context; avoid blind GET retries.
Discover layouts with `GET D/layouts`, layout metadata with `GET L`, scripts with `GET D/scripts`.
Portal writes, container multipart uploads and external-source authentication need their own contracts;
their detailed option coverage is not established by this short reference.

## Evidence and attribution

Consulted official URLs (facts only; no upstream prose/example blocks reproduced):
- https://help.claris.com/en/data-api-guide/content/log-in-database-session.html
- https://help.claris.com/en/data-api-guide/content/log-in-database-session-claris-id.html
- https://help.claris.com/en/data-api-guide/content/log-out-database-session.html
- https://help.claris.com/en/data-api-guide/content/edit-record.html
- https://help.claris.com/en/data-api-guide/content/perform-find-request.html
- https://help.claris.com/en/data-api-guide/content/run-filemaker-scripts.html
- https://help.claris.com/en/data-api-guide/content/get-layout-metadata.html
- https://help.claris.com/en/pro-help/content/extended-privileges.html

Local naming cross-check: `sources/claris-filemaker-pro-skill/references/data-api-reference.md`.
Credit: Darrin Southern / CadenceUX, https://github.com/CadenceUX/claris-filemaker-pro-skill,
declared CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). That declaration does not
license Claris documentation; this independently written reference retains facts and API names only.
