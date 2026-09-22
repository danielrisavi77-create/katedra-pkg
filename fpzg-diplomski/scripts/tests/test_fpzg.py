#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testovi za fpzg-diplomski — kućni stil FPZG-a.

Skill do v2.2.0 nije imao nijedan test. Ovdje se mjeri ono što skill tvrdi u
SKILL.md-u: provjeri_stil.py (dvotočke, duga crtica, mjeri se samo tijelo rada),
provjeri_prikaze.py (polja, placeholderi, prikazi bez izvora, i da neizmjereno
lomljenje tablica nije prolaz) te pomoćnici stil_grafikona.py.
"""
import contextlib
import importlib.util
import io
import os
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TU)
sys.path.insert(0, SCRIPTS)


def ucitaj_modul(ime):
    spec = importlib.util.spec_from_file_location(ime, os.path.join(SCRIPTS, ime + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PALO = []
SVE = []


def check(naziv, uvjet, detalj=""):
    SVE.append(naziv)
    print("  %-8s %s" % ("✓" if uvjet else "✗ FAIL", naziv))
    if not uvjet:
        PALO.append(naziv)
        if detalj:
            print("           detalj: %r" % (detalj,))


def tiho(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        kod = fn(*a)
    return kod, buf.getvalue()


stil = ucitaj_modul("provjeri_stil")
prikazi = ucitaj_modul("provjeri_prikaze")
import docx  # noqa: E402  (python-docx je ovisnost paketa)

CISTO = ("Rad istražuje financijsku pismenost mladih. Uzorak čini 131 student. "
         "Rezultati pokazuju umjerenu razinu znanja. Razlike među skupinama nisu velike. "
         "Zaključak se odnosi samo na ovaj uzorak.\n")

with tempfile.TemporaryDirectory() as d:
    # ── provjeri_stil.py nad markdownom ────────────────────────────────────
    p = os.path.join(d, "pog1.md")
    open(p, "w", encoding="utf-8").write("# 1. Uvod\n\n" + CISTO)
    kod, out = tiho(stil.main, [p])
    check("stil: čist tekst → 0", kod == 0, out)

    open(p, "w", encoding="utf-8").write("# 1. Uvod\n\n" + CISTO + "Rezultat je jasan — ali nije konačan.\n")
    kod, out = tiho(stil.main, [p])
    check("stil: jedna duga crtica u prozi → 1 (prag je 0)", kod == 1 and "duga crtica: 1×" in out, out)

    open(p, "w", encoding="utf-8").write(
        "# Naslov — s crticom u naslovu\n\n| a — b | c |\n\n" + CISTO)
    kod, out = tiho(stil.main, [p])
    check("stil: crtica u naslovu i tablici se ne broji (mjeri se proza)", kod == 0, out)

    # Dvotočka iza znamenke („12:30", „1:2") alat namjerno ne broji, pa fixture nema brojeva.
    gusto = "".join("Ovo je važna tvrdnja: ona se razrađuje ovdje. " for _ in range(10))
    open(p, "w", encoding="utf-8").write(gusto)
    kod, out = tiho(stil.main, [p])
    check("stil: 10 razrađujućih dvotočaka na 10 rečenica → 1", kod == 1 and "previše" in out, out)

    open(p, "w", encoding="utf-8").write("".join("Sastanak je u 12:30 sati. " for _ in range(10)))
    kod, out = tiho(stil.main, [p])
    check("stil: dvotočka u vremenu (12:30) nije stilska dvotočka", "dvotočaka: 0" in out, out)

    nabraja = "".join("Ovdje su tri skupine: A, B i C. " for _ in range(10))
    open(p, "w", encoding="utf-8").write(nabraja)
    kod, out = tiho(stil.main, [p])
    check("stil: dvotočka koja uvodi nabrajanje broji se kao nabrajanje, ne razrada",
          "uvodi nabrajanje: 10" in out and "razrađuje prethodnu tvrdnju: 0" in out, out)

    # ── provjeri_stil.py nad .docx: mjeri se samo tijelo rada ──────────────
    doc = docx.Document()
    doc.add_paragraph("Mentor: prof. dr. sc. Netko — naslovnica")
    doc.add_paragraph("1. Uvod")
    doc.add_paragraph(CISTO.strip())
    doc.add_paragraph("Literatura")
    doc.add_paragraph("Autor, A. (2020). Naslov — podnaslov. Zagreb: Izdavač.")
    pd = os.path.join(d, "rad.docx")
    doc.save(pd)
    kod, out = tiho(stil.main, [pd])
    check("stil (.docx): crtice na naslovnici i u literaturi se ne broje", kod == 0, out)

    # ── provjeri_prikaze.py ────────────────────────────────────────────────
    doc = docx.Document()
    doc.add_paragraph("1. Uvod")
    doc.add_paragraph("Tablica 1. Struktura uzorka")
    t = doc.add_table(rows=2, cols=2)
    t.cell(0, 0).text, t.cell(0, 1).text = "Skupina", "N"
    t.cell(1, 0).text, t.cell(1, 1).text = "Studenti", "131"
    doc.add_paragraph("Izvor: vlastito istraživanje.")
    pr = os.path.join(d, "prikazi.docx")
    doc.save(pr)
    kod, out = tiho(prikazi.main, pr)
    check("prikazi: bez PDF-a i uz tablicu → 2 (lomljenje nije izmjereno), ne 0",
          kod == 2 and "NIJE izmjereno" in out, out)

    doc = docx.Document()
    doc.add_paragraph("1. Uvod")
    doc.add_paragraph("Tekst bez prikaza.")
    bez = os.path.join(d, "bez_tablica.docx")
    doc.save(bez)
    kod, out = tiho(prikazi.main, bez)
    check("prikazi: rad bez tablica i bez PDF-a nema što lomiti → 0", kod == 0, out)

    doc = docx.Document()
    doc.add_paragraph("1. Uvod")
    doc.add_paragraph("Tvrdnja [TREBA IZVOR] i citat [PROVJERI STR.].")
    doc.add_paragraph("Grafikon 1. Razina pismenosti")
    doc.add_paragraph("tekst")
    ned = os.path.join(d, "nedovrseno.docx")
    doc.save(ned)
    kod, out = tiho(prikazi.main, ned)
    check("prikazi: TREBA IZVOR i PROVJERI STR su nalazi → 1",
          kod == 1 and "tvrdnja bez izvora: 1×" in out and "citat bez broja stranice: 1×" in out, out)
    check("prikazi: grafikon bez retka „Izvor:” je nalaz",
          "prikaza bez retka „Izvor:”: 1" in out, out)

# ── stil_grafikona.py ──────────────────────────────────────────────────────
try:
    sg = ucitaj_modul("stil_grafikona")
    ramp = sg.ordinalni_ramp(5)
    svjetlina = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in ramp]
    check("grafikoni: ordinalni ramp ide od svjetlijeg prema tamnijem",
          all(a > b for a, b in zip(svjetlina, svjetlina[1:])), svjetlina)
    check("grafikoni: sve boje rampa su valjane RGB vrijednosti",
          all(0 <= c <= 1 for boja in ramp for c in boja), ramp)

    class _Stupac:
        def __init__(self, rgb):
            self.rgb = rgb

        def get_facecolor(self):
            return (*self.rgb, 1.0)

    check("grafikoni: na tamnom stupcu oznaka je bijela",
          sg.boja_oznake(_Stupac((0.1, 0.1, 0.1))) == "#ffffff")
    check("grafikoni: na svijetlom stupcu oznaka je tinta, ne bijela",
          sg.boja_oznake(_Stupac((0.95, 0.95, 0.95))) != "#ffffff")
except ImportError as e:
    print("  PRESKOČENO  grafikoni: %s (nije prolaz)" % e)

print("")
print("%d/%d" % (len(SVE) - len(PALO), len(SVE)))
sys.exit(1 if PALO else 0)
