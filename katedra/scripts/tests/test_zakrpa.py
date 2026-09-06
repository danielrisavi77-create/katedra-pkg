#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testovi za katedra/scripts/zakrpa.py — provjera tvrdnji.

Kvar 117: provjera je gledala samo jedan smjer („SKILL.md zove skriptu koje
nema"). Zrcalni smjer — alat koji postoji, a dokumentacija ga nikad ne spominje
— nije gledao nitko, pa je rad-audit nosio devet nedokumentiranih provjera.
Ovdje stoji ograda da oba smjera i dalje mogu pasti; provjera koja ne može
pasti nije provjera (pravilo 34).
"""
import importlib.util
import os
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TU)

_spec = importlib.util.spec_from_file_location("zakrpa", os.path.join(SCRIPTS, "zakrpa.py"))
zakrpa = importlib.util.module_from_spec(_spec)
sys.path.insert(0, SCRIPTS)
_spec.loader.exec_module(zakrpa)

PALO = []


def check(naziv, uvjet, detalj=""):
    print("  %-8s %s" % ("✓" if uvjet else "✗ FAIL", naziv))
    if not uvjet:
        PALO.append(naziv)
        if detalj:
            print("           detalj: %r" % (detalj,))


def skill(skripte, md="# Skill\n", reference=None, katalog=None):
    """Napravi minimalan korijen skilla i vrati mu put."""
    korijen = os.path.join(tempfile.mkdtemp(), "proba-skill")
    os.makedirs(os.path.join(korijen, "scripts"))
    with open(os.path.join(korijen, "SKILL.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    for ime in skripte:
        with open(os.path.join(korijen, "scripts", ime), "w", encoding="utf-8", newline="\n") as f:
            f.write("# proba\n")
    if reference or katalog is not None:
        os.makedirs(os.path.join(korijen, "references"))
        for ime, tekst in (reference or {}).items():
            with open(os.path.join(korijen, "references", ime), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(tekst)
    if katalog is not None:
        tijelo = "".join("\n## %d. unos %d\n\ntekst\n" % (i, i)
                         for i in range(1, katalog + 1))
        with open(os.path.join(korijen, "references", "zamke.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write("# Katalog\n" + tijelo)
    return korijen


def nedokumentirani(nalazi):
    return [n for n in nalazi if "ne spominje ga ni" in n]


def main():
    print("=" * 70)
    print("TESTOVI zakrpa.py — provjera tvrdnji")
    print("=" * 70)

    # R44: alat koji postoji, a nitko ga ne spominje — zrcalni smjer
    n = zakrpa.provjeri_tvrdnje(skill(["check_hipoteze.py"]))
    check("R44: nedokumentiran alat je nalaz", len(nedokumentirani(n)) == 1, n)

    # R45: isti alat spomenut u SKILL.md-u više nije nalaz
    n = zakrpa.provjeri_tvrdnje(
        skill(["check_hipoteze.py"], md="# Skill\n\n`python3 check_hipoteze.py rad.docx`\n"))
    check("R45: spominjanje u SKILL.md gasi nalaz", nedokumentirani(n) == [], n)

    # R45b: i referenca vrijedi kao dokumentacija
    n = zakrpa.provjeri_tvrdnje(
        skill(["check_hipoteze.py"], reference={"audit.md": "zove se check_hipoteze.py\n"}))
    check("R45: spominjanje u references/ gasi nalaz", nedokumentirani(n) == [], n)

    # R46: pomoćne datoteke nisu alati
    n = zakrpa.provjeri_tvrdnje(skill(["__init__.py", "common.py", "_pomocno.py"]))
    check("R46: __init__, common i _* se ne traže u dokumentaciji",
          nedokumentirani(n) == [], n)

    # R47: prvi smjer nije izgubljen — SKILL.md koji zove skriptu koje nema
    n = zakrpa.provjeri_tvrdnje(skill([], md="# Skill\n\n`python3 nema_me.py rad.docx`\n"))
    check("R47: prvi smjer i dalje pada", any("nema ni u paketu" in x for x in n), n)

    # R48: oba smjera se prijavljuju istovremeno, ne jedan umjesto drugoga
    n = zakrpa.provjeri_tvrdnje(
        skill(["check_hipoteze.py"], md="# Skill\n\n`python3 nema_me.py rad.docx`\n"))
    check("R48: oba smjera zajedno",
          len(nedokumentirani(n)) == 1 and any("nema ni u paketu" in x for x in n), n)

    # R49: brojka o veličini kataloga mora se slagati s katalogom
    md_kriv = "# Skill\n\n| `references/zamke.md` | 31 stvarni kvar |\n"
    n = zakrpa.provjeri_tvrdnje(skill([], md=md_kriv, katalog=26))
    check("R49: kriva brojka o katalogu je nalaz",
          any("katalog nosi 26 unosa" in x for x in n), n)

    md_tocan = "# Skill\n\n| `references/zamke.md` | 26 stvarnih kvarova |\n"
    n = zakrpa.provjeri_tvrdnje(skill([], md=md_tocan, katalog=26))
    check("R49: točna brojka nije nalaz", not any("katalog nosi" in x for x in n), n)

    # R49b: katalozi citiraju tuđe brojke — citat u references/ nije tvrdnja
    n = zakrpa.provjeri_tvrdnje(
        skill([], md="# Skill\n", katalog=26,
              reference={"drugo.md": "dokaz: `31 stvarni kvar` u tuđem zamke.md\n"}))
    check("R49: citat u referenci se ne broji kao tvrdnja",
          not any("katalog nosi" in x for x in n), n)

    print("=" * 70)
    print("REZULTATI TESTOVA: %d/%d prošlo" % (9 - len(PALO), 9))
    print("=" * 70)
    return 1 if PALO else 0


if __name__ == "__main__":
    sys.exit(main())
