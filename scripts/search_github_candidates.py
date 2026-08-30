#!/usr/bin/env python3
"""Search and rank GitHub Agent candidates without claiming source-level facts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen


SIGNAL_WORDS = {
    "workflow": "workflow",
    "orchestration": "orchestration",
    "checkpoint": "checkpoint",
    "resume": "resume",
    "retry": "retry",
    "idempot": "idempotency",
    "evaluation": "evaluation",
    "eval": "evaluation",
    "grader": "evaluation",
    "audit": "audit",
    "trace": "observability",
    "telemetry": "observability",
    "cost": "cost-governance",
    "latency": "latency-governance",
    "memory": "memory",
    "rag": "rag",
    "retrieval": "rag",
    "approval": "human-in-loop",
    "human": "human-in-loop",
    "tool": "tool-contract",
    "celery": "durable-worker",
    "temporal": "durable-worker",
    "sandbox": "sandbox",
    "permission": "security",
}
DOMAIN_WORDS = {
    "research": "research/report",
    "report": "research/report",
    "support": "support/ticket",
    "customer": "support/ticket",
    "ticket": "support/ticket",
    "analytics": "data-analysis",
    "data analysis": "data-analysis",
    "sql": "data-analysis",
    "knowledge": "enterprise-knowledge",
    "document": "enterprise-knowledge",
    "devops": "devops",
    "incident": "devops",
}
EXCLUDE_WORDS = {
    "browser extension": "browser-extension",
    "chrome extension": "browser-extension",
    "sdk": "sdk",
    "library": "library",
    "framework": "framework",
    "toolkit": "toolkit",
    "desktop": "desktop-shell",
    "iot": "iot",
    "hardware": "hardware",
    "embedded": "embedded",
    "single model call": "single",
    "simple llm": "single",
    "prompt template": "single",
    "chat ui": "single",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_url(url: str) -> str:
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"


def _load_items(fixture: Path | None, queries: list[str], per_page: int) -> list[dict]:
    if fixture:
        data = json.loads(fixture.read_text(encoding="utf-8"))
        return list(data.get("items", data if isinstance(data, list) else []))
    items: list[dict] = []
    for query in queries:
        url = f"https://api.github.com/search/repositories?q={quote_plus(query)}&per_page={per_page}"
        request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "agent-intern-miner"})
        with urlopen(request, timeout=20) as response:
            items.extend(json.loads(response.read().decode("utf-8")).get("items", []))
    return items


def _probe(item: dict) -> dict:
    text = " ".join(
        str(item.get(key, "") or "")
        for key in ("name", "description", "topics", "readme", "language")
    ).lower()
    signals = sorted({value for word, value in SIGNAL_WORDS.items() if word in text})
    domains = sorted({value for word, value in DOMAIN_WORDS.items() if word in text})
    risks = sorted({value for word, value in EXCLUDE_WORDS.items() if word in text})
    stars = int(item.get("stargazers_count", item.get("stars", 0)) or 0)
    score = len(signals) * 3 + min(len(domains), 2) * 2
    if stars >= 1000:
        score += 1
    score -= len(risks) * 5
    readme = str(item.get("readme", "") or "")
    return {
        "name": item.get("name") or item.get("full_name") or "unknown",
        "full_name": item.get("full_name", ""),
        "url": _canonical_url(item.get("html_url") or item.get("url") or ""),
        "stars": stars,
        "language": item.get("language"),
        "updated_at": item.get("updated_at"),
        "license": (item.get("license") or {}).get("spdx_id") if isinstance(item.get("license"), dict) else item.get("license"),
        "description": item.get("description", ""),
        "readme_probe": {
            "text": readme[:800],
            "signals_only": True,
            "source_level_claim_allowed": False,
        },
        "domain_bucket": domains or ["unclassified"],
        "engineering_signals": signals,
        "risk_flags": risks,
        "candidate_score": score,
    }


def rank_candidates(items: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for item in items:
        candidate = _probe(item)
        if not candidate["url"]:
            continue
        existing = deduped.get(candidate["url"])
        if existing is None or candidate["candidate_score"] > existing["candidate_score"]:
            deduped[candidate["url"]] = candidate
    return sorted(
        deduped.values(),
        key=lambda item: (-item["candidate_score"], -min(item["stars"], 1000), item["name"].lower()),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--per-page", type=int, default=20)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args(argv)
    if not args.fixture and not args.query:
        parser.error("provide --query or --fixture")
    try:
        candidates = rank_candidates(_load_items(args.fixture, args.query, args.per_page))
    except Exception as exc:
        print(f"search failed: {exc}", file=sys.stderr)
        return 2
    payload = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "queries": args.query,
        "source": "fixture" if args.fixture else "github-api",
        "candidates": candidates,
        "shortlist": candidates[:4],
    }
    if args.format == "json":
        rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    else:
        lines = ["# GitHub Agent 候选池", ""]
        for item in candidates:
            lines.append(
                f"- {item['name']} | score={item['candidate_score']} | stars={item['stars']} | "
                f"{', '.join(item['engineering_signals']) or 'no-signal'}"
            )
        rendered = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
