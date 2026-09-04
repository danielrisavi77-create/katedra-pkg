# Dopuna kataloga zamki — fragment, nadovezuje se na unos 23

> Proizvod protokola `katedra` §1.3 nad 10 nalaza iz sesije 1. 9. 2026. (HKS-FZS diplomski, FPZG
> seminarski, orchestrator test). Numeracija kreće od 24 jer instalirani
> `rad-docx/references/zamke.md` završava na 23 — iako `rad-docx/SKILL.md` tvrdi 31, a
> `katedra/SKILL.md` citira kvarove 32 i 33. Taj nesklad je sam po sebi kvar (v. 37).
> Vlasnik je uz svaki unos naveden, jer katalog po ladici §1.2 živi u `rad-docx`, a većina
> ovih kvarova je u `katedra-lite` — v. IZVJESTAJ.md, nalaz o skillu K3.

## 24. Ključ s vrijednošću `null` nije „profil to ne propisuje", pa resolver pada i gate tiho preskače

Vlasnik: `katedra-lite` (nalaz 1). `profile_resolver.py --fakultet fpzg --tip <bilo koji>` izlazi s
kodom 2 jer `fpzg.json` u `struktura.opseg.esej` nosi `rijeci: null, izvori_min: null`, a resolver
`null` tumači kao „vrijednost izvan dopuštenog popisa", ne kao odsutnost. Drugi sloj istoga drifta:
`_schema.json` i `_resolved_schema.json` ne poznaju tip `esej` ni ključ `primjerci`, pa profil
proširen pravilima 17/24 sheme ne prolazi. Kvar je tih na razini rada: bez
`.katedra/resolved_profile.json` svaki gate korak „usklađenost s profilom" postaje `preskočeno`
za sva 4 tipa rada, a ne samo za esej.

```
$ profile_resolver.py --faculty-dir <synced>/references/fakulteti --fakultet fpzg --tip esej --json
❌ profil propisuje pravila koja Katedra ne zna provjeriti: /struktura/opseg/esej/izvori_min,
   /struktura/opseg/esej/rijeci — vrijednost je null ili izvan dopuštenog popisa.
[izlazni kod: 2]          → poslije zakrpe (3 diffa): [izlazni kod: 0]
```

Popravak: makni `null` ključeve iz `fpzg.json`, dodaj `esej` u `tipovi_radova` obiju shema i
`primjerci` u `_resolved_schema.json` (dokazi/nalaz1_resolver.txt, 2 → 0). Ograda koja bi ga bila
uhvatila i koje nema: test koji razriješi svaki profil iz `index.json` za svaki tip iz
`tipovi_radova` (3 × 4 = 12 poziva) — čeka u `ideje.md` dok se ne napiše.

## 25. Satelit se traži u četiri putanje, a peta (`synced/<hash>/`) je ona u kojoj Cowork živi

Vlasnik: `katedra-lite` (nalaz 2). `vjestine.py::kandidati()` traži `rad-audit`, `rad-docx`,
`fpzg-diplomski` i `replikacija-pspp` u `<SLUG>_HOME`, susjedu, `~/.claude/skills/<slug>`,
`/root/.claude/skills/<slug>` i pluginima. U Cowork sesiji skill živi u
`/root/.claude/skills/synced/<hash>/<slug>`, pa `--provjeri` javlja 3 od 3 satelita „nije
pronađen" (izlazni kod 3) iako su svi instalirani. Šteta je tiha: mod 4 radi bez faza A–G, mod 2/6
padaju na rezervu `build_docx.py` — a pravilo 10 kaže da se nedostatak satelita KAŽE.

```
PRIJE : ❌ izrada.docx  rad-docx  nije pronađen: instaliraj skill „rad-docx" …   [izlazni kod: 3]
POSLIJE: ✅ izrada.docx  rad-docx  /root/.claude/skills/synced/<hash>/rad-docx     [izlazni kod: 0]
```

Popravak: dva glob uzorka `~/.claude/skills/synced/*/<slug>` i `/root/.claude/skills/synced/*/<slug>`
u `kandidati()`; `<SLUG>_HOME` zadržava prednost (dokazi/nalaz2_vjestine.txt, 3 → 0).

## 26. `meta` se koristi u `_renderiraj` koji ga nikad nije primio

Vlasnik: `katedra-lite` (nalaz 3a). `build_docx.py --rukopis` s markdown tablicom pada s
`NameError: name 'meta' is not defined` na `oboji_tablicu(t, razrijesi_paletu(meta.get(...)))`
(redak ~222): funkcija `_renderiraj` nema parametar `meta`, poziv je prepisan iz `gradi()` gdje
`meta` postoji. Rukopis bez tablice prolazi, pa se kvar vidi tek na radu s prvom tablicom; zaobilazak
`--bez-prikaza` ga skriva.

```
$ build_docx.py --profil fpzg_sem.json --tip seminarski --rukopis fixture_rukopis_tablica --out prije.docx
NameError: name 'meta' is not defined                     [izlazni kod: 1]  → poslije: 0
```

Popravak: `_renderiraj(..., meta=None)` i `meta = meta or {}` (u `build_docx.py.diff`). Fixture:
`assets/fixture_rukopis_tablica/` — jedno poglavlje, jedna tablica (dokazi/nalaz3_build_docx.txt).

## 27. Grana `startswith('popis')` hvata prije `'popis literature'`, pa rukopis dobiva fantomske naslove

Vlasnik: `katedra-lite` (nalaz 3b). S `--rukopis` generator uvijek dodaje prazne naslove
„ZAKLJUČAK", „TIJELO TEKSTA", „PRILOZI" i „POPIS LITERATURE" kao TOC polje, jer uvjet
`n.startswith("popis")` pokupi i popis literature prije nego dođe do specifične grane;
`check_placeholders.py` u modu 6 te naslove zatim prijavi kao placeholder. Na stvarnom projektu:
105 odlomaka, 1 tablica, naslovi 1.–6. tek poslije zakrpe bez kostura. Uz to `docDefaults` ostaje
Cambria iako profil traži Times New Roman (gate „pravila" ⚠️) — treći sloj iste grane (3c).

```
if n.startswith("popis") or n.startswith("literatura"):   # hvata i „popis literature"
    ...                                                     # → prazan TOC naslov
```

Popravak: specifične grane prije općih; sažetak iz `.katedra/sazetak.md`; „Izjava…" bez rednog broja;
tema fonta iz profila. Ostaje (fixture, jedna pojava): naslov `# 1. Uvod` u markdownu izlazi kao
„1. 1. UVOD" — dvostruka numeracija, v. `ideje.md`.

## 28. Izlazni kod se računa iz broja simbola, a ne iz toga smije li simbol blokirati

Vlasnik: `katedra-lite` (nalaz 4, lažni nalaz). `gate.py --faza audit` javio BLOKIRA na koraku
„pravila" uz **0 kršenja** i 3 ⚠️ (font docDefaults, naslovnice ručno, nema prikaza) na profilu
FPZG `nepotvrdeno`. Pravilo 18 propisuje da nepotvrđeni raspon daje ⚠️, ne ❌ — doktrina je
postojala, implementacija `check_rules.py` ju nije čitala: ❌ je davala i pravilima bez
`provenance: explicit`, a izlazni kod nije razlikovao ⚠️ od ❌. Na HKS-FZS radu isti mehanizam:
„veličina fonta" ❌ [za potvrdu] prije, ⚠️ poslije.

```
PRIJE  : ✅ u skladu: 4   ⚠️ za provjeru: 3   ❌ kršenja: 1     (nepotvrdeno, bez explicit)
POSLIJE: ✅ u skladu: 4   ⚠️ za provjeru: 3   ❌ kršenja: 0
         → pravilo nije potvrđeno u službenim uputama — ⚠️ umjesto ❌, ne blokira
```

Popravak: izlazni kod 1 samo zbog ❌; na `nepotvrdeno` ❌ zadržavaju samo pravila s provenance
`explicit` (resolver ili sidecar `<profil>.provenance.json`), provenance se čita u oba oblika
(default/rules). Ide i u `zasto.md` pod pravilo 18 kao „što se dogodilo kad ga nije bilo".

## 29. Kućni stil završnog rada primjenjuje se na seminarski jer uvjet zna samo fakultet, ne tip

Vlasnik: `katedra-lite` + `fpzg-diplomski` (nalaz 5). `vjestine.json` veže `stil.kucni` →
`fpzg-diplomski` uz `fakultet: fpzg` bez tipa, pa mod 6 za FPZG **seminarski** zove lanac
`sastavi.py`/`gradi.sh` koji traži odlomak „Izjava o akademskoj čestitosti" (`next()` →
`StopIteration`), sažetak stavlja na kraj i piše „Literatura"/„Diplomski rad" — sve u sukobu s
`resolved_profile` seminarskog (sažetak sprijeda, POPIS LITERATURE, izjava se ne primjenjuje).
Agent je pao na `build_docx.py --rukopis` + `arhiva.py --pismo "Times New Roman"`.

```
--tip diplomski : ✅ stil.kucni fpzg-diplomski [radno, mod 2, 6]
--tip seminarski: ✅ stil.kucni fpzg-diplomski  (ne odnosi se na ovaj fakultet / tip rada)
```

Popravak u `katedra-lite`: `uvjet.tipovi: [zavrsni, diplomski]` + `izvan_uvjeta` u `vjestine.json`,
`--tip` u `vjestine.py`. Nepopravljeno (vlasnik `fpzg-diplomski`): `next()` bez zadane vrijednosti
mora javiti „nema izjave" umjesto `StopIteration`. Drugi sloj: `predaja.md` traži
`rad-docx/scripts/provjeri_reference.py` „obavezno nad konačnim PDF-om" — te skripte u `rad-docx`
**nema** (8 skripti, nijedna se tako ne zove); mrtva naredba, v. 37.

## 30. Numerički stil u ovalnim zagradama ne postoji, pa rad sa 75 referenci prolazi kao rad bez citata

Vlasnik: `katedra-lite` + `rad-audit` (nalaz 6). `citation_dialects.py` zna autor-godina, IEEE `[n]`
i legal-footnote. Rad HKS-FZS (Vancouver `(n)`, `(n, m)`, `(n–m)`) zato dobiva: rad-audit faza B
„unknown, 0 citata" + lažni kritični nalaz `Rec(2003)24` kao autor-godina; `check_argument` „bez
citata u svim poglavljima"; `rubrika` „vlastiti doprinos neispunjeno"; `verify_rewrite` čita
`(67,68)` kao decimalu. Četiri alata, ista rupa, nijedan nije rekao „ne znam ovaj stil".

```
PRIJE  : ⚠ Definirano u LITERATURI: (nije prepoznat popis)  Citirano u tekstu: 0   [izlazni kod: 1]
POSLIJE: CITIRANJE [Vancouver (N)]  Definirano: 75 (raspon 1–75)  Citirano: 75   [izlazni kod: 0]
         ⚠ bez razmaka iza zareza: 5× ['54,57', '67,68', …]   (savjetodavno)
```

Popravak: `vancouver` u `NUMERIC_DIALECTS`, `_schema.json` enum, `profile_rules`, `stanje_init`;
filtar decimala i tabličnih `n (%)`; rad-audit `check_citations.py` + `common.py`; red u
`pisanje.md` (pravilo pisanja). Dokaz: dokazi/nalaz6_check_citations.txt (1 → 0). Srodno, ali drugi
mehanizam od ideje „lažni CITAT BEZ REFERENCE" (institucionalni izvori) — ta ideja ostaje čekati.

## 31. Popis naslova popisa literature je zatvoren, pa nepoznat naslov ruši gate umjesto da javi

Vlasnik: `katedra-lite` (nalaz 7). Gate korak „popis literature protiv kućnog stila" puca (💥) na
radu s naslovom „POPIS CITIRANE LITERATURE": `provjeri_literaturu.py` zna „Literatura", „Popis
literature", „Popis izvora" i vraća „nijedna jedinica nije nađena" s izlaznim kodom 2, što gate
čita kao pad alata (pravilo 20).

```
PRIJE  : ❌ nijedna jedinica nije nađena — ima li rad naslov „Literatura”/„Popis literature”…  [2]
POSLIJE: 3 jedinica: 2 u skladu, 1 odstupa                                                      [1]
```

Popravak: `hr_text.NASLOV_LIT` + lokalni `NASLOV_LIT_PROSIREN` (dvaput, u dva commita — jedno mjesto
bi bilo dosta). Fixture: `assets/fixture_popis_citirane_literature.docx`. Dokaz je otvorio
kvar 36.

## 32. Admisija profila traži datoteku koju isporučeni paket ne nosi, pa se hash ne može osvježiti

Vlasnik: `katedra-lite` (nalaz 8). Nakon zakrpe `fpzg.json` (24) `profile_registry.py --write` odbija:
„admission bundle hash stale za fpzg: pokreni faculty_scale_gate.py ponovno". Ali
`faculty_scale_gate.py` traži `evals/benchmark/v1_vs_v2_contract.json`, a `razvoj.md` izrijekom kaže
da `evals/` od v1.3 **nije u paketu**. Dvije skripte zajedno čine petlju iz koje u instaliranom
skillu nema izlaza; svaka zakrpa profila ostavlja registry u stanju `stale`.

```
$ faculty_scale_gate.py --fakultet fpzg --tier production --as-of 2026-09-02
❌ profil se ne može pročitati: …/evals/benchmark/v1_vs_v2_contract.json: No such file   [2]
$ profile_registry.py --check
❌ admission bundle hash stale za fpzg: pokreni faculty_scale_gate.py ponovno              [2]
```

Popravak (nije napravljen): ili `--benchmark` opcionalan kad datoteke nema (uz ⚠️ „admisija bez
benchmarka"), ili `profile_registry.py --write --bez-admisije` koji hash osvježi i označi profil
`advisory`. Doktrina za `razvoj.md`/SKILL.md: zakrpa profila = ponovna admisija, u istom potezu.
Zaobilaz koji radi: `profile_resolver.py --profil-datoteka <slug>.json` (ADVISORY).

## 33. Shema opsega zna samo ukupni rad, pa se pravila po dijelovima ne mogu ni zapisati ni provjeriti

Vlasnik: `katedra-lite` (nalaz 9, kvar u obliku provjere koja ne postoji). Upute HKS-FZS traže
Uvod ≥ 3000 riječi i ≤ 1/3 teksta, Raspravu ≥ 1000, Sažetak ≤ 1800 znakova, razmak odlomaka 6 pt,
redoslijed podsekcija Metoda. `struktura.opseg.<tip>` nosi samo `stranice|rijeci|izvori_min|
poglavlja`, pa je pravilo s lokatorom u službenim Uputama moglo živjeti samo u `napomene` i u ručno
pisanoj `provjeri_hks_fzs.py`. Na radu: Uvod 3174 ✅ ali 37 % ⚠️, sažetak 1887 zn. ⚠️, „Metode:
Ustroj prije Etike" ⚠️ — ništa od toga profil nije mogao izraziti.

```
"dijelovi": {"uvod": {"rijeci_min": 3000, "udio_max": 0.333}, "sazetak": {"znakovi_max": 1800}, …}
```

Popravak: `dioOpsega` u obje sheme, 18 dijelova u `hks-fzs.json`, `provjeri_dijelove.py`
(generalizacija). Uz to je isporučen i `upute_u_profil.py` (812 redaka, PDF → skica profila) —
to nije popravak kvara nego nova mogućnost bez druge pojave; po §2 pripada u `ideje.md`.

## 34. Faza bez svog artefakta je „nezapočeta" i kad je rad došao gotov

Vlasnik: `katedra-lite` (nalaz 10, lažni nalaz). `napredak.py` za audit tuđeg gotovog rada (mod 4/6)
davao je Plan i Pisanje 🔴 i opseg ❔, jer su faze zaključivane iz `plan.json`/poglavlja koje takav
projekt nema. Popravak u v1.9 dodacima: `datoteke.rad_docx` bez `plan.json` → plan/pisanje „gotovi
izvana", opseg 100 „iz postojećeg rada".

```
* plan — gotovo: `stanje.plan_odobren` ILI gotov rad bez plana (`datoteke.rad_docx` bez `plan.json`)
```

Napomena protokola: verzija PRIJE popravka nije sačuvana (dodaci nose već popravljenu skriptu), pa
se po §1.4 kvar ne može reproducirati i unos ostaje **bez dokaza** — brojka 🔴/❔ dolazi iz
izvještaja sesije, ne iz ponovljenog trčanja.

## 35. Pravilo „godina s točkom" mjeri se i na stilu u kojem je točka iza godine kraj reference

Vlasnik: `katedra-lite` (novi lažni nalaz, otkriven pri dokazu za 31). `provjeri_literaturu.py` na
Vancouver profilu (`tocka_iza_godine: false`) daje ❌ „godina s točkom (2014.), a profil ju ne
traži" za jedinice oblika „…Zagreb: Zdravstveno veleučilište; 2014." — točka je završna točka
reference, ne hrvatska točka iza godine. Na HKS-FZS radu: **11 od 75** jedinica ❌ koje „blokiraju
predaju", sve lažne. Uz to se na numeričkom popisu provjerava abecedni red, koji Vancouver ne
propisuje (redoslijed prvog pojavljivanja).

```
❌ 15. Ozimec Vulinec Š. Palijativna skrb. Zagreb: Zdravstveno veleučilište; 2014.
     ❌ godina s točkom (2014.), a profil ju ne traži      × 11
```

Popravak (nije napravljen): za `stil` u `NUMERIC_DIALECTS` preskočiti „godina s točkom" i abecedni
red, a provjeravati numeraciju popisa. Fixture: `assets/fixture_popis_citirane_literature.docx`
(jedinica 2 daje isti lažni ❌).

## 36. Skill za učenje dokumentira dvije zastavice koje njegove skripte nemaju

Vlasnik: `katedra` (pravilo 8). `SKILL.md` §1.3 propisuje `kvar.py … --provjeri --nastavak-od 23`, a
frontmatter tvrdi da je validacija fragmenta dodana; `kvar.py` poznaje samo `--od N`, koji sadržaj
filtrira ali numeraciju i dalje broji od 1. §1.4 propisuje `dokaz.py … --ocekuj-pad-pa-prolaz`, koje
nema. Oba poziva izlaze s argparse kodom 2 — isti mehanizam kao §1.5 koji je ovaj skill sam
popravio (`--skill/--izvorni/--izmijenjeni`). Fragment od 12 unosa zato i dalje dobiva tvrdu grešku
„numeracija preskače — očekivan 1".

```
$ kvar.py fragment.md --provjeri --nastavak-od 23
kvar.py: error: unrecognized arguments: --nastavak-od 23          [2]
$ kvar.py fragment.md --provjeri --od 24
❌ KVARI KATALOG: 1 · kvar 24: numeracija preskače — očekivan 1    [1]
```

Popravak: `--nastavak-od N` koji postavlja `ocekivan = N + 1` (ili čita zaglavlje „nadovezuje se na
unos N"), `--ocekuj-pad-pa-prolaz` u `dokaz.py` (ili maknuti iz SKILL.md). Ograda: test koji svaku
`python3 …` naredbu iz SKILL.md-a pokrene s `--help`.

## 37. Katalog na koji se skill poziva ima 23 unosa, opis vlasnika kaže 31, a učenje citira 32 i 33

Vlasnik: `rad-docx` + `katedra`. `rad-docx/SKILL.md` (opis i §„Što je gdje") tvrdi „31 stvarni
kvar" s dvjema novim skupinama; instalirani `references/zamke.md` završava na 23. `katedra/SKILL.md`
pravilo 8 upućuje na „kvarove 32 i 33" kojih nema nigdje u instalaciji. Zakrpa koja je podigla
SKILL.md očito nije nosila `zamke.md` — a §1.5 kaže da zakrpa nosi samo promijenjene datoteke, pa je
katalog ostao na staroj verziji dok opis obećava novu. Isti obrazac: `kvar.md` primjer i
`predaja.md` zovu `provjeri_reference.py`, `katedra` §1.1 i `povratak.md` zovu
`provjeri_povratak.py`, `katedra-lite/SKILL.md` r. 332 i `rad-audit` zovu `provjeri_zamke_proze.py`
— **tri skripte, nula datoteka** (`ls` nad synced paketima, 2. 9. 2026.).

```
$ grep -c '^## [0-9]' rad-docx/references/zamke.md → 23     $ grep '31 stvarni kvar' rad-docx/SKILL.md → 1
$ ls rad-docx/scripts/provjeri_povratak.py katedra-lite/scripts/provjeri_zamke_proze.py → No such file (×2)
```

Popravak: `inventar_paketa.py`-tip provjere koja svaki `scripts/<ime>.py` spomenut u `SKILL.md` i
`references/*.md` traži na disku i pada ako ga nema; sljedeća zakrpa `rad-docx` nosi `zamke.md` 24–31.

## 38. Nepotvrđen izvor dobiva simbol i obrazloženje, ali nijednu naredbu čovjeku, pa se nalaz preskače

Vlasnik: `katedra-lite`. `verify_sources.py` za ⚠️ `unverified` i ⏸ `unavailable` ispisuje
simbol, redak literature i rečenicu zašto provjera nije uspjela — i tu stane. Na fixtureu od
5 jedinica to je 5 redaka na koje student ne zna odgovoriti: „formalno uredno, ali bez DOI-ja
i URL-a" opisuje stanje, ne kretnju. Sažetak je čak i tješio („⚠️ ne znači ne postoji"), pa je
ishod bio predvidiv: nalaz koji ništa ne traži tretira se kao nalaz koji ništa ne znači, i
cijela skupina ⚠️ ispada iz tablice „RUČNO PROVJERI" iz pravila 7. Kvar je tih dvostruko —
izlazni kod je 0, jer `unverified` po pravilu 18 ispravno NE blokira, pa ni gate ne prosvjeduje.

```
$ verify_sources.py assets/fixture_zahtjevi_covjeka.md --offline
⚠️  Čavlek   1998   Turoperatori i svjetski turizam
     formalno uredno, ali bez DOI-ja i URL-a — knjiga je takva sasvim uredna, samo se ne može provjeriti automatski
                                                          → 5 redaka, 0 radnji  [izlazni kod: 0]

$ verify_sources.py assets/fixture_zahtjevi_covjeka.md --offline --zahtjevi-covjeka provjera.md
[zahtjevi za čovjeka → provjera.md] 5 izvora traži ručnu provjeru
$ grep -c "PROVJERI RUČNO\|HITNO" provjera.md
5
```

Popravak: zastavica `--zahtjevi-covjeka PUT` (`radnja_za_izvor`, `zahtjevi_covjeka`,
`zapisi_zahtjeve`) piše markdown checklistu samo za izvore koji nisu `verified`, i svakom
dodjeljuje radnju po tome što jedinica ima: DOI → otvori `doi.org/<doi>` i usporedi autora,
godinu i naslov; URL → otvori adresu i provjeri je li na njoj baš ta jedinica (200 nije dokaz
o sadržaju); ni jedno ni drugo → NSK, Hrčak, CroRIS, pa mentor. `conflict`/`invalid` idu pod
`HITNO` (blokiraju predaju), ostalo pod `PROVJERI RUČNO`; ⏸ prvo traži ponovljenu provjeru jer
je nalaz o mreži, ne o izvoru. Ograda koje nema: nijedan test ne traži da nalaz koji ne blokira
ipak imenuje sljedeću kretnju — to je pravilo za oko, ne za stroj, i stoji u `references/kvar.md`.

## 39. Doktrina ne poznaje lokator koji kod već proizvodi, pa se gotov citat tretira kao nedovršen

Vlasnik: `katedra-lite`. `evidence_ingest.py` od popravka Q19 za izvor bez tiskane paginacije
ispravno upisuje `page_label: null` i `passage: N` — radije nego izmišljen redni broj koji bi
student prepisao u citat. Kod je dakle bio točan i nije mijenjan. Kvar je bio u tome što ta
odluka nigdje nije bila zapisana kao doktrina: `SKILL.md` pravilo 28 i `references/pisanje.md`
§2.1 poznavali su samo jedno stanje stranice — „nije potvrđena" → `[PROVJERI STR.]`. Izvor koji
stranicu NEMA padao je u istu kantu, pa je trajno stanje dobivalo privremenu oznaku: student
šalje sam sebe da traži broj kojeg nema, redak u tablici „RUČNO PROVJERI" se ne može zatvoriti,
a mrežni izvještaji i HTML članci u praksi ispadaju iz dokaznog sloja jer „nemaju stranicu".

```
$ evidence_ingest.py assets/fixture_izvor_bez_paginacije.txt --source-id src_test --out ev.jsonl
[evidence → ev.jsonl] dodano 5 passage(s), zamijenjeno 0, source=src_test
$ grep -c 'page_label": null' ev.jsonl
5                                    ← kod je uvijek bio ovakav; doktrina to nije priznavala
$ grep -c "locira po odlomku" references/pisanje.md
0                                    → poslije zakrpe: 1
```

Popravak: pravilo 28 i `pisanje.md` §2 sada razlikuju „stranica postoji, nepotvrđena"
(privremeno, `[PROVJERI STR.]`, ide u tablicu) od „izvor stranicu nema" (trajno, citira se po
odlomku `(N, odl. P)`, gotov je lokator i ne ide u tablicu); §2.1 dobiva odjeljak o
`page_label: null` s mjerom i obrazloženjem zašto je `null` točan podatak, a ne rupa. Ograda:
`assets/fixture_izvor_bez_paginacije.txt` s pet odlomaka drži brojku 5 provjerljivom — ako se
fixtureu doda odlomak, provjera pukne i tjera na usklađivanje umjesto da tiho prođe.

## 40. `inline_shapes` ne vidi sliku koju je autor povukao mišem, pa alat javi „nema što mjeriti"

`provjeri_prikaze.py` skupljao je prikaze iz `docx.Document(put).inline_shapes`. Taj popis
sadrži samo `<wp:inline>` — sliku usidrenu uz tekst. Čim autor u Wordu postavi „Wrap text"
(bilo koju opciju osim „In line with text"), slika postaje `<wp:anchor>` i `python-docx` je
ne vidi jer za plutajuće oblike nema API.

Na diplomskom radu s **4 slike, sve četiri `<wp:anchor>`, nula `<wp:inline>`**, alat je
ispisao „➖ dokument nema nijednu umetnutu sliku — nema što mjeriti" i vratio **izlazni kod
0**. Isti rad, isti trenutak, `check_rules.py`: „dokument sadrži slike, ali nijedan prikaz
nema natpis". Dva alata, dvije istine, jedan ulaz — a korisnik vidi zeleno.

Kvar je tih dvaput: nema poruke o kvaru, i nema razlike između „provjereno, uredno" i
„nisam ni pogledao". Kad je zakrpa proradila, ispalo je da su sve četiri slike umetnute na
**0,19–0,28× izvorne širine**, pa pismo od 10 pt u njima izlazi kao 1,9–2,8 pt. Nalaz koji
je stajao neviđen od prvog pokretanja.

```python
# prije: samo <wp:inline>
for i, sh in enumerate(d.inline_shapes, start=1): ...

# poslije: + <wp:anchor> izravno iz XML-a (extent nosi mjere, a:blip r:embed vezu)
for anchor in d.element.body.iter(f"{{{_NS_WP}}}anchor"):
    extent = anchor.find(f"{{{_NS_WP}}}extent")
    rid = anchor.find(f".//{{{_NS_A}}}blip").get(f"{{{_NS_R}}}embed")
```

Popravak je u `katedra-lite/scripts/provjeri_prikaze.py`: `_plutajuce()` čita anchor slike,
`_slike()` ih spaja s inline popisom. Uz to je dodana **ograda koja bi kvar bila uhvatila** —
`_crteza_u_xml()` broji `<w:drawing>`, pa kad je izmjerenih prikaza nula, a crteža nije,
alat izlazi s kodom 1 i porukom „NIJE provjereno, nije uredno" umjesto s tihom nulom.
Dokaz: isti rad, prije `exit 0` bez ijednog retka mjerenja, poslije `exit 1` i 4 izmjerene
slike s 4 kršenja.

## 41. Uvod na razini Heading 2 prijavljuje se kao „rad nema tezu"

`check_argument.py` gradi poglavlja samo iz `Heading 1` (`if razina == 1`). Naslov niže
razine pada u `podnaslovi` i njegova proza pripiše se prethodnom poglavlju. Kad je „Uvod"
zabunom ostao `Heading 2`, `uvod` je `None`, pa su dvije dimenzije javile:

```
❌ TEZA — nema uvoda
     Uvod nije prepoznat (nema Heading 1 čiji naslov sadrži „uvod").
❌ ZAKLJUČAK ZATVARA KRUG — nema: uvod
```

Poruka imenuje **posljedicu**, ne uzrok, i čita se kao presuda o kvaliteti rada. Na
diplomskom radu na kojem je nađena, promjena stila **tog jednog naslova** i ništa drugo
dala je `✅ TEZA — 3 kandidata` i `✅ ZAKLJUČAK ZATVARA KRUG — 100 % preklapanja (10/10)`.
Rad je cijelo vrijeme imao i tezu i zatvoren krug.

Ovo je lažni nalaz iz §0.3 željeznih pravila: alat koji viče na uredan rad uči korisnika da
ignorira crvenu boju. Ovdje je gore od toga — nalaz je usmjeravao na prepisivanje uvoda i
zaključka umjesto na jedan klik u Wordu.

Popravak je u `katedra-lite/scripts/check_argument.py`: `poglavlja()` pamti sve naslove
ispod razine 1 kao `(razina, tekst)`, a `_uvod_na_krivoj_razini()` ih pretraži prije nego
se javi „nema uvoda". Kad naslov postoji, poruka glasi „„Uvod” je na razini 2, ne 1" i
izrijekom kaže **„Ovo NIJE nalaz o tezi — dok je razina naslova kriva, teza se ne mjeri."**
Regresija provjerena: rad s Uvodom na `Heading 1` i dalje daje zeleno na obje dimenzije.

## 42. Alat za dokazivanje popravaka ne poznaje smjer tihog kvara koji sam skill proglašava prioritetom

`katedra/SKILL.md` § 1.4 kaže da tihi kvarovi imaju prednost: „Kvar koji sruši skriptu netko
će naći. Kvar koji tiho proizvede krivi dokument neće nitko." Popravak takvog kvara po naravi
ide **iz lažnog zelenog u istinito crveno**: prije `exit 0` bez nalaza, poslije `exit 1` s
nalazom. `dokaz.py` je taj smjer imao tvrdo označen kao grešku:

```
⚠ obrnuto od očekivanog: prije prolazi (0), poslije pada (1)
   Provjeri jesu li naredbe zamijenjene.
[izlazni kod 1]
```

Naredbe nisu bile zamijenjene — to je bio točan dokaz kvara 40 (`provjeri_prikaze.py` šuti
nad radom sa 4 plutajuće slike). Alat koji dokazuje popravke odbijao je jedinu vrstu kvara
koju vlastita doktrina stavlja na prvo mjesto, a jedini izlaz bio je `--dopusti-isto`, koji
tu ne vrijedi jer se kodovi razlikuju.

Popravak je u `katedra/scripts/dokaz.py`: zastavica `--tihi` obrće očekivanje na `0 → ≠0` i
javlja „✅ dokazan tihi kvar: 0 → 1". Kad smjer nije takav, `--tihi` pada s porukom da to
onda nije tihi kvar, pa se zastavica ne može upotrijebiti da bi se bilo što progurao.
Poruka u zadanom načinu sada upućuje na `--tihi` umjesto da tvrdi da su naredbe zamijenjene.
Provjereno: `--tihi` nad `1 → 0` pada, zadano ponašanje `1 → 0` i dalje prolazi.

Ovo je treći put da se pravilo iz § 0.8 potvrdilo (v. kvarove 36 i 37): alat za učenje koji
sebe izuzima prestaje učiti prvi. Nađeno je jer je protokol zahtijevao dokaz — da se dokaz
preskočio, kvar 40 bio bi isporučen s bilješkom „dokaz nije prošao, ali radi".

## 43. Doktrina je za 403 na pushu upućivala na read-only GitHub konektor, pa je popravak bio klik koji ništa ne mijenja

§ 0.0 je ispravno prepoznavao egress politiku („ne ponavljaj i ne zaobilazi — prijavi”), a onda
je korisniku nudio krivi popravak: „jedan klik korisnika (claude.ai → GitHub konekcija → Add
repository, uz pravo pisanja)”. Ta veza postoji, ali je **sinkronizacija datoteka za chat i
Projects i po dokumentaciji je read-only** — sesija dobije imena i sadržaj datoteka s odabrane
grane, a `push` pada na isti 403. Površina koja `push` doista daje je Claude Code on the web,
gdje se repo bira **za sesiju** i sesija sama otvara granu i PR.

```
remote: access denied by the git proxy: danielrisavi77-create/katedra-pkg is not in
this session's authorized repository set, so the proxy will not inject a credential for it.
fatal: ... The requested URL returned error: 403
```

Mjera kvara: 2 commita (`a633706`, `0935bd2`, 14 datoteka, +417/−21) bila su gotova i
provjerena, a isporuka je otišla ručnom rutom (bundle + patch) jer je sesija tražila
autorizaciju koje u toj površini nema. Korisnik je zatim upitao mora li sesiju pokretati iz
chata — točno u smjeru koji doktrina sugerira, a koji bi dao **manje** nego Cowork: datoteke bez
prava pisanja. Krivi popravak skuplji je od nikakvog jer izgleda kao da je posao gotov.

Popravak je u `katedra-lite/SKILL.md` § 0.0: umjesto jedne rečenice sada stoji tablica triju
površina (chat/Projects — read-only sinkronizacija; Claude Code on the web — repo kao izvor
sesije, gura granu i PR; Cowork — mape s računala, push samo ako je repo izvor zadatka) i
izričita rečenica da „GitHub konekcija u claude.ai” znači dvije različite stvari. Ograda protiv
ponavljanja: točka (5) u pravilima § 0.0 više ne imenuje konkretan klik nego pojam **izvor
sesije** i upućuje na tablicu, pa se popravak ne može opisati bez površine na koju se odnosi.
Doktrina koja imenuje simptom, a promaši mehanizam, ista je klasa kao kvar 41 — samo na razini
routera, gdje je nitko ne provjerava alatom.

## 44. Čitač kriterija „zadatak" nije imao granu ispunjeno, pa je pojas 5 bio nedosežljiv svakom radu koji ima zadatak.json

`citac_zadatak_komponente` u `rubrika.py` završavao je jednim bezuvjetnim `return`: čim
`.katedra/zadatak.json` postoji i ima barem jednu komponentu, kriterij je `djelomicno`.
Kriterij je `kljucni: true`, a `pojas()` na ključnom `djelomicno` vraća **4**. Gornja
granica rada tako nije ovisila o radu nego o tome je li itko zapisao zadatak — a zapis
zadatka je ono što željezno pravilo 14 izrijekom traži u modu 1. Rad je time kažnjen za
poslušnost prema vlastitoj doktrini.

```python
    return DJELOMICNO, (f"{len(kom)} komponenti zapisano; prisutnost u dokumentu "
                        f"provjerava rad-docx/provjeri_predaju.py --zadatak")
```

Drugi krak istog kvara stajao je u `rad-docx/scripts/provjeri_predaju.py`: komponenta bez
`igle` tražila je doslovan tekst zahtjeva unutar teksta rada (`igle = k.get("igle") or
[k["naziv"]]`). Zahtjev poput „broj stranice i kod parafraze" nije niska koja u dokumentu
može postojati — postoji samo kao **nalaz alata** koji ga je provjerio. Takav je zahtjev
zato uvijek padao kao greška „zadatak traži, a u radu nema", i to greška koja blokira
predaju. Alat je kažnjavao rad za svojstvo vlastitog načina provjere.

Mjera kvara: na seminarskom radu (EFZG RFIR, rujan 2026.) pojas je stajao na **4**, a
držao ga je jedini kriterij „Odgovor na zadatak predmeta" — uz 5 od 5 komponenti koje su
doista bile provjerene i zadovoljene. Poslije zakrpe: pojas **5**, „nijedna greška" u
`provjeri_predaju`. Popravak je mjeren na 10 slučajeva, s verzijom „prije" izvađenom iz
gita a ne rekonstruiranom.

Popravak uvodi polje `provjereno` (`{alat, nalaz, datum}`) uz komponentu: komponenta je
pokrivena ako je strojno provjerljiva (`igle`) **ili** ako uz nju stoji zapisan nalaz
provjere. Komponenta bez jednog i drugog i dalje drži kriterij na `djelomicno` i **imenuje
se**, pa se nepokrivenost vidi umjesto da se pretpostavi.

Ograda protiv ponavljanja, i drugi kvar koji je prva zakrpa usput otvorila: „pokriven" nije
isto što i „provjeren". Komponenta s iglama kojih u radu nema ulazila je u „sve pokrivene",
pa je `rubrika.py` nad istim `zadatak.json`-om govorila `✅ ispunjeno` dok je
`provjeri_predaju.py` govorio `❌ zadatak traži, a u radu nema` — dva alata, jedan artefakt,
suprotan nalaz, i to na ključnom kriteriju. Zato `provjeri_predaju.py` sada zapisuje nalaz
(`--json .katedra/predaja.json`, status po komponenti), a `rubrika.py` ga čita umjesto da
pretpostavlja da je provjera prošla. Bez tog nalaza kriterij ne ide iznad `djelomicno` za
komponente pokrivene samo iglama — nedostatak dokaza nije dokaz, isto načelo po kojem
`pojas()` odbija procijeniti pojas kad je ključni kriterij `nepoznato`.
