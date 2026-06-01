from __future__ import annotations

import secrets
import time
from typing import Any
from urllib.parse import urlencode, urlparse

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    RefreshToken,
    RegistrationError,
    TokenError,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from pydantic import AnyUrl

from minimalist_presentation_mcp.auth.store import AuthStore, now_ts

DEFAULT_SCOPES = ["deck:create", "deck:read"]
AUTHORIZATION_TTL_SECONDS = 600
ACCESS_TOKEN_TTL_SECONDS = 3600
REFRESH_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30


class AppAuthorizationCode(AuthorizationCode):
    user_id: str


class AppRefreshToken(RefreshToken):
    user_id: str
    resource: str | None = None


class InAppOAuthProvider:
    def __init__(
        self,
        *,
        store: AuthStore,
        issuer_url: str,
        resource_url: str,
        allowed_redirect_origins: list[str] | None = None,
    ) -> None:
        self.store = store
        self.issuer_url = issuer_url.rstrip("/")
        self.resource_url = resource_url
        self.allowed_redirect_origins = {origin.rstrip("/") for origin in (allowed_redirect_origins or [])}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self.store.get_client(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        if client_info.token_endpoint_auth_method is None:
            client_info.token_endpoint_auth_method = "none"
        for redirect_uri in client_info.redirect_uris or []:
            origin = _origin(str(redirect_uri))
            if self.allowed_redirect_origins and origin not in self.allowed_redirect_origins:
                raise RegistrationError("invalid_client_metadata", f"redirect_uri origin is not allowed: {origin}")
        self.store.save_client(client_info)

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        if params.resource and params.resource.rstrip("/") != self.resource_url.rstrip("/"):
            raise AuthorizeError("invalid_request", "resource does not match this MCP server")
        origin = _origin(str(params.redirect_uri))
        if self.allowed_redirect_origins and origin not in self.allowed_redirect_origins:
            raise AuthorizeError("invalid_request", f"redirect_uri origin is not allowed: {origin}")
        authorization_id = secrets.token_urlsafe(24)
        self.store.save_pending_authorization(
            {
                "id": authorization_id,
                "client_id": client.client_id,
                "scopes": params.scopes or DEFAULT_SCOPES,
                "code_challenge": params.code_challenge,
                "redirect_uri": str(params.redirect_uri),
                "redirect_uri_provided_explicitly": params.redirect_uri_provided_explicitly,
                "resource": params.resource or self.resource_url,
                "state": params.state,
                "expires_at": now_ts() + AUTHORIZATION_TTL_SECONDS,
            }
        )
        return f"{self.issuer_url}/login?{urlencode({'auth_request': authorization_id})}"

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AppAuthorizationCode | None:
        raw = self.store.load_authorization_code(authorization_code)
        if not raw or raw["client_id"] != client.client_id:
            return None
        return self._code_from_record(raw)

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AppAuthorizationCode
    ) -> OAuthToken:
        raw = self.store.consume_authorization_code(authorization_code.code)
        if not raw:
            raise TokenError("invalid_grant", "authorization code has already been used")
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        access_record = {
            "token": access_token,
            "client_id": client.client_id,
            "user_id": authorization_code.user_id,
            "scopes": authorization_code.scopes,
            "resource": authorization_code.resource,
            "expires_at": now_ts() + ACCESS_TOKEN_TTL_SECONDS,
            "revoked": False,
            "refresh_token": refresh_token,
        }
        refresh_record = {
            "token": refresh_token,
            "client_id": client.client_id,
            "user_id": authorization_code.user_id,
            "scopes": authorization_code.scopes,
            "resource": authorization_code.resource,
            "expires_at": now_ts() + REFRESH_TOKEN_TTL_SECONDS,
            "revoked": False,
            "access_token": access_token,
        }
        self.store.save_tokens(access=access_record, refresh=refresh_record)
        return OAuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_TTL_SECONDS,
            scope=" ".join(authorization_code.scopes),
        )

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> AppRefreshToken | None:
        raw = self.store.load_refresh_token(refresh_token)
        if not raw or raw["client_id"] != client.client_id:
            return None
        return AppRefreshToken(
            token=raw["token"],
            client_id=raw["client_id"],
            scopes=raw["scopes"],
            expires_at=raw["expires_at"],
            user_id=raw["user_id"],
            resource=raw.get("resource"),
        )

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: AppRefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        self.store.revoke_token(refresh_token.token)
        access_token = secrets.token_urlsafe(32)
        new_refresh_token = secrets.token_urlsafe(32)
        access_record = {
            "token": access_token,
            "client_id": client.client_id,
            "user_id": refresh_token.user_id,
            "scopes": scopes,
            "resource": refresh_token.resource,
            "expires_at": now_ts() + ACCESS_TOKEN_TTL_SECONDS,
            "revoked": False,
            "refresh_token": new_refresh_token,
        }
        refresh_record = {
            "token": new_refresh_token,
            "client_id": client.client_id,
            "user_id": refresh_token.user_id,
            "scopes": scopes,
            "resource": refresh_token.resource,
            "expires_at": now_ts() + REFRESH_TOKEN_TTL_SECONDS,
            "revoked": False,
            "access_token": access_token,
        }
        self.store.save_tokens(access=access_record, refresh=refresh_record)
        return OAuthToken(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_TTL_SECONDS,
            scope=" ".join(scopes),
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        raw = self.store.load_access_token(token)
        if not raw:
            return None
        if raw.get("resource") and raw["resource"].rstrip("/") != self.resource_url.rstrip("/"):
            return None
        return AccessToken(
            token=raw["token"],
            client_id=raw["client_id"],
            scopes=raw["scopes"],
            expires_at=raw["expires_at"],
            resource=raw.get("resource"),
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        return await self.load_access_token(token)

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        self.store.revoke_token(token.token)

    def complete_authorization(self, authorization_id: str, user_id: str) -> tuple[str, str]:
        pending = self.store.pop_pending_authorization(authorization_id)
        if not pending:
            raise ValueError("Authorization request expired or not found")
        code = secrets.token_urlsafe(32)
        record = {
            "code": code,
            "client_id": pending["client_id"],
            "user_id": user_id,
            "scopes": pending["scopes"],
            "expires_at": time.time() + AUTHORIZATION_TTL_SECONDS,
            "code_challenge": pending["code_challenge"],
            "redirect_uri": pending["redirect_uri"],
            "redirect_uri_provided_explicitly": pending["redirect_uri_provided_explicitly"],
            "resource": pending["resource"],
            "state": pending.get("state"),
            "used": False,
        }
        self.store.save_authorization_code(record)
        query: dict[str, str] = {"code": code}
        if pending.get("state"):
            query["state"] = pending["state"]
        return pending["redirect_uri"], urlencode(query)

    @staticmethod
    def _code_from_record(raw: dict[str, Any]) -> AppAuthorizationCode:
        return AppAuthorizationCode(
            code=raw["code"],
            scopes=raw["scopes"],
            expires_at=raw["expires_at"],
            client_id=raw["client_id"],
            code_challenge=raw["code_challenge"],
            redirect_uri=AnyUrl(raw["redirect_uri"]),
            redirect_uri_provided_explicitly=raw["redirect_uri_provided_explicitly"],
            resource=raw.get("resource"),
            user_id=raw["user_id"],
        )


def _origin(uri: str) -> str:
    parsed = urlparse(uri)
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
