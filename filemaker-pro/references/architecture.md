# FileMaker architecture: context before code

## Scope and evidence
- This is original design guidance, not a reproduction of Claris documentation.
- Official facts were checked against the URLs below on 2026-10-27.
- No FileMaker application, hosted database, or runtime test was available.
- Confirm the exact Pro, Go, WebDirect host, and Server builds before delivery.

## Model the business separately from the interface
- A base table stores a class of records; a table occurrence gives it a graph role.
- Several occurrences can point to the same base table without duplicating its data.
- A layout is based on a table occurrence, not merely on a familiar table name.
- Record which occurrence each service layout uses before writing navigation steps.
- Prefer stable, nonempty unique identifiers over names or record positions.
- Keep foreign keys compatible with the referenced identifier's type and format.
- Represent many-to-many business relationships with an explicit join table.
- Store attributes of the association on that join table.
- Treat cascading deletion and related-record creation as deliberate business decisions.
- A relationship does not replace account privileges or record-level authorization.

## Make context an explicit input
Document these properties for every public script:
1. File and account privilege assumptions.
2. Window ownership and whether navigation is allowed.
3. Starting layout and its table occurrence.
4. Current record identity, found set, and required sort order.
5. Browse or Find mode requirements.
6. Whether an active portal row is relevant.
7. Whether the caller may have uncommitted edits.
8. Result contract and promised context on return.

An occurrence name alone does not establish a current record.
A current record number is not a durable business identifier.
Changing layouts can alter relationship evaluation and activate script triggers.
Resolve a target by its key and verify it before changing any field.
If a helper owns a separate window, its changes have a separate transaction context.

## Storage and indexes
- Stored values can support indexes where their field type and settings permit.
- A stored calculation can avoid repeated evaluation and may be indexable.
- Unstored calculations are evaluated as needed and cannot supply a stored index.
- Related fields, summaries, globals, and unstored dependencies affect storage eligibility.
- Do not assume a calculation involving the current date advances while stored.
- Choose a dynamic calculation or an explicit refresh process for time-dependent facts.
- The related side's match field must be indexable for relationship matching.
- A global field can drive a relationship from the current side, not its indexed target.
- Test finds and sorts on realistic row counts rather than extrapolating from a demo.
- Repeated unstored calculations across a large list can amplify network and CPU work.
- Materialize expensive derived data only with a defined refresh and consistency policy.
- A cached value needs an owner, invalidation rule, and reconciliation procedure.

## Portals and presentation
- A related-record portal presents records through its configured relationship context.
- Portal filtering further restricts presentation; it is not an authorization boundary.
- Portal sorting can differ from the order used elsewhere in a script.
- Capture the related record's identifier, not just the portal row position.
- Do not infer a business total from the number of currently visible portal rows.
- Check the portal's source occurrence before placing or setting related fields.
- Separate display filters from business queries that drive updates or reports.
- Prefer bounded related lists over a dashboard that fetches every detail at startup.

## Execution surfaces
| Surface | Architectural consequence |
| --- | --- |
| Pro | Desktop UI, windows, and local resources need explicit ownership. |
| Go | Design for touch, interrupted connectivity, and mobile resource constraints. |
| WebDirect | Browser delivery does not imply support for every desktop script step. |
| Server / Cloud scripts | Separate FMSE sessions must establish their own context. |

Hosting a file does not mean all its scripts execute on the host.
Pass identifiers and options to server scripts; do not expect client globals or found sets.
Check each step's compatibility and platform-specific options for the actual release.
Server paths and network access belong to the server environment, not the user's device.
Use headless result envelopes rather than dialog-dependent service logic.
Test privileges with the intended service account, not only with Full Access.

## Consistency boundaries
- Native transactions start with Open Transaction, introduced in 19.6.1.
- Their record-change scope is the originating window, including supported file/table work.
- Do not move transaction work to another window and assume it is protected.
- A server-side call is a different session, not an extension of the caller's transaction.
- HTTP calls, email, and external services do not gain distributed atomicity.
- Execute FileMaker Data API step changes are outside the enclosing script transaction.
- Stage outbound work durably and reconcile delivery after the local commit.
- Define lock-conflict, retry, and duplicate-processing behavior before deployment.

## Review checklist
- Can every mutation be tied to a verified key and context?
- Are heavily queried fields stored and indexed when appropriate?
- Are relationship direction and portal filters understood?
- Are secrets and sensitive fields excluded from unnecessary layouts and logs?
- Are deployment, backup, recovery, and client compatibility documented?

## Official sources
- https://help.claris.com/en/pro-help/content/relationships.html
- https://help.claris.com/en/pro-help/content/calculation-fields.html
- https://help.claris.com/en/pro-help/content/running-scripts-on-server.html
- https://help.claris.com/en/pro-help/content/open-transaction.html
