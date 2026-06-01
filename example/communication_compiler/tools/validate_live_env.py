from __future__ import annotations

import importlib.metadata
import os
import sys
from pathlib import Path


REQUIRED_FOR_LIVE = [
    "APP_BASE_URL",
    "APP_DATA_DIR",
    "AGENT_PROVIDER",
    "AZURE_AI_FOUNDRY_PROJECT_ENDPOINT",
    "MESSAGE_FIRST_MCP_ENDPOINT",
    "MESSAGE_FIRST_PUBLIC_BASE_URL",
]


def main() -> int:
    env_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".env.live")
    values = dict(os.environ)
    if env_path.exists():
        values.update(_parse_env_file(env_path))

    errors: list[str] = []
    warnings: list[str] = []

    for name in REQUIRED_FOR_LIVE:
        if not values.get(name):
            errors.append(f"{name} is required.")

    if values.get("AGENT_PROVIDER") != "foundry":
        errors.append("AGENT_PROVIDER must be foundry for a live Azure AI Foundry test.")

    endpoint = values.get("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT", "")
    if endpoint and not endpoint.startswith("https://"):
        errors.append("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT must start with https://.")
    if endpoint and "/api/projects/" not in endpoint:
        warnings.append("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT should look like https://resource.ai.azure.com/api/projects/project.")

    if not values.get("AZURE_AI_FOUNDRY_AGENT_NAME") and not values.get("AZURE_AI_FOUNDRY_AGENT_ID"):
        errors.append("Set AZURE_AI_FOUNDRY_AGENT_NAME for Projects 2.x, or AZURE_AI_FOUNDRY_AGENT_ID for legacy/classic.")
    if values.get("AZURE_AI_FOUNDRY_AGENT_ID") and not values.get("AZURE_AI_FOUNDRY_AGENT_NAME"):
        warnings.append("Only AZURE_AI_FOUNDRY_AGENT_ID is set. Current azure-ai-projects 2.x expects AZURE_AI_FOUNDRY_AGENT_NAME.")

    if values.get("MESSAGE_FIRST_MCP_ALLOW_LOCAL_FALLBACK", "true").lower() in {"1", "true", "yes", "on"}:
        warnings.append("MESSAGE_FIRST_MCP_ALLOW_LOCAL_FALLBACK should be false for a real integration test.")

    try:
        projects_version = importlib.metadata.version("azure-ai-projects")
        identity_version = importlib.metadata.version("azure-identity")
    except importlib.metadata.PackageNotFoundError as exc:
        errors.append(f"Optional Foundry package is missing: {exc.name}. Run: uv sync --extra foundry")
        projects_version = "missing"
        identity_version = "missing"

    print("Live env validation")
    print(f"- env file: {env_path}")
    print(f"- azure-ai-projects: {projects_version}")
    print(f"- azure-identity: {identity_version}")
    print("- Azure API calls made: none")

    if warnings:
        print("\nWarnings:")
        for item in warnings:
            print(f"- {item}")
    if errors:
        print("\nErrors:")
        for item in errors:
            print(f"- {item}")
        return 1
    print("\nOK: live env shape is ready for the first paid smoke test.")
    return 0


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


if __name__ == "__main__":
    raise SystemExit(main())
