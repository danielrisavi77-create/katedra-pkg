#!/usr/bin/env python3
"""Inventar brojčanih tvrdnji + kandidati za sukob vrijednosti.

Uporaba:
  python3 numbers_inventory.py rad.docx
  python3 numbers_inventory.py rad.docx --domain elektro   (preskoči auto-detekciju)
  python3 numbers_inventory.py rad.docx --domain generic   (frekvencijski fallback)

Radi tri stvari:
  1. grupira sve "broj + jedinica" po jedinici (inventar za pregled),
  2. ispiše rečenice u kojima se domenski pojam veže uz broj,
  3. za svaki domenski pojam usporedi vrijednosti kroz rad — isti pojam s
     VIŠE RAZLIČITIH vrijednosti iste jedinice = kandidat za nesklad koji
     rad možda ne pomiruje (⚠, provjeri ručno je li razlika deklarirana).
Domena se auto-detektira iz sadržaja (v. domains/__init__.py); --domain
override. Ne zamjenjuje ručnu provjeru — daje popis za pregled.
"""
import re
import sys
from collections import defaultdict
from common import load_docx_text, sentences
from domains import DOMAINS, UNIT_ALTERNATION, detect_domain, generic_keywords


def main(path, domain_override=None):
    body, cells, _ = load_docx_text(path)
    text = body + "\n" + "\n".join(cells)

    if domain_override:
        domain, scores = domain_override, {}
    else:
        domain, scores = detect_domain(text)

    print("=" * 56)
    print("BROJČANI INVENTAR —", path)
    print("=" * 56)
    if scores:
        print(f"domena (auto-detekcija): {domain}  —  {DOMAINS[domain]['label']}  (bodovi: {scores})")
    else:
        print(f"domena: {domain}  —  {DOMAINS.get(domain, {}).get('label', '?')}")

    if domain == "generic" or not DOMAINS[domain]["keywords"]:
        KEYWORDS = generic_keywords(text)
        if KEYWORDS:
            print(f"(generički fallback — riječi učestale uz brojeve: {KEYWORDS})")
        else:
            print("(generički fallback nije našao dovoljno ponavljajućih pojmova uz brojeve)")
    else:
        KEYWORDS = DOMAINS[domain]["keywords"]

    # jedinstvena regex granica: (?!\w), NE \b — iza ne-word znaka (%, °)
    # \b zahtijeva word znak poslije, pa "45 %" i "10°" nikad ne bi matchali
    unit_re = re.compile(r"(\d+(?:,\d+)?)\s?(" + UNIT_ALTERNATION + r")(?!\w)")

    # 1) grupiranje broj+jedinica
    by_unit = defaultdict(set)
    for m in unit_re.finditer(text):
        by_unit[m.group(2)].add(m.group(1))
    print("\nVrijednosti po jedinici:")
    for u, vals in sorted(by_unit.items()):
        vv = sorted(vals, key=lambda s: float(s.replace(",", ".")))
        print(f"  {u:5}: {', '.join(vv)}")

    # 2) rečenice s domenskim pojmom + brojem (bez skrivenih dodatnih filtera —
    #    stara verzija je gejtala na "izvješć|projekt|…" pa je izvan originalnog
    #    čelik-workflowa sekcija uvijek bila prazna); spomen izvora se samo označi
    print("\nRečenice s ključnim pojmom + brojem:")
    seen = 0
    for s in sentences(text):
        if re.search(r"\d", s) and any(k in s.lower() for k in KEYWORDS):
            tag = "  [spominje izvor]" if re.search(r"izvješć|projekt|seminar|nacrt", s.lower()) else ""
            print("  •", s[:120] + tag)
            seen += 1
        if seen >= 25:
            print("  … (skraćeno)")
            break
    if not seen:
        print("  (nema — ili rad nema brojeva uz domenske pojmove, ili domena nije dobro pogođena)")

    # 3) kandidati za sukob: isti pojam s ≥2 različite vrijednosti iste jedinice
    kw_vals = defaultdict(lambda: defaultdict(set))
    for s in sentences(text):
        sl = s.lower()
        for k in KEYWORDS:
            if k in sl:
                for m in unit_re.finditer(s):
                    kw_vals[k][m.group(2)].add(m.group(1))
    conflicts = []
    for k, units in sorted(kw_vals.items()):
        for u, vals in sorted(units.items()):
            if len(vals) >= 2:
                vv = sorted(vals, key=lambda x: float(x.replace(",", ".")))
                conflicts.append((k, u, vv))
    print("\nKandidati za sukob (isti pojam, više vrijednosti iste jedinice):")
    if conflicts:
        for k, u, vv in conflicts:
            print(f"  ⚠ '{k}' + {u}: {', '.join(vv)}  — provjeri je li razlika deklarirana u radu")
    else:
        print("  nema")

    print("\nPODSJETNIK — ručno provjeri aritmetiku koja se DA izračunati:")
    print("  površina = Σ(a×b) ?   |   Σ(paneli×pokrivna širina) = površina krova ?")
    print("  (broj okvira−1)×raster ≈ duljina ?   |   broj stupova/greda vs broj okvira ?")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    dom = None
    if "--domain" in sys.argv:
        dom = sys.argv[sys.argv.index("--domain") + 1]
        if dom not in DOMAINS:
            print(f"Nepoznata domena '{dom}'. Dostupno: {list(DOMAINS)}")
            sys.exit(2)
    sys.exit(main(sys.argv[1], dom))


# ---------------------------------------------------------------- v1.3 zbroj kategorija
import re as _re

RE_UKUPNO = _re.compile(
    r"(\b(?:ukupno|svega|od (?:toga|ukupno)|N\s*=)\b[^.]{0,40}?|\b)(\d{2,6})\b[^.]{0,60}?"
    r"(?:optuž|predmet|slučaj|ispitanik|jedinic|osob)", _re.IGNORECASE | _re.UNICODE)


def zbroj_kategorija(recenice: list[str], tolerancija: int = 0) -> list[dict]:
    """Nađi mjesta gdje niz kategorija tvori cjelinu i provjeri IZVOR, ne samo zbroj.

    Pravilo 15 (Katedra): zbroj koji izlazi nije dokaz. Kategorija izvedena oduzimanjem od
    ukupnoga broja je izvedena vrijednost i mora nositi [TREBA IZVOR], pa makar zbroj bio točan.

    Nastalo iz ciklusa u kojemu je jedna kategorija bila podignuta s 19 na 21 upravo toliko da
    zbroj izađe na 161 nakon što je peta kategorija ispuštena. Provjera „zbrajaju li se" i
    provjera „daju li postoci 100 %" obje su prošle.
    """
    nalazi = []
    for r in recenice:
        brojevi = [int(x) for x in _re.findall(r"(?<![\w.,])(\d{1,6})(?![\w])", r)]
        if len(brojevi) < 4:
            continue
        ukupno = max(brojevi)
        ostali = [b for b in brojevi if b != ukupno]
        if len(ostali) < 3:
            continue
        for izostavi in range(-1, len(ostali)):
            skup = [b for i, b in enumerate(ostali) if i != izostavi]
            if abs(sum(skup) - ukupno) <= tolerancija and len(skup) >= 3:
                uputnica = bool(_re.search(r"\([^)]*\d{4}[^)]*\)", r))
                nalazi.append({
                    "vrsta": "ZBROJ_KATEGORIJA",
                    "ukupno": ukupno,
                    "kategorije": skup,
                    "ima_uputnicu": uputnica,
                    "poruka": ("skup kategorija tvori cjelinu; provjeri da SVAKA kategorija ima "
                               "vlastitu uputnicu i da sve dolaze iz ISTOGA izvora s navedenim "
                               "danom presjeka. Kategorija izvedena oduzimanjem nosi "
                               "[TREBA IZVOR] i kad se zbroj slaže."),
                    "recenica": r.strip()[:200],
                })
                break
    return nalazi
