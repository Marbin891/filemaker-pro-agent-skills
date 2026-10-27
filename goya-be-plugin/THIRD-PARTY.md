# Third-party sources and redistribution boundaries

This document records what is bundled, what is referenced, and which rights are
not granted. It is a technical provenance record, not legal advice.

## Summary

| Source | Declared licence | What this project bundles | What it does not bundle |
|---|---|---|---|
| CadenceUX skills (six repositories) | CC BY 4.0 in README files | Adapted instructions, CadenceUX synthesis, factual catalog metadata | Claude manifests, host cache paths, automatic update code, vendor binaries |
| Goya BaseElements documentation | No repository licence metadata found | Function names, signatures, parameter names/flags, versions, platform flags, URLs, CadenceUX synthesis | Vendor prose, vendor notes, vendor example code |
| Monkeybread MBS documentation | Vendor copyright; no documentation redistribution licence found | Function names, signatures, parameter names/flags, results, versions, platform flags, licensing status, URLs | Vendor prose, parameter descriptions, vendor examples, plug-in binary or licence keys |
| Beezwax bBox documentation | No repository licence metadata found | Function names, signatures, parameter names/flags, results, error references, versions, platform flags, URLs, CadenceUX shared-reference synthesis | Vendor prose, vendor notes, vendor example code, plug-in binary |
| Claris FileMaker documentation | Written permission required for documentation copies | Factual API metadata in adapted catalogs; rewritten examples | Raw help-page mirrors, Claris software, preview binaries, logos |

## CadenceUX

The six source repositories declare CC BY 4.0 in their READMEs. This project
attributes Darrin Southern / CadenceUX, links the licence, identifies changes and
keeps the adaptation record in `ATTRIBUTION.md` and per-skill
`references/provenance.json`. The declaration cannot license material owned by
Claris or by the plug-in vendors.

## Goya BaseElements

The BaseElements plug-in is free and open source, but the documentation
repository has no top-level licence file or GitHub licence metadata. The catalog
therefore retains factual API data and links every entry to the vendor page. It
does not reproduce the vendor's descriptions, notes or examples. The plug-in
binary, installer and any licence key are not included. Live use requires a
separately installed BaseElements plug-in compatible with the target FileMaker
product.

## Monkeybread MBS

MBS documentation and software are owned by Christian Schmitz Software GmbH.
The vendor site does not declare a documentation redistribution licence. The
catalog is a factual index: it omits vendor descriptions, parameter prose and
examples, and links each entry to the vendor page. The plug-in binary, installer,
registration key and add-on licences (DynaPDF, XL, Saxon) are not included.
Licensing status is recorded per function, but the authoritative terms are the
vendor's.

## Beezwax bBox

bBox documentation lives in a GitHub wiki with no declared documentation licence.
The catalog retains factual signatures, parameter names, results, error
references, version and platform data, plus CadenceUX's CC BY 4.0 shared-reference
synthesis. Vendor prose, notes and examples are omitted. The plug-in binary and
installer are not included. bBox runs on macOS and Ubuntu, not Windows; live use
requires the separately installed plug-in.

## Claris FileMaker

The native catalogs derive from the pinned CadenceUX snapshot. Claris's
documentation terms require written permission for copies or distribution. This
project retains factual metadata, attributes CadenceUX synthesis and rewrites
worked examples. It does not claim that the retained selection or arrangement is
free of Claris rights, and it does not claim written permission. See
`docs/RELEASE-STATUS.md` for the remaining review boundary.

## Linked resources

Links to Claris, Goya, Monkeybread, Beezwax, OpenAI and Agent Skills pages are
provided for verification and optional further reading. They are not mirrored,
cached or fetched automatically by any skill, build or test. Following a link is
a user or maintainer action.

## No endorsement

Use of a vendor name identifies interoperability only. No vendor, project or
OpenAI endorsement is claimed or implied.
