from __future__ import annotations

import re
from typing import Any

from minimalist_presentation_mcp.deck.parser import parse_deck_input
from minimalist_presentation_mcp.deck.render_html import render_deck_html
from minimalist_presentation_mcp.deck.schema import DeckIR, DeckValidationError, SCHEMA_VERSION
from minimalist_presentation_mcp.deck.warnings import build_warnings
from minimalist_presentation_mcp.storage.deck_store import DeckStore

SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.IGNORECASE | re.DOTALL)


def _strip_script_tags(html: str) -> str:
    return SCRIPT_TAG_RE.sub("", html)


def _sanitize_evidence_html(deck: DeckIR) -> DeckIR:
    slides = deck.slides.model_copy(deep=True)
    for key in ("E1", "E2"):
        slide = getattr(slides, key)
        slide.html = _strip_script_tags(slide.html).strip()
    return deck.model_copy(update={"slides": slides}, deep=True)


def create_deck_response(
    *,
    format: str,
    content: Any,
    store: DeckStore,
    base_url: str,
) -> dict[str, Any]:
    try:
        deck = parse_deck_input(format, content)
    except DeckValidationError as error:
        return {
            "error": "VALIDATION_ERROR",
            "message": error.message,
            "details": error.details,
        }

    warnings = build_warnings(deck)
    safe_deck = _sanitize_evidence_html(deck)
    deck_id = store.new_deck_id()
    html = render_deck_html(deck_id, safe_deck)
    store.save_with_id(deck_id, safe_deck, html)

    return {
        "deck_id": deck_id,
        "url": f"{base_url.rstrip('/')}/decks/{deck_id}",
        "schema_version": SCHEMA_VERSION,
        "page_count": 5,
        "warnings": warnings,
    }
