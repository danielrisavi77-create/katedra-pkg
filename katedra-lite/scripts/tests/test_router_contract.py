#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression contract for the Katedra Lite 2.0 thin router."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCRIPT = ROOT / "katedra-lite" / "scripts" / "router_contract.py"
SKILL = ROOT / "katedra-lite" / "SKILL.md"


def check(name: str, condition: bool, detail="") -> bool:
    print(f"  {'✓' if condition else '✗ FAIL':8} {name}")
    if not condition and detail:
        print(f"           detalj: {detail}")
    return condition


def _frontmatter_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"').lower()
    return ""


def main() -> int:
    ok = True

    ok &= check("R70: router_contract.py postoji", SCRIPT.exists(), SCRIPT)
    if not SCRIPT.exists():
        return 1

    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok &= check(
        "R70: stvarni repo zadovoljava thin-router contract",
        p.returncode == 0,
        (p.stdout + "\n" + p.stderr)[-1800:],
    )

    # R71: live Claude routing 2026-09-19 measured all 24 prompts. Citation
    # coverage and DOCX metadata only triggered 1/3 times, so the description
    # must state those as explicit REVIEW ACTIONS, not only as nearby nouns.
    # Mentor/version and contradiction intents stay pinned because they were the
    # other weak edges found by the first live pass. Unrelated negative controls
    # are intentionally not broadened.
    opis = _frontmatter_description(SKILL)
    sidra = {
        "provjera citata/literature": ("provjer", "citat", "literatur"),
        "mentorove povratne izmjene": ("mentor",),
        "provjera DOCX metapodataka": ("provjer", "docx", "metapod"),
        "unutarnja proturječja rada": ("proturječ",),
    }
    nedostaje = [
        naziv for naziv, tokeni in sidra.items()
        if not all(token in opis for token in tokeni)
    ]
    ok &= check(
        "R71: kartica eksplicitno pokriva live-routing akademske review namjere",
        not nedostaje,
        "nedostaju sidra: " + ", ".join(nedostaje) if nedostaje else "",
    )

    # Contract must detect a stale package tag independently of the real repo.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "katedra-lite" / "references").mkdir(parents=True)
        for ref in ("runtime.md", "quick_path.md", "prioriteti.md", "privatnost.md", "revizije.md"):
            (r / "katedra-lite" / "references" / ref).write_text("# x\n", encoding="utf-8")
        (r / "VERSION").write_text("2.0.0\n", encoding="utf-8")
        (r / "katedra-lite" / "SKILL.md").write_text(
            '---\nname: katedra-lite\ndescription: "router v1.9.41."\n---\n'
            '# KATEDRA-LITE\n'
            'package_version: VERSION · core_contract: 1.0.1\n'
            'quick path full path HARD GATE SIGNAL\n'
            'references/runtime.md references/quick_path.md references/prioriteti.md '
            'references/privatnost.md references/revizije.md\n',
            encoding="utf-8",
        )
        q = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(r)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        ok &= check(
            "R70: kriva frontmatter verzija pada",
            q.returncode == 1 and "VERSION" in q.stdout,
            q.stdout,
        )

    print("=" * 66)
    print("ROUTER CONTRACT:", "PASS" if ok else "FAIL")
    print("=" * 66)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
