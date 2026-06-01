from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from example.communication_compiler.models import (
    AgentKernelResult,
    ClaimExtractionResult,
    EvidenceGroundingResult,
    SessionState,
)


class AgentInputError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class AgentOutputError(RuntimeError):
    pass


class AgentClient(ABC):
    model_name = "unknown"

    @abstractmethod
    async def extract_claim_candidates(self, session: SessionState, *, max_candidates: int = 3) -> ClaimExtractionResult:
        raise NotImplementedError

    @abstractmethod
    async def refine_message_kernel(self, session: SessionState, user_feedback: str | None = None) -> AgentKernelResult:
        raise NotImplementedError

    @abstractmethod
    async def ground_evidence(self, session: SessionState, *, use_mock_evidence: bool = True) -> EvidenceGroundingResult:
        raise NotImplementedError

    @abstractmethod
    async def build_deck_payload(self, session: SessionState, *, language: str = "ja-JP") -> dict[str, Any]:
        raise NotImplementedError
