# Architecture

```text
User Free Talk
    ↓
Simple Web UI
    ↓
App Backend
    ↓
Azure AI Foundry Agent
    ├─ Claim Candidate Extraction
    ├─ 4-Line Message Kernel
    ├─ Diagnosis
    ├─ Evidence Grounding
    └─ Deck Payload Builder
          ↓
Minimalist Presentation MCP
          ↓
Five-page Message-First Deck
```

## Boundaries

The MCP server owns only the fixed deck-generation contract:

- `get_presentation_guideline`
- `create_message_first_deck`
- deck persistence
- `/decks/{deck_id}` HTML rendering
- remote MCP authentication when exposed to ChatGPT

The example app under `/example` owns the demo workflow:

- session state
- Free Talk intake
- Agent orchestration
- claim candidate selection
- Message Kernel revisions
- evidence grounding
- brief generation
- Idea Map generation
- UI state

Keeping the Agent outside the MCP server makes the tool boundary explicit and keeps the Azure AI Foundry story visible.

## Local Ports

- MCP server: `http://localhost:3000/mcp`
- Deck view: `http://localhost:3000/decks/{deck_id}`
- Example app: `http://localhost:8080`
