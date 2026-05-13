from __future__ import annotations

from minimalist_presentation_mcp.deck.schema import SCHEMA_VERSION


GUIDELINE = """Message-First Deck is a fixed five-page business presentation format for moving decisions quickly, not for exhaustive reading.

Use these reference frameworks as compression criteria:
- Pyramid Principle: put the highest-level conclusion in M1, supported by E1/E2.
- SCQA: keep Situation and Complication behind E1, and express the Answer in M1.
- SCR: compress the Resolution into M2 as strategy, constraints, and priority.
- Audience Transformation: design M1-M3 as a Before-to-After perception shift.
- Ethos / Pathos / Logos: use E1/E2 for logic and credibility, while M1-M3 create decision necessity.
- Data Storytelling: turn data, comparisons, workflows, and structures into judgment-ready evidence capsules.
- Strategy Kernel: show diagnosis, guiding policy, and coherent action through M2 and M3.

Generation mapping:
- M1: Pyramid Principle / SCQA Answer. Compress the top conclusion into one judgment-bearing sentence. Do not write a topic label.
- M2: SCR Resolution / Strategy Kernel. Make strategy, constraints, priorities, and discarded alternatives explicit.
- M3: Audience Transformation / Call to Action. State the exact decision, next action, owner, and timing when known. Do not end with vague consideration.
- E1: SCQA Situation & Complication / Logos. Show current state, issue structure, comparisons, or analysis that materially supports M1-M3. Treat E1 as a proof slide, not a summary slide.
- E2: Resolution Feasibility / Ethos. Show execution feasibility, risk handling, objections, metrics, or plan details that materially support M1-M3. Treat E2 as a proof slide, not a summary slide.

Rules:
- Always generate exactly five pages: M1, M2, M3, E1, E2.
- M1-M3 are short structured text only.
- E1-E2 are partial HTML Capsules only, inserted into the fixed evidence area.
- E1-E2 should be visibly denser than M1-M3 and should fill the evidence area with:
  1) one clear claim,
  2) one visual proof block,
  3) two to four supporting facts, comparisons, or drivers,
  4) one short takeaway strip that tells the audience how to read the evidence.
- If credible numeric data exists, use charts or quantified comparisons inside the capsule. Inline SVG is allowed and preferred for charts.
- When building charts, keep visible labels short and stable. Do not place an unknown-length sentence directly under a narrow bar, point, or callout.
- For chart categories, use a two-layer label strategy: a compact visible label plus the full label/value/detail in tooltip text or an adjacent legend.
- Prefer the shared evidence attributes `data-chart`, `data-chart-series`, `data-chart-item`, `data-chart-label`, `data-chart-value`, `data-chart-meta`, and `data-tooltip` so the built-in slide CSS can keep labels readable.
- Add hover-readable values to chart marks whenever possible. For SVG charts, include `<title>` in each bar, point, or segment and/or set `data-tooltip` with the exact value and context.
- Make charts decision-ready, not decorative: include units, exact values or deltas, and at least one benchmark, note, ranking, or explanatory cue when the data supports it.
- If credible numeric data does not exist, explicitly say so in the evidence and use a structure visual such as a matrix, timeline, driver tree, risk map, workflow, or comparison table instead of leaving whitespace.
- Do not merely restate M1-M3 in E1-E2; add proof, mechanism, comparison, or execution detail.
- Do not leave large intentional blank areas or center a short headline above an underfilled capsule.
- Do not generate the full HTML document, navigation, print CSS, or speaker-note UI.
- Avoid external CSS, external fonts, external image URLs, external JS, iframe, script, fetch, WebSocket, html/body/head tags, @page, and position: fixed in capsules.
- Include watch, claim, html, fallback_text, and speaker_note for E1/E2.
"""


SCHEMA_SUMMARY = """Root fields: schema_version, language, title, subtitle, metadata, slides.
schema_version is fixed to message-first-deck/v1.
slides must contain M1, M2, M3, E1, and E2.
M1-M3: type=message, watch, statement, sub_message, speaker_note.
E1-E2: type=html_capsule, watch, claim, html, fallback_text, speaker_note.
Evidence capsules should usually contain a chart, table, comparison grid, timeline, driver tree, risk map, or similar proof structure. When charts are used, visible labels should stay compact and full numeric context should be exposed by tooltip text or a companion legend. fallback_text should work as a short takeaway strip.
Recommended lengths: message watch <=30 chars, statement <=80, sub_message <=140; evidence watch <=40, claim <=120, fallback_text <=200; speaker_note <=500.
"""


def get_guideline_response() -> dict[str, object]:
    return {
        "format": SCHEMA_VERSION,
        "guideline": GUIDELINE,
        "schema_summary": SCHEMA_SUMMARY,
        "recommended_workflow": [
            "Clarify the presentation purpose",
            "Identify the audience and desired perception shift",
            "Compress the core thesis into M1",
            "Define the strategic constraint or priority in M2",
            "Define the requested decision or action in M3",
            "Generate evidence HTML capsules for E1 and E2",
            "Return the complete YAML or JSON payload",
        ],
    }
