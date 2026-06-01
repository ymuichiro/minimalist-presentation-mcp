# 4-Line Message Kernel

The 4-Line Message Kernel is the intermediate representation before deck generation.

```text
1. Audience Premise
2. Complication / Gap
3. Core Claim
4. Requested Decision / Action
```

## Evaluation Rubric

The example app evaluates the kernel with these criteria:

1. Specificity
2. Tension / Complication strength
3. Claim sharpness
4. Requested action clarity
5. Non-redundancy
6. Evidence supportability
7. Objection awareness
8. Audience fit

Warnings include:

- `GENERIC_CLAIM`
- `WEAK_COMPLICATION`
- `VAGUE_ACTION`
- `EVIDENCE_MISSING`
- `UNSUPPORTED_NUMERIC_CLAIM`
- `OBJECTION_NOT_HANDLED`
- `AUDIENCE_UNCLEAR`
- `DECK_GENERATED_WITHOUT_EVIDENCE`

The deck should not be generated before a kernel exists. If evidence grounding is skipped, the application must show a warning rather than pretending the claim is fully supported.
