from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _get_env(name: str) -> str | None:
    raw = os.getenv(name)
    if raw is None:
        return None
    value = raw.strip()
    return value or None


def _env_bool(name: str, default: bool) -> bool:
    raw = _get_env(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class AppSettings:
    app_base_url: str = "http://localhost:8080"
    app_env: str = "local"
    data_dir: Path = Path("data/app")
    evidence_fixture_dir: Path = Path("fixtures/evidence")
    agent_provider: str = "mock"
    azure_ai_foundry_project_endpoint: str | None = None
    azure_ai_foundry_agent_name: str | None = None
    azure_ai_foundry_agent_version: str | None = None
    azure_ai_foundry_agent_id: str | None = None
    azure_openai_deployment_name: str | None = None
    azure_speech_key: str | None = None
    azure_speech_region: str | None = None
    azure_speech_endpoint: str | None = None
    azure_speech_resource_id: str | None = None
    message_first_mcp_endpoint: str = "http://localhost:3000/mcp"
    message_first_public_base_url: str = "http://localhost:3000"
    message_first_mcp_bearer_token: str | None = None
    message_first_mcp_data_dir: Path = Path("data")
    allow_local_mcp_fallback: bool = True


def load_settings() -> AppSettings:
    return AppSettings(
        app_base_url=_get_env("APP_BASE_URL") or "http://localhost:8080",
        app_env=_get_env("APP_ENV") or "local",
        data_dir=Path(_get_env("APP_DATA_DIR") or "data/app").resolve(),
        evidence_fixture_dir=Path(_get_env("EVIDENCE_FIXTURE_DIR") or "fixtures/evidence").resolve(),
        agent_provider=(_get_env("AGENT_PROVIDER") or "mock").lower(),
        azure_ai_foundry_project_endpoint=_get_env("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"),
        azure_ai_foundry_agent_name=_get_env("AZURE_AI_FOUNDRY_AGENT_NAME"),
        azure_ai_foundry_agent_version=_get_env("AZURE_AI_FOUNDRY_AGENT_VERSION"),
        azure_ai_foundry_agent_id=_get_env("AZURE_AI_FOUNDRY_AGENT_ID"),
        azure_openai_deployment_name=_get_env("AZURE_OPENAI_DEPLOYMENT_NAME"),
        azure_speech_key=_get_env("AZURE_SPEECH_KEY"),
        azure_speech_region=_get_env("AZURE_SPEECH_REGION"),
        azure_speech_endpoint=_get_env("AZURE_SPEECH_ENDPOINT"),
        azure_speech_resource_id=_get_env("AZURE_SPEECH_RESOURCE_ID"),
        message_first_mcp_endpoint=_get_env("MESSAGE_FIRST_MCP_ENDPOINT") or "http://localhost:3000/mcp",
        message_first_public_base_url=_get_env("MESSAGE_FIRST_PUBLIC_BASE_URL") or "http://localhost:3000",
        message_first_mcp_bearer_token=_get_env("MESSAGE_FIRST_MCP_BEARER_TOKEN"),
        message_first_mcp_data_dir=Path(_get_env("MESSAGE_FIRST_MCP_DATA_DIR") or "data").resolve(),
        allow_local_mcp_fallback=_env_bool("MESSAGE_FIRST_MCP_ALLOW_LOCAL_FALLBACK", True),
    )
