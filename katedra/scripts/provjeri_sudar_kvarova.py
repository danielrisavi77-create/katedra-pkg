#!/usr/bin/env python3
"""Sudar brojeva kvarova između grane i baze (obično origin/main).

Kvar 178: paralelne sesije uzimaju „sljedeći slobodan broj” iz svoje kopije kataloga, pa dva
PR-a dodaju isti broj s različitim sadržajem. `kvar.py --provjeri` to ne vidi — unutar jedne
datoteke numeracija je ispravna — a sudar se otkrivao tek ručno, pri spajanju (22. 9. 2026.:
tri puta u jednom danu). Ova provjera uspoređuje naslove unosa grane s naslovima u bazi:
isti broj, drugi naslov = sudar.

Uporaba:
  python3 katedra/scripts/provjeri_sudar_kvarova.py --baza origin/main
  python3 katedra/scripts/provjeri_sudar_kvarova.py --baza origin/main --grana origin/moja-grana
Bez --grana uspoređuje radno stablo.
Izlaz: 0 bez sudara · 1 sudar (svaki imenovan, uz prvi slobodan broj) · 2 baza nije dostupna.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

KATALOZI = ("katedra-lite/references/zamke.md", "rad-audit/references/zamke.md",
            "rad-docx/references/zamke.md")
NASLOV = re.compile(r"^## (\d+)(?:\s*[–-]\s*(\d+))?\.\s+(.+?)\s*$", re.M)


def unosi(tekst: str) -> dict[int, str]:
    """{broj: naslov}; raspon „98–104.” pokriva svaki broj u sebi istim naslovom."""
    out: dict[int, str] = {}
    for m in NASLOV.finditer((tekst or "").replace("\r\n", "\n")):
        od, do, naslov = int(m.group(1)), int(m.group(2) or m.group(1)), m.group(3)
        for n in range(od, do + 1):
            out[n] = naslov
    return out


def sudari(baza: str, kandidat: str) -> list[tuple[int, str, str]]:
    """[(broj, naslov u bazi, naslov u grani)] za svaki broj koji postoji u obje s drugim naslovom."""
    b, k = unosi(baza), unosi(kandidat)
    return [(n, b[n], k[n]) for n in sorted(k) if n in b and b[n] != k[n]]


def _git_show(korijen: str, ref: str, put: str) -> str | None:
    r = subprocess.run(["git", "-C", korijen, "show", f"{ref}:{put}"], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--baza", required=True, help="git ref s kojim se uspoređuje (npr. origin/main)")
    ap.add_argument("--grana", help="git ref grane; bez njega radno stablo")
    ap.add_argument("--korijen", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    a = ap.parse_args(argv)
    if subprocess.run(["git", "-C", a.korijen, "rev-parse", "--verify", "-q", a.baza + "^{commit}"],
                      capture_output=True).returncode != 0:
        print(f"❌ baza {a.baza} nije dostupna — sudar NIJE izmjeren (git fetch origin main?)")
        return 2
    ukupno = 0
    for put in KATALOZI:
        baza = _git_show(a.korijen, a.baza, put)
        if a.grana:
            kand = _git_show(a.korijen, a.grana, put)
        else:
            p = os.path.join(a.korijen, put)
            kand = open(p, encoding="utf-8").read() if os.path.exists(p) else None
        if baza is None or kand is None:
            continue
        s = sudari(baza, kand)
        if s:
            slobodan = max(set(unosi(baza)) | set(unosi(kand))) + 1
            print(f"❌ {put}: {len(s)} broj(eva) već postoji u {a.baza} s drugim sadržajem "
                  f"— prenumeriraj od {slobodan}:")
            for n, nb, nk in s:
                print(f"   {n}. baza:  {nb[:90]}")
                print(f"   {' ' * len(str(n))}  grana: {nk[:90]}")
            ukupno += len(s)
    if ukupno:
        return 1
    print(f"✅ nijedan broj kvara ne sudara se s {a.baza}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
