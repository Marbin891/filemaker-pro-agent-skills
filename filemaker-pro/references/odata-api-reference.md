# OData: metadata-first integration

Boundary: upstream snapshot **26.0.3**, verified upstream **2026-10-02**.
This is original explanatory material based on local naming checks and official documentation,
not an engine test or a claim that every OData-standard feature works in FileMaker.

## Service and authentication

- Service prefix: `https://<HOST>/fmi/odata/v4`; database root: `<prefix>/<DB>`.
- OData addresses tables/fields, not Data API layouts/portals. Enable `fmodata` access.
- Server: use a permitted file account, `Authorization: Basic <BASE64_ACCOUNT_COLON_PASSWORD>`.
- Cloud: obtain a Claris ID token, then send `Authorization: FMID <CLARIS_ID_TOKEN>` on calls.
- Do not substitute Data API `/sessions` or its Bearer token into this contract.
- Cloud identity tokens have a documented one-hour validity; handle authentication renewal.
- Use HTTPS, `Accept: application/json` for data, and JSON Content-Type for JSON writes.
- Metadata is a schema document: do not feed it to a parser expecting a record collection.

## Discover before generating URLs

| GET URL relative to prefix | Meaning |
|---|---|
| `/` | Discover accessible database services |
| `/<DB>/` | Discover table/entity sets in that database |
| `/<DB>/$metadata` | Inspect types, keys, fields, IDs and FileMaker annotations |
| `/<DB>/<ENTITY_SET>` | Request a table's records |

Read the declared key from metadata rather than assuming every key is your UUID or ROWID.
FileMaker uses qualifying unique/nonempty fields as keys, otherwise the ROWID system field.
`BestRowID` identifies ROWID; `RowVersion` identifies ROWMODID; both can be selected explicitly.
FileMaker metadata also describes calculated/global fields, repetitions and immutable IDs.
Keep a cached schema for offline development, but invalidate it after migrations.

## Escaping is two different jobs

First construct valid OData syntax; then percent-encode URL components once using a URL library.
An apostrophe inside an OData string literal is doubled, not backslash-escaped.
For example the synthetic value `pilot's kit` becomes the literal `'pilot''s kit'`.
The FileMaker filter documentation requires double quotes around field names containing
special characters, including spaces or underscores; URL-encode those quote characters too.
Encode names as path segments; never encode the entire assembled URL including its separators.
Protect `$filter` and `$metadata` from shell variable expansion when using command-line clients.
Do not use FileMaker find operators such as `==` in an OData filter.

## A bounded read contract

Original logical request, shown before URL encoding, against a synthetic Dispatch table:
```text
GET <DATABASE_ROOT>/Dispatch?$select=DispatchCode,Priority&$filter=Priority ge 4&$orderby=DispatchCode&$top=25&$skip=0
```
`$filter` controls membership; `$select` reduces fields; `$orderby` supplies deterministic ordering.
`$top` takes rows and `$skip` omits rows; unlike Data API offset, the initial skip is zero.
Use a unique tie-breaker in ordering when the leading sort field is not unique.
Concurrent changes can still shift offset-based pages; deduplicate by key during extraction.
Date/time filter values use ISO 8601; document the server time-zone interpretation explicitly.
`$expand`, `$count` and `$apply` exist, but this reference does not establish every combination.
Unsupported documented features include `$search`, lambda `any`/`all`, and geo functions.

## Writes, scripts and schema are separate capabilities

POST to an entity set creates; PATCH to a keyed entity updates; DELETE removes a keyed entity.
Build the key literal from its metadata type; do not guess whether it needs string quotes.
Validate response status/body before committing local sync state; reconcile uncertain writes.
For scripts, use `POST <DATABASE_ROOT>/Script.<SCRIPT_NAME>`.
Use a completely empty body for no parameter, not `{}`; otherwise use `scriptParameterValue`.
Original parameter body: `{"scriptParameterValue":{"batch":"<BATCH_UUID>","dryRun":true}}`.
Inspect `scriptResult.code` and `scriptResult.resultParameter`; these are not Data API keys.
Scripts run server-side and cannot require user interaction. Script names have restrictions:
special characters such as `@`, `&`, `/`, and names beginning with a number are unsupported.
Standard OData writes do not activate script triggers; move required logic into explicit scripts.
No separate OData support matrix is bundled: DataAPI/CWP counts do not prove OData support.

Verified schema entry point: `POST <DATABASE_ROOT>/FileMaker_Tables` creates a table.
Its JSON representation uses `tableName` and `fields`; field definitions use `name` and `type`.
This is an administrative schema operation, not SQL text and not ordinary record creation.
Require a separate migration approval and schema backup; omit speculative schema endpoints.
Exact batch atomicity, ETag policy and all alter/index operations are outside this local contract.

## Evidence and attribution

Official URLs consulted:
- https://help.claris.com/en/odata-guide/content/write-odata-api-calls.html
- https://help.claris.com/en/odata-guide/content/creating-authenticated-connection.html
- https://help.claris.com/en/odata-guide/content/get-metadata.html
- https://help.claris.com/en/odata-guide/content/query-option-filter.html
- https://help.claris.com/en/odata-guide/content/run-scripts.html
- https://help.claris.com/en/odata-guide/content/create-table.html
- https://help.claris.com/en/odata-guide/content/odata-unsupported-features.html
- https://help.claris.com/en/odata-guide/content/create-record.html
- https://help.claris.com/en/odata-guide/content/update-record.html
- https://help.claris.com/en/odata-guide/content/delete-record.html
- https://help.claris.com/en/odata-guide/content/enable-access.html

Local cross-check: `sources/claris-filemaker-pro-skill/references/odata-api-reference.md`.
Naming/source credit: Darrin Southern / CadenceUX,
https://github.com/CadenceUX/claris-filemaker-pro-skill, declared CC BY 4.0:
https://creativecommons.org/licenses/by/4.0/. This does not grant rights to Claris text;
no Claris/upstream prose or example blocks are redistributed here.
