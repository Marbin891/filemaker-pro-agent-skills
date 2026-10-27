# Routing matrix and cases

The routing contract is intentionally deterministic where possible. Hosts still
perform their own implicit selection from the frontmatter descriptions.

## Matrix

| Request | Primary | Supporting |
|---|---|---|
| "Fix this FileMaker calculation" | `filemaker-pro` | — |
| "Does Open Transaction work on Server 19.6.1?" | `filemaker-pro` | — |
| "Build a JSON parameter for a script" | `filemaker-pro` | — |
| "Review this Data API / OData integration" | `filemaker-pro` | — |
| "Why is my `BE_HTTP_POST` returning empty?" | `goya-be-plugin` | `filemaker-pro` if script steps are involved |
| "Use BaseElements to write a CSV file" | `goya-be-plugin` | — |
| "Which MBS function creates a PDF?" | `monkeybread-mbs-plugin` | — |
| "Is DynaPDF included in the MBS licence?" | `monkeybread-mbs-plugin` | — |
| "Call `bBox_Zsh` from a server script" | `beezwax-bbox-plugin` | `filemaker-pro` for PSoS behaviour |
| "Write a script that calls MBS and BE_" | all three | `filemaker-pro` for steps |
| "Compare BE_, MBS and bBox for HTTP" | all three | `filemaker-pro` for native HTTP options |
| "Optimize PostgreSQL" | none | — |
| "Format generic JSON" | none | — |
| "Write an Excel formula" | none | — |

## Positive cases

1. **Native only.** "This `Set Variable` step fails when the found set is empty;
   explain the script-step behaviour and error handling."
   Route to `filemaker-pro`. The word "script" is a strong native signal.
2. **One plug-in.** "What parameters does `BE_HTTP_POST` take, and how do I check
   the HTTP status?"
   Route to `goya-be-plugin`. Do not load MBS or bBox.
3. **One plug-in, server context.** "Can `bBox_Applescript` run in Perform Script
   on Server?"
   Route to `beezwax-bbox-plugin`; add `filemaker-pro` only if the answer needs
   PSoS script-step behaviour. State the plug-in limitation first.
4. **Several plug-ins.** "Compare `MBS( "Files.ReadFile" ... )` with
   `BE_FileRead` for a server-side import."
   Load both plug-in skills. Compare only the looked-up entries. Do not invent a
   shared error model.
5. **Plug-in plus native steps.** "Write a script that reads a file with bBox,
   validates it, and exits with a JSON result."
   Load `beezwax-bbox-plugin` and `filemaker-pro`. Use bBox for the file call and
   FileMaker for `If`, `Exit Script` and JSON handling.

## Negative cases

1. "Optimize PostgreSQL." No FileMaker marker. Decline FileMaker routing unless
   the user supplies a FileMaker context.
2. "Format generic JSON." A native FileMaker JSON function may be relevant only
   if the user asks for FileMaker. Do not load a plug-in skill.
3. "Write an Excel formula." Not FileMaker.
4. "Install the MBS plug-in for me." The skill can explain requirements and
   point to the vendor, but it cannot install or license the binary.
5. "Which plug-in is fastest?" Without a target product, data volume and test
   method, do not guess. Ask for the environment and propose a measurement plan.

## Ambiguity handling

- If the supplied code contains no function calls but mentions a product, ask
  for the code or select the product skill.
- If a request names a generic capability ("HTTP", "PDF", "SQL"), do not load
  all plugin skills. Ask which product or inspect the code for a prefix.
- If two skills disagree, prefer the owning skill's catalog for that dialect and
  `filemaker-pro` for native FileMaker behaviour. Report the conflict rather
  than merging incompatible facts.
- If the host exposes a live FileMaker tool, authorization and evidence rules
  from `filemaker-pro` still apply.

## Evidence labels

Use the same labels across skills:

- **catalog-checked** — matched a local catalog entry;
- **documentation-checked** — checked the linked vendor or Claris page;
- **engine syntax-validated** — parsed or validated by a FileMaker engine;
- **engine-evaluated** — evaluated by a FileMaker engine;
- **written and read back** — a change was applied and read back.

Do not upgrade one label to another because a different skill supplied the call.
