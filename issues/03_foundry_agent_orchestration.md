# Issue 03: Implement Azure AI Foundry Agent Orchestration Layer

## Summary

Create the integration layer that allows the app backend to call an Azure AI Foundry Agent for Free Talk interpretation, claim extraction, Message Kernel refinement, evidence grounding, and MCP deck generation.

## Background

The contest application should visibly use Azure AI Foundry as the main Agent runtime. The existing MCP server should be attached as a tool used by the Agent, not as the owner of the conversation.

The Foundry Agent must be responsible for the communication-structuring workflow.

## Scope

Implement a backend adapter for Agent runs.

The adapter should support:

- Running claim candidate extraction
- Running Message Kernel generation/refinement
- Running diagnosis
- Running evidence grounding
- Calling MCP tool directly or through the Agent
- Returning structured JSON to the backend

## Recommended Design

Create an interface so local development can use a mock Agent.

```python
class AgentClient:
    def extract_claim_candidates(self, session: Session) -> list[ClaimCandidate]:
        ...

    def refine_message_kernel(self, session: Session, user_feedback: str | None) -> AgentKernelResult:
        ...

    def ground_evidence(self, session: Session) -> EvidenceGroundingResult:
        ...

    def build_deck_payload(self, session: Session) -> dict:
        ...
```

Implement:

```text
app/agent/base.py
app/agent/mock_agent.py
app/agent/foundry_agent.py
```

The backend should switch implementation with:

```dotenv
AGENT_PROVIDER=mock | foundry
```

## Foundry Agent Instructions

Create or document the Agent instructions.

The Agent identity:

```text
You are a Communication Compiler Agent.

Your job is not to create slides immediately.
Your job is to help the user discover and sharpen what they actually want to say.

You convert rough user input into:
1. claim candidates
2. a 4-Line Message Kernel
3. diagnosis of weaknesses
4. evidence gaps and objections
5. final Message-First Deck payload
```

The Agent must follow these principles:

```text
- Do not ask many generic interview questions.
- Prefer extracting structure from the user's rough speech.
- Ask only the minimum questions needed to resolve ambiguity.
- Always separate claim, evidence, objection, and requested action.
- Do not invent internal data.
- Mark uncertain evidence as uncertain.
- Treat the five-page deck as an output UI, not the main reasoning artifact.
```

## Output Contract

All Agent calls must return parseable JSON. Do not rely on natural-language-only responses.

### Claim Extraction Output

```json
{
  "claim_candidates": [
    {
      "claim_id": "claim_1",
      "title": "...",
      "summary": "...",
      "angle": "strategy",
      "why_this_may_be_true": ["..."],
      "potential_weakness": ["..."]
    }
  ],
  "recommended_next_question": "この3案のうち、どれが一番近いですか？"
}
```

### Kernel Refinement Output

```json
{
  "message_kernel": {
    "revision": 1,
    "premise": "...",
    "complication": "...",
    "claim": "...",
    "action": "...",
    "confidence": 0.82,
    "notes": ["..."]
  },
  "diagnosis": {
    "overall_score": 82,
    "strengths": ["..."],
    "issues": [
      {
        "severity": "high",
        "field": "action",
        "message": "..."
      }
    ],
    "recommended_questions": ["..."]
  }
}
```

### Evidence Grounding Output

```json
{
  "supporting_evidence": [
    {
      "evidence_id": "ev_1",
      "title": "...",
      "summary": "...",
      "source_type": "internal_doc | meeting_note | user_statement | mock | external",
      "source_ref": "...",
      "strength": "strong | medium | weak",
      "supports_kernel_line": "premise | complication | claim | action"
    }
  ],
  "evidence_gaps": [
    {
      "gap_id": "gap_1",
      "description": "...",
      "why_it_matters": "...",
      "suggested_source": "..."
    }
  ],
  "objections": [
    {
      "objection_id": "obj_1",
      "objection": "...",
      "response_strategy": "...",
      "evidence_needed": "..."
    }
  ]
}
```

### Deck Payload Output

This output must be compatible with the existing MCP `create_message_first_deck` tool.

```json
{
  "format": "json",
  "content": {
    "schema_version": "message-first-deck/v1",
    "language": "ja-JP",
    "title": "...",
    "subtitle": "...",
    "metadata": {
      "audience": "...",
      "purpose": "...",
      "desired_action": "..."
    },
    "slides": {
      "M1": {},
      "M2": {},
      "M3": {},
      "E1": {},
      "E2": {}
    }
  }
}
```

## Tool Use Policy

The Agent may use tools only after the Message Kernel exists.

Expected order:

```text
1. Extract claim candidates
2. User selects or comments
3. Create/refine Message Kernel
4. Diagnose
5. Evidence grounding
6. Generate deck payload
7. Call MCP deck tool
```

Do not let the Agent generate the deck before Message Kernel diagnosis.

## MCP Tool Connection

If Foundry Agent is configured to call the MCP directly, expose the existing MCP endpoint:

```text
http://localhost:3000/mcp
```

or production endpoint:

```text
https://{public-host}/mcp
```

If direct MCP tool calling is not ready, the backend may call the MCP after receiving the deck payload from the Agent.

Preferred for P0 reliability:

```text
Foundry Agent returns deck payload
→ backend calls MCP create_message_first_deck
```

This makes debugging easier.

## Logging

Store a concise trace summary in each session:

```json
[
  {
    "step": "extract_claim_candidates",
    "status": "success",
    "model": "...",
    "duration_ms": 1200,
    "summary": "Generated 3 claim candidates"
  }
]
```

Do not store full prompts with secrets or sensitive internal data unless explicitly required for debugging.

## Acceptance Criteria

- Backend can switch between mock Agent and Foundry Agent.
- Agent responses are parsed as JSON.
- Invalid Agent JSON is handled with a clear error.
- Claim extraction works through the adapter.
- Kernel refinement works through the adapter.
- Evidence grounding works through the adapter or mock.
- Deck payload generation works through the adapter.
- Agent run summaries are stored in the session.

## Test Plan

Unit tests:

- Mock Agent returns valid claim candidates.
- Mock Agent returns valid kernel.
- Invalid JSON handling.
- Session trace logging.

Manual tests:

1. Set `AGENT_PROVIDER=mock`.
2. Run full flow without Azure.
3. Set `AGENT_PROVIDER=foundry`.
4. Run at least claim extraction with Foundry Agent.
5. Confirm structured JSON is saved.

## Non-Goals

Do not implement a complex multi-agent system here. One orchestrating Agent is enough for the contest demo.
