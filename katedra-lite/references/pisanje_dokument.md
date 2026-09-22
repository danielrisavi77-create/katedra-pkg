# PISANJE — dokument, struktura i predaja (učitava se na okidač)

> Dio `pisanje.md` izdvojen radi štednje konteksta (v2.4). Otvori kad: se rad sastavlja
> u `.docx` ili se odlučuje tko radi dokument (§0, §0b); mentor traži hrpu strukturnih
> pomaka (§1.5); piše se ili provjerava sažetak (§3.0b); korisnik traži obojani prikaz
> izmjena (§6 redline); ili se radi više zahvata nad tekstom odjednom (lanac ovisnosti).
> Brojevi odjeljaka su isti kao u izvornom `pisanje.md`, pa stare reference vrijede.

---

## 0. Prije prve rečenice — gdje tekst živi

**Markdown je izvor istine, `.docx` je izvedeni artefakt.** Poglavlja se pišu u
`.katedra/poglavlja/NN-naziv.md`, jedno po datoteci, a dokument se iz njih
SASTAVLJA. Ne piši poglavlje u razgovor pa neka ga student prekopira, i ne upisuj
ga izravno u `.docx`.

```bash
python3 <KATEDRA_SKILL>/scripts/rukopis.py init            # kostur iz plana.json
python3 <KATEDRA_SKILL>/scripts/rukopis.py status          # koliko je napisano
python3 <KATEDRA_SKILL>/scripts/build_docx.py --fakultet <slug> --tip <tip> \
    --rukopis --out ./rad.docx --provjeri
```

Zašto tako: upis u markdown je običan zapis datoteke — verzionira se u gitu, diff
se vidi, a prekinuta sesija nastavlja se ondje gdje je stala. Upis u `.docx` bi za
svako poglavlje morao naći mjesto u tuđem XML-u i ne razbiti unakrsne reference, a
to puca na svakom ručnom oblikovanju.

**Cijenu reci studentu izrijekom, ne prešuti je:** ono što dotjera rukom u Wordu
gubi se pri sljedećem sastavljanju. Word je za čitanje i mentora; pisanje ide kroz
rukopis. Ako student inzistira na Wordu kao izvoru istine, to je legitimno — ali
tada se poglavlja ne generiraju nego se dokument samo provjerava i popravlja
(`check_rules.py`, `fix_rules.py`).

Konvencije rukopisa (iste kao u skillu `fpzg-diplomski`, pa se isti rukopis može
predati i njemu): `# Naslov` je poglavlje, `## ` potpoglavlje, `**podebljano**` i
`*kurziv*`, `- ` i `1. ` popisi, `> ` blok-citat, markdown tablica s natpisom
IZNAD i retkom `Izvor:` ISPOD, `[[PB]]` prijelom stranice. Redoslijed poglavlja
dolazi iz broja u imenu datoteke — bez njega bi abeceda stavila zaključak pred uvod.

## 0b. Tko radi dokument

**Prvo pitaj tko radi dokument.** Za fakultet koji ima vlastiti skill za izradu
(FPZG → `fpzg-diplomski`) dokument radi TAJ skill — on zna kućni stil, unakrsne
reference, popise prikaza i grafikone. Katedrin generator je rezerva:

```bash
python3 <KATEDRA_SKILL>/scripts/vjestine.py --sposobnost izrada.docx --fakultet <slug>
```

Granica i razlog: `references/vjestine.md`. Dvije skripte koje rade `.docx` postoje
namjerno; ono što ne smije postojati je nezapisana granica među njima.

Katedra do audita nije proizvodila `.docx`, samo ga je ocjenjivala: student je
dokument slagao ručno, a alat mu je poslije govorio što nije u redu. Šest od
četrnaest blokirajućih stavki iz `references/predaja.md` §2 su čisto mehaničke i
jeftinije ih je proizvesti ispravno nego naknadno prijavljivati.

```bash
python3 <KATEDRA_SKILL>/scripts/build_docx.py --fakultet <slug> --tip <tip> \
  --tema "..." --autor "..." --mentor "..." --godina 2026 \
  --plan ./.katedra/plan.json --out ./rad.docx --provjeri
```

Dobiva se naslovnica s podacima iz stanja, izjava, sažetak/summary, **sadržaj kao
Wordovo POLJE** (ne natipkan popis), rimska numeracija do Uvoda pa arapska od 1,
prijelom pred poglavljem ako ga profil traži, i primjer prikaza s ispravnim
sklopom natpis + tablica (`cantSplit`) + „Izvor:". Poglavlja dolaze iz
`plan.json` ako je predan.

`--provjeri` odmah pokrene `check_rules.py` nad vlastitim izlazom. Ako to padne,
ili generator ne poštuje profil ili ga provjera krivo čita — u oba slučaja se ne
nastavlja dalje.

**Student i dalje piše sadržaj.** Kostur ne piše nijednu rečenicu rada: sve
sadržajne pozicije su uglate zagrade koje `check_placeholders.py` pred predajom
mora naći praznima.


### 1.5 Karta premještanja — kad mentor traži hrpu strukturnih pomaka

Zamjerke tipa „ovo pripada u poglavlje 3, ne 2" rijetko dolaze pojedinačno — obično ih je
odjednom šest do deset. Izvođenje jedne po jedne, redoslijedom iz dokumenta, stvara novu
zbrku: premještanje #3 mijenja kontekst koji je #1 već pretpostavljao. Prije nego što se
dirne ijedan odlomak, napravi kartu premještanja:

```bash
python3 <KATEDRA_SKILL>/scripts/zamjerke.py grupiraj --po mjesto
```

Iz toga se vidi obrazac (npr. „četiri zamjerke traže da se poglavlje 2 preseli u 4") koji se
rješava jednim prolazom kroz strukturu, ne kroz izolirana uređivanja koja se međusobno
poništavaju. Kod opsežnog restrukturiranja često je jeftinije poglavlje prepisati iz
`.katedra/poglavlja/*.md` iznova, s odlukom o mjestu svakog dijela unaprijed, nego raditi
kirurgiju nad postojećim odlomcima — v. §0 o rukopisu kao izvoru istine.


### 3.0b Sažetak se piše zadnji i provjerava protiv rada

Sažetak nastaje rano i poslije se ne dira, a rad se u međuvremenu mijenja. Prije predaje
provjeri izrijekom:

* **broj poglavlja iz sažetka = broj naslova prve razine.** Na jednom je radu sažetak
  tvrdio „pet cjelina koje zauzimaju šest poglavlja", a rad ih je imao osam;
* **nijedna tvrdnja sažetka ne smije biti opovrgnuta u tijelu.** Isti je sažetak nudio
  terminal za ukapljeni plin kao dokaz da je anticipacija bila moguća, dok ga je šesto
  poglavlje u međuvremenu razložilo u suprotno;
* svaka rečenica sažetka koja imenuje nalaz mora imati parnjaka u zaključku.

Mentor sažetak čita prvi. Aritmetička netočnost na prvoj stranici skuplja je od bilo koje
u tijelu rada.

Strojno: `python3 <KATEDRA_SKILL>/scripts/provjeri_sazetak.py ./rad.docx --tablica`. Alat
mjeri ono što se dade izmjeriti (broj poglavlja, pojmove, brojke, ključne riječi, parnjaka
u zaključku), a **proturječje ne vidi** — za to ispisuje paritetnu tablicu: svaka tvrdnja
sažetka uz dva mjesta u tijelu koja govore o istome, s brojem poglavlja. Duge se rečenice
sažetka pritom razlažu na tvrdnje, jer bi inače pogodak uvijek padao na prvu i najčešću.


## 6. Isporuka — vizualni prikaz izmjena i kompatibilnost

**Kad korisnik traži vizualni prikaz svega što je promijenjeno** (npr. „obojaj crveno što si
promijenio") — to nije `diff_versions.py`, koji radi interni tekstualni sažetak i ne
proizvodi dokument za čitanje:

```bash
python3 <KATEDRA_SKILL>/scripts/revizije.py redline rad_prije.docx rad_poslije.docx redline.docx
```

Rezultat je treći `.docx`: izbrisan tekst crven i precrtan, dodan/izmijenjen tekst crven bez
precrtavanja, bojano izravno preko fonta (ne Wordov `<w:ins>`/`<w:del>`, čija boja ovisi o
recenzentu). Premješteni odlomci pojavljuju se dva puta (brisanje na starom mjestu, dodavanje
na novom) — očekivano ponašanje diffa na razini teksta, ne bug; reci to korisniku uz isporuku.

> Backward compatibility: ako rad ima samo faculty-level pravila i nema programme/work-type/
> course/mentor overlaya, dopušten je i izravni poziv
> `check_paragraphs.py ../rad.docx --profil ../references/fakulteti/<slug>.json`.
> Za RFIR i druge specifične kontekste koristi resolved profil iz `profile_resolver.py`.


## Redoslijed zahvata nad tekstom je lanac ovisnosti, ne preporuka

Empirijski utvrđeno na stvarnom radu; obrnuti redoslijed je razbio numeraciju i
tražio ponavljanje cijelog kruga.

```
renumeracija literature
        ↓            (markdown nosi KONAČNE brojeve citata)
zamjena / skraćivanje teksta
        ↓
tipografija
        ↓
naslovnice
        ↓
sekcije i numeracija stranica
        ↓
Wordova polja (TOC, SEQ, REF)
```

Zamjena teorijskog dijela mora ići **poslije** prenumeriranja literature: ako se
tekst zamijeni prije, novi tekst nosi stare brojeve citata i numeracija se raspadne.
Isto vrijedi nizvodno — polja se osvježavaju zadnja jer ovise o svemu iznad.
