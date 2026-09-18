#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Katedra Lite 2.0 thin-router architecture.

This is a structural release guard, not a semantic trigger benchmark. Semantic
activation remains measured by evals/pokreni_trigger.py against a live Claude CLI.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_REFS = (
    "runtime.md",
    "quick_path.md",
    "prioriteti.md",
    "privatnost.md",
    "revizije.md",
)
FORBIDDEN_ROUTER_FRAGMENTS = (
    "KATEDRA_PKG_URL_TOKEN",
    "/root/.claude/",
    "access denied by the git proxy",
    "https://<token>@",
)
MAX_ROUTER_CHARS = 24000
DESCRIPTION_VERSION_RE = re.compile(r"\sv(\d+\.\d+\.\d+)\.\"?\s*$", re.M)


def validate(root: Path) -> list[str]:
    findings: list[str] = []
    version_path = root / "VERSION"
    router_path = root / "katedra-lite" / "SKILL.md"
    refs_dir = root / "katedra-lite" / "references"

    if not version_path.is_file():
        return ["VERSION nedostaje"]
    if not router_path.is_file():
        return ["katedra-lite/SKILL.md nedostaje"]

    version = version_path.read_text(encoding="utf-8").strip()
    router = router_path.read_text(encoding="utf-8")

    m = DESCRIPTION_VERSION_RE.search(router)
    if not m:
        findings.append("SKILL.md description nema završnu package VERSION oznaku")
    elif m.group(1) != version:
        findings.append(f"SKILL.md description nosi v{m.group(1)}, VERSION je {version}")

    if len(router) > MAX_ROUTER_CHARS:
        findings.append(
            f"router je {len(router)} znakova; limit thin-router contracta je {MAX_ROUTER_CHARS}"
        )

    for token in FORBIDDEN_ROUTER_FRAGMENTS:
        if token in router:
            findings.append(f"runtime/bootstrap detalj ostao je u routeru: {token!r}")

    required_markers = (
        "package_version: VERSION",
        "core_contract: 1.0.1",
        "Quick path",
        "Full path",
        "HARD",
        "GATE",
        "SIGNAL",
    )
    for marker in required_markers:
        if marker not in router:
            findings.append(f"router nema obavezni marker: {marker}")

    for ref in REQUIRED_REFS:
        p = refs_dir / ref
        if not p.is_file():
            findings.append(f"nedostaje references/{ref}")
        if f"references/{ref}" not in router:
            findings.append(f"router ne upućuje na references/{ref}")

    forbidden_claims = (
        "Sve u `.katedra/` ide u git",
        "Uzorak mentora jači je od profila",
    )
    for claim in forbidden_claims:
        if claim in router:
            findings.append(f"zastarjela globalna tvrdnja ostala je u routeru: {claim}")

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args()

    findings = validate(args.root.resolve())
    print("=" * 66)
    print("KATEDRA-LITE THIN ROUTER CONTRACT")
    print("=" * 66)
    if findings:
        for finding in findings:
            print(f"❌ {finding}")
        print(f"\nREZULTAT: FAIL ({len(findings)} nalaza)")
        return 1
    print("✅ verzija, veličina, reference i granice routera su usklađene")
    print("\nREZULTAT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
