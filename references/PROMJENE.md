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

## Izmjene u dokumentaciji

- `SKILL.md` — `apply_safe_fixes.py` više ne uklanja prijelome po defaultu; dodan `--strip-breaks` i objašnjenje kad se smije koristiti; faza F preformulirana (prijelom se skida s natpisa prikaza, ne s naslova poglavlja).
- `references/pipeline.md` — ista distinkcija + 4 nova retka u katalogu zamki (hrvatski APA, narativni citat, sklonidba, separator tisućica).

## Provjera nakon instalacije

```bash
cd scripts/tests && python3 test_all.py     # mora završiti izlaznim kodom 0
```
