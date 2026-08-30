import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills"


class AgentSkillRuleTest(unittest.TestCase):
    def test_scan_requires_real_source_and_concise_explanation(self):
        text = (SKILL_DIR / "agent-chain-scan" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "扫描器只负责定位候选",
            "真实源码正文",
            "不得只根据类名",
            "证据附录",
        ):
            self.assertIn(phrase, text)

    def test_project_selection_is_chain_first_and_carrier_aware(self):
        text = (SKILL_DIR / "agent-project-select" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "经历承载项目",
            "曼弗实习",
            "链路嵌入点",
            "业务承载自然度",
            "高饱和",
            "链路迁移到曼弗业务",
            "链路能力卡",
            "选择理由",
            "淘汰理由",
            "源码嵌入点",
        ):
            self.assertIn(phrase, text)

    def test_packaging_skill_contains_evidence_and_no_claim_boundary(self):
        text = (SKILL_DIR / "agent-package" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("[源码证据]", "[建议改造]", "[不可写成已完成]", "方案演进", "30 秒"):
            self.assertIn(phrase, text)

    def test_grill_covers_agent_failure_dimensions(self):
        text = (SKILL_DIR / "agent-grill" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("checkpoint", "幂等", "评测", "记忆", "成本", "提示词注入", "🔴"):
            self.assertIn(phrase, text)

    def test_self_check_has_interview_length_and_provenance_gates(self):
        text = (SKILL_DIR / "agent-self-check" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("来源", "五个", "30 秒", "2 分钟", "角色真实性"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
