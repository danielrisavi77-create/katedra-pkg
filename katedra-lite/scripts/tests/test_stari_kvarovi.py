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
import re
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

    # --- doktrinarni kvarovi: 43, 49, 134 -------------------------------------
    # Doktrina je artefakt kao i kod, pa ograda smije mjeriti njezin tekst — ali
    # samo ODLUČUJUĆI token, ne rečenicu. Preformulacija ne smije rušiti test;
    # brisanje odluke mora.
    with io.open(os.path.join(KORIJEN, "SKILL.md"), encoding="utf-8") as f:
        router = f.read()

    # 43: 403 se rješava pojmom „izvor sesije", ne imenom klika u postavkama
    check("K43: doktrina imenuje `izvor sesije`", "izvor sesije" in router)
    check("K43: doktrina ne šalje korisnika u konkretnu postavku",
          "Add from GitHub" not in router.split("| Površina |")[0])

    # 49: uz verziju paketa u prvoj poruci mora stajati i redak drift.py
    # Odlučujući token je zahtjev iz pravila (4), ne prvi spomen varijable:
    # ista se riječ pojavljuje i u bash bloku iznad.
    zahtjev = re.search(r"ispiši u prvoj poruci", router)
    okolina = router[max(0, zahtjev.start() - 260):zahtjev.end()] if zahtjev else ""
    check("K49: uz verziju paketa traži se i redak `drift.py --kratko`",
          "drift.py --kratko" in okolina, okolina[-90:])

    # 134: Cowork redak je ❌ BEZ uvjeta — uvjet koji se ne ispunjava nigdje
    #      briše se, ne ublažava (issue #84581)
    red = next((x for x in router.splitlines() if x.startswith("| Cowork")), "")
    check("K134: Cowork redak postoji i nosi ❌", "❌" in red, red[:90])
    check("K134: Cowork redak nema uvjetni izlaz („samo ako”)",
          "samo ako" not in red, red[:90])

    # --- fixture dokumenti: 40, 41, 45, 71 ------------------------------------
    # Najmanji .docx koji kvar izaziva. Fixture je jeftiniji od cijelog rada i
    # preživljava; gradi se ovdje, ne čuva u repou.
    from docx import Document
    from docx.shared import Cm
    from PIL import Image
    mapa = tempfile.mkdtemp()

    # 40: slika koju je autor „povukao mišem" je <wp:anchor>, ne <wp:inline>,
    #     i inline_shapes je ne vidi — alat je javljao „nema što mjeriti".
    png = os.path.join(mapa, "s.png")
    Image.new("RGB", (40, 40), "white").save(png)
    p_inline = os.path.join(mapa, "inline.docx")
    d = Document(); d.add_paragraph("Tekst."); d.add_picture(png, width=Cm(4)); d.save(p_inline)
    pp = modul("provjeri_prikaze")
    check("K40: inline slika se broji", len(pp._slike(p_inline)[1]) == 1)
    p_anchor = os.path.join(mapa, "anchor.docx")
    d2 = Document(p_inline)
    WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
    for el in list(d2.element.body.iter("{%s}inline" % WP)):
        el.tag = "{%s}anchor" % WP
    d2.save(p_anchor)
    d3 = Document(p_anchor)
    check("K40: fixture doista zaobilazi inline_shapes", len(d3.inline_shapes) == 0)
    check("K40: plutajuća slika se ipak broji", len(pp._slike(p_anchor)[1]) == 1,
          pp._slike(p_anchor)[1])
    check("K40: ograda protiv tihe nule — <w:drawing> u XML-u je 1",
          pp._crteza_u_xml(d3) == 1, pp._crteza_u_xml(d3))

    # 41: „Uvod" zabunom na Heading 2 → uvod je None → „rad nema tezu"
    p41 = os.path.join(mapa, "uvod2.docx")
    d = Document()
    d.add_paragraph("Uvod", style="Heading 2")
    d.add_paragraph("Ovaj rad tvrdi da je X posljedica Y, jer se Z pokazalo presudnim u tri slučaja.")
    d.add_paragraph("Rasprava", style="Heading 1")
    d.add_paragraph("Duga rečenica koja prelazi četrdeset znakova da bi bila odlomak, i završava točkom.")
    d.add_paragraph("Zaključak", style="Heading 1")
    d.add_paragraph("Još jedna dovoljno duga rečenica koja završava točkom za zaključak rada.")
    d.save(p41)
    ca.poglavlja(p41)
    krivi = ca._uvod_na_krivoj_razini()
    check("K41: „Uvod” na Heading 2 se prepoznaje kao kriva razina, ne kao odsutan",
          krivi is not None and krivi[0] == 2, krivi)
    p41b = os.path.join(mapa, "uvod1.docx")
    d = Document(); d.add_paragraph("Uvod", style="Heading 1")
    d.add_paragraph("Rečenica uvoda koja je dovoljno duga da bude odlomak i završava točkom.")
    d.save(p41b)
    ca.poglavlja(p41b)
    check("K41: „Uvod” na Heading 1 nije kriva razina", ca._uvod_na_krivoj_razini() is None)

    # 45: format papira — Letter je prolazio kao A4 jer ga nitko nije mjerio
    cr = modul("check_rules")

    class Iz:
        def __init__(self):
            self.r = []

        def dodaj(self, pravilo, trazeno, nadjeno, stanje, detalji=None, **kw):
            self.r.append((pravilo, stanje, kw.get("rule_id")))

    def dokument_formata(w_cm, h_cm, ime):
        p = os.path.join(mapa, ime)
        dd = Document()
        dd.sections[0].page_width = Cm(w_cm)
        dd.sections[0].page_height = Cm(h_cm)
        dd.add_paragraph("Tekst.")
        dd.save(p)
        return Document(p)

    iz = Iz()
    cr.provjeri_format_stranice(iz, dokument_formata(21.59, 27.94, "letter.docx"), {"format": {}})
    check("K45: Letter uz očekivani A4 je KRŠENJE (format.stranica)",
          any(st == cr.LOSE and rid == "format.stranica" for _p, st, rid in iz.r), iz.r)
    iz = Iz()
    cr.provjeri_format_stranice(iz, dokument_formata(21.0, 29.7, "a4.docx"), {"format": {}})
    check("K45: A4 uz očekivani A4 prolazi",
          any(st == cr.OK and rid == "format.stranica" for _p, st, rid in iz.r)
          and not any(st == cr.LOSE for _p, st, _r in iz.r), iz.r)

    # 71: faza A (placeholderi) mora imati izvršitelja. U predaji je to izravan
    #     blokirajući korak; u auditu ide kroz motor (engine.py --audit →
    #     rad-audit/generate_report.py:115, koji sam citira kvar 71), pa se ondje
    #     mjeri da je motor blokirajući — bez toga bi faza A opet bila bez ruke.
    g = modul("gate")
    c = {"rad": "rad.docx", "pdf": None, "profil": "p.json", "tip": "diplomski",
         "kat": ".katedra"}
    k = next((x for x in g.koraci("predaja", c) if x.kid == "placeholderi"), None)
    check("K71: predaja zove check_placeholders.py kao blokirajući korak",
          k is not None and k.blokira
          and any("check_placeholders.py" in str(a) for a in k.argv),
          None if k is None else (k.blokira, [str(a) for a in k.argv][:3]))
    m = next((x for x in g.koraci("audit", c) if x.kid == "motor_audit"), None)
    check("K71: audit ima blokirajući motor koji nosi fazu A",
          m is not None and m.blokira and any("--audit" in str(a) for a in m.argv),
          None if m is None else (m.blokira, [str(a) for a in m.argv][:3]))

    print("=" * 70)
    print("REZULTATI TESTOVA: %d/%d prošlo"
          % (len(SVE) - len(PALO), len(SVE)))
    print("=" * 70)
    return 1 if PALO else 0


if __name__ == "__main__":
    sys.exit(main())
