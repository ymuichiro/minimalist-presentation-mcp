# Example Roadmap: Communication Compiler Demo

- Date: 2026-05-18
- Branch: `codex/chatgpt-auth-mcp`
- Scope: `/example`

## Goal

Build a contest-ready demo application that makes the Agentic communication workflow visible:

```text
Free Talk
  -> Claim Candidates
  -> 4-Line Message Kernel
  -> Diagnosis
  -> Evidence / Gaps / Objections
  -> Idea Map
  -> Deck / Brief outputs
```

The demo app is separate from the public MCP server. It may use dummy auth and mock Agent behavior by default, but it must expose an Azure AI Foundry Agent adapter so the same API server can be switched to a real Foundry Agent.

## Implementation Plan

1. Add a FastAPI app under `/example` with its own session model, file storage, static UI, and `/healthz`.
2. Implement session APIs for Free Talk, claim extraction, claim selection, kernel refinement, evidence grounding, deck generation, brief generation, and idea-map retrieval.
3. Add an `AgentClient` interface with `mock` and `foundry` providers.
4. Keep `mock` deterministic and demo-ready; use it as the default provider for local development.
5. Implement the Foundry provider as an optional adapter using Azure AI Foundry project endpoint and agent id configuration.
6. Add mock evidence fixtures and deterministic grounding behavior that never invents unsupported sources.
7. Call the existing MCP endpoint for deck generation; allow an explicit local fallback for demo resilience.
8. Build a Vercel-inspired single-page UI with staged sections rather than a chat surface.
9. Add tests covering the session flow, guardrails, brief output, idea-map output, and deck payload generation.

## Acceptance Checks

- `GET /example` or the example root displays the demo UI.
- A user can run the full demo flow from sample Free Talk to deck URL and brief URL.
- The UI shows intermediate artifacts, not just final slides.
- The backend can switch `AGENT_PROVIDER=mock` or `AGENT_PROVIDER=foundry`.
- The mock provider works without Azure credentials.
- Evidence gaps and objections are shown before deck generation.
- Brief output is available without requiring deck generation.
