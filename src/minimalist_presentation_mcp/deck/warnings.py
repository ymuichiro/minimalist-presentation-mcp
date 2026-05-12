from __future__ import annotations

import re

from minimalist_presentation_mcp.deck.schema import DeckIR

EXTERNAL_URL_RE = re.compile(r"""(?:https?:)?//|data-[^=]*=\s*["']https?://""", re.IGNORECASE)
NUMERIC_SIGNAL_RE = re.compile(r"\d")
NO_NUMERIC_EXPLANATION_MARKERS = (
    "no numeric",
    "numeric data unavailable",
    "numerical data unavailable",
    "no quantified data",
    "without numeric data",
    "数値データ",
    "定量データ",
    "定量根拠",
    "公開データなし",
    "統計なし",
)
STRUCTURAL_EVIDENCE_MARKERS = (
    "<svg",
    "<table",
    "<ul",
    "<ol",
    "<dl",
    "display:grid",
    "grid-template-columns",
    "driver",
    "timeline",
    "matrix",
    "risk-map",
    "comparison",
    "workflow",
)


def _has_numeric_signal(*parts: str) -> bool:
    return bool(NUMERIC_SIGNAL_RE.search(" ".join(parts)))


def _explains_missing_numeric_data(*parts: str) -> bool:
    normalized = " ".join(parts).lower()
    return any(marker in normalized for marker in NO_NUMERIC_EXPLANATION_MARKERS)


def _has_structural_evidence(html_lower: str) -> bool:
    return any(marker in html_lower for marker in STRUCTURAL_EVIDENCE_MARKERS)


def build_warnings(deck: DeckIR) -> list[str]:
    warnings: list[str] = []

    for key in ("M1", "M2", "M3"):
        slide = getattr(deck.slides, key)
        if len(slide.watch) > 30:
            warnings.append(f"{key}.watch is longer than recommended length")
        if len(slide.statement) > 80:
            warnings.append(f"{key}.statement is longer than recommended length")
        if len(slide.sub_message) > 140:
            warnings.append(f"{key}.sub_message is longer than recommended length")
        if slide.speaker_note and len(slide.speaker_note) > 500:
            warnings.append(f"{key}.speaker_note is longer than recommended length")

    for key in ("E1", "E2"):
        slide = getattr(deck.slides, key)
        html = slide.html
        html_lower = html.lower()
        if len(slide.watch) > 40:
            warnings.append(f"{key}.watch is longer than recommended length")
        if len(slide.claim) > 120:
            warnings.append(f"{key}.claim is longer than recommended length")
        if len(slide.fallback_text) > 200:
            warnings.append(f"{key}.fallback_text is longer than recommended length")
        if slide.speaker_note and len(slide.speaker_note) > 500:
            warnings.append(f"{key}.speaker_note is longer than recommended length")
        if len(html) > 12000:
            warnings.append(f"{key}.html may overflow the slide area")
        if "<script" in html_lower or "</script" in html_lower:
            warnings.append(f"{key}.html contains script, which is discouraged")
        if "<iframe" in html_lower or "</iframe" in html_lower:
            warnings.append(f"{key}.html contains iframe, which is discouraged")
        for tag in ("html", "body", "head"):
            if re.search(rf"</?{tag}(?:\s|>|/)", html, re.IGNORECASE):
                warnings.append(f"{key}.html contains {tag} tag, which is discouraged")
        if EXTERNAL_URL_RE.search(html):
            warnings.append(f"{key}.html contains an external URL, which is discouraged")
        if not _has_numeric_signal(slide.claim, slide.html, slide.fallback_text) and not _explains_missing_numeric_data(
            slide.claim, slide.html, slide.fallback_text
        ):
            warnings.append(f"{key} does not appear to include quantified evidence or explain why it is unavailable")
        if not _has_structural_evidence(html_lower):
            warnings.append(f"{key}.html may be too sparse to function as an evidence capsule")

    return warnings
