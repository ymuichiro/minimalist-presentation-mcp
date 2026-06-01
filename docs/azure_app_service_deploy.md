# Azure App Service Demo Deployment

Created on 2026-06-01.

## Goal

Run the demo UI, FastAPI backend, and Streamable HTTP MCP endpoint in a single Azure App Service.

## Current Deployment

- Resource group: `rg-mfdemo-20260531`
- App Service location: `japanwest`
- App Service plan: Free Linux `F1`
- Web App: `mfdemo-app-20260601-v26tanj`
- URL: `https://mfdemo-app-20260601-v26tanj.azurewebsites.net`
- Startup command: `python -m uvicorn azure_app:app --host 0.0.0.0 --port 8000`
- ASGI entrypoint: `azure_app:app`

## Auth

Azure App Service Easy Auth is enabled with Microsoft Entra ID using `authsettingsV2`.

- Unauthenticated access: blocked
- Provider: Azure Active Directory
- Auth mode: App Service Auth V2
- Client app: `mfdemo-easyauth-20260601-v26tanj`
- Callback: `https://mfdemo-app-20260601-v26tanj.azurewebsites.net/.auth/login/aad/callback`
- OpenID issuer: `https://login.microsoftonline.com/e1198883-fbec-44d6-bfa9-894832d8f050/v2.0`

Access token implicit grant is disabled. ID token issuance is enabled because App Service Easy Auth requests `response_type=code id_token` for this provider flow even though the application itself only relies on the authenticated user/session exposed by Easy Auth.

Demo judge credentials are stored locally only:

```text
.azure-deploy/appservice-demo-v2.env
```

Do not commit that file.

## Verification

App startup was verified by temporarily disabling Easy Auth, checking the app, then restoring Easy Auth.

```text
GET /healthz -> 200
GET / -> Communication Compiler HTML
```

Final auth state was restored and verified:

```text
GET / -> 401
Easy Auth enabled: true
Unauthenticated action: RedirectToLoginPage
```

The created demo account reaches credential validation and MFA enrollment was confirmed by the owner.

## Previous Deployment

The first App Service was `mfdemo-app-20260601-jwz0fbg`. It used classic authentication settings and was replaced because the callback flow could stop on a blank `/.auth/login/aad/callback` page after MFA.
