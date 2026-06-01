from __future__ import annotations

import json
import time
from pathlib import Path
from threading import RLock
from typing import Any

from mcp.shared.auth import OAuthClientInformationFull

from minimalist_presentation_mcp.auth.passwords import hash_password, verify_password


def now_ts() -> int:
    return int(time.time())


class AuthStore:
    def __init__(self, data_dir: Path) -> None:
        self.path = data_dir / "auth.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        if not self.path.exists():
            self._write(
                {
                    "users": {},
                    "clients": {},
                    "pending_authorizations": {},
                    "authorization_codes": {},
                    "access_tokens": {},
                    "refresh_tokens": {},
                    "browser_sessions": {},
                }
            )

    def bootstrap_admin(self, username: str | None, password: str | None) -> None:
        if not username or not password:
            return
        with self._lock:
            data = self._read()
            if any(user["username"] == username for user in data["users"].values()):
                return
            user_id = self._new_id("usr")
            data["users"][user_id] = {
                "id": user_id,
                "username": username,
                "password_hash": hash_password(password),
                "language": "ja",
                "theme": "light",
                "created_at": now_ts(),
            }
            self._write(data)

    def authenticate_user(self, username: str, password: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read()
            for user in data["users"].values():
                if user["username"] == username and verify_password(password, user["password_hash"]):
                    return dict(user)
        return None

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        with self._lock:
            user = self._read()["users"].get(user_id)
            return dict(user) if user else None

    def update_preferences(self, user_id: str, *, language: str, theme: str) -> dict[str, Any] | None:
        if language not in {"ja", "en"}:
            language = "ja"
        if theme not in {"light", "dark"}:
            theme = "light"
        with self._lock:
            data = self._read()
            user = data["users"].get(user_id)
            if not user:
                return None
            user["language"] = language
            user["theme"] = theme
            self._write(data)
            return dict(user)

    def save_client(self, client: OAuthClientInformationFull) -> None:
        if not client.client_id:
            raise ValueError("client_id is required")
        with self._lock:
            data = self._read()
            data["clients"][client.client_id] = client.model_dump(mode="json")
            self._write(data)

    def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        with self._lock:
            raw = self._read()["clients"].get(client_id)
            return OAuthClientInformationFull.model_validate(raw) if raw else None

    def save_pending_authorization(self, record: dict[str, Any]) -> None:
        with self._lock:
            data = self._read()
            data["pending_authorizations"][record["id"]] = record
            self._write(data)

    def pop_pending_authorization(self, authorization_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read()
            record = data["pending_authorizations"].pop(authorization_id, None)
            self._write(data)
            if not record or record["expires_at"] < now_ts():
                return None
            return record

    def save_authorization_code(self, record: dict[str, Any]) -> None:
        with self._lock:
            data = self._read()
            data["authorization_codes"][record["code"]] = record
            self._write(data)

    def load_authorization_code(self, code: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._read()["authorization_codes"].get(code)
            if not record or record.get("used") or record["expires_at"] < time.time():
                return None
            return dict(record)

    def consume_authorization_code(self, code: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read()
            record = data["authorization_codes"].get(code)
            if not record or record.get("used") or record["expires_at"] < time.time():
                return None
            record["used"] = True
            self._write(data)
            return dict(record)

    def save_tokens(self, *, access: dict[str, Any], refresh: dict[str, Any]) -> None:
        with self._lock:
            data = self._read()
            data["access_tokens"][access["token"]] = access
            data["refresh_tokens"][refresh["token"]] = refresh
            self._write(data)

    def load_access_token(self, token: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._read()["access_tokens"].get(token)
            if not record or record.get("revoked") or record["expires_at"] < now_ts():
                return None
            return dict(record)

    def load_refresh_token(self, token: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._read()["refresh_tokens"].get(token)
            if not record or record.get("revoked") or record["expires_at"] < now_ts():
                return None
            return dict(record)

    def revoke_token(self, token: str) -> None:
        with self._lock:
            data = self._read()
            access = data["access_tokens"].get(token)
            refresh = data["refresh_tokens"].get(token)
            user_id = None
            if access:
                access["revoked"] = True
                user_id = access.get("user_id")
            if refresh:
                refresh["revoked"] = True
                user_id = refresh.get("user_id")
            if user_id:
                for item in data["access_tokens"].values():
                    if item.get("user_id") == user_id and item.get("refresh_token") == token:
                        item["revoked"] = True
                for item in data["refresh_tokens"].values():
                    if item.get("user_id") == user_id and item.get("access_token") == token:
                        item["revoked"] = True
            self._write(data)

    def create_browser_session(self, user_id: str, ttl_seconds: int = 60 * 60 * 24 * 14) -> str:
        session_id = self._new_token()
        with self._lock:
            data = self._read()
            data["browser_sessions"][session_id] = {"user_id": user_id, "expires_at": now_ts() + ttl_seconds}
            self._write(data)
        return session_id

    def get_browser_session_user(self, session_id: str | None) -> dict[str, Any] | None:
        if not session_id:
            return None
        with self._lock:
            data = self._read()
            session = data["browser_sessions"].get(session_id)
            if not session or session["expires_at"] < now_ts():
                return None
            user = data["users"].get(session["user_id"])
            return dict(user) if user else None

    def delete_browser_session(self, session_id: str | None) -> None:
        if not session_id:
            return
        with self._lock:
            data = self._read()
            data["browser_sessions"].pop(session_id, None)
            self._write(data)

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{AuthStore._new_token()[:22]}"

    @staticmethod
    def _new_token() -> str:
        import secrets

        return secrets.token_urlsafe(32)
