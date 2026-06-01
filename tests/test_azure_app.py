from __future__ import annotations

from starlette.testclient import TestClient

from azure_app import app


def test_azure_combined_app_serves_demo_and_mcp() -> None:
    with TestClient(app) as client:
        index = client.get("/")
        healthz = client.get("/healthz")
        mcp_probe = client.get("/mcp")

    assert index.status_code == 200
    assert "Communication Compiler" in index.text
    assert healthz.status_code == 200
    assert healthz.json()["status"] == "ok"
    assert mcp_probe.status_code in {400, 405, 406, 421}
