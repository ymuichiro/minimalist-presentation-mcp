from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response

from minimalist_presentation_mcp.config import DEFAULT_BASE_URL, DEFAULT_HOST, DEFAULT_PORT, Settings, load_settings
from minimalist_presentation_mcp.deck.guideline import get_guideline_response
from minimalist_presentation_mcp.deck.service import create_deck_response
from minimalist_presentation_mcp.storage.deck_store import DeckStore


def get_data_dir() -> Path:
    configured = os.getenv("MESSAGE_FIRST_DECK_DATA_DIR")
    if configured:
        return Path(configured)
    return Path.cwd() / "data"


def _build_transport_security(settings: Settings) -> TransportSecuritySettings | None:
    if not settings.allowed_hosts and not settings.allowed_origins:
        return None

    allowed_hosts = sorted(
        {
            host
            for host in (settings.allowed_hosts or [])
            for host in (host, f"{host}:*")
            if host != "*"
        }
    )
    allowed_origins = set(settings.allowed_origins or [])
    for host in settings.allowed_hosts or []:
        if host == "*":
            continue
        allowed_origins.update(
            {
                f"http://{host}",
                f"http://{host}:*",
                f"https://{host}",
                f"https://{host}:*",
            }
        )

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=sorted(allowed_origins),
    )


def create_mcp_server(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    base_url: str = DEFAULT_BASE_URL,
    data_dir: Path | None = None,
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
    log_level: str | None = None,
) -> FastMCP:
    settings = Settings(
        host=host,
        port=port,
        public_base_url=base_url,
        data_dir=data_dir or get_data_dir(),
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
        log_level=log_level or os.getenv("LOG_LEVEL", "INFO"),
    )
    store = DeckStore(settings.data_dir)
    server = FastMCP(
        "minimalist-presentation-mcp",
        host=settings.host,
        port=settings.port,
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
        log_level=settings.log_level,
        transport_security=_build_transport_security(settings),
    )

    @server.tool()
    def get_presentation_guideline() -> dict[str, object]:
        """Return the Message-First Deck generation guideline and schema summary."""
        return get_guideline_response()

    @server.tool()
    def create_message_first_deck(format: str, content: Any) -> dict[str, Any]:
        """Create a fixed five-page Message-First Deck from YAML or JSON input."""
        return create_deck_response(format=format, content=content, store=store, base_url=settings.public_base_url)

    @server.custom_route("/", methods=["GET"], include_in_schema=False)
    async def root(_: Request) -> Response:
        return JSONResponse({"status": "ok", "mcp": "/mcp"})

    @server.custom_route("/healthz", methods=["GET"], include_in_schema=False)
    async def healthz(_: Request) -> Response:
        return JSONResponse({"status": "ok", "mcp": "/mcp"})

    @server.custom_route("/decks/{deck_id}", methods=["GET"], include_in_schema=False)
    async def deck_view(request: Request) -> Response:
        deck_id = request.path_params["deck_id"]
        html = store.get_html(deck_id)
        if html is None:
            return PlainTextResponse("Deck not found", status_code=404)
        return HTMLResponse(html)

    return server


def create_mcp_server_from_settings(settings: Settings | None = None) -> FastMCP:
    resolved = settings or load_settings()
    return create_mcp_server(
        host=resolved.host,
        port=resolved.port,
        base_url=resolved.public_base_url,
        data_dir=resolved.data_dir,
        allowed_hosts=resolved.allowed_hosts,
        allowed_origins=resolved.allowed_origins,
        log_level=resolved.log_level,
    )
