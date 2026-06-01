from __future__ import annotations

from typing import Any

from example.communication_compiler.agent.base import AgentClient, AgentInputError
from example.communication_compiler.config import AppSettings
from example.communication_compiler.models import (
    AgentKernelResult,
    ClaimCandidate,
    ClaimExtractionResult,
    EvidenceGroundingResult,
    MessageKernel,
    SessionState,
)
from example.communication_compiler.services.deck_payload import build_deck_payload
from example.communication_compiler.services.evidence import ground_with_fixtures
from example.communication_compiler.services.guardrails import evaluate_kernel


class MockAgentClient(AgentClient):
    model_name = "mock-communication-compiler"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def extract_claim_candidates(self, session: SessionState, *, max_candidates: int = 3) -> ClaimExtractionResult:
        if len(session.free_talk.strip()) < 150:
            raise AgentInputError(
                "FREE_TALK_TOO_SHORT",
                "もう少し話してください。最低でも150文字程度あると、言いたいことの候補を抽出できます。",
            )
        candidates = [
            ClaimCandidate(
                claim_id="claim_1",
                title="AI 投資はツール配布から業務 Agent 実装へ移すべきである",
                summary="Copilot 配布の利用促進ではなく、業務プロセスに組み込まれた Agent 設計へ投資を移すべきという主張。",
                angle="strategy",
                why_this_may_be_true=[
                    "個人向けツール配布だけでは業務KPIに接続しづらい",
                    "PoC が増えても本番化や定着に進みにくい",
                ],
                potential_weakness=[
                    "既存 Copilot 投資との関係を否定ではなく役割分担として説明する必要がある",
                ],
            ),
            ClaimCandidate(
                claim_id="claim_2",
                title="問題は現場のスキル不足ではなく、業務運用モデルの未設計である",
                summary="プロンプト教育や利用率の問題に見えるが、本質はナレッジ、責任範囲、業務フローが設計されていないことだという主張。",
                angle="operation",
                why_this_may_be_true=[
                    "現場にはプロンプトを書く時間も業務文脈を整理する余力もない",
                    "ナレッジが散らばるほど個人努力型の AI 活用は再現性を失う",
                ],
                potential_weakness=[
                    "業務運用モデルを誰が設計し、保守するのかを明確にする必要がある",
                ],
            ),
            ClaimCandidate(
                claim_id="claim_3",
                title="次の予算判断は広いライセンス拡張より本番前提の Agent ユースケースを優先すべきである",
                summary="AI 活用をコスト削減ではなく業務成果に接続するため、次四半期の投資配分を絞るべきという主張。",
                angle="investment",
                why_this_may_be_true=[
                    "予算は利用率ではなく業務成果に接続する対象へ寄せる必要がある",
                    "対象を絞ることで評価指標、責任者、リスク対応を同時に設計できる",
                ],
                potential_weakness=[
                    "対象業務別の ROI や優先順位を示す根拠が不足しやすい",
                ],
            ),
        ]
        return ClaimExtractionResult(
            claim_candidates=candidates[:max_candidates],
            recommended_next_question="この3案のうち、あなたの感覚に一番近いものはどれですか？",
        )

    async def refine_message_kernel(self, session: SessionState, user_feedback: str | None = None) -> AgentKernelResult:
        selected = next((item for item in session.claim_candidates if item.claim_id == session.selected_claim_id), None)
        if selected is None:
            raise AgentInputError("CLAIM_SELECTION_REQUIRED", "4-Line Message Kernel を作るには、先に主張候補を選んでください。")
        revision = len(session.message_kernel_revisions) + 1
        emphasis = "コスト削減ではなく業務成果への接続として" if user_feedback else "業務成果への接続として"
        kernel = MessageKernel(
            revision=revision,
            premise=f"{session.audience or '聞き手'}は、AI 投資を Copilot など個人向けツール配布中心に進めている。",
            complication="しかし、業務プロセスに組み込まれない限り、利用率が上がっても成果や定着には接続しない。",
            claim=selected.title,
            action=f"次四半期は3業務に絞り、{emphasis}本番導入前提の Agent 実装へ予算と責任者を振り替える。",
            confidence=0.82 if revision == 1 else 0.88,
            notes=[
                "4行は Premise, Complication, Claim, Action の役割が重ならないように分離しています。",
                "数値効果は未確認のため、根拠整理ではギャップとして扱います。",
            ],
        )
        diagnosis = evaluate_kernel(
            kernel,
            audience=session.audience,
            evidence_count=len(session.supporting_evidence),
            objections_count=len(session.objections),
        )
        return AgentKernelResult(message_kernel=kernel, diagnosis=diagnosis)

    async def ground_evidence(self, session: SessionState, *, use_mock_evidence: bool = True) -> EvidenceGroundingResult:
        if session.current_message_kernel is None:
            raise AgentInputError("MESSAGE_KERNEL_REQUIRED", "根拠整理には 4-Line Message Kernel が必要です。")
        return ground_with_fixtures(session.current_message_kernel, self.settings.evidence_fixture_dir)

    async def build_deck_payload(self, session: SessionState, *, language: str = "ja-JP") -> dict[str, Any]:
        return build_deck_payload(session, language=language)
