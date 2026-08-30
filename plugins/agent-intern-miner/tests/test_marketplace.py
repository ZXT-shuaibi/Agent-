import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "agent-intern-miner"


class MarketplaceTest(unittest.TestCase):
    def test_marketplace_registers_the_plugin_with_relative_source(self):
        marketplace = json.loads(
            (REPO_ROOT / "marketplace.json").read_text(encoding="utf-8")
        )

        self.assertEqual(marketplace["name"], "agent-intern-github")
        self.assertEqual(len(marketplace["plugins"]), 1)

        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "agent-intern-miner")
        self.assertEqual(entry["source"], {
            "source": "local",
            "path": "./plugins/agent-intern-miner",
        })
        self.assertEqual(entry["policy"], {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        })
        self.assertEqual(entry["category"], "Education")

    def test_marketplace_source_contains_the_plugin_manifest_and_skills(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["name"], "agent-intern-miner")
        self.assertEqual(manifest["version"], "1.2.0")

        skill_dirs = [
            path for path in (PLUGIN_ROOT / "skills").iterdir() if path.is_dir()
        ]
        self.assertEqual(len(skill_dirs), 7)
        self.assertTrue(all((path / "SKILL.md").exists() for path in skill_dirs))


if __name__ == "__main__":
    unittest.main()
