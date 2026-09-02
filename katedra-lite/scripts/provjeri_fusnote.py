#!/usr/bin/env python3
"""Disciplina fusnota — za radove koji citiraju u fusnoti.

Zašto postoji
-------------
`citation_dialects.py` poznaje `legal-footnote`, `check_citations` skenira fusnote
za citate. Ali **disciplinu fusnote nije provjeravao nitko**: prvo puni pa
skraćeni oblik, `ibid.` samo uz neposredno prethodnu fusnotu, kontinuitet
numeracije, i razrješava li se fusnotni citat u popisu literature.

Za pravne radove to je središnje. Libertas profil **izrijekom traži fusnote** kod
izravnog citata, netrivijalnog činjeničnog iskaza i parafraze, a njegova napomena
već bilježi da je Pravilnik u tome interno nedosljedan.

Što se mjeri
------------
Ono što se dade odlučiti iz slijeda fusnota: red pojavljivanja punog i skraćenog
oblika, upotreba `ibid.`/`nav. dj.`/`op. cit.`, praznine u numeraciji, i pogađa li
prezime iz fusnote ijednu jedinicu u popisu literature.

Što se NE mjeri
---------------
Je li fusnota **trebala** postojati. Pravilo „izravan citat ide u fusnotu” traži
razumijevanje teksta, ne slijeda fusnota — to ostaje čovjeku i profilu.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SKRIPTE = os.path.dirname(os.path.abspath(__file__))
if SKRIPTE not in sys.path:
    sys.path.insert(0, SKRIPTE)

import hr_text as H  # noqa: E402

OK, UPOZ, LOSE, PRESKOK = "✅", "⚠️", "❌", "➖"

IBID = re.compile(r"\b(ibid\.?|ibidem|isto\b|na\s+istom\s+mjestu)", re.IGNORECASE)
SKRACENO = re.compile(r"\b(nav\.\s*dj\.|op\.\s*cit\.|cit\.\s*dj\.)", re.IGNORECASE)
# Puni oblik: prezime + inicijal/ime, pa naslov ili nakladnik — barem dvije sastavnice
PUNI = re.compile(r"^[^\s,]{3,},\s*[A-ZČĆŽŠĐ][^,]{0,40},.*\d{4}", re.IGNORECASE)
PREZIME = re.compile(r"^\s*([^\s,.]{3,})[,.]")
PROPIS = re.compile(r"(?i)^\s*(narodne novine|nn\b|zakon|pravilnik|uredba|odluka|"
                    r"ustav|direktiva|čl\.|članak)")


def fusnote(put):
    """[(broj, tekst)] iz .docx-a, redoslijedom pojavljivanja."""
    if not put.endswith(".docx"):
        raise ValueError("očekuje se .docx — fusnote se u markdownu ne vide")
    import zipfile
    from xml.etree import ElementTree as ET
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    out = []
    with zipfile.ZipFile(put) as z:
        if "word/footnotes.xml" not in z.namelist():
            return out
        korijen = ET.fromstring(z.read("word/footnotes.xml"))
        for fn in korijen.findall(f"{W}footnote"):
            vrsta = fn.get(f"{W}type")
            if vrsta in ("separator", "continuationSeparator",
                         "continuationNotice"):
                continue
            bid = fn.get(f"{W}id")
            tekst = "".join(t.text or "" for t in fn.iter(f"{W}t")).strip()
            if tekst:
                try:
                    out.append((int(bid), tekst))
                except (TypeError, ValueError):
                    continue
    out.sort(key=lambda x: x[0])
    return out


def literatura_prezimena(put):
    try:
        import docx
        d = docx.Document(put)
    except Exception:  # noqa: BLE001
        return set()
    u, prez = False, set()
    for p in d.paragraphs:
        t = (p.text or "").strip()
        if not t:
            continue
        if H.NASLOV_LIT.match(t):
            u = True
            continue
        if u and len(t) > 15:
            m = PREZIME.match(t)
            if m:
                prez.add(H.bez_dijakritika(m.group(1)).lower())
    return prez


def provjeri(put):
    fn = fusnote(put)
    nalazi = []

    def dodaj(stanje, pravilo, poruka, gdje=""):
        nalazi.append({"pravilo": pravilo, "stanje": stanje,
                       "poruka": poruka, "gdje": gdje})

    if not fn:
        return {"fusnota": 0, "nalazi": [], "prazno": True}

    brojevi = [b for b, _ in fn]
    ocekivani = list(range(min(brojevi), min(brojevi) + len(brojevi)))
    if brojevi != ocekivani:
        rupe = sorted(set(ocekivani) - set(brojevi))
        dodaj(LOSE, "numeracija",
              f"prekid u numeraciji fusnota: nedostaju {rupe[:8]}",
              f"{len(fn)} fusnota, od {min(brojevi)} do {max(brojevi)}")

    # ibid. u prvoj fusnoti, ili iza fusnote koja nije bibliografska
    prvi_puni = {}
    for i, (b, t) in enumerate(fn):
        ib = bool(IBID.match(t.strip()))
        sk = bool(SKRACENO.search(t))
        if ib and i == 0:
            dodaj(LOSE, "ibid_prva",
                  "„ibid.” u PRVOJ fusnoti — nema na što upućivati", f"fn {b}")
        elif ib:
            _pb, pt = fn[i - 1]
            if IBID.match(pt.strip()):
                dodaj(UPOZ, "ibid_lanac",
                      "„ibid.” iza „ibid.” — lanac je legitiman, ali nakon dva "
                      "koraka čitatelj gubi trag; ponovi skraćeni oblik",
                      f"fn {b}")
        if sk or (not ib and not sk):
            m = PREZIME.match(t)
            if not m or PROPIS.match(t):
                continue
            klj = H.bez_dijakritika(m.group(1)).lower()
            puni = bool(PUNI.match(t))
            if klj not in prvi_puni:
                prvi_puni[klj] = (b, puni)
                if sk and not puni:
                    dodaj(LOSE, "skraceno_prvo",
                          f"skraćeni oblik („{m.group(1)}, nav. dj.”) prije nego "
                          f"je izvor ijednom naveden u punom obliku", f"fn {b}")
            elif puni and prvi_puni[klj][1]:
                dodaj(UPOZ, "puni_ponovljen",
                      f"puni oblik za „{m.group(1)}” ponovljen (prvi put u fn "
                      f"{prvi_puni[klj][0]}) — dalje ide skraćeni", f"fn {b}")

    # razrješava li se fusnotni citat u popisu literature
    prez_lit = literatura_prezimena(put)
    if prez_lit:
        siroci = []
        for b, t in fn:
            if IBID.match(t.strip()) or PROPIS.match(t):
                continue
            m = PREZIME.match(t)
            if not m:
                continue
            klj = H.bez_dijakritika(m.group(1)).lower()
            if klj not in prez_lit and len(klj) > 3:
                siroci.append((b, m.group(1)))
        if siroci:
            dodaj(LOSE, "siroce",
                  f"{len(siroci)} fusnota upućuje na izvor kojega nema u popisu "
                  f"literature",
                  "; ".join(f"fn {b}: {p}" for b, p in siroci[:6]))
    else:
        dodaj(PRESKOK, "popis",
              "popis literature nije nađen — razrješavanje fusnota nije "
              "provjereno")

    return {"fusnota": len(fn), "nalazi": nalazi, "prazno": False,
            "raspon": f"{min(brojevi)}–{max(brojevi)}"}


def ispisi(r):
    print("FUSNOTE — disciplina navođenja")
    print("=" * 30)
    if r.get("prazno"):
        print(f"{PRESKOK} dokument nema fusnota — nema što provjeriti.")
        print("   Ako profil traži fusnote kod izravnog citata (npr. Libertas),")
        print("   to je nalaz za check_rules, ne za ovaj alat.")
        return
    print(f"  {r['fusnota']} fusnota ({r['raspon']})\n")
    if not r["nalazi"]:
        print(f"{OK} disciplina navođenja je uredna")
    for n in r["nalazi"]:
        print(f"{n['stanje']} {n['poruka']}")
        if n["gdje"]:
            print(f"     {n['gdje']}")
    lose = sum(1 for n in r["nalazi"] if n["stanje"] == LOSE)
    print(f"\n{lose} kršenja")
    print("Je li fusnota TREBALA postojati alat ne zna — to traži razumijevanje")
    print("teksta i stoji u profilu fakulteta.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Disciplina fusnota u .docx-u.")
    ap.add_argument("rad")
    ap.add_argument("--json", dest="kao_json", metavar="PUT")
    args = ap.parse_args(argv)
    if not os.path.exists(args.rad):
        print(f"❌ nema datoteke: {args.rad}", file=sys.stderr)
        return 2
    try:
        r = provjeri(args.rad)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"❌ provjera nije uspjela: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    ispisi(r)
    if args.kao_json:
        with open(args.kao_json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    return 1 if any(n["stanje"] == LOSE for n in r["nalazi"]) else 0


if __name__ == "__main__":
    sys.exit(main())
