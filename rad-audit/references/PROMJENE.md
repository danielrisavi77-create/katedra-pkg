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
