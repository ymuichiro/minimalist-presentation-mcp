# Issue 11: Add Evaluation, Warnings, and Safety Guardrails

## Summary

Add evaluation and guardrails so the application does not produce unsupported, overconfident, or generic business messages.

## Background

The application produces persuasive communication artifacts. This creates a risk of generating polished but unsupported claims. The system must explicitly surface uncertainty, evidence gaps, and objections.

## Evaluation Targets

Evaluate the following artifacts:

- Claim candidates
- 4-Line Message Kernel
- Evidence grounding
- Deck payload
- Brief

## Message Kernel Evaluation

Implement a scoring rubric.

### Criteria

```text
1. Specificity
2. Tension / Complication strength
3. Claim sharpness
4. Requested action clarity
5. Non-redundancy
6. Evidence supportability
7. Objection awareness
8. Audience fit
```

Each criterion should be scored from 1 to 5.

Example:

```json
{
  "specificity": 4,
  "complication_strength": 5,
  "claim_sharpness": 4,
  "action_clarity": 5,
  "non_redundancy": 4,
  "evidence_supportability": 3,
  "objection_awareness": 4,
  "audience_fit": 4
}
```

The UI may show only the overall score and key issues.

## Warning Types

Use these warning codes.

```text
GENERIC_CLAIM
WEAK_COMPLICATION
VAGUE_ACTION
EVIDENCE_MISSING
UNSUPPORTED_NUMERIC_CLAIM
OBJECTION_NOT_HANDLED
AUDIENCE_UNCLEAR
DECK_GENERATED_WITHOUT_EVIDENCE
```

## Unsupported Numeric Claims

If the Agent generates any numeric claim, it must either:

- cite a supporting source
- mark it as an assumption
- remove it

Bad:

```text
Agent 化により30%効率化できます。
```

Good:

```text
現時点では効率化率を示す社内データは未確認です。対象業務の処理時間データが必要です。
```

## Deck Generation Guardrails

Before deck generation, check:

- Message Kernel exists
- action line is not vague
- evidence grounding has run or user explicitly skipped it
- no unsupported numeric claims exist in final payload
- E1/E2 do not pretend missing evidence exists

## Brief Guardrails

The brief must include a section for:

```text
Evidence Gaps
Likely Objections
```

If no evidence exists, it must explicitly say:

```text
現時点で、この主張を直接支える社内データは確認できていません。
```

## Trace Summary

Store concise trace summary in session.

```json
[
  {
    "step": "claim_extraction",
    "status": "success",
    "summary": "Generated 3 claim candidates."
  },
  {
    "step": "kernel_diagnosis",
    "status": "warning",
    "summary": "Action line was vague; revision suggested."
  }
]
```

## Acceptance Criteria

- Message Kernel diagnosis includes actionable warnings.
- Unsupported numeric claims are detected or avoided.
- Deck generation warns if evidence grounding is skipped.
- Brief contains evidence gaps and objections.
- Session stores trace summary.
- UI shows warning messages clearly.

## Test Plan

Unit tests:

- Vague action detection
- Generic claim detection
- Unsupported numeric claim detection
- Missing evidence warning
- Deck precondition check

Manual tests:

1. Enter generic Free Talk.
2. Confirm generic claim warning appears.
3. Try generating deck without evidence grounding.
4. Confirm warning appears.
5. Generate brief and confirm evidence gap section exists.

## Non-Goals

Do not create a complex automated evaluator dashboard. The goal is contest-ready transparency and safety.
