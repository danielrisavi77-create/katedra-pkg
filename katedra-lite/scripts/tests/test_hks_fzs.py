#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ograde za kvarove 161 i 162 u `provjeri_hks_fzs.py`.

K161  uzorak uputnice na tablicu tražio se nad odlomcima spojenima znakom \n, pa
      je točka na KRAJU rečenice, iza koje slijedi odlomak s malim početnim
      slovom (bilješka ispod tablice), ispadala kršenje Uputa. Izmjereno na
      ispravljenoj verziji diplomskog rada: 2 lažna nalaza. Isti uzorak nije
      poznavao množinu („u Tablicama 7. i 8."), pa je STVARNO kršenje promašio.

K162  profil nosi propisani redoslijed dijelova rada u
      `struktura.opseg.diplomski.dijelovi.<ime>.redoslijed`, ali ga nitko nije
      čitao: provjeravalo se samo postojanje. Na tom radu Sadržaj i Popis
      kratica bili su zamijenjeni, a alat je javio „Sadržaj: nađen".

Testovi ne ovise o konkretnom radu: grade se minimalni .docx dokumenti.
"""
import importlib.util
import io
import os
import re
import sys
import contextlib
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TU)
sys.path.insert(0, SCRIPTS)

SVE, PALO = [], []


def check(ime, uvjet, detalj=""):
    SVE.append(ime)
    if not uvjet:
        PALO.append(ime)
    print(("  ✓      " if uvjet else "  ✗ PAD  ") + ime)
    if not uvjet and detalj:
        print("           detalj: %s" % (detalj,)[:300])


def _modul():
    put = os.path.join(SCRIPTS, "provjeri_hks_fzs.py")
    spec = importlib.util.spec_from_file_location("provjeri_hks_fzs", put)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _docx(odlomci, put):
    import docx
    d = docx.Document()
    for t in odlomci:
        d.add_paragraph(t)
    d.save(put)
    return put


def main():
    M = _modul()
    RE = M.RE_TAB_REF_TOCKA

    # ---------------- K161: lažni nalaz preko granice odlomka
    check("K161: točka na kraju rečenice nije kršenje (jedan odlomak)",
          RE.findall("Obilježja su prikazana u Tablici 1.") == [],
          RE.findall("Obilježja su prikazana u Tablici 1."))
    spojeno = "Obilježja su prikazana u Tablici 1.\nn – broj ispitanika; % – postotak"
    check("K161: spajanje odlomaka VIŠE ne stvara nalaz kad se traži po odlomku",
          all(RE.findall(o) == [] for o in spojeno.split("\n")),
          [RE.findall(o) for o in spojeno.split("\n")])
    # ---------------- K161: stvarna kršenja se i dalje vide
    check("K161: „u Tablici 2. pokazuju\" JEST kršenje",
          RE.findall("Rezultati prikazani u Tablici 2. pokazuju razliku") != [])
    check("K161: množina „u Tablicama 7. i 8.\" JEST kršenje",
          RE.findall("Rezultati prikazani u Tablicama 7. i 8. ne podupiru H4") != [],
          RE.findall("Rezultati prikazani u Tablicama 7. i 8. ne podupiru H4"))
    check("K161: „u Tablici 1\" bez točke nije kršenje",
          RE.findall("prikazano je u Tablici 1 i vrijedi") == [])

    # ---------------- K162: redoslijed dijelova
    ispravan = ["TEMELJNA DOKUMENTACIJSKA KARTICA", "BASIC DOCUMENTATION CARD",
                "SAŽETAK", "SUMMARY", "Sadržaj", "POPIS KRATICA", "1. UVOD",
                "Tekst uvoda koji ima dovoljno riječi."]
    zamijenjen = ["TEMELJNA DOKUMENTACIJSKA KARTICA", "BASIC DOCUMENTATION CARD",
                  "SAŽETAK", "SUMMARY", "POPIS KRATICA", "Sadržaj", "1. UVOD",
                  "Tekst uvoda koji ima dovoljno riječi."]
    with tempfile.TemporaryDirectory() as td:
        def ispis(odlomci, ime):
            put = _docx(odlomci, os.path.join(td, ime))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    M.main([put])
                except SystemExit:
                    pass
            return buf.getvalue()

        out_ok = ispis(ispravan, "ok.docx")
        out_los = ispis(zamijenjen, "los.docx")

    red_ok = [r for r in out_ok.splitlines() if "redoslijed dijelova" in r]
    red_los = [r for r in out_los.splitlines() if "redoslijed dijelova" in r]
    check("K162: provjera redoslijeda dijelova uopće postoji",
          bool(red_ok) and bool(red_los), (red_ok, red_los))
    check("K162: ispravan redoslijed prolazi",
          bool(red_ok) and "✅" in red_ok[0], red_ok)
    check("K162: zamijenjeni Sadržaj i Popis kratica JESU nalaz",
          bool(red_los) and "⚠" in red_los[0], red_los)
    check("K162: nalaz imenuje propisani redoslijed",
          bool(red_los) and "propisano" in red_los[0], red_los)

    print("=" * 70)
    print("REZULTATI TESTOVA: %d/%d prošlo" % (len(SVE) - len(PALO), len(SVE)))
    print("=" * 70)
    return 1 if PALO else 0


if __name__ == "__main__":
    sys.exit(main())
