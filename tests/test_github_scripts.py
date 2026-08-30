import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures"
SEARCH_SCRIPT = ROOT / "scripts" / "search_github_candidates.py"
PULL_SCRIPT = ROOT / "scripts" / "pull_github_repos.py"


class GithubScriptTest(unittest.TestCase):
    def test_search_fixture_deduplicates_and_scores_engineering(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SEARCH_SCRIPT),
                "--fixture",
                str(FIXTURE / "github_search.json"),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        candidates = payload["candidates"]
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0]["name"], "durable-support-agent")
        self.assertIn("readme_probe", candidates[0])
        self.assertIn("engineering_signals", candidates[0])
        self.assertTrue(any("single" in c["risk_flags"] for c in candidates))

    def test_pull_local_fixture_records_clone_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "clones"
            manifest_path = Path(temp_dir) / "manifest.json"
            source = (FIXTURE / "github_source_repo").resolve().as_uri()
            result = subprocess.run(
                [
                    sys.executable,
                    str(PULL_SCRIPT),
                    "--repo",
                    source,
                    "--output-dir",
                    str(output_dir),
                    "--manifest",
                    str(manifest_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["repositories"][0]["status"], "cloned")
            self.assertTrue(manifest["repositories"][0]["files"])

    def test_pull_failure_is_recorded_without_false_verification(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "manifest.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(PULL_SCRIPT),
                    "--repo",
                    "https://github.com/example/does-not-exist-agent.git",
                    "--output-dir",
                    str(Path(temp_dir) / "clones"),
                    "--manifest",
                    str(manifest_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertNotEqual(manifest["repositories"][0]["status"], "cloned")


if __name__ == "__main__":
    unittest.main()
