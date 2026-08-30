# GitHub Marketplace Install Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the GitHub repository itself a Codex marketplace so another computer can install the Agent plugin directly from `ZXT-shuaibi/Agent-`.

**Architecture:** Keep the existing plugin unchanged under `plugins/agent-intern-miner/`. Add a repository-root `marketplace.json` whose plugin source is `./plugins/agent-intern-miner`. Put marketplace-level installation instructions in the root README and keep plugin-specific documentation inside the plugin directory.

**Tech Stack:** Codex plugin manifest JSON, Codex marketplace JSON, Markdown, Python `unittest`, Git.

---

### Task 1: Create the repository marketplace layout

**Files:**
- Create: `marketplace.json`
- Move: `.codex-plugin/`, `agents/`, `profiles/`, `references/`, `scripts/`, `skills/`, `tests/` into `plugins/agent-intern-miner/`
- Keep: `.gitignore` at repository root; move the existing plugin README to `plugins/agent-intern-miner/README.md` and create a new marketplace README at the repository root

- [x] **Step 1: Add the marketplace manifest**

Create `marketplace.json` with marketplace name `agent-intern-github`, display name `Agent 实习链路工作台`, and one `agent-intern-miner` entry using source path `./plugins/agent-intern-miner`, installation policy `AVAILABLE`, authentication policy `ON_INSTALL`, and category `Education`.

- [x] **Step 2: Move the plugin files**

Move the existing plugin directories and files under `plugins/agent-intern-miner/`, preserving their relative paths so links from each skill continue to resolve from the plugin root.

- [x] **Step 3: Check the staged tree**

Run `git status --short` and confirm that the only structural changes are the marketplace manifest, the root README, and the plugin subtree move.

### Task 2: Update documentation and contracts

**Files:**
- Modify: `README.md`
- Modify: `plugins/agent-intern-miner/README.md`
- Modify: `plugins/agent-intern-miner/tests/test_plugin_structure.py`
- Modify: `plugins/agent-intern-miner/tests/test_reference_contracts.py`
- Create: `plugins/agent-intern-miner/tests/test_marketplace.py`

- [x] **Step 1: Document direct GitHub installation**

Make the root README explain that the repository is a Git marketplace and show exactly:

```powershell
codex plugin marketplace add ZXT-shuaibi/Agent- --ref main
codex plugin add agent-intern-miner@agent-intern-github
codex plugin list --marketplace agent-intern-github
```

Keep plugin usage, evidence rules, and module descriptions in the nested plugin README.

- [x] **Step 2: Add marketplace tests**

Test that `marketplace.json` has the expected name, plugin name, relative source path, installation policy, authentication policy, and category. Test that the referenced plugin manifest exists and has the same plugin name.

- [x] **Step 3: Adjust existing test root resolution**

Change tests that use `Path(__file__).resolve().parents[1]` so their root resolves to `plugins/agent-intern-miner`; do not change assertions about plugin behavior.

### Task 3: Validate the installable repository

**Files:**
- Read: `marketplace.json`
- Read: `plugins/agent-intern-miner/.codex-plugin/plugin.json`
- Test: `plugins/agent-intern-miner/tests/`

- [x] **Step 1: Run the Python test suite**

Run `python -m unittest discover -s plugins/agent-intern-miner/tests -v`. Expected result: all tests pass.

- [x] **Step 2: Validate marketplace paths**

Run a Python JSON check that loads `marketplace.json`, resolves `plugins[0].source.path` from the repository root, and asserts that both the plugin manifest and all seven skill `SKILL.md` files exist.

- [x] **Step 3: Validate direct CLI discovery when available**

The repository was validated structurally against the Codex marketplace schema. Direct CLI discovery was not run because the CLI has no dry-run/config-path option and would mutate the user's default plugin configuration; the same commands are documented in the root README for explicit user execution.

### Task 4: Commit the packaging change

**Files:**
- Commit all files from Tasks 1–3.

- [ ] **Step 1: Review the diff**

Run `git diff --stat` and verify no `__pycache__`, `.pyc`, local clone, or generated scan output is included.

- [ ] **Step 2: Commit**

Run `git add -A` followed by `git commit -m "Make repository directly installable as Codex marketplace"`.

- [ ] **Step 3: Report the push command**

Run `git status --short --branch` and report `git push origin main` as the only remaining remote action if the environment cannot authenticate to GitHub.
