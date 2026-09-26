# Delivery B — typed numeric review

`scripts/inference_context.py` owns the **new** `inference_context_schema.json` sidecar;
`scripts/numeric_semantics.py` evaluates the declared facts and arithmetic. It does not
parse a PDF/table into facts, resolve legal meaning, or certify a human's annotation.
Existing claim/evidence schemas remain unchanged. The minimal fixture under
`tests/fixtures/evidence_bcd/numeric_example.json` is synthetic and has illustrative
(non-matching) bindings: never treat it as a review of an actual manuscript.

## Workflow

1. Track the exact document with the existing artifact-manifest command; choose the
   view only after explicit revision handling. No automatic accept/reject.
2. Create a **new** empty sidecar:

```bash
python3 katedra-lite/scripts/inference_context.py init --project-root . \
  --rad rad.docx --kat .katedra --view original_no_revisions \
  --out .katedra/inference_context.json
```

This creates a template, not a PASS. Read evidence and annotate values, units, periods,
organisation/population/geography, actual/capacity/target/planned/estimate, flow role,
denominator, component memberships, review decision and locator. Retain original
claim/evidence IDs; derived facts identify their derivation. Do not fill unknown fields
with guesses. Strings representing numbers use decimal dots **after** explicit locale
parsing; `parse_local_number` accepts only declared `hr` or `en` conventions.

3. Run directly or from the phase gate:

```bash
python3 katedra-lite/scripts/numeric_semantics.py --context .katedra/inference_context.json \
  --project-root . --rad rad.docx --kat .katedra --view original_no_revisions \
  --out .katedra/numeric_semantics.json
python3 katedra-lite/scripts/gate.py audit --project-root . --rad rad.docx \
  --inference-context .katedra/inference_context.json --view original_no_revisions
```

## Meaning and boundaries

Identity does not equate capacity with actual, input with output, or different scopes.
Year-to-year changes must be explicit; unrelated values in different years are not
contradictions. Percentages require the same denominator; changes in percentage
points and relative percentage changes are separate operations. `yield_percent`
explicitly divides output by input for the same period/scope. Simple sums require
reviewed disjoint member sets; `union` requires an explicit intersection fact.
A complement gives only “not the source category”, not a new characteristic.

Only `exact` values enter exact arithmetic. Lower/upper bounds, intervals, approximate
and unknown values are represented, but remain `review_required` for these operations.
Nonzero tolerance requires a reason and named reviewer, is not automatically inferred,
and remains visible in the context. Decimal arithmetic has bounded input size.
Known compatible units are converted; unknown conversions require review.

`pass` (0) means the **declared numeric scope** passed; `blocked` (1) means a deterministic
contradiction; `review_required`, `unmeasured`, or `stale` (2) are not a release pass.
A changed document, ledger, or local source requires fresh annotations/bindings. Never
rebind automatically just to erase a stale warning. The report always says
`whole_document: false`: coverage is of the supplied sidecar, not every number in prose.
The caller's source-review annotation is not an independent assessment of the source.
