import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "agent-intern",
    "agent-chain-scan",
    "agent-chain-extract",
    "agent-project-select",
    "agent-package",
    "agent-grill",
    "agent-self-check",
)
REFERENCES = (
    "high-value-agent-chains.md",
    "business-carrier-scenarios.md",
    "evidence-first-explanation.md",
    "evidence-protocol.md",
    "github-research.md",
    "output-schema.md",
    "dynamic-rule-update.md",
)
SCRIPTS = (
    "scan_agent_repo.py",
    "search_github_candidates.py",
    "pull_github_repos.py",
    "markdown_to_pdf.py",
)


class PluginStructureTest(unittest.TestCase):
    DISPLAY_NAMES = {
        "agent-intern": "Agent 实习挖掘总入口",
        "agent-chain-scan": "Agent 源码链路扫描",
        "agent-chain-extract": "Agent 口述链路提取",
        "agent-project-select": "GitHub Agent 项目筛选",
        "agent-package": "Agent 项目/实习包装",
        "agent-grill": "Agent 面试拷打",
        "agent-self-check": "Agent 质量门禁",
    }

    def test_required_paths_and_manifest(self):
        manifest_path = ROOT / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "agent-intern-miner")
        self.assertEqual(manifest["skills"], "./skills")
        for name in SKILLS:
            self.assertTrue((ROOT / "skills" / name / "SKILL.md").exists(), name)
        for name in REFERENCES:
            self.assertTrue((ROOT / "references" / name).exists(), name)
        for name in SCRIPTS:
            self.assertTrue((ROOT / "scripts" / name).exists(), name)

    def test_skill_frontmatter_and_no_scaffold_placeholders(self):
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            frontmatter = text.split("---\n", 2)[1]
            self.assertIn("name:", frontmatter, path)
            self.assertIn("description: Use when", frontmatter, path)
        for path in ROOT.rglob("*"):
            if "tests" in path.parts:
                continue
            if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".py"}:
                self.assertNotIn("[TODO:", path.read_text(encoding="utf-8"), path)

    def test_each_skill_exposes_chinese_name_and_usage_contract(self):
        interface = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("Agent 实习链路挖掘", interface)
        for skill_id, display_name in self.DISPLAY_NAMES.items():
            text = (ROOT / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(display_name, text, skill_id)
            for section in ("作用", "输入", "输出", "何时使用", "怎么用"):
                self.assertIn(section, text, f"{skill_id} missing {section}")

    def test_readme_documents_codex_and_portable_installation(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "安装到 Codex",
            "codex plugin marketplace add",
            "codex plugin add",
            "其他平台使用",
            "完整使用流程",
            "渐进式披露",
            "新建任务",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
