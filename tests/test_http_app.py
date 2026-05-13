from __future__ import annotations

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
