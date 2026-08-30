#!/usr/bin/env python3
"""Render the Markdown handoff report to a readable PDF when ReportLab is available."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _font_name() -> str:
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError as exc:
        raise RuntimeError("renderer reportlab is unavailable: install reportlab") from exc
    candidates = (
        Path(r"C:\Windows\Fonts\msyh.ttf"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    )
    for font_path in candidates:
        if font_path.exists():
            try:
                pdfmetrics.registerFont(TTFont("AgentReportFont", str(font_path)))
                return "AgentReportFont"
            except Exception:
                continue
    return "Helvetica"


def _plain_lines(markdown: str) -> list[str]:
    lines: list[str] = []
    in_fence = False
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not line:
            lines.append("")
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        if line.startswith("- "):
            line = "* " + line[2:]
        lines.append(line)
    return lines


def _wrap(text: str, max_chars: int = 46) -> list[str]:
    if not text:
        return [""]
    return [text[index : index + max_chars] for index in range(0, len(text), max_chars)]


def render_pdf(markdown: str, output: Path, renderer: str = "auto", title: str = "") -> None:
    if renderer not in {"auto", "reportlab"}:
        raise RuntimeError(f"renderer {renderer!r} is unavailable")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError("renderer reportlab is unavailable: install reportlab") from exc

    font = _font_name()
    page_width, page_height = A4
    pdf = canvas.Canvas(str(output), pagesize=A4)
    pdf.setTitle(title or "Agent internship report")
    y = page_height - 48
    pdf.setFont(font, 10)
    for line in _plain_lines(markdown):
        for wrapped in _wrap(line):
            if y < 48:
                pdf.showPage()
                pdf.setFont(font, 10)
                y = page_height - 48
            pdf.drawString(42, y, wrapped)
            y -= 15
        y -= 3
    pdf.save()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--renderer", default="auto")
    parser.add_argument("--title", default="Agent internship report")
    args = parser.parse_args(argv)
    output = args.output or args.input.with_suffix(".pdf")
    try:
        markdown = args.input.read_text(encoding="utf-8")
        output.parent.mkdir(parents=True, exist_ok=True)
        render_pdf(markdown, output, args.renderer, args.title)
    except (OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        if output.exists() and output.stat().st_size == 0:
            output.unlink()
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
