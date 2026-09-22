#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Svaki SKILL.md u paketu je router i ostaje ispod granice veličine.

Zašto postoji: router_contract.py čuva samo katedra-lite. U v2.1.0 je
rad-orchestrator/SKILL.md imao 46 321 znak (36 KB je bio „Dodatak A" s cijelim
JS-om, i to starijim od skripte u paketu), a rad-audit/SKILL.md 31 954. Svaka
sesija koja je aktivirala te skillove učitavala je taj tekst u kontekst.
Granica je ista kao u thin-router contractu katedra-litea.

Izlazni kod: 0 = svi routeri su unutar granice, 1 = barem jedan nije,
2 = nema nijednog SKILL.md-a (ne može se izmjeriti; nije prolaz).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

GRANICA = 24000
SKILLOVI = (
    "katedra",
    "katedra-lite",
    "rad-audit",
    "rad-docx",
    "fpzg-diplomski",
    "replikacija-pspp",
    "rad-orchestrator",
)


def izmjeri(korijen: Path, granica: int = GRANICA) -> tuple[list[tuple[str, int]], list[str]]:
    mjere: list[tuple[str, int]] = []
    nalazi: list[str] = []
    for slug in SKILLOVI:
        p = korijen / slug / "SKILL.md"
        if not p.is_file():
            continue
        n = len(p.read_text(encoding="utf-8"))
        mjere.append((slug, n))
        if n > granica:
            nalazi.append(f"{slug}/SKILL.md ima {n} znakova; granica routera je {granica}")
    return mjere, nalazi


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("korijen", nargs="?", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--granica", type=int, default=GRANICA)
    a = ap.parse_args(argv)
    mjere, nalazi = izmjeri(Path(a.korijen), a.granica)
    if not mjere:
        print("⛔ nijedan SKILL.md nije nađen; veličina routera nije izmjerena")
        return 2
    for slug, n in sorted(mjere, key=lambda x: -x[1]):
        oznaka = "❌" if n > a.granica else "✓"
        print(f"  {oznaka} {slug:<18} {n:>6} znakova")
    if nalazi:
        print("")
        for f in nalazi:
            print(f"❌ {f}")
        return 1
    print(f"\n✅ svi routeri ≤ {a.granica} znakova")
    return 0


if __name__ == "__main__":
    sys.exit(main())
