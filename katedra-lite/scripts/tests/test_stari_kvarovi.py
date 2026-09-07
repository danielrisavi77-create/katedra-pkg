#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ograde za stare kvarove koji ih dosad nisu imali (kvar 141).

Kvar 140 je izmjerio da jedanaest unosa iz duga nema nijedan test koji dodiruje
isti kod. Ovdje se zatvaraju oni koji se daju provjeriti bez dokumenta i bez
mreže: 24, 25, 31, 33, 52.

Prva verzija ovih testova bila je LAŽNA: provjeravala je `"esej" in json.dumps(...)`
i `any("synced" in redak)`, pa je mutacija `"esej"` → `"esejX"` prolazila jer
podniska i dalje postoji. Svih pet mutacija prošlo je bez ijednog pada. Zato ovdje
nema provjere nad tekstom datoteke: gleda se ponašanje ili razriješena struktura.
"""
import importlib.util
import io
import json
import os
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TU)
KORIJEN = os.path.dirname(SCRIPTS)

PALO = []
SVE = []


def check(naziv, uvjet, detalj=""):
    SVE.append(naziv)
    print("  %-8s %s" % ("✓" if uvjet else "✗ FAIL", naziv))
    if not uvjet:
        PALO.append(naziv)
        if detalj:
            print("           detalj: %r" % (detalj,))


def modul(ime):
    spec = importlib.util.spec_from_file_location(ime, os.path.join(SCRIPTS, ime + ".py"))
    m = importlib.util.module_from_spec(spec)
    if SCRIPTS not in sys.path:
        sys.path.insert(0, SCRIPTS)
    spec.loader.exec_module(m)
    return m


def shema(ime):
    with io.open(os.path.join(KORIJEN, "references", "fakulteti", ime),
                 encoding="utf-8") as f:
        return json.load(f)


def _svi_stringovi(o):
    """Sve niske u strukturi, kao skup — ne kao tekst datoteke."""
    out = set()
    if isinstance(o, str):
        out.add(o)
    elif isinstance(o, dict):
        for k, v in o.items():
            out.add(k)
            out |= _svi_stringovi(v)
    elif isinstance(o, list):
        for v in o:
            out |= _svi_stringovi(v)
    return out


def main():
    print("=" * 70)
    print("TESTOVI starih kvarova bez ograde")
    print("=" * 70)

    # --- kvar 25: satelit u synced/<hash>/<slug> --------------------------------
    # Pravi uvjet: lažni HOME u kojem satelit STVARNO leži pod synced/<hash>/.
    # Bez tog uzorka `kandidati()` ga ne vraća, pa satelit koji jest instaliran
    # prolazi kao „nije pronađen" i posao se improvizira (pravilo 10).
    lazni_home = tempfile.mkdtemp()
    gnijezdo = os.path.join(lazni_home, ".claude", "skills", "synced", "abc123", "rad-docx")
    os.makedirs(gnijezdo)
    stari_home = {k: os.environ.get(k) for k in ("HOME", "USERPROFILE")}
    os.environ["HOME"] = lazni_home
    os.environ["USERPROFILE"] = lazni_home
    try:
        v = modul("vjestine")
        nadjeni = v.kandidati("rad-docx")
    finally:
        for k, val in stari_home.items():
            if val is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = val
    check("K25: satelit iz synced/<hash>/ je među kandidatima",
          any(os.path.normcase(gnijezdo) == os.path.normcase(p) for p in nadjeni),
          nadjeni[:4])

    # --- kvar 31: nepoznat naslov popisa ne smije rušiti gate -------------------
    pl = modul("provjeri_literaturu")
    for naslov in ("POPIS LITERATURE", "Izvori i literatura", "CITIRANA LITERATURA",
                   "5. Popis korištene literature", "Bibliografija", "Popis referenci"):
        check("K31: „%s” je naslov popisa" % naslov[:28], pl.je_naslov_literature(naslov))
    check("K31: obična rečenica NIJE naslov popisa",
          not pl.je_naslov_literature("U literaturi se navodi da je to tako."))

    # --- kvar 52: strukturni znak je osjetljiv na veličinu slova ----------------
    # `re.IGNORECASE` nad CIJELIM uzorkom činio je da „autor: vlastita obrada"
    # ispadne tuđe autorstvo, jer je veliko slovo iza „autor" bilo strukturni
    # znak koji je ignorecase pojeo.
    ca = modul("check_argument")
    check("K52: „autor Kovačević” JEST tuđe autorstvo",
          bool(ca._TUDJE_AUTORSTVO_IME_RE.search("prema autor Kovačević")))
    check("K52: „autor vlastita obrada” NIJE tuđe autorstvo",
          not ca._TUDJE_AUTORSTVO_IME_RE.search("Izvor: autor vlastita obrada"))
    check("K52: „Autori Marić i Horvat” JEST tuđe autorstvo",
          bool(ca._TUDJE_AUTORSTVO_IME_RE.search("Autori Marić i Horvat")))

    # --- kvar 24: tip rada `esej` i `primjerci` u shemama -----------------------
    # Gleda se RAZRIJEŠENA struktura, ne tekst datoteke: `"esej" in json.dumps(...)`
    # prolazi i kad u shemi piše „esejX".
    s, rs = shema("_schema.json"), shema("_resolved_schema.json")
    n_s, n_rs = _svi_stringovi(s), _svi_stringovi(rs)
    check("K24: shema poznaje tip rada „esej”", "esej" in n_s, sorted(x for x in n_s if "esej" in x))
    check("K24: razriješena shema poznaje tip rada „esej”", "esej" in n_rs)
    check("K24: razriješena shema poznaje `primjerci`", "primjerci" in n_rs)

    # --- kvar 33: opseg po dijelovima ------------------------------------------
    check("K33: obje sheme poznaju `dioOpsega`",
          "dioOpsega" in n_s and "dioOpsega" in n_rs)
    check("K33: `provjeri_dijelove.py` postoji",
          os.path.exists(os.path.join(SCRIPTS, "provjeri_dijelove.py")))

    # --- kvar 29: uvjet je znao samo fakultet, ne i tip rada ------------------
    # Kućni stil završnog primjenjivao se na seminarski jer `uvjet.tipovi`
    # nitko nije gledao. `_primjenjivo` je čista funkcija, pa se mjeri izravno.
    zapis = {"uvjet": {"tipovi": ["zavrsni", "diplomski"]}}
    check("K29: sposobnost za završni NE vrijedi za seminarski",
          not v._primjenjivo(zapis, None, "seminarski"))
    check("K29: ista sposobnost vrijedi za diplomski",
          v._primjenjivo(zapis, None, "diplomski"))
    check("K29: bez `tipovi` ne isključuje se ništa",
          v._primjenjivo({"uvjet": {}}, None, "seminarski"))
    check("K29: bez konteksta (tip nije poznat) ne isključuje se ništa",
          v._primjenjivo(zapis, None, None))

    # --- kvar 26: `meta` se koristio u `_renderiraj` koji ga nikad nije primio --
    import inspect
    bd = modul("build_docx")
    par = inspect.signature(bd._renderiraj).parameters
    check("K26: `_renderiraj` prima `meta`", "meta" in par)
    check("K26: `meta` ima zadanu vrijednost (poziv bez njega ne puca)",
          "meta" in par and par["meta"].default is not inspect.Parameter.empty,
          str(par.get("meta")))

    # --- kvar 48: proturječje u vlastitim brojkama rada ------------------------
    # „šest od sedam koraka" u jednom poglavlju i „pet od sedam koraka" u drugom
    # ne pada ni na jednoj provjeri lanca — nijedna ne gleda rad protiv njega
    # samoga. Lens i usporedba su čiste funkcije.
    pb = modul("provjeri_brojke_u_tekstu")
    m = pb.UZORAK_OD.search("Time je zatvoreno šest od sedam koraka postupka.")
    check("K48: uzorak hvata „N od M <imenica>”", bool(m), m and m.groups())
    nalazi = [("korak", "od", "6", "7", "Rasprava", "šest od sedam koraka"),
              ("korak", "od", "5", "7", "Zaključak", "pet od sedam koraka")]
    prot = pb.proturjecja(nalazi)
    check("K48: dvije različite vrijednosti istog pojma su nalaz",
          len(prot) == 1 and prot[0]["pojam"] == "korak", prot)
    isti = [("korak", "od", "6", "7", "Rasprava", "šest od sedam"),
            ("korak", "od", "6", "7", "Zaključak", "šest od sedam")]
    check("K48: ista vrijednost dvaput NIJE nalaz", pb.proturjecja(isti) == [])

    print("=" * 70)
    print("REZULTATI TESTOVA: %d/%d prošlo"
          % (len(SVE) - len(PALO), len(SVE)))
    print("=" * 70)
    return 1 if PALO else 0


if __name__ == "__main__":
    sys.exit(main())
