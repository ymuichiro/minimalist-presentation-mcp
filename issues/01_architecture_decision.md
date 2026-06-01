# Issue 01: Adopt Simple Web UI + Azure AI Foundry Agent + MCP Tool Architecture

## Summary

Define and implement the target architecture where the Azure AI Foundry Agent owns the communication-structuring workflow, and the existing MCP server remains a tool for generating Message-First Decks.

## Background

The current repository is an MCP server that exposes deck-generation tools. This is a good tool boundary. However, the contest application needs to demonstrate an Agentic workflow, not merely a deck renderer.

The key product experience is:

```text
User speaks roughly
→ Agent extracts what the user wants to say
→ Agent compresses it into a 4-Line Message Kernel
→ Agent diagnoses weaknesses
→ Agent grounds the claim with evidence and objections
→ Agent calls the MCP server to create a five-page deck
```

The Agent must be visible as the orchestrator. It should not be hidden inside the MCP server.

## Decision

Use this architecture:

```text
Simple Web UI
  ↓
App Backend
  ↓
Azure AI Foundry Agent
  ↓
Existing Minimalist Presentation MCP
```

## Responsibilities

### Simple Web UI

Responsible for:

- Free Talk input
- Displaying claim candidates
- Displaying the 4-Line Message Kernel
- Displaying diagnosis, evidence gaps, objections
- Displaying Idea Map
- Displaying output links:
  - deck
  - brief
  - optional image

### App Backend

Responsible for:

- Session creation
- Persisting session state
- Calling Azure AI Foundry Agent
- Returning structured intermediate outputs to the UI
- Calling local helper services if needed
- Storing generated artifacts

### Azure AI Foundry Agent

Responsible for:

- Understanding Free Talk
- Extracting claim candidates
- Creating and refining the 4-Line Message Kernel
- Diagnosing message quality
- Searching or requesting evidence
- Calling MCP tools
- Returning structured JSON outputs

### Minimalist Presentation MCP

Responsible for:

- Returning deck-generation guidelines
- Accepting validated deck IR
- Rendering five-page HTML deck
- Returning `deck_id` and deck URL

The MCP server must not own:

- user interview logic
- conversation state
- long-running session orchestration
- claim candidate generation
- evidence search decisions

## Why Not Put the Agent Inside the MCP Server?

Do not implement the interview Agent inside the MCP server.

Reasons:

1. It makes the Agent/tool boundary unclear.
2. It weakens the Azure AI Foundry story for the contest.
3. It causes a nested Agent problem if the client is ChatGPT or another LLM.
4. It makes UI traceability harder.
5. It bloats the MCP server with application logic.

## Why Not Use ChatGPT as the Main UI?

ChatGPT + MCP is useful for development verification, but it should not be the main contest demo.

Reasons:

1. The hackathon rewards visible Microsoft Agent usage.
2. A custom UI can show intermediate artifacts better.
3. ChatGPT UI makes the result look like a generic slide-generation conversation.
4. The key experience is the refinement process, not just the final deck URL.

## Deliverables

- Architecture diagram in Markdown
- Updated README section explaining the architecture
- App backend skeleton
- Foundry Agent connection placeholder
- MCP endpoint configuration
- `.env.example` entries for all required endpoints and keys

## Environment Variables

Add or document the following variables.

```dotenv
# App
APP_BASE_URL=http://localhost:8080
APP_ENV=local

# Azure AI Foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=
AZURE_AI_FOUNDRY_AGENT_ID=
AZURE_AI_FOUNDRY_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=

# MCP
MESSAGE_FIRST_MCP_ENDPOINT=http://localhost:3000/mcp
MESSAGE_FIRST_PUBLIC_BASE_URL=http://localhost:3000

# Storage
APP_DATA_DIR=./data/app

# Optional evidence mock
EVIDENCE_FIXTURE_DIR=./fixtures/evidence
```

## Acceptance Criteria

- The repository contains a clear architecture document.
- The MCP server remains callable independently.
- The app backend can be run separately from the MCP server.
- The backend has configuration for Azure AI Foundry Agent and MCP endpoint.
- The README clearly states that the Agent is outside the MCP server.
- The README clearly states that the MCP server is used as a tool by the Agent.
- A developer can run the MCP server and app backend locally using documented commands.

## Test Plan

Manual test:

1. Start the existing MCP server.
2. Start the app backend.
3. Confirm `/healthz` works on both services.
4. Confirm the app backend can read MCP endpoint configuration.
5. Confirm a placeholder Agent run can be triggered or mocked.

## Notes

Keep this issue focused on architectural separation. Do not implement Free Talk parsing or deck generation logic here.
