# Evidence & inference hardening — B, C and D implementation

Approved direction: issue #53 and `2026-09-22-evidence-inference-hardening-design.md`.
Base: `5871c46256391838e025bfa794d871d66a924a23`. Separate dependent deliveries, no merge.

## Invariants
- No manuscript, personal data, source screenshots, secrets or live API billing.
- No changes to frozen claim/evidence v1 contracts or faculty rules.
- Missing measurements, unknown semantics and pending human review never become PASS.
- Structured annotations are human/agent assertions; algebra checks do not certify a source's truth.
- Render evidence must match the last DOCX bytes; manual visual signoff is not automatic.

## B — numeric semantics
1. Add a strict, versioned sidecar bound to document, ledgers and source bytes.
2. Test exact decimal/localized parsing, actual/capacity, input/output, scope/period/denominator,
   disjoint component aggregation, bounded values, tolerance, percent/percentage-points.
3. Add numeric evaluator and CLI; record inspected coverage and deterministic findings separately
   from insufficient evidence. Add opt-in phase-gate step without changing legacy behavior.

## C — inference scope
1. Add validated claim links with actual text fingerprints; reject cycles and dangling IDs.
2. Propagate invalidated premises transitively, except explicitly re-reviewed independent support.
3. Check declared inclusion criteria, complements/absence, generalisation and certificate scope.
4. Flag epistemic strengthening in rewrite comparisons as review-required, not proven falsehood.
5. Integrate with sidecar/phase gate; keep schemas, reports and examples executable.

## D — DOCX delivery integrity
1. Reuse rad-docx package loader and no-overwrite snapshot publication; do not duplicate engines.
2. Compare ordered visible content, fields, relationships, visual identities/data and alt descriptions.
3. Check section-aware widths and fixed-height clipping risks; never infer render success from XML.
4. Clean only explicitly named metadata groups; do not accept revisions or delete comments implicitly.
5. Validate render manifest with document/PDF/page hashes and explicit visual review over all pages.
6. Add final composite gate, retaining excluded administrative items and explicit unmeasured states.

## Verification and delivery
Each implementation follows observed RED then GREEN with legitimate controls. Run whole suite after
B/C/D, code syntax, change invariants, source-tree equality; publish B/C/D as separate stacked drafts.
Record Linux, Windows, live and visual evidence separately. No unmeasured live/visual claim.
