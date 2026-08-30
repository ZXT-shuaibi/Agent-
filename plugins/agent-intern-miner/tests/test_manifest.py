import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ManifestTest(unittest.TestCase):
    def test_manifest_matches_expected_identity(self):
        manifest_path = ROOT / ".codex-plugin" / "plugin.json"
        expected_path = ROOT / "tests" / "expected_manifest.json"
        self.assertTrue(manifest_path.exists(), "plugin.json is missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        for key, value in expected.items():
            self.assertEqual(manifest.get(key), value, key)

    def test_manifest_does_not_reference_java_plugin(self):
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("bian-intern", manifest.get("name", ""))


if __name__ == "__main__":
    unittest.main()
