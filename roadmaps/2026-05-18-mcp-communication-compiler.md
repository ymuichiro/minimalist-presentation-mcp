# MCP Roadmap: Communication Compiler Integration

- Date: 2026-05-18
- Branch: `codex/chatgpt-auth-mcp`
- Scope: MCP server, configuration, and documentation

## Goal

Keep the public MCP server focused on Message-First Deck rendering while documenting and supporting its role as a tool used by the Communication Compiler demo app.

The MCP server must remain independently callable by ChatGPT and other remote MCP clients. The Agentic interview, session state, and Free Talk interpretation belong outside the MCP server.

## Implementation Plan

1. Preserve the existing Streamable HTTP MCP endpoint at `/mcp`.
2. Preserve the two public MCP tools:
   - `get_presentation_guideline`
   - `create_message_first_deck`
3. Document that the Azure AI Foundry Agent is the orchestrator and the MCP server is the deck rendering tool.
4. Add example-app environment variables to `.env.example`.
5. Add developer commands for starting the MCP server and example app together.
6. Add documentation for architecture, concept, demo script, Message Kernel, and Foundry Agent configuration.
7. Keep authentication and deck ownership behavior on the MCP server unchanged.
8. Ensure existing MCP tests continue to pass.

## Acceptance Checks

- MCP remains reachable at `http://localhost:3000/mcp`.
- Decks remain reachable at `http://localhost:3000/decks/{deck_id}`.
- Existing authenticated ChatGPT MCP behavior is not weakened.
- README explains that this is not a generic slide generator.
- Documentation describes the Agent outside the MCP server and MCP as a tool boundary.
