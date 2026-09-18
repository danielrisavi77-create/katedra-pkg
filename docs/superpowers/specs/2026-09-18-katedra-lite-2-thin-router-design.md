# Katedra Lite 2.0 — Thin Router Design

## Goal

Make `katedra-lite` a small orchestration layer that keeps Katedra's strongest guarantees while loading operational detail only when needed.

## Non-goals

- Do not rewrite `rad-audit`, `rad-docx`, `replikacija-pspp`, faculty profiles, or evidence machinery.
- Do not weaken fail-closed gates, provenance, snapshots, rewrite verification, or manual final reading.
- Do not add deterministic substring routing that competes with host semantic skill activation.

## Architecture

### 1. Thin router

`katedra-lite/SKILL.md` keeps only:
- product identity and version contract;
- resume/direct-mode guard;
- seven modes;
- quick-vs-full execution decision;
- a short set of universal invariants;
- references to mode/runtime/policy documents.

Operational Claude/Cowork/GitHub bootstrap material moves to `references/runtime.md`.

### 2. Two execution paths

**Quick path** is for bounded transformations where the user supplied the text/material and is not asking for a thesis-wide workflow. It avoids full project state and gates unless the task requires document mutation, external factual verification, or a large-work plan dependency.

**Full path** remains the default for new final/thesis work, thesis-wide writing, audit, defence, submission, return-from-Word, or any task with faculty rules, claims/evidence, derived numbers, or document mutation.

Quick path must never bypass source integrity, privacy, or mutation safety.

### 3. Rule taxonomy

Replace the idea that every operational heuristic is equally “iron” with three classes:

- **HARD** — integrity/safety invariant; cannot be waived by convenience.
- **GATE** — workflow prerequisite; may be explicitly exempted only with a recorded reason when the relevant input is unavailable or not applicable.
- **SIGNAL** — advisory heuristic; triggers review, never by itself proves a defect.

Existing gates and scripts keep their semantics; the taxonomy clarifies how the agent talks about them.

### 4. Privacy

Katedra no longer instructs agents to commit all of `.katedra/` automatically. Project state is durable, but sensitive artefacts may stay local. `references/privatnost.md` defines a minimum-safe policy and recommended ignore patterns.

### 5. Track Changes

Do not silently treat “accept all” as the user's canonical document. For a document with tracked changes:
- preserve the original;
- create an accepted-copy for machine extraction when needed;
- state which view was analysed;
- when authorship intent matters, distinguish current/final/original views and ask only if the requested conclusion would materially depend on that choice.

### 6. Authority hierarchy

For formatting and local practice, use:
1. explicit written mentor instruction for this project;
2. official faculty/institution rules;
3. confirmed resolved profile;
4. measured defended examples;
5. heuristics/signals.

A defended example is evidence of practice, never a formal rule by itself.

### 7. Version model

Use exactly two concepts in the router:
- `package_version` = repository/card version from `VERSION`;
- `core_contract` = frozen certified release contract, currently `1.0.1`.

No third version label should be presented as the active package version.

## Success criteria

- `SKILL.md` is materially smaller and does not embed Claude/GitHub bootstrap implementation.
- Quick path exists and explicitly preserves HARD invariants.
- Runtime, priority taxonomy, privacy, and revision-view policy are separate references.
- Existing mode references and capability boundaries remain reachable.
- Version tag in frontmatter matches `VERSION`.
- A machine-checkable router contract guards the new architecture.
