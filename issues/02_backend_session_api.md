# Issue 02: Implement App Backend Session API

## Summary

Create a lightweight app backend that manages user sessions, stores intermediate Agent outputs, and serves the Web UI.

## Background

The application is a multi-step experience. The user starts with a rough Free Talk input, receives claim candidates, refines a 4-Line Message Kernel, and finally generates outputs. This requires session state.

The current MCP server generates decks but does not manage user sessions. Add a separate app backend for session orchestration.

## Scope

Implement a backend with the following responsibilities:

- Create sessions
- Store Free Talk input
- Store claim candidates
- Store selected claim
- Store 4-Line Message Kernel revisions
- Store diagnosis, evidence gaps, objections
- Store generated artifact URLs
- Provide API endpoints for UI
- Delegate Agent processing to Foundry Agent adapter or mock adapter

## Suggested Technology

Use one of the following:

- FastAPI if keeping Python-centric repository
- Next.js API Routes if building a React/Next UI
- Azure Functions if deployment speed is prioritized

For fastest integration with the existing Python MCP repo, FastAPI is recommended.

## Data Model

### Session

```json
{
  "session_id": "ses_01H...",
  "created_at": "2026-05-18T12:00:00Z",
  "updated_at": "2026-05-18T12:10:00Z",
  "status": "draft | awaiting_user_selection | refining_kernel | ready_to_generate | generated | error",
  "free_talk": "...",
  "audience": "役員会",
  "desired_action": "次四半期の投資方針を決める",
  "claim_candidates": [],
  "selected_claim_id": null,
  "message_kernel_revisions": [],
  "current_message_kernel": null,
  "diagnosis": null,
  "evidence_gaps": [],
  "objections": [],
  "artifacts": {
    "deck_url": null,
    "brief_url": null,
    "idea_map_url": null,
    "image_url": null
  },
  "agent_trace_summary": []
}
```

### ClaimCandidate

```json
{
  "claim_id": "claim_1",
  "title": "AI 導入はツール配布ではなく業務設計の問題である",
  "summary": "Copilot 配布ではなく業務プロセスに組み込む Agent 実装へ投資を移すべきという主張。",
  "angle": "strategy | operation | investment | risk | culture",
  "why_this_may_be_true": [
    "現場での利用が業務成果に接続していない",
    "PoC が本番化しづらい"
  ],
  "potential_weakness": [
    "既存 Copilot 投資との関係を説明する必要がある"
  ]
}
```

### MessageKernel

```json
{
  "revision": 1,
  "premise": "当社の AI 投資は、個人向けツール配布を中心に進んでいる。",
  "complication": "しかし、業務プロセスに組み込まれない限り、利用率は上がっても成果には接続しない。",
  "claim": "次の投資は、ツール利用拡大ではなく、業務単位の Agent 実装へ切り替えるべきである。",
  "action": "次四半期は3業務に絞り、PoC ではなく本番導入前提の Agent 開発に予算を振り替える。",
  "confidence": 0.78,
  "notes": [
    "action line is specific enough for executive decision"
  ]
}
```

### Diagnosis

```json
{
  "overall_score": 82,
  "strengths": [
    "主張が明確",
    "相手に求める判断が具体的"
  ],
  "issues": [
    {
      "severity": "high",
      "field": "complication",
      "message": "Copilot 配布型がなぜ成果に接続しないかの根拠が不足している。"
    }
  ],
  "recommended_questions": [
    "Copilot 配布後の利用状況を示す社内データはありますか？"
  ]
}
```

## API Endpoints

### `POST /api/sessions`

Create a new session.

Request:

```json
{}
```

Response:

```json
{
  "session_id": "ses_..."
}
```

### `GET /api/sessions/{session_id}`

Return session state.

Response:

```json
{
  "session": {}
}
```

### `POST /api/sessions/{session_id}/free-talk`

Submit or replace Free Talk input.

Request:

```json
{
  "free_talk": "ユーザーが雑に話した内容...",
  "audience": "役員会",
  "desired_action": "投資方針を決める"
}
```

Response:

```json
{
  "session": {}
}
```

### `POST /api/sessions/{session_id}/extract-claims`

Ask the Agent to extract claim candidates.

Request:

```json
{
  "max_candidates": 3
}
```

Response:

```json
{
  "claim_candidates": []
}
```

### `POST /api/sessions/{session_id}/select-claim`

Select one candidate.

Request:

```json
{
  "claim_id": "claim_2",
  "user_feedback": "この案が近い。ただしコスト削減ではなく業務成果を強調したい。"
}
```

Response:

```json
{
  "session": {}
}
```

### `POST /api/sessions/{session_id}/refine-kernel`

Create or refine the 4-Line Message Kernel.

Request:

```json
{
  "additional_user_input": "経営層にはライセンス費ではなく成果への接続として説明したい。"
}
```

Response:

```json
{
  "message_kernel": {},
  "diagnosis": {}
}
```

### `POST /api/sessions/{session_id}/ground-evidence`

Find evidence gaps, objections, and supporting points.

Request:

```json
{
  "use_mock_evidence": true
}
```

Response:

```json
{
  "evidence_gaps": [],
  "objections": [],
  "supporting_evidence": []
}
```

### `POST /api/sessions/{session_id}/generate-deck`

Generate the deck by calling the MCP server.

Request:

```json
{
  "language": "ja-JP"
}
```

Response:

```json
{
  "deck_url": "http://localhost:3000/decks/dck_..."
}
```

### `POST /api/sessions/{session_id}/generate-brief`

Generate a distributable Markdown/HTML brief.

Response:

```json
{
  "brief_url": "http://localhost:8080/artifacts/briefs/..."
}
```

## Storage

For local development, file-based JSON storage is acceptable.

Suggested directory:

```text
data/app/sessions/{session_id}.json
data/app/artifacts/{session_id}/brief.md
data/app/artifacts/{session_id}/brief.html
data/app/artifacts/{session_id}/idea-map.json
```

Do not store secrets in session JSON.

## Acceptance Criteria

- A developer can create a session through API.
- A session can persist Free Talk input.
- A session can store and return claim candidates.
- A session can store and return the current Message Kernel.
- Generated artifact URLs are stored in the session.
- API responses are JSON and stable enough for the UI to consume.
- Basic error responses are implemented.

## Error Format

All API errors should use:

```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "Session not found",
    "details": {}
  }
}
```

## Test Plan

Unit tests:

- Create session
- Get missing session returns 404
- Save Free Talk
- Store claim candidates
- Store Message Kernel
- Store artifact URLs

Manual tests:

1. Start backend.
2. Create session.
3. Submit Free Talk.
4. Retrieve session.
5. Confirm state persists after backend restart if file storage is used.

## Non-Goals

Do not implement the full Agent reasoning in this issue. Use mock outputs where needed.
