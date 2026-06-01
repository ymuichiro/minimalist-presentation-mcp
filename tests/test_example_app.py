from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from example.communication_compiler.config import AppSettings
from example.communication_compiler.main import create_app
from example.communication_compiler.models import MessageKernel
from example.communication_compiler.services.guardrails import has_unsupported_numeric_claim


SAMPLE_FREE_TALK = """最近、社内で AI 活用を進めたいんだけど、みんな Copilot を入れればいいと思っていて、
でも実際には業務に入っていない気がしている。現場はプロンプトを書く時間もないし、
ナレッジも散らばっているし、PoC は増えるけど定着しない。
だから、単にライセンスを配るより、業務単位で Agent を作る方に予算を寄せたい。
ただ、経営層にはコスト削減だけで説明したくない。
むしろ、業務プロセスの再設計として伝えたい。"""


def _app(tmp_path: Path):
    return create_app(
        AppSettings(
            app_base_url="http://localhost:8080",
            data_dir=tmp_path / "app",
            evidence_fixture_dir=Path("fixtures/evidence").resolve(),
            message_first_mcp_endpoint="http://127.0.0.1:9/mcp",
            message_first_public_base_url="http://localhost:3000",
            message_first_mcp_data_dir=tmp_path / "mcp",
            allow_local_mcp_fallback=True,
        )
    )


def test_example_healthz_and_low_quality_input(tmp_path) -> None:
    with TestClient(_app(tmp_path)) as client:
        assert client.get("/healthz").json()["agent_provider"] == "mock"
        session_id = client.post("/api/sessions").json()["session_id"]
        client.post(
            f"/api/sessions/{session_id}/free-talk",
            json={"free_talk": "短い", "audience": "役員会", "desired_action": "決める"},
        )
        claims = client.post(f"/api/sessions/{session_id}/extract-claims", json={"max_candidates": 3})

    assert claims.status_code == 400
    assert claims.json()["error"]["code"] == "FREE_TALK_TOO_SHORT"


def test_example_full_mock_flow_generates_artifacts(tmp_path) -> None:
    with TestClient(_app(tmp_path)) as client:
        session_id = client.post("/api/sessions").json()["session_id"]
        free_talk = client.post(
            f"/api/sessions/{session_id}/free-talk",
            json={
                "free_talk": SAMPLE_FREE_TALK,
                "audience": "役員会",
                "desired_action": "次四半期の AI 投資方針を決める",
                "tone": "executive",
            },
        )
        assert free_talk.status_code == 200

        claims = client.post(f"/api/sessions/{session_id}/extract-claims", json={"max_candidates": 3})
        assert claims.status_code == 200
        assert len(claims.json()["claim_candidates"]) == 3

        selected = client.post(f"/api/sessions/{session_id}/select-claim", json={"claim_id": "claim_1"})
        assert selected.status_code == 200

        kernel = client.post(f"/api/sessions/{session_id}/refine-kernel", json={"additional_user_input": ""})
        assert kernel.status_code == 200
        assert kernel.json()["message_kernel"]["revision"] == 1
        assert kernel.json()["diagnosis"]["overall_score"] > 0

        grounding = client.post(f"/api/sessions/{session_id}/ground-evidence", json={"use_mock_evidence": True})
        assert grounding.status_code == 200
        assert grounding.json()["supporting_evidence"]
        assert grounding.json()["evidence_gaps"]
        assert grounding.json()["objections"]

        idea_map = client.post(f"/api/sessions/{session_id}/generate-idea-map", json={})
        assert idea_map.status_code == 200
        node_ids = {node["id"] for node in idea_map.json()["idea_map"]["nodes"]}
        assert {"premise", "complication", "claim", "action"}.issubset(node_ids)

        brief = client.post(f"/api/sessions/{session_id}/generate-brief", json={"format": "markdown"})
        assert brief.status_code == 200
        brief_text = client.get(f"/artifacts/{session_id}/brief.md")
        assert brief_text.status_code == 200
        assert "## 1. 4-Line Message Kernel" in brief_text.text
        assert "## 6. Evidence Gaps" in brief_text.text

        deck = client.post(f"/api/sessions/{session_id}/generate-deck", json={"language": "ja-JP"})
        assert deck.status_code == 200
        payload = deck.json()
        assert payload["deck_id"].startswith("dck_")
        assert payload["deck_url"].startswith("http://localhost:3000/decks/dck_")
        assert any("MCP_REMOTE_UNAVAILABLE_USED_LOCAL_FALLBACK" in warning for warning in payload["warnings"])

    deck_files = list((tmp_path / "mcp" / "decks").glob("dck_*.html"))
    assert deck_files


def test_example_deck_generation_requires_kernel(tmp_path) -> None:
    with TestClient(_app(tmp_path)) as client:
        session_id = client.post("/api/sessions").json()["session_id"]
        deck = client.post(f"/api/sessions/{session_id}/generate-deck", json={"language": "ja-JP"})

    assert deck.status_code == 400
    assert deck.json()["error"]["code"] == "MESSAGE_KERNEL_REQUIRED"


def test_speech_transcription_requires_azure_configuration(tmp_path) -> None:
    with TestClient(_app(tmp_path)) as client:
        response = client.post(
            "/api/speech/transcribe",
            data={"language": "ja-JP"},
            files={"audio": ("speech.webm", b"not real audio", "audio/webm")},
        )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SPEECH_NOT_CONFIGURED"


def test_guardrail_detects_unsupported_numeric_claim() -> None:
    kernel = MessageKernel(
        revision=1,
        premise="現状は利用拡大が中心である。",
        complication="しかし成果への接続は限定的である。",
        claim="Agent 化により30%効率化できる。",
        action="次四半期に予算を振り替える。",
        confidence=0.7,
    )

    assert has_unsupported_numeric_claim(kernel.claim)
    assert not has_unsupported_numeric_claim(kernel.claim, ["30%"])
