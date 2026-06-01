from __future__ import annotations

import re

from example.communication_compiler.models import Diagnosis, DiagnosisIssue, KernelRubric, MessageKernel


GENERIC_WORDS = ("重要", "推進", "検討", "活用", "改善", "強化")
VAGUE_ACTION_WORDS = ("検討", "今後", "進めたい", "必要がある", "考える")
NUMERIC_RE = re.compile(r"(?<![A-Za-z0-9])\d+(?:\.\d+)?\s*(?:%|％|割|倍|円|万円|億円|人|件|時間|分|日|週|か月|ヶ月)")


def has_unsupported_numeric_claim(text: str, supporting_texts: list[str] | None = None) -> bool:
    if not NUMERIC_RE.search(text):
        return False
    support_blob = "\n".join(supporting_texts or [])
    for match in NUMERIC_RE.findall(text):
        if match in support_blob:
            return False
    return True


def evaluate_kernel(kernel: MessageKernel, *, audience: str, evidence_count: int = 0, objections_count: int = 0) -> Diagnosis:
    issues: list[DiagnosisIssue] = []
    strengths: list[str] = []
    warnings: list[str] = []

    specificity = 4 if len(kernel.premise) >= 20 and audience else 3
    complication_strength = 5 if any(marker in kernel.complication for marker in ("しかし", "一方", "限り", "なければ")) else 3
    claim_sharpness = 5 if any(marker in kernel.claim for marker in ("ではなく", "切り替える", "扱うべき", "優先")) else 3
    action_clarity = 5 if any(marker in kernel.action for marker in ("次四半期", "週間", "本日", "承認", "予算", "決める")) else 2
    non_redundancy = 4 if len({kernel.premise, kernel.complication, kernel.claim, kernel.action}) == 4 else 2
    evidence_supportability = 4 if evidence_count else 3
    objection_awareness = 4 if objections_count else 3
    audience_fit = 4 if audience else 2

    if len(kernel.claim) < 18 or all(word in kernel.claim for word in ("AI", "活用")) and not any(
        marker in kernel.claim for marker in ("ではなく", "として", "切り替える", "優先")
    ):
        issues.append(
            DiagnosisIssue(
                severity="high",
                field="claim",
                code="GENERIC_CLAIM",
                message="主張が一般論に寄っています。何を捨て、何へ切り替えるのかを明確にしてください。",
            )
        )
        warnings.append("GENERIC_CLAIM")
        claim_sharpness = min(claim_sharpness, 2)

    if len(kernel.complication) < 18 or "課題" in kernel.complication and len(kernel.complication) < 28:
        issues.append(
            DiagnosisIssue(
                severity="medium",
                field="complication",
                code="WEAK_COMPLICATION",
                message="Complication が弱く、なぜ現状の前提では不十分なのかが見えにくいです。",
            )
        )
        warnings.append("WEAK_COMPLICATION")
        complication_strength = min(complication_strength, 2)

    if any(word in kernel.action for word in VAGUE_ACTION_WORDS) and not any(
        marker in kernel.action for marker in ("承認", "決定", "予算", "いつ", "次四半期", "本日")
    ):
        issues.append(
            DiagnosisIssue(
                severity="high",
                field="action",
                code="VAGUE_ACTION",
                message="求める行動が曖昧です。誰が、いつ、何を決めるのかを明示してください。",
            )
        )
        warnings.append("VAGUE_ACTION")
        action_clarity = min(action_clarity, 2)

    if not audience:
        issues.append(
            DiagnosisIssue(
                severity="medium",
                field="audience",
                code="AUDIENCE_UNCLEAR",
                message="聞き手が未指定です。相手の責任範囲に合わせた表現にすると判断につながります。",
            )
        )
        warnings.append("AUDIENCE_UNCLEAR")

    if evidence_count == 0:
        issues.append(
            DiagnosisIssue(
                severity="medium",
                field="evidence",
                code="EVIDENCE_MISSING",
                message="現時点では主張を支える根拠が整理されていません。資料化前に根拠と反論を確認してください。",
            )
        )
        warnings.append("EVIDENCE_MISSING")

    if has_unsupported_numeric_claim("\n".join([kernel.premise, kernel.complication, kernel.claim, kernel.action])):
        issues.append(
            DiagnosisIssue(
                severity="high",
                field="numeric_claim",
                code="UNSUPPORTED_NUMERIC_CLAIM",
                message="数値主張がありますが、対応する根拠がありません。根拠を付けるか仮説として明記してください。",
            )
        )
        warnings.append("UNSUPPORTED_NUMERIC_CLAIM")

    if not issues:
        strengths.append("4行の役割が明確で、判断につながる構造になっています。")
    if claim_sharpness >= 4:
        strengths.append("主張が単なるテーマではなく、方針転換として表現されています。")
    if action_clarity >= 4:
        strengths.append("相手に求める判断が具体的です。")

    rubric = KernelRubric(
        specificity=specificity,
        complication_strength=complication_strength,
        claim_sharpness=claim_sharpness,
        action_clarity=action_clarity,
        non_redundancy=non_redundancy,
        evidence_supportability=evidence_supportability,
        objection_awareness=objection_awareness,
        audience_fit=audience_fit,
    )
    score = round(sum(rubric.model_dump().values()) / 40 * 100)
    recommended_questions = []
    if "EVIDENCE_MISSING" in warnings:
        recommended_questions.append("この主張を支える社内データや現場の具体例はありますか？")
    if "VAGUE_ACTION" in warnings:
        recommended_questions.append("最終的に誰に、いつまでに、何を決めてほしいですか？")
    if not recommended_questions:
        recommended_questions.append("この4行で相手が反論しそうな点はどこですか？")

    return Diagnosis(
        overall_score=score,
        strengths=strengths,
        issues=issues,
        recommended_questions=recommended_questions,
        rubric=rubric,
        warnings=sorted(set(warnings)),
    )
