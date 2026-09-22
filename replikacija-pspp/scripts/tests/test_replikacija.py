#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testovi za replikacija-pspp — bez PSPP-a i bez zaslona.

Skill do v2.2.0 nije imao nijedan test, a njegova je jedina svrha reći „brojka u
radu se (ne) poklapa s neovisnim izračunom". Ovdje se mjeri upravo taj sud:
čitanje PSPP-ova CSV ispisa, parsiranje hrvatskih i PSPP-ovih brojeva,
tolerancija po točnosti zapisa i to da promašaj daje izlaz „ne poklapa se".
PSPP i snimke sučelja se ne pokreću; to ostaje ručni korak skilla.
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TU)
SKILL = os.path.dirname(SCRIPTS)

_spec = importlib.util.spec_from_file_location("pspp_replikacija", os.path.join(SCRIPTS, "pspp_replikacija.py"))
pr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pr)

PALO = []
SVE = []


def check(naziv, uvjet, detalj=""):
    SVE.append(naziv)
    print("  %-8s %s" % ("✓" if uvjet else "✗ FAIL", naziv))
    if not uvjet:
        PALO.append(naziv)
        if detalj:
            print("           detalj: %r" % (detalj,))


PRIMJER = json.load(open(os.path.join(SKILL, "assets", "primjer_replikacija.json"), encoding="utf-8"))

# ── 1. primjer konfiguracije je valjan prema vlastitoj shemi ───────────────
try:
    import jsonschema
    shema = json.load(open(os.path.join(SKILL, "assets", "replikacija.schema.json"), encoding="utf-8"))
    greske = sorted(jsonschema.Draft202012Validator(shema).iter_errors(PRIMJER), key=str) \
        if "2020" in shema.get("$schema", "") else sorted(jsonschema.Draft7Validator(shema).iter_errors(PRIMJER), key=str)
    check("primjer_replikacija.json prolazi replikacija.schema.json", not greske,
          [g.message for g in greske[:3]])
except ImportError:
    print("  PRESKOČENO  shema: nema paketa jsonschema (nije prolaz)")

# ── 2. sintaksa ─────────────────────────────────────────────────────────────
k = dict(PRIMJER, varijable=["dob", "FL"])
sps = pr.gradi_sintaksu(k)
check("sintaksa učitava bazu po imenu datoteke, ne po apsolutnoj putanji",
      "/FILE='%s'" % os.path.basename(PRIMJER["baza"]) in sps, sps[:300])
check("sintaksa sprema baza.sav", "SAVE OUTFILE='baza.sav'." in sps)
check("svaka analiza ima natpis i svoju sintaksu, redom",
      all(("* %s." % a.get("natpis", a["ime"])) in sps and a["sintaksa"].strip() in sps
          for a in PRIMJER["analize"]))
redoslijed = [sps.index(a["sintaksa"].strip()) for a in PRIMJER["analize"]]
check("redoslijed analiza u sintaksi = redoslijed u konfiguraciji", redoslijed == sorted(redoslijed))

# ── 3. brojevi ──────────────────────────────────────────────────────────────
check("broj('.74') = 0.74 (PSPP ispušta vodeću nulu)", pr.broj(".74") == 0.74)
check("broj('51.9%') = 51.9", pr.broj("51.9%") == 51.9)
check("broj('') i broj('abc') su None, ne 0", pr.broj("") is None and pr.broj("abc") is None)
check("kao_broj('24,5') = 24.5 (decimalni zarez iz rada)", pr.kao_broj("24,5") == 24.5)
check("kao_broj('< 0,001') = 0.001", pr.kao_broj("< 0,001") == 0.001)
check("decimala('24,51') = 2, decimala('131') = 0",
      pr.decimala("24,51") == 2 and pr.decimala("131") == 0)
check("hr(24.5, 2) = '24,50'", pr.hr(24.5, 2) == "24,50")


# ── 4. izvlačenje i sud „poklapa se" iz sintetskog PSPP CSV-a ──────────────
def ispis_csv(mapa, mean_dob):
    with open(os.path.join(mapa, "izlaz.csv"), "w", encoding="utf-8", newline="") as f:
        f.write("Table: Descriptive Statistics\n")
        f.write(",N,Mean,Std Dev,Minimum,Maximum\n")
        f.write("dob,131,%s,3.10,19,41\n" % mean_dob)
        f.write("Valid N (listwise),131,,,,\n")


konf = {
    "oznake": {},
    "ocekivano": [
        {"oznaka": "A1", "statistika": "N", "u_radu": "131", "decimala": 0,
         "izvor": {"tip": "deskriptiva", "varijabla": "dob", "stupac": "N"}},
        {"oznaka": "A2", "statistika": "dob M", "u_radu": "24,5", "decimala": 2,
         "izvor": {"tip": "deskriptiva", "varijabla": "dob", "stupac": "Mean"}},
    ],
}

with tempfile.TemporaryDirectory() as d:
    ispis_csv(d, "24.51")
    with contextlib.redirect_stdout(io.StringIO()) as out:
        ok = pr.izvuci(konf, d)
    check("24,5 u radu i 24.51 u PSPP-u se poklapaju (mjerodavna je grublja točnost)", ok is True,
          out.getvalue())
    usporedba = open(os.path.join(d, "usporedba.csv"), encoding="utf-8").read()
    check("usporedba.csv nosi oba retka s ocjenom 'da'", usporedba.count(",da") == 2, usporedba)

with tempfile.TemporaryDirectory() as d:
    ispis_csv(d, "24.61")
    with contextlib.redirect_stdout(io.StringIO()) as out:
        ok = pr.izvuci(konf, d)
    check("24,5 u radu i 24.61 u PSPP-u NE poklapaju se → izvuci vraća False", ok is False,
          out.getvalue())
    check("promašaj je imenovan oznakom i objema vrijednostima",
          "A2: rad 24,5 | PSPP 24,61" in out.getvalue(), out.getvalue())

with tempfile.TemporaryDirectory() as d:
    ispis_csv(d, "24.51")
    konf2 = json.loads(json.dumps(konf))
    konf2["ocekivano"][1]["izvor"]["varijabla"] = "nepostojeca"
    with contextlib.redirect_stdout(io.StringIO()) as out:
        ok = pr.izvuci(konf2, d)
    usporedba = open(os.path.join(d, "usporedba.csv"), encoding="utf-8").read()
    check("vrijednost koju PSPP ne ispisuje je 'ne ispisuje se', nikad 'da'",
          "ne ispisuje se" in usporedba and usporedba.count(",da") == 1, usporedba)

print("")
print("%d/%d" % (len(SVE) - len(PALO), len(SVE)))
sys.exit(1 if PALO else 0)
