# Issue 05: Implement 4-Line Message Kernel Generation, Diagnosis, and Refinement

## Summary

Implement the core product feature: converting a selected claim into a 4-Line Message Kernel, diagnosing its weaknesses, and refining it based on user feedback.

## Background

The five-page deck is not the main artifact. The main artifact before deck generation is the 4-Line Message Kernel.

This kernel represents the sharpened business message.

```text
1. Audience Premise
2. Complication / Gap
3. Core Claim
4. Requested Decision / Action
```

The Agent must not generate the deck until this kernel exists and has been diagnosed.

## User Story

As a user, I want the Agent to compress my rough idea into four sharp lines and tell me why the lines are weak, so that I can refine the actual message before creating any slides.

## Input

The feature requires:

- Free Talk
- selected claim candidate
- optional user feedback
- audience
- desired action

## Output

The Agent returns:

- 4-Line Message Kernel
- diagnosis
- recommended questions
- revision number

## Message Kernel Schema

```json
{
  "revision": 1,
  "premise": "当社の AI 投資は、個人向けツール配布を中心に進んでいる。",
  "complication": "しかし、業務プロセスに組み込まれない限り、利用率は上がっても成果には接続しない。",
  "claim": "次の投資は、ツール利用拡大ではなく、業務単位の Agent 実装へ切り替えるべきである。",
  "action": "次四半期は3業務に絞り、PoC ではなく本番導入前提の Agent 開発に予算を振り替える。",
  "confidence": 0.82,
  "notes": [
    "action line includes target period and decision type"
  ]
}
```

## Diagnosis Schema

```json
{
  "overall_score": 82,
  "strengths": [
    "主張が明確",
    "聞き手に求める判断が具体的"
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

## Diagnosis Rules

The Agent must evaluate the kernel using these criteria.

### 1. Claim Exists

The kernel must contain an arguable claim. It must not be a generic topic.

Bad:

```text
AI 活用を推進すべきである。
```

Good:

```text
AI 投資は個人向けツール配布から、業務単位の Agent 実装へ移すべきである。
```

### 2. Audience Premise Is Specific

The premise should describe the audience's current belief or organizational current state.

Bad:

```text
AI は重要である。
```

Good:

```text
当社の AI 投資は、個人向けツール配布を中心に進んでいる。
```

### 3. Complication Creates Tension

The second line must explain why the current premise is insufficient.

Bad:

```text
しかし、課題がある。
```

Good:

```text
しかし、業務プロセスに組み込まれない限り、利用率は上がっても成果には接続しない。
```

### 4. Claim Is Not Generic

The third line should force a reframing.

Bad:

```text
AI 活用をさらに推進すべきである。
```

Good:

```text
次の投資は、ツール利用拡大ではなく、業務単位の Agent 実装へ切り替えるべきである。
```

### 5. Action Is Decidable

The fourth line must indicate what the audience should decide or do.

Bad:

```text
今後検討したい。
```

Good:

```text
次四半期は3業務に絞り、本番導入前提の Agent 開発に予算を振り替える。
```

### 6. Lines Are Not Redundant

Each line must play a distinct role.

### 7. Evidence Can Support the Claim

The kernel must be testable or supportable with evidence.

### 8. Objections Are Anticipated

The kernel must imply what objections need to be handled.

## UI Requirements

Show the kernel as four editable rows.

```text
1. Audience Premise
2. Complication
3. Core Claim
4. Requested Action
```

Each row should have:

- label
- text
- warning badge if diagnosis issue applies
- optional edit control

Show diagnosis panel:

- overall score
- strengths
- issues grouped by severity
- recommended follow-up question

Buttons:

- `この4行を改善する`
- `追加情報を話す`
- `根拠を確認する`
- `この4行で資料化する`

## Refinement Flow

User may add feedback:

```text
経営層には、コスト削減ではなく業務成果への接続として伝えたい。
```

Backend endpoint:

```text
POST /api/sessions/{session_id}/refine-kernel
```

The Agent must create a new revision rather than overwriting the old one.

Store revision history:

```json
[
  {
    "revision": 1,
    "message_kernel": {},
    "diagnosis": {},
    "created_at": "..."
  },
  {
    "revision": 2,
    "message_kernel": {},
    "diagnosis": {},
    "created_at": "..."
  }
]
```

## Example Bad-to-Good Transformation

Bad kernel:

```text
1. 当社では AI 活用が重要になっている。
2. しかし、まだ十分に活用できていない。
3. 今後は AI 活用をさらに推進すべきである。
4. そのために業務効率化の施策を検討したい。
```

Diagnosis:

```text
- premise is too generic
- complication does not explain the failure mechanism
- claim is generic and not controversial
- action is not decidable
```

Improved kernel:

```text
1. 当社の AI 投資は、個人向けツール配布を中心に進んでいる。
2. しかし、業務プロセスに組み込まれない限り、利用率は上がっても成果には接続しない。
3. 次の投資は、ツール利用拡大ではなく、業務単位の Agent 実装へ切り替えるべきである。
4. 次四半期は3業務に絞り、PoC ではなく本番導入前提の Agent 開発に予算を振り替える。
```

## Acceptance Criteria

- Agent can generate a valid 4-Line Message Kernel from selected claim.
- Agent returns diagnosis with strengths and issues.
- UI displays all four lines clearly.
- UI displays diagnosis issues by severity.
- User can provide additional feedback.
- Feedback creates a new kernel revision.
- Revision history is stored.
- Deck generation is blocked until a kernel exists.

## Test Plan

Unit tests:

- Validate kernel has four non-empty lines.
- Validate diagnosis schema.
- Validate revision history.

Manual tests:

1. Submit sample Free Talk.
2. Select a claim.
3. Generate kernel.
4. Confirm diagnosis contains at least one useful issue.
5. Add feedback.
6. Confirm revision 2 is created.
7. Confirm UI shows current kernel and revision history.

## Non-Goals

Do not implement evidence search in this issue. Evidence grounding is handled separately.
