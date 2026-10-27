#!/usr/bin/env python3
"""Derive project icons from the unchanged PNG master using RGBA Lanczos.

Requires requirements-dev.txt, never used by installed skills. No network.
--check compares decoded pixels, independent of PNG compressor versions.
--preview writes a 48px review sheet to an explicit path, not to the package.
"""
import argparse
import hashlib
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = {"logo-512.png": 512, "icon-128.png": 128}
MASTER_SHA256 = "705d01e7034e8c56938759b50d006b4fbb3f0aaeec916e5d346a3ef3c22afb67"


def resize(image, size):
    from PIL import Image
    # Pad, never crop or stretch. RGBA resizing uses premultiplied alpha in
    # Pillow, avoiding dark halos at transparent edges.
    ratio = min(size / image.width, size / image.height)
    dimensions = (max(1, round(image.width * ratio)), max(1, round(image.height * ratio)))
    scaled = image.convert("RGBA").resize(dimensions, Image.Resampling.LANCZOS)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(scaled, ((size - dimensions[0]) // 2, (size - dimensions[1]) // 2))
    return result


def safe_destination(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError(f"Refusing symlink destination: {candidate}")


def generate(check=False, preview=None):
    from PIL import Image
    master = ROOT / "assets/logo.png"
    raw = master.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MASTER_SHA256:
        raise ValueError("Master differs from the reviewed PNG; review a replacement before changing the pin")
    with Image.open(io.BytesIO(raw)) as original:
        original.load()
        if original.format != "PNG" or original.mode != "RGBA":
            raise ValueError("Expected the original RGBA PNG master")
        for name, size in VARIANTS.items():
            expected = resize(original, size)
            path = ROOT / "assets" / name
            safe_destination(path)
            if check:
                with Image.open(path) as current:
                    current.load()
                    if current.mode != "RGBA" or current.size != expected.size or current.tobytes() != expected.tobytes():
                        raise ValueError(f"Generated pixels differ: {name}")
            else:
                # New image: strips textual, EXIF and other incidental metadata.
                expected.save(path, format="PNG", optimize=True, compress_level=9)
        if preview:
            path = Path(preview).absolute()
            safe_destination(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            icon = resize(original, 128).resize((48, 48), Image.Resampling.LANCZOS)
            # Actual 48px render on both backgrounds plus enlarged review views.
            sheet = Image.new("RGB", (384, 240), "white")
            for x, color in ((0, "#ffffff"), (192, "#18202c")):
                panel = Image.new("RGBA", (192, 240), color)
                panel.alpha_composite(icon, (72, 12))
                panel.alpha_composite(icon.resize((144, 144), Image.Resampling.NEAREST), (24, 84))
                sheet.paste(panel.convert("RGB"), (x, 0))
            sheet.save(path, format="PNG", optimize=True)
    return "PASS: Lanczos variants match the unchanged RGBA master" if check else "Generated 512px logo and 128px composer icon"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    print(generate(args.check, args.preview))


if __name__ == "__main__":
    main()
