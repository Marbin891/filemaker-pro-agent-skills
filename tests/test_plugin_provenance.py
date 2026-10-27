"""Reproduce plugin catalog transformations from pinned local clones when available."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = Path(os.environ.get("CADENCEUX_SOURCES", ROOT.parent / "sources"))
sys.path.insert(0, str(ROOT / "scripts"))
import import_plugin_catalogs as importer


@unittest.skipUnless(SOURCES.is_dir(), "Reviewed CadenceUX clones are not present")
class PluginProvenanceTests(unittest.TestCase):
    def test_baseelements_matches_pinned_transform(self):
        source = SOURCES / "goya-be-plugin-skill/references/function-catalog.json"
        current = json.loads((ROOT / "goya-be-plugin/references/function-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(current, importer.be_catalog(source))

    def test_bbox_matches_pinned_transform(self):
        source = SOURCES / "beezwax-bbox-plugin-skill/references/function-catalog.json"
        current = json.loads((ROOT / "beezwax-bbox-plugin/references/function-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(current, importer.bbox_catalog(source))

    def test_mbs_matches_pinned_transform(self):
        with tempfile.TemporaryDirectory() as temporary:
            total, components = importer.mbs_catalog(SOURCES / "monkeybread-mbs-plugin-skill", Path(temporary))
            self.assertEqual((total, components), (7859, 245))
            current = json.loads((ROOT / "monkeybread-mbs-plugin/references/index.json").read_text(encoding="utf-8"))
            generated = json.loads((Path(temporary) / "references/index.json").read_text(encoding="utf-8"))
            self.assertEqual(current, generated)
            for path in sorted((ROOT / "monkeybread-mbs-plugin/references").glob("group-*.json")):
                self.assertEqual(path.read_bytes(), (Path(temporary) / "references" / path.name).read_bytes())


if __name__ == "__main__":
    unittest.main()
