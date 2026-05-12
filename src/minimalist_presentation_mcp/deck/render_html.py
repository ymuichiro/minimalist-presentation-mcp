from __future__ import annotations

from html import escape

from minimalist_presentation_mcp.deck.schema import DeckIR, EvidenceSlide, MessageSlide


def _message_slide(page: str, role: str, slide: MessageSlide) -> str:
    return f"""
    <section class="slide message-slide" data-page="{page}" aria-label="{escape(role)}">
      <div class="slide-kicker">{escape(page)} / {escape(role)}</div>
      <p class="watch">{escape(slide.watch)}</p>
      <h1>{escape(slide.statement)}</h1>
      <p class="sub-message">{escape(slide.sub_message)}</p>
      <aside class="speaker-note" aria-label="Speaker note">{escape(slide.speaker_note or "")}</aside>
    </section>
    """


def _evidence_slide(page: str, role: str, slide: EvidenceSlide) -> str:
    return f"""
    <section class="slide evidence-slide" data-page="{page}" aria-label="{escape(role)}">
      <div class="evidence-top">
        <div class="slide-kicker">{escape(page)} / {escape(role)}</div>
        <div class="evidence-header">
          <p class="watch">{escape(slide.watch)}</p>
          <h1>{escape(slide.claim)}</h1>
        </div>
      </div>
      <div class="capsule-frame" aria-label="HTML Capsule">
        {slide.html}
      </div>
      <p class="fallback-text">{escape(slide.fallback_text)}</p>
      <aside class="speaker-note" aria-label="Speaker note">{escape(slide.speaker_note or "")}</aside>
    </section>
    """


def render_deck_html(deck_id: str, deck: DeckIR) -> str:
    title = escape(deck.title)
    subtitle = escape(deck.subtitle or "")
    metadata_bits = [deck.metadata.audience, deck.metadata.purpose, deck.metadata.desired_action]
    metadata = " / ".join(escape(bit) for bit in metadata_bits if bit)
    slides = "\n".join(
        [
            _message_slide("M1", "Core Thesis", deck.slides.M1),
            _message_slide("M2", "Constraint / Strategy", deck.slides.M2),
            _message_slide("M3", "Decision / Action", deck.slides.M3),
            _evidence_slide("E1", "Evidence 1", deck.slides.E1),
            _evidence_slide("E2", "Evidence 2", deck.slides.E2),
        ]
    )

    return f"""<!doctype html>
<html lang="{escape(deck.language or "ja-JP")}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #161616;
      --muted: #676767;
      --line: #d9d9d9;
      --paper: #fbfaf7;
      --accent: #8f2f2b;
      --panel: #ffffff;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #ece9e3; color: var(--ink); }}
    .app-shell {{ min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }}
    .toolbar {{
      display: flex; align-items: center; gap: 12px; padding: 10px 16px;
      background: rgba(255, 255, 255, 0.96); border-bottom: 1px solid var(--line);
      position: sticky; top: 0; z-index: 5;
    }}
    .deck-title {{
      min-width: 0; flex: 1; display: flex; align-items: baseline; gap: 10px;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .deck-title strong, .deck-title span {{ overflow: hidden; text-overflow: ellipsis; }}
    .deck-title span {{ color: var(--muted); font-size: 13px; }}
    .nav-buttons {{ display: flex; gap: 6px; align-items: center; }}
    button {{
      border: 1px solid var(--line); background: var(--panel); color: var(--ink);
      height: 34px; min-width: 34px; border-radius: 6px; padding: 0 11px;
      cursor: pointer; font: inherit; font-size: 13px;
    }}
    button[aria-pressed="true"] {{ border-color: var(--accent); color: var(--accent); }}
    .stage {{ display: grid; place-items: center; padding: 20px; }}
    .deck {{ width: min(1280px, calc(100vw - 40px)); aspect-ratio: 16 / 9; position: relative; }}
    .slide {{
      display: none; width: 100%; height: 100%; aspect-ratio: 16 / 9; overflow: hidden;
      background: var(--paper); border: 1px solid #d6d0c7;
      box-shadow: 0 18px 42px rgba(0, 0, 0, 0.14); position: relative;
    }}
    .slide.active {{ display: block; }}
    .message-slide {{ padding: 7.2% 8%; }}
    .slide-kicker {{
      color: var(--accent); font-size: clamp(14px, 1.2vw, 19px);
      font-weight: 700; letter-spacing: 0; text-transform: uppercase;
    }}
    .watch {{
      margin: 4.8% 0 2.2%; color: var(--muted);
      font-size: clamp(18px, 2vw, 28px); line-height: 1.35;
    }}
    h1 {{
      margin: 0; max-width: 1030px; font-size: clamp(42px, 5.4vw, 74px);
      line-height: 1.09; letter-spacing: 0; text-wrap: balance;
    }}
    .sub-message {{
      margin: 4% 0 0; max-width: 900px; color: #393939;
      font-size: clamp(20px, 2.15vw, 31px); line-height: 1.48;
    }}
    .evidence-slide {{
      padding: 4.2% 4.8% 3.8%; display: none;
      grid-template-rows: auto minmax(0, 1fr) auto; gap: 14px; align-content: start;
    }}
    .evidence-slide.active {{ display: grid; }}
    .evidence-top {{ display: grid; gap: 10px; align-content: start; }}
    .evidence-header {{
      display: grid; grid-template-columns: minmax(220px, 0.9fr) minmax(0, 2.1fr); gap: 28px; align-items: start;
      border-bottom: 1px solid var(--line); padding-bottom: 14px;
    }}
    .evidence-header .watch {{ margin: 0; font-size: clamp(15px, 1.35vw, 20px); }}
    .evidence-header h1 {{ font-size: clamp(25px, 2.8vw, 42px); line-height: 1.2; }}
    .capsule-frame {{
      min-height: 0; height: 100%; overflow: hidden;
      background: var(--panel); border: 1px solid var(--line);
    }}
    .fallback-text {{
      display: block; margin: 0; padding: 10px 14px;
      color: #2e2e2e; background: #f1efe9; border: 1px solid var(--line);
      font-size: 14px; line-height: 1.45;
    }}
    .speaker-note {{
      display: none; position: absolute; left: 0; right: 0; bottom: 0; z-index: 3;
      padding: 14px 18px; background: rgba(22, 22, 22, 0.9); color: #fff;
      font-size: 16px; line-height: 1.45; max-height: 28%; overflow: auto;
    }}
    body.notes-visible .speaker-note {{ display: block; }}
    .page-indicator {{ color: var(--muted); font-size: 13px; min-width: 52px; text-align: center; }}
    @page {{ size: 16in 9in; margin: 0; }}
    @media print {{
      body {{ background: #fff; }}
      .toolbar {{ display: none; }}
      .stage {{ display: block; padding: 0; }}
      .deck {{ width: 100%; height: auto; aspect-ratio: auto; }}
      .slide, .slide.active, .evidence-slide, .evidence-slide.active {{
        display: block; width: 16in; height: 9in; border: 0; box-shadow: none;
        page-break-after: always; break-after: page;
      }}
      .evidence-slide, .evidence-slide.active {{ display: grid; }}
      .speaker-note, body.notes-visible .speaker-note {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="app-shell" data-deck-id="{escape(deck_id)}">
    <header class="toolbar">
      <div class="deck-title">
        <strong>{title}</strong>
        <span>{subtitle}</span>
        <span>{metadata}</span>
      </div>
      <div class="nav-buttons" role="navigation" aria-label="Deck navigation">
        <button type="button" data-prev aria-label="Previous slide">←</button>
        <span class="page-indicator" data-page-indicator>1 / 5</span>
        <button type="button" data-next aria-label="Next slide">→</button>
        <button type="button" data-notes aria-pressed="false">Notes</button>
        <button type="button" data-print>PDF</button>
      </div>
    </header>
    <main class="stage">
      <article class="deck" aria-label="Message-First Deck">{slides}</article>
    </main>
  </div>
  <script>
    (() => {{
      const slides = Array.from(document.querySelectorAll(".slide"));
      const indicator = document.querySelector("[data-page-indicator]");
      const notesButton = document.querySelector("[data-notes]");
      let index = 0;
      function show(nextIndex) {{
        index = Math.max(0, Math.min(slides.length - 1, nextIndex));
        slides.forEach((slide, slideIndex) => slide.classList.toggle("active", slideIndex === index));
        indicator.textContent = `${{index + 1}} / ${{slides.length}}`;
      }}
      document.querySelector("[data-prev]").addEventListener("click", () => show(index - 1));
      document.querySelector("[data-next]").addEventListener("click", () => show(index + 1));
      notesButton.addEventListener("click", () => {{
        const visible = document.body.classList.toggle("notes-visible");
        notesButton.setAttribute("aria-pressed", visible ? "true" : "false");
      }});
      document.querySelector("[data-print]").addEventListener("click", () => window.print());
      window.addEventListener("keydown", (event) => {{
        if (event.key === "ArrowLeft") show(index - 1);
        if (event.key === "ArrowRight") show(index + 1);
        if (event.key.toLowerCase() === "n" && !event.metaKey && !event.ctrlKey && !event.altKey) notesButton.click();
      }});
      show(0);
    }})();
  </script>
</body>
</html>
"""
