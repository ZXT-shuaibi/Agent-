import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_NAMES = [
    "high-value-agent-chains.md",
    "business-carrier-scenarios.md",
    "evidence-first-explanation.md",
    "evidence-protocol.md",
    "github-research.md",
    "output-schema.md",
    "dynamic-rule-update.md",
]


class ReferenceContractTest(unittest.TestCase):
    def test_all_references_exist(self):
        for name in REFERENCE_NAMES:
            self.assertTrue((ROOT / "references" / name).exists(), name)

    def test_evidence_labels_and_dynamic_fields_are_documented(self):
        text = "\n".join(
            (ROOT / "references" / name).read_text(encoding="utf-8")
            for name in REFERENCE_NAMES
            if (ROOT / "references" / name).exists()
        )
        for label in ("[用户事实]", "[源码证据]", "[公开资料]", "[建议改造]", "[不可写成已完成]"):
            self.assertIn(label, text)
        for level in ("S 级", "A 级", "B 级"):
            self.assertIn(level, text)
        self.assertIn("candidate_patterns", text)
        self.assertIn("rule_update_proposal", text)

    def test_business_carrier_reference_defines_novelty_and_fit_gates(self):
        text = (ROOT / "references" / "business-carrier-scenarios.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "经历承载项目",
            "业务对象",
            "生命周期",
            "链路嵌入点",
            "高饱和",
            "合规证据链",
            "指标口径治理",
        ):
            self.assertIn(phrase, text)

    def test_evidence_first_explanation_separates_proof_from_narrative(self):
        text = (ROOT / "references" / "evidence-first-explanation.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "扫描器只负责定位候选",
            "真实源码正文",
            "不得只根据类名",
            "主文",
            "证据附录",
            "证据 ID",
            "不大量堆叠代码",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
