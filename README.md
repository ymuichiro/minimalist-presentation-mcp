# Minimalist Presentation MCP / Communication Compiler

This project is not a generic slide generator.

It is a communication-structuring application powered by an Azure AI Foundry Agent.
The Agent listens to rough user thoughts, extracts possible claims, compresses the selected claim into a 4-Line Message Kernel, diagnoses contradictions and evidence gaps, and then calls the Minimalist Presentation MCP server to expand the refined message into a five-page Message-First Deck.

The deck is the UI.
The real output is a sharpened business message.

このプロジェクトは、単なるスライド生成ツールではありません。

Azure AI Foundry Agent がユーザーの雑な発話を受け取り、言いたいことの候補を抽出し、選ばれた主張を 4-Line Message Kernel に圧縮し、矛盾・根拠不足・反論可能性を診断したうえで、Minimalist Presentation MCP を呼び出して5枚の Message-First Deck へ展開します。

スライドは UI です。本当の成果物は、研ぎ澄まされたビジネスメッセージです。

## Architecture

The public MCP server remains a small tool boundary:

- `GET/POST /mcp`: Streamable HTTP MCP endpoint
- `get_presentation_guideline`: generation rules for Message-First Decks
- `create_message_first_deck`: fixed five-page HTML deck renderer

The contest demo app is separate under `/example`:

- Free Talk intake
- claim candidate extraction
- 4-Line Message Kernel refinement and diagnosis
- evidence gaps and objections
- Idea Map
- deck and brief output links

The Azure AI Foundry Agent is the orchestrator. The MCP server is the deck-rendering tool.

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

## Run the Communication Compiler Demo

Start the MCP server:

```bash
make run
```

In another terminal, start the demo app:

```bash
make run-example
```

Open:

```text
http://localhost:8080
```

Default demo settings use the deterministic mock Agent. To connect an Azure AI Foundry Agent:

```bash
uv sync --extra foundry
AGENT_PROVIDER=foundry \
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://... \
AZURE_AI_FOUNDRY_AGENT_ID=... \
make run-example
```

The demo app calls `MESSAGE_FIRST_MCP_ENDPOINT` for deck generation. For local contest demos, `MESSAGE_FIRST_MCP_ALLOW_LOCAL_FALLBACK=true` keeps the demo usable if the MCP server is temporarily unavailable.

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

## Authentication

Set these values before exposing the app as an authenticated ChatGPT MCP server:

```dotenv
AUTH_ENABLED=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-long-random-password
PUBLIC_BASE_URL=https://zen-presentation.notelligent.app
ALLOWED_HOSTS=127.0.0.1,localhost,app.internal,zen-presentation.notelligent.app
ALLOWED_REDIRECT_ORIGINS=https://chat.openai.com,https://chatgpt.com
```

The app exposes OAuth-compatible endpoints for ChatGPT remote MCP connections:

- `/.well-known/oauth-protected-resource`
- `/.well-known/oauth-protected-resource/mcp`
- `/.well-known/oauth-authorization-server`
- `/register`
- `/authorize`
- `/token`
- `/revoke`
- `/mcp`

The login provider is local username/password. Browser pages under `/dashboard`,
`/mypage`, and `/decks/{deck_id}` require a valid app session when auth is
enabled. Decks created through authenticated MCP calls are owned by the logged-in
user and are not visible to other users. Dynamic OAuth client registration only
accepts redirect URI origins listed in `ALLOWED_REDIRECT_ORIGINS`.

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
