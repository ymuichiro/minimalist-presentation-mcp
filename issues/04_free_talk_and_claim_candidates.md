# Issue 04: Implement Free Talk Intake and Three Claim Candidate Extraction

## Summary

Implement the first visible user experience: the user enters rough thoughts, and the Agent extracts three possible interpretations of what the user may really want to say.

## Background

The product must not begin with a generic questionnaire. The user should be able to speak or write freely. The Agent should infer structure from rough input and return claim candidates.

This creates the key user experience:

> “I just talked roughly, but the Agent understood the possible points I wanted to make.”

## User Story

As a user, I want to paste or type an unstructured thought dump so that the Agent can identify several possible messages I may be trying to communicate.

## UI Requirements

Create a Free Talk input area.

Fields:

- `free_talk`: required multiline text
- `audience`: optional text
- `desired_action`: optional text
- `tone`: optional select
  - direct
  - cautious
  - executive
  - technical
  - narrative

Example placeholder:

```text
思っていることをそのまま話してください。
整理されていなくて構いません。
例: AI 活用を進めたいが、今の Copilot 配布中心の進め方では成果につながっていない気がする...
```

Primary button:

```text
言いたいこと候補を抽出する
```

## Backend Flow

Endpoint:

```text
POST /api/sessions/{session_id}/free-talk
POST /api/sessions/{session_id}/extract-claims
```

The backend should:

1. Save Free Talk.
2. Call Agent claim extraction.
3. Store claim candidates in session.
4. Return candidates to UI.

## Agent Prompt Requirements

The Agent must produce exactly three claim candidates unless the input is too short.

Each candidate should represent a different possible interpretation.

The candidates should differ by angle, for example:

- strategy
- investment
- operation
- risk
- culture
- product
- governance

Prompt behavior:

```text
Given the user's rough input, infer what they may actually want to say.
Do not summarize the input.
Extract three possible business claims.
Each claim must be something that can be argued, not just a topic.
Each claim must imply a different framing.
```

## Output Format

```json
{
  "claim_candidates": [
    {
      "claim_id": "claim_1",
      "title": "AI 導入はツール配布ではなく業務設計の問題である",
      "summary": "現場の利用努力ではなく、業務プロセスに組み込まれた Agent 設計へ投資を移すべきという主張。",
      "angle": "strategy",
      "why_this_may_be_true": [
        "Copilot 配布だけでは業務成果に接続しづらい",
        "PoC が本番化しない問題がある"
      ],
      "potential_weakness": [
        "既存 Copilot 投資との関係を説明する必要がある"
      ]
    }
  ],
  "recommended_next_question": "この3案のうち、あなたの感覚に一番近いものはどれですか？"
}
```

## UI Display

For each candidate, show:

- title
- angle badge
- summary
- why this may be true
- potential weakness
- select button

Example card:

```text
Candidate A: 戦略フレーム
AI 導入はツール配布ではなく業務設計の問題である

Why:
- Copilot 配布だけでは業務成果に接続しづらい
- PoC が本番化しない問題がある

Weakness:
- 既存 Copilot 投資との関係説明が必要
```

## Empty / Low-Quality Input Handling

If Free Talk is too short, return:

```json
{
  "error": {
    "code": "FREE_TALK_TOO_SHORT",
    "message": "もう少し話してください。最低でも300文字程度あると、言いたいことの候補を抽出できます。"
  }
}
```

Recommended threshold:

- P0: 150 Japanese characters minimum
- Ideal: 500+ characters

## Acceptance Criteria

- User can submit Free Talk.
- Backend persists the Free Talk.
- Agent returns three claim candidates.
- UI displays all three candidates.
- User can select one candidate.
- Selected claim is stored in the session.
- Low-quality input returns a helpful message.

## Test Data

Use this sample Free Talk:

```text
最近、社内で AI 活用を進めたいんだけど、みんな Copilot を入れればいいと思っていて、
でも実際には業務に入っていない気がしている。現場はプロンプトを書く時間もないし、
ナレッジも散らばっているし、PoC は増えるけど定着しない。
だから、単にライセンスを配るより、業務単位で Agent を作る方に予算を寄せたい。
ただ、経営層にはコスト削減だけで説明したくない。
むしろ、業務プロセスの再設計として伝えたい。
```

Expected candidate themes:

1. AI investment should shift from tool distribution to workflow-embedded agents.
2. The problem is not employee skill but operating model design.
3. The next budget decision should prioritize production Agent use cases over broad license expansion.

## Non-Goals

Do not generate the final deck in this issue. Claim extraction must remain an early-stage step.
