#!/usr/bin/env python3
"""Faza D, korak 0 — inventar tvrdnji po referenci.

Uporaba:
  python3 inventar_tvrdnji.py rad.docx
  python3 inventar_tvrdnji.py rad.docx --json tvrdnje.json
  python3 inventar_tvrdnji.py rad.docx --dosjei fazaD/ --po-seriji 7

Zašto postoji
-------------
Faza D pita sadrži li izvor tvrdnju koja mu se pripisuje. Prije nego se ijedan
izvor otvori, treba znati ŠTO se kojemu izvoru pripisuje — a to u paketu nije
postojalo: `mapa_izvora.py` veže ključ citata na datoteku izvora,
`check_tvrdnja_izvor.py` provjerava brojku kad datoteka postoji, ali nitko nije
izvlačio popis tvrdnji iz samoga rada.

Na diplomskom radu sa 78 referenci taj je popis izrađen ručno prije nego što je
faza D uopće mogla početi: 51 referenca nosila je brojčanu tvrdnju, 27 samo
opisnu. Podjela je bitna jer se brojčana tvrdnja provjerava mehanički (broj je
ili u izvoru ili nije), a opisna traži čitanje. Rezultat je bio 6 neslaganja i
9 tvrdnji kojih u izvoru nema — nijedno se ne bi našlo bez ovog koraka.

Što radi
--------
1. razdvaja tijelo rada od popisa literature (`common.LIT_HEADING_RE`),
2. čita bibliografske jedinice iz popisa,
3. za svaku rečenicu tijela nalazi citate u njoj (Vancouver `(N)` ili IEEE `[N]`),
4. svakoj referenci pripisuje rečenice koje je citiraju, razvrstane na
   BROJČANE (rečenica nosi broj i izvan samog navoda) i OPISNE,
5. po želji ispisuje dosjee po seriji, spremne za ručnu ili podijeljenu provjeru.

Ne provjerava ništa sam — to je posao čitanja izvora. Ovo je popis posla.

Izlazni kod: 0 za izrađen inventar, 2 za nevaljane argumente, 3 za deklariranu
granicu (nedostupan dokument, neprepoznat popis ili nepodržan stil citiranja).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from common import (load_docx_text, load_supplementary_text,  # noqa: E402
                    find_vancouver_citations, detect_citation_style,
                    parse_citation_group, LIT_HEADING_RE)

# Statistika u zagradi nije citat (kvar 13): t(106,08), F(4; 44,89).
STAT = re.compile(r"\b[A-Za-zͰ-Ͽ]{1,3}\(\s*\d+[.,;]\s*\d*[.,]?\d*\s*\)")
RE_JEDINICA = re.compile(r"(?m)^\s*(\d{1,3})\.\s+(\S.*)$")
RE_JEDINICA_IEEE = re.compile(r"(?m)^\s*\[(\d{1,3})\]\s+(\S.*)$")
RE_IEEE = re.compile(r"\[([0-9][0-9,\s–-]*)\]")
RE_RECENICA = re.compile(r"(?<=[.!?])\s+(?=[A-ZČĆŠŽĐ])")


def _jedinice(lit: str, najvise: int = 999, stil: str = "vancouver") -> dict[int, str]:
    out = {}
    uzorak = RE_JEDINICA_IEEE if stil == "ieee" else RE_JEDINICA
    for broj, tekst in uzorak.findall(lit):
        n = int(broj)
        if n <= najvise and n not in out:
            out[n] = " ".join(tekst.split())
    return out


def _citati_u(recenica: str, stil: str) -> set[int]:
    if stil == "ieee":
        nums = set()
        for m in RE_IEEE.finditer(recenica):
            nums |= {k for k in parse_citation_group(m.group(1)) if k <= 999}
        return nums
    nums = set()
    for _pos, grupa in find_vancouver_citations(recenica):
        nums |= set(grupa)
    return nums


def analiza(put: str):
    if not os.path.exists(put):
        return None, f"datoteka ne postoji: {put}"
    try:
        body, cells, _ = load_docx_text(put, include_tables=True)
        sup = load_supplementary_text(put)
    except Exception as e:  # noqa: BLE001
        return None, f"dokument se ne da pročitati kao .docx ({e})"
    m = list(LIT_HEADING_RE.finditer(body))
    if not m:
        return None, "popis literature nije prepoznat"
    rez = m[-1].end()
    tijelo, lit = body[:rez], body[rez:]

    stil, _ = detect_citation_style(body)
    if stil not in {"ieee", "vancouver"}:
        return None, f"stil citiranja {stil!r} nije podržan: inventar traži IEEE ili Vancouver"
    jed = _jedinice(lit, stil=stil)
    if not jed:
        return None, "popis je prepoznat, ali nijedna jedinica nije pročitana"
    najveci = max(jed)

    izvori_teksta = [tijelo, "\n".join(cells), sup["footnotes"], sup["endnotes"]]
    mapa: dict[int, dict[str, list]] = {n: {"brojcane": [], "opisne": []} for n in jed}
    for blok in izvori_teksta:
        for rec in RE_RECENICA.split(STAT.sub(" ", blok or "")):
            rec = " ".join(rec.split())
            if not rec:
                continue
            nums = {k for k in _citati_u(rec, stil) if k in jed}
            if not nums:
                continue
            golo = re.sub(r"\((?:\d{1,3})(?:\s*[,;–-]\s*\d{1,3})*\)", "", rec)
            golo = RE_IEEE.sub("", golo)
            kljuc = "brojcane" if re.search(r"\d", golo) else "opisne"
            for n in nums:
                if rec not in mapa[n][kljuc]:
                    mapa[n][kljuc].append(rec)

    return {"stil": stil, "najveci": najveci,
            "jedinice": jed, "tvrdnje": mapa}, None


def _dosjei(res, mapa_dir, po_seriji):
    os.makedirs(mapa_dir, exist_ok=True)
    s_brojkama = sorted(n for n, v in res["tvrdnje"].items() if v["brojcane"])
    serije = [s_brojkama[i:i + po_seriji]
              for i in range(0, len(s_brojkama), po_seriji)]
    putovi = []
    for i, grupa in enumerate(serije, 1):
        redci = [f"# Serija {i} — reference: {', '.join(map(str, grupa))}\n"]
        for n in grupa:
            v = res["tvrdnje"][n]
            redci.append(f"\n## Referenca {n}\n")
            redci.append(f"\n**Bibliografska jedinica:** {res['jedinice'][n]}\n")
            redci.append("\n**Rečenice s brojkama (provjeri SVAKU brojku u izvoru):**\n")
            for r in v["brojcane"]:
                redci.append(f"- {r}\n")
            if v["opisne"]:
                redci.append("\n*Opisne rečenice (provjeri ako je izvor lako dostupan):*\n")
                for r in v["opisne"][:3]:
                    redci.append(f"- {r}\n")
        put = os.path.join(mapa_dir, f"serija{i}.md")
        with open(put, "w", encoding="utf-8") as fh:
            fh.write("".join(redci))
        putovi.append(put)
    return putovi


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    ap = argparse.ArgumentParser(description="Inventar tvrdnji po numeričkoj referenci.")
    ap.add_argument("rad")
    ap.add_argument("--json", dest="kao_json")
    ap.add_argument("--dosjei")
    ap.add_argument("--po-seriji", type=int, default=7)
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if args.po_seriji < 1:
        print("--po-seriji mora biti pozitivan cijeli broj.")
        return 2
    put = args.rad
    res, greska = analiza(put)
    print("=" * 62)
    print("INVENTAR TVRDNJI PO REFERENCI —", put)
    print("=" * 62)
    if greska:
        print(f"[DEKLARIRANA GRANICA — {greska}]")
        print("  Bez popisa literature tvrdnje se ne mogu vezati uz jedinice,")
        print("  pa faza D nema polazište. Provjeri naslov popisa.")
        return 3

    t = res["tvrdnje"]
    s_br = sorted(n for n in t if t[n]["brojcane"])
    s_op = sorted(n for n in t if not t[n]["brojcane"] and t[n]["opisne"])
    bez = sorted(n for n in t if not t[n]["brojcane"] and not t[n]["opisne"])
    print(f"stil citiranja: {res['stil']} | jedinica u popisu: {len(res['jedinice'])}")
    print(f"  s BROJČANOM tvrdnjom (prioritet faze D): {len(s_br)}")
    print(f"  samo s opisnom tvrdnjom:                 {len(s_op)}")
    print(f"  bez ijedne pronađene rečenice:           {len(bez)}"
          + (f"  ⚠ {bez}" if bez else "   ✓"))
    ukupno_br = sum(len(t[n]['brojcane']) for n in t)
    print(f"  ukupno rečenica s brojkama: {ukupno_br}")

    if args.kao_json:
        izlaz = args.kao_json
        with open(izlaz, "w", encoding="utf-8") as fh:
            json.dump({str(k): v for k, v in t.items()} | {"_jedinice": res["jedinice"]},
                      fh, ensure_ascii=False, indent=1)
        print(f"✔ JSON spremljen: {izlaz}")

    if args.dosjei:
        mapa_dir = args.dosjei
        po = args.po_seriji
        putovi = _dosjei(res, mapa_dir, po)
        print(f"✔ dosjea: {len(putovi)} u {mapa_dir}/ (po {po} referenci)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
