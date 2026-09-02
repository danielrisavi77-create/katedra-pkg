#!/usr/bin/env python3
"""Provjera dosljednosti citiranja — AUTOR-GODINA stil (APA/Harvard), npr. (Ivić, 2020).

Uporaba:  python3 check_citations_authoryear.py rad.docx

Za numerički IEEE [N] stil koristi check_citations.py. Ako nisi siguran koji
stil rad koristi, `audit_all.py` ga auto-detektira (common.detect_citation_style)
i pokreće odgovarajuću skriptu.

VAŽNA NAPOMENA — ovo je heuristika, ne egzaktna provjera kao kod IEEE brojeva:
  Usporedba ide po ključu (PRVI autor prezime, godina), ne po punom popisu
  autora niti punom nazivu. To znači:
  - dvije različite reference istog prvog autora u istoj godini bez slovnog
    sufiksa (2020a/2020b) mogu se stopiti u isti ključ — provjeri ručno;
  - "Ivić i Perić, 2020" i "Ivić i dr., 2020" dijele isti ključ (ivić, 2020)
    što je namjerno pojednostavljenje;
  - jako neuobičajeni formati reference (obrnuti redoslijed, brojčana lista
    unutar autor-godina teksta) možda se neće ispravno parsirati.
Rezultat čitaj kao POPIS ZA RUČNU PROVJERU, ne kao konačnu presudu.

Provjerava:
  - popis referenci (LITERATURA/POPIS LITERATURE/...) -> (prezime, godina) parovi
  - citate u tekstu, UKLJUČUJUĆI fusnote/endnote (učestalo mjesto autor-godina
    citata u humanističkim/društvenim radovima) -> (prezime, godina) parovi
  - siročad (referenca u popisu, ne citirana) i citat bez reference
"""
import re
import sys
import common as C
from common import (load_docx_text, load_supplementary_text, CITE_AY_RE,
                    parse_ay_citation_group, parse_ay_narrative)

HEADING_RE = re.compile(
    r"(?im)^\s*(?:\d+\.?\s*)?"
    r"(LITERATURA|POPIS LITERATURE|REFERENCE|BIBLIOGRAFIJA|POPIS IZVORA|IZVORI)\s*$"
)

# Redak reference: "Prezime, I. (2020). Naslov..." / "Prezime I. (2020) Naslov..."
# Pravni oblik tvrtke piše se malim slovom i stoji IZA imena („easyJet plc",
# „Jet2 plc", „Podravka d.d."). Uzorak je tražio velika početna slova u svakoj
# riječi, pa je stao na imenu i nije stigao do godine — takav redak popisa
# literature ostao je bez ključa, a citat u tekstu postao lažno „citat bez
# reference". Nađeno mjerenjem na stvarnom radu, nije bilo u prijavi.
_OBLIK_TVRTKE = (r"(?:plc|inc|ltd|llc|corp|co|gmbh|ag|sa|nv|bv|spa|oyj|ab|as|kg|"
                 r"d\.\s?d\.|d\.\s?o\.\s?o\.|j\.\s?d\.\s?o\.\s?o\.)")
# Ime institucije mora sadržavati barem jedno veliko slovo („easyJet", „TUI",
# „Jet2"), inače bi uzorak hvatao obične rečenice u popisu.
BIBLIO_INST_RE = re.compile(
    r"^[•\-\d\.\)\s]*((?=[\w&\-]*[A-ZČĆŠŽĐ])[\w&\-]+"
    r"(?:\s+(?:[A-ZČĆŠŽĐ][\w&\-]*|" + _OBLIK_TVRTKE + r")){0,3})"
    # Institucionalni autor često nosi raspis kratice prije godine:
    # „HNB (Hrvatska narodna banka) (2023)". Bez ovoga takav redak nema ključ.
    r"(?:\s*\([^)]{3,80}\))?"
    r"[,\s]*\(?(\d{4})\.?[a-z]?\)?",
    re.IGNORECASE | re.UNICODE,
)
# Uzorak je tražio INICIJAL („Prezime, I. (2007)"), a FPZG Upute traže PUNO IME
# („Prezime, Ime (2007)"). Zbog toga cijeli popis literature u FPZG obliku nije
# prolazio raščlambu i svaki citat u tekstu ispadao je siroče. Uz to nije poznavao
# čestice u prezimenu („Van der Zwan, Natascha") ni institucionalne autore s
# raspisom („HNB (Hrvatska narodna banka) (2023)").
BIBLIO_LINE_RE = re.compile(
    r"^[•\-\d\.\)\s]*"
    r"((?:(?:van|von|de|del|della|di|da|dos|der|den|la|le|ten|ter)\s+)*"
    r"[A-ZČĆŠŽĐ][\wčćžšđ\-]+(?:\s+[A-ZČĆŠŽĐ][\wčćžšđ\-]+){0,2})"
    r"\s*,\s*"
    r"(?:[A-ZČĆŠŽĐ]\.(?:\s*[A-ZČĆŠŽĐ]\.)*|[A-ZČĆŠŽĐ][\wčćžšđ\-]+)"
    r"\s*.{0,120}?\(?(\d{4}[a-z]?)\)?",
    re.IGNORECASE | re.UNICODE,
)


def extract_biblio_keys(lit_text):
    keys = set()
    unmatched = 0
    for line in lit_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = BIBLIO_LINE_RE.match(line)
        if m:
            # Ključ ide kroz ZAJEDNIČKI `kljuc_prezimena`, isti koji koriste oba
            # parsera citata u tekstu. Dok je svaka strana gradila ključ po svome,
            # „Van der Zwan" je iz teksta bio „van", a iz popisa „zwan".
            keys.add((C.kljuc_prezimena(m.group(1)), m.group(2).lower()))
        elif BIBLIO_INST_RE.match(line) and re.search(r"\(\d{4}", line):
            mi = BIBLIO_INST_RE.match(line)
            keys.add((C.kljuc_prezimena(mi.group(1)), mi.group(2).lower()))
        elif re.search(r"\d{4}", line) and len(line) > 15:
            unmatched += 1
    return keys, unmatched



def _osnova(prezime):
    """Skini hrvatske padežne nastavke: Albersa→Albers, Faulkneru→Faulkner."""
    for n in ("ovima", "ima", "ova", "ove", "ovi", "om", "ju", "u", "a", "e", "i"):
        if prezime.endswith(n) and len(prezime) - len(n) >= 4:
            yield prezime[: -len(n)]
    yield prezime


def uskladi_kljuceve(citirani, definirani):
    """Vrati (siročad, citat_bez_reference) uz toleranciju na hrvatsku sklonidbu,
    višečlana prezimena i institucionalne autore.

    Bez ovoga svaki narativni citat u kosom padežu ("Albersa i Rundshagena
    (2020.)") izgleda kao citat bez reference, a referenca kao siroče."""
    def slaze(c, d):
        if c[1] != d[1]:
            return False
        a, b = c[0], d[0]
        if a == b:
            return True
        if len(a) >= 4 and len(b) >= 4 and (a.startswith(b) or b.startswith(a)):
            return True
        return any(o == b for o in _osnova(a)) or any(o == a for o in _osnova(b))

    siroces = {d for d in definirani if not any(slaze(c, d) for c in citirani)}
    bez_ref = {c for c in citirani if not any(slaze(c, d) for d in definirani)}
    return siroces, bez_ref


def main(path):
    body, cells, _ = load_docx_text(path, include_tables=True)
    sup = load_supplementary_text(path)

    # Split na LITERATURU SAMO po body tekstu; ćelije tablica i fusnote/endnote
    # se dodaju u "korišteno u tekstu" NAKON splita. (Da se lijepe prije splita,
    # fusnote bi UVIJEK pale iza naslova literature — koji je u body-ju — pa
    # citati u fusnotama nikad ne bi bili viđeni, što je točno slučaj zbog
    # kojeg fusnote i čitamo.)
    m = list(HEADING_RE.finditer(body))
    split = m[-1].end() if m else len(body)
    lit = body[split:]
    used_text = "\n".join([body[:split], "\n".join(cells),
                            sup["footnotes"], sup["endnotes"]])

    defined, unmatched_lines = extract_biblio_keys(lit)
    cited = set()
    for inner in CITE_AY_RE.findall(used_text):
        cited |= parse_ay_citation_group(inner)
    # narativni oblik — u hrvatskim radovima najčešći
    zagradnih = len(cited)
    cited |= parse_ay_narrative(used_text)
    print(f"  (zagradnih ključeva: {zagradnih}, "
          f"narativnih dodatno: {len(cited) - zagradnih})")

    print("=" * 60)
    print("CITIRANJE (autor-godina, heuristika) —", path)
    print("=" * 60)
    if not m:
        print("⚠ Naslov popisa literature nije prepoznat (LITERATURA/POPIS LITERATURE/...) "
              "— cijeli tekst je tretiran kao 'korišten u tekstu', rezultat je nepouzdan.")
    if not defined:
        print("⚠ Nijedna referenca u popisu nije prepoznata u autor-godina formatu — "
              "provjeri je li ovo doista APA/Harvard stil (ili je popis drukčije formatiran).")
    if unmatched_lines:
        print(f"({unmatched_lines} redaka u popisu literature sadrži godinu ali nije prepoznato "
              f"kao 'Prezime, I. (GODINA)' — pregledaj ručno format)")

    print(f"\nDefinirano u popisu literature (prezime+godina): {len(defined)}")
    print(f"Citirano u tekstu (uklj. fusnote/endnote): {len(cited)}")
    if sup["footnotes"] or sup["endnotes"]:
        print(f"  (od toga u fusnotama/endnotama: {len(sup['footnotes']) + len(sup['endnotes'])} znakova teksta pretraženo)")

    _sir, _bez = uskladi_kljuceve(cited, defined)
    orphans, undefined = sorted(_sir), sorted(_bez)
    print(f"\n  {'⚠ SIROČAD' if orphans else 'SIROČAD'} (u popisu, ne citirano): {orphans or 'nema'}")
    print(f"  {'⚠ CITAT BEZ REFERENCE' if undefined else 'CITAT BEZ REFERENCE'}: {undefined or 'nema'}")

    print("\n⚠ HEURISTIKA — ključ je (prvi autor, godina), ne pun popis autora/naslov.")
    print("  Prije zaključka ručno provjeri: duple godine istog prvog autora (2020a/2020b),")
    print("  'i dr.'/'et al.' grupe, i retke koje regex nije prepoznao (v. gore).")

    ok = defined and not orphans and not undefined and bool(m)
    print("\nREZULTAT:", "✓ interno konzistentno (uz gornju napomenu)" if ok else "⚠ ima nalaza / potrebna ručna provjera")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))


# ---------------------------------------------------------------- v1.3 pin-cite nalazi
# Tri nalaza iz stvarnoga ciklusa (FPZG, kolovoz 2026.). Sva tri prošla su postojeću
# provjeru zatvorenosti skupa (15 jedinica, 15 ključeva, 0 siročadi) jer ona gleda
# POSTOJI li referenca, a ne pokriva li stranica tvrdnju.
RE_JEDINICA_RASPON = re.compile(r"(\d{1,4})\s*[–-]\s*(\d{1,4})\s*\.?\s*$")


def _raspon_jedinice(redak: str):
    """Iz retka popisa literature izvuci raspon stranica jedinice, ako ga ima."""
    m = RE_JEDINICA_RASPON.search(redak.strip())
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return (a, b) if b > a else None


def pin_cite_nalazi(citati, jedinice_redci):
    """citati: [(kljuc, stranica_str, kontekst)] · jedinice_redci: {kljuc: redak_popisa}

    Vraća listu nalaza:
      PIN_CITE_RASPON     stranica u citatu = cijeli raspon jedinice („negdje u ovom tekstu")
      PIN_CITE_RUB        stranica je prva ili zadnja stranica jedinice
      PIN_CITE_PONOVLJEN  isti (autor, godina, stranica) uz dvije različite tvrdnje
    """
    nalazi = []
    po_kljucu = {}
    for kljuc, stranica, kontekst in citati:
        if not stranica:
            continue
        raspon = _raspon_jedinice(jedinice_redci.get(kljuc, ""))
        s = stranica.strip()
        m = re.match(r"^(\d{1,4})\s*[–-]\s*(\d{1,4})$", s)
        if m and raspon and (int(m.group(1)), int(m.group(2))) == raspon:
            nalazi.append({
                "vrsta": "PIN_CITE_RASPON", "kljuc": kljuc, "stranica": s,
                "poruka": "stranica u citatu jednaka je rasponu cijele jedinice — to nije "
                          "pin-cite nego 'negdje u ovom tekstu'",
                "kontekst": kontekst[:120]})
        elif raspon and re.fullmatch(r"\d{1,4}", s):
            n = int(s)
            if n in raspon:
                nalazi.append({
                    "vrsta": "PIN_CITE_RUB", "kljuc": kljuc, "stranica": s,
                    "poruka": "stranica je prva ili zadnja stranica jedinice — često znak da "
                              "je podatak preuzet iz sažetka ili zaključka, a ne iz tijela",
                    "kontekst": kontekst[:120]})
        po_kljucu.setdefault((kljuc, s), []).append(kontekst)
    for (kljuc, s), konteksti in po_kljucu.items():
        if len(konteksti) < 2:
            continue
        jedinstveni = {k.strip()[:60] for k in konteksti}
        if len(jedinstveni) > 1:
            nalazi.append({
                "vrsta": "PIN_CITE_PONOVLJEN", "kljuc": kljuc, "stranica": s,
                "poruka": f"ista stranica nosi {len(jedinstveni)} različite tvrdnje — jedna "
                          f"stranica ne može biti izvor za dva različita nalaza",
                "konteksti": sorted(jedinstveni)[:3]})
    return nalazi
