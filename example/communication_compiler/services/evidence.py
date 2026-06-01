from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from example.communication_compiler.models import (
    EvidenceGap,
    EvidenceGroundingResult,
    MessageKernel,
    Objection,
    SupportingEvidence,
)


def _load_fixture_chunks(fixture_dir: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    if not fixture_dir.exists():
        return chunks
    for path in sorted(fixture_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for chunk in payload.get("content", []):
            chunks.append(
                {
                    "source_id": payload.get("source_id", path.stem),
                    "title": payload.get("title", path.stem),
                    "source_type": payload.get("source_type", "mock"),
                    "chunk_id": chunk.get("chunk_id", "chunk"),
                    "text": chunk.get("text", ""),
                }
            )
    return chunks


def ground_with_fixtures(kernel: MessageKernel, fixture_dir: Path) -> EvidenceGroundingResult:
    chunks = _load_fixture_chunks(fixture_dir)
    evidence: list[SupportingEvidence] = []
    for index, chunk in enumerate(chunks[:3], start=1):
        text = str(chunk["text"])
        if "Copilot" in text or "PoC" in text or "業務" in text:
            target_line = "complication" if index == 1 else "claim"
            evidence.append(
                SupportingEvidence(
                    evidence_id=f"ev_{index}",
                    title=str(chunk["title"]),
                    summary=_summarize_evidence(text),
                    source_type=str(chunk["source_type"]),
                    source_ref=f"{chunk['source_id']}#{chunk['chunk_id']}",
                    strength="strong" if "限定的" in text or "定着" in text else "medium",
                    supports_kernel_line=target_line,
                    quoted_or_paraphrased_basis=text[:120],
                )
            )

    gaps = [
        EvidenceGap(
            gap_id="gap_1",
            description="業務 Agent 化した場合の対象業務別 ROI や処理時間短縮の見積が不足しています。",
            why_it_matters="予算振替の判断には、既存投資との差分と費用対効果を説明する必要があります。",
            suggested_source="対象業務の処理時間データ、PoC 結果、運用コスト見積、現場ヒアリング",
        )
    ]
    if not evidence:
        gaps.insert(
            0,
            EvidenceGap(
                gap_id="gap_0",
                description="現時点で、この主張を直接支える社内データは確認できていません。",
                why_it_matters="根拠なしに断定すると、聞き手は実行可否よりも信頼性を疑います。",
                suggested_source="社内利用ログ、業務KPI、会議メモ、運用担当者の定性証言",
            ),
        )

    objections = [
        Objection(
            objection_id="obj_1",
            objection="既に Copilot に投資しているのに、なぜ追加で Agent 開発が必要なのか。",
            response_strategy="Copilot 投資を否定せず、個人利用の底上げと業務プロセス組み込みの役割差を説明する。",
            evidence_needed="Copilot 利用率と業務成果の乖離、Agent 化対象業務の改善余地",
        ),
        Objection(
            objection_id="obj_2",
            objection="業務単位で作ると標準化できず、運用負荷が増えるのではないか。",
            response_strategy="対象業務を絞り、共通基盤と個別業務設計を分けて段階導入する計画を示す。",
            evidence_needed="対象業務の優先順位、共通コンポーネント、運用責任者",
        ),
    ]

    summary = (
        "主張の方向性は説明可能ですが、予算判断には対象業務別の効果見積が必要です。"
        if evidence
        else "根拠は未確認です。主張を弱めるか、必要な社内データを明示して進めるべきです。"
    )
    return EvidenceGroundingResult(
        supporting_evidence=evidence,
        evidence_gaps=gaps,
        objections=objections,
        grounding_summary=summary,
    )


def _summarize_evidence(text: str) -> str:
    if "限定的" in text:
        return "Copilot 配布後も、利用増加が業務成果へ十分に接続していないことを示しています。"
    if "本番化" in text or "定着" in text:
        return "PoC が増えても本番定着しづらい構造課題を示しています。"
    return text[:90]
