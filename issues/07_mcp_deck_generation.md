# Issue 07: Integrate Existing MCP Server for Message-First Deck Generation

## Summary

Implement the integration that converts the final Message Kernel and evidence grounding results into a valid Message-First Deck payload and calls the existing MCP server to generate the five-page deck.

## Background

The existing MCP server already exposes:

- `get_presentation_guideline`
- `create_message_first_deck`

It accepts JSON or YAML content with schema version:

```text
message-first-deck/v1
```

The Agent should not generate a deck until:

- Free Talk exists
- selected claim exists
- current 4-Line Message Kernel exists
- diagnosis exists
- evidence grounding has run or been explicitly skipped

## Flow

```text
Session
  ↓
Message Kernel
  ↓
Evidence Grounding
  ↓
Deck Payload Builder
  ↓
MCP create_message_first_deck
  ↓
Deck URL
  ↓
UI
```

## Deck Payload Mapping

### M1: Core Thesis

Use the `claim` line from the Message Kernel.

```json
{
  "type": "message",
  "watch": "結論",
  "statement": "{kernel.claim}",
  "sub_message": "この提案は、{kernel.complication} という前提に基づく。",
  "speaker_note": "..."
}
```

### M2: Constraint / Strategy

Use the mechanism that explains how the claim should be pursued.

Derived from:

- selected claim
- complication
- evidence grounding
- response strategies

### M3: Decision / Action

Use the `action` line from the Message Kernel.

```json
{
  "type": "message",
  "watch": "求める判断",
  "statement": "{kernel.action}",
  "sub_message": "判断を曖昧にせず、対象・時期・責任範囲を明確にする。",
  "speaker_note": "..."
}
```

### E1: Evidence 1

Use current state and complication proof.

Should support:

- `premise`
- `complication`

Suggested formats:

- comparison grid
- bar chart
- table
- issue structure
- workflow failure map

### E2: Evidence 2

Use feasibility, objections, and execution plan.

Should support:

- `claim`
- `action`

Suggested formats:

- risk-response map
- execution timeline
- decision criteria table
- objection handling grid

## Payload Schema

Build this payload:

```json
{
  "format": "json",
  "content": {
    "schema_version": "message-first-deck/v1",
    "language": "ja-JP",
    "title": "業務 Agent 投資への転換提案",
    "subtitle": "4-Line Message Kernel から生成",
    "metadata": {
      "audience": "役員会",
      "purpose": "AI投資方針の見直し",
      "desired_action": "次四半期の予算振替判断",
      "created_by": "Communication Compiler Agent"
    },
    "slides": {
      "M1": {
        "type": "message",
        "watch": "結論",
        "statement": "...",
        "sub_message": "...",
        "speaker_note": "..."
      },
      "M2": {
        "type": "message",
        "watch": "戦略",
        "statement": "...",
        "sub_message": "...",
        "speaker_note": "..."
      },
      "M3": {
        "type": "message",
        "watch": "判断",
        "statement": "...",
        "sub_message": "...",
        "speaker_note": "..."
      },
      "E1": {
        "type": "html_capsule",
        "watch": "根拠",
        "claim": "...",
        "html": "...",
        "fallback_text": "...",
        "speaker_note": "..."
      },
      "E2": {
        "type": "html_capsule",
        "watch": "実行性",
        "claim": "...",
        "html": "...",
        "fallback_text": "...",
        "speaker_note": "..."
      }
    }
  }
}
```

## HTML Capsule Requirements

E1/E2 `html` must be partial HTML only.

Allowed:

- `<div>`
- `<section>`
- `<table>`
- `<ul>`
- `<ol>`
- `<svg>`
- inline style if needed
- data attributes

Avoid:

- `<html>`
- `<head>`
- `<body>`
- `<script>`
- `<iframe>`
- external CSS
- external JS
- external images
- runtime fetching

## Backend Endpoint

```text
POST /api/sessions/{session_id}/generate-deck
```

Request:

```json
{
  "language": "ja-JP",
  "force": false
}
```

Response:

```json
{
  "deck_id": "dck_...",
  "deck_url": "http://localhost:3000/decks/dck_...",
  "warnings": []
}
```

## Generation Preconditions

Return error if no kernel exists:

```json
{
  "error": {
    "code": "MESSAGE_KERNEL_REQUIRED",
    "message": "Deck generation requires a finalized 4-Line Message Kernel."
  }
}
```

Return warning if evidence grounding is missing:

```json
{
  "warning": {
    "code": "EVIDENCE_GROUNDING_SKIPPED",
    "message": "Evidence grounding has not been run. The generated deck may include weak evidence."
  }
}
```

Allow generation if user explicitly confirms.

## Acceptance Criteria

- Backend can build a valid `message-first-deck/v1` payload from session state.
- Backend calls MCP `create_message_first_deck`.
- Deck URL is returned and stored in session.
- MCP warnings are surfaced in UI.
- Deck generation is blocked if Message Kernel is missing.
- E1/E2 include evidence or explicitly state when evidence is unavailable.
- Generated deck reflects the final 4-Line Message Kernel.

## Test Plan

Unit tests:

- Payload builder produces required five slides.
- Payload builder rejects missing kernel.
- E1/E2 contain no script tags.
- MCP error is handled.

Manual tests:

1. Run through Free Talk → claim → kernel → evidence.
2. Generate deck.
3. Open deck URL.
4. Confirm M1/M3 match kernel claim/action.
5. Confirm E1/E2 contain grounding/gap information.

## Non-Goals

Do not implement PPTX export here. HTML deck output is sufficient for P0.
