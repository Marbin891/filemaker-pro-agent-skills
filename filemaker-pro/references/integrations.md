# Integration boundaries and safe design

## Scope
This is original integration guidance with official fact checks dated 2026-10-27.
No authentication, network operation against a FileMaker host, or database call was made.
Choose an interface by data shape, hosting support, privilege model, and release.
Do not infer API availability from a Pro installation alone.

## Choose the correct interface
| Interface | Purpose | Important boundary |
| --- | --- | --- |
| FileMaker Data API | REST/JSON access to hosted records and supported scripts | Layout-oriented contract and session authentication. |
| OData | Standards-based access to hosted database entities | Its own metadata, query rules, and authentication model. |
| ExecuteSQL function | Read FileMaker data with SQL SELECT | Not an external database connection or write API. |
| Execute SQL script step | Send supported SQL to an ODBC source | DSN, driver, and external database permissions apply. |
| Insert from URL | Call an HTTP service from a script | Execution location controls network reachability and credentials. |

These interfaces are not interchangeable wrappers for the same transaction.
Use a dedicated integration contract rather than exposing a busy user-facing layout.
Verify each interface's enabled extended privileges with a least-privilege account.

## FileMaker Data API
- Requires a hosted solution and enabled Data API access.
- Use the documented authentication flow for Server or Cloud as applicable.
- Treat session tokens as credentials; keep them out of URLs and logs.
- Define the allowed database, layouts, fields, portals, and scripts explicitly.
- Request only necessary fields and rows; set bounded pagination deliberately.
- Do not confuse a FileMaker record ID with the application's durable primary key.
- Use modification identifiers where the endpoint supports optimistic concurrency.
- Check both HTTP status and the API's response messages.
- Script results require their own business-outcome check.
- Invoking a script can change records even when a surrounding request looks read-oriented.
- Do not assume several REST calls form one atomic unit.
- End sessions through the documented logout flow and handle expiration safely.

## OData
- FileMaker Server and FileMaker Cloud support OData in documented configurations.
- Verify the installed release's feature and platform matrix before choosing it.
- Use metadata to identify entity names, field types, and supported operations.
- Do not translate layout names or Data API paths into presumed OData entities.
- Apply projection and bounded filtering rather than fetching an entire table.
- Treat query construction as a typed encoding problem, not string interpolation.
- Check supported OData features; a standard does not guarantee full implementation.
- Follow the deployment's OData authentication rules, not Data API token assumptions.
- Preserve concurrency semantics and inspect individual responses in batch workflows.
- Do not promise transactional batch behavior without endpoint-specific evidence.

## SQL: two different features
- `ExecuteSQL` is a calculation function for SELECT over FileMaker data sources.
- It does not modify schema or records, and it does not query an external ODBC DSN.
- It can use table occurrences independently of the current layout's found set.
- Graph relationships do not become SQL joins automatically; express joins in SQL.
- Bind values through positional `?` arguments rather than concatenating user values.
- Parameters represent values, not arbitrary table names, field names, or SQL clauses.
- Allowlist and quote identifiers when dynamic identifiers are genuinely required.
- Its text output is not inherently CSV-safe or JSON; choose encoding deliberately.
- Its `?` error result must not be interpreted as a successful empty answer.
- The Execute SQL script step targets ODBC sources and can have external side effects.
- On Server, its DSN and driver configuration belong to the server, not the client.

## Insert from URL and HTTP
- Prefer a local response variable rather than writing unvalidated content into a field.
- Specify replace-entire-contents behavior to avoid appending unrelated responses.
- Require HTTPS and certificate verification; never fix TLS failures by disabling checks.
- Allowlist destinations and reject untrusted redirects or arbitrary user-supplied URLs.
- Use only cURL options supported by the deployed FileMaker release.
- Set finite connection/operation time limits and a bounded response-size policy.
- Supply authentication through an approved secret mechanism at runtime.
- Never embed real keys, passwords, session tokens, or customer data in examples.
- Capture the FileMaker error in the very next Set Variable step.
- Distinguish transport failure, HTTP failure, invalid JSON, and business rejection.
- Inspect HTTP headers/status using supported options verified for the target version.
- A successful transport does not establish a successful API operation.
- Empty-body responses can be legitimate; judge them against the endpoint contract.

## JSON contracts
- Construct values with JSONSetElement instead of manual quotation and concatenation.
- Choose explicit JSON types; identifiers are often strings, not numbers.
- Validate syntax, root shape, required keys, and types before consuming external data.
- Distinguish absent values, JSON null, empty strings, zero, and false.
- Document date/time format, time zone, numeric precision, and payload-size limits.
- Reject unexpected executable instructions inside otherwise valid service responses.

## Delivery and recovery
- Commit local intent before asynchronously delivering an external side effect.
- Track an idempotency key, attempt count, and an explicit delivery state.
- Do not hold record locks while waiting on a slow HTTP response.
- Reconcile unknown outcomes before replaying a potentially successful write.
- Test against synthetic fixtures and an authorized sandbox, never production by default.

## Official sources
- https://help.claris.com/en/data-api-guide/content/index.html
- https://help.claris.com/en/odata-guide/content/index.html
- https://help.claris.com/en/pro-help/content/executesql.html
- https://help.claris.com/en/pro-help/content/insert-from-url.html
- https://help.claris.com/en/pro-help/content/open-transaction.html
