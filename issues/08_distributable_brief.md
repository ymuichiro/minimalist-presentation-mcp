# Issue 08: Generate Distributable Markdown / HTML Brief

## Summary

Add a non-slide output: a detailed distributable brief in Markdown and optionally HTML.

## Background

A five-page deck is useful for presentation, but not always sufficient for thinking or distribution. The application should also output a written brief that expands the 4-Line Message Kernel into a readable document.

This reinforces the concept that the system is not merely creating slides. It is structuring communication.

## User Story

As a user, I want a written brief that explains my sharpened message in detail so that I can share it before or after a meeting.

## Output Types

P0:

- Markdown brief

P1:

- HTML brief

## Brief Structure

Generate a Markdown document with this structure.

```markdown
# {title}

## 1. 4-Line Message Kernel

| Line | Message |
|---|---|
| Audience Premise | ... |
| Complication | ... |
| Core Claim | ... |
| Requested Decision / Action | ... |

## 2. Executive Summary

Short prose summary of the intended message.

## 3. Why This Matters

Explain the complication and why the audience should care.

## 4. Core Argument

Explain the claim and reasoning.

## 5. Supporting Evidence

List supporting evidence with strength labels and source references.

## 6. Evidence Gaps

List missing evidence and why it matters.

## 7. Likely Objections and Responses

List objections and recommended responses.

## 8. Recommended Decision

State what the audience should decide.

## 9. Appendix: Agent Notes

Optional concise notes about uncertainty and next steps.
```

## Backend Endpoint

```text
POST /api/sessions/{session_id}/generate-brief
```

Request:

```json
{
  "format": "markdown"
}
```

Response:

```json
{
  "brief_markdown_url": "http://localhost:8080/artifacts/ses_x/brief.md",
  "brief_html_url": null
}
```

## Storage

Store under:

```text
data/app/artifacts/{session_id}/brief.md
data/app/artifacts/{session_id}/brief.html
```

## Content Requirements

The brief must:

- include the 4-Line Message Kernel
- include supporting evidence
- include evidence gaps
- include objections
- distinguish facts from Agent interpretation
- avoid unsupported numerical claims
- avoid pretending weak evidence is strong

## Example Brief Excerpt

```markdown
## 1. 4-Line Message Kernel

| Line | Message |
|---|---|
| Audience Premise | 当社の AI 投資は、個人向けツール配布を中心に進んでいる。 |
| Complication | しかし、業務プロセスに組み込まれない限り、利用率は上がっても成果には接続しない。 |
| Core Claim | 次の投資は、ツール利用拡大ではなく、業務単位の Agent 実装へ切り替えるべきである。 |
| Requested Decision / Action | 次四半期は3業務に絞り、PoC ではなく本番導入前提の Agent 開発に予算を振り替える。 |
```

## UI Requirements

On the output area, show:

- `Deck を開く`
- `Brief を開く`
- `Markdown をコピー`
- optional `HTML を開く`

Brief generation should be available after Message Kernel exists.

If evidence grounding is missing, show:

```text
根拠整理が未実行です。この Brief は主張中心で作成されます。
```

## Acceptance Criteria

- User can generate a Markdown brief.
- Brief includes kernel, evidence, gaps, objections, and decision.
- Brief is stored as a file.
- Brief URL is stored in session.
- UI displays link to brief.
- Brief does not require deck generation to exist.

## Test Plan

Unit tests:

- Brief builder works with full session.
- Brief builder works with missing evidence but includes warning.
- Markdown contains required headings.

Manual tests:

1. Generate kernel.
2. Generate evidence grounding.
3. Generate brief.
4. Open Markdown.
5. Confirm content matches session.

## Non-Goals

Do not implement rich document editing here. The brief can be static Markdown/HTML.
