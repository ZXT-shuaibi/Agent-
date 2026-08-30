#!/usr/bin/env python3
"""Build a bian-intern-style standalone Agent plugin archive."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


PLUGIN_NAME = "agent-intern-miner"
PLUGIN_PARTS = (".codex-plugin", "agents", "profiles", "references", "scripts", "skills")


def _ignore_generated(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name == "__pycache__" or name.endswith((".pyc", ".pyo"))
    }


def _standalone_readme(plugin_readme: str) -> str:
    marker = (
        "本目录是插件本体，仓库根目录是可直接从 GitHub 安装的 marketplace。"
        "新电脑优先执行根目录 [README](../../README.md) 中的 GitHub 安装命令；"
        "下面保留插件的完整使用说明和本地 marketplace 安装方式。"
    )
    replacement = (
        "这是从 GitHub 或压缩包获取的独立插件目录。Codex 推荐使用仓库根目录的 "
        "marketplace 安装命令；支持插件目录的其他平台可以直接读取本目录。"
        "压缩包同时包含 `.codex-plugin` 和兼容 Claude Code 的 `.claude-plugin` manifest。"
    )
    return plugin_readme.replace(marker, replacement)


def build_archive(repo_root: Path, output: Path) -> Path:
    plugin_root = repo_root / "plugins" / PLUGIN_NAME
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"plugin manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"{PLUGIN_NAME}-") as temp_dir:
        stage_root = Path(temp_dir) / PLUGIN_NAME
        stage_root.mkdir()

        for part in PLUGIN_PARTS:
            source = plugin_root / part
            if not source.exists():
                raise FileNotFoundError(f"plugin directory is missing: {source}")
            shutil.copytree(source, stage_root / part, ignore=_ignore_generated)

        readme = (plugin_root / "README.md").read_text(encoding="utf-8")
        (stage_root / "README.md").write_text(
            _standalone_readme(readme), encoding="utf-8", newline="\n"
        )

        # Claude Code uses a separate manifest name; keep it derived from the
        # canonical Codex manifest so metadata cannot drift between packages.
        claude_manifest = {
            key: manifest[key]
            for key in ("name", "version", "description", "author", "license", "skills")
            if key in manifest
        }
        claude_root = stage_root / ".claude-plugin"
        claude_root.mkdir()
        (claude_root / "plugin.json").write_text(
            json.dumps(claude_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        if output.exists():
            output.unlink()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage_root.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(Path(temp_dir)).as_posix())

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository containing plugins/agent-intern-miner (default: script repository)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="output .zip path",
    )
    args = parser.parse_args()
    archive = build_archive(args.repo_root.resolve(), args.output)
    print(f"Built standalone plugin archive: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
