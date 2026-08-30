import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "agent_repo"
SCRIPT = ROOT / "scripts" / "scan_agent_repo.py"


class AgentScannerTest(unittest.TestCase):
    def test_detects_agent_frameworks_and_evidence(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURE), "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn("langgraph", report["frameworks"])
        self.assertIn("celery", report["frameworks"])
        self.assertTrue(any(item["kind"] == "orchestration" for item in report["evidence"]))
        self.assertTrue(any(item["kind"] == "tool" for item in report["evidence"]))
        self.assertTrue(any(item["kind"] == "evaluation" for item in report["evidence"]))
        self.assertIn("candidate_patterns", report)

    def test_missing_root_is_a_nonzero_error(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(ROOT / "does-not-exist"), "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
