# Delivery C — claim dependencies and inference scope

`scripts/claim_inference.py` evaluates the optional `inference` block in the B sidecar.
The block is described by `references/claim_inference_schema.json` and included in the
sidecar schema; existing claim/evidence v1 ledgers remain unchanged. No claims are
rewritten and no graph edge is inferred from prose. Annotate exact ledger IDs and
SHA-256 of the UTF-8 claim text reviewed by the named reviewer.

Nodes distinguish confirmed, contradicted and unknown evidence **as recorded by the
reviewer**. A changed fingerprint, missing linked support, or unknown/contradicted
premise requires renewed review and transitively invalidates downstream conclusions.
It does not declare those conclusions false. A separate independent review can stop
propagation only with a current claim fingerprint, actual linked support, named
reviewer, and evidence not reused from the invalidated premise. Cycles and dangling IDs
are invalid inputs. Missing required nodes are unmeasured, never a green empty graph.

Generalisation compares explicitly annotated evidence/claim units, not just keywords.
Causal links require a recorded design review and linked evidence; that declaration
is not itself proof that causal identification is correct. Complement and absence
links reject “new property from complement” and “unknown therefore absent”.
Inclusion criteria remain fixed; cases with missing or contradicted requirements are
flagged. Pilot exclusion must have a reason and never silently edits the method.
Certificate/regulation/report scope includes subject, holder, units, features, validity
and source locator. Coverage beyond those annotations needs review; no legal inference
or certification is performed automatically.

```bash
python3 katedra-lite/scripts/claim_inference.py --context .katedra/inference_context.json \
  --project-root . --rad rad.docx --kat .katedra --view original_no_revisions \
  --out .katedra/claim_inference.json
python3 katedra-lite/scripts/gate.py audit --project-root . --rad rad.docx \
  --claim-inference-context .katedra/inference_context.json --view original_no_revisions
```

When numeric annotations are present, C imports their B findings and invalidates the
claims affected by those findings. Source/ledger/document hashes must still match;
a fresh filename alone cannot erase stale evidence. Qualitative graphs do not require
inventing numeric facts. `whole_document` remains false.

## Rewriting

`verify_rewrite.py --epistemic-review` adds candidate review for strengthening or scope
expansion, preserving existing numeric/citation/mutation checks. `may be associated`
→ `causes` and `in the sample` → `all in the country` are review candidates. Quoted,
negated strong words and preserved uncertainty have negative controls.

```bash
python3 katedra-lite/scripts/verify_rewrite.py before.md after.md --zahvat stil --epistemic-review
```

The opt-in candidate result returns 2 (review required), not 0 and not a verdict that
a claim is false. No generic keyword scan can certify causal or legal meaning. For
an intentional content change, renew the evidence and claim review rather than treating
it as a cosmetic rewrite. Test fixtures are synthetic, not facts about real subjects.
