#!/usr/bin/env python3
"""Regresijski testovi za gate.py — kvar 58.

Kvar 58 (5.9.2026.): blokirajući korak kojemu fali ulaz izlazio je kao
`preskočeno`, a `zakljucak()` je blokirao samo NALAZ i PUKAO. Gate je ispisivao
„✅ nijedna blokirajuća provjera nije pala" uz izlazni kod 0, dok se sedam
blokirajućih provjera nikad nije pokrenulo. Dovoljno je bilo da se rad zove
drukčije od `rad.docx`.

Ovi testovi postoje da se to ne vrati. Uporaba:  python3 tests/test_gate.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import gate  # noqa: E402

REZULTATI = []


def check(naziv, uvjet, detalj=None):
    REZULTATI.append((naziv, bool(uvjet), detalj))


def r(korak, stanje, blokira=True):
    return {"korak": korak, "naziv": korak, "stanje": stanje, "blokira": blokira}


def main() -> int:
    # ── zakljucak() ───────────────────────────────────────────────────────
    kod, s = gate.zakljucak([r("pravila", gate.PRESKOCENO)])
    check("G1: preskočen BLOKIRAJUĆI korak daje izlazni kod 1", kod == 1, (kod, s))
    check("G1: i imenuje se pod 'nepokrenuto'", s["nepokrenuto"] == ["pravila"], s)

    kod, _ = gate.zakljucak([r("stil", gate.PRESKOCENO, blokira=False)])
    check("G2: preskočen SAVJETODAVNI korak ne blokira", kod == 0, kod)

    kod, s = gate.zakljucak([r("pravila", gate.PRESKOCENO)],
                            {"pravila": "rad je tuđi, profil fakulteta nije dostupan"})
    check("G3: izuzet preskok ne blokira", kod == 0, (kod, s))
    check("G3: razlog izuzeća ostaje u izvještaju",
          s["preskok_dopusten"]["pravila"].startswith("rad je tuđi"), s)

    kod, _ = gate.zakljucak([r("pravila", gate.OK), r("jezik", gate.NALAZ)])
    check("G4: nalaz i dalje blokira", kod == 1, kod)

    kod, _ = gate.zakljucak([r("pravila", gate.OK), r("jezik", gate.OK)])
    check("G5: sve prošlo daje 0", kod == 0, kod)

    kod, s = gate.zakljucak([r("a", gate.NALAZ), r("b", gate.PRESKOCENO)])
    check("G6: nalaz i nepokrenuto se broje odvojeno",
          s["blokira"] == ["a"] and s["nepokrenuto"] == ["b"], s)

    # ── faze: koje provjere uopće blokiraju ───────────────────────────────
    c = {"rad": "rad.docx", "pdf": None, "profil": "p.json", "tip": "diplomski",
         "kat": ".katedra"}
    audit = gate.koraci("audit", c)
    blok = {k.kid for k in audit if k.blokira}
    for korak in ("motor_audit", "jezik", "fusnote", "dosljednost", "literatura",
                  "revizije", "pravila"):
        check(f"G7: faza audit blokira na '{korak}'", korak in blok, sorted(blok))
    check("G7: faza audit ima više od jedne blokirajuće provjere",
          len(blok) >= 6, sorted(blok))

    predaja = gate.koraci("predaja", c)
    kidovi = {k.kid for k in predaja}
    check("G8: faza predaja zove provjeri_predaju.py (rad-docx)",
          "predaja_docx" in kidovi, sorted(kidovi))
    check("G8: faza predaja provjerava praćene izmjene",
          "revizije" in kidovi, sorted(kidovi))

    # check_rules dobiva --strogo u obje faze
    for faza in ("audit", "predaja"):
        k = next(x for x in gate.koraci(faza, c) if x.kid == "pravila")
        check(f"G9: check_rules u fazi {faza} dobiva --strogo",
              "--strogo" in k.argv, k.argv)

    # ── end-to-end: prazan projekt ────────────────────────────────────────
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, ".katedra"), exist_ok=True)
        p = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "gate.py"), "--faza", "audit",
             "--kat", os.path.join(d, ".katedra"), "--project-root", d],
            capture_output=True, text=True)
        check("G10: prazan projekt NE prolazi fazu audit", p.returncode == 1,
              p.returncode)
        check("G10: ispis imenuje što se nije pokrenulo",
              "NIJE POKRENUTO" in p.stdout, p.stdout[-300:])
        check("G10: ispis NE tvrdi da je sve prošlo",
              "nijedna blokirajuća provjera nije pala" not in p.stdout,
              p.stdout[-300:])

        # nepoznat korak u --dopusti-preskok je greška, ne tiho ignoriranje
        p = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "gate.py"), "--faza", "audit",
             "--kat", os.path.join(d, ".katedra"), "--project-root", d,
             "--dopusti-preskok", "nepostojeci=razlog"],
            capture_output=True, text=True)
        check("G11: --dopusti-preskok s nepoznatim korakom vraća 2",
              p.returncode == 2, (p.returncode, p.stderr[-200:]))

        p = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "gate.py"), "--faza", "audit",
             "--kat", os.path.join(d, ".katedra"), "--project-root", d,
             "--dopusti-preskok", "bez-razloga"],
            capture_output=True, text=True)
        check("G12: --dopusti-preskok bez razloga vraća 2", p.returncode == 2,
              p.returncode)

    proslo = sum(1 for _, ok, _ in REZULTATI if ok)
    print("=" * 66)
    print(f"GATE TESTOVI: {proslo}/{len(REZULTATI)} prošlo")
    print("=" * 66)
    for naziv, ok, detalj in REZULTATI:
        print(f"  {'✓' if ok else '✗ FAIL':8} {naziv}")
        if not ok and detalj is not None:
            print(f"           detalj: {detalj}")
    return 0 if proslo == len(REZULTATI) else 1


if __name__ == "__main__":
    sys.exit(main())
