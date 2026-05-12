from __future__ import annotations

import json
from typing import Any

import yaml
from pydantic import ValidationError

from minimalist_presentation_mcp.deck.schema import (
    DeckIR,
    DeckValidationError,
    ensure_mapping,
    validation_error_details,
)


def parse_deck_input(format: str, content: Any) -> DeckIR:
    normalized_format = format.lower().strip()
    try:
        if normalized_format == "yaml":
            if not isinstance(content, str):
                raise DeckValidationError(
                    "YAML content must be a string",
                    [{"path": "content", "reason": "string required for yaml"}],
                )
            parsed = yaml.safe_load(content)
        elif normalized_format == "json":
            parsed = json.loads(content) if isinstance(content, str) else content
        else:
            raise DeckValidationError(
                "format must be yaml or json",
                [{"path": "format", "reason": "unsupported format"}],
            )
    except DeckValidationError:
        raise
    except (yaml.YAMLError, json.JSONDecodeError) as error:
        raise DeckValidationError(
            "Deck content could not be parsed",
            [{"path": "content", "reason": str(error)}],
        ) from error

    try:
        return DeckIR.model_validate(ensure_mapping(parsed))
    except ValidationError as error:
        raise DeckValidationError("Deck validation failed", validation_error_details(error)) from error
