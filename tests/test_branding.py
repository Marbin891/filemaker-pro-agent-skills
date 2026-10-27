"""Branding, distribution and final-review regression tests. No live host calls."""
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build
import generate_assets
import install_codex
import lint_examples
import validate

try:
    from PIL import Image
except ImportError:
    Image = None


class BrandingStructureTests(unittest.TestCase):
    def test_master_is_unchanged(self):
        raw = (ROOT / "assets/logo.png").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), generate_assets.MASTER_SHA256)

    def test_png_structure_and_limits(self):
        for name, size in generate_assets.VARIANTS.items():
            validate.validate_png((ROOT / "assets" / name).read_bytes(), size)

    def test_corrupt_png_is_rejected(self):
        data = bytearray((ROOT / "assets/icon-128.png").read_bytes())
        data[50] ^= 1
        with self.assertRaises(ValueError):
            validate.validate_png(bytes(data), 128)

    def test_wrong_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            validate.validate_png((ROOT / "assets/logo-512.png").read_bytes(), 128)

    def test_readmes_use_the_same_project_identity(self):
        for name in ("README.md", "README.es.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('src="assets/logo-512.png"', text)
            self.assertIn('width="128" height="128"', text)

    def test_plugin_contains_only_required_variants(self):
        build.build(verbose=False)
        with zipfile.ZipFile(ROOT / "dist/plugin.zip") as archive:
            assets = {name for name in archive.namelist() if name.startswith("assets/")}
            self.assertEqual(assets, set(build.PLUGIN_ASSETS))
            interface = json.loads(archive.read("plugin.json"))["extensions"]["com.openai"]["interface"]
            for key, size in (("logo", 512), ("composerIcon", 128)):
                validate.validate_png(archive.read(interface[key][2:]), size)
            self.assertNotIn("assets/logo.png", archive.namelist())

    def test_installed_plugin_copies_visual_resources(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = install_codex.install_plugin(Path(temporary).resolve())
            for relative in build.PLUGIN_ASSETS:
                self.assertEqual((target / relative).read_bytes(), (ROOT / relative).read_bytes())

    def test_standalone_skills_do_not_depend_on_plugin_icons(self):
        for name in build.SKILLS:
            files = build.prepare_skill(name)
            self.assertFalse(any(p.startswith("assets/") for p in files))
            self.assertNotIn("../../assets", files["agents/openai.yaml"].decode())


@unittest.skipUnless(Image is not None, "Pillow is a development dependency; install requirements-dev.txt")
class BrandingPixelTests(unittest.TestCase):
    def test_lanczos_pixels_match_the_master(self):
        generate_assets.generate(check=True)

    def test_variants_are_decodable_rgba_without_metadata(self):
        for name, size in generate_assets.VARIANTS.items():
            with Image.open(ROOT / "assets" / name) as image:
                image.verify()
            with Image.open(ROOT / "assets" / name) as image:
                self.assertEqual(image.size, (size, size))
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.getchannel("A").getextrema(), (0, 255))
                self.assertFalse(image.info)

    def test_square_padding_does_not_stretch_or_crop(self):
        source = Image.new("RGBA", (100, 50), (0, 80, 200, 255))
        result = generate_assets.resize(source, 128)
        self.assertEqual(result.size, (128, 128))
        self.assertEqual(result.getchannel("A").getbbox(), (0, 32, 128, 96))

    def test_48px_preview_is_derived_from_the_composer_icon(self):
        with Image.open(ROOT / "assets/icon-128.png") as image:
            icon = image.resize((48, 48), Image.Resampling.LANCZOS)
            self.assertEqual(icon.size, (48, 48))
            alpha = icon.getchannel("A")
            self.assertEqual(alpha.getextrema(), (0, 255))
            # Objective coverage check only; recognizability is a visual review.
            self.assertGreater(sum(v >= 128 for v in alpha.getdata()), 1000)


class FinalReviewRegressionTests(unittest.TestCase):
    def test_builder_preflights_before_overwriting_notices(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "dist").mkdir()
            (root / "outside").mkdir()
            (root / "LICENSE").write_text("sentinel")
            try:
                (root / "filemaker-pro").symlink_to(root / "outside", target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable")
            with patch.object(build, "ROOT", root), patch.object(build, "DIST", root / "dist"):
                with self.assertRaises(ValueError):
                    build.build(False)
            self.assertEqual((root / "LICENSE").read_text(), "sentinel")
            self.assertEqual(list((root / "outside").iterdir()), [])

    def test_marketplace_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "marketplace.json"
            for relative in ("../elsewhere", "./plugins/../../elsewhere", "C:\\plugins"):
                with self.assertRaises(ValueError):
                    install_codex.register_marketplace(path, relative)
            self.assertFalse(path.exists())

    def test_linter_rejects_unknown_plugin_function(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            path = Path(temporary) / "case.md"
            path.write_text('```filemaker\nBE_FileWrite ( "path" ; "text" )\n```\n')
            with patch.object(lint_examples, "example_paths", return_value=[path]):
                self.assertEqual(lint_examples.scan()["status"], "REVIEW")

    def test_linter_rejects_missing_smtp_arguments(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            path = Path(temporary) / "case.md"
            path.write_text('```filemaker\nBE_SMTPSend ( "body-only" )\n```\n')
            with patch.object(lint_examples, "example_paths", return_value=[path]):
                self.assertTrue(lint_examples.scan()["argument_count_issues"])

    def test_mbs_lookup_normalizes_component_case(self):
        result = subprocess.run([sys.executable, str(ROOT / "monkeybread-mbs-plugin/scripts/catalog.py"),
                                 "function", " dialog.setmessage "], text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["entry"]["name"], "Dialog.SetMessage")


if __name__ == "__main__":
    unittest.main()
