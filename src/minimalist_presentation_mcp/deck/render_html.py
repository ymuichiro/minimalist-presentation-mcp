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
    .app-shell {{
      min-height: 100vh; display: grid; grid-template-rows: auto minmax(0, 1fr);
      --notes-height: 180px;
    }}
    body.notes-visible .app-shell {{ grid-template-rows: auto minmax(0, 1fr) var(--notes-height); }}
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
    .app-shell:fullscreen {{ background: #111; }}
    .app-shell:fullscreen .toolbar {{
      position: fixed; left: 0; right: 0; top: 0; z-index: 30;
      background: rgba(17, 17, 17, 0.72); color: #fff; border-bottom-color: rgba(255, 255, 255, 0.18);
    }}
    .app-shell:fullscreen .deck-title span,
    .app-shell:fullscreen .page-indicator {{ color: rgba(255, 255, 255, 0.72); }}
    .app-shell:fullscreen button {{
      background: rgba(255, 255, 255, 0.12); color: #fff; border-color: rgba(255, 255, 255, 0.28);
    }}
    .app-shell:fullscreen button[aria-pressed="true"] {{ border-color: #ff5b50; color: #ffb3ad; }}
    .app-shell:fullscreen .stage {{ min-height: 0; padding: 58px 0 0; background: #111; }}
    .app-shell:fullscreen .deck {{
      width: min(100vw, calc((100vh - 58px) * 16 / 9));
      height: min(calc(100vh - 58px), calc(100vw * 9 / 16));
    }}
    body.notes-visible .app-shell:fullscreen .deck {{
      width: min(100vw, calc((100vh - 58px - var(--notes-height)) * 16 / 9));
      height: min(calc(100vh - 58px - var(--notes-height)), calc(100vw * 9 / 16));
    }}
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
      flex-direction: column; gap: 14px; justify-content: flex-start; align-items: stretch;
    }}
    .evidence-slide.active {{ display: flex; }}
    .evidence-top {{ display: grid; gap: 10px; align-content: start; flex: 0 0 auto; }}
    .evidence-header {{
      display: grid; grid-template-columns: minmax(220px, 0.9fr) minmax(0, 2.1fr); gap: 28px; align-items: start;
      border-bottom: 1px solid var(--line); padding-bottom: 14px;
    }}
    .evidence-header .watch {{ margin: 0; font-size: clamp(15px, 1.35vw, 20px); }}
    .evidence-header h1 {{ font-size: clamp(25px, 2.8vw, 42px); line-height: 1.2; }}
    .capsule-frame {{
      min-height: 0; flex: 1 1 auto; display: flex; flex-direction: column; justify-content: flex-start; overflow: hidden;
      background: var(--panel); border: 1px solid var(--line);
    }}
    .capsule-frame :where([data-chart]) {{
      min-width: 0; color: var(--ink);
    }}
    .capsule-frame :where([data-chart]) * {{ min-width: 0; }}
    .capsule-frame :where([data-chart-series], [data-chart-bars], [data-chart-grid], [data-chart-legend]) {{
      display: grid; gap: 12px;
    }}
    .capsule-frame :where([data-chart-series], [data-chart-bars], [data-chart-grid]) {{
      grid-template-columns: repeat(auto-fit, minmax(88px, 1fr)); align-items: end;
    }}
    .capsule-frame :where([data-chart-item], [data-chart-card], [data-chart-point], [data-chart-bar], [data-chart-callout]) {{
      min-width: 0;
    }}
    .capsule-frame :where([data-chart-card], [data-chart-item]) {{
      display: grid; grid-template-rows: minmax(0, 1fr) auto auto; gap: 8px;
    }}
    .capsule-frame :where([data-chart-label]) {{
      display: block; margin: 0; min-height: 2.8em;
      color: #2f2f2f; font-size: 12px; line-height: 1.25; text-align: center;
      overflow-wrap: anywhere; word-break: break-word;
    }}
    .capsule-frame :where([data-chart-value]) {{
      display: block; margin: 0; color: var(--ink);
      font-size: 12px; line-height: 1.2; font-weight: 700; text-align: center; white-space: nowrap;
    }}
    .capsule-frame :where([data-chart-meta]) {{
      display: block; margin: 0; color: var(--muted);
      font-size: 11px; line-height: 1.3; text-align: center; overflow-wrap: anywhere;
    }}
    .capsule-frame :where([data-tooltip], [data-chart-bar], [data-chart-point], [data-chart-segment]) {{ cursor: help; }}
    .capsule-frame :where(svg) {{ max-width: 100%; height: auto; overflow: visible; }}
    .capsule-frame :where(svg text) {{ font-family: inherit; fill: currentColor; }}
    .capsule-frame :where(svg [data-chart-label]) {{
      font-size: 11px; text-anchor: middle;
    }}
    .fallback-text {{
      display: block; margin: 0; padding: 10px 14px;
      color: #2e2e2e; background: #f1efe9; border: 1px solid var(--line);
      font-size: 14px; line-height: 1.45;
    }}
    .deck-tooltip {{
      position: fixed; left: 0; top: 0; z-index: 20; display: none;
      max-width: min(320px, 38vw); padding: 8px 10px;
      border-radius: 8px; background: rgba(22, 22, 22, 0.94); color: #fff;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
      font-size: 13px; line-height: 1.4; white-space: pre-line; pointer-events: none;
    }}
    .deck-tooltip.visible {{ display: block; }}
    .laser-pointer {{
      position: fixed; left: 0; top: 0; z-index: 40; display: none;
      width: 28px; height: 28px; margin: -14px 0 0 -14px; border-radius: 999px;
      border: 2px solid rgba(255, 255, 255, 0.88);
      background: rgba(226, 42, 28, 0.72); box-shadow: 0 0 0 9px rgba(226, 42, 28, 0.2), 0 0 24px rgba(226, 42, 28, 0.88);
      pointer-events: none;
    }}
    body.pointer-enabled .laser-pointer.visible {{ display: block; }}
    .speaker-note {{
      display: none;
    }}
    .notes-panel {{
      display: none; min-height: 96px; max-height: min(50vh, 420px);
      background: #fff; border-top: 1px solid var(--line); box-shadow: 0 -10px 24px rgba(0, 0, 0, 0.08);
      overflow: hidden;
    }}
    body.notes-visible .notes-panel {{ display: grid; grid-template-rows: 10px minmax(0, 1fr); }}
    .notes-resizer {{
      cursor: ns-resize; background: linear-gradient(to bottom, #e7e2d9, #f8f6f0);
      border-bottom: 1px solid var(--line);
    }}
    .notes-resizer::before {{
      content: ""; display: block; width: 54px; height: 3px; margin: 3px auto 0;
      border-radius: 999px; background: #b8b1a6;
    }}
    .notes-content {{
      padding: 16px 22px; overflow: auto; color: var(--ink);
      font-size: 16px; line-height: 1.55; white-space: pre-wrap;
    }}
    .notes-empty {{ color: var(--muted); }}
    .app-shell:fullscreen .notes-panel {{
      background: #171717; color: #f4f4f4; border-top-color: rgba(255, 255, 255, 0.18);
    }}
    .app-shell:fullscreen .notes-resizer {{
      background: linear-gradient(to bottom, #252525, #1a1a1a); border-bottom-color: rgba(255, 255, 255, 0.16);
    }}
    .app-shell:fullscreen .notes-resizer::before {{ background: rgba(255, 255, 255, 0.42); }}
    .app-shell:fullscreen .notes-content {{ color: #f4f4f4; }}
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
      .evidence-slide, .evidence-slide.active {{ display: flex; }}
      .speaker-note, .notes-panel, body.notes-visible .notes-panel {{ display: none; }}
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
        <button type="button" data-pointer aria-pressed="false">Pointer</button>
        <button type="button" data-fullscreen aria-pressed="false">Fullscreen</button>
        <button type="button" data-print>PDF</button>
      </div>
    </header>
    <main class="stage">
      <article class="deck" aria-label="Message-First Deck">{slides}</article>
    </main>
    <aside class="notes-panel" aria-label="Speaker notes">
      <div class="notes-resizer" data-notes-resizer aria-hidden="true"></div>
      <div class="notes-content" data-notes-content></div>
    </aside>
  </div>
  <script>
    (() => {{
      const slides = Array.from(document.querySelectorAll(".slide"));
      const shell = document.querySelector(".app-shell");
      const deck = document.querySelector(".deck");
      const indicator = document.querySelector("[data-page-indicator]");
      const notesButton = document.querySelector("[data-notes]");
      const notesPanel = document.querySelector(".notes-panel");
      const notesContent = document.querySelector("[data-notes-content]");
      const notesResizer = document.querySelector("[data-notes-resizer]");
      const pointerButton = document.querySelector("[data-pointer]");
      const fullscreenButton = document.querySelector("[data-fullscreen]");
      const tooltip = document.createElement("div");
      tooltip.className = "deck-tooltip";
      tooltip.setAttribute("aria-hidden", "true");
      document.body.appendChild(tooltip);
      const laserPointer = document.createElement("div");
      laserPointer.className = "laser-pointer";
      laserPointer.setAttribute("aria-hidden", "true");
      document.body.appendChild(laserPointer);
      let index = 0;

      function readText(node) {{
        return node ? node.textContent.replace(/\\s+/g, " ").trim() : "";
      }}

      function readTooltip(target) {{
        const explicit = target.dataset.tooltip || target.getAttribute("title") || "";
        if (explicit.trim()) return explicit.trim();
        const titleNode = target.querySelector("title");
        const titleText = readText(titleNode);
        if (titleText) return titleText;
        const label = target.dataset.label || target.getAttribute("aria-label") || readText(target.querySelector("[data-chart-label]"));
        const value = target.dataset.value || readText(target.querySelector("[data-chart-value]"));
        const detail = target.dataset.detail || readText(target.querySelector("[data-chart-meta]"));
        if (label && value && detail) return `${{label}}: ${{value}}\n${{detail}}`;
        if (label && value) return `${{label}}: ${{value}}`;
        return value || label || "";
      }}

      function getTooltipTarget(origin) {{
        if (!(origin instanceof Element)) return null;
        const target = origin.closest("[data-tooltip], [data-chart-bar], [data-chart-point], [data-chart-segment], [data-value][data-label]");
        if (!target || !target.closest(".capsule-frame")) return null;
        return readTooltip(target) ? target : null;
      }}

      function placeTooltip(event) {{
        if (!tooltip.classList.contains("visible")) return;
        const offset = 16;
        const bounds = tooltip.getBoundingClientRect();
        let left = event.clientX + offset;
        let top = event.clientY + offset;
        if (left + bounds.width > window.innerWidth - 12) left = event.clientX - bounds.width - offset;
        if (top + bounds.height > window.innerHeight - 12) top = event.clientY - bounds.height - offset;
        tooltip.style.left = `${{Math.max(12, left)}}px`;
        tooltip.style.top = `${{Math.max(12, top)}}px`;
      }}

      function showTooltip(target, event) {{
        tooltip.textContent = readTooltip(target);
        if (!tooltip.textContent) return;
        tooltip.classList.add("visible");
        tooltip.setAttribute("aria-hidden", "false");
        placeTooltip(event);
      }}

      function hideTooltip() {{
        tooltip.classList.remove("visible");
        tooltip.setAttribute("aria-hidden", "true");
      }}

      function isFullscreen() {{
        return document.fullscreenElement === shell;
      }}

      async function enterFullscreen() {{
        if (!shell.requestFullscreen || isFullscreen()) return;
        await shell.requestFullscreen();
      }}

      async function exitFullscreen() {{
        if (!document.exitFullscreen || !document.fullscreenElement) return;
        await document.exitFullscreen();
      }}

      function syncFullscreenButton() {{
        const active = isFullscreen();
        fullscreenButton.setAttribute("aria-pressed", active ? "true" : "false");
        fullscreenButton.textContent = active ? "Exit" : "Fullscreen";
      }}

      function showLaserPointer(event) {{
        if (!document.body.classList.contains("pointer-enabled")) return;
        if (!deck.contains(event.target)) {{
          laserPointer.classList.remove("visible");
          return;
        }}
        laserPointer.style.left = `${{event.clientX}}px`;
        laserPointer.style.top = `${{event.clientY}}px`;
        laserPointer.classList.add("visible");
      }}

      function hideLaserPointer() {{
        laserPointer.classList.remove("visible");
      }}

      function updateNotes() {{
        const activeNote = slides[index].querySelector(".speaker-note");
        const text = activeNote ? activeNote.textContent.trim() : "";
        notesContent.textContent = text || "No speaker notes for this slide.";
        notesContent.classList.toggle("notes-empty", !text);
      }}

      function clampNotesHeight(height) {{
        const maxHeight = Math.min(420, window.innerHeight * 0.5);
        return Math.max(96, Math.min(maxHeight, height));
      }}

      function show(nextIndex) {{
        index = Math.max(0, Math.min(slides.length - 1, nextIndex));
        slides.forEach((slide, slideIndex) => slide.classList.toggle("active", slideIndex === index));
        indicator.textContent = `${{index + 1}} / ${{slides.length}}`;
        updateNotes();
      }}
      document.querySelector("[data-prev]").addEventListener("click", () => show(index - 1));
      document.querySelector("[data-next]").addEventListener("click", () => show(index + 1));
      notesButton.addEventListener("click", () => {{
        const visible = document.body.classList.toggle("notes-visible");
        notesButton.setAttribute("aria-pressed", visible ? "true" : "false");
      }});
      notesResizer.addEventListener("pointerdown", (event) => {{
        event.preventDefault();
        notesResizer.setPointerCapture(event.pointerId);
        const startY = event.clientY;
        const startHeight = notesPanel.getBoundingClientRect().height;
        function drag(moveEvent) {{
          const nextHeight = clampNotesHeight(startHeight + startY - moveEvent.clientY);
          shell.style.setProperty("--notes-height", `${{nextHeight}}px`);
        }}
        function stop(upEvent) {{
          notesResizer.releasePointerCapture(upEvent.pointerId);
          window.removeEventListener("pointermove", drag);
          window.removeEventListener("pointerup", stop);
          window.removeEventListener("pointercancel", stop);
        }}
        window.addEventListener("pointermove", drag);
        window.addEventListener("pointerup", stop);
        window.addEventListener("pointercancel", stop);
      }});
      pointerButton.addEventListener("click", () => {{
        const active = document.body.classList.toggle("pointer-enabled");
        pointerButton.setAttribute("aria-pressed", active ? "true" : "false");
        if (!active) hideLaserPointer();
      }});
      fullscreenButton.addEventListener("click", () => {{
        if (isFullscreen()) exitFullscreen();
        else enterFullscreen();
      }});
      document.addEventListener("pointerover", (event) => {{
        const target = getTooltipTarget(event.target);
        if (!target) return;
        showTooltip(target, event);
      }});
      document.addEventListener("pointermove", (event) => {{
        const target = getTooltipTarget(event.target);
        if (!target) {{
          hideTooltip();
          return;
        }}
        showTooltip(target, event);
      }});
      document.addEventListener("pointermove", showLaserPointer);
      deck.addEventListener("pointerleave", hideLaserPointer);
      document.addEventListener("pointerdown", hideTooltip);
      document.addEventListener("scroll", hideTooltip, true);
      document.addEventListener("fullscreenchange", syncFullscreenButton);
      document.querySelector("[data-print]").addEventListener("click", () => window.print());
      window.addEventListener("keydown", (event) => {{
        if (event.key === "ArrowLeft") show(index - 1);
        if (event.key === "ArrowRight") show(index + 1);
        if (event.key === "Escape" && isFullscreen()) exitFullscreen();
        if (event.key.toLowerCase() === "n" && !event.metaKey && !event.ctrlKey && !event.altKey) notesButton.click();
      }});
      show(0);
    }})();
  </script>
</body>
</html>
"""
