from __future__ import annotations

import json
from pathlib import Path

import ulid

from example.communication_compiler.models import SessionState


class SessionNotFoundError(KeyError):
    pass


class SessionStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.sessions_dir = data_dir / "sessions"
        self.artifacts_dir = data_dir / "artifacts"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def new_session_id(self) -> str:
        return f"ses_{ulid.new().str}"

    def create(self) -> SessionState:
        session = SessionState(session_id=self.new_session_id())
        self.save(session)
        return session

    def path_for(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def load(self, session_id: str) -> SessionState:
        path = self.path_for(session_id)
        if not path.exists():
            raise SessionNotFoundError(session_id)
        return SessionState.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, session: SessionState) -> SessionState:
        session.touch()
        path = self.path_for(session.session_id)
        path.write_text(json.dumps(session.model_dump(mode="json", by_alias=True), ensure_ascii=False, indent=2), encoding="utf-8")
        return session

    def artifact_dir(self, session_id: str) -> Path:
        path = self.artifacts_dir / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path
