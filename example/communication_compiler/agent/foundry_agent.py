from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from example.communication_compiler.agent.base import AgentClient, AgentInputError, AgentOutputError
from example.communication_compiler.config import AppSettings
from example.communication_compiler.models import (
    AgentKernelResult,
    ClaimExtractionResult,
    EvidenceGroundingResult,
    SessionState,
)
from example.communication_compiler.services.deck_payload import build_deck_payload
from example.communication_compiler.services.evidence import ground_with_fixtures


AGENT_INSTRUCTIONS = """You are a Communication Compiler Agent.

Your job is not to create slides immediately.
Your job is to help the user discover and sharpen what they actually want to say.

You convert rough user input into:
1. claim candidates
2. a 4-Line Message Kernel
3. diagnosis of weaknesses
4. evidence gaps and objections
5. final Message-First Deck payload

Rules:
- Return parseable JSON only.
- Do not ask many generic interview questions.
- Prefer extracting structure from the user's rough speech.
- Ask only the minimum questions needed to resolve ambiguity.
- Always separate claim, evidence, objection, and requested action.
- Do not invent internal data.
- Mark uncertain evidence as uncertain.
- Treat the five-page deck as an output UI, not the main reasoning artifact.
"""


class FoundryAgentClient(AgentClient):
    model_name = "azure-ai-foundry-agent"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        if not settings.azure_ai_foundry_project_endpoint or not (
            settings.azure_ai_foundry_agent_name or settings.azure_ai_foundry_agent_id
        ):
            raise RuntimeError(
                "AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_FOUNDRY_AGENT_NAME are required when AGENT_PROVIDER=foundry. "
                "AZURE_AI_FOUNDRY_AGENT_ID is supported only for legacy/classic SDKs."
            )

    async def extract_claim_candidates(self, session: SessionState, *, max_candidates: int = 3) -> ClaimExtractionResult:
        payload = await self._run_json(
            "extract_claim_candidates",
            session,
            {
                "task": "Extract exactly three different business claim candidates from Free Talk.",
                "max_candidates": max_candidates,
                "schema": ClaimExtractionResult.model_json_schema(),
            },
        )
        try:
            return ClaimExtractionResult.model_validate(_trim_root_extra(payload, ClaimExtractionResult))
        except ValidationError as exc:
            raise AgentOutputError(f"Foundry Agent returned invalid claim JSON: {exc}") from exc

    async def refine_message_kernel(self, session: SessionState, user_feedback: str | None = None) -> AgentKernelResult:
        payload = await self._run_json(
            "refine_message_kernel",
            session,
            {
                "task": "Create or revise the 4-Line Message Kernel and diagnose it.",
                "user_feedback": user_feedback or "",
                "schema": AgentKernelResult.model_json_schema(),
            },
        )
        try:
            return AgentKernelResult.model_validate(_trim_root_extra(payload, AgentKernelResult))
        except ValidationError as exc:
            raise AgentOutputError(f"Foundry Agent returned invalid kernel JSON: {exc}") from exc

    async def ground_evidence(self, session: SessionState, *, use_mock_evidence: bool = True) -> EvidenceGroundingResult:
        if use_mock_evidence:
            if session.current_message_kernel is None:
                raise AgentInputError("MESSAGE_KERNEL_REQUIRED", "根拠整理には 4-Line Message Kernel が必要です。")
            return ground_with_fixtures(session.current_message_kernel, self.settings.evidence_fixture_dir)
        payload = await self._run_json(
            "ground_evidence",
            session,
            {
                "task": (
                    "Return supporting evidence, evidence gaps, and likely objections. "
                    "Return only the JSON object matching the provided schema. "
                    "Do not invent internal data. If no direct internal evidence is available, "
                    "use user_free_talk only as needs_confirmation supporting evidence, and still return "
                    "at least three evidence_gaps and at least two objections."
                ),
                "use_mock_evidence": use_mock_evidence,
                "schema": EvidenceGroundingResult.model_json_schema(),
            },
        )
        try:
            evidence_payload = _trim_root_extra(payload, EvidenceGroundingResult)
            evidence_payload.setdefault("grounding_summary", _fallback_grounding_summary(evidence_payload))
            return EvidenceGroundingResult.model_validate(evidence_payload)
        except ValidationError as exc:
            raise AgentOutputError(f"Foundry Agent returned invalid evidence JSON: {exc}") from exc

    async def build_deck_payload(self, session: SessionState, *, language: str = "ja-JP") -> dict[str, Any]:
        return build_deck_payload(session, language=language)

    async def _run_json(self, step: str, session: SessionState, instruction: dict[str, Any]) -> dict[str, Any]:
        prompt = json.dumps(
            {
                "system": AGENT_INSTRUCTIONS,
                "step": step,
                "instruction": instruction,
                "session": session.model_dump(mode="json", by_alias=True),
            },
            ensure_ascii=False,
        )
        if self.settings.azure_ai_foundry_agent_name:
            return await self._run_json_with_responses_api(prompt)
        return await self._run_json_with_classic_agents(prompt)

    async def _run_json_with_responses_api(self, prompt: str) -> dict[str, Any]:
        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:
            raise RuntimeError(
                "Install optional Foundry dependencies with: uv sync --extra foundry"
            ) from exc

        project = AIProjectClient(
            endpoint=str(self.settings.azure_ai_foundry_project_endpoint),
            credential=DefaultAzureCredential(),
        )
        openai = project.get_openai_client()
        agent_reference: dict[str, str] = {
            "type": "agent_reference",
            "name": str(self.settings.azure_ai_foundry_agent_name),
        }
        if self.settings.azure_ai_foundry_agent_version:
            agent_reference["version"] = self.settings.azure_ai_foundry_agent_version
        response = openai.responses.create(
            input=prompt,
            extra_body={"agent_reference": agent_reference},
        )
        return _extract_json(_response_output_text(response))

    async def _run_json_with_classic_agents(self, prompt: str) -> dict[str, Any]:
        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:
            raise RuntimeError(
                "Install optional Foundry dependencies with: uv sync --extra foundry"
            ) from exc

        client = AIProjectClient(endpoint=str(self.settings.azure_ai_foundry_project_endpoint), credential=DefaultAzureCredential())
        if not hasattr(client, "agents"):
            raise RuntimeError(
                "The installed azure-ai-projects SDK does not expose the legacy agents client. "
                "Use AZURE_AI_FOUNDRY_AGENT_NAME with the current Projects 2.x Responses API path."
            )

        thread = client.agents.threads.create()
        client.agents.messages.create(thread_id=thread.id, role="user", content=prompt)
        run = client.agents.runs.create_and_process(thread_id=thread.id, agent_id=self.settings.azure_ai_foundry_agent_id)
        if getattr(run, "status", "") == "failed":
            raise AgentOutputError(f"Foundry Agent run failed: {getattr(run, 'last_error', None)}")
        messages = client.agents.messages.list(thread_id=thread.id)
        text = _latest_assistant_text(messages)
        return _extract_json(text)


def _latest_assistant_text(messages: Any) -> str:
    for message in messages:
        if getattr(message, "role", None) != "assistant":
            continue
        content = getattr(message, "content", [])
        if isinstance(content, str):
            return content
        parts: list[str] = []
        for item in content:
            text = getattr(getattr(item, "text", None), "value", None) or getattr(item, "text", None)
            if text:
                parts.append(str(text))
        if parts:
            return "\n".join(parts)
    raise AgentOutputError("Foundry Agent did not return an assistant message.")


def _response_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text)
    parts: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(str(text))
    if parts:
        return "\n".join(parts)
    raise AgentOutputError("Foundry Agent response did not include output text.")


def _extract_json(text: str) -> dict[str, Any]:
    candidate = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, flags=re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise AgentOutputError(f"Foundry Agent returned non-JSON output: {text[:240]}") from exc


def _trim_root_extra(payload: dict[str, Any], model: type[Any]) -> dict[str, Any]:
    allowed = set(getattr(model, "model_fields", {}).keys())
    if not allowed:
        return payload
    if not any(key in allowed for key in payload):
        nested = _find_nested_model_payload(payload, allowed)
        if nested is not None:
            payload = nested
    return {key: value for key, value in payload.items() if key in allowed}


def _fallback_grounding_summary(payload: dict[str, Any]) -> str:
    evidence_count = len(payload.get("supporting_evidence") or [])
    gap_count = len(payload.get("evidence_gaps") or [])
    objection_count = len(payload.get("objections") or [])
    return f"整理済み: supporting evidence {evidence_count}件、evidence gaps {gap_count}件、objections {objection_count}件。"


def _find_nested_model_payload(payload: dict[str, Any], allowed: set[str]) -> dict[str, Any] | None:
    best: tuple[int, dict[str, Any]] | None = None
    stack = [payload]
    while stack:
        current = stack.pop()
        score = len(set(current.keys()) & allowed)
        if score and (best is None or score > best[0]):
            best = (score, current)
        for value in current.values():
            if isinstance(value, dict):
                stack.append(value)
    return best[1] if best else None
