from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import ulid

from minimalist_presentation_mcp.deck.schema import DeckIR


class DeckStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.decks_dir = data_dir / "decks"
        self.decks_dir.mkdir(parents=True, exist_ok=True)

    def new_deck_id(self) -> str:
        return f"dck_{ulid.new().str}"

    def save(self, deck: DeckIR, html: str) -> str:
        deck_id = self.new_deck_id()
        self.save_with_id(deck_id, deck, html)
        return deck_id

    def save_with_id(self, deck_id: str, deck: DeckIR, html: str) -> None:
        payload: dict[str, Any] = {
            "deck_id": deck_id,
            "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "schema_version": deck.schema_version,
            "source": deck.model_dump(mode="json"),
            "html": html,
        }
        json_path = self.decks_dir / f"{deck_id}.json"
        html_path = self.decks_dir / f"{deck_id}.html"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        html_path.write_text(html, encoding="utf-8")

    def get_html(self, deck_id: str) -> str | None:
        path = self.decks_dir / f"{deck_id}.html"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")
