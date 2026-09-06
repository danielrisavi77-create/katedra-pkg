#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testovi za katedra/scripts/kvar.py — registar kvarova.

Skill `katedra` do sada nije imao nijedan test, a njegovi alati čuvaju registar
brojeva na koji se pozivaju svi ostali skillovi. Kvar 116 je nastao točno ondje:
naslov u tuđem obliku alat nije vidio, pa je „sljedeći slobodan" pokazivao na
broj koji je već potrošen.
"""
import importlib.util
import os
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TU)

_spec = importlib.util.spec_from_file_location("kvar", os.path.join(SCRIPTS, "kvar.py"))
kvar = importlib.util.module_from_spec(_spec)
sys.path.insert(0, SCRIPTS)
_spec.loader.exec_module(kvar)

PALO = []
SVE = []


def check(naziv, uvjet, detalj=""):
    # Kvar 125: broj u izvještaju mora se BROJATI, ne tvrditi. Ukovana
    # konstanta („%d/%d" % (6 - len(PALO), 6)) razmakne se čim se doda
    # provjera, i onda suite javlja 6/6 dok ih je pokrenuo sedam. Taj broj
    # čita `zakrpa.py --provjeri-tvrdnje`, pa laž putuje dalje.
    SVE.append(naziv)
    print("  %-8s %s" % ("✓" if uvjet else "✗ FAIL", naziv))
    if not uvjet:
        PALO.append(naziv)
        if detalj:
            print("           detalj: %r" % (detalj,))


def katalog(sadrzaj):
    p = os.path.join(tempfile.mkdtemp(), "zamke.md")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(sadrzaj)
    return p


TIJELO = "\nMjereno: 5 od 7.\n\n```\nizlaz koji kvar pokazuje\n```\n\n" + ("prozni opis mehanizma. " * 20) + "\n"
ZAGLAVLJE = "# Katalog\n\n"


def main():
    print("=" * 70)
    print("TESTOVI kvar.py")
    print("=" * 70)

    # R42: naslov u tuđem obliku je tvrdi nalaz, ne tišina
    p = katalog(ZAGLAVLJE + "## 1. prvi" + TIJELO + "\n## Kvar 2 — drugi" + TIJELO)
    tekst = open(p, encoding="utf-8").read()
    check("R42: tuđi oblik naslova se prepoznaje", len(kvar.tudji_naslovi(tekst)) == 1,
          kvar.tudji_naslovi(tekst))
    check("R42: takav katalog ne prolazi provjeru", kvar.provjeri(p) == 1)

    # R42b: raspon u tuđem obliku također
    p2 = katalog(ZAGLAVLJE + "## 1. prvi" + TIJELO + "\n## Kvarovi 2–4 — drugi" + TIJELO)
    check("R42: tuđi oblik s rasponom se prepoznaje",
          len(kvar.tudji_naslovi(open(p2, encoding="utf-8").read())) == 1)

    # R43: --popravi-naslove prevodi i time katalog postaje ispravan
    n = kvar.popravi_naslove(p2)
    tekst2 = open(p2, encoding="utf-8").read()
    check("R43: popravi_naslove prevodi raspon", n == 1 and "## 2–4. drugi" in tekst2,
          tekst2[:80])
    check("R43: poslije popravka katalog prolazi", kvar.provjeri(p2) == 0)
    check("R43: unos s rasponom pokriva sve brojeve",
          kvar.unosi(tekst2)[-1][1] == 4, kvar.unosi(tekst2)[-1][:2])

    # R43b: ispravan katalog se ne dira
    p3 = katalog(ZAGLAVLJE + "## 1. prvi" + TIJELO)
    prije = open(p3, encoding="utf-8").read()
    check("R43: ispravan katalog popravak ne mijenja",
          kvar.popravi_naslove(p3) == 0 and open(p3, encoding="utf-8").read() == prije)

    print("=" * 70)
    print("REZULTATI TESTOVA: %d/%d prošlo"
          % (len(SVE) - len(PALO), len(SVE)))
    print("=" * 70)
    return 1 if PALO else 0


if __name__ == "__main__":
    sys.exit(main())
