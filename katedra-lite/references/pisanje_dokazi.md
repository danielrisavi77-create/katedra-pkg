# PISANJE — izvori, dokazi i rewrite safety (učitava se na okidač)

> Dio `pisanje.md` §2 izdvojen radi štednje konteksta (v2.4). Otvori kad: se izvori
> verificiraju (`verify_sources.py`), tvrdnja ulazi u tekst preko evidence/claim ledgera,
> mentor traži produbljivanje (§2.0b), ili se prepisuje cijeli `.docx` (B13).
> Citatni oblik i pravila koja vrijede svugdje ostaju u `pisanje.md` §2.

## 2. Citiranje — dopušteni izvori i verifikacija

Dozvoljeni izvori su konkretne bibliografske jedinice: recenzirani članci, knjige i
monografije, službeni dokumenti institucija te relevantni datasetovi/statistike. HRČAK i
JSTOR mogu hostati konkretan rad; **Google Scholar je discovery servis, ne izvor**. Ako je
članak pronađen preko Scholara, u bibliografiji se navodi članak, a discovery kanal se po
potrebi bilježi kao `discovered_via: google_scholar`.

Kod `legal-footnote` profila first-class su i propisi, sudske odluke i EU akti. B10 ih
tipizira (`law`, `regulation`, `court_decision`, `eu_act`); B11 provjerava identitet i
source-quality metadata. Citation parser sam ne potvrđuje da izvor postoji.

`verify_sources.py` koristi stabilne semantičke statuse:

- `verified` — automatika je potvrdila identitet/lokator u deklariranom scopeu;
- `unverified` — automatika nema dovoljno dokaza ili je provider nedostupan; **nije dokaz da izvor ne postoji**;
- `conflict` — postoji kontradiktoran dokaz (npr. DOI vodi na očito drugo djelo); blokira do razrješenja;
- `invalid` — negativno potvrđen/nevaljan source entity; blokira do ispravka ili zamjene.

Quality taxonomy: **A/B/C/D/E/X** = A primarni/službeni/peer-reviewed · B akademski
sekundarni · C institucionalni izvještaj · D reputabilni kontekstualni/novinarski · E
samo discovery · X neprihvatljiv ili kontradiktoran. Klasa se automatski dodjeljuje samo
kad postoje dovoljni dokazi; inače ostaje `needs_classification`.

```bash
python3 <KATEDRA_SKILL>/scripts/verify_sources.py ./literatura.md
python3 <KATEDRA_SKILL>/scripts/verify_sources.py ./literatura.md --discovered-via "Google Scholar" --json ./.katedra/izvori.json
```

`conflict` i `invalid` ne ulaze u rad dok se problem ne razriješi. `unverified` ide u
**RUČNO PROVJERI** (npr. hrvatska knjiga bez Crossref zapisa, katalog NSK/Hrčak/službeni
katalog), ali se ne briše samo zato što automatika nije pronašla potvrdu.

### 2.0b Produbljivanje bez izmišljanja

Zamjerka „ovo poglavlje je plitko, produbi" ne rješava se izmišljanjem detalja (datuma,
brojki članaka, imena studija) da tekst zvuči uvjerljivije. Prvo provjeri već citirane izvore
u poglavlju — autor citiran za jednu tvrdnju često ima i druge, dobro poznate nalaze koji
izravno produbljuju istu temu bez novog izvora (npr. Cook i sur. 2005 već citiran za
definiciju kompleksne traume redovito nudi i tipologiju domena oštećenja iz istog rada). Tek
ako produbljenje traži nešto čega nema u `izvori.json`, stavi `[TREBA IZVOR]` i idi dalje —
ne izmišljaj broj da praznina ne bude vidljiva. Brojevi propisa, članaka i NN-oznaka posebno
su rizični jer zvuče provjerljivo dok sjećanje o točnom broju vara: „iz sjećanja" ide pod
`[PROVJERI ČL.]` / `[PROVJERI NN BR.]` (vokabular: `references/intake.md` § 0.7b), nikad kao
gotova tvrdnja. Rad koji tiho nosi krivi broj NN je gora šteta od rada koji priznaje da nešto
nije provjereno — primjena željeznog pravila 2 na najčešću strukturnu zamjerku mentora.

### 2.1 Page-level evidence i Claim Ledger

`verify_sources.py --json .katedra/izvori.json` svakom izvoru dodjeljuje stabilni
`source_id`. Kad je PDF/TXT/MD stvarno dostupan, ingestiraj ga iz korijena projekta:

```bash
python3 <KATEDRA_SKILL>/scripts/evidence_ingest.py ./izvori/autor2024.pdf \
  --source-id src_... --source-verification ./.katedra/izvori.json \
  --out ./.katedra/evidence.jsonl
```

Svaka izvučena jedinica ima `evidence_id` i locator `page + passage + char range`.
Tvrdnju zapiši i zatim poveži samo s dokazom koji je stvarno podupire:

```bash
python3 <KATEDRA_SKILL>/scripts/claim_ledger.py add \
  --claims ./.katedra/claims.jsonl --text "…" --chapter 2.1
python3 <KATEDRA_SKILL>/scripts/claim_ledger.py link \
  --claims ./.katedra/claims.jsonl --evidence ./.katedra/evidence.jsonl \
  --claim-id clm_... --evidence-id ev_... --relation supports
python3 <KATEDRA_SKILL>/scripts/claim_ledger.py validate \
  --claims ./.katedra/claims.jsonl --evidence ./.katedra/evidence.jsonl
```

**Izvor bez tiskane paginacije.** `page_label` je TISKANA oznaka stranice, ne redni broj
koji bi alat sam dodijelio. Kad je izvor `.txt`/`.md` bez prijeloma stranice ili PDF bez
oznaka, `evidence_ingest.py` upisuje `page_label: null` i `passage: N` — i tu ne nedostaje
ništa. Redni broj koji bi alat izmislio student bi prepisao u citat, a čitatelj ga ne bi
mogao naći ni u jednom otisku; zato je `null` točan podatak, a ne rupa.

```
$ evidence_ingest.py assets/fixture_izvor_bez_paginacije.txt --source-id src_test --out ev.jsonl
[evidence → ev.jsonl] dodano 5 passage(s), zamijenjeno 0, source=src_test
$ grep -c 'page_label": null' ev.jsonl
5
```

Odlomak je stabilna jedinica: granice se izvode iz praznih redaka u normaliziranom tekstu,
ne iz prijeloma retka, pa dva ingesta iste datoteke daju iste granice i isti `evidence_id`.
Citat po odlomku zato je provjerljiv jednako kao citat po stranici, i evidence gate ga
prihvaća bez iznimke. `[PROVJERI STR.]` na takvom izvoru je nalaz o doktrini, ne o izvoru.

`contextualizes` nije isto što i `supports`; `contradicts` se čuva, ne briše.
`claim_ledger.py report` samo opisuje ledger. Prije nego claim uđe u tekst, napravi
**Source Analysis Matrix** i strict evidence gate:

```bash
python3 <KATEDRA_SKILL>/scripts/evidence_gate.py \
  --claims ./.katedra/claims.jsonl --evidence ./.katedra/evidence.jsonl \
  --sources ./.katedra/izvori.json --policy strict --out ./.katedra/evidence_gate.json
```

`unsupported`, `conflicted`, `contradicted` i evidence iz `conflict/invalid` izvora blokiraju
strict gate. `advisory` je samo dijagnostika.

---

### 2.1 B13 rewrite safety gate

Prije izmjene cijelog `.docx` dokumenta napravi strict evidence gate i snapshot. Nakon rewritea
ne prihvaćaj datoteku bez oba safety checka:

```bash
python3 <KATEDRA_SKILL>/scripts/evidence_gate.py \
  --claims ./.katedra/claims.jsonl --evidence ./.katedra/evidence.jsonl \
  --sources ./.katedra/izvori.json --policy strict
python3 <KATEDRA_SKILL>/scripts/diff_versions.py --snapshot ./rad.docx --biljeska "prije rewritea"
python3 <KATEDRA_SKILL>/scripts/verify_rewrite.py ./rad_prije.docx ./rad_poslije.docx \
  --zahvat stil --profil ./.katedra/resolved_profile.json \
  --evidence-gate --require-snapshot
```

Za privremene tekstualne fragmente bez dokument-snapshota koristi `--evidence-gate`;
`--require-snapshot` je gate za stvarnu izmjenu dokumenta.
