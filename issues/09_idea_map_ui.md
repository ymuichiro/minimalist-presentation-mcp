# Issue 09: Implement Idea Map Data Model and Visualization UI

## Summary

Add an Idea Map that visually shows how the user's rough thoughts were structured into premise, complication, claim, action, evidence, gaps, and objections.

## Background

The product must visually demonstrate that the Agent is not merely making slides. It is mapping the user's intent and communication structure.

The Idea Map is a key demo artifact.

## User Story

As a user, I want to see how my rough thoughts were transformed into a structured message so that I can understand and refine my own thinking.

## Data Model

Create an Idea Map JSON representation.

```json
{
  "nodes": [
    {
      "id": "premise",
      "type": "kernel_line",
      "label": "Audience Premise",
      "text": "当社の AI 投資は、個人向けツール配布を中心に進んでいる。"
    },
    {
      "id": "complication",
      "type": "kernel_line",
      "label": "Complication",
      "text": "しかし、業務プロセスに組み込まれない限り、利用率は上がっても成果には接続しない。"
    },
    {
      "id": "claim",
      "type": "kernel_line",
      "label": "Core Claim",
      "text": "次の投資は、業務単位の Agent 実装へ切り替えるべきである。"
    },
    {
      "id": "action",
      "type": "kernel_line",
      "label": "Requested Action",
      "text": "次四半期は3業務に絞り、予算を振り替える。"
    },
    {
      "id": "ev_1",
      "type": "evidence",
      "label": "Supporting Evidence",
      "text": "Copilot 利用は増えたが成果接続は限定的。"
    },
    {
      "id": "gap_1",
      "type": "gap",
      "label": "Evidence Gap",
      "text": "対象業務別 ROI が不足。"
    },
    {
      "id": "obj_1",
      "type": "objection",
      "label": "Objection",
      "text": "既存 Copilot 投資との関係は？"
    }
  ],
  "edges": [
    {
      "from": "premise",
      "to": "complication",
      "type": "leads_to"
    },
    {
      "from": "complication",
      "to": "claim",
      "type": "supports_reframe"
    },
    {
      "from": "claim",
      "to": "action",
      "type": "requires_decision"
    },
    {
      "from": "ev_1",
      "to": "complication",
      "type": "supports"
    },
    {
      "from": "gap_1",
      "to": "action",
      "type": "weakens"
    },
    {
      "from": "obj_1",
      "to": "claim",
      "type": "challenges"
    }
  ]
}
```

## Node Types

Use these types:

```text
kernel_line
claim_candidate
evidence
gap
objection
question
user_input
```

## Edge Types

Use these types:

```text
leads_to
supports
weakens
challenges
requires_decision
refines
derived_from
```

## UI Requirements

Render a simple graph or map.

P0 options:

- React Flow
- Mermaid
- SVG
- HTML/CSS boxes and arrows

For fastest implementation, React Flow is recommended if using React.

Layout suggestion:

```text
[Audience Premise] → [Complication] → [Core Claim] → [Requested Action]
       ↑                   ↑               ↑                 ↑
   evidence             evidence        objection          evidence gap
```

Visual requirements:

- Kernel line nodes should be prominent.
- Evidence nodes should connect to the line they support.
- Gap nodes should visually indicate uncertainty.
- Objection nodes should challenge claim/action.
- Clicking a node should show detail text.

## Backend Endpoint

```text
GET /api/sessions/{session_id}/idea-map
```

Response:

```json
{
  "idea_map": {
    "nodes": [],
    "edges": []
  }
}
```

Optional generation endpoint:

```text
POST /api/sessions/{session_id}/generate-idea-map
```

## Generation Rules

The map should be generated from session state, not from a new LLM call if possible.

Mapping rules:

- Kernel lines become four core nodes.
- Supporting evidence becomes evidence nodes.
- Evidence gaps become gap nodes.
- Objections become objection nodes.
- Selected claim candidate may be linked to the `claim` node.
- Free Talk may be represented as one source node if useful.

## Acceptance Criteria

- Idea Map JSON can be generated from session state.
- UI can render the map.
- Kernel lines appear as main path.
- Evidence, gaps, and objections connect to relevant kernel lines.
- Node detail is visible on click or hover.
- Map updates after kernel refinement.

## Test Plan

Unit tests:

- Idea Map builder creates four kernel nodes.
- Evidence links to correct kernel line.
- Empty evidence still renders kernel path.
- Objections link to claim/action.

Manual tests:

1. Complete kernel and evidence flow.
2. Open Idea Map.
3. Confirm visual path from premise to action.
4. Confirm gap and objection nodes are visible.

## Non-Goals

Do not implement complex graph editing. The map is a visualization, not a full whiteboard.
