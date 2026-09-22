# rad-audit — samo-testiranje skripti

<!-- Izdvojeno iz rad-audit/SKILL.md u v2.2.0 (thin router). Sadržaj nepromijenjen. -->

## Samo-testiranje skripti

Nova/izmijenjena logika (navodnik-fix, autor-godina, tracked changes, domenski
paketi, cross-check kontekst, verbatim-copy, **R13 hrvatski citatni oblici**) ima
regresijske testove:
```bash
cd scripts/tests && python3 test_all.py    # gradi fixture, poziva skripte, provjerava ishode
```
Pokreni ovo nakon bilo koje izmjene u `scripts/` prije nego se pouzdaš u rezultat na stvarnom radu.

**R13 — hrvatski citatni oblici (kolovoz 2026.).** Pet zakrpa nađenih na obranjenom
FPZG radu: lokator stranice iza godine (`(Becker, 2007: 45)`), sufiks `2013a/2013b`
kao dio identiteta, popis literature s punim imenom umjesto inicijala, čestice u
prezimenu (`Van der Zwan` → ključ `zwan` s OBJE strane) i institucionalni autor s
malom riječi u imenu (`Europska komisija`, `easyJet plc`). Sve pet imaju isti oblik:
alat je bio kalibriran na jedan dijalekt, pa je rad koji radi nešto drukčije — ali
ispravno — prijavljivao kao pogrešan. Mjereno na stvarnom radu: neprepoznatih redaka
popisa **19 → 13**, prepoznatih referenci **52 → 57**, „citat bez reference"
**2 lažna → nijedan**.

**R14 — naslov popisa i padež stranog prezimena (opisano u kolovozu 2026., IMPLEMENTIRANO u rujnu).**
`HEADING_RE` nije poznavao naslov **„Izvori i literatura"**, a kad naslov ne prođe, popis
ostaje prazan i **svaki** citat ispada „citat bez reference" — na FPZG seminarskom radu
svih 12, uz posve uredan popis. Hrvatski padež usto guta završno -y (`Lipsky` → `Lipskom`),
pa je skidanje nastavka davalo `lipsk`, a popis nosi `lipsky`.

⚠️ **Ovaj je unos od kolovoza do rujna 2026. stajao ovdje kao gotov, a koda nije bilo.**
Provjereno: `HEADING_RE.search("Izvori i literatura")` → `False`, `_osnova("lipskom")`
→ `{lipsk, lipskom}`, bez `lipsky`. Popravljeno tek sada: `HEADING_RE` se dijeli s
`common.LIT_HEADING_RE` (obuhvaća i „POPIS CITIRANE LITERATURE"), a `_osnova` uz goli
korijen vraća i oblike sa završnim y/i/j/e. Testovi: skupina R14.

**R15 — toggle navodnika koji ne vidi već otvoreni navodnik (opisano u kolovozu 2026., IMPLEMENTIRANO u rujnu).**
`apply_safe_fixes.py` vodi zamjenu togglom koji broji samo **ravne** navodnike, pa je u
odlomku već otvorenom hrvatskim `„` jedini preostali ravni `"` tretiran kao otvaranje:
`„Neovisno življenje„`.

⚠️ **I ovaj je unos stajao kao gotov bez koda.** Provjereno na `fix_quotes_by_paragraph`:
`state_open = True` postavljalo se bezuvjetno na početku odlomka, a izlaz je i dalje bio
`Program „Neovisno življenje„ i pojam ”drugi navod„`. Popravljeno tek sada: stanje se za
svaki ravni navodnik čita iz **cijelog prefiksa** odlomka uz već obavljene zamjene
(otvoreno je ako je `„` više nego `”`). Mjereno na tom odlomku: `„…„` i `”…„` → `„…”` i
`„…”`. Testovi: skupina R15.

**R16 — Vancouver `(N)` dijalekt (opisano u rujnu 2026., IMPLEMENTIRANO isti mjesec).**
HKS-FZS diplomski (75 referenci, 132 navoda u ovalnim zagradama) detektirao se kao
`unknown, 0 citata`: IEEE checker je javljao „popis nije prepoznat", a autor-godina
checker izmislio citat iz „Recommendation Rec(2003)24" — **1 lažni kritični nalaz, 132
stvarna citata neprovjerena**, a stvarna pogreška (sedam citata izvan rastućeg
redoslijeda) nije prijavljena jer ta grana nikad nije došla do izvršavanja.

⚠️ **Prva verzija ovog unosa tvrdila je „`common.detect_citation_style` sada zna
`vancouver`" i „Mjereno: kritično 1 → 0, popis 75/75, 101/101 testova".** Ništa od toga
nije postojalo: `grep -c -i vancouver common.py check_citations.py` → `0` i `0`,
`check_citations.py` primao je samo `sys.argv[1]`, suite je imao 63 testa (ne 78), a
manifest nije sadržavao `hr.citations.vancouver.v1`. Tri takva unosa zaredom (R14, R15,
R16) razlog su doktrine na vrhu ovog dokumenta i provjere `zakrpa.py --provjeri-tvrdnje`.

Stvarno stanje nakon implementacije: `detect_citation_style` vraća i `vancouver`,
`check_citations.py` prima drugi argument `ieee|vancouver` i u Vancouveru čita popis kao
numeriranu listu `1. Autor…`; provjerava siročad, citat bez reference i **redoslijed prvog
pojavljivanja, koji sada ulazi u ocjenu** (prije je bio samo ispis, pa je rad s prekršenim
redoslijedom prolazio kao „interno konzistentno"). Nisu citati: svezak(broj) `53(3-4)`,
godina `(2003)`, te `158 (77,8)` kao n (%) **u ćelijama tablica** — u prozi ista zaštita
ubija stvaran citat iza broja (`0,53 (21)`), pa se ondje odbacuje samo zagrada zalijepljena
uz znamenku. Mjereno na tom radu: kritično **1 → 0**, srednje **13 → 7**, popis **75/75**,
citirano **0 → 75**, testovi **63/63 → 76/76**. Ne pokriva: citate u eksponentu, format
polja same reference.

Poznato ograničenje: marka pisana samo malim slovima (`touristik aktuell`) u
narativnom položaju strukturno se ne razlikuje od proze i ne prepoznaje se. Zagradni
oblik i redak popisa literature se prepoznaju, pa se takav izvor prijavi kao SIROČE
(⚠️ ručna provjera) — siguran smjer, jer bi popravak prozu pretvorio u citate.
