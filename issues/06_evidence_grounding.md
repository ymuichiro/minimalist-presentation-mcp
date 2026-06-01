# Issue 06: Implement Evidence Grounding, Evidence Gaps, and Objection Extraction

## Summary

Implement the step that checks whether the 4-Line Message Kernel can be supported, what evidence is missing, and what objections the audience may raise.

## Background

The application should not generate polished but unsupported slides. The Agent must help the user say what they want to say correctly.

The purpose of evidence grounding is not to let data discover the claim. The claim comes from the user's intent. Evidence is used to:

- support the claim
- identify weak points
- identify missing proof
- prepare for likely objections
- avoid hallucinated confidence

## User Story

As a user, I want the Agent to tell me what evidence supports my message, what evidence is missing, and what objections I should prepare for before generating the final deck.

## Scope

Implement:

- supporting evidence extraction
- evidence gap detection
- objection extraction
- response strategy suggestion
- source strength labels
- mock evidence mode for demo

## Data Sources

P0 may use mock evidence fixtures.

P1 may connect to:

- Azure AI Search
- SharePoint
- OneDrive
- Teams transcript export
- uploaded files
- local fixtures

## Evidence Fixture Format

Create fixtures under:

```text
fixtures/evidence/
```

Example file:

```json
{
  "source_id": "doc_ai_adoption_2026",
  "title": "AI活用状況調査 2026 Q1",
  "source_type": "internal_doc",
  "created_at": "2026-04-01",
  "content": [
    {
      "chunk_id": "chunk_1",
      "text": "Copilot ライセンス配布後、週次利用者は増加したが、定型業務の処理時間短縮は限定的だった。"
    }
  ]
}
```

## Output Schema

```json
{
  "supporting_evidence": [
    {
      "evidence_id": "ev_1",
      "title": "AI活用状況調査 2026 Q1",
      "summary": "Copilot 配布後、利用者数は増えたが業務成果への接続は限定的だった。",
      "source_type": "internal_doc",
      "source_ref": "doc_ai_adoption_2026#chunk_1",
      "strength": "strong",
      "supports_kernel_line": "complication",
      "quoted_or_paraphrased_basis": "週次利用者は増加したが、定型業務の処理時間短縮は限定的だった"
    }
  ],
  "evidence_gaps": [
    {
      "gap_id": "gap_1",
      "description": "業務 Agent 化した場合の対象業務別 ROI が不足している。",
      "why_it_matters": "予算振替の判断には費用対効果の説明が必要。",
      "suggested_source": "対象業務の工数データ、PoC 結果、運用コスト見積"
    }
  ],
  "objections": [
    {
      "objection_id": "obj_1",
      "objection": "既に Copilot に投資しているのに、なぜ追加で Agent 開発が必要なのか。",
      "response_strategy": "Copilot 投資を否定せず、個人利用と業務プロセス組み込みの役割差を説明する。",
      "evidence_needed": "Copilot 利用率と業務成果の乖離を示すデータ"
    }
  ],
  "grounding_summary": "主張の方向性は妥当だが、予算振替を正当化するには対象業務別の効果見積が必要。"
}
```

## Strength Labels

Use these labels:

```text
strong
medium
weak
needs_confirmation
```

Guidelines:

- `strong`: directly supports a kernel line using credible source
- `medium`: related but indirect
- `weak`: mostly anecdotal or user statement only
- `needs_confirmation`: plausible but not supported by available evidence

## UI Requirements

Display three panels.

### Supporting Evidence

For each item:

- title
- source type
- strength badge
- supports which kernel line
- summary
- source reference

### Evidence Gaps

For each gap:

- description
- why it matters
- suggested source

### Objections

For each objection:

- objection
- response strategy
- evidence needed

Buttons:

- `追加で話す`
- `この根拠で進める`
- `根拠不足を明記して進める`

## Agent Behavior

The Agent must not invent sources.

If evidence is not found, it must say so.

Bad:

```text
社内データによると、Agent 化により30%効率化できます。
```

Good:

```text
現時点では、Agent 化による効率化率を示す社内データは見つかっていません。
この主張を強く言うには、対象業務の処理時間データが必要です。
```

## Backend Endpoint

```text
POST /api/sessions/{session_id}/ground-evidence
```

Request:

```json
{
  "use_mock_evidence": true,
  "search_query_hint": "AI活用 Copilot PoC 本番化 業務成果"
}
```

Response:

```json
{
  "supporting_evidence": [],
  "evidence_gaps": [],
  "objections": [],
  "grounding_summary": "..."
}
```

## Acceptance Criteria

- Evidence grounding can run after Message Kernel exists.
- Supporting evidence is linked to kernel lines.
- Evidence gaps are shown when evidence is missing.
- Objections are generated.
- No unsupported numeric claims are invented.
- Mock evidence mode works for demo.
- Results are stored in session.

## Test Plan

Unit tests:

- Evidence output schema validation
- Strength label validation
- Gap output when no evidence fixture matches
- Objection output exists for claims with action line

Manual tests:

1. Generate kernel.
2. Run grounding with mock evidence.
3. Confirm at least one support, one gap, and one objection appear.
4. Remove fixtures and confirm gaps are produced rather than fake evidence.

## Non-Goals

Do not build full enterprise search infrastructure in P0. Mock evidence is acceptable for contest demo if clearly labeled.
