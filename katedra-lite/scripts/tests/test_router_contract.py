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


def check(name: str, condition: bool, detail="") -> bool:
    print(f"  {'✓' if condition else '✗ FAIL':8} {name}")
    if not condition and detail:
        print(f"           detalj: {detail}")
    return condition


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
