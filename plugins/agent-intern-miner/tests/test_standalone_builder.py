import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_standalone_plugin.py"


class StandaloneBuilderTest(unittest.TestCase):
    def test_builds_dual_manifest_archive_without_generated_caches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "agent-intern-plugin.zip"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BUILD_SCRIPT),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())

            self.assertIn("agent-intern-miner/.codex-plugin/plugin.json", names)
            self.assertIn("agent-intern-miner/.claude-plugin/plugin.json", names)
            self.assertIn("agent-intern-miner/skills/agent-intern/SKILL.md", names)
            self.assertIn("agent-intern-miner/references/evidence-protocol.md", names)
            self.assertNotIn("agent-intern-miner/tests/test_manifest.py", names)
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))


if __name__ == "__main__":
    unittest.main()
