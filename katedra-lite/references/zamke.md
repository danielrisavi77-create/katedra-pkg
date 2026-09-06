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

## 45. Opseg se procjenjuje uz pretpostavku A4, a format papira nitko ne mjeri

`check_rules.py` broj stranica procjenjuje iz broja riječi „(A4, prored 1,5)" i provjerava
margine, font, prored i poravnanje. Format papira ne provjerava nijedno od 15 pravila.

Na radu Paroci (seminarski, EFZG RFIR) dokument je kroz sve krugove bio **US Letter,
21,59 × 27,94 cm**, na obje sekcije. Margine su bile točne (2,5 cm), pa je `check_rules`
davao **14 u skladu, 1 za provjeru, 0 kršenja**, a `gate.py --faza audit` je prolazio.
Kvar je uhvatio tek `rad-docx/scripts/provjeri_predaju.py --zadatak`, i to slučajno, jer se
zadatak provjeravao zbog nečeg drugog.

```
· stranica nije A4 (21.6 × 27.9 cm)
```

Tih je i skup: rad se ispisuje i predaje u krivom formatu, a razlika je 1,76 cm visine, pa se
mijenja i prijelom. Poslije prebacivanja na A4 isti je rukopis pao s 20 na 19 stranica, čime
je cijelo prethodno podešavanje opsega bilo mjereno protiv krive geometrije.

Popravak: pravilo `format.stranica` u `check_rules.py`, s očekivanom vrijednošću iz profila
(zadano A4, 21,0 × 29,7 cm) i tolerancijom 0,2 cm, kao **kršenje**, ne kao „za provjeru".
Ograda koja bi ga bila uhvatila: procjena stranica koja se poziva na A4 mora prvo provjeriti
da dokument jest A4, inače procjenjuje nešto što ne postoji.

## 46. `_empirijski` se hrani statusom dijela koji time postaje ključan

`_empirijski(kat)` vraća `True` ako je dio `metodologija` u statusu `napravljeno` ili
`provjereno`. Kriterij `metodologija` je `uvjetno_kljucni: "rad ima vlastito istraživanje"` i
postaje ključan upravo kad je `empirijski` istinit. `citac_dio_metodologija` za `napravljeno`
i `provjereno` vraća `DJELOMICNO` i nema granu `ISPUNJENO`.

```python
def _empirijski(kat) -> bool:
    m = (d.get("dijelovi") or {}).get("metodologija") or {}
    if m.get("status") in ("napravljeno", "provjereno"):
        return True
```

Petlja je zatvorena: označiš da je metodologija napravljena → rad je proglašen empirijskim →
metodologija postaje ključni kriterij → kriterij vraća `DJELOMICNO` → pojas 4. Izlaza nema
ni za rad koji metodologiju uistinu ima, ni za rad koji je nema.

Na radu Paroci rubrika je ispisivala „rad je prepoznat kao empirijski" za rad koji u
potpoglavlju 1.2 izrijekom kaže da **ne provodi vlastito empirijsko istraživanje**. Registar
dijelova uz `metodologija` sam kaže: „svaki rad s vlastitim istraživanjem; teorijski rad
umjesto nje ima odjeljak o pristupu i građi". Alat taj uvjet ne čita.

Popravak je dvodijelan. Prvo, `citac_dio_metodologija` za status `provjereno` vraća
`ISPUNJENO`, a `DJELOMICNO` ostavlja samo za `napravljeno` — razlika između „napisano" i
„netko je provjerio osam odjeljaka" time dobiva smisao. Drugo, `_empirijski` se ne izvodi iz
statusa dijela nego iz zapisa u `stanje.json` (`vlastito_istrazivanje: da|ne`), koji se
postavlja u modu 1 dok je uputa pred očima.

## 47. Lokator dokaza poznaje samo stranicu, pa standardi i propisi ispadaju iz lanca

`validate_records` u `claim_ledger.py` traži `locator.kind == "page"` i cijeli broj
`locator.page >= 1`. Točka standarda (`t. A55`), članak propisa (`čl. 7. st. 3.`) i odlomak
izvora bez paginacije ne mogu se izraziti.

Na radu Paroci **10 od 60 dokaza** nije moglo ući u `evidence.jsonl` — MRevS 240, MRevS 315 i
Zakon o računovodstvu — pa je **5 od 42 tvrdnje** ostalo izvan `claims.jsonl`. Te tvrdnje
imaju uredan lokator i doslovan navod; jedino ih shema ne prima.

```
ev_b03215d02346fff7e3dd: nedostaje valjani page locator
```

Posljedica je gora od izostanka: tvrdnja koja se osloni samo na standard izgleda kao tvrdnja
bez potpore, a `evidence_gate` je nikad ne vidi. Rad koji uredno citira propis time se mjeri
kao slabije potkrijepljen od rada koji ga ne citira.

Popravak: `locator.kind` prima i `clause` (točka standarda, članak propisa) i `passage`
(izvor bez tiskane paginacije, uz `page_label: null` — v. željezno pravilo 28 u
`katedra-lite/SKILL.md`). Za `clause` se umjesto `page` traži `clause_label` kao neprazna
niska. Ograda: `evidence_gate` u ispisu i dalje razdvaja stranicu od točke, da se ne bi
činilo kako je sve mjereno istom mjerom.

## 48. Cross-chapter provjera gleda samo tvrdnje iz lanca, pa proturječje u vlastitim brojkama prolazi

`consistency_check.py` čita `claims.jsonl`, a u lancu su tvrdnje koje se oslanjaju na izvore.
Brojke koje rad sam izvodi iz vlastite tablice ondje ne postoje, pa ih nitko ne uspoređuje
međusobno.

Na radu Paroci potpoglavlje 4.3 tvrdilo je da se „posljednja **tri** koraka" odvijaju nad
već evidentiranim potraživanjem, a potpoglavlje 4.4 i Zaključak da ih je „**šest od sedam**".
Uz to je 4.3 tvrdilo da je potraživanje evidentirano „na **četvrtome** koraku", dok ga vlastiti
popis u istom odlomku stavlja na **peti**. Sve je to prošlo:

```
CROSS-CHAPTER CONSISTENCY
SUMMARY chapters=10 edges=0 findings=0 blocking=0 coverage=sufficient
```

Proturječje je nađeno tek čitanjem, u trećem krugu, nakon što su dva kruga alata završila
bez ijednog blokirajućeg nalaza. Riječ je o brojci koja nosi zaključak rada.

Popravak: lens koji iz tijela rada vadi obrasce `N od M <imenica>` i `<redni broj> korak(u)`
te uspoređuje pojavnice istoga pojma. Kad se za isti pojam pojave dvije različite vrijednosti,
to je nalaz razine A, jednako kao brojka koja se ne slaže s izvorom. Alat ne odlučuje koja je
vrijednost točna — imenuje obje i mjesto na kojem stoje.

Ograda koja bi ga bila uhvatila: faza C već radi „isti pojam, više vrijednosti iste jedinice"
za mjerne veličine. Ista logika nad brojem koraka i udjelima nije bila primijenjena.

## 49. `drift.py` mjeri samo SKILL.md, a kartica i repo razilaze se i u `scripts/`

`drift.py --kratko` uspoređuje `SKILL.md` account kartice i repoa i vraća 0 kad su isti.
Skripte ne uspoređuje. Kartica se sinkronizira kao cjelina, pa može nositi **stariji
`scripts/` uz identičan SKILL.md**, a to je stanje koje alat prijavljuje kao uredno.

Mjereno 4. rujna 2026. na skillu `katedra`: `drift.py --kratko` javio je
`✅ SKILL.md: kartica i repo su iste (89ba4b59f17d)`, a u istom trenutku:

```
$ python3 <synced>/katedra/scripts/kvar.py fragment.md --provjeri --nastavak-od 43
kvar.py: error: unrecognized arguments: --nastavak-od

$ python3 ~/.katedra-pkg/katedra/scripts/kvar.py fragment.md --provjeri --nastavak-od 43
fragment: nadovezuje se na unos 43, numeracija se očekuje od 44   → izlaz 0
```

Zastavica je dokumentirana u `SKILL.md`-u i postoji u repou, ali je u kartici nema. To je
druga pojava kvara 36 („dokumentirana zastavica koju skripte nisu imale") u drugom
mehanizmu: prvi put je nedostajala svugdje, sada nedostaje samo ondje odakle agent radi.
Sesija koja se drži doktrine „`<KATEDRA_SKILL>` je ono što je § 0.0 izvezao" na to naleti
tek kad naredba padne.

Popravak: `drift.py` uspoređuje i `scripts/` (popis datoteka i hash svake), a izlazni kod 1
daje i kad se SKILL.md poklapa, a skripte ne. Ograda: § 0.0 već traži da se verzija paketa
ispiše u prvoj poruci; uz nju treba stajati i redak „skripte: kartica == repo" ili razlika,
jer bez toga „paket 1.9.2" znači samo da je repo dohvaćen, a ne da se iz njega i radi.

## 50. Primjerak mjeri veličinu pisma iz natpisa prikaza, jer odlomci tijela nemaju izričitu veličinu

`primjerci.py` uzima kao tijelo svaki odlomak koji nije naslov i dulji je od 80 znakova, a
veličinu čita iz runa pa iz stila. Odlomak koji veličinu nasljeđuje iz `docDefaults` vraća
`None` i ispada iz moda. Na uzorku s ocjenom 5 tijelo je imalo **59 takvih odlomaka**, a
jedinih pet s izričitom veličinom bili su natpisi tablica (stil `Caption`, 11 pt) — dulji
od 80 znakova i formalno nisu naslovi. Mod je zato ispao 11 pt, iako je tijelo 12 pt.

```
PRIJE:   "velicina_pt": 11.0     (5 natpisa; 59 odlomaka tijela nije brojano)
POSLIJE: "velicina_pt": 12.0     (docDefaults w:sz=24)
```

Kvar je tih i skup jer se **širi**: izmjerena vrijednost upisuje se u profil kao primjerak,
a po željeznom pravilu 17 primjerak je jači od profila. U ovoj je sesiji 11 pt ušlo u
`resolved_profile.json`, `check_rules` je zatim blokirao vlastiti generirani rad zbog
„11 pt", a autor je uskladio dokument prema krivoj mjeri. Popravak ima dva dijela: stilovi
koji nisu tijelo (`Caption`, `table of figures`, `TOC*`, zaglavlja, fusnote) izbacuju se iz
uzorka, a `None` se čita kao „nasljeđuje iz `docDefaults`" i zamjenjuje stvarnom zadanom
veličinom. Ograda: mjeri se i dalje mod, pa dokument u kojem tijelo doista ima dvije
veličine daje onu češću, bez upozorenja.

## 51. Redni broj pravne reference pred velikim slovom lomi rečenicu, pa se mjeri ritam kojega nema

`hr_text._zastiti` štiti točku iza znamenke samo ako iza nje slijedi malo slovo ili zagrada
(`2020. godine`). U pravnoj prozi iza rednog broja redovito stoji velika kratica
(`prema članku 6. ZPD-a`, `u točki 47. MRS-a 12`), pa se svaka takva rečenica lomi na dvije.

```python
>>> recenice("Prema članku 6. ZPD-a osnovica se umanjuje.")
PRIJE:   ['Prema članku 6.', 'ZPD-a osnovica se umanjuje.']
POSLIJE: ['Prema članku 6. ZPD-a osnovica se umanjuje.']
```

Na fixtureu od četiri rečenice pravne proze mjereno je 6 rečenica, medijan 9,5 i 50 %
kratkih; poslije 4 rečenice, medijan 15,5 i 0 % kratkih. `check_ai_style` na temelju toga
javlja „staccato" i „rečenica ≤10 riječi iznad praga" na tekstu koji je iznad praga, pa
autor prepisuje uredne rečenice. Popravak štiti točku iza rednog broja kad joj prethodi
najavna riječ (`čl`, `st`, `t`, `točk*`, `član*`, `stav*`, `alinej*`, `odjelj*`, `redak`).
Ograda se izgovara: `To stoji u članku 6. Sljedeće poglavlje…` sada se spaja u jednu
rečenicu. To je svjestan ustupak — krivo spajanje je rijetko, krivo lomljenje je pogađalo
svaku rečenicu s pravnom referencom. Isti mehanizam u `rad-audit/common.py` vodi se kao
`rad-audit` kvar 10.

## 52. `re.IGNORECASE` gasi strukturni znak, pa svaki izvor s provenijencijom postaje tuđe autorstvo

`_TUDJE_AUTORSTVO_RE` razlikuje studentov prikaz od tuđeg po velikom slovu iza korijena
(`autori Obzor 2020` je tuđe, `obrada autora prema ZPD` nije). Uzorak je bio jedan, s
`re.IGNORECASE` nad cijelim izrazom, pa je `[A-ZČĆŽŠĐ]` hvatao i mala slova: u nizu
`izrada autora prema ZPD` podudarnost je bila `autora p`.

```
"Izvor: izrada autora prema ZPD, čl. 28."   PRIJE: vlastiti=False   POSLIJE: True
"Izvor: autorov izračun prema ZDPIRP"       PRIJE: vlastiti=False   POSLIJE: True
"Izvor: autori projekta Obzor 2020"         PRIJE: vlastiti=False   POSLIJE: False
```

Pogađa **svaki** izvor koji uz autorstvo imenuje i podlogu, a to je oblik koji profil
traži („Izvor:" ispod prikaza). Na radu sa šest autorskih prikaza mjereno je
`vlastitih: 0 · prerađenih: 6`, `rubrika` je zbog toga kriterij „Vlastiti doprinos"
(težina 5, ključni) spustila na `djelomicno`, a pojas na 4. Skuplja je posljedica bila
ponašanje koje alat time nagrađuje: u ovoj je sesiji autor izbrisao „prema ZPD, čl. 28."
iz dva izvora **da bi zadovoljio mjerilo**, čime je izgubljena provenijencija koju drugo
pravilo istog paketa izrijekom traži. Popravak dijeli uzorak na dva: popis zajedničkih
imenica ostaje neosjetljiv na veličinu slova, strukturni znak postaje osjetljiv.

```
PRIJE:   prikaza s izvorom: 6 · vlastitih: 0 · prerađenih: 6
POSLIJE: prikaza s izvorom: 6 · vlastitih: 6 · prerađenih: 0
```

## 53. Rep predaje pripada vrsti rada, a čitao se s razine fakulteta, pa svaki seminarski kasni

`tempo.py` odbija `predaja.administrativni_rep_dana` od dana do roka. Ta brojka u
`efzg.json` iznosi 14 i pokriva Turnitin, uvez, unos u repozitorij i prijavu obrane —
korake **završnog rada**. Seminarski se predaje e-mailom nositelju i nema nijedan od njih,
ali profil rep ne veže uz vrstu rada, pa ga tempo primjenjuje na sve.

```
seminarski, rok za 7 dana:
PRIJE:   • ROK JE PROŠAO ILI GA JEDE ADMINISTRATIVNI REP
POSLIJE: ✅ U PLANU        (rep 0 dana, izvor: profil)
```

Svaki seminarski s rokom kraćim od 14 dana, dakle gotovo svaki, dobivao je istu poruku, a
uz nju i `napredak.py` gasi cijelu procjenu tempa. Popravak je dvodijelan: overlay
`efzg-rfir-seminarski` dobiva vlastiti blok `predaja` s repom 0 i dva stvarna koraka, a
`tempo.py` uz brojku ispisuje i **odakle je uzeta** („profil" ili „zadano u tempo.py"),
jer rep bez izvora ne da se provjeriti. Ograda: rep za druge vrste radova i dalje dolazi s
razine fakulteta; overlay ga nadjačava samo ondje gdje je izmjeren ili izjavljen.

## 54. Kartica `katedra-lite` nosi samo `SKILL.md`, a router imenuje 44 datoteke koje ne nosi

Mjereno 5. rujna 2026.:

```
kartica:  /root/.claude/skills/synced/<hash>/katedra-lite/
          SKILL.md   (34.582 B)   scripts/ NEMA   references/ NEMA
repo:     ~/.katedra-pkg/katedra-lite/
          SKILL.md   (isti md5)   scripts/ 72     references/ 69

$ grep -oE '(scripts|references)/[a-z_0-9]+\.(py|md|json)' kartica/SKILL.md | sort -u | wc -l
44
```

Doktrina u kartici je **ista** kao u repou (isti md5). Nedostaje samo ono na što upućuje:
`gate.py`, `rubrika.py`, `check_rules.py`, `dijelovi.py`, `references/pisanje.md` i još 39
datoteka. Skill radi jedino ako `~/.katedra-pkg` već postoji ili ako git prođe.

Druga polovica kvara je redoslijed u § 0.0. Usporedba s bratskim skillom:

| skill | redoslijed izvora paketa |
|---|---|
| `rad-orchestrator` v1.2.1 | **prilog u chatu** → git → synced kartica |
| `katedra-lite` v1.9.x | git → synced kartica |

Skill kojemu je paket nužan imao je slabiji dohvat, a kartica koja mu je „rezerva" je
prazna, pa rezerve nema.

Popravak, dva dijela: (a) § 0.0 kreće od priloga; (b) kartica dobiva `scripts/` i
`references/`, a fallback grana ispisuje ❗ umjesto da tiho nastavi:

```
$ (bez priloga, bez mreže, kartica bez scripts/)
⚠️ paket nije dostupan — NAJBRŽE: priloži katedra-pkg-vX.zip u chat. Kartica: <put>
❗ kartica nosi samo SKILL.md — nijedna skripta iz ovog routera nije dostupna; radi se
   rukom, SVAKI strojni korak ide kao preskocen (pravilo 8), nista se ne prijavljuje
   kao provjereno
$ (ista mutacija, ali kartica IMA scripts/)
⚠️ paket nije dostupan — NAJBRŽE: priloži katedra-pkg-vX.zip u chat. Kartica: <put>
   (drugog retka nema)
```

**Dva kvara u samom popravku, nađena mutacijskim testom (pravilo 34), oba tiha:**

1. `ls -d "$KATEDRA_PKG"/*/` ne vidi mape koje počinju točkom. Zip napravljen iz
   `~/.katedra-pkg` nosi korijen `.katedra-pkg/`, pa se grana za spljoštavanje nije
   okidala: paket je bio raspakiran, a poruka je i dalje glasila „paket nije dostupan".
   Popravak traži mapu koja *sadrži* `bin/env.sh`, ne prvu mapu.
2. Hrvatski zatvoreni navodnik u poruci bio je **ASCII `"`**, pa je zatvorio nisku u
   ljusci: `bash -n` → `syntax error near unexpected token '('`. Cijeli § 0.0 ne bi se
   izvršio ni u jednoj sesiji. Ograda: `bash -n` nad izvučenim blokom prije isporuke.

Isti mutacijski test na `drift.py`:

```
A) stvarno stanje         ❗ KARTICA NEMA scripts/ … imenuje 18 skripti   izlaz 1
B) kartica ima scripts/   ✅ kartica i repo su iste (72 datoteke)          izlaz 0
C) fali gate.py           ❌ 1 samo u repou (gate.py)                      izlaz 1
```

## 55. `SKILL.md` spremljen kao dopuna gubi router; tri skilla su se tako okrnjila

Kartica pri spremanju **zamjenjuje cijeli** `SKILL.md`. Prijedlog napisan kao „dopune A–D,
postojeći sadržaj ostaje nepromijenjen" zato ne dopunjuje ništa — briše sve ostalo.

```
$ grep -rl "Napomena o ovoj datoteci" <kartice>/*/SKILL.md
<kartice>/dokazna-stranica/SKILL.md
<kartice>/rektorova/SKILL.md

$ grep -h "^description:" ~/.katedra-pkg/rad-docx/SKILL.md <kartice>/rad-docx/SKILL.md | cut -c1-95
description: "Ažurira broj kvarova u katalogu zamki s 23 na 31 i imenuje dvije nove skupine (p
description: "Motor izrade predajnog .docx-a iz markdown rukopisa: petlja do fiksne točke pagi
```

Dvije pojave su sanirane i **same to pišu** u § 4 svojih SKILL.md-ova (`rektorova`, dopune
A–D; `dokazna-stranica`, dopune 5a–5e): router je bio izgubljen, sekcije 0–2 rekonstruirane
iz `references/`. Treća nije sanirana: `rad-docx/SKILL.md` **u repou** nosi opis *promjene*
umjesto opisa skilla, i to je opis po kojem se skill bira. Kartica ima ispravan.

Popravak: prijedlog skilla uvijek nosi **cijeli** `SKILL.md`, nikad diff ni „ostatak
ostaje". Ograda: `drift.py --kratko` (kvar 49) i provjera da `description:` opisuje skill,
a ne zadnju izmjenu.

## 56. Doktrina o gateovima postojala je u dva skilla i nikad nije prešla u `katedra-lite`

```
$ grep -rlE "ne smije preslikati implementaciju|koji ne može pasti nije" <kartice>/*/SKILL.md
<kartice>/audit-dokazne-stranice/SKILL.md
<kartice>/rektorova/SKILL.md

$ grep -c "mutacijski" <kartice>/katedra-lite/SKILL.md
0
```

`rektorova` (dopuna A) i `audit-dokazne-stranice` (§ 5) nose, riječ po riječ: *„Gate računa
neovisno iz zaključanog izvora, nikad ne kopira izraz iz generatora. Gate koji ne može pasti
nije gate. Svaki novi gate mutacijski testiraj — pokvari kod, pokaži da pada, vrati."*
Ondje je nastalo skupo: dvaput je gate ponavljao istu pogrešku generatora (medijan uz paran
broj parova; brojnik i nazivnik iz različitih skupova) i time je **potvrđivao**.

`katedra-lite` to nije imala. Kvarovi 44–48 svi su njezin oblik: `check_fields.py` ispisuje
`updateFields: NE` i vraća ✓; `rubrika.py` za dvije komponente nema granu „ispunjeno";
`provjeri_predaju.py` proglašava greškom komponentu koja nije strojno provjerljiva.

Ovo je kvar u **prijenosu između skillova**, ne u kodu: nalaz plaćen u jednom skillu ostaje
zaključan u njemu. Popravak: pravila 33 i 34 u `katedra-lite/SKILL.md`, i obveza da
`katedra` § 1.3 pri svakom novom pravilu provjeri nose li ga bratski skillovi već pod drugim
imenom (ladica doktrina, ne samo ladica kvarova).

## 57. `VERSION` zaostaje za commitom, a § 0.0 taj broj ispisuje kao prvo što sesija kaže

```
$ git -C ~/.katedra-pkg log --oneline -1
e57ac53 Merge PR #7: v1.9.3 (prenumerirano 50–53 / 9–11 / 25–26, pravilo 32, otisak fb8ae4bb)
$ cat ~/.katedra-pkg/VERSION
1.9.2
```

§ 0.0 pravilo (4) traži da se `KATEDRA_PKG_VERZIJA` ispiše u prvoj poruci sesije. Ta brojka
dolazi iz `VERSION`, a `VERSION` se održava rukom i ne ulazi u nijednu provjeru. Sesija
zato izgovori „katedra-pkg 1.9.2" nad paketom koji je v1.9.3 — a upravo se po toj brojci
odlučuje treba li povlačiti novije, pa je pogrešna brojka gora od nikakve.

Posljedica je izmjerena u ovoj sesiji: lokalna kopija bila je 1.9.2, remote v1.9.3, a
razlika (kvarovi 50–53, pravilo 32, četiri nove skripte) otkrivena je slučajno, pri
suhom pokretanju § 0.0, a ne pri dohvatu paketa. Zakrpa pisana nad zastarjelom kopijom
bila je numerirana od 50 i sudarila bi se sa svime što je već u repou.

Popravak: `VERSION` se ne piše rukom nego ga podiže isti korak koji radi commit, a
`bin/env.sh` uz broj ispisuje i kratki hash i datum HEAD-a, da se „1.9.2" ne može pomiješati
s dvjema različitim sadržajima. Ograda dok toga nema: uz verziju ispiši i
`git -C "$KATEDRA_PKG" log --oneline -1`.

---

## 58. gate je zeleno javljao fazu u kojoj se ništa nije pokrenulo

**Kad:** 5. 9. 2026. **Gdje:** `katedra-lite/scripts/gate.py:384` (`zakljucak`).

`blokirajuci` je uzimao samo `NALAZ` i `PUKAO`. Blokirajući korak kojemu fali ulaz
izlazi kao `PRESKOCENO` (`gate.py:307`, „nema ulaza"), pa je gate ispisivao
**„✅ nijedna blokirajuća provjera nije pala" uz izlazni kod 0** dok se sedam
blokirajućih provjera nikad nije pokrenulo. Dovoljno je da se rad zove drukčije
od `rad.docx`.

Izmjereno prije i poslije, isti prazan projekt, faza audit:

```
prije:   3 prošlo · 0 nalaza · 12 preskočeno   →  ✅ ... , izlazni kod 0
poslije: 3 prošlo · 0 nalaza · 14 preskočeno   →  ⛔ NIJE POKRENUTO, a blokira:
         revizije, motor_audit, pravila, jezik, fusnote, dosljednost, literatura
         izlazni kod 1
```

**Ograda:** `katedra-lite/scripts/tests/test_gate.py`, skupine G1–G12 (25 testova),
uključujući end-to-end tvrdnju da prazan projekt NE prolazi fazu audit i da ispis
ne smije sadržavati „nijedna blokirajuća provjera nije pala".

**Izlaz iz blokade:** `gate.py --dopusti-preskok korak=razlog`. Razlog se upisuje
u `gate.json` pod `sazetak.preskok_dopusten` i ispisuje u završnom retku.

---

## 59. faza audit nije pokretala audit

**Gdje:** `gate.py::koraci("audit")`. Korak `motor` je zvao `engine.py --provjeri`
(samo razrješavanje motora, `blokira=False`), a pravi audit (`engine.py --audit`,
faze A–G: citati, brojke, tipografija, Word polja) stajao je samo u prozi
`references/audit.md:174`. Mod čija je jedina svrha naći pogreške nije imao korak
koji ih traži; blokirala je točno jedna provjera od petnaest.

**Ograda:** `test_gate.py` G7 traži da faza audit blokira na `motor_audit`, `jezik`,
`fusnote`, `dosljednost`, `literatura`, `revizije` i `pravila`, i da blokirajućih
koraka bude najmanje šest.

---

## 60. `provjeri_predaju.py` nije bio korak nijednog gatea

Alat postoji od v1.4 i hvata zastarjele brojke iz modela, `updateFields`, TOC,
neuravnotežena polja, `REF` bez zabilješke i numeraciju sekcija. Bio je naredba u
`references/predaja.md` koje se agent morao sjetiti. Posljedica: `rubrika.py` je
rutinski čitala `.katedra/predaja.json` koji nitko nije napisao.

**Ograda:** `test_gate.py` G8.

---

## 61–63. audit koji se smije ignorirati

* `generate_report.py`: iznimka u modulu upisivala se bez znaka ⚠, pa je ispadala
  iz sažetka i brojača — srušena faza izgledala je kao faza bez nalaza.
* `audit_all.py:83`: bezuvjetni `return 0`.
* `numbers_inventory`, `check_repetition`: `return 0` i kad ima nalaza.

Sada: iznimka je KRITIČNO, faza s izlaznim kodom ≥ 2 ulazi u nalaze kao
„faza nije izvedena", a `audit_all` vraća `max(KODOVI.values())`.

---

## 64–66. klase pogrešaka koje nijedan alat nije gledao

| Kvar | Što je prolazilo | Alat |
|---|---|---|
| 64 | „147 ispitanika" u Metodologiji i „152 ispitanika" u Rezultatima | `numbers_inventory.uzorak_nalazi` |
| 65 | `zbroj_kategorija` i `uzorak_nalazi` bile su definirane ISPOD `if __name__ == "__main__"` — mrtav kod koji `pipeline.md` opisuje kao aktivnu fazu | pozvane iz `main()` |
| 66 | duga crtica, nedosljedan postotak, `20°C`, `...`, polunavodnici | `check_typography` |

Prije: tekst s dugom crticom i miješanim „45%" / „62 %" dobivao je `✓ tipografija čista`.

**Ograda:** `rad-audit/scripts/tests/test_all.py`, skupine R19 i R20.

---

## 67–70. lažni nalazi koji su gate činili neupotrebljivim

* **67** `uskladi_kljuceve.slaze`: prefiks od 4 znaka spajao je `Markov` i
  `Marković` iste godine u isti ključ, pa je pravi citat bez reference nestajao.
  Sada prefiks vrijedi samo ako je razlika hrvatski padežni nastavak.
* **68** `parse_ay_narrative` radio je nad tekstom spojenim s `\n`, a `\s` hvata
  prijelom retka: naslov „1. UVOD" iznad „Prema Beckeru (2007)" davao je ključ
  `('uvod', '2007')` i izvještaj ga je svrstavao u KRITIČNO.
* **69** tri kopije `LIT_HEADING_RE` (`common`, `check_overlap`, `check_repetition`),
  dvije bez „IZVORI I LITERATURA" i „POPIS CITIRANE LITERATURE".
* **70** hrvatska rečenica koja uvodi citat počinje velikim slovom na funkcijskoj
  riječi: „Prema Kovačević (2019)" davalo je ključ `prema`.

Redoslijed je bio namjeran: **prvo su počišćeni lažni nalazi, pa tek onda podignute
blokade.** Gate koji pada iz krivih razloga zaobiđe se za tjedan dana.

**Ograda:** R17, R18, R21.

---

## 71. faza A bez izvršitelja

`SKILL.md` je fazu A opisivao kao provjeru placeholdera, a alat je bio u drugom
skillu i nijedan runner ga odavde nije zvao. `[TREBA IZVOR]` u fusnoti prolazio je
do predaje. Sada: `rad-audit/scripts/check_placeholders.py` (tijelo, ćelije,
fusnote, endnote, zaglavlja, podnožja), faza A2 u obama runnerima.

---

## 72–73. alat za provjeru tvrdnji bio je i sam tvrdnja bez pokrića

`zakrpa.py --provjeri-tvrdnje` nad `katedra-lite` vraćao je „✓ SKILL.md i kod se
slažu" i izlazni kod 0, jer su sve tri provjere ovisile o `scripts/engine_contract.json`
i `scripts/tests/test_all.py`, kojih katedra-lite nema. Uz to je `main()` vraćao 1,
a ulazna točka ga je zvala bez `sys.exit`, pa je alat uvijek izlazio s 0.

Dodano: svaka skripta imenovana u `SKILL.md` i `references/*.md` mora postojati u
paketu ili kod satelita. Odmah je našla dvije rupe: `provjeri_povratak.py` (motor
cijelog moda 7, opisan u `povratak.md`, nije postojao) i `soffice.py`.

## 74. Trajna napomena o metodi nosila je znak ⚠, pa je svaki rad — i savršeno čist — imao barem jedan „nalaz"

`check_citations_authoryear.py` na kraju ispisa objašnjava kako gradi ključ. To je **napomena
o metodi**, ne nalaz o radu: vrijedi jednako za čist i za pokvaren rad. Redak je počinjao
znakom `⚠`, a `generate_report.py` svrstava u nalaze svaki redak s tim znakom, pa je napomena
ulazila u brojač na **svakom** radu.

```
prije:   ⚠ HEURISTIKA — ključ je (prvi autor, godina), ne pun popis autora/naslov.
poslije: NAPOMENA O METODI — ključ je (prvi autor, godina), ne pun popis autora/naslov.
```

Izmjereno na čistom radu (dva izvora, oba citirana, nijedno siroče): redaka sa znakom `⚠`
**1 → 0**. Autor zakrpe mjerio je na stvarnom radu (18 odlomaka, 2 izvora) i dobio srednje
nalaze **2 → 1**, gdje je preostali stvarno pitanje.

Brojač koji nikad ne pokazuje nulu prestaje se čitati — isti mehanizam kao gate koji nikad ne
pada (kvar 58), samo obrnut: ondje je zeleno bilo lažno, ovdje je crveno. Oba puta signal
gubi vezu sa stanjem rada.

Ovaj je unos napisan naknadno. Popravak je stigao u seriji v1.9.6 kao commit „kvar 74", ali
**bez unosa u katalogu**: `kvar.py` je zato javljao `numeracija preskače — očekivan 74`, a
broj 74 stajao je potrošen u porukama commita i nedostupan sljedećoj zakrpi. Mjerenje gore
napravljeno je pri upisu, nad verzijama iz gita, a ne prepisano iz poruke commita.

## 75–78. prvi prolaz kroz STVARNI rad

**Kad:** 5. 9. 2026., odmah nakon podizanja blokada. **Rad:** FPZG, preddiplomski,
politička ekonomija uvjetovanosti, 5 172 riječi, 117 odlomaka, 3 tablice, 2 sekcije.

Prvi puni prolaz dao je **2 kritična i 2 kozmetička nalaza, a nijedan nije bio
greška u radu**. To je opasniji ishod od propuštene greške: gate koji puca iz
krivih razloga zaobiđe se za tjedan dana i onda više ne hvata ni prave greške.

| Kvar | Lažni nalaz | Uzrok | Zakrpa |
|---|---|---|---|
| 75 | „Putnamovo (1988)", „Closina (2021)", „Thinusinu (2025)" kao CITAT BEZ REFERENCE, a jedinice kao SIROČAD | `_osnova` je znala padeže, ali ne **posvojne pridjeve**, koje hrvatski akademski tekst tvori redovito | `_POSVOJNI` uzorak `(ov\|ev\|in)(a\|o\|u\|e\|i\|om\|im\|oj\|og\|…)?$` |
| 76 | „Notes from Poland (2026)" citiran, a u popisu stoji | narativni uzorak prekida se na maloj riječi u sredini imena, pa je ključ iz teksta `poland`, a iz popisa `notes` | svaka velikim slovom pisana riječ institucionalnog imena postaje alias |
| 77 | 9 „engleskih polunavodnika" | U+2019 između slova je **apostrof** („Orbán's", „the EU's"), a rad ima engleske naslove u popisu | broji se samo U+2018 i U+2019 koji nije među slovima; stvarno stanje: 2 |
| 78 | „slovo 'x' kao množenje" | DOI `10.1177/1023263X251338198` | granice tokena: ni s jedne strane ne smije biti slovo, kosa crta ni točka |

Poslije zakrpa: **kritično 0, kozmetičko 1**, izlazni kod 0. Preostala tri
savjetodavna nalaza su stvarna pitanja (`updateFields: NE`, `pageBreakBefore: 5`).

**Ograda:** `rad-audit/scripts/tests/test_all.py`, skupine R23–R26, svaka s
**oba smjera**: posvojni pridjev spaja Putnamovo s Putnam, ali NE spaja Putnamovo
s Kovač; apostrof nije nalaz, ali pravi polunavodnici jesu; DOI nije množenje,
ali „80 x 80 mm" jest.

**Pravilo koje iz ovoga slijedi:** provjera podignuta u blokadu mora prije toga
proći kroz barem jedan stvarni rad. Sintetički fixture pokazuje da alat hvata;
samo stvarni rad pokazuje koliko lažno hvata.

---

## 79. popis literature gutao je sve iza sebe

Svugdje u lancu popis literature se rezao kao „od naslova do KRAJA dokumenta".
Rad koji iza literature ima Popis tablica, Popis grafikona, sažetak i summary,
dakle standardna FPZG struktura, davao je **30 bibliografskih jedinica umjesto
27**: redci popisa prikaza i rečenice sažetka brojali su se kao jedinice.

Sada `common.dio_literature()` omeđuje popis s obje strane; kraj je prvi sljedeći
naslov istoga ranga (`KRAJ_LITERATURE_RE`). Koriste ga svi potrošači.
**Ograda:** R27.

---

## 80–86. tri stavke koje su ostale nakon v1.9.5

**80 — službena oznaka akta u jednom obliku.** `Uredba (EU, Euratom) 2020/2092`
nije prolazila jer je uzorak tražio doslovno `Uredba (EU)`. Propis bez DOI-ja nije
nepotvrđena jedinica.

**81 — nenađen blok nije obarao mjerenje.** `izmjeri.py` je prikaz kojemu natpis
ili „Izvor:" nije nađen u PDF-u ispisivao u JSON i to je bilo sve. Takav prikaz
ispada i iz `prelomi.json` (pa se lomi preko dvije stranice) i iz `natpisi.json`
(pa nema retka u popisu prikaza), a `gradi.py` javi „✅ stabilno". Fiksna točka
izračunata nad nepotpunim skupom nije fiksna točka. Izuzetak: `--dopusti-nenadene`.

**82 — smanjeni opseg izgledao je kao uspjeh.** Bez LibreOfficea `gradi.py` je
gradio dokument bez ijednog izmjerenog broja stranice i vraćao 0. Sada vraća 4,
kod koji `gate.py` već preslikava u „preskočeno", dakle u deklariranu granicu.
Uz to je ulazna točka zvala `main()` bez `sys.exit`, pa je i 4 postajalo 0.

**83 — `prikazi.py` je smio pasti.** Povratna vrijednost se nije gledala, pa je
`blokovi.json` ostajao od prošle izgradnje i mjerio se pogrešan skup blokova.
Dodana je i provjera da `blokovi.json` nije stariji od dokumenta.

**84 — fiksna točka protiv zaostalog stanja.** `toc.json`, `prelomi.json` i
`natpisi.json` nisu se brisali na početku, pa je prvi krug mogao dati tri „=" i
poruku „stabilno" uspoređujući novo mjerenje sa stanjem prethodne izgradnje.
Sada se premještaju u `_stanje_prosli/`; `--zadrzi-stanje` je svjestan izuzetak.

**85 — pomak numeracije od krivog mjesta.** `gradi.py` nikad nije prosljeđivao
`--pocetak-tijela`, pa je pomak računat od PRVOG naslova rukopisa. U FPZG
strukturi prvi je dio predtekst, pa su svi brojevi u sadržaju i popisima bili
pomaknuti za konstantu. Ograda protiv rasapa to ne vidi jer raspon ostaje
netaknut, pa se petlja uredno stabilizirala na pogrešnim brojevima. Sada se
`tijelo_pocinje_od` čita iz profila.

**86 — popis prikaza bez parityja.** Nitko nije uspoređivao broj natpisa u tijelu
s brojem redaka u popisu, ni provjeravao je li numeracija po vrsti neprekinuta.
Rad je išao u predaju s osam tablica i šest redaka u popisu, ili s „Tablica 1, 2,
2, 4", jer `SEQ` polje razliku maskira dok se ne osvježi.

---

## Nova faza D2 i B2 — dvije klase koje nijedan alat nije gledao

**D2, `check_tvrdnja_izvor.py`.** `cross_check.py` traži brojku kao podniz po SVIM
izvorima ZAJEDNO, pa brojka koja postoji u izvoru A, a pripisana je izvoru B,
prolazi čista. To je oblik pogreške koji recenzent nađe za dvije minute, a alat
nije nalazio nikad. Veza se ne da pogoditi iz teksta: zapisuje se jednom u
`izvori/mapa.json` (`mapa_izvora.py --izgradi` daje prijedlog uparen po prezimenu
i godini u imenu datoteke). Tri ishoda: potvrđeno, PRIPISANO KRIVOM IZVORU (uz
popis izvora u kojima brojka stvarno jest), nije nađeno. Granice se broje i
ispisuju: rečenice bez citata, citati bez unosa u mapi, jedinice bez priložene
datoteke.

**B2, `check_reference_exists.py`.** Sloj provjere citata gledao je samo
ZATVORENOST skupa, pa je izmišljena jedinica koja JE citirana prolazila kao
potpuno čista. Sada se svaka jedinica svrstava po tome čime je potkrijepljena:
građa, identifikator (DOI, valjan ISBN, URL), službena oznaka (NN, ECLI, CELEX,
COM, uredba, presuda) ili NEPOTVRĐENA. Alat ne tvrdi da je nepotvrđena jedinica
izmišljena, nego da ništa u projektu ne pokazuje da postoji. Savjetodavno u modu
4, `--strogo` u modu 6.

**Ograde:** R27–R29 (11 tvrdnji), G7b i G8 u `test_gate.py`.

**Izmjereno na stvarnom radu:** 27 jedinica, 21 s identifikatorom, 6 službenih,
0 nepotvrđenih. Prije zakrpe 80 i 79: 30 „jedinica" i 4 lažno nepotvrđene.

---

## 87–90. drugi stvarni rad, druga vrsta rada

**Rad:** MEDRI, sveučilišni diplomski sanitarnog inženjerstva, empirijski,
14 008 riječi, 11 tablica, uzorak n=172, Vancouver numerički. Dakle sve ono
čega u prvom radu (teorijski, autor-godina) nije bilo.

Prvi prolaz: **0 kritičnih, 15 srednjih, 3 kozmetička**. Kritičnih nije bilo, ali
su tri klase srednjih i kozmetičkih nalaza bile lažne, i sve tri iz koda napisanog
istoga dana.

**87 — crta u umetnutom položaju.** Provjeru je trebalo maknuti, ne popraviti.
U hrvatskom je crta (–) ISPRAVAN znak za umetanje („rad – uz ogradu – pokazuje"),
jednako kao za raspone; nepravilna je duga crtica (—), koje u hrvatskom nema.
Provjera je prijavila 18 ispravnih umetanja. **Pogrešna provjera nije stroža
provjera, nego provjera koja uči autora krivo.**

**88 — veličina podskupine nije proturječje.** `uzorak_nalazi` je hvatao SVAKI
broj uz imenicu, pa je u empirijskom radu s tablicama podskupina prijavljivao
`ispitan: 11, 27, 45, 114, 127, 129` i `sudion: 2, 27, 29, … 172`. To su veličine
podskupina i legitimno se razlikuju. Namjera je bila proturječna veličina UKUPNOG
uzorka, pa broj sada mora stajati u okviru koji govori o cjelini (`OKVIR_UKUPNO`),
a rečenica ne smije nositi oznaku podskupine (`OZNAKA_PODSKUPINE`).

**89 — sitni brojevi se zbrajaju slučajno.** „ukupno 3 = 1 + 1 + 0 + 1" nije skup
kategorija. Prag: ukupno ≥ 20 i svaka kategorija > 0.

**90 — engleska posvojna množina.** Zakrpa 77 je popravila `Orbán’s`, ali ne i
`students’`, `consumers’`, `Scientists’`: apostrof je uvijek IZA slova, a navodnik
je onaj kojemu slovo ne PRETHODI. Druga polovica uvjeta bila je suvišna i lažna.

Poslije: **0 kritičnih, 10 srednjih, 1 kozmetički**, i taj jedan je stvaran
(zatvarajući navodnik U+201C umjesto U+201D, 14×). Prvi rad nepromijenjen
(0 kritičnih), dakle zakrpe nisu zamijenile jedan šum drugim.

**Ograda:** R30 i R31, svaka s oba smjera.

**Pravilo koje iz ovoga slijedi, dopunjeno:** jedan stvarni rad nije dovoljan.
Teorijski rad s autor-godina citiranjem i empirijski rad s tablicama podskupina
pokazuju različite klase lažnih nalaza. Prije nego provjera uđe u blokadu, mora
proći kroz oba tipa.

---

## 91. pravni rad: svaka jedinica iz popisa bila je siroče

**Kad:** 5. 9. 2026. **Kako nađen:** Daniel nije imao pri ruci pravni ni tehnički
rad, pa su izgrađena dva fixturea koja vjerno nose konvencije tih vrsta: pravni s
12 fusnota (ibid., op. cit., nav. dj., loc. cit., supra bilj., NN, ECLI, čl. i st.,
skraćeni oblik) i tehnički s formulama, indeksima, jedinicama (µm, °C, mV/s, Ω cm²),
rasponima s minusom, `10^5` i kemijskim oznakama (Ti-6Al-4V, NaCl).

**Tehnički rad prošao je čisto**, uz jedan istinit nalaz (`10 x 10 x 2 mm`).
Konvencije koje su izgledale rizično (pH 7,4, −1,0 V do +1,5 V, 0,05 µm, ±)
nisu proizvele nijedan lažni nalaz.

**Pravni rad dao je 100 % lažnih kritičnih nalaza.** Rad koji citira U FUSNOTAMA
nema u tijelu ni `[N]` ni `(N)` ni `(Prezime, godina)`, pa je detektor vraćao
„unknown", a `generate_report` je unatoč tome puštao autor-godina provjeru. Ona je
onda **svaku** jedinicu iz popisa proglasila siročetom, jer citata u tijelu doista
nema. Cijeli citatni sloj bio je neupotrebljiv na pravnom radu.

Sada `common.detect_footnote_citing()` traži dvoje istodobno: fusnote nose oznake
fusnotnog aparata, a tijelo NEMA vlastitih oznaka citata. Jedno bez drugoga nije
dovoljno, jer rad s autor-godina citiranjem smije imati i pokoju fusnotu. Kad je
rad fusnotni, sve tri grane provjere citata se preskaču, a izvještaj **imenuje
alat koji je za taj rad ispravan** (`provjeri_fusnote.py`), umjesto da šuti.

Prvi test ove funkcije pao je odmah: brojio je samo zagradne citate, pa je rad s
tri narativna autor-godina citata izgledao kao fusnotni. Narativni se sada broji
jednako.

**Ograda:** R32, četiri tvrdnje (fusnotni jest; autor-godina nije; bez fusnota
nije; fusnota bez citatnog aparata nije).

**Stanje na sva četiri rada:**

| Rad | Kritično | Srednje | Kozmetičko |
|---|---|---|---|
| politička ekonomija (teorijski, autor-godina) | 0 | 3 | 1 |
| Znahor (empirijski, Vancouver, 11 tablica) | 0 | 10 | 1 |
| pravni (fusnotni aparat) | 0 | 0 | 0 |
| tehnički (formule, jedinice) | 0 | 0 | 1 |

---

## 92. najveći izvor šuma u paketu, nađen tek na stvarnom empirijskom radu

**Rad:** HKS, Fakultet zdravstvenih studija, diplomski o palijativnoj skrbi,
11 438 riječi, 12 tablica, 173 Vancouver citata. Prvi rad iz korpusa koji je
dohvaćen iz Drivea, a ne priložen u chatu.

Fusnotno prepoznavanje (kvar 91) potvrđeno je na **stvarnom** pravnom radu:
seminarski s Pravnog fakulteta, 105 fusnota (12 409 znakova: `Ibid.`, `Vidi:`,
`Narodne novine, br. 71/2023`, `Zbornik PFZ, vol. 61, br. 1, 2011., str. 65.`),
bez ijedne oznake citata u tijelu. Prepoznat kao fusnotni, autor-godina siročad
se ne prijavljuje, `provjeri_fusnote.py` uredno pročitao svih 105 i dao dva
smislena savjeta o lancu `ibid.`

Ali medicinski rad je razotkrio nešto veće. Detektor „isti pojam, više
vrijednosti iste jedinice" proizveo je **11 „sukoba", svaki s 12 do 30
vrijednosti**, a ključevi su bili funkcijske riječi:

```
⚠ 'samo' + %: 12,6, 13,8, 15,9, 18, 23,5, 29,1, 31,0, 32,0, 32,2, 35, 37,4, …
⚠ 'odnosno' + %: 3,63, 12,7, 13,8, 38,9, 41,5, 43,6, 50, 54,1, 65,7, 70,5, …
⚠ 'naspram' + %: 6,2, 46,7, 48,1, 62,1, 80,0
⚠ 'godina' + %: 28,1, 29, 30, 39, 42, 43,1, 45, 45,8, 46,7, 48,1, 50,7, 56, …
```

Nijedan nije bio nalaz. U empirijskom radu postoci se **po definiciji**
razlikuju; skup od dvadeset vrijednosti nije proturječje nego raspodjela. Ovo je
kod koji je u paketu stajao od početka, dakle nije nastao u ovom ciklusu, i
upravo zato je opasan: šum koji je uvijek bio ondje uči autora da preskoči
srednju kategoriju u cijelosti.

Tri ograde, sve tri nužne: ključ ne smije biti funkcijska riječ (ona stoji uz
svaki broj), skup od više od tri vrijednosti je raspodjela i ne prijavljuje se
(ali se BROJI i izgovara), ključ mora biti dulji od tri znaka.

**Izmjereno:** HKS s 16 srednjih nalaza na 5, i svih pet je stvarno
(`updateFields: NE`; dva skupa kategorija bez uputnice; 7 postotaka bez razmaka
naspram 193 s razmakom). Pravni rad zadržao je oba svoja nalaza, jer su ondje
ključevi sadržajni pojmovi s po dvije vrijednosti.

**Ograda:** R33, oba smjera (osam postotaka uz „samo" nije sukob; dvije
vrijednosti uz sadržajni pojam jest).

---

## Korpus na kojem je lanac provjeren

| Rad | Tip | Citiranje | Kritično | Srednje |
|---|---|---|---|---|
| politička ekonomija (FPZG) | teorijski | autor-godina | 0 | 3 |
| Znahor (MEDRI) | empirijski, 11 tablica | Vancouver | 0 | 10 |
| palijativna skrb (HKS) | empirijski, 12 tablica | Vancouver, 173 citata | 0 | 5 |
| obiteljsko pravo (PFZG) | pravni | 105 fusnota | 0 | 6 |
| tehnički fixture | formule, jedinice | autor-godina | 0 | 0 |
| pravni fixture | 12 fusnota | fusnotni aparat | 0 | 0 |

Četiri stvarna rada iz četiri različita fakulteta i tri različita stila
citiranja. Svaki od njih otkrio je barem jedan kvar koji ostali nisu.

---

## 93–97. tehnički radovi: popis literature u tri neprepoznata oblika

**Radovi:** `Uvod i teorija` (čelične konstrukcije, S235/S355, IEEE `[N]`, 3 749
riječi) i `Seminar - FER` (komercijalizacija inovacija, autor-godina, 3 922
riječi, 4 tablice). Peti i šesti stvarni rad, i prvi s IEEE stilom.

Prvi prolaz: FER seminar **16 kritičnih nalaza „citat bez reference"**, a svaka
je jedinica bila uredno u popisu. Uzrok: raščlamba popisa poznavala je samo
godinu u zagradi u prvih 120 znakova retka. Tri oblika koje nije poznavala, sva
tri uobičajena u hrvatskim tehničkim i medicinskim popisima:

| Kvar | Oblik | Primjer |
|---|---|---|
| 93 | godina na kraju retka | `Hrvatski zavod za javno zdravstvo. Atlas. Zagreb: HZJZ, 2024.` |
| 93 | naziv institucije s malim riječima u sredini | `Državni zavod za statistiku. Istraživanje…` |
| 97 | godina uz broj sveska, iza nje stranice | `Medicina Fluminensis. Vol. 57, br. 4(2021), str. 328–340.` |

**94 — akronim u nakladničkom dijelu.** Institucija se u tekstu citira akronimom
(`DZS, 2024`, `HZJZ, 2024`, `WIPO, 2025`), a u popisu je raspisana, s akronimom
tek iza mjesta izdanja. Alias je dotad hvatao samo akronim u zagradi uz autora.
Prvi pokušaj zakrpe uzimao je **svaku veliku riječ retka**, pa je `Ljetopis` iz
naslova postao alias i odmah oborio postojeći test R13. Traži se isključivo
akronim.

**95 — hrvatski izvor prikaza.** `(autorski sažetak prema: Podobnik, 2026)` i
`(autorska analiza prema: Porter, 2008)` davali su ključ `autorski`, jer je
uzorak skidao samo golo „prema" na početku segmenta.

**96 — razlika izrečena u istoj rečenici.** „Čelik S355 nije krući od čelika
S235" nosi obje vrijednosti u istoj rečenici, dakle razlika je izrečena i pitanje
„je li razlika deklarirana" ima odgovor u samom tekstu. Isto za visinu na strehi
i na sljemenu (4,50 m i 6,50 m).

**Izmjereno:** FER seminar 16 kritičnih na 0; čelične konstrukcije 5 srednjih na
1. Preostali jedan nalaz na čeličnim konstrukcijama je **istinit**: redoslijed
prvog pojavljivanja IEEE navoda je 1, 2, **4, 3**, 5, dakle `[4]` stoji prije
`[3]`, što u numeriranju po pojavljivanju treba prenumerirati.

**Ograda:** R34, jedanaest tvrdnji, uključujući negativnu (`autorska` ne smije
biti ključ) i test da alias ne nastaje iz naslova.

---

## Korpus na kojem je lanac provjeren (šest radova, pet fakulteta, četiri stila)

| Rad | Tip | Citiranje | Kritično | Srednje |
|---|---|---|---|---|
| politička ekonomija (FPZG) | teorijski | autor-godina | 0 | 3 |
| Znahor (MEDRI) | empirijski, 11 tablica | Vancouver | 0 | 9 |
| palijativna skrb (HKS) | empirijski, 12 tablica | Vancouver, 173 citata | 0 | 5 |
| obiteljsko pravo (PFZG) | pravni | 105 fusnota | 0 | 4 |
| čelične konstrukcije | tehnički | IEEE `[N]` | 1 (istinit) | 1 |
| komercijalizacija (FER) | pregledni | autor-godina | 0 | 2 |

**Svaki od šest radova otkrio je barem jedan kvar koji nijedan drugi nije.**
To više nije dojam nego mjerenje: teorijski rad dao je posvojne pridjeve,
empirijski veličine podskupina i raspodjele postotaka, pravni fusnotni aparat,
tehnički tri oblika bibliografske jedinice.

---

## 98–104. audit paketa nakon rada Znahor

Izvor: `AUDITskillovanakonradaZnahor.md`, napisan poslije stvarne sesije na
diplomskom radu MEDRI (8 297 → 13 830 riječi, 50 stranica, 11 tablica, 56 referenci).
Nalazi su tamo podijeljeni po tome **tko griješi**, i to je razlikovanje zadržano.

### Zajednički obrazac triju kvarova

Autor audita ga imenuje točno: **alat mjeri pogrešnu razinu dokumenta.** Prored se
čita iz stila `Normal` umjesto iz odlomka koji nosi sliku; numeracija iz posljednje
sekcije umjesto iz one u kojoj kreće; marker se uspoređuje doslovno iako je zahvat
tipografski. Nije riječ o tri neovisna buga nego o jednoj navici: **uzeti prvi
dohvatljivi nositelj svojstva umjesto onoga koji svojstvo stvarno nosi.**

| Kvar | Alat | Što je bilo | Što je sada |
|---|---|---|---|
| 98 | `check_paragraphs.py` | profil bez `format.odlomak` → `ap.error`, kod 2, trajno „alat pukao" | kod 3 = preskočeno, deklarirana granica (pravilo 20) |
| 99 | `verify_rewrite.py` | marker se uspoređuje doslovno, pa tipografski popravak (NBSP, dvostruki razmak) blokira sam sebe | pod `--zahvat stil` bjelina se normalizira; pod `lomljenje` i `geometrija` marker ostaje doslovan |
| 100 | `provjeri_predaju.py` | numeracija se tražila u `sekcije[-1]`, a to je u radu s 12 sekcija prilog | traži se sekcija koja numeraciju RESTARTA, u bilo kojoj poziciji |
| 101 | `provjeri_predaju.py` | „prored je fiksan — inline slike se obrežu" i kad nijedna slika nije u fiksno prorezanom odlomku | nalaz samo za odlomke koji STVARNO nose sliku; inače upozorenje |
| 102 | `check_typography.py` | bezuvjetno tražen zatvarajući U+201D | dijalekt `ihjj` / `njem`, kao Vancouver u `citation_dialects.py`; nalaz je NEDOSLJEDNOST, ne izbor |
| 103 | `provjeri_prikaze.py` | nijedan alat nije gledao ŠTO je u slici | `_rub_odrezan()`: ne-bijeli pikseli na rubu platna |
| 104 | `inventar_paketa.py` | mrtvi medijski dijelovi nevidljivi | `mrtvi_mediji()` + `tezina()` + `priprema_slanja.py` |

### 103 — jedina rupa koju je našlo oko, a ne alat

Legenda grafikona „zeleno: unutar sigurnog prostora" izašla je iz platna i u radu
je pisalo `zeleno: unutar sigurnog pros`. Rad je prošao `provjeri_prikaze.py`,
`gate --faza audit`, sve faze rad-audita i `provjeri_predaju.py`. Nijedan alat to
nije vidio jer **svi mjere sliku kao pravokutnik** (dpi, širina, omjer, skala), a
nijedan ne gleda sadržaj. `matplotlib` odsijeca tiho: bez upozorenja, bez iznimke,
bez traga u datoteci.

Provjereno na fixtureu s dvije slike: pogodila je točno onu odrezanu
(`lijevo 16 px, gore 16 px, dolje 14 px`), a čistu je pustila. Granica je
deklarirana: grafikon s punim pozadinskim ispunom (heatmap, fotografija) pali ovo
uvijek, pa postoji `--dopusti-rub` umjesto tihog gašenja.

### 104 — 749 kB nevidljivog sadržaja

Zamjena slike ostavlja stari PNG u `word/media/`: relacija ostaje, referenca u
`document.xml` nestaje. Na stvarnom radu **49 % datoteke**. Uz težinu nosi i
**staru verziju grafikona**, dostupnu svakome tko raspakira .docx — za rad koji ide
na provjeru podudarnosti i u repozitorij to je sadržaj, ne higijena.
`priprema_slanja.py` piše ZASEBNU izlaznu datoteku; arhivska verzija ostaje
netaknuta.

### Doktrina koja je iz audita ušla u reference

* `predaja.md` — **opseg se mjeri, ne procjenjuje** (izmjereno: prikazi su nosili
  5 od 29 stranica koje je trebalo skratiti; pretpostavka bi stajala dan) i
  **rad koji se ne može poslati nije predan** (1,5 MB ne prolazi kroz e-poštu).
* `stil_pipeline.md` — **stilske dimenzije su spregnute** (skraćivanje rečenica
  srušilo koheziju s 15+ na 13,4 i podiglo dvotočja na 3,9/1000) i **strojni stil
  ne hvata kvarove koje sam zahvat proizvodi** (metrika kohezije mjeri prisutnost
  veznih sredstava, pa je zahvat koji ih umeće prazno formalno poboljšanje).
* `pisanje.md` — **redoslijed zahvata je lanac ovisnosti**: renumeracija →
  zamjena teksta → tipografija → naslovnice → sekcije → polja.
* `docx_zamke.md` (nova) — šest zamki, među njima najskuplja: `doc.paragraphs`
  gradi NOVE omotače, pa `if p is sadrzaj` nikad nije istina i kod pisan da nešto
  preskoči obriše sve. U stvarnoj sesiji obrisalo je 489 odlomaka.

### Profil `mefri-sanitarno`

Napravljen iz Naputka MEDRI 2025./2026. (12 pt, rubnici 2,5 cm, dvostruki prored,
broj stranice donji desni kut, naslovi tablica iznad a slika ispod, Vancouver po
redoslijedu pojavljivanja, sažetak ≤ 250 riječi, 15–50 stranica od Uvoda nadalje).
Status `nepotvrdeno`, jer je dokument čitan preko sažimača: izravno preuzimanje
nije prošlo kroz proxy i **egress nije zaobiđen**.

Trošak nepostojanja profila je izmjeren u auditu: bez `resolved_profile.json` gate
je preskočio **4 od 15 koraka**, uključujući jedan blokirajući, a sažetak je i dalje
govorio „nijedna blokirajuća provjera nije pala". Taj je dio popravljen kvarom 58.

Profil zasad stoji kao datoteka, kao i `hks-fzs`, i **nije upisan u registry**:
`profile_registry.py --write` odbija generirati jer je admission bundle hash za
`efzg` zastario. To se ne zaobilazi; upis u registry je zaseban zahvat koji počinje
ponovnim pokretanjem `faculty_scale_gate.py`.

---

## 105. metapodaci: cijela razina dokumenta koju nitko nije gledao

Lanac je čitao tekst, brojke, citate, polja, slike i paket. `docProps/` nije
gledao nitko. Provjereno na svih šest radova iz korpusa: **nijedan nije bio čist**,
a dva su nosila podatak koji ondje nema što raditi (`app.Company` = „HT",
`lastModifiedBy` = „Provenance Test Generator").

Nova faza **A4**, `rad-audit/scripts/provjeri_metapodatke.py`, u
`generate_report`, `audit_all` i kao blokirajući korak faze predaja.

Prijavljuje: ostavljene predloške (`Student`, `PC`), tragove alata i radne
okoline, naziv tvrtke i upravitelja, tuđi predložak, lokalne putanje u
relacijama, autore praćenih izmjena i komentara, prazan `dc:title`, zastarjelu
statistiku (`Pages` = 1 u radu od 67 stranica), zaglavljen ili nulti `TotalTime`,
i **razilaženje `dc:creator` s imenom na naslovnici**.

`--postavi` piše u NOVU datoteku i ne dira `word/document.xml` (test to tvrdi
usporedbom bajtova), pa `rsid` oznake i povijest izmjena ostaju. To je namjerno:
one se rješavaju prihvaćanjem izmjena, ne brisanjem.

**Usput nađeno:** generički placeholder predloška u uglatoj zagradi. Prva izvedba
uzorka („svaka uglata zagrada s riječima") dala je na Vancouver radu **12 lažnih
nalaza**, jer je `[Internet]` standardna oznaka vrste izvora u tom stilu. Uzorak
sada traži RIJEČ IZ PREDLOŠKA (ime, prezime, datum, mentor, upisati…), ne oblik
zagrade. Time je nađeno `[Ime i prezime]` na naslovnici pravnog seminara i
`[upisati vrijednost]` u gotovu diplomskom radu s HKS-a.

**Ograda:** R36, četrnaest tvrdnji, uključujući negativne ([Internet], [12, 13],
[3] nisu placeholderi) i tvrdnju da `--postavi` ne mijenja `document.xml`.

        Korak("metapodaci", "što dokument o sebi govori u docProps/",
              ["<RAD_AUDIT>/scripts/provjeri_metapodatke.py", rad,
               "--json", os.path.join(kat, "metapodaci.json")],
              treba=[rad], satelit="rad-audit",
              zasto="metapodaci putuju u repozitorij i na provjeru podudarnosti, "
                    "a u Wordu se ne vide dok se ne otvore Podaci"),
    check("G8: faza predaja provjerava metapodatke",
          "metapodaci" in kidovi, sorted(kidovi))
import provjeri_metapodatke
    run("A4 — METAPODACI", provjeri_metapodatke.main, [path])
    # Nađeno na stvarnom pravnom seminaru: naslovnica je i dalje nosila
    # „[Ime i prezime]". Prva izvedba uzorka bila je preširoka („svaka uglata
    # zagrada s riječima") i na Vancouver radu prijavila 12 lažnih nalaza, jer je
    # „[Internet]" standardna oznaka vrste izvora u tom stilu. Zato se traži
    # RIJEČ IZ PREDLOŠKA, ne oblik zagrade.
    (r"\[[^\]]{0,30}\b(?i:ime|prezime|naslov rada|datum|mentor|komentor|ustanova|"
     r"kolegij|broj indeksa|upi[šs]i|upisati|unesi|unijeti|vaše|tvoje|ovdje)"
     r"[^\]]{0,30}\]", "nepopunjeno polje predloška"),
 "engine_version": "0.0.0-undeclared+2b35822d",
import provjeri_metapodatke
    # metapodaci koji putuju s radom
    "odaje alat ili radnu okolinu", "ostavljen predložak, ne ime",
    "nema što raditi u studentskom radu", "polje iz poslovnog predloška",
    "metapodatak i rad ne govore isto", "odaju mapu s računala",
    "praćene izmjene ili komentari nose imena", "nepopunjeno polje predloška",
    # Faza A4: metapodaci putuju s dokumentom u repozitorij i na provjeru
    # podudarnosti, a nitko ih u Wordu ne vidi dok ne otvori Datoteka → Podaci.
    txt, code = run_captured(provjeri_metapodatke.main, [path])
    phases.append(("A4 — Metapodaci", txt, code))

#!/usr/bin/env python3
"""Faza A4 — metapodaci .docx-a: što dokument o sebi govori kad ga nitko ne čita.

Uporaba:
  python3 provjeri_metapodatke.py rad.docx
  python3 provjeri_metapodatke.py rad.docx --autor "Ime Prezime" --naslov "…" --postavi
  python3 provjeri_metapodatke.py rad.docx --json .katedra/metapodaci.json

Zašto postoji
-------------
Cijeli lanac čita tekst, brojke, citate i polja. Nitko dosad nije pogledao
`docProps/`. Izmjereno na šest stvarnih radova, i nijedan nije bio čist:

* `cp:lastModifiedBy` = „Provenance Test Generator" u radu koji ide mentorici;
* `app.Company` = „HT" u studentskom seminarskom radu (ime poslodavca);
* `dc:creator` = „Student", `lastModifiedBy` = „PC" (ostavljeni predlošci);
* `app.Pages` = 1 u radu od 67 stranica (zastarjela statistika koju Word prikaže);
* `app.TotalTime` = 0 u diplomskom od 50 stranica, i 21 474 (358 sati) u drugom;
* `dc:title` prazan ili zaostao iz radne verzije („poglavlja 1–3" u gotovu radu).

Ovo su podaci koji putuju s dokumentom u repozitorij, na provjeru podudarnosti i
u mentoričin inbox. Nitko ih ne vidi u Wordu dok ne otvori Datoteka → Podaci.

Što alat radi i što NE radi
---------------------------
RADI: čita i prijavljuje, i s `--postavi` upisuje polja koja mu se izrijekom
zadaju (autor, naslov, tema, ključne riječi), te s `--ocisti-curenje` uklanja
ono što u radu nema što raditi: naziv tvrtke, upravitelja, naziv predloška koji
nije `Normal`, lokalne putanje i tragove alata iz `lastModifiedBy`.

NE RADI: ne dira `w:rsid` oznake, povijest praćenih izmjena ni autore komentara.
Te se stavke PRIJAVLJUJU da autor zna da postoje, i uklanjaju se prihvaćanjem
izmjena (`revizije.py prihvati`), ne brisanjem tragova. Alat koji bi ih brisao
služio bi jednoj svrsi: onemogućavanju provjere podrijetla dokumenta.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from xml.etree import ElementTree as ET

NS = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dcterms": "http://purl.org/dc/terms/",
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
}
for k, v in NS.items():
    ET.register_namespace(k, v)

# Nizovi koji odaju alat ili radnu okolinu, a ne autora.
TRAGOVI_ALATA = re.compile(
    r"(?i)(generator|python|docx|script|test|template|admin|user\b|pc\b|laptop|"
    r"desktop|localhost|claude|gpt|openai|anthropic|bot\b)")
PLACEHOLDER = {"student", "pc", "user", "korisnik", "autor", "ime prezime",
               "ime i prezime", "n.n.", "unknown", "nepoznato"}


def _core(z):
    try:
        return ET.fromstring(z.read("docProps/core.xml"))
    except KeyError:
        return None


def _app(z):
    try:
        return ET.fromstring(z.read("docProps/app.xml"))
    except KeyError:
        return None


def _t(el):
    return (el.text or "").strip() if el is not None else ""


def procitaj(put: str) -> dict:
    out = {"core": {}, "app": {}, "tragovi": {}, "custom": False}
    with zipfile.ZipFile(put) as z:
        imena = z.namelist()
        c = _core(z)
        if c is not None:
            for polje, staza in [
                ("autor", "dc:creator"), ("zadnji_uredio", "cp:lastModifiedBy"),
                ("naslov", "dc:title"), ("tema", "dc:subject"),
                ("kljucne_rijeci", "cp:keywords"), ("opis", "dc:description"),
                ("kategorija", "cp:category"), ("revizija", "cp:revision"),
                ("nastalo", "dcterms:created"), ("mijenjano", "dcterms:modified"),
                ("zadnje_ispisano", "cp:lastPrinted"),
            ]:
                out["core"][polje] = _t(c.find(staza, NS))
        a = _app(z)
        if a is not None:
            for tag in ("Application", "AppVersion", "Company", "Manager", "Template",
                        "TotalTime", "Pages", "Words", "Characters"):
                out["app"][tag] = _t(a.find(f"ep:{tag}", NS))
        out["custom"] = "docProps/custom.xml" in imena
        doc = z.read("word/document.xml").decode("utf-8", "ignore")
        out["tragovi"] = {
            "autori_izmjena": sorted(set(re.findall(r'w:author="([^"]+)"', doc))),
            "rsid_sesija": len(set(re.findall(r'w:rsid[A-Za-z]*="([0-9A-Fa-f]{8})"', doc))),
            "ima_comments": "word/comments.xml" in imena,
            "ima_people": "word/people.xml" in imena,
        }
        putanje = []
        for dio in imena:
            if dio.endswith(".rels"):
                r = z.read(dio).decode("utf-8", "ignore")
                putanje += re.findall(r'Target="(file:[^"]+|[A-Za-z]:\\[^"]+)"', r)
        out["tragovi"]["lokalne_putanje"] = sorted(set(putanje))[:10]
    return out


def ime_s_naslovnice(put: str) -> str:
    """Ime koje rad SAM navodi kao autora, iz prvih odlomaka naslovnice."""
    try:
        from docx import Document
    except ImportError:
        return ""
    d = Document(put)
    redci = [p.text.strip() for p in d.paragraphs[:40] if p.text.strip()]
    for i, r in enumerate(redci):
        if re.fullmatch(r"(?i)(ime i prezime|student(ica)?|autor(ica)?)\s*:?", r) and i + 1 < len(redci):
            return redci[i + 1]
        m = re.match(r"(?i)^(?:student(?:ica)?|autor(?:ica)?)\s*:\s*(.+)$", r)
        if m:
            return m.group(1).strip()
    # inače: prvi redak od dvije do tri riječi s velikim početnim slovima
    for r in redci[:20]:
        rijeci = r.split()
        if 2 <= len(rijeci) <= 3 and all(w[:1].isupper() for w in rijeci) \
                and not re.search(r"(?i)sveučilište|fakultet|studij|zagreb|rijeka|osijek|split", r):
            return r
    return ""


def nalazi(m: dict, deklarirani_autor: str = "") -> list[tuple[str, str]]:
    """[(težina, poruka)]; težina je 'g' greška, 'u' upozorenje, 'o' granica."""
    n = []
    c, a, tr = m["core"], m["app"], m["tragovi"]

    for polje, opis in [("autor", "dc:creator"), ("zadnji_uredio", "cp:lastModifiedBy")]:
        v = c.get(polje, "")
        if not v:
            n.append(("u", f"{opis} je prazan — dokument ne navodi {opis.split(':')[1]}"))
            continue
        if v.strip().lower() in PLACEHOLDER:
            n.append(("g", f"{opis} = „{v}” je ostavljen predložak, ne ime"))
        elif TRAGOVI_ALATA.search(v):
            n.append(("g", f"{opis} = „{v}” odaje alat ili radnu okolinu, "
                           f"a ne autora rada"))

    if deklarirani_autor:
        aut = (c.get("autor") or "").strip()
        if aut and aut.lower() not in PLACEHOLDER and not TRAGOVI_ALATA.search(aut):
            prez_meta = {w.lower().strip(",.") for w in aut.split()}
            prez_nasl = {w.lower().strip(",.") for w in deklarirani_autor.split()}
            if not (prez_meta & prez_nasl):
                n.append(("g", f"dc:creator = „{aut}”, a naslovnica navodi "
                               f"„{deklarirani_autor}” — metapodatak i rad ne govore isto"))

    if not c.get("naslov"):
        n.append(("u", "dc:title je prazan — repozitoriji ga često preuzimaju kao naslov"))

    if a.get("Company"):
        n.append(("g", f"app.Company = „{a['Company']}” — naziv tvrtke nema što raditi "
                       f"u studentskom radu"))
    if a.get("Manager"):
        n.append(("g", f"app.Manager = „{a['Manager']}” — polje iz poslovnog predloška"))
    if a.get("Template") and a["Template"] != "Normal":
        n.append(("u", f"app.Template = „{a['Template']}” — odaje predložak iz kojeg je "
                       f"dokument nastao"))

    tt = a.get("TotalTime")
    if tt and tt.isdigit():
        minuta = int(tt)
        if minuta == 0:
            n.append(("u", "app.TotalTime = 0 — dokument tvrdi da nije uređivan ni minutu"))
        elif minuta > 20000:
            n.append(("u", f"app.TotalTime = {minuta} min ({minuta / 60:.0f} h) — "
                           f"brojač je zaglavljen, Word ga prikazuje u Podacima"))

    if a.get("Pages", "").isdigit() and int(a["Pages"]) <= 1:
        n.append(("u", f"app.Pages = {a['Pages']} — zastarjela statistika; osvježi je "
                       f"otvaranjem i spremanjem u Wordu"))

    if c.get("nastalo") and c.get("nastalo") == c.get("mijenjano"):
        n.append(("o", "dcterms:created = dcterms:modified — dokument je generiran, "
                       "ne uređivan; to je točan opis stanja, ne kvar"))

    if tr["autori_izmjena"]:
        n.append(("g", f"praćene izmjene ili komentari nose imena: "
                       f"{', '.join(tr['autori_izmjena'])} — prihvati izmjene "
                       f"(revizije.py prihvati) prije predaje"))
    if tr["ima_comments"] or tr["ima_people"]:
        n.append(("u", "dokument nosi komentare (word/comments.xml) — provjeri je li to "
                       "namjerno prije predaje"))
    if tr["lokalne_putanje"]:
        n.append(("g", f"lokalne putanje u relacijama: {tr['lokalne_putanje'][0]} "
                       f"(ukupno {len(tr['lokalne_putanje'])}) — odaju mapu s računala"))
    if m["custom"]:
        n.append(("u", "docProps/custom.xml postoji — prilagođena svojstva se rijetko "
                       "postavljaju namjerno"))
    return n


def postavi(put: str, izlaz: str, polja: dict, ocisti_curenje: bool) -> list[str]:
    """Upiši zadana polja i, po izboru, ukloni ono što curi. Vrati popis promjena."""
    promjene = []
    tmp = tempfile.mkdtemp(prefix="meta-")
    try:
        with zipfile.ZipFile(put) as z:
            z.extractall(tmp)
        core_put = os.path.join(tmp, "docProps", "core.xml")
        if os.path.exists(core_put):
            c = ET.parse(core_put)
            root = c.getroot()
            staze = {"autor": "dc:creator", "naslov": "dc:title", "tema": "dc:subject",
                     "kljucne_rijeci": "cp:keywords", "zadnji_uredio": "cp:lastModifiedBy"}
            for polje, vrijednost in polja.items():
                if vrijednost is None:
                    continue
                staza = staze.get(polje)
                el = root.find(staza, NS)
                if el is None:
                    pre, tag = staza.split(":")
                    el = ET.SubElement(root, f"{{{NS[pre]}}}{tag}")
                el.text = vrijednost
                promjene.append(f"{staza} = „{vrijednost}”")
            c.write(core_put, xml_declaration=True, encoding="UTF-8")

        app_put = os.path.join(tmp, "docProps", "app.xml")
        if ocisti_curenje and os.path.exists(app_put):
            a = ET.parse(app_put)
            root = a.getroot()
            for tag in ("Company", "Manager"):
                el = root.find(f"ep:{tag}", NS)
                if el is not None and (el.text or "").strip():
                    promjene.append(f"uklonjeno app.{tag} = „{el.text.strip()}”")
                    root.remove(el)
            el = root.find("ep:Template", NS)
            if el is not None and (el.text or "").strip() not in ("", "Normal"):
                promjene.append(f"app.Template „{el.text.strip()}” → Normal")
                el.text = "Normal"
            a.write(app_put, xml_declaration=True, encoding="UTF-8")

        if os.path.exists(izlaz):
            os.remove(izlaz)
        zf = zipfile.ZipFile(izlaz, "w", zipfile.ZIP_DEFLATED)
        for korijen, _d, fajlovi in os.walk(tmp):
            for fn in fajlovi:
                fp = os.path.join(korijen, fn)
                zf.write(fp, os.path.relpath(fp, tmp))
        zf.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return promjene


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Metapodaci .docx-a: pročitaj, prijavi, uskladi.")
    ap.add_argument("rad")
    ap.add_argument("--autor")
    ap.add_argument("--naslov")
    ap.add_argument("--tema")
    ap.add_argument("--kljucne-rijeci", dest="kljucne_rijeci")
    ap.add_argument("--postavi", action="store_true",
                    help="upiši zadana polja u NOVU datoteku (--izlaz)")
    ap.add_argument("--ocisti-curenje", dest="ocisti_curenje", action="store_true",
                    help="ukloni Company, Manager i naziv predloška")
    ap.add_argument("--izlaz", help="izlazna datoteka za --postavi (zadano: rad-meta.docx)")
    ap.add_argument("--json", dest="json_out")
    a = ap.parse_args(argv)

    if not os.path.isfile(a.rad):
        print(f"❌ nema datoteke: {a.rad}", file=sys.stderr)
        return 2

    m = procitaj(a.rad)
    deklarirani = ime_s_naslovnice(a.rad)
    n = nalazi(m, deklarirani)

    print("=" * 62)
    print("A4 — METAPODACI —", os.path.basename(a.rad))
    print("=" * 62)
    for polje, v in m["core"].items():
        if v:
            print(f"  {polje:16} {v[:80]}")
    for tag, v in m["app"].items():
        if v:
            print(f"  app.{tag:12} {v[:60]}")
    if deklarirani:
        print(f"  {'naslovnica':16} {deklarirani}")
    print(f"  {'rsid sesija':16} {m['tragovi']['rsid_sesija']}")

    greske = [x for t, x in n if t == "g"]
    upoz = [x for t, x in n if t == "u"]
    gran = [x for t, x in n if t == "o"]
    for naslov, popis, znak in [("PODACI KOJI NE SMIJU OTIĆI S RADOM", greske, "⚠"),
                                ("PROVJERI PRIJE PREDAJE", upoz, "⚠"),
                                ("GRANICE", gran, "ℹ️")]:
        if popis:
            print(f"\n{znak} {naslov} ({len(popis)}):")
            for x in popis:
                print(f"   • {x}")
    if not (greske or upoz):
        print("\n✅ metapodaci ne odaju ništa što rad ne bi trebao nositi")

    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump({**m, "naslovnica": deklarirani,
                       "nalazi": [{"tezina": t, "poruka": x} for t, x in n]},
                      fh, ensure_ascii=False, indent=2)

    if a.postavi or a.ocisti_curenje:
        izlaz = a.izlaz or (os.path.splitext(a.rad)[0] + "-meta.docx")
        if os.path.abspath(izlaz) == os.path.abspath(a.rad):
            print("❌ izlaz ne smije biti isti kao ulaz", file=sys.stderr)
            return 2
        polja = {"autor": a.autor, "naslov": a.naslov, "tema": a.tema,
                 "kljucne_rijeci": a.kljucne_rijeci}
        promjene = postavi(a.rad, izlaz, polja, a.ocisti_curenje)
        print(f"\n✔ {izlaz}")
        for p in promjene:
            print(f"   {p}")
        print("   Praćene izmjene, autori komentara i rsid oznake NISU dirane: "
              "one se rješavaju prihvaćanjem izmjena, ne brisanjem tragova.")
        return 0

    return 1 if greske else 0


if __name__ == "__main__":
    sys.exit(main())
    # 105 — metapodaci (faza A4)
    import os as _os
    import tempfile as _tf
    import zipfile as _zf
    import provjeri_metapodatke as MP
    import check_placeholders as PH2
    from docx import Document as _Doc

    def _s_meta(put, **polja):
        d = _Doc()
        d.add_paragraph("Sveu\u010dili\u0161te u Zagrebu")
        d.add_paragraph("Ana Ani\u0107")
        d.add_heading("1. UVOD", level=1)
        d.add_paragraph("Tekst rada.")
        d.core_properties.author = polja.get("autor", "")
        d.core_properties.last_modified_by = polja.get("zadnji", "")
        d.core_properties.title = polja.get("naslov", "")
        d.save(put)
        return put

    with _tf.TemporaryDirectory() as dd:
        r1 = _s_meta(_os.path.join(dd, "a.docx"),
                     autor="Ana Ani\u0107", zadnji="Provenance Test Generator",
                     naslov="Naslov")
        n1 = MP.nalazi(MP.procitaj(r1), "Ana Ani\u0107")
        poruke = " | ".join(x for _t, x in n1)
        check("R36: trag alata u lastModifiedBy je gre\u0161ka",
              any(t == "g" and "odaje alat" in x for t, x in n1), poruke)

        r2 = _s_meta(_os.path.join(dd, "b.docx"),
                     autor="Student", zadnji="PC", naslov="Naslov")
        n2 = MP.nalazi(MP.procitaj(r2), "Ana Ani\u0107")
        check("R36: ostavljeni predlo\u017eak (Student/PC) je gre\u0161ka",
              sum(1 for t, x in n2 if t == "g" and "predlo\u017eak" in x) == 2,
              [x for t, x in n2])

        r3 = _s_meta(_os.path.join(dd, "c.docx"),
                     autor="Marko Marki\u0107", zadnji="Marko Marki\u0107", naslov="Naslov")
        n3 = MP.nalazi(MP.procitaj(r3), "Ana Ani\u0107")
        check("R36: autor u metapodacima \u2260 naslovnica je gre\u0161ka",
              any("ne govore isto" in x for _t, x in n3), [x for t, x in n3])

        n4 = MP.nalazi(MP.procitaj(r1), "Ana Ani\u0107")
        check("R36: uskla\u0111en autor NIJE nalaz",
              not any("ne govore isto" in x for _t, x in n4), [x for t, x in n4])

        # --postavi piše u NOVU datoteku i ne dira tragove
        izl = _os.path.join(dd, "a-meta.docx")
        MP.postavi(r1, izl, {"zadnji_uredio": "Ana Ani\u0107"}, True)
        check("R36: --postavi ostavlja izvornik netaknut", _os.path.exists(r1))
        check("R36: --postavi pi\u0161e novu datoteku", _os.path.exists(izl))
        m_novi = MP.procitaj(izl)
        check("R36: upisano lastModifiedBy",
              m_novi["core"]["zadnji_uredio"] == "Ana Ani\u0107", m_novi["core"])
        with _zf.ZipFile(r1) as z1, _zf.ZipFile(izl) as z2:
            check("R36: document.xml NIJE diran (rsid i izmjene ostaju)",
                  z1.read("word/document.xml") == z2.read("word/document.xml"))

    # 105b — placeholder predloška: oba smjera
    for tekst, treba in [("[Ime i prezime]", True), ("[Datum obrane]", True),
                         ("[Internet]", False), ("[12, 13]", False), ("[3]", False),
                         ("[zavr\u0161ni rad]", False)]:
        import re as _re
        uz = [u for u, _o in PH2.UZORCI if "ime|prezime" in u][0]
        check(f"R36: placeholder {tekst} \u2192 {treba}",
              bool(_re.search(uz, tekst)) == treba, tekst)

## 106–107. zatvaranje popisa iz prve dijagnoze
U prvoj dijagnozi ovoga ciklusa (nalaz 6) stajalo je da `parafraza.py`,
`propagacija.py` i `brojke_iz_rasprave.py` postoje i rade, ali nisu ožičeni ni u
jedan agregat. To je ostalo otvoreno kroz cijeli ciklus, unatoč tome što je bilo
zapisano. Zatvoreno je tek kad je postavljeno pitanje „jesmo li pokrili sve".

* `brojke_iz_rasprave` → faza **C2** u `generate_report` i `audit_all`.
* `propagacija` i `parafraza` **ostaju izvan audita namjerno**: prva traži
  rukopis i generator, druga dvije verzije istoga teksta. To nisu ulazi koje
  audit gotova .docx-a ima, pa bi ožičenje značilo lažnu fazu koja uvijek
  preskače. Zovu se iz moda 3 (poboljšanje), gdje ti ulazi postoje.

**106 — nova provjera F2, `check_uputnice.py`.** Lanac je provjeravao da svaki
prikaz ima natpis, da je numeracija neprekinuta i da popis prikaza odgovara
tijelu. Obrnuti smjer nije provjeravao nitko: da rečenica „prikazano je u
Tablici 3" pogađa tablicu koja postoji, i da svaki prikaz bude bar jednom uveden
rečenicom.

Na dva stvarna rada odmah je našla nespomenute prikaze (Grafikon 1 i Tablica 3 u
radu iz političke ekonomije).

Prva izvedba je pritom **sama proizvela lažni nalaz**: uzorak `Slik\w*` ne hvata
lokativ `Slici`, jer hrvatska sibilarizacija mijenja k u c. Rad je uredno pisao
„prikazana je na Slici 3", a alat je prijavio da se Slika 3 nigdje ne spominje.
Ispravljeno u `Sli[kc]\w*`.

**107 — kod 3 je granica, kod 2 je pad.** `brojke_iz_rasprave` vraćao je 2 kad
rad nema poglavlje „Rasprava". Po pravilu iz kvara 61 `generate_report` svaki kod
≥ 2 svrstava u KRITIČNO „faza nije izvedena", pa su **četiri od šest stvarnih
radova** dobila lažni kritični nalaz čim je faza C2 ožičena. Teorijski, pravni i
pregledni rad nemaju zasebnu Raspravu i to nije kvar nego njihova struktura.
Sada: kod 3 = deklarirana granica (srednje), kod 2 i više = pad alata (kritično).

**Ograda:** R37, šest tvrdnji, uključujući palatalizaciju i razliku koda 3 od 2.

---

## Što lanac i dalje NE provjerava

Popis je kratak namjerno: sve u njemu je provjereno da doista nedostaje, i ništa
se ne tvrdi da je pokriveno „otprilike".

1. **Argument i logika.** Slijedi li zaključak iz rezultata; odgovara li rad na
   postavljene hipoteze; proturječi li Rasprava Rezultatima. `check_argument.py`
   je savjetodavan i plitak. Ovo je jedina preostala kategorija koju mentor
   stvarno ocjenjuje, i jedina za koju alat vjerojatno nije pravi oblik.
2. **Hrvatska gramatika iznad razine pravopisa.** Slaganje roda i broja preko
   rečenice, zamjenica bez imenice, prazna vezna sredstva. Audit Znahor je našao
   četiri takva kvara koje je proizveo sam stilski zahvat, i nijedan alat ih ne
   vidi (v. `stil_pipeline.md`).
3. **Aritmetika unutar tablice.** Zbroj stupca, N po podskupinama naspram
   ukupnoga, postoci koji daju 100 unutar jedne tablice.
4. **Statističko izvještavanje.** Naziv testa, stupnjevi slobode, veličina
   učinka, i slaže li se opis („značajno") s prijavljenim p.
5. **Registry admission** za `mefri-sanitarno` (blokiran zastarjelim hashom,
   namjerno se ne zaobilazi).
6. **Mršavljenje routera** (SKILL.md 550+ redaka), jedina promjena bez ograde
   koja bi je uhvatila.

## 108–111. zatvaranje popisa „što lanac NE provjerava"
Popis od šest stavki iz v1.9.8 obrađen je redom. Četiri su zatvorene, dvije su
ostale i za obje postoji razlog koji nije „nismo stigli".

### C3 — statističko izvještavanje (`check_statistika.py`)

Lanac je provjeravao postoje li brojke i imaju li pokriće. Nije provjeravao
**govori li tekst o njima istinu**. „Razlika je statistički značajna (p = 0,322)"
ima brojku koja postoji, dolazi iz rada, i potpuno je pogrešno opisana.

Prva izvedba je na stvarnom radu proglasila **devet urednih rečenica
proturječnima**, jer hrvatska negacija ne stoji uz pridjev: „nije **se
statistički** značajno razlikovala", „nije **bila** statistički značajna". Uzorak
je tražio „nije značaj…" bez umetnutih riječi, vidio riječ „značajno" i previdio
negaciju. Sada se dopušta do četiri umetnute riječi.

Druga izvedba je prijavljivala rečenicu koja **deklarira prag** („značajnost je
utvrđivana na razini p < 0,05") — ondje je p jednak pragu po definiciji.

Treća je tražila naziv testa uz svaku p-vrijednost i ispisala 23 „nalaza" koji su
svi bili uredni: test se imenuje jednom, u Metodologiji, i to je ispravno. Sada
se prijavljuje samo slučaj kad testa nema **nigdje** u radu.

### C4 — aritmetika u tablicama (`check_tablice.py`)

Brojke su se provjeravale u tekstu i naspram izvora, unutar tablice nikad, a
ondje su najlakše provjerive.

Tri lažna nalaza na stvarnim radovima, sva tri ista klasa: **„Ukupno" u nazivu
retka nije redak zbroja.** „Ukupno suspendirana sredstva" stajalo je kao drugi od
četiri retka. Sada: redak zbroja je zadnji redak, i zbroj ne može biti manji od
najvećeg pribrojnika (time otpada „Ukupno (0–25 bodova) = 54,1 %" uz pojedinačne
udjele do 73,6 %). Za `n` iz natpisa dopušten je višekratnik: tablica koja slaže
dvije podjele istoga uzorka zbraja na 2N, i to je oblik tablice, ne nesklad.

### G1 — hipoteze i ciljevi (`check_hipoteze.py`)

„Slijedi li zaključak iz rezultata" alat ne može presuditi. Ali jedan dio te
kategorije je posve mehanički i mentori ga traže prvo: **svaka postavljena
hipoteza mora dobiti izričitu presudu.**

Dvije izvedbe pale su na izdvajanju poglavlja: prva je stala iza prve hipoteze
(svaki redak „H2. Druga…" izgleda kao novi naslov), druga je izrezala pola
dokumenta. Treća ne izdvaja poglavlje uopće: skupi sve oznake H<n> izvan sadržaja
i za svaku pita postoji li odlomak koji o njoj donosi presudu. Jedinica je
**odlomak, ne rečenica**, jer rastavljač rečenica u „H1. Studenti…" vidi kraj
rečenice i oznaka ostaje sama.

**Nalaz na stvarnom radu:** MEDRI diplomski postavlja H1–H5 i **nijednu ne
presuđuje**. To je prvo pitanje na obrani.

### Prazna vezna sredstva (`verify_rewrite.py`)

Audit Znahor, C3: metrika kohezije mjeri **prisutnost** veznih sredstava, pa je
zahvat koji umeće „Naime," i „Dakle," prazno formalno poboljšanje — alat potvrdi
ono što je sam pokvario. Dodan je smjerni guard: skok gustoće veznih sredstava
uz nepromijenjen broj rečenica je nalaz zahvata, ne poboljšanje.

**Ograde:** R38 (6 tvrdnji), R39 (3), R40 (3), sve s oba smjera.

---

## Što OSTAJE nepokriveno, i zašto

**1. Registry admission za `mefri-sanitarno`.** Nije „zastario hash" kako je
ranije zapisano. `faculty_scale_gate.py` traži
`katedra-lite/evals/benchmark/v1_vs_v2_contract.json`, datoteku s dokazima
evaluacije koja u paketu ne postoji. Ponovno pokretanje gatea to ne rješava, a
izmišljanje te datoteke bilo bi upravo ono protiv čega gate stoji. Profil ostaje
datoteka sa statusom `nepotvrdeno`, kao i `hks-fzs`.

**2. Mršavljenje routera.** SKILL.md je i dalje 550+ redaka i plaća se u svakoj
poruci. Ovo je jedina preostala promjena **bez ograde koja bi je uhvatila**:
mjeri se ponašanjem modela, a za to nema testa. Radi se sa zasebnim evalom ili se
ne radi.

**3. Ono što alat ne može.** Slijedi li zaključak iz rezultata, proturječi li
Rasprava Rezultatima, drži li argument. G1 pokriva mehanički dio (je li na
pitanje odgovoreno), ne sadržajni (je li odgovor točan). Za to postoji željezno
pravilo 31 i obavezan korak `citanje_tijela`, i to je pošten odgovor, ne rupa
koju treba zatvoriti skriptom.

## 112. „nije se pokrenula" i „ne odnosi se na ovaj rad" bili su isto stanje
**Kad:** 5. 9. 2026., nađen na pitanje „jesmo li gotovi", provjerom umjesto
procjene. **Uzrok: moja vlastita zakrpa iz istoga dana.**

Kvar 58 je uveo da preskočena blokirajuća provjera blokira, i to je bilo točno:
provjera koja se nije pokrenula nije provjera koja je prošla. Ali faze C3, C4 i
G1, dodane nekoliko sati poslije, vraćaju kod 3 kad se **izvedu i utvrde da se
na taj rad ne odnose** (rad nema hipoteza, nema p-vrijednosti, nema brojčanih
tablica). Gate je kod 3 mapirao u `preskočeno`, pa je **pravni seminarski rad
padao na fazi audit** iako su sve tri provjere uredno odradile svoj posao.

Izmjereno na stvarnom pravnom radu, prije i poslije:

```
prije:   ⛔ NIJE POKRENUTO, a blokira: dosljednost, hipoteze, statistika
poslije: ◦ ne odnosi se na ovaj rad: odlomci, tvrdnja_izvor, hipoteze,
           tablice, statistika
         ⛔ NIJE POKRENUTO, a blokira: dosljednost      ← jedini stvaran
```

Pravilo 20 razlikuje pad od prolaza. Ovo je ista razlika jedan stupanj finije, i
sada je stanje pet, ne četiri:

| stanje | značenje | blokira |
|---|---|---|
| `ok` | provjera je prošla | ne |
| `nalaz` | provjera je našla problem | **da** |
| `neprimjenjivo` | provjera se IZVELA i utvrdila da se ne odnosi na ovaj rad | ne |
| `preskočeno` | provjera se NIJE izvela, nema ulaza | **da** |
| `pukao` | provjera se srušila | **da** |

Razlika je cijela poanta: `neprimjenjivo` je **nalaz o radu** (teorijski rad nema
hipoteze i to je uredu), `preskočeno` je **nalaz o projektu** (ulaz fali i to
netko mora riješiti).

Usput je istim mjerenjem nađeno da `check_tvrdnja_izvor.py` vraća 2 kad nema
`izvori/mapa.json`, pa je gate na svakom radu bez priložene građe, dakle na
većini, javljao „alat pukao".

**Ograda:** G13, tri tvrdnje, uključujući onu da preskočeno i dalje blokira i kad
u istoj fazi postoji neprimjenjiva provjera.

**Pouka koja ide uz kvar 91:** svaka nova provjera koja se doda u gate mora se
pokrenuti na radu **na koji se ne odnosi**, ne samo na onom na koji se odnosi.
Fixture za to postoji: pravni rad nema ni hipoteza, ni p-vrijednosti, ni
brojčanih tablica.

## 113. `kvar.py` je poznavao samo jedan broj po unosu, pa je grupirani unos bio ili nevidljiv ili lažni preskok

Zakrpa v1.9.5 upisala je četiri unosa koji svaki pokrivaju tri do četiri kvara, jer su to
klase s istim popravkom i jednim mjerenjem (`61–63` exit-code disciplina, `64–66` nove
provjere, `67–70` lažni nalazi, `72–73` alat za tvrdnje). Naslovi su glasili
`## Kvar 61–63 — naslov`, a `NASLOV` uzorak traži `## <broj>. <naslov>`. Alat ih zato
**nije vidio uopće**:

```
prije:    unosa: 34 · zadnji broj: 57 · sljedeći slobodan: 58   ✅ numeracija teče
stvarno:  katalog nosi unose do broja 73
```

To je najgori mogući ishod za registar brojeva: sljedeća bi zakrpa uzela 58–73, koje su već
potrošene, i sudarila se s njima — a alat bi je pritom uvjeravao da je sve u redu. Kad su
naslovi prepisani u oblik koji alat čita, javio je tri preskoka (`očekivan 62, 65, 68`), što
je bilo jednako netočno: brojevi nisu preskočeni nego pokriveni.

Razdvajanje na po jedan broj nije bilo moguće bez pogađanja: poruka commita za skupinu 61–63
navodi `audit_all`, iznimku bez oznake i `cross_check` glob, a katalog za istu skupinu
navodi `generate_report`, `audit_all:83` i `numbers_inventory`/`check_repetition`. Koji broj
pripada kojoj stavci ne stoji nigdje, pa bi svaka podjela bila izmišljen podatak.

Popravak je zato u alatu, ne u sadržaju: naslov prima i raspon
(`## 61–63. naslov`, en dash, em dash ili crtica), `unosi()` vraća i zadnji pokriveni broj,
numeracija se provjerava **po brojevima** a sadržaj **po unosu**, a `--novi` kreće od zadnjeg
pokrivenog broja. Poslije:

```
unosa: 42 (od toga 4 s rasponom) · zadnji broj: 73 · sljedeći slobodan: 74
✅ numeracija teče, naslovi su različiti, svaki unos ima mjeru i isječak
```

Ograda: raspon koji ide unatrag (`## 66–64.`) daje tvrdi nalaz, provjereno mutacijom.

---

## 114. Katalozi kvarova nisu bili u jedinom ulazu za testove, pa je suite bio zelen nad pokvarenim registrom

`bin/testovi.sh` postoji da bi „jedan ulaz" dao „jedan izlazni kod", i pokretao je devet
skupina: tri test suitea i šest provjera tvrdnji. `kvar.py` nije bio među njima. Mjereno na
stanju u kojem je katalog imao tri tvrda nalaza:

```
kvar.py katedra-lite/references/zamke.md --provjeri   ❌ KVARI KATALOG: 3   izlaz 1
bin/testovi.sh                                        ✅ svih 9 skupina prošlo   izlaz 0
```

Isti repo, dvije istine, a ona koja se pokreće je zelena. Registar brojeva koji nitko ne
provjerava iz jedinog ulaza nije registar nego dogovor.

Dodane tri skupine (`katalog kvarova: katedra-lite | rad-audit | rad-docx`), suite ide s 9 na
12. Ograda po pravilu 34: `## 71.` prepisan u `## 75.` obara skupinu i s njom cijeli suite
(`❌ 1 od 12 skupina palo`, izlaz 1); vraćanjem se vraća i zeleno.

## 115. Otisak motora hashirao je bajtove radnog stabla, pa je isti commit imao dva otiska ovisno o platformi

`katedra_adapter.otisak_motora()` računa sha256 nad `rad-audit/scripts/*.py` čitajući ih u
binarnom načinu. Git s `core.autocrlf=true` — zadano na Windowsu — piše CRLF u radno stablo,
a LF u objekte. Isti commit zato daje dva otiska:

```
sirovi bajtovi, CRLF radno stablo   0.0.0-undeclared+3b6c7a3e
sirovi bajtovi, LF radno stablo     0.0.0-undeclared+b133a824
```

Posljedica nije kozmetička. `engine_contract.json` sadrži jednu vrijednost, pa je manifest
ispravan na platformi na kojoj je zapisan i **pogrešan na svakoj drugoj**. Test R22 („manifest
se slaže s otiskom koda") time prestaje mjeriti slaganje koda i ugovora i počinje mjeriti
okolinu u kojoj se pokreće. Katedra u motor načinu odbija `DocumentAuditResult` s otiskom koji
joj se ne slaže, pa bi lanac na jednoj platformi radio, a na drugoj odbijao rezultat — bez
ijedne izmjene u kodu.

Nađeno mjerenjem, ne čitanjem: `bin/testovi.sh` prošao je 12/12 u svježem klonu, a odmah
zatim pao `2 od 12` u `~/.katedra-pkg` nad **istim commitom**. Razlika je bila u tome što je
klon imao dio datoteka zapisanih s LF (one koje je sesija pisala), a `~/.katedra-pkg` sve s
CRLF iz checkouta.

Popravak: prijelomi retka normaliziraju se prije hashiranja (`\r\n` i `\r` → `\n`). Otisak
sada mjeri **sadržaj** motora, ne način na koji ga je git zapisao na disk. Izmjereno poslije:
CRLF stablo i LF stablo daju isti `b133a824`.

Ograda: `R41` u `rad-audit/scripts/tests/test_all.py` gradi dvije kopije motora, jednu u CRLF
i jednu u LF, i traži isti otisak. Mutacijom provjereno da pada — vraćanje starog načina
hashiranja obara R41 i R22 (185 → 183 prošlo), povratak popravka vraća 185/185.

## 116. Naslov u obliku koji registar ne čita bio je tišina, pa je „sljedeći slobodan” pokazivao na potrošen broj

`kvar.py` čita `## N. naslov` i `## N–M. naslov`. Zakrpe su četiri puta zaredom pisale
`## Kvar N — naslov` i `## Kvarovi N–M — naslov` (v1.9.5, v1.9.6, v1.9.7, v1.9.10). Takav
unos alat **ne vidi** — ne kao pogrešku, nego ga uopće nema:

```
katalog nosi unose do broja 73
alat javlja:  unosa: 34 · zadnji broj: 57 · sljedeći slobodan: 58   ✅ numeracija teče
```

Zeleno nad registrom koji je kraći nego što jest. Posljedica je sudar: sljedeća zakrpa uzme
„slobodan” broj koji je već potrošen, pa se pri spajanju mora prenumerirati. Dogodilo se s
brojevima 74, 105, 106 i 107 — svaki put ručno, svaki put nakon što je zakrpa već napisana.

Popravak ima dva dijela, jer kvar ima dva kraja.

**Oblik se prijavljuje i popravlja.** Naslov u tuđem obliku sada je **tvrdi nalaz** s
naredbom koja ga prevodi:

```
❌ NASLOVI KOJE REGISTAR NE ČITA: 1
   · redak 2126: ## Kvarovi 116–118 — proba tudjeg oblika
   Popravak: python3 kvar.py <katalog> --popravi-naslove
```

Mjereno na toj probi: prije popravka `--sljedeci` javlja **116** iako unos tvrdi 116–118;
poslije popravka **119**. Prijevod ne dira sadržaj, samo naslov.

**Broj se pita, ne pretpostavlja.** `--sljedeci` ispisuje prvi slobodan broj iz kataloga u
koji unos ide. Sudari su nastali tako što su dvije grane brojile od istog mjesta ne znajući
jedna za drugu; zakrpa koja pita cilj ne može promašiti. Oboje zapisano u
`katedra/references/kvar.md`.

Ograda: `katedra/scripts/tests/test_kvar.py` (sedam provjera, skupina „katedra: registar
kvarova” u `bin/testovi.sh`) traži da se tuđi oblik prepozna, da katalog s njim **ne prođe**,
da ga `--popravi-naslove` prevede i da ispravan katalog ostane nepromijenjen. Skill `katedra`
do sada nije imao nijedan test, a drži registar na koji se pozivaju svi ostali skillovi.

---

## 117. provjera tvrdnji gledala je samo jedan smjer
`zakrpa.py --provjeri-tvrdnje` od kvara 72 provjerava da SKILL.md ne imenuje
skriptu koje nema. Obrnuti smjer nije gledao nitko: **alat koji postoji, a
dokumentacija ga nikad ne spominje.**

Izmjereno: **trinaest** takvih alata, od toga **devet u rad-auditu**. Svih devet
faza dodanih u v1.9.5 do v1.9.10 (metapodaci, uputnice, tablice, statistika,
hipoteze, tvrdnja↔izvor, postojanje reference, mapa izvora, propagacija) radilo je
samo zato što ih `generate_report.py` zove. Tko skill otvori izravno, za njih nije
mogao znati.

**Nedokumentiran alat je alat koji se ne koristi, isto kao alat koji ne postoji.**
To je ista klasa kao kvar 8 („SKILL.md zove skriptu koje nema"), samo u zrcalu, i
promakla je jer je provjera bila jednosmjerna.

Nađeno i u katedra-liteu (`provjeri_brojke_u_tekstu`, `sigurni_popravci_hr`) i u
rad-docxu (`inventar_paketa`, `priprema_slanja`).

Mjereno na `main` prije zakrpe i na grani poslije, istim alatom:

```
PRIJE                       POSLIJE
rad-audit          9   →   0
katedra-lite       2   →   0
rad-docx           2   →   0
ukupno            13   →   0
```

Ograda po pravilu 34 — provjera koja ne može pasti nije provjera. Dvije mutacije:

```
A) `check_hipoteze.py` preimenovan u SKILL.md-u  → oba smjera prijave isto:
   ❌ SKILL.md zove `check_XXXXX.py`, a te skripte nema
   ⚠ `scripts/check_hipoteze.py` postoji, a ne spominje ga nitko
B) nova `scripts/proba_nedokumentirana.py`       → ⚠ prijavljena odmah
C) vraćeno u čisto stanje                        → 0 nalaza
```

---

## 118. Opis skilla je površina odluke, ne changelog

Opisi skillova postali su popis verzija. `description` je jedini tekst koji se
čita **prije** nego se skill učita: po njemu se odlučuje hoće li se uopće
aktivirati. `katedra-lite` je ondje imao changelog.

```
katedra-lite/SKILL.md, description (main):
  ukupno                      827 znakova
  opis što skill radi         131 zn.  (16 %)
  nabrajanje verzija          696 zn.  (84 %)
  riječ „Aktiviraj”           NEMA

isti opis nakon prepisivanja:
  ukupno                      693 zn.
  oznaka verzije                8 zn.  („v1.9.11.")
  riječ „Aktiviraj”           ima — s okidačima (seminarski, završni,
                              diplomski, audit rada, provjera citata…)
```

Zakrpa je tvrdila 842 znaka; izmjereno ih je 827. Brojka je ispravljena, jer
unos vrijedi onoliko koliko mu se brojka da ponoviti.

Ista je mjera primijenjena na satelite: `rad-audit` 507 → 730 zn. i `rad-docx`
399 → 542 zn., ali u suprotnom smjeru — njihovi opisi nisu spominjali **nijednu**
od deset provjera dodanih u v1.9.5–v1.9.10, pa se za te zadatke skill nije imao
razloga aktivirati. Opis smije rasti kad opisuje površinu, i mora se kratiti kad
opisuje prošlost.

---

## 119. Provjera tvrdnji rušila se na hrvatskoj konzoli, pa je nalaz koji je NAŠLA izlazio kao traceback

Novi zrcalni smjer (kvar 117) nije se dao izmjeriti jer `zakrpa.py
--provjeri-tvrdnje` na ovom računalu uopće nije dolazio do ispisa. Dva mjesta,
oba kodna stranica konzole (`cp1250`):

```
1) subprocess.run(..., text=True)   ← bez `encoding`
   dijete (test_all.py) ispisuje ✓ i ⚠ u UTF-8, roditelj dekodira cp1250:
   UnicodeDecodeError → dretva čitača umre → r.stdout je None →
   TypeError: expected string or bytes-like object, got 'NoneType'

2) print(" ", nalaz)                ← nalaz počinje znakom ⚠
   UnicodeEncodeError: 'charmap' codec can't encode character '⚠'
```

Prvo mjerenje zbog toga je pokazalo **„rad-audit: 0 nedokumentiranih"** — nula
koja je bila pad, ne čistoća. Isti alat s popravljenim ispisom na istom commitu
javlja **9**. Pravilo 20 doslovno: alat koji je pukao nije provjera koja je
prošla, a najskuplji oblik tog kvara je onaj u kojem pad izgleda kao uredan
rezultat.

Popravak: dekodiranje djeteta je izrijekom `encoding="utf-8",
errors="replace"` (uz `PYTHONIOENCODING=utf-8` u okolini djeteta), a vlastiti
ispis dobiva `sys.stdout.reconfigure(errors="replace")`. Kodna stranica se ne
mijenja — č, ć, ž, š i đ postoje u cp1250 — mijenja se samo to da znak koji u
njoj ne postoji izađe kao `?` umjesto da obori alat:

```
prije:  Traceback … UnicodeEncodeError            (izlaz 1, nula nalaza)
poslije: ? `scripts/check_hipoteze.py` postoji, a ne spominje ga nitko
```

Ograda: `bin/testovi.sh` već izvozi `PYTHONIOENCODING=utf-8` (kvar 114), pa suite
ovo ne bi uhvatio — kvar se vidi samo kad se alat pokrene rukom, kako ga se i
pokreće. Zato popravak stoji u samom alatu, ne u pokretaču.

---

## 120. Brojka „31 stvarni kvar” stajala je u opisu nad katalogom od 26, a kvar 37 ju je zapisao još 2. rujna

Kvar 37 (2. rujna 2026.) izmjerio je da `rad-docx/SKILL.md` na dva mjesta tvrdi
**31 stvarni kvar** nad katalogom koji ih tada nosi **23**, i predložio popravak:
provjeru koja svaku takvu tvrdnju traži na disku. Provedena je samo polovica —
ona za **skripte** (`SKILL.md` zove datoteku koje nema). Brojka o veličini
kataloga ostala je proza, pa ju je i dalje mjerio samo onaj tko se sjeti.

Četiri dana i osamdesetak unosa poslije, stanje na `main`:

```
$ grep -c '^## [0-9]' rad-docx/references/zamke.md   → 26
$ grep -c '31 stvarni kvar' rad-docx/SKILL.md        → 1     (i „katalog zamki 23→31" u opisu)
```

Tvrdnja je preživjela vlastiti unos u katalogu jer katalog nije alat: unos opisuje
kvar, ali ništa ne pada dok netko ne pogleda. **Nalaz bez ograde je bilješka.**

Popravak: `zakrpa.py --provjeri-tvrdnje` dobiva šesti nalaz — svaki redak
`SKILL.md`-a koji spominje `zamke.md` i broji kvarove uspoređuje se s brojem
unosa u tom katalogu. Brojke u `rad-docxu` ispravljene su na izmjerenih 26.

```
prije:  ❌ SKILL.md tvrdi „31 stvarni kvar" o references/zamke.md, a katalog nosi 26 unosa
poslije: ✓ SKILL.md i kod se slažu          (svih 7 skillova)
```

Provjera gleda **samo `SKILL.md`**, ne i reference. Razlog je u ovom istom
katalogu: unos 37 doslovno nosi tuđi `31 stvarni kvar` kao dokaz, pa bi
skeniranje referenci prijavilo citat kao tvrdnju. Lažan nalaz iz alata koji lovi
lažne tvrdnje skuplji je od tvrdnje koju propusti (kvar 91).

Ograda: `test_zakrpa.py` R49 — kriva brojka mora pasti, točna ne smije, citat u
referenci ne smije. Mutacija (usporedba zamijenjena s `if False`) obara prvu:
9/9 → 8/9.

---

## 121. mjerilo je palo, a zaključak je htio pasti na opis
**Kad:** 6. 9. 2026. **Gdje:** `skill-creator/scripts/run_eval.py::run_single_query`
i, nakon toga, u prvoj verziji vlastite zamjene.

Trigger eval za `katedra-lite` vratio je **12/24: svih 12 „ne smije okinuti"
prošlo, svih 12 „mora okinuti" palo**. Broj je izgledao kao presuda o opisu
skilla — 0 % odziva — i sljedeći potez bio bi prepisati `description:`.

Dva neovisna kvara mjerila, oba istog oblika: mjeri se nešto što nije predmet.

**(a) Ime pod kojim skill odgovara.** Harness registrira privremenu kopiju pod
jedinstvenim imenom `katedra-lite-skill-<uuid>` i okidanje broji samo ako se
**to** ime pojavi u ulazu alata:

```python
if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
```

Kad je pravi `katedra-lite` instaliran, on odgovori prvi, pod svojim imenom.
Ručna provjera jednog „palog" upita:

```
Provuci mi diplomski kroz audit prije predaje.
→ Skill | {'skill': 'katedra-lite', 'args': 'audit'}      ← okinuo, prvi poziv
harness: promašaj
```

Izolacija instalirane kartice ne pomaže: `mv` synced mape traje do prve
sinkronizacije (demon ju vrati usred mjerenja, pa je pola prolaza mjereno u
jednom, pola u drugom uvjetu), a `HOME` ne upravlja popisom skillova — probano,
`katedra-lite` je i dalje odgovorio.

**(b) Vlastita zamjena mjerila istu grešku u drugom obliku.** Prva verzija
`evals/pokreni_trigger.py` vraćala je „nije okinuo" čim **prvi** alat nije Skill:

```python
if c.get("name") == "Skill":
    return {...}
return {"skill": None}      # prvi alat koji nije Skill → promašaj
```

Model koji prvo pogleda `ls` ima li uopće dokumenta, pa **onda** pozove skill,
time je bio promašaj. Odgoda nije promašaj.

Izmjereno, isti skup od 24 upita, ista instalirana kartica:

```
run_eval.py (tuđe ime + strogi prvi alat):   12/24  (50 %) — 0/12 pozitivnih
pokreni_trigger.py v1 (strogi prvi alat):    15/24  (62 %) — 3/12 pozitivnih
pokreni_trigger.py v2 (Skill bilo gdje,
                       3 pokretanja, većina): v. `evals/trigger_rezultat.json`
```

**Ograda:** `katedra-lite/evals/pokreni_trigger.py` bilježi uz svaki redak
`pozicija` (koji je po redu bio Skill poziv) i `stopa` (udio pokretanja u kojima
je okinuo), a `--ponavljanja` je zaseban parametar jer jedno pokretanje nije
mjerenje: **isti upit koji je ručno okinuo, u jednom prolazu harnessa nije.**
Redak s `pozicija: 3` i `stopa: 0.67` više se ne da pročitati kao „opis ne
valja".

**Pravilo koje iz ovoga slijedi (uz pravilo 20):** *prije nego broj postane sud
o predmetu, pokreni jedan slučaj ručno i pogledaj sirovi prijepis.* Mjerilo koje
nikad nije provjereno na poznatom ishodu nije mjerilo. Ovdje je cijena bila
prepisan `description:` koji nije bio pokvaren — promjena bez kvara, na sam
ulaz usmjeravanja.

**Što je mjerenje pokazalo o samom opisu** (24 upita, 3 pokretanja, instalirana
kartica v1.9.5, prazna radna mapa):

```
18/24 (75 %)   12/12 negativnih — nijedan lažni odziv
                6/12 pozitivnih
```

Četiri od šest palih pozitivnih imaju stopu 33 %: okidaju, ali nepouzdano. Nula
imaju točno dva, i oba imenuju sposobnost koju **v1.9.5 opis ne spominje**:

```
0 %  „Provjeri metapodatke ovog .docx-a prije nego ga pošaljem mentorici.”
0 %  „Nađi mi proturječja između Rezultata i Rasprave u ovom radu.”
```

Opis v1.9.11 obje imenuje (`metapodaci`, `hipoteze`, `brojke naspram izvora`).
Predviđanje koje se da provjeriti čim kartica bude osvježena: te dvije nule
nestaju bez ijedne izmjene opisa. Zato se opis **ne prepisuje sada** — prvo se
mjeri opis koji je već napisan, a nikad nije bio u opticaju.

Jedan pravi sudar usmjeravanja: „Rad mi je vratio mentor s komentarima, usporedi
s onim što sam mu poslao" u jednom je prolazu otišao u skill `docx`, ne u
`katedra-lite` (mod 7, povratak iz Worda). Kandidat za sljedeći zahvat na opisu.

**Ograničenje mjerenja, izrečeno da se broj ne čita krivo:** upiti se pokreću u
praznoj mapi, bez `.docx`-a. Model koji nema dokument često prvo traži dokument
umjesto da učita skill, pa je 75 % **donja granica**, ne stvarni odziv. Idući
korak mjerenja je isti skup uz fixture rad u mapi.

---

## 122. Indeks kataloga čitao je tuđi oblik naslova, a ne svoj, pa je jedanaest unosa izgubilo broj

`indeks_zamki.py` (v1.9.12) postoji da se katalog od 90 kB ne mora učitavati.
Njegov `BROJ_RE` prima `## 27. Naslov`, `## Kvar 58 — Naslov` i
`## Kvarovi 80–86 — Naslov`, ali **ne** i `## 80–86. Naslov` — kanonski raspon,
oblik koji `kvar.py --popravi-naslove` upravo proizvodi. Indeks je dakle čitao
oblik koji registar odbija, a ne oblik koji registar piše.

Posljedica je dvostruka i tiha:

```
kvar.py --provjeri     → unosa: 64 (od toga 11 s rasponom)
indeks_zamki.py --upisi → ✓ upisano … (69 unosa)

u indeksu: | — | 80–86. tri stavke koje su ostale nakon v1.9.5 | … |
           ^ broj je ispao iz stupca i završio u naslovu
```

Razlika 69 naspram 64 je zbroj dvaju predznaka: **−11** rasponskih unosa koji su
ostali bez broja i **+16** redaka koje indeks broji a katalog ne (11 istih
rasponskih, prepoznatih kao bezimeni, plus 5 nenumeriranih odjeljaka poput
„Korpus na kojem je lanac provjeren"). Nijedan alat nije pao: `--provjeri`
uspoređuje indeks sam sa sobom, pa je zeleno bilo iskreno i beskorisno.

Isti mehanizam kao kvar 116, samo obrnuto: ondje je zakrpa pisala oblik koji
alat ne čita, ovdje alat ne čita oblik koji zakrpa piše. Zajednički uzrok je da
gramatika naslova živi na dva mjesta.

Popravak: `BROJ_RE` prima i kanonski raspon; zaglavlje indeksa broji numerirane
unose odvojeno od nenumeriranih odjeljaka i to izriče:

```
Unosa: 64 (isti broj javlja kvar.py --provjeri) · uz njih 5 nenumeriranih odjeljaka
```

Ograda: `katedra-lite/scripts/tests/test_indeks.py`, skupina „katedra-lite:
indeks zamki" u `bin/testovi.sh`. **R53 ne testira uzorak nego slaganje dvaju
alata nad stvarnim katalogom** — `kvar.py` i `indeks_zamki.py` moraju dati isti
broj, jer uzorak se da popraviti u jednom alatu i opet raziću. Kad se kartica
instalira bez satelita, `kvar.py` nije uz nju; R53 se tada preskače **naglas**,
ne prešuti kao prolaz. Mutacija (vraćen stari uzorak) obara 3 od 5.

---

## 123. „VERSION ne smije zaostajati” bila bi provjera crvena u 28 od 32 stanja, pa je mjerena prije nego je napisana

Kvar 57 zapisao je da `VERSION` piše rukom onaj tko radi commit, i ostavio
ogradu neispunjenom. `bin/env.sh` od tada ispisuje zaostatak
(`❗ VERSION zaostaje 1 commit`), ali ništa ne pada. Očit sljedeći potez bio je
pretvoriti taj ispis u tvrdi uvjet. Izmjeren je prije pisanja, po pravilu 35:

```
$ za svaki commit na main-u: koliko je bitnih datoteka (SKILL.md, scripts/, bin/)
  promijenjeno nakon zadnje promjene VERSION-a

commita (first-parent):                             32
stanja s bitnim izmjenama nakon zadnje verzije:     28
```

**88 % povijesti bilo bi crveno.** To nije ograda nego alarm koji stalno zvoni,
i završio bi kao svaki takav — preskočen. Kvar 91 je isti oblik s druge strane:
lažni nalaz je skuplji od propuštenog. Prijedlog je odbačen mjerenjem, i to je
ovdje zapisano da se ne predloži četvrti put.

**Što se DA provjeriti.** Uža tvrdnja: oznaka verzije u opisu skilla mora biti
ista kao `VERSION`. Ta oznaka nije ukras — ona je jedino mjesto na kojem
*instalirana kartica* kaže iz koje je verzije, i kvar 121 se vidio upravo tako
(kartica v1.9.5, repo v1.9.12, šest verzija doktrine izvan opticaja). Ako se
oznaka piše rukom, laže i taj signal.

Oznaka je **zadnje** što stoji u opisu, u obliku ` v1.9.12.` Uzorak je usidren
na kraj namjerno: `rad-audit` u opisu nosi rečenicu „Od v1.9.10 i: metapodaci…",
koja je povijesna, ne tvrdnja o verziji. Uzorak bez sidra pročitao bi je kao
oznaku i dao lažan nalaz na svakom takvom opisu — mutacija to i pokazuje.

```
$ verzija.py --stanje
  ✓      katedra           v1.9.13
  ✓      katedra-lite      v1.9.13
  ✓      rad-audit         v1.9.13
  ✓      rad-docx          v1.9.13
  —      rad-orchestrator  (nema oznaku; ne provjerava se)
  —      fpzg-diplomski, replikacija-pspp  (isto)
```

`rad-orchestrator` broji vlastite verzije (`v1.2.1`) i nije dio ovog vlaka; skill
bez oznake se jednostavno ne provjerava, a `--stanje` kaže tko je tko.

Popravak ide dalje od provjere: `verzija.py --postavi X.Y.Z` upisuje `VERSION` i
sve oznake **u istom potezu**, pa se ne mogu raziću rukom — to je ono što kvar
57 traži. `--sljedeca` ispisuje sljedeći broj zakrpe, po istom pravilu po kojem
`kvar.py --sljedeci` ispisuje sljedeći broj kvara: broj se pita, ne pretpostavlja.

Ograda: `katedra/scripts/tests/test_verzija.py` (devet provjera) i skupina
„katedra: oznaka verzije = VERSION" u `bin/testovi.sh` koja provjeru vrti nad
stvarnim paketom. Mutacije: uzorak bez sidra na kraju obara 2 od 9, ugašena
usporedba 1 od 9.

Ostaje neriješeno i izrečeno: **koliko zaostajanje `VERSION`-a stvarno stoji, i
dalje nitko ne mjeri.** Ispis u `env.sh` je jedini signal i namjerno je ostao
mekan.

---

## 124. Mjerilo usmjeravanja nije znalo reći da nije moglo mjeriti, i mjerilo je samo jedan uvjet

Kartica je učitana i `drift.py` javlja da su kartica i repo iste (`SKILL.md` i
73 skripte). Time je predviđanje iz kvara 121 postalo provjerljivo — ali se
`pokreni_trigger.py` na ovom računalu ne može pokrenuti, a način na koji to kaže
bio je kvar:

```
$ python3 katedra-lite/evals/pokreni_trigger.py --skup <skup>
  File "…/subprocess.py", line 1552, in _execute_child
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

Traceback ne imenuje ni alat koji nedostaje ni to da mjerenja nije bilo. Hvata
se samo `TimeoutExpired`; `FileNotFoundError` prolazi kroz. Pravilo 20 opet:
alat koji je pukao nije mjerenje koje je palo. Ovdje je razlika presudna jer bi
sljedeći potez bio sud o **opisu skilla**, a ni jedan upit nije poslan.

Uzrok nije opremljenost stroja nego zamjena pojmova: na disku **jest**
`AnthropicClaude/claude.exe`, ali to je desktop aplikacija, ne CLI koji zna
`claude -p --output-format stream-json`.

**Drugi kvar iste skripte:** radna mapa bila je ukovana (`cwd=OVDJE`). Vlastito
ograničenje u izvještaju kaže da je odziv u praznoj mapi *donja granica* i da je
idući korak isti skup uz rad u mapi — a taj se korak nije dao izvesti bez
izmjene koda. Ograničenje koje se ne da ukloniti nije ograničenje, nego zid.

Popravak:

```
$ python3 pokreni_trigger.py --skup <skup>
❌ `claude` CLI nije pronađen u PATH-u — mjerenje se ne može izvesti.
   Ovo NIJE nalaz o opisu skilla, nego o okolini.                      (izlaz 2)
```

Alat se traži **prije** nego se pošalje ijedan upit; `--mapa` bira radnu mapu; a
rečenica o ograničenju se sada **mjeri**, ne prepisuje — izvještaj nosi
`radova_u_mapi` i tekst koji odgovara stvarnom uvjetu.

Ograda: `katedra-lite/scripts/tests/test_trigger.py`, skupina „katedra-lite:
mjerilo usmjeravanja". Odziv modela se ne testira — to traži živi model —
nego to da harness kaže istinu o tome je li mogao mjeriti i gdje je mjerio.

---

## 125. Broj testova u izvještaju bio je ukovana konstanta, pa je suite tvrdio 6/6 dok je pokretao sedam

Svih pet test-datoteka pisalo je zbroj rukom:

```python
print("REZULTATI TESTOVA: %d/%d prošlo" % (6 - len(PALO), 6))
```

Konstanta se razmakne čim se doda provjera. Izmjereno nad `main`-om:

```
datoteka            poziva check()   tvrdi
test_kvar.py               7           6      ← laž od PR-a #17
test_zakrpa.py             9           9
test_verzija.py            9           9
test_indeks.py             5           (računa)
test_trigger.py            8           9      ← laž nastala dok se pisala
```

Nijedan test nije pao zbog toga — laž je bila u **izvještaju**, ne u ishodu. Zato
je i preživjela: zeleno je bilo točno, brojka uz njega nije. Cijena je dvostruka:
`zakrpa.py --provjeri-tvrdnje` čita upravo taj redak i uspoređuje ga s tvrdnjama
u `SKILL.md`-u, pa kriva brojka putuje dalje; a unos kvara 116 u ovom katalogu
tvrdio je „šest provjera" i time je i katalog nosio istu laž.

Popravak nije ispraviti brojke — one bi se opet razmakle — nego ih maknuti:
`check()` broji sam (`SVE.append(naziv)`), a izvještaj ispisuje `len(SVE)`.
Isti oblik kao `kvar.py --sljedeci` i `verzija.py --postavi`: broj se ne piše
rukom ondje gdje ga stroj može prebrojati.

```
poslije: test_kvar.py 7/7 · test_zakrpa.py 9/9 · test_verzija.py 9/9
         test_indeks.py 5/5 · test_trigger.py 8/8
```

Ispravljena je i tvrdnja „šest provjera" uz kvar 116 na izmjerenih sedam.

---

## 126. Provjera tvrdnji tražila je skripte samo u `scripts/`, pa je alat koji postoji prijavila kao nepostojeći

Unos kvara 124 spominje `pokreni_trigger.py`. Suite je odmah pao:

```
❌ references/zamke.md zove `pokreni_trigger.py`, a te skripte nema ni u paketu
   ni kod satelita
                                            ↑ a datoteka postoji:
$ ls katedra-lite/evals/pokreni_trigger.py  → katedra-lite/evals/pokreni_trigger.py
```

Popis postojećih skripti gradio se s `korijen.glob("scripts/**/*.py")`. Harness
iz v1.9.12 živi u `evals/`, dakle izvan tog stabla, pa za provjeru nije postojao.
**Lažan ❌ iz alata koji lovi lažne tvrdnje** — kvar 91 primijenjen na samog
sebe, i najgori mogući oblik: nalaz je izgledao točno onako kako izgleda pravi.

Zašto nije puklo ranije: `katedra-lite/SKILL.md` harness spominje punom stazom
(`katedra-lite/evals/pokreni_trigger.py`), a uzorak hvata golo ime datoteke.
Tek ga je unos u katalogu napisao golo, i tvrdnja je postala vidljiva.

Popravak je jedan znak manje u uzorku: postojanje se traži nad **cijelim**
skillom (`korijen.glob("**/*.py")`), isto i kod satelita. Zrcalni smjer (kvar
117) namjerno ostaje na `scripts/*.py`: „alat koji nitko ne spominje" je tvrdnja
o **alatima skilla**, a `evals/` je pribor za mjerenje, ne alat koji korisnik
zove.

Ograda: `test_zakrpa.py` R63 — skripta u `evals/` ne smije dati nalaz, a
skripta koje doista nema i dalje mora pasti. Mutacija (vraćen uski uzorak) obara
prvu: 11/11 → 10/11.
