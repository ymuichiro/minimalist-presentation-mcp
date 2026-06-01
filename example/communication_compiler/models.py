from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


SessionStatus = Literal[
    "draft",
    "awaiting_user_selection",
    "refining_kernel",
    "ready_to_generate",
    "generated",
    "error",
]

Tone = Literal["direct", "cautious", "executive", "technical", "narrative"]
Angle = Literal["strategy", "operation", "investment", "risk", "culture", "product", "governance"]
Severity = Literal["high", "medium", "low"]
Strength = Literal["strong", "medium", "weak", "needs_confirmation"]
KernelLine = Literal["premise", "complication", "claim", "action"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ClaimCandidate(StrictModel):
    claim_id: str
    title: str
    summary: str
    angle: Angle
    why_this_may_be_true: list[str] = Field(default_factory=list)
    potential_weakness: list[str] = Field(default_factory=list)


class ClaimExtractionResult(StrictModel):
    claim_candidates: list[ClaimCandidate]
    recommended_next_question: str


class MessageKernel(StrictModel):
    revision: int
    premise: str
    complication: str
    claim: str
    action: str
    confidence: float = Field(ge=0, le=1)
    notes: list[str] = Field(default_factory=list)


class DiagnosisIssue(StrictModel):
    severity: Severity
    field: str
    message: str
    code: str | None = None


class KernelRubric(StrictModel):
    specificity: int = Field(ge=1, le=5)
    complication_strength: int = Field(ge=1, le=5)
    claim_sharpness: int = Field(ge=1, le=5)
    action_clarity: int = Field(ge=1, le=5)
    non_redundancy: int = Field(ge=1, le=5)
    evidence_supportability: int = Field(ge=1, le=5)
    objection_awareness: int = Field(ge=1, le=5)
    audience_fit: int = Field(ge=1, le=5)


class Diagnosis(StrictModel):
    overall_score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    issues: list[DiagnosisIssue] = Field(default_factory=list)
    recommended_questions: list[str] = Field(default_factory=list)
    rubric: KernelRubric | None = None
    warnings: list[str] = Field(default_factory=list)


class KernelRevision(StrictModel):
    revision: int
    message_kernel: MessageKernel
    diagnosis: Diagnosis
    created_at: str = Field(default_factory=utc_now)


class AgentKernelResult(StrictModel):
    message_kernel: MessageKernel
    diagnosis: Diagnosis


class SupportingEvidence(StrictModel):
    evidence_id: str
    title: str
    summary: str
    source_type: str
    source_ref: str
    strength: Strength
    supports_kernel_line: KernelLine
    quoted_or_paraphrased_basis: str | None = None


class EvidenceGap(StrictModel):
    gap_id: str
    description: str
    why_it_matters: str
    suggested_source: str


class Objection(StrictModel):
    objection_id: str
    objection: str
    response_strategy: str
    evidence_needed: str


class EvidenceGroundingResult(StrictModel):
    supporting_evidence: list[SupportingEvidence] = Field(default_factory=list)
    evidence_gaps: list[EvidenceGap] = Field(default_factory=list)
    objections: list[Objection] = Field(default_factory=list)
    grounding_summary: str


class Artifacts(StrictModel):
    deck_url: str | None = None
    deck_id: str | None = None
    brief_url: str | None = None
    brief_html_url: str | None = None
    idea_map_url: str | None = None
    image_url: str | None = None


class AgentTraceEntry(StrictModel):
    step: str
    status: Literal["success", "warning", "error"]
    summary: str
    model: str | None = None
    duration_ms: int | None = None
    created_at: str = Field(default_factory=utc_now)


class IdeaMapNode(StrictModel):
    id: str
    type: Literal["kernel_line", "claim_candidate", "evidence", "gap", "objection", "question", "user_input"]
    label: str
    text: str


class IdeaMapEdge(StrictModel):
    from_: str = Field(alias="from")
    to: str
    type: Literal["leads_to", "supports", "weakens", "challenges", "requires_decision", "refines", "derived_from"]


class IdeaMap(StrictModel):
    nodes: list[IdeaMapNode]
    edges: list[IdeaMapEdge]


class SessionState(StrictModel):
    session_id: str
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    status: SessionStatus = "draft"
    free_talk: str = ""
    audience: str = ""
    desired_action: str = ""
    tone: Tone = "executive"
    claim_candidates: list[ClaimCandidate] = Field(default_factory=list)
    selected_claim_id: str | None = None
    message_kernel_revisions: list[KernelRevision] = Field(default_factory=list)
    current_message_kernel: MessageKernel | None = None
    diagnosis: Diagnosis | None = None
    supporting_evidence: list[SupportingEvidence] = Field(default_factory=list)
    evidence_gaps: list[EvidenceGap] = Field(default_factory=list)
    objections: list[Objection] = Field(default_factory=list)
    grounding_summary: str | None = None
    artifacts: Artifacts = Field(default_factory=Artifacts)
    agent_trace_summary: list[AgentTraceEntry] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = utc_now()


class ApiError(StrictModel):
    code: str
    message: str


class ErrorResponse(StrictModel):
    error: ApiError
