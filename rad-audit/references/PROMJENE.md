# Faza B: izvori bez osobnog autora (rujan 2026.) — kvar 2

`check_citations_authoryear.py` sada iz retka literature prepoznaje institucionalnog
autora kao naziv prije prve godine u zagradi. Time isti ključ dobivaju mediji i platforme
s točkom u nazivu (`danas.hr`, `Index.hr`), institucije i kratice s točkom prije godine
(`UNESCO. (2021)`). Osobni autor i dalje prvo prolazi kroz stroži postojeći parser.

Parentetički parser sada iz identiteta citata izostavlja signalnu riječ (`usp.`, `vidi`,
`prema`, `cf.`) i kratku napomenu iza godine. Zato oblik `usp. Tonković, Krolo i Marcelić,
2014, za analizu` daje isti ključ `tonković/2014` kao redak literature.

Regresijski fixture `author_year_institutions.docx` pokriva pet konzistentnih jedinica:
dvije domene, ministarstvo, UNESCO i osobnog autora u citatu sa signalnom riječi/napomenom.
Prije zakrpe: 2 definirane jedinice, 3 neprepoznata retka, 1 lažno siroče i 3 lažna citata
bez reference; poslije: 5 definiranih, 0 neprepoznatih, 0 siročadi, 0 citata bez reference,
exit 0. Zasebni guardovi potvrđuju da stvarno nedostajući medij i pogrešna godina i dalje
ostaju nalazi.

Promjena dviju skripti osvježava otisak u `engine_contract.json`; bez toga Katedrin
`engine.py` ispravno odbija rezultat kao verzijski nekompatibilan.

# Detekcija domene (rujan 2026.) — kvar 1

Nađeno na diplomskom radu iz medijskih studija (FPZG, 13 203 riječi).

| datoteka | greška | posljedica prije zakrpe |
|---|---|---|
| `domains/__init__.py` | `tl.count(k)` traži korijen kao slobodan podniz, bez granice riječi | `stup` hvata „nastup"/„dostupan" (30×), `okvir` „teorijski okvir" (38×), `temelj` „temelji se" (13×) → **83 boda za „celik"** na radu o glazbi |
| `domains/__init__.py` | domena se prihvaća golim zbrojem ≥ `min_score` | na dovoljno dugom tekstu dvije česte riječi prijeđu svaki fiksni prag; `generic` (točan odgovor) postao nedostižan |

Popravljeno: korijeni se traže na početku riječi (`(?<!\w)`), a domena se prihvaća samo uz
jedan od dva dokaza struke — **≥ 5 različitih** ključnih riječi (`MIN_RAZLICITIH`) ili **≥ 1
domensku oznaku** iz `claim_patterns` (IPE 300, S235, RAL 9006, IP44, HTTP 404…). Novi
`detect_domain_detail()` vraća i razlog odluke; `numbers_inventory.py` ga ispisuje kao
`↳ 'celik' ima 38 bodova, ali samo 4 različitih ključnih riječi (traži se 5) i 0 domenskih
oznaka`, pa je kriva detekcija vidljiva umjesto tiha.

Mjereno na tri ulaza: sporni rad `celik` → `generic`; `katedra/assets/domena_celik.docx`
(stvarni inženjerski rječnik) `celik` → `celik`, bez regresije;
`katedra/assets/domena_drustvene.docx` `celik` → `generic`.

**Granica:** `detect_domain` i dalje ne poznaje nijednu ne-inženjersku domenu. Rad iz
društvenih i humanističkih znanosti ide na generički frekvencijski rječnik, što je točno,
ali znači da faza C nad takvim radom ne nudi domensku provjeru — samo popis riječi uz
brojeve. Sukob koji je u tom radu ostao neuhvaćen („oko četrdeset pet zemalja" naspram „iz
oko 4 zemalja") generički rječnik i dalje ne hvata; to traži zaseban zahvat u
`zbroj_kategorija`.

**Naknadno popravljeno u 1.9.2:** lažni „CITAT BEZ REFERENCE" i lažno siroče u fazi B nad
izvorima bez osobnog autora — v. `references/zamke.md`, kvar 2.

**Dopuna (4. 9. 2026.):** docstring `_bodovi` postao je raw string. `(?<!\w)` u običnom
docstringu daje `SyntaxWarning: invalid escape sequence` na Pythonu 3.12+, pa je svaki
poziv `numbers_inventory.py` ispisivao upozorenje prije rezultata, a na budućem Pythonu
to je greška. Mjereno: prije 1 upozorenje nad `domena_celik.docx`, poslije 0; detekcija
nepromijenjena (`celik` → `celik`, `domena_drustvene` → `generic`).

# Zakrpe skripti (kolovoz 2026.)

Nađeno i ispravljeno na stvarnom završnom radu (EFZG, hrvatski APA, 61 izvor).

| datoteka | greška | posljedica prije zakrpe |
|---|---|---|
| `common.py` | `CITE_AY_RE` traži `)` odmah iza godine | hrvatski „(Čavlek i sur., 2011.)" nije prepoznat — **0 citata pronađeno** |
| `check_citations_authoryear.py` | vidi samo zagradni oblik | narativni „Faulkner (2001.)" nevidljiv; na testnom radu 62 od 86 citata |
| `check_citations_authoryear.py` | usporedba je gola razlika skupova | sklonidba („Albersa"), višečlana prezimena („van Heiningen") i institucije („TUI AG") daju lažne nalaze |
| `check_typography.py` | `m` u alternaciji hvata „**m**ilijuna" | hrvatski separator tisućica „1.465 milijuna" prijavljen kao decimalna točka |
| `check_fields.py` | `pageBreakBefore` uvijek upozorenje | propisani prijelom pred poglavljem prijavljen kao problem |
| `apply_safe_fixes.py` | briše sve `pageBreakBefore` po defaultu | **tiho krši formalni zahtjev fakulteta**; sada je opt-in `--strip-breaks` |

**Učinak na testnom radu:** nalazi citiranja **42 lažno kritična → 4 za ručnu
provjeru**, tipografija **5 lažnih → 0**, regresijski testovi (`scripts/tests/test_all.py`)
i dalje prolaze.

Preostala 4 nalaza granica su heuristike (npr. „Na primjerima koncerna TUI i
Thomas Cook Boz (2016.)…" gdje regex zahvati i imena poduzeća). Skripta sama kaže
da je heuristika i traži ručnu provjeru — to je sada istina, prije je bila poplava
lažnih alarma.

## v1.9 — Vancouver dijalekt (rujan 2026.)

| datoteka | promjena |
|---|---|
| `common.py` | `VANCOUVER_CITE_RE`, `vancouver_is_decimal`, `parse_vancouver_citations`, `LIT_HEADING_RE` (i „Popis citirane literature", „Literatura i izvori"…), `NUMBERED_ITEM_RE`; `detect_citation_style` vraća i `vancouver` |
| `check_citations.py` | drugi argument `ieee\|vancouver` (inače po tekstu); Vancouver: siročad, bez reference, redoslijed, razmak iza zareza, en-crtica, citat prije interpunkcije, „i sur." nakon 6 autora |
| `audit_all.py`, `generate_report.py` | faza B pokreće Vancouver granu; `mixed` uz Vancouver signal pokreće i nju |
| `katedra_adapter.py`, `engine_contract.json` | capability `hr.citations.vancouver.v1`, novi otisak motora |
| `tests/` | fixture `vancouver.docx` + skupina R16 (15 provjera) |

**Učinak na HKS-FZS radu (75 referenci):** kritično **1 → 0** (lažni `Rec(2003)24`), popis 75/75, 0 siročadi.

## Izmjene u dokumentaciji

- `SKILL.md` — `apply_safe_fixes.py` više ne uklanja prijelome po defaultu; dodan `--strip-breaks` i objašnjenje kad se smije koristiti; faza F preformulirana (prijelom se skida s natpisa prikaza, ne s naslova poglavlja).
- `references/pipeline.md` — ista distinkcija + 4 nova retka u katalogu zamki (hrvatski APA, narativni citat, sklonidba, separator tisućica).

## Provjera nakon instalacije

```bash
cd scripts/tests && python3 test_all.py     # mora završiti izlaznim kodom 0
```
