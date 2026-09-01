#!/usr/bin/env python3
"""Provjera dosljednosti citiranja (numerički/IEEE stil [N]).

Uporaba:  python3 check_citations.py rad.docx

Provjerava:
  - definirane reference u LITERATURI (bez rupa u numeraciji)
  - siročad (referenca u popisu, ne citirana u tekstu)
  - citate bez reference
  - redoslijed prvog pojavljivanja (IEEE)
"""
import re
import sys
from common import load_docx_text, load_supplementary_text, parse_citation_group


def main(path):
    body, cells, _ = load_docx_text(path, include_tables=True)
    sup = load_supplementary_text(path)

    # LITERATURA split se radi SAMO na body tekstu — ćelije tablica i fusnote se
    # dodaju u "korišteno u tekstu" NAKON splita. Da se lijepe prije splita,
    # citat koji postoji samo u tablici/fusnoti pao bi iza LITERATURE i bio
    # lažno proglašen siročetom (a redak tablice koji počinje s "[5]" lažnom
    # referencom). Pretpostavka: sam popis literature je u body prozi (standard).
    m = list(re.finditer(
        r"(?im)^\s*(?:\d+\.?\s*)?"
        r"(LITERATURA|POPIS LITERATURE|REFERENCE|BIBLIOGRAFIJA|POPIS IZVORA|IZVORI)\s*$",
        body))
    if m:
        split = m[-1].end()
    else:
        # fallback: prvi red koji počinje s [1]
        mm = re.search(r"(?m)^\s*\[1\]", body)
        split = mm.start() if mm else len(body)
    lit = body[split:]
    used_text = "\n".join([body[:split], "\n".join(cells),
                            sup["footnotes"], sup["endnotes"]])

    defined = sorted(set(int(n) for n in re.findall(r"(?m)^\s*\[(\d+)\]", lit)))
    if not defined:
        # popis možda nije na početku retka
        defined = sorted(set(int(n) for n in re.findall(r"\[(\d+)\]\s+[A-ZČĆŠŽĐ]", lit)))

    cited = set()
    first_order = []
    year_like = set()
    for mm in re.finditer(r"\[([0-9][0-9,\s–\-]*)\]", used_text):
        for k in parse_citation_group(mm.group(1)):
            if k > 999:
                # [2020] i sl. je gotovo sigurno godina u uglatoj zagradi, ne
                # citat (nijedan rad nema 1000+ referenci) — ne broji se kao
                # citat, ali se prijavi da se ručno provjeri o čemu se radi.
                year_like.add(k)
                continue
            cited.add(k)
            if k not in first_order:
                first_order.append(k)

    print("=" * 56)
    print("CITIRANJE —", path)
    print("=" * 56)
    if defined:
        print(f"Definirano u LITERATURI: {len(defined)}  (raspon {min(defined)}–{max(defined)})")
        gaps = [i for i in range(min(defined), max(defined) + 1) if i not in defined]
        print(f"  {'⚠ rupe u numeraciji' if gaps else 'rupe u numeraciji'}: {gaps or 'nema'}")
    else:
        print("⚠ Definirano u LITERATURI: (nije prepoznat popis — provjeri ručno)")

    print(f"Citirano u tekstu (uklj. tablice/fusnote/endnote): {len(cited)}")
    if year_like:
        print(f"  ⚠ uglata zagrada s brojem >999 (vjerojatno godina, NE citat — provjeri ručno): {sorted(year_like)}")
    orphans = [d for d in defined if d not in cited]
    undefined = [c for c in sorted(cited) if c not in defined]
    print(f"  {'⚠ SIROČAD' if orphans else 'SIROČAD'} (u popisu, ne citirano): {orphans or 'nema'}")
    print(f"  {'⚠ CITAT BEZ REFERENCE' if undefined else 'CITAT BEZ REFERENCE'}: {undefined or 'nema'}")

    # redoslijed pojavljivanja
    viol = []
    mx = 0
    for n in first_order:
        if n < mx:
            viol.append(n)
        mx = max(mx, n)
    if defined:
        print(f"\nRedoslijed prvog pojavljivanja: {first_order[:12]}{' …' if len(first_order) > 12 else ''}")
        if viol:
            print(f"  ⚠ krši rastući redoslijed (IEEE) na {len(viol)} mjesta — "
                  f"ili prenumeriraj, ili objasni tematsko grupiranje u metodologiji.")
        else:
            print("  ✓ prati redoslijed pojavljivanja")

    ok = defined and not orphans and not undefined
    print("\nREZULTAT:", "✓ interno konzistentno" if ok else "⚠ ima nalaza (v. gore)")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
