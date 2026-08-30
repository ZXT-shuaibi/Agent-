#!/usr/bin/env python3
"""Clone candidate repositories and record a verifiable local manifest."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname


SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
MAX_FILES = 300


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _local_source(repo: str) -> Path | None:
    parsed = urlparse(repo)
    if parsed.scheme == "file":
        value = url2pathname(unquote(parsed.path))
        if len(value) >= 3 and value[0] == "/" and value[2] == ":":
            value = value[1:]
        return Path(value)
    if parsed.scheme:
        return None
    path = Path(repo)
    return path if path.exists() else None


def _safe_name(repo: str, source: Path | None) -> str:
    if source:
        return source.name or "repository"
    parsed = urlparse(repo)
    name = Path(parsed.path.rstrip("/")).name or "repository"
    return name[:-4] if name.endswith(".git") else name


def _destination(base: Path, name: str) -> Path:
    candidate = base / name
    index = 2
    while candidate.exists():
        candidate = base / f"{name}-{index}"
        index += 1
    return candidate


def _inventory(root: Path) -> list[str]:
    entries: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        entries.append(path.relative_to(root).as_posix())
        if len(entries) >= MAX_FILES:
            break
    return entries


def _git_commit(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def clone_one(repo: str, output_dir: Path) -> dict:
    source = _local_source(repo)
    name = _safe_name(repo, source)
    destination = _destination(output_dir, name)
    record = {
        "source": repo,
        "name": name,
        "status": "failed",
        "local_path": str(destination),
        "commit": None,
        "files": [],
        "error": None,
    }
    try:
        if source:
            if not source.is_dir():
                raise FileNotFoundError(f"local source is not a directory: {source}")
            shutil.copytree(source, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo, str(destination)],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            if result.returncode != 0:
                record["error"] = (result.stderr or result.stdout).strip()[-1000:]
                return record
        record["status"] = "cloned"
        record["commit"] = _git_commit(destination)
        record["files"] = _inventory(destination)
        return record
    except (OSError, subprocess.SubprocessError) as exc:
        record["error"] = str(exc)
        return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", default=[])
    parser.add_argument("--repo-file", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    repos = list(args.repo)
    if args.repo_file:
        repos.extend(line.strip() for line in args.repo_file.read_text(encoding="utf-8").splitlines() if line.strip())
    if not repos:
        parser.error("provide --repo or --repo-file")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = [clone_one(repo, args.output_dir) for repo in repos]
    payload = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "repositories": records,
        "verified_count": sum(record["status"] == "cloned" for record in records),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
