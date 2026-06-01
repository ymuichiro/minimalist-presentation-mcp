# ChatGPT Authenticated MCP Work Log

- Created: 2026-05-16
- Branch: `codex/chatgpt-auth-mcp`
- Base branch: `main`

## Goal

Implement an authenticated remote MCP application that connects correctly from ChatGPT using a ChatGPT/MCP-compatible OAuth flow.

The application must support:

- ChatGPT connecting to `/mcp` with authentication.
- OAuth 2.1 Authorization Code + PKCE S256 for ChatGPT MCP access.
- An application-owned username/password login flow.
- Only authenticated users accessing generated presentation decks.
- Authenticated users viewing a simple dashboard listing their own generated decks.

## Required Security Rules

- `/mcp` must require a valid bearer access token.
- Generated deck pages under `/decks/{deck_id}` must be accessible only to the user who created the deck.
- The dashboard must be accessible only to authenticated users.
- Authorization codes must be short-lived and single-use.
- PKCE must require `code_challenge_method=S256`.
- OAuth `redirect_uri` values must match registered client metadata exactly.
- Access tokens must be bound to the expected MCP resource, issuer, expiry, scope, and user.
- Revocation or inactive token/session state must prevent MCP access.

## Expected Public Endpoints

- `GET /.well-known/oauth-protected-resource`
- `GET /.well-known/oauth-protected-resource/mcp`
- `GET /.well-known/oauth-authorization-server`
- `POST /register`
- `GET /authorize`
- `POST /login`
- `POST /token`
- `POST /revoke`
- `GET /dashboard`
- `GET /decks/{deck_id}`
- `POST /logout`
- `GET /healthz`
- `POST /mcp`

## Additional UI Requirements

- `/dashboard` lists only the authenticated user's own decks.
- `/mypage` lets the authenticated user switch display language between Japanese and English.
- `/mypage` lets the authenticated user switch the application theme between light mode and dark mode.

## Implementation Direction

- Keep the current Streamable HTTP MCP transport.
- Add a small local persistence layer for users, OAuth clients, authorization codes, access token sessions, and deck ownership.
- Use application-owned username/password credentials for the login screen.
- Keep the HTML UI intentionally simple.
- Prefer explicit, local checks over implicit trust in headers, tunnel identity, or client claims.

## Acceptance Criteria

- ChatGPT can complete OAuth connection to the remote MCP server.
- ChatGPT can call `get_presentation_guideline` and `create_message_first_deck` with a valid token.
- Unauthenticated `/mcp` requests are rejected with correct OAuth discovery metadata.
- A generated deck belongs to the authenticated user that created it.
- Another unauthenticated or different user cannot view that deck.
- The authenticated user can open `/dashboard` and see only their own decks.
- Existing Cloudflare Tunnel deployment path remains usable.
