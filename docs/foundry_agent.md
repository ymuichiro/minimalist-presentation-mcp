# Azure AI Foundry Agent

The demo backend supports two Agent providers:

```dotenv
AGENT_PROVIDER=mock
AGENT_PROVIDER=foundry
```

`mock` is deterministic and works without credentials. It is the default provider for local demo reliability.

`foundry` uses an Azure AI Foundry Agent configured by:

```dotenv
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=
AZURE_AI_FOUNDRY_AGENT_NAME=
AZURE_AI_FOUNDRY_AGENT_VERSION=
AZURE_AI_FOUNDRY_AGENT_ID=
AZURE_OPENAI_DEPLOYMENT_NAME=
```

For the current `azure-ai-projects` 2.x path, prefer `AZURE_AI_FOUNDRY_AGENT_NAME`.
`AZURE_AI_FOUNDRY_AGENT_ID` is retained only for legacy/classic SDK compatibility.

Install optional dependencies before using Foundry:

```bash
uv sync --extra foundry
```

Validate a live `.env` shape without making Azure API calls:

```bash
cp .env.live.example .env.live
make validate-live-env
```

## Agent Instructions

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

## Rules

- Return parseable JSON only.
- Do not ask many generic interview questions.
- Prefer extracting structure from the user's rough speech.
- Ask only the minimum questions needed to resolve ambiguity.
- Always separate claim, evidence, objection, and requested action.
- Do not invent internal data.
- Mark uncertain evidence as uncertain.
- Treat the five-page deck as an output UI, not the main reasoning artifact.

## P0 Reliability Path

For demo reliability, the Foundry Agent may return structured JSON and the backend may call the MCP server after receiving the deck payload.

```text
Foundry Agent returns deck payload
  -> backend calls MCP create_message_first_deck
  -> UI receives deck URL
```
