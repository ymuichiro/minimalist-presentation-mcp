from __future__ import annotations

import json
import yaml

from minimalist_presentation_mcp.deck.guideline import get_guideline_response
from minimalist_presentation_mcp.deck.parser import parse_deck_input
from minimalist_presentation_mcp.deck.render_html import render_deck_html
from minimalist_presentation_mcp.deck.service import create_deck_response
from minimalist_presentation_mcp.deck.warnings import build_warnings
from minimalist_presentation_mcp.storage.deck_store import DeckStore

from conftest import sample_deck


def test_parse_yaml_success() -> None:
    deck = parse_deck_input("yaml", yaml.safe_dump(sample_deck(), allow_unicode=True))

    assert deck.schema_version == "message-first-deck/v1"
    assert deck.slides.M1.type == "message"
    assert deck.slides.E1.type == "html_capsule"


def test_parse_json_missing_required_field() -> None:
    payload = sample_deck()
    del payload["slides"]["M1"]["statement"]

    try:
        parse_deck_input("json", payload)
    except Exception as error:
        assert getattr(error, "message") == "Deck validation failed"
        assert any(detail["path"] == "slides.M1.statement" for detail in error.details)
    else:
        raise AssertionError("Expected validation error")


def test_schema_version_error(tmp_path) -> None:
    payload = sample_deck()
    payload["schema_version"] = "wrong"

    response = create_deck_response(
        format="json",
        content=payload,
        store=DeckStore(data_dir=tmp_path),
        base_url="http://localhost:3000",
    )

    assert response["error"] == "VALIDATION_ERROR"
    assert "schema_version" in response["details"][0]["path"]


def test_warnings_for_discouraged_html_and_long_text() -> None:
    payload = sample_deck()
    payload["slides"]["M1"]["statement"] = "長い" * 50
    payload["slides"]["E1"]["html"] = '<section><script>alert(1)</script><img src="https://example.com/a.png"></section>'
    deck = parse_deck_input("json", payload)

    warnings = build_warnings(deck)

    assert "M1.statement is longer than recommended length" in warnings
    assert "E1.html contains script, which is discouraged" in warnings
    assert "E1.html contains an external URL, which is discouraged" in warnings


def test_guideline_mentions_dense_evidence_and_charts() -> None:
    response = get_guideline_response()
    guideline = str(response["guideline"])

    assert "proof slide" in guideline
    assert "Inline SVG is preferred for charts" in guideline
    assert "Do not merely restate M1-M3 in E1-E2" in guideline
    assert "two-layer label strategy" in guideline
    assert "data-tooltip" in guideline
    assert "line, pie/donut, stacked bar" in guideline


def test_warnings_flag_sparse_evidence_without_quant_or_structure() -> None:
    payload = sample_deck()
    payload["slides"]["E1"]["html"] = "<section><p>懸念はある。</p></section>"
    payload["slides"]["E1"]["fallback_text"] = "読み取り：懸念は継続する。"
    deck = parse_deck_input("json", payload)

    warnings = build_warnings(deck)

    assert "E1 does not appear to include quantified evidence or explain why it is unavailable" in warnings
    assert "E1.html may be too sparse to function as an evidence capsule" in warnings


def test_warnings_allow_structural_evidence_when_no_numeric_data_is_explained() -> None:
    payload = sample_deck()
    payload["slides"]["E1"]["html"] = """
    <section style="display:grid; grid-template-columns: 1fr 1fr; gap: 12px;">
      <div><strong>制約</strong><p>調達データが非公開である。</p></div>
      <div><strong>比較</strong><ul><li>競争環境は強い</li><li>提携余地は残る</li></ul></div>
    </section>
    """.strip()
    payload["slides"]["E1"]["fallback_text"] = "公開数値データがないため、構造比較で意思決定に必要な論点を示す。"
    deck = parse_deck_input("json", payload)

    warnings = build_warnings(deck)

    assert "E1 does not appear to include quantified evidence or explain why it is unavailable" not in warnings
    assert "E1.html may be too sparse to function as an evidence capsule" not in warnings


def test_render_escapes_message_text_and_inserts_capsule() -> None:
    payload = sample_deck()
    payload["slides"]["M1"]["statement"] = "<b>escape me</b>"
    payload["slides"]["E1"]["html"] = "<section class=\"capsule\"><strong>raw capsule</strong></section>"
    deck = parse_deck_input("json", payload)

    html = render_deck_html("dck_test", deck)

    assert "&lt;b&gt;escape me&lt;/b&gt;" in html
    assert "<strong>raw capsule</strong>" in html
    assert html.count('class="slide ') == 5
    assert "window.print()" in html
    assert "@media print" in html
    assert "requestFullscreen" in html
    assert "exitFullscreen" in html
    assert 'data-fullscreen' in html
    assert 'data-pointer' in html
    assert 'class="notes-panel"' in html
    assert 'data-notes-resizer' in html
    assert "updateNotes()" in html


def test_render_exposes_evidence_takeaway_and_top_wrapper() -> None:
    deck = parse_deck_input("json", sample_deck())

    html = render_deck_html("dck_test", deck)

    assert 'class="evidence-top"' in html
    assert "flex-direction: column; gap: 14px; justify-content: flex-start; align-items: stretch;" in html
    assert "flex: 1 1 auto; display: flex; flex-direction: column; justify-content: flex-start;" in html
    assert "display: block; margin: 0; padding: 10px 14px;" in html
    assert ".deck-tooltip" in html
    assert ".laser-pointer" in html
    assert ".notes-panel" in html
    assert ".notes-resizer" in html
    assert "[data-chart-label]" in html
    assert 'document.addEventListener("pointerover"' in html
    assert 'document.addEventListener("fullscreenchange"' in html


def test_render_keeps_chart_tooltip_metadata_in_capsules() -> None:
    deck = parse_deck_input("json", sample_deck())

    html = render_deck_html("dck_test", deck)

    assert 'data-chart-bar data-label="導入前の一次回答時間"' in html
    assert "<title>導入前の一次回答時間: 19分" in html
    assert 'data-chart-series' in html



def test_create_deck_persists_html(tmp_path) -> None:
    response = create_deck_response(
        format="json",
        content=sample_deck(),
        store=DeckStore(data_dir=tmp_path),
        base_url="http://localhost:3000",
    )

    assert response["schema_version"] == "message-first-deck/v1"
    assert response["page_count"] == 5
    assert response["url"].startswith("http://localhost:3000/decks/dck_")
    assert (tmp_path / "decks" / f"{response['deck_id']}.json").exists()
    assert (tmp_path / "decks" / f"{response['deck_id']}.html").exists()


def test_create_deck_strips_script_tags_before_persisting(tmp_path) -> None:
    payload = sample_deck()
    payload["slides"]["E1"]["html"] = """
    <section class="capsule">
      <script>alert('x')</script>
      <svg viewBox="0 0 40 20"><rect x="0" y="0" width="20" height="10"></rect></svg>
    </section>
    """.strip()

    response = create_deck_response(
        format="json",
        content=payload,
        store=DeckStore(data_dir=tmp_path),
        base_url="http://localhost:3000",
    )

    html_path = tmp_path / "decks" / f"{response['deck_id']}.html"
    json_path = tmp_path / "decks" / f"{response['deck_id']}.json"
    saved_html = html_path.read_text(encoding="utf-8")
    saved_payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert "E1.html contains script, which is discouraged" in response["warnings"]
    assert "alert('x')" not in saved_html
    assert "<script" not in saved_payload["source"]["slides"]["E1"]["html"]
