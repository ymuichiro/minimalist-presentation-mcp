from __future__ import annotations

from typing import Any

from minimalist_presentation_mcp.deck.parser import parse_deck_input
from minimalist_presentation_mcp.deck.render_html import render_deck_html
from minimalist_presentation_mcp.deck.schema import DeckValidationError, SCHEMA_VERSION
from minimalist_presentation_mcp.deck.warnings import build_warnings
from minimalist_presentation_mcp.storage.deck_store import DeckStore


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

    deck_id = store.new_deck_id()
    html = render_deck_html(deck_id, deck)
    store.save_with_id(deck_id, deck, html)
    warnings = build_warnings(deck)

    return {
        "deck_id": deck_id,
        "url": f"{base_url.rstrip('/')}/decks/{deck_id}",
        "schema_version": SCHEMA_VERSION,
        "page_count": 5,
        "warnings": warnings,
    }
