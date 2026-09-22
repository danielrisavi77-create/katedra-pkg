# Zakrpa audit guards — implementation plan

> Execute inline with test-driven changes and exact-head verification.

**Goal:** Integrate the useful 2026-09-20 patch on main 14c339ba without citation false negatives, implicit faculty selection, or false measured passes.

**Architecture:** Preserve the existing citation validator and all 26 package groups. Keep faculty selection explicit at the report/adapter boundary. HKS ordering reads the existing profile; missing evidence is unmeasured. Add standalone regression groups rather than copy the uploaded monolithic test file with unconditional assertions.

**Spec:** The user-approved audit of katedra-zakrpa-20260920.tar.gz (SHA256 c46fe6a3b1e41758119b18ba1e136e6fb6cc36986b1f8e4ae7ff88fcbfbe5a03).

## Constraints

- Do not change the 24 live routing cases, their 3 repetitions, or majority criterion.
- Keep existing K160 (year suffixes) and all existing tests.
- Do not promote the HKS profile to confirmed based only on uploaded assertions; the original PDF was not verified here.
- No API billing; live eval uses the configured CI OAuth secret.
- No merge; draft until the exact final revision has a fully measured passing live evaluation and full package suite.

## Steps

- [x] Record original patch red run; validate exact baseline source tree and run baseline suite.
- [x] Add `rad-audit/scripts/tests/test_zakrpa_release.py` using real report imports and synthetic temporary fixtures, including missing references, explicit faculty selection, missing structure, profile mutation and IEEE.
- [x] Add `katedra-lite/scripts/tests/test_hks_fzs.py`, preserving the valid uploaded checks with new catalog IDs K161/K162. Run both against pre-fix candidate and record failures.
- [x] Keep main `check_citations.py`; port structural statistics, plural references, hypothesis verdicts, threshold, category and quotation fixes with positive and negative controls.
- [x] Fix report phase H: no implicit fallback; unknown -> code 3, invalid explicit checker/failed execution -> code 2; preserve stdout/stderr and adapter JSON evidence.
- [x] Fix HKS order: read JSON `redoslijed`; missing rules/structure and manual review are `ok: null`; report measured and unmeasured counts separately.
- [x] Fix inventory bibliography parsing symmetrically for IEEE/Vancouver; reject unsupported styles and invalid batch sizes explicitly.
- [x] Add both regression scripts to `bin/testovi.sh` (26 existing + 2 new groups). Keep original `test_all.py` unchanged.
- [x] Bump package to 2.0.1 using `verzija.py --postavi`; append evidence-based catalog entries, preserve history, regenerate index/registry and engine fingerprint.
- [ ] Run `bash bin/testovi.sh`, regression scripts, compile/syntax checks, and `git diff --check`; review diff for accidental changes and secrets.
- [ ] Publish corrective draft PR, remove temporary source-export workflow from final tree, and inspect exact-head workflow/artifacts. Only mark ready when every gate is measured and passing.

## Review focus

Undefined single/group/range citations must still fail. Unknown or mistyped faculty/checker must never become HKS. Missing profile fields must not reuse hardcoded order. Unavailable external manuscripts must not count as passing tests. The adapter must preserve the phase-H code and explanation in JSON.
