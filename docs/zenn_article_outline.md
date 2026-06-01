# Zenn Article Outline

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
