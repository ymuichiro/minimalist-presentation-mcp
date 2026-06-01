from __future__ import annotations

from html import escape
from typing import Any

from example.communication_compiler.models import SessionState


class DeckPreconditionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def assert_deck_preconditions(session: SessionState, *, force: bool = False) -> list[str]:
    if session.current_message_kernel is None:
        raise DeckPreconditionError("MESSAGE_KERNEL_REQUIRED", "Deck generation requires a finalized 4-Line Message Kernel.")
    warnings: list[str] = []
    if not session.supporting_evidence and not session.evidence_gaps and not force:
        raise DeckPreconditionError(
            "EVIDENCE_GROUNDING_REQUIRED",
            "Evidence grounding has not been run. Run grounding first or retry with force=true.",
        )
    if not session.supporting_evidence and force:
        warnings.append("DECK_GENERATED_WITHOUT_EVIDENCE")
    if session.diagnosis:
        warnings.extend(session.diagnosis.warnings)
    return sorted(set(warnings))


def build_deck_payload(session: SessionState, *, language: str = "ja-JP") -> dict[str, Any]:
    if session.current_message_kernel is None:
        raise DeckPreconditionError("MESSAGE_KERNEL_REQUIRED", "Deck generation requires a finalized 4-Line Message Kernel.")
    kernel = session.current_message_kernel
    evidence_html = _evidence_capsule(session)
    execution_html = _execution_capsule(session)
    title = _deck_title(session)
    action_statement = _action_statement_for_slide(kernel.action)
    return {
        "format": "json",
        "content": {
            "schema_version": "message-first-deck/v1",
            "language": language,
            "title": title,
            "subtitle": "4-Line Message Kernel から生成",
            "metadata": {
                "audience": session.audience or "未指定",
                "purpose": "AI投資方針の見直し",
                "desired_action": session.desired_action or kernel.action,
                "created_by": "Communication Compiler Agent",
            },
            "slides": {
                "M1": {
                    "type": "message",
                    "watch": "結論",
                    "statement": kernel.claim,
                    "sub_message": f"この提案は、{kernel.complication} という前提に基づく。",
                    "speaker_note": "中心命題を先に提示し、ツール導入ではなく判断すべき方針転換として扱う。",
                },
                "M2": {
                    "type": "message",
                    "watch": "戦略",
                    "statement": "広い配布より、成果が測れる業務に絞って深く組み込む。",
                    "sub_message": "既存ツール投資を否定せず、個人利用と業務プロセス組み込みの役割を分けて説明する。",
                    "speaker_note": "制約と優先順位を示し、なぜ広げるより絞るべきかを説明する。",
                },
                "M3": {
                    "type": "message",
                    "watch": "求める判断",
                    "statement": action_statement,
                    "sub_message": "対象・期間・予算配分を明確にし、次フェーズ投資の判断に進む。",
                    "speaker_note": "最後は具体的な決定事項と次アクションに接続する。",
                },
                "E1": {
                    "type": "html_capsule",
                    "watch": "根拠：現状と構造",
                    "claim": "現状の AI 活用は、利用拡大と業務成果の接続にギャップがある。",
                    "html": evidence_html,
                    "fallback_text": "現状の根拠と不足している根拠を分け、主張の強さを過大に見せない。",
                    "speaker_note": "ここでは Premise と Complication を支える情報を示す。不足根拠は不足として明示する。",
                },
                "E2": {
                    "type": "html_capsule",
                    "watch": "実行性：反論と次手",
                    "claim": "反論を処理しながら、対象業務を絞った実行計画へ進める。",
                    "html": execution_html,
                    "fallback_text": "想定反論、対応方針、次に集めるべき根拠をセットで提示する。",
                    "speaker_note": "ここでは実行可能性と反論処理を示し、判断への不安を下げる。",
                },
            },
        },
    }


def _deck_title(session: SessionState) -> str:
    selected = next((item for item in session.claim_candidates if item.claim_id == session.selected_claim_id), None)
    if selected:
        return selected.title
    if session.current_message_kernel:
        return session.current_message_kernel.claim[:42]
    return "Communication Compiler Deck"


def _action_statement_for_slide(action: str) -> str:
    if len(action) <= 92:
        return action
    if "20%" in action and "8週間" in action and ("3業務" in action or "問い合わせ" in action):
        return "3業務・8週間検証・20%予算振替を、次四半期の役員会決議として承認する。"
    return action[:88].rstrip("、。 ") + "。"


def _evidence_capsule(session: SessionState) -> str:
    evidence_cards = "".join(
        f"""
        <article class="cc-card" data-chart-card>
          <strong>{escape(item.title)}</strong>
          <span>{escape(item.strength)} / {escape(item.supports_kernel_line)}</span>
          <p>{escape(item.summary)}</p>
          <small>{escape(item.source_ref)}</small>
        </article>
        """
        for item in session.supporting_evidence
    )
    if not evidence_cards:
        evidence_cards = """
        <article class="cc-card cc-muted">
          <strong>根拠未確認</strong>
          <p>現時点で、この主張を直接支える社内データは確認できていません。</p>
        </article>
        """
    gap_cards = "".join(
        f"""
        <li>
          <strong>{escape(gap.description)}</strong>
          <span>{escape(gap.why_it_matters)}</span>
        </li>
        """
        for gap in session.evidence_gaps[:3]
    )
    return f"""
    <section class="capsule cc-capsule">
      <style>
        .cc-capsule {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; padding: 18px; height: 100%; display: grid; grid-template-columns: 1.12fr .88fr; gap: 14px; background: #fff; color: #111; }}
        .cc-capsule h2 {{ margin: 0 0 8px; font-size: 18px; letter-spacing: 0; }}
        .cc-grid {{ display: grid; gap: 8px; }}
        .cc-card {{ border: 1px solid #e5e5e5; border-radius: 8px; padding: 10px; background: #fafafa; display: grid; gap: 4px; }}
        .cc-card strong {{ font-size: 13px; }}
        .cc-card span, .cc-card small {{ color: #666; font-size: 10.5px; }}
        .cc-card p {{ margin: 0; font-size: 11.5px; line-height: 1.32; }}
        .cc-muted {{ border-style: dashed; }}
        .cc-gap-list {{ margin: 0; padding-left: 18px; display: grid; gap: 8px; }}
        .cc-gap-list li {{ font-size: 12px; line-height: 1.35; }}
        .cc-gap-list span {{ display: block; color: #666; margin-top: 3px; }}
      </style>
      <div>
        <h2>Supporting Evidence</h2>
        <div class="cc-grid">{evidence_cards}</div>
      </div>
      <div>
        <h2>Evidence Gaps</h2>
        <ul class="cc-gap-list">{gap_cards}</ul>
      </div>
    </section>
    """.strip()


def _execution_capsule(session: SessionState) -> str:
    objection_rows = "".join(
        f"""
        <tr>
          <td>{escape(item.objection)}</td>
          <td>{escape(item.response_strategy)}</td>
          <td>{escape(item.evidence_needed)}</td>
        </tr>
        """
        for item in session.objections[:2]
    )
    if not objection_rows:
        objection_rows = """
        <tr><td>反論未整理</td><td>根拠整理を先に実行する。</td><td>聞き手の懸念と必要証拠</td></tr>
        """
    return f"""
    <section class="capsule cc-capsule cc-execution">
      <style>
        .cc-execution {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; padding: 24px; height: 100%; display: grid; gap: 18px; background: #fff; color: #111; }}
        .cc-steps {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
        .cc-step {{ border-left: 4px solid #111; background: #fafafa; padding: 12px; }}
        .cc-step strong {{ display: block; font-size: 15px; margin-bottom: 6px; }}
        .cc-step span {{ color: #555; font-size: 12px; line-height: 1.4; }}
        .cc-objections {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
        .cc-objections th, .cc-objections td {{ border: 1px solid #e5e5e5; padding: 9px; vertical-align: top; }}
        .cc-objections th {{ background: #f5f5f5; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0; }}
      </style>
      <div class="cc-steps">
        <div class="cc-step"><strong>1. 対象業務</strong><span>成果が測れる3業務に絞る</span></div>
        <div class="cc-step"><strong>2. 責任範囲</strong><span>業務オーナーと運用責任を定義</span></div>
        <div class="cc-step"><strong>3. 根拠確認</strong><span>利用率ではなく業務KPIで検証</span></div>
        <div class="cc-step"><strong>4. 判断</strong><span>次四半期の予算配分へ接続</span></div>
      </div>
      <table class="cc-objections">
        <thead><tr><th>Likely Objection</th><th>Response Strategy</th><th>Evidence Needed</th></tr></thead>
        <tbody>{objection_rows}</tbody>
      </table>
    </section>
    """.strip()
