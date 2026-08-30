#!/usr/bin/env python3
"""Static, execution-free scanner for Python/Agent repositories."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "site-packages",
    "dist",
    "build",
}
SOURCE_SUFFIXES = {".py", ".json", ".yaml", ".yml", ".toml", ".txt", ".md"}
FRAMEWORK_PATTERNS = {
    "fastapi": ("fastapi",),
    "flask": ("flask",),
    "django": ("django",),
    "langgraph": ("langgraph", "stategraph"),
    "langchain": ("langchain", "langchain_core"),
    "crewai": ("crewai",),
    "autogen": ("autogen", "microsoft.autogen"),
    "mcp": ("modelcontextprotocol", "fastmcp", "mcp.server"),
    "celery": ("celery",),
    "rq": ("redis.queue", "rq"),
    "arq": ("arq",),
    "temporal": ("temporalio", "temporal"),
    "prefect": ("prefect",),
    "airflow": ("airflow",),
    "qdrant": ("qdrant",),
    "chroma": ("chromadb", "chroma"),
    "weaviate": ("weaviate",),
    "pinecone": ("pinecone",),
    "langfuse": ("langfuse",),
    "langsmith": ("langsmith",),
    "phoenix": ("arize", "phoenix"),
    "opentelemetry": ("opentelemetry",),
}
MAX_FILE_BYTES = 500_000
MAX_EVIDENCE_PER_KIND = 20


def discover_files(root: Path) -> list[Path]:
    """Return bounded, source-like files while skipping generated/dependency trees."""
    if not root.is_dir():
        raise FileNotFoundError(f"repository root is not a directory: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size <= MAX_FILE_BYTES:
                files.append(path)
        except OSError:
            continue
    return sorted(files)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:MAX_FILE_BYTES]
    except OSError:
        return ""


def detect_frameworks(files: list[Path]) -> list[str]:
    found: set[str] = set()
    for path in files:
        text = _read_text(path).lower()
        for name, patterns in FRAMEWORK_PATTERNS.items():
            if any(pattern in text for pattern in patterns):
                found.add(name)
    return sorted(found)


def _decorator_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _decorator_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _call_name(node: ast.Call) -> str:
    return _decorator_name(node.func)


def _excerpt(lines: list[str], line: int) -> str:
    if not lines or line < 1 or line > len(lines):
        return ""
    return " ".join(lines[line - 1].strip().split())[:240]


def _add_evidence(
    evidence: list[dict],
    counts: dict[str, int],
    root: Path,
    path: Path,
    line: int,
    symbol: str,
    kind: str,
    excerpt: str,
    confidence: float = 0.8,
) -> None:
    if counts[kind] >= MAX_EVIDENCE_PER_KIND:
        return
    counts[kind] += 1
    evidence.append(
        {
            "id": f"E{len(evidence) + 1}",
            "path": path.relative_to(root).as_posix(),
            "line": line or 1,
            "symbol": symbol or "<module>",
            "kind": kind,
            "excerpt": excerpt,
            "confidence": round(confidence, 2),
        }
    )


def _module_names(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name.lower() for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.lower()


def _scan_python_file(
    root: Path, path: Path, evidence: list[dict], counts: dict[str, int]
) -> None:
    text = _read_text(path)
    lines = text.splitlines()
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return

    modules = set(_module_names(tree))
    if modules.intersection({"fastapi", "flask", "django"}):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators = {_decorator_name(d).lower() for d in node.decorator_list}
                if any(
                    name.endswith((".get", ".post", ".put", ".patch", ".delete", ".websocket"))
                    or name in {"app.route", "route"}
                    for name in decorators
                ):
                    _add_evidence(
                        evidence,
                        counts,
                        root,
                        path,
                        node.lineno,
                        node.name,
                        "entrypoint",
                        _excerpt(lines, node.lineno),
                    )

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = {_decorator_name(d).lower() for d in node.decorator_list}
            if "tool" in decorators or any(name.endswith(".tool") for name in decorators):
                _add_evidence(
                    evidence,
                    counts,
                    root,
                    path,
                    node.lineno,
                    node.name,
                    "tool",
                    _excerpt(lines, node.lineno),
                )
            if any(name.endswith(".task") or name == "task" for name in decorators):
                _add_evidence(
                    evidence,
                    counts,
                    root,
                    path,
                    node.lineno,
                    node.name,
                    "long_running",
                    _excerpt(lines, node.lineno),
                )
            if node.name == "main" or any(
                isinstance(child, ast.If)
                and isinstance(child.test, ast.Compare)
                for child in node.body
            ):
                _add_evidence(
                    evidence,
                    counts,
                    root,
                    path,
                    node.lineno,
                    node.name,
                    "entrypoint",
                    _excerpt(lines, node.lineno),
                    0.65,
                )

        if isinstance(node, ast.Call):
            name = _call_name(node).lower()
            if name.endswith("stategraph") or name.endswith(".add_node"):
                _add_evidence(
                    evidence,
                    counts,
                    root,
                    path,
                    node.lineno,
                    name,
                    "orchestration",
                    _excerpt(lines, node.lineno),
                )
            elif name.endswith(".compile") and any(
                keyword.arg in {"checkpointer", "checkpoint", "store"}
                for keyword in node.keywords
            ):
                _add_evidence(
                    evidence,
                    counts,
                    root,
                    path,
                    node.lineno,
                    name,
                    "persistence",
                    _excerpt(lines, node.lineno),
                )
            elif any(
                token in name
                for token in ("retry", "backoff", "circuit", "idempot", "timeout")
            ):
                _add_evidence(
                    evidence,
                    counts,
                    root,
                    path,
                    node.lineno,
                    name,
                    "reliability",
                    _excerpt(lines, node.lineno),
                    0.7,
                )

    lower = text.lower()
    if "stategraph" in lower or ".add_node(" in lower or "workflow.compile(" in lower:
        _add_evidence(
            evidence,
            counts,
            root,
            path,
            1,
            "<module>",
            "orchestration",
            "graph/workflow construction detected",
            0.75,
        )
    if any(token in lower for token in ("autoretry_for", "retry_backoff", "max_retries", "checkpoint")):
        _add_evidence(
            evidence,
            counts,
            root,
            path,
            1,
            "<module>",
            "reliability",
            "retry/checkpoint configuration detected",
            0.75,
        )
    if any(token in lower for token in ("memory", "conversation_store", "summary_buffer")):
        _add_evidence(
            evidence,
            counts,
            root,
            path,
            1,
            "<module>",
            "memory",
            "memory/context lifecycle signal detected",
            0.6,
        )
    if any(token in lower for token in ("trace", "langfuse", "langsmith", "opentelemetry", "token_usage")):
        _add_evidence(
            evidence,
            counts,
            root,
            path,
            1,
            "<module>",
            "observability",
            "trace/cost/telemetry signal detected",
            0.7,
        )
    if any(token in lower for token in ("permission", "allowlist", "prompt injection", "sandbox", "audit")):
        _add_evidence(
            evidence,
            counts,
            root,
            path,
            1,
            "<module>",
            "security",
            "permission/sandbox/audit signal detected",
            0.65,
        )


def extract_python_evidence(root: Path, files: list[Path]) -> list[dict]:
    evidence: list[dict] = []
    counts: dict[str, int] = defaultdict(int)
    for path in files:
        if path.suffix.lower() == ".py":
            _scan_python_file(root, path, evidence, counts)
        elif path.suffix.lower() in {".json", ".yaml", ".yml"}:
            name = path.name.lower()
            if any(part.lower() in {"eval", "evals", "evaluation", "benchmark"} for part in path.parts) or "test_case" in name:
                _add_evidence(
                    evidence,
                    counts,
                    root,
                    path,
                    1,
                    path.stem,
                    "evaluation",
                    _excerpt(_read_text(path).splitlines(), 1),
                    0.75,
                )
    return evidence


def _candidate_patterns(files: list[Path], evidence: list[dict]) -> list[dict]:
    names = {item["kind"] for item in evidence}
    patterns: list[dict] = []
    if "persistence" in names and "orchestration" in names:
        patterns.append(
            {
                "name": "checkpoint-backed-orchestration",
                "evidence_paths": sorted({item["path"] for item in evidence if item["kind"] in {"persistence", "orchestration"}}),
                "chain_position": "orchestration",
                "generic_value": "可恢复的状态化执行",
                "project_specific": "需要结合本项目的状态存储与副作用确认",
                "confidence": 0.75,
                "repeated": False,
            }
        )
    if "reliability" in names and "tool" in names:
        patterns.append(
            {
                "name": "tool-retry-boundary",
                "evidence_paths": sorted({item["path"] for item in evidence if item["kind"] in {"reliability", "tool"}}),
                "chain_position": "tool",
                "generic_value": "工具失败与副作用边界治理",
                "project_specific": "需确认是否有幂等键和权限策略",
                "confidence": 0.65,
                "repeated": False,
            }
        )
    return patterns


def _build_chains(evidence: list[dict]) -> list[dict]:
    order = [
        "entrypoint",
        "orchestration",
        "long_running",
        "tool",
        "memory",
        "rag",
        "persistence",
        "reliability",
        "evaluation",
        "observability",
        "security",
    ]
    by_kind: dict[str, list[str]] = defaultdict(list)
    for item in evidence:
        by_kind[item["kind"]].append(item["id"])
    stages = [
        {"stage": kind, "evidence_ids": by_kind[kind]}
        for kind in order
        if by_kind[kind]
    ]
    if stages:
        return [{"name": "agent-business-flow", "stages": stages}]
    return []


def build_report(root: Path) -> dict:
    files = discover_files(root)
    evidence = extract_python_evidence(root, files)
    for index, item in enumerate(evidence, start=1):
        item["id"] = f"E{index}"
    return {
        "schema_version": "1.0",
        "root": str(root.resolve()),
        "frameworks": detect_frameworks(files),
        "entrypoints": [item for item in evidence if item["kind"] == "entrypoint"],
        "evidence": evidence,
        "chains": _build_chains(evidence),
        "candidate_patterns": _candidate_patterns(files, evidence),
        "rule_update_proposal": None,
    }


def _markdown(report: dict) -> str:
    lines = [
        "# Agent 项目链路扫描报告",
        "",
        f"- 源码根目录：{report['root']}",
        f"- 检测框架：{', '.join(report['frameworks']) or '未识别'}",
        "",
        "## 链路",
    ]
    for chain in report["chains"]:
        lines.append(f"### {chain['name']}")
        for stage in chain["stages"]:
            lines.append(f"- {stage['stage']}：{', '.join(stage['evidence_ids'])}")
    lines.extend(["", "## 证据"])
    for item in report["evidence"]:
        lines.append(
            f"- {item['id']} [{item['kind']}] {item['path']}:{item['line']} "
            f"{item['symbol']} - {item['excerpt']}"
        )
    lines.extend(["", "## candidate_patterns", ""])
    lines.append(json.dumps(report["candidate_patterns"], ensure_ascii=False, indent=2))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(args.root)
    except (FileNotFoundError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rendered = (
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else _markdown(report)
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
