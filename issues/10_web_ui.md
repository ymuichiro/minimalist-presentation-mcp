# Issue 10: Implement Contest Demo Web UI

## Summary

Build a simple Web UI that makes the Agentic communication-structuring workflow visible.

## Background

The UI must avoid looking like a generic chat or slide generator. The key visual experience is:

```text
rough thought
→ claim candidates
→ 4-Line Message Kernel
→ diagnosis
→ evidence gaps / objections
→ idea map
→ deck / brief outputs
```

## Recommended UI Layout

Single-page app with staged sections.

```text
┌───────────────────────────────────────────────┐
│ Header: Communication Compiler                │
├───────────────────────────────────────────────┤
│ Step 1: Free Talk                             │
├───────────────────────────────────────────────┤
│ Step 2: Claim Candidates                      │
├───────────────────────────────────────────────┤
│ Step 3: 4-Line Message Kernel                 │
│         + Diagnosis                           │
├───────────────────────────────────────────────┤
│ Step 4: Evidence / Gaps / Objections          │
├───────────────────────────────────────────────┤
│ Step 5: Idea Map                              │
├───────────────────────────────────────────────┤
│ Step 6: Outputs                               │
│         Deck / Brief / Optional Image         │
└───────────────────────────────────────────────┘
```

## Header Copy

Use this copy:

```text
Communication Compiler
話すだけで、言いたいことが「伝わる構造」になる。
```

Subtitle:

```text
AI Agent が雑な発話を 4-Line Message Kernel に圧縮し、根拠と反論を整理して、5枚の Message-First Deck に展開します。
```

## Step 1: Free Talk

Fields:

- Free Talk textarea
- Audience input
- Desired action input
- Tone select

Button:

```text
言いたいこと候補を抽出する
```

## Step 2: Claim Candidates

Display three cards.

Each card:

- angle
- title
- summary
- why this may be true
- potential weakness
- select button

Button:

```text
この方向で4行に圧縮する
```

## Step 3: 4-Line Message Kernel

Display as four rows:

```text
1. 相手の現在の前提
2. その前提では足りない理由
3. こちらが通したい主張
4. 相手に求める判断・行動
```

Show diagnosis next to it:

- score
- strengths
- issues
- recommended question

User can add feedback:

```text
追加で伝えたいこと
```

Buttons:

- `4行を改善する`
- `根拠を整理する`

## Step 4: Evidence / Gaps / Objections

Three columns:

```text
Supporting Evidence
Evidence Gaps
Likely Objections
```

Each item should have a strength or severity label.

Buttons:

- `このまま進める`
- `追加で話す`
- `資料化する`

## Step 5: Idea Map

Render graph or structured map.

If graph implementation is delayed, use a structured card layout:

```text
Premise → Complication → Claim → Action
Evidence under each node
Gaps and objections attached
```

## Step 6: Outputs

Show buttons:

- `Deck を開く`
- `Brief を開く`
- `Markdown をコピー`
- optional `Image を表示`

Also show:

```text
Final 4-Line Message Kernel
```

This is important. The final deck must be visually connected to the kernel.

## Demo Mode

Add a demo preset button:

```text
デモ用サンプルを入力
```

It should populate Free Talk with:

```text
最近、社内で AI 活用を進めたいんだけど、みんな Copilot を入れればいいと思っていて、
でも実際には業務に入っていない気がしている。現場はプロンプトを書く時間もないし、
ナレッジも散らばっているし、PoC は増えるけど定着しない。
だから、単にライセンスを配るより、業務単位で Agent を作る方に予算を寄せたい。
ただ、経営層にはコスト削減だけで説明したくない。
むしろ、業務プロセスの再設計として伝えたい。
```

Audience:

```text
役員会
```

Desired action:

```text
次四半期の AI 投資方針を決める
```

## State Handling

The UI should handle these states:

```text
idle
loading
success
error
```

Each section should show loading state independently.

## Error Display

Use user-friendly error messages.

Example:

```text
言いたいこと候補を抽出できませんでした。
入力が短すぎる可能性があります。もう少し詳しく話してください。
```

## Acceptance Criteria

- User can complete the full flow from Free Talk to Deck URL.
- UI clearly shows intermediate artifacts.
- UI does not look like a generic chatbot.
- Final output section shows deck and brief links.
- Demo preset works.
- Kernel remains visible after deck generation.
- Errors are displayed clearly.

## Test Plan

Manual tests:

1. Open UI.
2. Click demo preset.
3. Extract candidates.
4. Select candidate.
5. Generate kernel.
6. Refine kernel.
7. Ground evidence.
8. Generate deck.
9. Generate brief.
10. Confirm final output links.

## Non-Goals

Do not build a complex collaborative editor. This is a contest demo UI.
