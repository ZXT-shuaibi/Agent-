import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "markdown_to_pdf.py"


class OutputSchemaTest(unittest.TestCase):
    def test_reference_schema_mentions_required_handoff_fields(self):
        text = (ROOT / "references" / "output-schema.md").read_text(encoding="utf-8")
        for field in (
            "candidate_patterns",
            "evidence",
            "已有能力",
            "建议改造",
            "不可写成已完成",
            "carrier_mapping",
            "target_business",
        ):
            self.assertIn(field, text)
        payload = {
            "candidate_patterns": [],
            "evidence": [],
            "已有能力": [],
            "建议改造": [],
            "不可写成已完成": [],
            "carrier_mapping": [],
            "target_business": "",
        }
        self.assertIn("candidate_patterns", json.dumps(payload, ensure_ascii=False))

    def test_unknown_renderer_returns_clear_nonzero_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "report.md"
            target = Path(temp_dir) / "report.pdf"
            source.write_text("# report\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(source),
                    "--output",
                    str(target),
                    "--renderer",
                    "missing-renderer",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("renderer", result.stderr.lower())
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
