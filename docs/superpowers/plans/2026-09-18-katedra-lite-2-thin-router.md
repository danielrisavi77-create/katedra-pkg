# Katedra Lite 2.0 Thin Router Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `katedra-lite` into a thin, two-speed orchestration layer without weakening existing academic integrity and release gates.

**Architecture:** Keep existing engines and mode references intact. Move runtime/development detail out of the router, add policy references for quick path, priorities, privacy, and revision views, then enforce the new router shape with a small contract validator and regression test.

**Tech Stack:** Markdown skill/router files, Python 3 contract checks, existing GitHub/Claude skill package.

**Spec:** `docs/superpowers/specs/2026-09-18-katedra-lite-2-thin-router-design.md`

## Global Constraints

- Do not reimplement or fork rad-audit, rad-docx, replikacija-pspp, or faculty profiles.
- Preserve fail-closed semantics: skipped/broken blocking checks are not passes.
- Quick path cannot bypass source integrity, privacy, or document mutation safety.
- Avoid deterministic substring routing as a replacement for host semantic activation.
- Keep core contract `1.0.1` distinct from package version.

---

### Task 1: Add a router architecture contract

**Files:**
- Create: `katedra-lite/scripts/router_contract.py`
- Create: `katedra-lite/scripts/tests/test_router_contract.py`
- Modify: `bin/testovi.sh`

**Interfaces:**
- Consumes: repository root, `VERSION`, `katedra-lite/SKILL.md`, required reference paths.
- Produces: exit 0 when the thin-router contract holds; exit 1 with named findings otherwise.

- [ ] Write a failing test that requires the contract tool, version equality, required references, a router size ceiling, and absence of embedded Claude/GitHub credential/bootstrap details.
- [ ] Run the new test and confirm RED because the tool/reference architecture does not yet exist.
- [ ] Implement the smallest contract validator.
- [ ] Add it to `bin/testovi.sh`.
- [ ] Re-run the focused test.

### Task 2: Add modular policy references

**Files:**
- Create: `katedra-lite/references/runtime.md`
- Create: `katedra-lite/references/quick_path.md`
- Create: `katedra-lite/references/prioriteti.md`
- Create: `katedra-lite/references/privatnost.md`
- Create: `katedra-lite/references/revizije.md`
- Modify: `katedra-lite/references/mapa.md`

**Interfaces:**
- Consumes: current router bootstrap, current Track Changes policy, existing gate semantics.
- Produces: focused references that can be loaded only when relevant.

- [ ] Move runtime/bootstrap guidance into `runtime.md`.
- [ ] Define quick/full decision and non-bypassable invariants in `quick_path.md`.
- [ ] Define HARD/GATE/SIGNAL semantics in `prioriteti.md`.
- [ ] Define local-first sensitive-state policy and ignore guidance in `privatnost.md`.
- [ ] Define original/accepted/current revision-view handling in `revizije.md`.
- [ ] Register all five in `mapa.md`.

### Task 3: Replace the monolithic router

**Files:**
- Modify: `katedra-lite/SKILL.md`
- Modify: `VERSION`

**Interfaces:**
- Consumes: the five new references and existing mode references.
- Produces: a compact router with seven modes, quick/full path, core invariants, and version/core-contract labels.

- [ ] Set package version to `2.0.0` and frontmatter tag to `v2.0.0`.
- [ ] Keep direct/resume routing and seven modes.
- [ ] Replace the long bootstrap with a pointer to `runtime.md`.
- [ ] Replace 35 flat “iron rules” with a compact universal set plus pointer to `prioriteti.md`.
- [ ] Add quick-path decision before full intake.
- [ ] Replace “all .katedra goes to git” with privacy-aware persistence guidance.
- [ ] Replace “mentor sample beats profile” with the explicit authority hierarchy.
- [ ] Replace automatic Track Changes acceptance language with view-aware extraction guidance.

### Task 4: Verify behavior and release integrity

**Files:**
- Modify only if tests identify regressions.

**Interfaces:**
- Consumes: complete branch.
- Produces: fresh focused and package-level verification evidence.

- [ ] Run `test_router_contract.py`.
- [ ] Run `katedra/scripts/verzija.py --provjeri`.
- [ ] Run `katedra-lite/scripts/tests/test_trigger.py` if a logged-in Claude CLI is available; otherwise record the environment limitation.
- [ ] Run `bin/testovi.sh` and report every failing group rather than hiding environment-dependent skips.
- [ ] Review the final diff against this spec before opening a PR.
