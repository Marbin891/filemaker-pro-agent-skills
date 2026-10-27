# Project identity

`logo.png` is the unmodified RGBA PNG master (1254 × 1254). The identity belongs
to this project, not Claris, FileMaker, Goya, Monkeybread Software or Beezwax.
No third-party logo or endorsement is implied.

| File | Use | Distributed in plugin |
|---|---|---|
| `logo.png` | Original master; never overwritten | No |
| `logo-512.png` | Plugin listing, GitHub/README display | Yes |
| `icon-128.png` | Plugin composer icon | Yes |

Generate using `python scripts/generate_assets.py` after installing
`requirements-dev.txt`. Both derivatives are RGBA PNGs, resized directly from
the master with Lanczos, without recolouring, cropping or stretching. A
non-square replacement would receive transparent padding. No JPEG conversion,
palette reduction or alternate design is used.

`--check` compares dimensions, RGBA mode and exact decoded pixels to a fresh
Lanczos render. `--preview /path/to/preview.png` creates a review sheet at 48px
on light and dark backgrounds. Preview sheets are not distributed.

The artwork was supplied as project identity without separate author or licence
metadata. The documentation/code CC BY 4.0 notice does not independently grant
artwork rights; confirm artwork redistribution rights before public release.
