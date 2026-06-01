# Live Azure Setup

Created on 2026-05-31 for the live Communication Compiler smoke test.

## Subscription

- Subscription name: `default`
- Subscription id: `a73caabc-b02c-48fa-bc3f-8a7801255634`
- Tenant: `ymuichirogmail.onmicrosoft.com`
- User: `ym.u.ichiro@icloud.com`

## Resources

- Resource group: `rg-mfdemo-20260531`
- Location: `eastus2`
- Foundry resource: `mfdemo-20260531-u09qvl`
- Foundry project: `mfdemo-proj`
- Project endpoint: `https://mfdemo-20260531-u09qvl.services.ai.azure.com/api/projects/mfdemo-proj`
- Agent name: `communication-compiler-agent`
- Agent version: `1`
- Agent id: `communication-compiler-agent:1`

## Cost Guardrails

- API key/local auth is disabled on the Foundry resource.
- The app uses `DefaultAzureCredential`, so local live tests use `az login`.
- Model deployment: `gpt-5.4-nano`
- Model version: `2026-03-17`
- Deployment name: `gpt-5-4-nano`
- SKU: `GlobalStandard`
- Capacity: `1`
- Resource group budget: `budget-mfdemo-low-20260531`
- Budget amount: `5` monthly
- Budget notifications: actual spend over 50%, actual spend over 80%, forecasted spend over 100%
- Budget contact: `ym.u.ichiro@icloud.com`
- `.env.live` sets `MESSAGE_FIRST_MCP_ALLOW_LOCAL_FALLBACK=false` so MCP integration failures surface directly.

`gpt-5.4-nano` was selected because it is lower-cost than `gpt-5.4-mini` and available in the created account.

The Azure budget is an alerting guardrail only. It does not hard-stop model inference or delete resources when the threshold is crossed.

## Validate Without Paid Inference

```bash
make validate-live-env
```

## Run Live App

Terminal 1:

```bash
make run
```

Terminal 2:

```bash
set -a
source .env.live
set +a
uv run --extra foundry uvicorn example.communication_compiler.main:app --host 127.0.0.1 --port 8080
```

For the first paid smoke test, run only:

```text
demo preset -> extract claims
```

Do not continue to kernel refinement or evidence grounding until claim extraction returns valid JSON.

## Cleanup

Delete all live resources when the demo is no longer needed:

```bash
az group delete --name rg-mfdemo-20260531
```
