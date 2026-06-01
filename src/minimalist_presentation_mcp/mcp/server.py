from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import quote

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response

from minimalist_presentation_mcp.auth.oauth import DEFAULT_SCOPES, InAppOAuthProvider
from minimalist_presentation_mcp.auth.store import AuthStore
from minimalist_presentation_mcp.auth.ui import (
    dashboard_page,
    get_session_user,
    handle_login_post,
    login_form,
    mypage,
    redirect_to_login,
)
from minimalist_presentation_mcp.config import (
    DEFAULT_ALLOWED_REDIRECT_ORIGINS,
    DEFAULT_BASE_URL,
    DEFAULT_HOST,
    DEFAULT_PORT,
    Settings,
    load_settings,
)
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
    allowed_redirect_origins: list[str] | None = None,
    log_level: str | None = None,
    auth_enabled: bool = False,
    admin_username: str | None = None,
    admin_password: str | None = None,
) -> FastMCP:
    settings = Settings(
        host=host,
        port=port,
        public_base_url=base_url,
        data_dir=data_dir or get_data_dir(),
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
        allowed_redirect_origins=allowed_redirect_origins or DEFAULT_ALLOWED_REDIRECT_ORIGINS,
        auth_enabled=auth_enabled,
        admin_username=admin_username,
        admin_password=admin_password,
        log_level=log_level or os.getenv("LOG_LEVEL", "INFO"),
    )
    store = DeckStore(settings.data_dir)
    auth_store: AuthStore | None = None
    oauth_provider: InAppOAuthProvider | None = None
    auth_settings: AuthSettings | None = None
    if settings.auth_enabled:
        if not settings.admin_username or not settings.admin_password:
            raise RuntimeError("MESSAGE_FIRST_DECK_ADMIN_USERNAME and MESSAGE_FIRST_DECK_ADMIN_PASSWORD are required.")
        auth_store = AuthStore(settings.data_dir)
        auth_store.bootstrap_admin(settings.admin_username, settings.admin_password)
        resource_url = f"{settings.public_base_url.rstrip('/')}/mcp"
        oauth_provider = InAppOAuthProvider(
            store=auth_store,
            issuer_url=settings.public_base_url,
            resource_url=resource_url,
            allowed_redirect_origins=settings.allowed_redirect_origins,
        )
        auth_settings = AuthSettings(
            issuer_url=settings.public_base_url,
            resource_server_url=resource_url,
            required_scopes=DEFAULT_SCOPES,
            client_registration_options=ClientRegistrationOptions(
                enabled=True,
                valid_scopes=DEFAULT_SCOPES,
                default_scopes=DEFAULT_SCOPES,
            ),
            revocation_options=RevocationOptions(enabled=True),
        )
    server = FastMCP(
        "minimalist-presentation-mcp",
        host=settings.host,
        port=settings.port,
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
        log_level=settings.log_level,
        transport_security=_build_transport_security(settings),
        auth=auth_settings,
        auth_server_provider=oauth_provider,
    )

    @server.tool()
    def get_presentation_guideline() -> dict[str, object]:
        """Return the Message-First Deck generation guideline and schema summary."""
        return get_guideline_response()

    @server.tool()
    def create_message_first_deck(format: str, content: Any) -> dict[str, Any]:
        """Create a fixed five-page Message-First Deck from YAML or JSON input."""
        owner_user_id = None
        if auth_store is not None:
            access_token = get_access_token()
            token_record = auth_store.load_access_token(access_token.token) if access_token else None
            owner_user_id = token_record["user_id"] if token_record else None
        return create_deck_response(
            format=format,
            content=content,
            store=store,
            base_url=settings.public_base_url,
            owner_user_id=owner_user_id,
        )

    @server.custom_route("/", methods=["GET"], include_in_schema=False)
    async def root(_: Request) -> Response:
        return JSONResponse({"status": "ok", "mcp": "/mcp"})

    @server.custom_route("/healthz", methods=["GET"], include_in_schema=False)
    async def healthz(_: Request) -> Response:
        return JSONResponse({"status": "ok", "mcp": "/mcp"})

    if settings.auth_enabled:

        @server.custom_route("/.well-known/oauth-protected-resource", methods=["GET", "OPTIONS"], include_in_schema=False)
        async def protected_resource_root(_: Request) -> Response:
            return JSONResponse(
                {
                    "resource": f"{settings.public_base_url.rstrip('/')}/mcp",
                    "authorization_servers": [settings.public_base_url.rstrip("/")],
                    "scopes_supported": DEFAULT_SCOPES,
                    "bearer_methods_supported": ["header"],
                }
            )

    @server.custom_route("/login", methods=["GET"], include_in_schema=False)
    async def login_get(request: Request) -> Response:
        if auth_store is None:
            return RedirectResponse("/dashboard", status_code=302)
        return login_form(request, user=get_session_user(request, auth_store))

    @server.custom_route("/login", methods=["POST"], include_in_schema=False)
    async def login_post(request: Request) -> Response:
        if auth_store is None or oauth_provider is None:
            return PlainTextResponse("Authentication is disabled", status_code=404)
        return await handle_login_post(request, auth_store, oauth_provider)

    @server.custom_route("/logout", methods=["POST"], include_in_schema=False)
    async def logout(request: Request) -> Response:
        if auth_store is not None:
            auth_store.delete_browser_session(request.cookies.get("mfd_session"))
        response = RedirectResponse("/login", status_code=302)
        response.delete_cookie("mfd_session", path="/")
        return response

    @server.custom_route("/dashboard", methods=["GET"], include_in_schema=False)
    async def dashboard(request: Request) -> Response:
        if auth_store is None:
            return dashboard_page({"id": "", "language": "ja", "theme": "light"}, store)
        user = get_session_user(request, auth_store)
        if not user:
            return redirect_to_login(request)
        return dashboard_page(user, store)

    @server.custom_route("/mypage", methods=["GET"], include_in_schema=False)
    async def mypage_get(request: Request) -> Response:
        if auth_store is None:
            return RedirectResponse("/dashboard", status_code=302)
        user = get_session_user(request, auth_store)
        if not user:
            return redirect_to_login(request)
        return mypage(user)

    @server.custom_route("/mypage/preferences", methods=["POST"], include_in_schema=False)
    async def mypage_preferences(request: Request) -> Response:
        if auth_store is None:
            return PlainTextResponse("Authentication is disabled", status_code=404)
        user = get_session_user(request, auth_store)
        if not user:
            return redirect_to_login(request)
        form = await request.form()
        auth_store.update_preferences(
            user["id"],
            language=str(form.get("language") or "ja"),
            theme=str(form.get("theme") or "light"),
        )
        return RedirectResponse("/mypage", status_code=302)

    @server.custom_route("/decks/{deck_id}", methods=["GET"], include_in_schema=False)
    async def deck_view(request: Request) -> Response:
        deck_id = request.path_params["deck_id"]
        if auth_store is not None:
            user = get_session_user(request, auth_store)
            if not user:
                return RedirectResponse(f"/login?next={quote(str(request.url.path))}", status_code=302)
            metadata = store.get_metadata(deck_id)
            if metadata is None:
                return PlainTextResponse("Deck not found", status_code=404)
            if metadata.get("owner_user_id") != user["id"]:
                return PlainTextResponse("Deck not found", status_code=404)
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
        allowed_redirect_origins=resolved.allowed_redirect_origins,
        log_level=resolved.log_level,
        auth_enabled=resolved.auth_enabled,
        admin_username=resolved.admin_username,
        admin_password=resolved.admin_password,
    )
