#!/usr/bin/env python3
"""Provjera dosljednosti citiranja — numerički stilovi: IEEE [N] i Vancouver (N).

Uporaba:  python3 check_citations.py rad.docx [ieee|vancouver]
          (bez drugog argumenta stil se bira iz teksta: (N) ovalne vs. [N] uglate)

Provjerava (oba stila):
  - definirane reference u LITERATURI (bez rupa u numeraciji)
  - siročad (referenca u popisu, ne citirana u tekstu)
  - citate bez reference
  - redoslijed prvog pojavljivanja (numerički stilovi numeriraju po pojavljivanju)

Samo Vancouver (v1.9):
  - decimale i tablične ćelije „158 (77,8)" NISU citati (v. common.vancouver_is_decimal)
  - razmak iza zareza: Vancouver traži „(67, 68)", ne „(67,68)"
  - raspon en-crticom „(3–7)", ne spojnicom „(3-7)"
  - citat PRIJE interpunkcije: „…skrbi (1)." a ne „…skrbi. (1)"
  - popis: „i sur."/„et al." nakon šest autora; stavka s više od šest autora bez toga
"""
import re
import sys
from common import (load_docx_text, load_supplementary_text, parse_citation_group,
                    parse_vancouver_citations, IEEE_CITE_RE, VANCOUVER_CITE_RE,
                    LIT_HEADING_RE, NUMBERED_ITEM_RE)


def _authors_count(item):
    """Broj autora u Vancouver stavci: prvi segment do točke, autori odvojeni zarezom
    („Knaul FM, Arreola-Ornelas H, Kwete XJ i sur. Naslov…"). Vraća (n, ima_i_sur)."""
    head = re.split(r"\.\s", item, maxsplit=1)[0]
    has_etal = bool(re.search(r"\b(?:i\s+sur|et\s+al)\b", head, re.I))
    head = re.sub(r"\b(?:i\s+sur|et\s+al)\b.*$", "", head, flags=re.I)
    parts = [p.strip() for p in head.split(",") if p.strip()]
    # autor = „Prezime Inicijali" — bar dvije riječi ili inicijali velikim slovima
    authors = [p for p in parts if re.match(r"^[A-ZČĆŽŠĐ][\w'’\-]+(?:\s+[A-ZČĆŽŠĐ][\w'’\-]*)*\s+[A-ZČĆŽŠĐ]{1,3}$", p)
               or re.match(r"^(?:van|von|de|del|di|da)\s+", p, re.I)]
    return len(authors), has_etal


def main(path, style=None):
    body, cells, _ = load_docx_text(path, include_tables=True)
    sup = load_supplementary_text(path)

    # LITERATURA split se radi SAMO na body tekstu — ćelije tablica i fusnote se
    # dodaju u "korišteno u tekstu" NAKON splita. Da se lijepe prije splita,
    # citat koji postoji samo u tablici/fusnoti pao bi iza LITERATURE i bio
    # lažno proglašen siročetom (a redak tablice koji počinje s "[5]" lažnom
    # referencom). Pretpostavka: sam popis literature je u body prozi (standard).
    m = list(LIT_HEADING_RE.finditer(body))
    if m:
        split = m[-1].end()
    else:
        # fallback: prvi red koji počinje s [1] ili „1. Velikoslovo"
        mm = re.search(r"(?m)^\s*(?:\[1\]|1[.)])\s+[A-ZČĆŠŽĐ]", body)
        split = mm.start() if mm else len(body)
    lit = body[split:]
    # popis završava na sljedećem verzalnom naslovu („9. PRILOZI", „ŽIVOTOPIS")
    end = re.search(r"(?m)^\s*(?:\d{1,2}\.\s+)?[A-ZČĆŽŠĐ][A-ZČĆŽŠĐ ]{3,}$", lit)
    trailing = ""
    if end:
        lit, trailing = lit[:end.start()], lit[end.start():]
    used_text = "\n".join([body[:split], trailing, "\n".join(cells),
                           sup["footnotes"], sup["endnotes"]])

    if style not in ("ieee", "vancouver"):
        n_v = len(parse_vancouver_citations(body[:split]))
        n_i = len(IEEE_CITE_RE.findall(body[:split]))
        style = "vancouver" if n_v > n_i else "ieee"

    # Stavke popisa: „[N] …", „N. …" ili „N) …". IEEE popis je po pravilu „[N]",
    # pa se ondje „N." stavke uzimaju tek ako uglatih nema (inače bi „2. izd."
    # usred reference postalo lažna stavka).
    items = {}
    dupl = []
    for mm in NUMBERED_ITEM_RE.finditer(lit):
        n = int(mm.group(1) or mm.group(2))
        if style == "ieee" and mm.group(2) is None:
            continue
        if n in items:
            dupl.append(n)
        items[n] = mm.group(3).strip()
    if style == "ieee" and not items:
        for mm in NUMBERED_ITEM_RE.finditer(lit):
            items[int(mm.group(1) or mm.group(2))] = mm.group(3).strip()
    defined = sorted(items)
    if not defined and style == "ieee":
        # popis možda nije na početku retka
        defined = sorted(set(int(n) for n in re.findall(r"\[(\d+)\]\s+[A-ZČĆŠŽĐ]", lit)))

    cited = set()
    first_order = []
    year_like = set()
    no_space, hyphen_range, after_punct = [], [], []
    if style == "vancouver":
        for pos, inner, nums in parse_vancouver_citations(used_text):
            if re.search(r"\d,\d", inner):
                no_space.append(inner)
            if re.search(r"\d\s*-\s*\d", inner):
                hyphen_range.append(inner)
            # citat iza interpunkcije: „…skrbi. (1)" / „…skrbi, (1)"
            before = used_text[max(0, pos - 3):pos]
            if re.search(r"[.,;:]\s*$", before):
                after_punct.append(used_text[max(0, pos - 30):pos + len(inner) + 2].replace("\n", " "))
            for k in sorted(nums):
                cited.add(k)
                if k not in first_order:
                    first_order.append(k)
    else:
        for mm in re.finditer(r"\[([0-9][0-9,\s–\-]*)\]", used_text):
            for k in sorted(parse_citation_group(mm.group(1))):
                if k > 999:
                    # [2020] i sl. je gotovo sigurno godina u uglatoj zagradi, ne
                    # citat (nijedan rad nema 1000+ referenci) — ne broji se kao
                    # citat, ali se prijavi da se ručno provjeri o čemu se radi.
                    year_like.add(k)
                    continue
                cited.add(k)
                if k not in first_order:
                    first_order.append(k)

    label = "Vancouver (N)" if style == "vancouver" else "IEEE [N]"
    print("=" * 56)
    print(f"CITIRANJE [{label}] —", path)
    print("=" * 56)
    if defined:
        print(f"Definirano u LITERATURI: {len(defined)}  (raspon {min(defined)}–{max(defined)})")
        gaps = [i for i in range(min(defined), max(defined) + 1) if i not in defined]
        print(f"  {'⚠ rupe u numeraciji' if gaps else 'rupe u numeraciji'}: {gaps or 'nema'}")
        if dupl:
            print(f"  ⚠ dvostruki brojevi u popisu: {sorted(set(dupl))}")
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
            print(f"  ⚠ krši rastući redoslijed ({label}) na {len(viol)} mjesta — "
                  f"ili prenumeriraj, ili objasni tematsko grupiranje u metodologiji.")
        else:
            print("  ✓ prati redoslijed pojavljivanja")

    if style == "vancouver":
        print("\nVancouver stil (savjetodavno, ne blokira):")
        if no_space:
            print(f"  ⚠ bez razmaka iza zareza — Vancouver traži „(67, 68)\": {len(no_space)}× npr. {no_space[:6]}")
        else:
            print("  ✓ razmak iza zareza u višestrukim citatima")
        if hyphen_range:
            print(f"  ⚠ raspon spojnicom umjesto en-crtice „(3–7)\": {len(hyphen_range)}× npr. {hyphen_range[:6]}")
        else:
            print("  ✓ rasponi en-crticom (ili ih nema)")
        if after_punct:
            print(f"  ⚠ citat IZA interpunkcije (treba „…skrbi (1).\"): {len(after_punct)}× npr. {after_punct[:3]}")
        else:
            print("  ✓ citati stoje prije interpunkcije")
        too_many = []
        for n, t in sorted(items.items()):
            cnt, etal = _authors_count(t)
            if cnt > 6 and not etal:
                too_many.append(n)
        if too_many:
            print(f"  ⚠ popis: više od 6 autora bez „i sur.\"/„et al.\": stavke {too_many[:10]}")
        elif items:
            print("  ✓ popis: „i sur.\" nakon šest autora (ili nema stavki s >6 autora)")

    ok = bool(defined) and not orphans and not undefined
    print("\nREZULTAT:", "✓ interno konzistentno" if ok else "⚠ ima nalaza (v. gore)")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
