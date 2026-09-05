# -*- coding: utf-8 -*-
"""Katalog kvarova: provjera oblika i dodavanje novog unosa.

Katalog (`rad-docx/references/zamke.md`) je jedina memorija lanca izrade. Vrijedi
onoliko koliko su unosi upotrebljivi šest mjeseci poslije, pa oblik nije stvar
ukusa: naslov mora imenovati mehanizam, a unos mora reći simptom, uzrok, popravak
i mjesto. Unos bez popravka je pritužba, unos bez mjesta se ne da primijeniti.

    python3 kvar.py zamke.md --provjeri
    python3 kvar.py zamke.md --novi "Sadržaj se mjeri iz PDF-a bez sadržaja"
    python3 kvar.py dodatak.md --provjeri --nastavak-od 23     # fragment: numeracija od 24
    python3 kvar.py dodatak.md --novi "Naslov" --nastavak-od 23 # prvi kostur dobiva broj 24

Fragment (dopuna katalogu koja putuje zakrpom) počinje na N+1. Bez `--nastavak-od`
alat ga čita kao cijeli katalog i javlja „numeracija preskače — očekivan 1”; isto
se postiže zaglavljem „nadovezuje se na unos N” u prvom retku fragmenta.
"""
import argparse
import os
import re
import sys

# Raspon (`## 61–63. naslov`) postoji jer neki kvarovi imaju smisla samo
# zajedno — ista klasa, isti popravak, jedno mjerenje. Alat ih broji kao
# jedan UNOS koji pokriva više BROJEVA: numeracija se provjerava po
# brojevima, sadržaj po unosu. Bez toga je grupirani unos ili nevidljiv
# (drugi format naslova) ili lažni preskok u numeraciji.
NASLOV = re.compile(r"^##\s+(\d+)(?:\s*[–—-]\s*(\d+))?\.\s+(.+?)\s*$", re.M)
BROJKA = re.compile(r"\d")
ISJECAK = re.compile(r"^```|^\s{4}\S", re.M)
NAJKRACI = 400          # znakova; kraće od toga nije opisan mehanizam nego dojam
NASTAVAK = re.compile(r"nadovezuje se na unos\s+(\d+)", re.I)


def nastavak_iz_zaglavlja(tekst):
    """Broj N iz zaglavlja „nadovezuje se na unos N” (prije prvog unosa), ili None."""
    prvi = NASLOV.search(tekst)
    glava = tekst[: prvi.start()] if prvi else tekst
    m = NASTAVAK.search(glava)
    return int(m.group(1)) if m else None

KOSTUR = """

## {broj}. {naslov}

<Što se dogodilo i koliko: jedna brojka koja kvar mjeri. Zatim zašto — na razini
mehanizma, ne simptoma. Ako je kvar bio tih, reci to izrijekom.>

```
<isječak koda ili izlaza koji kvar pokazuje>
```

<Popravak, tako da se može ponoviti, i mjesto u koje ide. Ako je kvar bio tih,
popravak mora sadržavati i ogradu koja bi ga bila uhvatila.>
"""


def unosi(tekst):
    """[(broj, naslov, tijelo)] u redoslijedu pojavljivanja."""
    m = list(NASLOV.finditer(tekst))
    out = []
    for i, g in enumerate(m):
        kraj = m[i + 1].start() if i + 1 < len(m) else len(tekst)
        prvi = int(g.group(1))
        zadnji = int(g.group(2)) if g.group(2) else prvi
        out.append((prvi, max(prvi, zadnji), g.group(3), tekst[g.end():kraj]))
    return out


def provjeri(put, od=None, nastavak_od=None):
    """Provjerava ono što se DA provjeriti, a ne ono što bi bilo lijepo.

    Prva verzija tražila je od svakog unosa četiri naslovljena dijela
    (Simptom/Uzrok/Popravak/Gdje) i na katalogu od 31 kvara javila 37 nalaza.
    Ispalo je da taj format ne poštuje ni starih 23 unosa ni novih osam — kuća
    piše prozom, a četiri stvari su u njoj SADRŽAJ, ne naslovi. Alat je dakle
    mjerio format koji nitko ne koristi.

    Ostalo je ono što stroj stvarno može potvrditi: teče li numeracija, ponavlja
    li se naslov, ima li unos brojku koja kvar mjeri, ima li isječak koji ga
    pokazuje i je li uopće dovoljno dug da opiše mehanizam. Je li popravak dobar
    procjenjuje čovjek, i alat to kaže naglas umjesto da glumi da zna.
    """
    tekst = open(put, encoding="utf-8").read()
    svi = unosi(tekst)
    if not svi:
        print(f"❌ {put}: ne nalazim nijedan unos oblika „## <broj>. <naslov>\"")
        return 1

    if nastavak_od is None:
        nastavak_od = nastavak_iz_zaglavlja(tekst)
    tvrdi, meki = [], []
    ocekivan, vidjeni = (nastavak_od + 1 if nastavak_od else 1), {}
    for broj, do_broja, naslov, tijelo in svi:
        if broj != ocekivan:
            tvrdi.append((broj, f"numeracija preskače — očekivan {ocekivan}"))
        if do_broja < broj:
            tvrdi.append((broj, f"raspon ide unatrag: {broj}–{do_broja}"))
        ocekivan = do_broja + 1
        kljuc = naslov.strip().lower()
        if kljuc in vidjeni:
            tvrdi.append((broj, f"isti naslov već nosi kvar {vidjeni[kljuc]}"))
        vidjeni[kljuc] = broj

        if od is not None and broj < od:
            continue
        if not BROJKA.search(tijelo):
            meki.append((broj, "nema nijedne brojke — kvar bez mjere je slutnja"))
        if not ISJECAK.search(tijelo):
            meki.append((broj, "nema isječka koda ni izlaza koji kvar pokazuje"))
        if len(tijelo.strip()) < NAJKRACI:
            meki.append((broj, f"kratak unos ({len(tijelo.strip())} zn.) — "
                               "provjeri opisuje li mehanizam ili samo simptom"))

    print("=" * 72)
    print(f"KATALOG KVAROVA — {put}")
    print("=" * 72)
    _rasponi = sum(1 for u in svi if u[1] > u[0])
    print(f"unosa: {len(svi)}" + (f" (od toga {_rasponi} s rasponom)" if _rasponi else "")
          + f" · zadnji broj: {svi[-1][1]} · sljedeći slobodan: {svi[-1][1] + 1}")
    if nastavak_od:
        print(f"fragment: nadovezuje se na unos {nastavak_od}, numeracija se očekuje od {nastavak_od + 1}")
    if od is not None:
        print(f"sadržaj se provjerava od kvara {od} nadalje")

    if tvrdi:
        print(f"\n❌ KVARI KATALOG: {len(tvrdi)}")
        for broj, poruka in tvrdi:
            print(f"   · kvar {broj}: {poruka}")
    if meki:
        print(f"\n⚠️  ZA OKO: {len(meki)}")
        for broj, poruka in meki:
            print(f"   · kvar {broj}: {poruka}")
    if not tvrdi and not meki:
        print("\n✅ numeracija teče, naslovi su različiti, svaki unos ima mjeru i isječak")

    print("\nAlat ne procjenjuje je li popravak dobar ni imenuje li naslov mehanizam —")
    print("to čita čovjek. Mjerilo je u references/kvar.md.")
    return 1 if tvrdi else 0


def novi(put, naslov, nastavak_od=None):
    tekst = open(put, encoding="utf-8").read() if os.path.exists(put) else ""
    svi = unosi(tekst)
    if nastavak_od is None:
        nastavak_od = nastavak_iz_zaglavlja(tekst)
    broj = (svi[-1][1] + 1) if svi else ((nastavak_od + 1) if nastavak_od else 1)
    with open(put, "a", encoding="utf-8") as f:
        f.write(KOSTUR.format(broj=broj, naslov=naslov))
    print(f"✔ dodan kostur kvara {broj}: {naslov}")
    print(f"  Popuni ga pa pokreni: python3 kvar.py {put} --provjeri")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("katalog")
    ap.add_argument("--provjeri", action="store_true")
    ap.add_argument("--novi", metavar="NASLOV")
    ap.add_argument("--od", type=int, metavar="N",
                    help="provjeravaj sadržaj samo od kvara N nadalje")
    ap.add_argument("--nastavak-od", type=int, metavar="N",
                    help="datoteka je FRAGMENT koji se nadovezuje na unos N kataloga: "
                         "numeracija se očekuje od N+1 (isto daje zaglavlje "
                         "„nadovezuje se na unos N”)")
    a = ap.parse_args()
    if a.novi:
        sys.exit(novi(a.katalog, a.novi, a.nastavak_od))
    sys.exit(provjeri(a.katalog, a.od, a.nastavak_od))


if __name__ == "__main__":
    main()
