# Live Test Preparation

The live Foundry test is paid. Complete every local check below before setting `AGENT_PROVIDER=foundry`.

## No-Charge Local Checks

1. Install normal and optional dependencies:

   ```bash
   uv sync --extra foundry
   ```

2. Run the full local test suite:

   ```bash
   uv run pytest
   ```

3. Validate the live environment shape without calling Azure:

   ```bash
   cp .env.live.example .env.live
   make validate-live-env
   ```

4. Run the local mock demo:

   ```bash
   make run
   make run-example
   ```

5. In the browser, confirm the mock flow:

   ```text
   demo preset -> extract claims -> select claim -> refine kernel -> ground evidence -> generate brief -> generate deck
   ```

## Required Live Values

Set these in `.env.live`:

- `AGENT_PROVIDER=foundry`
- `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`
  - Expected shape: `https://<resource-name>.ai.azure.com/api/projects/<project-name>`
- `AZURE_AI_FOUNDRY_AGENT_NAME`
  - Preferred for current Azure AI Projects 2.x.
- `AZURE_AI_FOUNDRY_AGENT_VERSION`
  - Optional; use only when you need a specific agent version.
- `AZURE_AI_FOUNDRY_AGENT_ID`
  - Legacy/classic fallback only.
- `APP_BASE_URL`
- `APP_DATA_DIR`
- `MESSAGE_FIRST_MCP_ENDPOINT`
- `MESSAGE_FIRST_PUBLIC_BASE_URL`
- `MESSAGE_FIRST_MCP_ALLOW_LOCAL_FALLBACK=false`

Authentication uses `DefaultAzureCredential`, so run:

```bash
az login
```

The signed-in principal must have permission to invoke the Foundry project and Agent. In practice, use the Azure AI User role at the project scope for development smoke tests.

## First Paid Smoke Test

Use only the smallest useful flow first.

1. Start the MCP server:

   ```bash
   make run
   ```

2. Start the example app with live settings:

   ```bash
   set -a
   source .env.live
   set +a
   uv run --extra foundry uvicorn example.communication_compiler.main:app --host 127.0.0.1 --port 8080
   ```

3. In the UI, run only:

   ```text
   demo preset -> extract claims
   ```

Stop here if claim extraction fails. Do not run kernel refinement or evidence grounding until the first paid call returns valid JSON.

## Expected Paid Calls

The current demo makes Foundry calls for:

1. Claim extraction
2. Kernel refinement
3. Evidence grounding

Deck generation calls the local MCP server and does not require Foundry if the deck payload is already built.

## Stop Rules

Stop the live test immediately if:

- the Agent returns non-JSON
- validation fails with schema errors
- Foundry auth/RBAC fails
- `MESSAGE_FIRST_MCP_ALLOW_LOCAL_FALLBACK=false` exposes an MCP integration failure
- generated claims are generic enough that proceeding would waste paid calls
