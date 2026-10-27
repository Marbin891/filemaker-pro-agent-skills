# SQL inside FileMaker: read queries without context confusion

Reference boundary: FileMaker **26.0.3**, upstream snapshot **2026-10-02**.
Examples are independently constructed for a fictional inspection system, not copied upstream.
No query below has been run against a FileMaker engine during this adaptation.

## Choose the correct execution surface

| Surface | Contract |
|---|---|
| `ExecuteSQL` calculation function | SELECT against FileMaker table occurrences; returns text |
| `Execute SQL` script step | SQL through an ODBC data source; not the calculation function |
| External ODBC/JDBC client | Driver-supported SQL; permissions/configuration apply |
| OData schema APIs | HTTP schema representations; not a SQL execution endpoint |

`ExecuteSQL` cannot INSERT, UPDATE, DELETE, CREATE or ALTER. Do not implement migrations
by passing DDL into a calculation. SQL-reference syntax for drivers is not automatically
permission to use that syntax in the calculation function.

## Function contract

`ExecuteSQL ( sqlQuery ; fieldSeparator ; rowSeparator { ; arguments... } )`

- `sqlQuery` is SELECT text; `?` represents a bound value, in positional argument order.
- Parameters bind values, not table names, column names, sort directions or whole clauses.
- Choose identifiers from a developer-controlled allowlist; never concatenate user input.
- Double-quote identifiers; within a FileMaker string, escape each quote as `\"`.
- Single quotes denote SQL text literals; prefer bound arguments instead.
- Empty field separator means comma; empty row separator means carriage return.
- Output is text, not records, JSON or guaranteed escaped CSV.

The FROM names are table occurrences available to the FileMaker data source.
Graph relationship predicates do not define the SQL join. Found set and current layout
do not supply implicit WHERE clauses; state every join and filter explicitly.
Account restrictions still apply: independence from layout context is not privilege bypass.

## Original parameterized join

Assume occurrences `InspectionRun` (RunUUID, StationUUID, Outcome, MeasuredAt) and
`TestStation` (StationUUID, Label). `$wantedOutcome` and `$fromTimestamp` are caller inputs.
```filemaker
ExecuteSQL (
  "SELECT s.\"Label\", COUNT(*)
   FROM \"InspectionRun\" r
   INNER JOIN \"TestStation\" s ON r.\"StationUUID\" = s.\"StationUUID\"
   WHERE r.\"Outcome\" = ? AND r.\"MeasuredAt\" >= ?
   GROUP BY s.\"Label\"
   ORDER BY s.\"Label\""
  ; Char ( 9 ) ; Char ( 13 ) ; $wantedOutcome ; $fromTimestamp
)
```
Bind the timestamp as a FileMaker timestamp value, not a locale-formatted display string.
This groups equal station labels together; group by StationUUID too if labels can repeat.
It intentionally excludes stations with no qualifying run. To retain them, use LEFT OUTER
JOIN and place right-side eligibility predicates in ON, not a null-rejecting WHERE clause.
Count a non-null right-side key rather than `COUNT(*)` when counting outer-joined matches.
INNER JOIN and LEFT OUTER JOIN are documented; RIGHT and FULL OUTER JOIN are unsupported.

## Result and correctness checks

- Test `?` as an execution/parsing failure; do not confuse it with an empty result.
- `ExecuteSQLe` can provide more diagnostic detail on versions that support it.
- A valid query with no matching rows differs from an aggregate row whose count is zero.
- Use `IS NULL` / `IS NOT NULL`; equality against NULL is not a null test.
- Convert numeric output deliberately; a delimited multirow result is not one number.
- If text may contain the chosen separators, do not split it without a separate encoding contract.
- Parameterize dates/times. Literal dates use SQL syntax such as `DATE '2026-09-17'`.
- ExecuteSQL does not accept ODBC brace-wrapped date/time constants.
- Returned numbers/dates use SQL formatting, not necessarily the user's file/system locale.
- SQL Unicode binary sorting differs from language-aware FileMaker sorting.
- Avoid `SELECT *` in long-lived integrations: schema changes otherwise alter column positions.
- Profile representative data and privilege sets; successful syntax does not establish speed.

## System fields and scope limits

FileMaker SQL exposes `ROWID` and `ROWMODID`, not Data API's JSON `recordId` / `modId` keys.
They identify internal record identity and modification count, not application UUIDs.
Do not turn modification counts into a cross-table clock or assume they detect deletions.
Container handling, driver DDL options, external-source types and all SQL functions are not
exhaustively specified here; consult the matching execution surface before extending a query.

## Evidence and attribution

Consulted official URLs:
- https://help.claris.com/en/pro-help/content/executesql.html
- https://help.claris.com/en/sql-reference/content/from-clause.html
- https://help.claris.com/en/sql-reference/content/sql-clauses.html
- https://help.claris.com/en/sql-reference/content/filemaker-system-columns.html

Local naming check: `sources/claris-filemaker-pro-skill/references/sql-reference.md`.
Credit for that factual reference: Darrin Southern / CadenceUX,
https://github.com/CadenceUX/claris-filemaker-pro-skill; declared CC BY 4.0,
https://creativecommons.org/licenses/by/4.0/. Claris documentation has separate rights;
this file reproduces neither its explanatory prose nor its worked examples.
