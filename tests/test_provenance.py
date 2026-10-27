"""Exercise pinned-Git-object verification without network or global Git configuration."""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_provenance import verify_repo


@unittest.skipUnless(shutil.which("git"), "Local Git is needed for provenance fixture tests")
class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name).resolve()
        self.git("init", "--quiet")
        (self.repo / "facts.json").write_bytes(b'{"fact": 7}\n')
        self.git("add", "facts.json")
        self.git("-c", "user.name=Test Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={self.repo / 'hooks-disabled'}",
                 "commit", "--quiet", "-m", "Synthetic local test fixture")
        self.pin = self.git("rev-parse", "HEAD").strip()
        self.records = [{"path": "facts.json", "sha256": hashlib.sha256((self.repo / "facts.json").read_bytes()).hexdigest()}]

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True, stderr=subprocess.PIPE)

    def test_exact_pinned_object_passes(self):
        verify_repo(self.repo, self.pin, self.records)

    def test_modified_source_and_matching_inventory_still_rejected(self):
        (self.repo / "facts.json").write_bytes(b'{"fact": 999}\n')
        self.records[0]["sha256"] = hashlib.sha256((self.repo / "facts.json").read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            verify_repo(self.repo, self.pin, self.records)

    def test_missing_inventory_file_rejected(self):
        with self.assertRaises(ValueError):
            verify_repo(self.repo, self.pin, [])

    def test_forged_inventory_hash_rejected(self):
        self.records[0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_repo(self.repo, self.pin, self.records)

    def test_unexpected_pin_rejected(self):
        with self.assertRaises(ValueError):
            verify_repo(self.repo, "0" * 40, self.records)


if __name__ == "__main__":
    unittest.main()
