from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3000
DEFAULT_BASE_URL = "http://localhost:3000"
DEFAULT_ALLOWED_REDIRECT_ORIGINS = ["https://chat.openai.com", "https://chatgpt.com"]


def _get_env(name: str) -> str | None:
    raw = os.getenv(name)
    if raw is None:
        return None
    value = raw.strip()
    return value or None


def _parse_csv_env(name: str) -> list[str] | None:
    raw = _get_env(name)
    if not raw:
        return None
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or None


def _parse_int_env(name: str, default: int) -> int:
    raw = _get_env(name)
    return int(raw) if raw is not None else default


@dataclass(frozen=True, slots=True)
class Settings:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    public_base_url: str = DEFAULT_BASE_URL
    data_dir: Path = Path("data")
    allowed_hosts: list[str] | None = None
    allowed_origins: list[str] | None = None
    allowed_redirect_origins: list[str] | None = None
    auth_enabled: bool = False
    admin_username: str | None = None
    admin_password: str | None = None
    log_level: str = "INFO"


def load_settings() -> Settings:
    port = _parse_int_env("MESSAGE_FIRST_DECK_PORT", DEFAULT_PORT)
    public_base_url = _get_env("MESSAGE_FIRST_DECK_PUBLIC_BASE_URL") or _get_env("PUBLIC_BASE_URL")
    auth_enabled = (_get_env("MESSAGE_FIRST_DECK_AUTH_ENABLED") or "").lower() in {"1", "true", "yes", "on"}
    return Settings(
        host=_get_env("MESSAGE_FIRST_DECK_HOST") or DEFAULT_HOST,
        port=port,
        public_base_url=public_base_url or f"http://localhost:{port}",
        data_dir=Path(_get_env("MESSAGE_FIRST_DECK_DATA_DIR") or "data").resolve(),
        allowed_hosts=_parse_csv_env("MESSAGE_FIRST_DECK_ALLOWED_HOSTS") or _parse_csv_env("ALLOWED_HOSTS"),
        allowed_origins=_parse_csv_env("MESSAGE_FIRST_DECK_ALLOWED_ORIGINS") or _parse_csv_env("ALLOWED_ORIGINS"),
        allowed_redirect_origins=(
            _parse_csv_env("MESSAGE_FIRST_DECK_ALLOWED_REDIRECT_ORIGINS")
            or _parse_csv_env("ALLOWED_REDIRECT_ORIGINS")
            or DEFAULT_ALLOWED_REDIRECT_ORIGINS
        ),
        auth_enabled=auth_enabled,
        admin_username=_get_env("MESSAGE_FIRST_DECK_ADMIN_USERNAME"),
        admin_password=_get_env("MESSAGE_FIRST_DECK_ADMIN_PASSWORD"),
        log_level=_get_env("LOG_LEVEL") or "INFO",
    )
