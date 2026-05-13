Minimalist Presentation MCP
===========================

HTTP Streamable MCP server for generating fixed five-page Message-First Deck presentations.

## Run

```bash
uv run python main.py
```

Defaults:

- MCP endpoint: `http://localhost:3000/mcp`
- Deck view: `http://localhost:3000/decks/{deck_id}`
- Health check: `http://localhost:3000/healthz`

The package also installs a console command:

```bash
uv run minimalist-presentation-mcp
```

## Cloudflare Named Tunnel

This repo follows the same maintained pattern as the other remote MCP servers in
`~/github/ymuichiro`: Docker Compose runs the app on an internal network,
`localproxy` exposes only a local loopback port for operator checks, and
`cloudflared` is enabled only through the `tunnel` profile.

Create `.env` and fill in the public Cloudflare hostname and Named Tunnel token:

```bash
make init-env
```

Example `.env` values:

```dotenv
APP_PORT=13000
PUBLIC_BASE_URL=https://message-first-deck.example.com
ALLOWED_HOSTS=127.0.0.1,localhost,app.internal,message-first-deck.example.com
CLOUDFLARE_TUNNEL_TOKEN=...
```

Start local-only:

```bash
make up
curl http://127.0.0.1:13000/healthz
```

Start with the named Cloudflare Tunnel:

```bash
make up-tunnel
```

Remote MCP clients should connect to:

```text
https://message-first-deck.example.com/mcp
```

`ALLOWED_HOSTS` must include the public tunnel hostname. The MCP transport uses
DNS rebinding protection, so requests for unlisted hostnames are rejected.

## Tools

- `get_presentation_guideline`
- `create_message_first_deck`

`create_message_first_deck` accepts:

```json
{
  "format": "yaml",
  "content": "schema_version: message-first-deck/v1\n..."
}
```

or:

```json
{
  "format": "json",
  "content": {
    "schema_version": "message-first-deck/v1",
    "title": "...",
    "slides": {}
  }
}
```

Generated decks are persisted under `data/decks/`.

## Evidence slide contract

- `M1`-`M3` are intentionally terse message slides.
- `E1` and `E2` are proof slides and should be denser than `M1`-`M3`.
- When credible numeric data exists, `E1`/`E2` should prefer quantified comparisons or small charts inside the HTML capsule. Inline SVG is the preferred chart medium.
- Recommended SVG chart families are bar/column, line, pie/donut, stacked bar, waterfall, scatter, and timeline-like quantitative visuals. Pick the simplest one that matches the data and label density.
- Keep evidence charts SVG-based inside the capsule. Avoid canvas, runtime chart libraries, and data fetching inside evidence slides.
- For charts with variable label length, keep the visible axis/category label compact and move the full label, exact value, and context into tooltip text or a nearby legend row.
- The shared capsule helpers `data-chart`, `data-chart-series`, `data-chart-item`, `data-chart-label`, `data-chart-value`, `data-chart-meta`, and `data-tooltip` are supported by the renderer and help keep charts readable when wording changes.
- For hover inspection, add `data-tooltip` and/or an SVG `<title>` to each bar, point, or segment so the exact number can be read on mouseover.
- Charts should be decision-ready rather than decorative: include units, exact values or deltas, and a benchmark, note, ranking, or explanatory cue when the evidence supports it.
- When numeric evidence is unavailable, the capsule should say so and use a structure visual such as a comparison grid, timeline, driver tree, workflow, or risk map instead of leaving empty space.
- `fallback_text` should read like a short takeaway strip that explains how to interpret the evidence.
- If a model emits `<script>` inside an evidence capsule, the server strips it before persistence and rendering.
