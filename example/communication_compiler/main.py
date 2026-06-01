from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from example.communication_compiler.agent import AgentInputError, AgentOutputError, get_agent_client
from example.communication_compiler.config import AppSettings, load_settings
from example.communication_compiler.models import (
    AgentTraceEntry,
    KernelRevision,
    SessionState,
)
from example.communication_compiler.services.brief import build_brief_markdown, brief_markdown_to_html
from example.communication_compiler.services.deck_payload import DeckPreconditionError, assert_deck_preconditions
from example.communication_compiler.services.idea_map import build_idea_map
from example.communication_compiler.services.mcp_client import McpDeckClient
from example.communication_compiler.services.speech import AzureSpeechTranscriber, SpeechTranscriptionError
from example.communication_compiler.storage import SessionNotFoundError, SessionStore


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


class FreeTalkRequest(BaseModel):
    free_talk: str = Field(min_length=1)
    audience: str = ""
    desired_action: str = ""
    tone: str = "executive"


class ExtractClaimsRequest(BaseModel):
    max_candidates: int = Field(default=3, ge=1, le=5)


class SelectClaimRequest(BaseModel):
    claim_id: str
    user_feedback: str = ""


class RefineKernelRequest(BaseModel):
    additional_user_input: str = ""


class GroundEvidenceRequest(BaseModel):
    use_mock_evidence: bool = True
    search_query_hint: str = ""


class GenerateDeckRequest(BaseModel):
    language: str = "ja-JP"
    force: bool = False


class GenerateBriefRequest(BaseModel):
    format: str = "markdown"


def create_app(settings: AppSettings | None = None) -> FastAPI:
    resolved = settings or load_settings()
    store = SessionStore(resolved.data_dir)
    agent = get_agent_client(resolved)
    mcp_client = McpDeckClient(resolved)
    speech = AzureSpeechTranscriber(resolved)
    app = FastAPI(title="Communication Compiler Demo", version="0.1.0")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def index() -> Response:
        return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))

    @app.get("/example", include_in_schema=False)
    async def example_redirect() -> Response:
        return RedirectResponse("/", status_code=302)

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {
            "status": "ok",
            "agent_provider": resolved.agent_provider,
            "mcp_endpoint": resolved.message_first_mcp_endpoint,
        }

    @app.post("/api/sessions")
    async def create_session() -> dict[str, str]:
        session = store.create()
        return {"session_id": session.session_id}

    @app.post("/api/speech/transcribe")
    async def transcribe_speech(
        audio: UploadFile = File(...),
        language: str = Form(default="ja-JP"),
    ) -> Response:
        try:
            text = await speech.transcribe(
                audio=await audio.read(),
                content_type=audio.content_type or "application/octet-stream",
                language=language,
            )
        except SpeechTranscriptionError as exc:
            status = 503 if exc.code == "SPEECH_NOT_CONFIGURED" else 400
            return _error(exc.code, exc.message, status_code=status)
        return JSONResponse({"text": text, "language": language})

    @app.get("/api/sessions/{session_id}")
    async def get_session(session_id: str) -> Response:
        try:
            return _session_response(store.load(session_id))
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)

    @app.post("/api/sessions/{session_id}/free-talk")
    async def submit_free_talk(session_id: str, payload: FreeTalkRequest) -> Response:
        try:
            session = store.load(session_id)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        session.free_talk = payload.free_talk
        session.audience = payload.audience
        session.desired_action = payload.desired_action
        session.tone = payload.tone if payload.tone in {"direct", "cautious", "executive", "technical", "narrative"} else "executive"
        session.status = "draft"
        store.save(session)
        return _session_response(session)

    @app.post("/api/sessions/{session_id}/extract-claims")
    async def extract_claims(session_id: str, payload: ExtractClaimsRequest) -> Response:
        try:
            session = store.load(session_id)
            started = time.perf_counter()
            result = await agent.extract_claim_candidates(session, max_candidates=payload.max_candidates)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        except AgentInputError as exc:
            return _error(exc.code, exc.message, status_code=400)
        except (AgentOutputError, RuntimeError) as exc:
            return _error("AGENT_ERROR", str(exc), status_code=502)
        session.claim_candidates = result.claim_candidates
        session.selected_claim_id = None
        session.status = "awaiting_user_selection"
        _trace(session, "claim_extraction", "success", f"Generated {len(result.claim_candidates)} claim candidates.", agent.model_name, started)
        store.save(session)
        return JSONResponse(
            {
                "claim_candidates": [item.model_dump(mode="json") for item in result.claim_candidates],
                "recommended_next_question": result.recommended_next_question,
                "session": session.model_dump(mode="json", by_alias=True),
            }
        )

    @app.post("/api/sessions/{session_id}/select-claim")
    async def select_claim(session_id: str, payload: SelectClaimRequest) -> Response:
        try:
            session = store.load(session_id)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        if not any(item.claim_id == payload.claim_id for item in session.claim_candidates):
            return _error("CLAIM_NOT_FOUND", "Selected claim was not found in this session.", status_code=400)
        session.selected_claim_id = payload.claim_id
        session.status = "refining_kernel"
        _trace(session, "claim_selection", "success", f"Selected {payload.claim_id}.")
        store.save(session)
        return _session_response(session)

    @app.post("/api/sessions/{session_id}/refine-kernel")
    async def refine_kernel(session_id: str, payload: RefineKernelRequest) -> Response:
        try:
            session = store.load(session_id)
            started = time.perf_counter()
            result = await agent.refine_message_kernel(session, payload.additional_user_input or None)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        except AgentInputError as exc:
            return _error(exc.code, exc.message, status_code=400)
        except (AgentOutputError, RuntimeError) as exc:
            return _error("AGENT_ERROR", str(exc), status_code=502)
        session.current_message_kernel = result.message_kernel
        session.diagnosis = result.diagnosis
        session.message_kernel_revisions.append(
            KernelRevision(
                revision=result.message_kernel.revision,
                message_kernel=result.message_kernel,
                diagnosis=result.diagnosis,
            )
        )
        session.status = "ready_to_generate"
        _trace(
            session,
            "kernel_diagnosis",
            "warning" if result.diagnosis.warnings else "success",
            f"Kernel revision {result.message_kernel.revision} scored {result.diagnosis.overall_score}.",
            agent.model_name,
            started,
        )
        store.save(session)
        return JSONResponse(
            {
                "message_kernel": result.message_kernel.model_dump(mode="json"),
                "diagnosis": result.diagnosis.model_dump(mode="json"),
                "session": session.model_dump(mode="json", by_alias=True),
            }
        )

    @app.post("/api/sessions/{session_id}/ground-evidence")
    async def ground_evidence(session_id: str, payload: GroundEvidenceRequest) -> Response:
        try:
            session = store.load(session_id)
            started = time.perf_counter()
            result = await agent.ground_evidence(session, use_mock_evidence=payload.use_mock_evidence)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        except AgentInputError as exc:
            return _error(exc.code, exc.message, status_code=400)
        except (AgentOutputError, RuntimeError) as exc:
            return _error("AGENT_ERROR", str(exc), status_code=502)
        session.supporting_evidence = result.supporting_evidence
        session.evidence_gaps = result.evidence_gaps
        session.objections = result.objections
        session.grounding_summary = result.grounding_summary
        _trace(
            session,
            "evidence_grounding",
            "warning" if result.evidence_gaps else "success",
            f"Found {len(result.supporting_evidence)} evidence items, {len(result.evidence_gaps)} gaps, {len(result.objections)} objections.",
            agent.model_name,
            started,
        )
        store.save(session)
        return JSONResponse(
            {
                "supporting_evidence": [item.model_dump(mode="json") for item in result.supporting_evidence],
                "evidence_gaps": [item.model_dump(mode="json") for item in result.evidence_gaps],
                "objections": [item.model_dump(mode="json") for item in result.objections],
                "grounding_summary": result.grounding_summary,
                "session": session.model_dump(mode="json", by_alias=True),
            }
        )

    @app.get("/api/sessions/{session_id}/idea-map")
    async def idea_map(session_id: str) -> Response:
        try:
            session = store.load(session_id)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        return JSONResponse({"idea_map": build_idea_map(session).model_dump(mode="json", by_alias=True)})

    @app.post("/api/sessions/{session_id}/generate-idea-map")
    async def generate_idea_map(session_id: str) -> Response:
        try:
            session = store.load(session_id)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        session.artifacts.idea_map_url = f"{resolved.app_base_url.rstrip('/')}/api/sessions/{session_id}/idea-map"
        _trace(session, "idea_map", "success", "Generated idea map from session state.")
        store.save(session)
        return JSONResponse(
            {
                "idea_map": build_idea_map(session).model_dump(mode="json", by_alias=True),
                "idea_map_url": session.artifacts.idea_map_url,
                "session": session.model_dump(mode="json", by_alias=True),
            }
        )

    @app.post("/api/sessions/{session_id}/generate-brief")
    async def generate_brief(session_id: str, payload: GenerateBriefRequest) -> Response:
        try:
            session = store.load(session_id)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        if session.current_message_kernel is None:
            return _error("MESSAGE_KERNEL_REQUIRED", "Brief generation requires a 4-Line Message Kernel.", status_code=400)
        markdown = build_brief_markdown(session)
        html = brief_markdown_to_html(markdown)
        artifact_dir = store.artifact_dir(session_id)
        (artifact_dir / "brief.md").write_text(markdown, encoding="utf-8")
        (artifact_dir / "brief.html").write_text(html, encoding="utf-8")
        session.artifacts.brief_url = f"{resolved.app_base_url.rstrip('/')}/artifacts/{session_id}/brief.md"
        session.artifacts.brief_html_url = f"{resolved.app_base_url.rstrip('/')}/artifacts/{session_id}/brief.html"
        _trace(session, "brief_generation", "success", f"Generated {payload.format} brief.")
        store.save(session)
        return JSONResponse(
            {
                "brief_markdown_url": session.artifacts.brief_url,
                "brief_html_url": session.artifacts.brief_html_url,
                "session": session.model_dump(mode="json", by_alias=True),
            }
        )

    @app.post("/api/sessions/{session_id}/generate-deck")
    async def generate_deck(session_id: str, payload: GenerateDeckRequest) -> Response:
        try:
            session = store.load(session_id)
            if (
                session.current_message_kernel is not None
                and not session.supporting_evidence
                and not session.evidence_gaps
                and not session.objections
                and not payload.force
            ):
                grounding = await agent.ground_evidence(session, use_mock_evidence=False)
                session.supporting_evidence = grounding.supporting_evidence
                session.evidence_gaps = grounding.evidence_gaps
                session.objections = grounding.objections
                session.grounding_summary = grounding.grounding_summary
                _trace(
                    session,
                    "evidence_grounding",
                    "warning" if grounding.evidence_gaps else "success",
                    f"Auto-grounded before deck generation: {len(grounding.supporting_evidence)} evidence items, "
                    f"{len(grounding.evidence_gaps)} gaps, {len(grounding.objections)} objections.",
                )
            warnings = assert_deck_preconditions(session, force=payload.force)
            deck_payload = await agent.build_deck_payload(session, language=payload.language)
            started = time.perf_counter()
            response = await mcp_client.create_message_first_deck(deck_payload)
        except SessionNotFoundError:
            return _error("SESSION_NOT_FOUND", "Session not found.", status_code=404)
        except DeckPreconditionError as exc:
            return _error(exc.code, exc.message, status_code=400)
        except AgentInputError as exc:
            return _error(exc.code, exc.message, status_code=400)
        except (AgentOutputError, RuntimeError) as exc:
            return _error("DECK_GENERATION_FAILED", str(exc), status_code=502)
        response_warnings = sorted(set(warnings + list(response.get("warnings", []))))
        if response.get("error"):
            return JSONResponse(response, status_code=400)
        session.artifacts.deck_url = response.get("url")
        session.artifacts.deck_id = response.get("deck_id")
        session.warnings = response_warnings
        session.status = "generated"
        _trace(
            session,
            "deck_generation",
            "warning" if response_warnings else "success",
            "Generated Message-First Deck through MCP.",
            "minimalist-presentation-mcp",
            started,
        )
        store.save(session)
        return JSONResponse(
            {
                "deck_id": response.get("deck_id"),
                "deck_url": response.get("url"),
                "warnings": response_warnings,
                "session": session.model_dump(mode="json", by_alias=True),
            }
        )

    @app.get("/artifacts/{session_id}/{filename}", include_in_schema=False)
    async def artifact(session_id: str, filename: str) -> Response:
        if filename not in {"brief.md", "brief.html"}:
            return _error("ARTIFACT_NOT_FOUND", "Artifact not found.", status_code=404)
        path = store.artifact_dir(session_id) / filename
        if not path.exists():
            return _error("ARTIFACT_NOT_FOUND", "Artifact not found.", status_code=404)
        media_type = "text/markdown; charset=utf-8" if filename.endswith(".md") else "text/html; charset=utf-8"
        return FileResponse(path, media_type=media_type)

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception) -> Response:
        return _error("INTERNAL_ERROR", str(exc), status_code=500)

    return app


def _trace(
    session: SessionState,
    step: str,
    status: str,
    summary: str,
    model: str | None = None,
    started: float | None = None,
) -> None:
    duration_ms = round((time.perf_counter() - started) * 1000) if started else None
    session.agent_trace_summary.append(
        AgentTraceEntry(
            step=step,
            status=status,  # type: ignore[arg-type]
            summary=summary,
            model=model,
            duration_ms=duration_ms,
        )
    )


def _session_response(session: SessionState) -> JSONResponse:
    return JSONResponse({"session": session.model_dump(mode="json", by_alias=True)})


def _error(code: str, message: str, *, status_code: int) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status_code)


app = create_app()
