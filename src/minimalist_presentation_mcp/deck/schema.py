from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

SCHEMA_VERSION = "message-first-deck/v1"
PAGE_KEYS = ("M1", "M2", "M3", "E1", "E2")


class DeckValidationError(Exception):
    def __init__(self, message: str, details: list[dict[str, str]] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or []


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    audience: str | None = None
    purpose: str | None = None
    desired_action: str | None = None
    created_by: str | None = None


class MessageSlide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["message"]
    watch: str
    statement: str
    sub_message: str
    speaker_note: str | None = ""


class EvidenceSlide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["html_capsule"]
    watch: str
    claim: str
    html: str
    fallback_text: str
    speaker_note: str | None = ""


class Slides(BaseModel):
    model_config = ConfigDict(extra="forbid")

    M1: MessageSlide
    M2: MessageSlide
    M3: MessageSlide
    E1: EvidenceSlide
    E2: EvidenceSlide


class DeckIR(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    language: str | None = None
    title: str
    subtitle: str | None = ""
    metadata: Metadata = Field(default_factory=Metadata)
    slides: Slides

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
        return value


def validation_error_details(error: ValidationError) -> list[dict[str, str]]:
    details: list[dict[str, str]] = []
    for item in error.errors():
        path = ".".join(str(part) for part in item["loc"])
        details.append({"path": path, "reason": str(item["msg"])})
    return details


def ensure_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DeckValidationError(
            "Deck content must be an object",
            [{"path": "$", "reason": "object required"}],
        )
    return value
