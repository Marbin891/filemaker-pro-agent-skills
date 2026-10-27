# Compatibility and snapshot boundaries

The bundled factual catalogs originate in CadenceUX's FileMaker 26 reference,
verified upstream 2026-10-02 against 26.0.3. We counted the actual entries locally;
we did not revalidate all 584 entries against the engine or current web pages.

## Interpreting versions

- Compare numeric components, padded with zeros: `19.6.1 > 19.6 > 19.3`.
- `6.0 or earlier` supplies an upper bound on introduction, not an exact date.
  A target below 6.0 is **unknown**, not automatically unsupported.
- Marketing year mapping: 2023 = 20, 2024 = 21, 2025 = 22, 2026 = 26.
  The lookup CLI accepts engine versions, not marketing years.
- Minimum introduction is necessary, not sufficient. Later options, changed behavior,
  removed features, bug fixes, privilege sets and host/client compatibility are separate.
- A version above 26.0.3 is outside this verified snapshot. Even when minimum-version
  comparison passes, report current support as unverified.
- Example: Open Transaction requires **19.6.1**, not the broad “19.3 or later”.
- Example: PDF steps originated in 26, but WebDirect file upload/download behavior
  changed in 26.0.3. A version field alone cannot approve 26.0.1 options.

## Script support

The delta matrix has seven keys: Pro, Go, WebDirect, Server, Cloud, DataAPI, CWP.
An absent key means Yes **for the upstream snapshot**, `No` means unsupported,
and `Partial` means some behavior/options differ. The complete catalog keeps
all exceptions, OS restrictions, original behavioral notes and technical metadata.
The notes are snapshot evidence; release-specific changes still need checking.

Measured Yes / Partial / No counts:

| Product | Yes | Partial | No |
|---|---:|---:|---:|
| Pro | 204 | 6 | 6 |
| Go | 154 | 20 | 42 |
| WebDirect | 106 | 35 | 75 |
| Server | 108 | 29 | 79 |
| Cloud | 106 | 27 | 83 |
| DataAPI | 91 | 26 | 99 |
| CWP | 99 | 26 | 91 |

Unsupported steps generally report error 3. Never rely on automatic skipping as
correct business logic. Detect the environment and design an explicit branch.
Do not map OData onto DataAPI or assume Cloud and Server are interchangeable.

## Functions, fields and client differences

There is no complete function-platform matrix here. Validate mobile, window, plug-in,
AI, container and UI-context functions against their specific release documentation.
Catalog absence is not a claim of incompatibility. Field storage/index flags describe
capabilities, not a schema specification or an XML serializer.

Server scripts execute in a distinct session. Client globals, window state, active
layout and found sets do not automatically transfer. Pass parameters and establish
context. WebDirect browser UI and Go device APIs are not desktop equivalents.

## Official sources checked during adaptation

- https://help.claris.com/en/pro-release-notes/content/index.html
- https://help.claris.com/en/pro-help/content/open-transaction.html
- https://help.claris.com/en/pro-help/content/jsonsetelement.html
- https://help.claris.com/en/data-api-guide/content/index.html
- https://help.claris.com/en/odata-guide/content/index.html

These links are for optional deeper checks, not required for ordinary local lookups.
