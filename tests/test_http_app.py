from __future__ import annotations

import base64
import hashlib
import json
from urllib.parse import parse_qs, urlparse

from starlette.testclient import TestClient

from minimalist_presentation_mcp.deck.service import create_deck_response
from minimalist_presentation_mcp.mcp.server import create_mcp_server
from minimalist_presentation_mcp.storage.deck_store import DeckStore

from conftest import sample_deck


def test_http_routes_and_mcp_mount(tmp_path) -> None:
    server = create_mcp_server(data_dir=tmp_path)
    app = server.streamable_http_app()

    with TestClient(app, base_url="http://localhost:3000") as client:
        health = client.get("/healthz")
        assert health.status_code == 200
        assert health.json()["mcp"] == "/mcp"

        root = client.get("/")
        assert root.status_code == 200
        assert root.json()["mcp"] == "/mcp"

        mcp_probe = client.get("/mcp")
        assert mcp_probe.status_code in {200, 405, 406}


def test_deck_route_returns_persisted_html(tmp_path) -> None:
    store = DeckStore(data_dir=tmp_path)
    response = create_deck_response(
        format="json",
        content=sample_deck(),
        store=store,
        base_url="http://localhost:3000",
    )
    server = create_mcp_server(data_dir=tmp_path)
    app = server.streamable_http_app()

    with TestClient(app, base_url="http://localhost:3000") as client:
        deck = client.get(f"/decks/{response['deck_id']}")
        assert deck.status_code == 200
        assert "Message-First Deck" in deck.text
        assert deck.text.count('class="slide ') == 5
        assert 'class="evidence-top"' in deck.text
        assert "読み取り：" in deck.text
        assert 'tooltip.className = "deck-tooltip"' in deck.text
        assert 'data-chart-bar' in deck.text


def test_mcp_transport_allows_configured_public_host(tmp_path) -> None:
    server = create_mcp_server(
        data_dir=tmp_path,
        allowed_hosts=["127.0.0.1", "localhost", "message-first.example.com"],
    )
    app = server.streamable_http_app()

    with TestClient(app, base_url="https://message-first.example.com") as client:
        mcp_probe = client.get("/mcp")
        assert mcp_probe.status_code in {200, 405, 406}


def test_mcp_transport_rejects_unconfigured_host(tmp_path) -> None:
    server = create_mcp_server(data_dir=tmp_path, allowed_hosts=["localhost"])
    app = server.streamable_http_app()

    with TestClient(app, base_url="https://unexpected.example.com") as client:
        mcp_probe = client.get("/mcp")
        assert mcp_probe.status_code == 421


def _challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def _auth_server(tmp_path):
    return create_mcp_server(
        data_dir=tmp_path,
        base_url="https://message-first.example.com",
        allowed_hosts=["message-first.example.com"],
        auth_enabled=True,
        admin_username="alice",
        admin_password="correct-password",
    )


def test_authenticated_mcp_oauth_pkce_flow(tmp_path) -> None:
    app = _auth_server(tmp_path).streamable_http_app()

    with TestClient(app, base_url="https://message-first.example.com", follow_redirects=False) as client:
        unauthenticated = client.get("/mcp")
        assert unauthenticated.status_code == 401
        assert "resource_metadata" in unauthenticated.headers["www-authenticate"]

        metadata = client.get("/.well-known/oauth-protected-resource/mcp")
        assert metadata.status_code == 200
        assert metadata.json()["resource"] == "https://message-first.example.com/mcp"
        root_metadata = client.get("/.well-known/oauth-protected-resource")
        assert root_metadata.status_code == 200
        assert root_metadata.json()["resource"] == "https://message-first.example.com/mcp"

        registration = client.post(
            "/register",
            json={
                "redirect_uris": ["https://chat.openai.com/aip/callback"],
                "token_endpoint_auth_method": "none",
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "scope": "deck:create deck:read",
                "client_name": "ChatGPT",
            },
        )
        assert registration.status_code == 201
        client_id = registration.json()["client_id"]

        verifier = "test-verifier-value-with-enough-length"
        authorize = client.get(
            "/authorize",
            params={
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": "https://chat.openai.com/aip/callback",
                "scope": "deck:create deck:read",
                "state": "state-1",
                "code_challenge": _challenge(verifier),
                "code_challenge_method": "S256",
                "resource": "https://message-first.example.com/mcp",
            },
        )
        assert authorize.status_code == 302
        login_url = authorize.headers["location"]
        assert login_url.startswith("https://message-first.example.com/login?auth_request=")

        login = client.post(
            login_url,
            data={
                "username": "alice",
                "password": "correct-password",
                "auth_request": parse_qs(urlparse(login_url).query)["auth_request"][0],
            },
        )
        assert login.status_code == 302
        redirected = urlparse(login.headers["location"])
        assert redirected.scheme == "https"
        assert redirected.netloc == "chat.openai.com"
        query = parse_qs(redirected.query)
        assert query["state"] == ["state-1"]

        token = client.post(
            "/token",
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "code": query["code"][0],
                "redirect_uri": "https://chat.openai.com/aip/callback",
                "code_verifier": verifier,
            },
        )
        assert token.status_code == 200
        payload = token.json()
        assert payload["token_type"] == "Bearer"
        assert payload["access_token"]
        assert payload["refresh_token"]


def test_dynamic_registration_rejects_untrusted_redirect_origin(tmp_path) -> None:
    app = _auth_server(tmp_path).streamable_http_app()

    with TestClient(app, base_url="https://message-first.example.com", follow_redirects=False) as client:
        registration = client.post(
            "/register",
            json={
                "redirect_uris": ["https://evil.example.com/callback"],
                "token_endpoint_auth_method": "none",
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "scope": "deck:create deck:read",
                "client_name": "Unexpected client",
            },
        )
        assert registration.status_code == 400
        assert registration.json()["error"] == "invalid_client_metadata"
        assert "redirect_uri origin is not allowed" in registration.json()["error_description"]


def test_dashboard_mypage_and_deck_pages_require_authenticated_owner(tmp_path) -> None:
    store = DeckStore(data_dir=tmp_path)
    owned = create_deck_response(
        format="json",
        content=sample_deck(),
        store=store,
        base_url="https://message-first.example.com",
        owner_user_id="usr_manual",
    )
    app = _auth_server(tmp_path).streamable_http_app()
    user_id = next(iter(json.loads((tmp_path / "auth.json").read_text())["users"]))
    visible = create_deck_response(
        format="json",
        content=sample_deck(),
        store=store,
        base_url="https://message-first.example.com",
        owner_user_id=user_id,
    )

    with TestClient(app, base_url="https://message-first.example.com", follow_redirects=False) as client:
        dashboard = client.get("/dashboard")
        assert dashboard.status_code == 302
        assert dashboard.headers["location"].startswith("/login")

        login = client.post(
            "/login",
            data={"username": "alice", "password": "correct-password", "next": "/dashboard"},
        )
        assert login.status_code == 302
        dashboard = client.get("/dashboard")
        assert dashboard.status_code == 200
        assert "作成した資料" in dashboard.text
        assert visible["deck_id"] in dashboard.text

        forbidden = client.get(f"/decks/{owned['deck_id']}")
        assert forbidden.status_code == 404
        allowed = client.get(f"/decks/{visible['deck_id']}")
        assert allowed.status_code == 200

        preferences = client.post("/mypage/preferences", data={"language": "en", "theme": "dark"})
        assert preferences.status_code == 302
        mypage = client.get("/mypage")
        assert mypage.status_code == 200
        assert 'lang="en"' in mypage.text
        assert 'data-theme="dark"' in mypage.text
        assert "Display settings" in mypage.text
