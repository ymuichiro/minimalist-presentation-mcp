from __future__ import annotations

from typing import Any


def sample_deck() -> dict[str, Any]:
    capsule = """
<section class="capsule" data-chart>
  <style>
    .capsule { font-family: sans-serif; padding: 22px; height: 100%; }
    .grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 16px; align-items: stretch; }
    .panel { border: 1px solid #ddd; padding: 16px; background: #fff; }
    .metric { margin: 0 0 12px; font-size: 28px; font-weight: 700; }
    .label { margin: 0 0 6px; font-size: 12px; color: #666; text-transform: uppercase; }
    .notes { margin: 0; padding-left: 18px; line-height: 1.5; }
    .summary { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 12px; }
    .mini-card { padding: 10px 12px; border-radius: 10px; background: #f5f3ee; }
    .mini-card strong { display: block; margin-bottom: 4px; font-size: 12px; }
    svg { width: 100%; height: auto; display: block; }
  </style>
  <div class="grid">
    <div class="panel">
      <p class="label">効果指標</p>
      <p class="metric">一次回答時間 42%短縮</p>
      <svg viewBox="0 0 320 150" role="img" aria-label="導入前後の一次回答時間比較">
        <g data-chart-bar data-label="導入前の一次回答時間" data-value="19分" data-detail="問い合わせ分類と初回ドラフト作成が手作業中心">
          <title>導入前の一次回答時間: 19分
問い合わせ分類と初回ドラフト作成が手作業中心</title>
          <rect x="28" y="36" width="96" height="72" rx="6" fill="#d9d9d9"></rect>
        </g>
        <g data-chart-bar data-label="PoC後の一次回答時間" data-value="11分" data-detail="分類自動化とテンプレート提示で短縮">
          <title>PoC後の一次回答時間: 11分
分類自動化とテンプレート提示で短縮</title>
          <rect x="180" y="62" width="96" height="46" rx="6" fill="#8f2f2b"></rect>
        </g>
        <line x1="20" y1="108" x2="300" y2="108" stroke="#bbbbbb"></line>
      </svg>
      <div data-chart-series>
        <div data-chart-item>
          <span data-chart-value>19分</span>
          <span data-chart-label>導入前の一次回答時間</span>
          <span data-chart-meta>手作業仕分けが中心</span>
        </div>
        <div data-chart-item>
          <span data-chart-value>11分</span>
          <span data-chart-label>PoC後の一次回答時間</span>
          <span data-chart-meta>分類自動化とテンプレート提示</span>
        </div>
      </div>
      <div class="summary">
        <div class="mini-card">
          <strong>改善幅</strong>
          8分短縮
        </div>
        <div class="mini-card">
          <strong>補足</strong>
          週15件の手戻り抑制
        </div>
      </div>
    </div>
    <div class="panel">
      <p class="label">差が出る要因</p>
      <ul class="notes">
        <li>問い合わせ分類を自動化し、担当者の仕分け工数を削減</li>
        <li>回答テンプレートを参照し、初回ドラフト作成を短縮</li>
        <li>承認フローを維持したまま、手戻りを週15件抑制</li>
      </ul>
    </div>
  </div>
</section>
""".strip()
    return {
        "schema_version": "message-first-deck/v1",
        "language": "ja-JP",
        "title": "生成AI活用提案",
        "subtitle": "業務プロセス再設計としてのAI導入",
        "metadata": {
            "audience": "経営層",
            "purpose": "承認獲得",
            "desired_action": "8週間PoCの開始承認",
            "created_by": "AI",
        },
        "slides": {
            "M1": {
                "type": "message",
                "watch": "この提案の中心命題",
                "statement": "生成AI導入は、ツール導入ではなく業務プロセス再設計として扱うべきである。",
                "sub_message": "単発PoCではなく、業務単位で効果と責任範囲を定義する必要がある。",
                "speaker_note": "論点をツール選定から業務設計へ移す。",
            },
            "M2": {
                "type": "message",
                "watch": "判断すべき制約",
                "statement": "成果が出る領域を絞り、横展開よりも深い業務適用を優先する。",
                "sub_message": "全社一律導入ではなく、効果測定可能な業務から始める。",
                "speaker_note": "成果が見える領域に集中する。",
            },
            "M3": {
                "type": "message",
                "watch": "求める意思決定",
                "statement": "まず1業務を対象に、8週間の業務再設計PoCへ進むべきである。",
                "sub_message": "本日は対象業務、責任者、評価指標の合意を取りたい。",
                "speaker_note": "合意事項に接続する。",
            },
            "E1": {
                "type": "html_capsule",
                "watch": "根拠：現状課題の構造",
                "claim": "現在の生成AI活用は、業務成果ではなくツール利用に偏っている。",
                "html": capsule,
                "fallback_text": "読み取り：19分かかっていた一次回答を11分まで短縮できれば、PoCは業務KPIと接続できる。",
                "speaker_note": "現状課題を構造的に見せる。",
            },
            "E2": {
                "type": "html_capsule",
                "watch": "根拠：実行計画と反論処理",
                "claim": "8週間PoCなら、業務効果・運用負荷・リスクを同時に検証できる。",
                "html": capsule,
                "fallback_text": "読み取り：8週間で効果測定、運用設計、リスク管理を同じ枠組みで確認できる。",
                "speaker_note": "実行可能性と反論処理を示す。",
            },
        },
    }
