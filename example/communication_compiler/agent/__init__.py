from __future__ import annotations

from example.communication_compiler.agent.base import AgentClient, AgentInputError, AgentOutputError
from example.communication_compiler.agent.foundry_agent import FoundryAgentClient
from example.communication_compiler.agent.mock_agent import MockAgentClient
from example.communication_compiler.config import AppSettings


def get_agent_client(settings: AppSettings) -> AgentClient:
    if settings.agent_provider == "foundry":
        return FoundryAgentClient(settings)
    return MockAgentClient(settings)


__all__ = [
    "AgentClient",
    "AgentInputError",
    "AgentOutputError",
    "FoundryAgentClient",
    "MockAgentClient",
    "get_agent_client",
]
