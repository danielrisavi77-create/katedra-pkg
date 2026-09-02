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
