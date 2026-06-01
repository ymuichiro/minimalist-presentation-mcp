# Issue 12: Prepare Contest Demo Scenario and Documentation

## Summary

Write documentation and demo materials that clearly position the application as a communication-structuring Agent, not a slide-generation tool.

## Background

The implementation can be misunderstood if the demo only shows final slide generation. The demo must show the intermediate process:

```text
rough thought
→ claim candidates
→ 4-Line Message Kernel
→ diagnosis
→ evidence gaps and objections
→ deck and brief
```

## Required Documentation

Add or update the following:

```text
README.md
docs/concept.md
docs/architecture.md
docs/demo_script.md
docs/message_kernel.md
docs/foundry_agent.md
```

## README Opening Copy

Use this concept in the README.

```markdown
# Minimalist Presentation MCP / Communication Compiler

This project is not a generic slide generator.

It is a communication-structuring application powered by an Azure AI Foundry Agent.
The Agent listens to rough user thoughts, extracts possible claims, compresses the selected claim into a 4-Line Message Kernel, diagnoses contradictions and evidence gaps, and then calls the Minimalist Presentation MCP server to expand the refined message into a five-page Message-First Deck.

The deck is the UI.
The real output is a sharpened business message.
```

Japanese version:

```markdown
# Minimalist Presentation MCP / Communication Compiler

このプロジェクトは、単なるスライド生成ツールではありません。

Azure AI Foundry Agent がユーザーの雑な発話を受け取り、
言いたいことの候補を抽出し、
選ばれた主張を 4-Line Message Kernel に圧縮し、
矛盾・根拠不足・反論可能性を診断したうえで、
Minimalist Presentation MCP を呼び出して5枚の Message-First Deck へ展開します。

スライドは UI です。
本当の成果物は、研ぎ澄まされたビジネスメッセージです。
```

## Demo Script

The demo should follow this sequence.

### Scene 1: Problem

Say:

```text
AI can already generate slides.
But in real business communication, the hard part is not drawing slides.
The hard part is sharpening what you actually want to say.
```

### Scene 2: Free Talk

Paste the demo Free Talk.

```text
最近、社内で AI 活用を進めたいんだけど、みんな Copilot を入れればいいと思っていて、
でも実際には業務に入っていない気がしている。現場はプロンプトを書く時間もないし、
ナレッジも散らばっているし、PoC は増えるけど定着しない。
だから、単にライセンスを配るより、業務単位で Agent を作る方に予算を寄せたい。
ただ、経営層にはコスト削減だけで説明したくない。
むしろ、業務プロセスの再設計として伝えたい。
```

### Scene 3: Claim Candidates

Show three candidates.

Say:

```text
The Agent does not immediately make slides.
It first asks: what is the user really trying to say?
```

### Scene 4: 4-Line Message Kernel

Show the selected candidate compressed into four lines.

Say:

```text
This is the real intermediate artifact.
The final deck is generated only after this message kernel is refined.
```

### Scene 5: Diagnosis

Show weaknesses.

Say:

```text
The Agent points out where the message is vague, generic, unsupported, or not yet decidable.
```

### Scene 6: Evidence Grounding

Show evidence gaps and objections.

Say:

```text
Internal data is not used to invent the claim.
It is used to support, challenge, and correct the user's intended claim.
```

### Scene 7: Deck Generation

Generate deck.

Say:

```text
Now that the message is sharpened, the MCP server expands it into a five-page Message-First Deck.
```

### Scene 8: Brief / Idea Map

Show brief and/or idea map if available.

Say:

```text
The output is not limited to slides.
The same structured message can become a brief, a map, or other communication artifacts.
```

### Closing

Say:

```text
This is not a slide generator.
It is a Communication Compiler: it turns rough thoughts into a business message that can be understood, challenged, and acted on.
```

## Architecture Diagram

Include this in `docs/architecture.md`.

```text
User Free Talk
    ↓
Simple Web UI
    ↓
App Backend
    ↓
Azure AI Foundry Agent
    ├─ Claim Candidate Extraction
    ├─ 4-Line Message Kernel
    ├─ Diagnosis
    ├─ Evidence Grounding
    └─ Deck Payload Builder
          ↓
Minimalist Presentation MCP
          ↓
Five-page Message-First Deck
```

## Zenn Article Outline

```markdown
# スライド生成ではなく、コミュニケーションをコンパイルする Agent を作った

## 背景
- 生成AIで資料は作れるようになった
- しかし実務で難しいのは「何を言うべきか」を研ぎ澄ますこと

## コンセプト
- Communication Compiler
- 4-Line Message Kernel
- Message-First Deck

## 体験
- 雑に話す
- Agent が言いたいこと候補を3つ出す
- 4行に圧縮する
- 弱点・根拠不足・反論を診断する
- 5枚に展開する

## アーキテクチャ
- Azure AI Foundry Agent
- MCP server
- Simple Web UI

## 実装
- Agent orchestration
- MCP integration
- Message Kernel schema
- Evidence grounding
- Deck renderer

## デモ
- Free Talk
- Claim candidates
- Kernel refinement
- Deck generation

## 今後
- Teams / SharePoint
- Voice input
- PowerPoint export
- Message Kernel library
```

## Acceptance Criteria

- README explains the product correctly.
- Docs include architecture and demo script.
- Demo script can be followed without conversation history.
- Zenn article outline exists.
- Documentation avoids positioning the product as a mere slide generator.
- Documentation explains why the 4-Line Message Kernel matters.
- Documentation explains why Azure AI Foundry Agent is the main orchestrator.
- Documentation explains the MCP server's tool role.

## Non-Goals

Do not write the final Zenn article in this issue unless explicitly requested. Create the structure and copy blocks needed for it.
