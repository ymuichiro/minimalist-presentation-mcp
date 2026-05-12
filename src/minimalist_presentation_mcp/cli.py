from __future__ import annotations

from minimalist_presentation_mcp.mcp.server import create_mcp_server_from_settings


def main() -> None:
    create_mcp_server_from_settings().run(transport="streamable-http")
